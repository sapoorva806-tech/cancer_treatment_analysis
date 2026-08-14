const API_BASE = (window.APP_CONFIG && window.APP_CONFIG.API_BASE) || "http://localhost:8000/api";

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
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    window.location.href = "login.html";
    return null;
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    // no body
  }

  if (!res.ok) {
    const message = data?.detail
      ? (Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(", ") : data.detail)
      : `Request failed (${res.status})`;
    throw new Error(message);
  }

  return data;
}

async function registerUser(payload) {
  return apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

async function loginUser(email, password) {
  const form = new URLSearchParams();
  form.set("grant_type", "password");
  form.set("username", email);
  form.set("password", password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.detail || "Login failed");
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
  const res = await fetch(`${API_BASE}/auth/otp/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone_number: phoneNumber }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.detail || "Failed to send OTP");
  }
  return data;
}

async function verifyOtp(phoneNumber, code, fullName) {
  const res = await fetch(`${API_BASE}/auth/otp/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone_number: phoneNumber, code, full_name: fullName || null }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.detail || "Invalid or expired OTP");
  }
  saveToken(data.access_token);
  return data;
}
async function requestOtp(phoneNumber) {
  const res = await fetch(`${API_BASE}/auth/otp/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone_number: phoneNumber }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.detail || "Failed to send OTP");
  }
  return data;
}

async function verifyOtp(phoneNumber, code, fullName) {
  const res = await fetch(`${API_BASE}/auth/otp/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone_number: phoneNumber, code, full_name: fullName || null }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data?.detail || "Invalid or expired OTP");
  }
  saveToken(data.access_token);
  return data;
}