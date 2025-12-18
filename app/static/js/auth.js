async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  if (!res.ok) {
    document.getElementById("error").innerText = "Login failed";
    return;
  }

  const data = await res.json();
  localStorage.setItem("token", data.access_token);

  window.location.href = "/dashboard";
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}
