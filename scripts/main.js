// --- Multi-language support ---
const translations = {
  en: {
    landingTitle: "Hi, I'm [Your Name]",
    landingDesc: "I'm a Full Stack Developer & Data Scientist passionate about building intelligent, beautiful, and user-friendly digital experiences. I love Python, Django, Flask, and AI/ML. I turn data into stories and code into magic!",
    contactMe: "Contact Me",
    sendMessage: "Send Message"
  },
  fr: {
    landingTitle: "Bonjour, je suis [Votre Nom]",
    landingDesc: "Je suis développeur full stack et data scientist passionné par la création d'expériences numériques intelligentes, belles et conviviales. J'adore Python, Django, Flask et l'IA/ML. Je transforme les données en histoires et le code en magie!",
    contactMe: "Contactez-moi",
    sendMessage: "Envoyer le message"
  },
  es: {
    landingTitle: "Hola, soy [Tu Nombre]",
    landingDesc: "Soy desarrollador full stack y científico de datos apasionado por crear experiencias digitales inteligentes, hermosas y fáciles de usar. Me encanta Python, Django, Flask y IA/ML. ¡Transformo datos en historias y código en magia!",
    contactMe: "Contáctame",
    sendMessage: "Enviar mensaje"
  }
};

function setLanguage(lang) {
  document.querySelector('.landing-title').textContent = translations[lang].landingTitle;
  document.querySelector('.landing-desc').textContent = translations[lang].landingDesc;
  document.querySelector('.section-title').textContent = translations[lang].contactMe;
  document.querySelector('.btn-primary[aria-label="Send Message"]').textContent = translations[lang].sendMessage;
}

const langSwitch = document.getElementById('lang-switch');
if (langSwitch) {
  langSwitch.addEventListener('change', (e) => {
    setLanguage(e.target.value);
  });
}
// --- Dynamic Skills (static for now, can be made API-driven) ---
const skills = [
  { name: 'Python', icon: 'assets/python.svg' },
  { name: 'Flask', icon: 'assets/flask.svg' },
  { name: 'Django', icon: 'assets/django.svg' },
  { name: 'Machine Learning', icon: 'assets/ml.svg' },
  { name: 'Data Science', icon: 'assets/ds.svg' },
];
const skillsDashboard = document.getElementById('skills-dashboard');
if (skillsDashboard) {
  skills.forEach(skill => {
    const div = document.createElement('div');
    div.className = 'skill-badge';
    div.innerHTML = `<img src="${skill.icon}" alt="${skill.name}"/><span>${skill.name}</span>`;
    skillsDashboard.appendChild(div);
  });
}


// --- API Base URL ---
// Prefer a global override if provided by config/env.js
const API_BASE = (typeof window !== 'undefined' && window.API_BASE) ? window.API_BASE : 'http://127.0.0.1:8000';

// --- Fetch and Render Projects ---
async function loadProjects() {
  const grid = document.getElementById('projects-grid');
  if (!grid) return;
  try {
    const res = await fetch(`${API_BASE}/api/projects`);
    const projects = await res.json();
    grid.innerHTML = '';
    projects.forEach(project => {
      const card = document.createElement('div');
      card.className = 'project-card';
      card.innerHTML = `
        <img src="${project.thumbnail_image}" alt="${project.title}" />
        <h3>${project.title}</h3>
        <p>${project.description}</p>
        <div class="tech-tags">${project.tech_stack.map(tag => `#${tag}`).join(' ')}</div>
        <div class="card-actions">
          <a href="${project.live_demo_link}" class="btn btn-secondary" target="_blank" rel="noopener">View Live</a>
          <a href="${project.github_link}" class="btn btn-primary" target="_blank" rel="noopener">GitHub Repo</a>
        </div>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    grid.innerHTML = '<p>Unable to load projects.</p>';
  }
}
loadProjects();


// --- Fetch and Render Quest Board (Kanban) ---
async function loadQuests() {
  const columns = {
    'Hypothesis': document.getElementById('kanban-hypothesis'),
    'In-Lab': document.getElementById('kanban-inlab'),
    'Published': document.getElementById('kanban-published'),
  };
  try {
    const res = await fetch(`${API_BASE}/api/quests`);
    const quests = await res.json();
    Object.values(columns).forEach(col => {
      if (col) col.querySelectorAll('.sticky-note').forEach(n => n.remove());
    });
    quests.forEach(quest => {
      const note = document.createElement('div');
      note.className = 'sticky-note';
      note.innerHTML = `
        <span>${quest.task_name}</span>
        <small>${quest.description || ''}</small>
        <div style="margin-top:0.5rem;">
          <button class="btn btn-secondary btn-upvote" data-id="${quest.id}">Hype (${quest.upvotes})</button>
        </div>
      `;
      if (columns[quest.status] && columns[quest.status].appendChild) {
        columns[quest.status].appendChild(note);
      }
    });
    // Add upvote listeners
    document.querySelectorAll('.btn-upvote').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = btn.getAttribute('data-id');
        await fetch(`${API_BASE}/api/quests/vote`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id })
        });
        loadQuests();
      });
    });
  } catch (e) {
    Object.values(columns).forEach(col => {
      if (col) col.innerHTML += '<p>Unable to load quests.</p>';
    });
  }
}
loadQuests();


// --- Contact Form Submission ---
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(contactForm);
    const data = Object.fromEntries(formData.entries());
            // Get reCAPTCHA token
            const recaptchaResponse = grecaptcha.getResponse();
            if (!recaptchaResponse) {
              alert('Please complete the reCAPTCHA.');
              return;
            }
            data['g-recaptcha-response'] = recaptchaResponse;
            try {
              await fetch(`${API_BASE}/api/contact`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
              });
              alert('Message sent!');
              contactForm.reset();
              grecaptcha.reset();
            } catch (err) {
              alert('Failed to send message.');
            }
  });
}

// --- Button Glow Effect ---
const btnPrimary = document.querySelector('.btn-primary');
if (btnPrimary) {
  btnPrimary.addEventListener('mouseenter', () => {
    btnPrimary.style.boxShadow = '0 0 32px #4f8cffcc';
  });
  btnPrimary.addEventListener('mouseleave', () => {
    btnPrimary.style.boxShadow = '';
  });
}

// --- Dark Mode + Sidebar Persistence ---
document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;
  const sidebar = document.querySelector('.sidebar');
  const darkBtn = document.querySelector('.dark-toggle-btn');
  const sidebarToggle = document.getElementById('sidebar-toggle');

  // Apply saved theme
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    body.classList.add('dark');
  }

  // Apply saved sidebar state
  const savedSidebar = localStorage.getItem('sidebarCollapsed');
  if (savedSidebar === 'true' && sidebar) {
    sidebar.classList.add('collapsed');
  }

  // Dark mode toggle handler
  if (darkBtn) {
    darkBtn.addEventListener('click', () => {
      body.classList.toggle('dark');
      const isDark = body.classList.contains('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
  }

  // Sidebar collapse toggle handler
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      const isCollapsed = sidebar.classList.contains('collapsed');
      localStorage.setItem('sidebarCollapsed', isCollapsed ? 'true' : 'false');
    });
  }
});
