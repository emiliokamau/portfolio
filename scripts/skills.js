// --- API Base URL ---
const API_BASE = (
  (typeof window !== 'undefined' && window.API_BASE)
    ? window.API_BASE
    : 'https://portfolio-emiliokamau.up.railway.app'
).replace(/\/+$/, '');

const fallbackSkills = [
  'Python',
  'Django',
  'Flask',
  'Computer Vision (SafeMotion)',
  'Artificial Intelligence (MedicAI, SafeMotion)',
  'Data Science',
  'JavaScript',
  'HTML',
  'CSS',
];

// --- Fetch and Render Skills ---
async function loadSkills() {
  const dashboard = document.getElementById('skills-dashboard');
  if (!dashboard) return;
  try {
    const res = await fetch(`${API_BASE}/api/skills`);
    const skills = await res.json();
    dashboard.innerHTML = '';
    const source = Array.isArray(skills) && skills.length
      ? skills.map((skill) => skill.name)
      : fallbackSkills;
    source.forEach((skillName) => {
      const div = document.createElement('div');
      div.className = 'skill-badge';
      div.innerHTML = `<span>${skillName}</span>`;
      dashboard.appendChild(div);
    });
  } catch (e) {
    dashboard.innerHTML = '';
    fallbackSkills.forEach((skillName) => {
      const div = document.createElement('div');
      div.className = 'skill-badge';
      div.innerHTML = `<span>${skillName}</span>`;
      dashboard.appendChild(div);
    });
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
