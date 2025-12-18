async function loadDashboard() {
  const summary = await authFetch("/dashboard/summary").then(r => r.json());
  document.getElementById("totalValue").innerText =
    "₹ " + summary.total_value;
}

async function refreshPrices() {
  await authFetch("/prices/refresh", { method: "POST" });
  alert("Prices refreshed. Re-run EOD valuation if needed.");
}
