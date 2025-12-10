# The Cloud Lab Portfolio

A modern, accessible, multi-page personal portfolio built with plain HTML/CSS/JS. Prepared for dynamic content via a Django/DRF backend.

## Features
- Fixed, collapsible sidebar with persistent state
- Global dark mode with localStorage persistence
- Responsive layouts, glassmorphism, and subtle animations
- Accessibility improvements (ARIA, focus styles, contrast)
- Contact page with reCAPTCHA (frontend) and backend guidance
- API-ready: `config/env.js` sets `window.API_BASE` for backend separation

## Structure
- `landing.html`, `skills.html`, `projects.html`, `experiments.html`, `contact.html`
- `styles/global.css` — global styles
- `scripts/main.js` — shared functionality (API calls, persistence)
- `config/env.js` — frontend API base configuration

## Local Run
```powershell
# From the project root
python -m http.server 5500; Start-Process "http://localhost:5500/landing.html"
```
Backend (Django) example:
```powershell
# From your Django project folder
python manage.py runserver 8000
```
Set `config/env.js`:
```js
window.API_BASE = 'http://127.0.0.1:8000';
```

## Deployment
Frontend: Netlify/Vercel (static hosting)
Backend: Render/Railway (Gunicorn, optional Postgres)
- Update `config/env.js` with your production backend URL
- Add your frontend origins to Django CORS settings

## License
Proprietary. All rights reserved.
