export async function submitExpense(payload, initData) {
 const response = await fetch("https://your-worker.example.workers.dev/submit", {
   method: "POST",
   headers: {
     "Content-Type": "application/json",
     "X-Telegram-Init-Data": initData
   },
   body: JSON.stringify(payload)
 });
 const data = await response.json();
 if (!response.ok) {
   throw new Error(data.error || "Request failed");
 }
 return data;
}
