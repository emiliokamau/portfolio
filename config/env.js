// Frontend Configuration
// Point to your deployed backend (update this with your Render backend URL once deployed)

window.RECAPTCHA_SITE_KEY = '6Ldh-EosAAAAAEW2LY03WUJtN-ev_mMpEBI4FauR';

// Set API_BASE based on environment
const hostname = window.location.hostname;
const isProduction = hostname.includes('vercel.app') || hostname.includes('netlify.app');
const isRender = hostname.includes('onrender.com');
const isDevelopment = hostname === 'localhost' || hostname === '127.0.0.1';

if (isRender) {
  // Render full-stack hosting: frontend and backend are same-origin
  window.API_BASE = window.location.origin;
} else if (isProduction) {
  // Production: use your deployed Render backend
  window.API_BASE = 'https://portfolio-backend-XXXX.onrender.com';
} else if (isDevelopment) {
  // Local development
  window.API_BASE = 'http://localhost:8000';
} else {
  // Fallback
  window.API_BASE = 'https://portfolio-backend-XXXX.onrender.com';
}

console.log('Portfolio API Base:', window.API_BASE);
