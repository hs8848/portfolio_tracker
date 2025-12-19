function renderKeyValueList(elementId, dataObj, emptyMsg) {
  const ul = document.getElementById(elementId);
  ul.innerHTML = "";

  if (!dataObj || Object.keys(dataObj).length === 0) {
    const li = document.createElement("li");
    li.innerText = emptyMsg;
    ul.appendChild(li);
    return;
  }

  for (const [key, value] of Object.entries(dataObj)) {
    const li = document.createElement("li");
    li.innerText = `${key} — ₹ ${formatAmount(value)}`;
    ul.appendChild(li);
  }
}

function formatAmount(amount) {
  return Number(amount).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

async function refreshPrices() {
  await authFetch("/prices/refresh", { method: "POST" });
  alert("Prices refreshed. Please re-run EOD valuation if needed.");
}


console.log("dashboard.js loaded");

async function loadDashboard() {
  try {
        const summary = await authFetch("/dashboard/summary")
          .then(r => r.json());

        console.log("Dashboard Summary:", summary);

        // Welcome message
        document.getElementById("welcomeMsg").innerText =
          `Hello, ${summary.user_name}`;

        // Total portfolio value
        document.getElementById("totalValue").innerText =
          `₹ ${formatAmount(summary.total_value)}`;

        document.getElementById("asOfDate").innerText =
          `As of ${summary.as_of_date}`;

        // By Instrument Type
        renderKeyValueList(
          "byInstType",
          summary.by_inst_type,
          "No instrument data"
        );

        // MF by Class
        renderKeyValueList(
          "byMfClass",
          summary.by_mf_class,
          "No MF class data"
        );

        // MF by AMC
        renderKeyValueList(
          "byMfAmc",
          summary.by_mf_amc,
          "No AMC data"
        );

       } catch (err) {
            console.error("Error loading dashboard", err);
        }
}

async function refreshPrices() {
  await authFetch("/prices/refresh", { method: "POST" });
  alert("Prices refreshed. Re-run EOD valuation if needed.");
}
