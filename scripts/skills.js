// --- API Base URL ---
const API_BASE = 'https://portfolio-emiliokamau.up.railway.app/';

// --- Fetch and Render Skills ---
async function loadSkills() {
  const dashboard = document.getElementById('skills-dashboard');
  if (!dashboard) return;
  try {
    const res = await fetch(`${API_BASE}/api/skills`);
    const skills = await res.json();
    dashboard.innerHTML = '';
    skills.forEach(skill => {
      const div = document.createElement('div');
      div.className = 'skill-badge';
      div.innerHTML = `<span>${skill.name}</span>`;
      dashboard.appendChild(div);
    });
  } catch (e) {
    dashboard.innerHTML = '<p>Unable to load skills.</p>';
  }
}
loadSkills();

// --- Add Skill Form ---
const addSkillForm = document.getElementById('add-skill-form');
if (addSkillForm) {
  addSkillForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const skillName = document.getElementById('skill-name').value.trim();
    if (!skillName) return;
    try {
      await fetch(`${API_BASE}/api/skills`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: skillName })
      });
      loadSkills();
      addSkillForm.reset();
    } catch (err) {
      alert('Failed to add skill.');
    }
  });
}
