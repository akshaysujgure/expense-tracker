import crypto from "node:crypto";

function toBase64(bytes) {
  if (typeof Buffer !== "undefined") {
    return Buffer.from(bytes).toString("base64");
  }
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

function fromBase64(value) {
  if (typeof Buffer !== "undefined") {
    return Uint8Array.from(Buffer.from(value, "base64"));
  }
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

async function deriveEncryptionKey(secret) {
  const encoder = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    "PBKDF2",
    false,
    ["deriveKey"]
  );

  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: encoder.encode("expense-tracker-v1"),
      iterations: 100000,
      hash: "SHA-256"
    },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"]
  );
}

async function encryptTransaction(record, secretKey) {
  if (!secretKey) {
    throw new Error("Missing TRANSACTION_ENCRYPTION_KEY in worker secrets");
  }

  const encoder = new TextEncoder();
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await deriveEncryptionKey(secretKey);
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    encoder.encode(JSON.stringify(record))
  );

  return {
    encrypted: true,
    algorithm: "AES-GCM",
    iv: toBase64(iv),
    ciphertext: toBase64(new Uint8Array(ciphertext))
  };
}

function parseInitData(initDataString) {
 const params = new URLSearchParams(initDataString);
 const data = {};
 for (const [key, value] of params.entries()) {
   data[key] = value;
 }
 return data;
}
function validateTelegramInitData(initDataString, botToken) {
 if (!initDataString || !botToken) {
   return { valid: false, error: "Missing Telegram init data or bot token" };
 }
 const params = new URLSearchParams(initDataString);
 const hash = params.get("hash");
 if (!hash) {
   return { valid: false, error: "Missing Telegram hash" };
 }
 const authDate = Number(params.get("auth_date"));
 const now = Math.floor(Date.now() / 1000);
 if (!Number.isFinite(authDate) || now - authDate > 60 * 60) {
   return { valid: false, error: "Telegram init data expired" };
 }
 const sortedKeys = [];
 for (const [key, value] of params.entries()) {
   if (key === "hash") continue;
   sortedKeys.push(`${key}=${value}`);
 }
 sortedKeys.sort();
 const secretKey = crypto.createHash("sha256").update(botToken).digest();
 const dataCheckString = sortedKeys.join("\n");
 const expectedHash = crypto
   .createHmac("sha256", secretKey)
   .update(dataCheckString)
   .digest("hex");
 if (expectedHash !== hash) {
   return { valid: false, error: "Telegram init data signature mismatch" };
 }
 const payload = parseInitData(initDataString);
 return {
   valid: true,
   raw: payload,
   user: payload.user ? JSON.parse(payload.user) : null,
   chat: payload.chat ? JSON.parse(payload.chat) : null
 };
}
function createTransactionId() {
 return crypto.randomUUID();
}
async function writeToGithub(rawTransaction, env) {
 const timestamp = new Date(rawTransaction.timestamp);
 const year = timestamp.getUTCFullYear();
 const month = String(timestamp.getUTCMonth() + 1).padStart(2, "0");
 const day = String(timestamp.getUTCDate()).padStart(2, "0");
 const path = `data/raw/${year}/${month}/${day}/${rawTransaction.transaction_id}.json`;
 const content = JSON.stringify(rawTransaction, null, 2) + "\n";
 const response = await fetch(`https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/contents/${path}`, {
   method: "PUT",
   headers: {
     "Content-Type": "application/json",
     "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
     "Accept": "application/vnd.github+json",
     "User-Agent": "expense-tracker-worker"
   },
   body: JSON.stringify({
     message: `Add expense ${rawTransaction.transaction_id}`,
     content: Buffer.from(content).toString("base64"),
     branch: env.GITHUB_BRANCH || "main"
   })
 });
 if (!response.ok) {
   const text = await response.text();
   throw new Error(`GitHub write failed: ${response.status} ${text}`);
 }
 return await response.json();
}
export default {
 async fetch(request, env) {
   if (request.method !== "POST") {
     return new Response(JSON.stringify({ error: "Method not allowed" }), {
       status: 405,
       headers: { "Content-Type": "application/json" }
     });
   }
   try {
     const body = await request.json();
     const initData = request.headers.get("X-Telegram-Init-Data") || "";
     const validation = validateTelegramInitData(initData, env.TELEGRAM_BOT_TOKEN);
     if (!validation.valid) {
       return new Response(JSON.stringify({ error: validation.error }), {
         status: 401,
         headers: { "Content-Type": "application/json" }
       });
     }
     const user = validation.user;
     const chat = validation.chat || null;
     if (!user || !user.id) {
       return new Response(JSON.stringify({ error: "Missing authenticated Telegram user" }), {
         status: 401,
         headers: { "Content-Type": "application/json" }
       });
     }
     const scope = String(body.scope || "PERSONAL").toUpperCase();
     if (!["PERSONAL", "FAMILY"].includes(scope)) {
       return new Response(JSON.stringify({ error: "Invalid scope" }), {
         status: 400,
         headers: { "Content-Type": "application/json" }
       });
     }
     if (!chat || !chat.id) {
       return new Response(JSON.stringify({ error: "Family scope requires a trusted Telegram chat context" }), {
         status: 400,
         headers: { "Content-Type": "application/json" }
       });
     }
     const amount = Number(body.amount);
     if (!Number.isFinite(amount) || amount <= 0) {
       return new Response(JSON.stringify({ error: "Invalid amount" }), {
         status: 400,
         headers: { "Content-Type": "application/json" }
       });
     }
     const requestDate = typeof body.date === "string" && body.date ? body.date : new Date().toISOString().slice(0, 10);
     const tx = {
       transaction_id: createTransactionId(),
       family_id: String(chat.id),
       telegram_user_id: String(user.id),
       timestamp: new Date().toISOString(),
       date: requestDate,
       amount,
       type: "expense",
       scope,
       paid_by: String(user.id),
       beneficiaries: scope === "PERSONAL" ? [String(user.id)] : [],
       category: String(body.category || "Other"),
       subcategory: String(body.subcategory || "Miscellaneous"),
       payment_method: String(body.payment_method || "UPI"),
       merchant: String(body.merchant || ""),
       note: String(body.note || ""),
       status: "ACTIVE"
     };

    const encryptedRecord = {
       ...tx,
       encrypted: true,
       encrypted_payload: await encryptTransaction(tx, env.TRANSACTION_ENCRYPTION_KEY)
    };

    await writeToGithub(encryptedRecord, env);
    return new Response(JSON.stringify({ ok: true, transaction_id: tx.transaction_id, message: "Expense stored securely" }), {
       headers: { "Content-Type": "application/json" }
     });
   } catch (error) {
     return new Response(JSON.stringify({ error: error.message || "Unexpected error" }), {
       status: 500,
       headers: { "Content-Type": "application/json" }
     });
   }
 }
};
