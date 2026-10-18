const defaultWorkerUrl = "https://your-worker.example.workers.dev";
const workerUrl = (
  window.ExpenseTrackerConfig?.workerUrl ||
  window.__EXPENSE_TRACKER_CONFIG__?.workerUrl ||
  defaultWorkerUrl
).replace(/\/$/, "");

export async function submitExpense(payload, initData) {
  if (!initData) {
    throw new Error("Open this app inside Telegram to submit expenses.");
  }

  if (workerUrl === defaultWorkerUrl) {
    throw new Error("Set the worker URL in ExpenseTrackerConfig.workerUrl before deploying the Mini App.");
  }

  const response = await fetch(`${workerUrl}/submit`, {
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
