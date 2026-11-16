
const API_BASE =
  (window.APP_CONFIG && window.APP_CONFIG.API_BASE) ||
  (window.location.hostname === "localhost" ||
   window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000/api"
    : "https://hodgkin-risk-api.onrender.com/api");

const TOKEN_KEY = "hodgkin_access_token";

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function isLoggedIn() {
  return !!getToken();
}

async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (
    options.body &&
    !(options.body instanceof URLSearchParams)
  ) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  if (res.status === 401) {
    clearToken();
    throw new Error("Session expired. Please log in again.");
  }

  let data = null;

  try {
    data = await res.json();
  } catch {
    // Response has no JSON body.
  }

  if (!res.ok) {
    const message = data?.detail
      ? (
          Array.isArray(data.detail)
            ? data.detail.map(d => d.msg).join(", ")
            : data.detail
        )
      : `Request failed (${res.status})`;

    throw new Error(message);
  }

  return data;
}

async function registerUser(payload) {
  return apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

async function loginUser(email, password) {
  const form = new URLSearchParams();

  form.set("grant_type", "password");
  form.set("username", email);
  form.set("password", password);

  const data = await apiFetch("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: form
  });

  if (!data?.access_token) {
    throw new Error("Login response did not contain an access token.");
  }

  saveToken(data.access_token);
  return data;
}

async function getCurrentUser() {
  return apiFetch("/users/me");
}

function logout() {
  clearToken();
  window.location.href = "login.html";
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = "login.html";
  }
}

async function requestOtp(phoneNumber) {
  return apiFetch("/auth/otp/request", {
    method: "POST",
    body: JSON.stringify({
      phone_number: phoneNumber
    })
  });
}

async function verifyOtp(phoneNumber, code, fullName) {
  const data = await apiFetch("/auth/otp/verify", {
    method: "POST",
    body: JSON.stringify({
      phone_number: phoneNumber,
      code: code,
      full_name: fullName || null
    })
  });

  if (!data?.access_token) {
    throw new Error("OTP verification did not return an access token.");
  }

  saveToken(data.access_token);
  return data;
}

// Make functions available to every HTML page.
window.loginUser = loginUser;
window.registerUser = registerUser;
window.getCurrentUser = getCurrentUser;
window.logout = logout;
window.requireAuth = requireAuth;
window.isLoggedIn = isLoggedIn;
window.requestOtp = requestOtp;
window.verifyOtp = verifyOtp;

window.API_BASE = API_BASE;
