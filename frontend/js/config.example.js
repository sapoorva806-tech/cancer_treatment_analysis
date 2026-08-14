// Copy this to config.js (gitignored) and set the correct value per environment.
// api.js reads window.APP_CONFIG if present, otherwise falls back to localhost.

window.APP_CONFIG = {
  API_BASE: "https://your-backend-domain.com/api", // production
  // API_BASE: "http://localhost:8000/api", // local dev
};