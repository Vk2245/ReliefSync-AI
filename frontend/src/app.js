/**
 * ReliefSync-AI Frontend Application
 * Handles all UI interactions, routing, data rendering, and charts.
 */
document.addEventListener('DOMContentLoaded', () => {
  // ── Demo Data ──────────────────────────────────────
  const EMERGENCIES = [
    { id: 'e1', title: 'Severe Flooding — Chennai Coast', emergency_type: 'flood', severity: 'critical', description: 'Massive flooding due to cyclone remnants. 12 districts affected, water levels rising rapidly.', location: { latitude: 13.08, longitude: 80.27, city: 'Chennai' }, affected_people: 25000, status: 'active', created_at: new Date(Date.now() - 3600000).toISOString(), assigned_volunteers: 145, ai_severity_score: 0.96 },
    { id: 'e2', title: 'Earthquake 6.8M — Gujarat', emergency_type: 'earthquake', severity: 'critical', description: 'Strong earthquake in Kutch region. Multiple building collapses reported, aftershocks continuing.', location: { latitude: 23.24, longitude: 69.66, city: 'Bhuj' }, affected_people: 8500, status: 'active', created_at: new Date(Date.now() - 7200000).toISOString(), assigned_volunteers: 89, ai_severity_score: 0.94 },
    { id: 'e3', title: 'Industrial Fire — Mumbai Docks', emergency_type: 'fire', severity: 'high', description: 'Chemical storage facility fire at Mumbai port. Toxic fumes reported in 3km radius.', location: { latitude: 18.93, longitude: 72.84, city: 'Mumbai' }, affected_people: 3200, status: 'active', created_at: new Date(Date.now() - 10800000).toISOString(), assigned_volunteers: 67, ai_severity_score: 0.87 },
    { id: 'e4', title: 'Landslide — Himachal Pradesh', emergency_type: 'landslide', severity: 'high', description: 'Major landslide blocking NH-5. Several villages cut off, 200+ people stranded.', location: { latitude: 31.10, longitude: 77.17, city: 'Shimla' }, affected_people: 1200, status: 'active', created_at: new Date(Date.now() - 18000000).toISOString(), assigned_volunteers: 34, ai_severity_score: 0.82 },
    { id: 'e5', title: 'Dengue Outbreak — Kolkata', emergency_type: 'epidemic', severity: 'medium', description: 'Dengue cases surging in eastern Kolkata. 450+ confirmed cases in the past week.', location: { latitude: 22.57, longitude: 88.36, city: 'Kolkata' }, affected_people: 2800, status: 'active', created_at: new Date(Date.now() - 86400000).toISOString(), assigned_volunteers: 56, ai_severity_score: 0.71 },
    { id: 'e6', title: 'Road Accident — NH-44', emergency_type: 'accident', severity: 'medium', description: 'Multi-vehicle pileup on NH-44 near Hyderabad. 15 vehicles involved, rescue underway.', location: { latitude: 17.38, longitude: 78.49, city: 'Hyderabad' }, affected_people: 45, status: 'active', created_at: new Date(Date.now() - 5400000).toISOString(), assigned_volunteers: 12, ai_severity_score: 0.65 },
  ];

  const VOLUNTEERS = [
    { uid: 'v1', display_name: 'Dr. Priya Sharma', skills: ['medical', 'first_aid', 'triage'], languages: ['en', 'hi'], trust_score: 94, status: 'on_task', tasks_completed: 47 },
    { uid: 'v2', display_name: 'Rahul Verma', skills: ['rescue', 'swimming', 'driving'], languages: ['en', 'hi', 'mr'], trust_score: 88, status: 'available', tasks_completed: 32 },
    { uid: 'v3', display_name: 'Aisha Khan', skills: ['counseling', 'translation', 'logistics'], languages: ['en', 'hi', 'ur', 'ar'], trust_score: 91, status: 'available', tasks_completed: 28 },
    { uid: 'v4', display_name: 'James Chen', skills: ['engineering', 'construction', 'electrical'], languages: ['en', 'zh'], trust_score: 85, status: 'on_task', tasks_completed: 19 },
    { uid: 'v5', display_name: 'Maria Santos', skills: ['nursing', 'first_aid', 'childcare'], languages: ['en', 'pt', 'es'], trust_score: 92, status: 'available', tasks_completed: 55 },
    { uid: 'v6', display_name: 'Vikram Patel', skills: ['driving', 'logistics', 'communication'], languages: ['en', 'hi', 'gu'], trust_score: 79, status: 'available', tasks_completed: 15 },
    { uid: 'v7', display_name: 'Fatima Ali', skills: ['medical', 'pharmacy', 'lab_tech'], languages: ['en', 'ar', 'fr'], trust_score: 96, status: 'on_task', tasks_completed: 63 },
    { uid: 'v8', display_name: 'Arjun Reddy', skills: ['rescue', 'firefighting', 'first_aid'], languages: ['en', 'te', 'hi'], trust_score: 90, status: 'available', tasks_completed: 41 },
  ];

  const ACTIVITIES = [
    { icon: 'fa-triangle-exclamation', color: 'critical', text: 'New CRITICAL emergency reported: Chennai Flooding', time: '2 min ago' },
    { icon: 'fa-user-check', color: 'success', text: '45 volunteers deployed to Gujarat earthquake zone', time: '8 min ago' },
    { icon: 'fa-brain', color: 'warning', text: 'AI predicted medical supply shortage in Mumbai — auto-reorder triggered', time: '15 min ago' },
    { icon: 'fa-check-circle', color: 'success', text: 'Task #T-234 completed: Evacuation of Shimla sector B', time: '32 min ago' },
    { icon: 'fa-route', color: 'info', text: 'Route optimization saved 34% travel time for Kolkata response team', time: '1 hour ago' },
    { icon: 'fa-shield-halved', color: 'warning', text: 'Fraud detection flagged 2 suspicious volunteer registrations', time: '2 hours ago' },
  ];

  // ── Navigation ─────────────────────────────────────
  const navLinks = document.querySelectorAll('.nav-link');
  const pages = document.querySelectorAll('.page');

  function navigateTo(pageName) {
    pages.forEach(p => p.classList.remove('active'));
    navLinks.forEach(l => l.classList.remove('active'));
    const target = document.getElementById(`page-${pageName}`);
    if (target) target.classList.add('active');
    const link = document.querySelector(`[data-page="${pageName}"]`);
    if (link) link.classList.add('active');
    if (pageName === 'analytics') initCharts();
    if (pageName === 'map') initFullMap();
  }

  navLinks.forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      navigateTo(link.dataset.page);
    });
  });

  // ── Render Emergency List (Dashboard) ──────────────
  function renderEmergencyList() {
    const list = document.getElementById('emergency-list');
    list.innerHTML = EMERGENCIES.slice(0, 5).map(e => `
      <div class="emergency-item" data-id="${e.id}">
        <div class="severity-dot ${e.severity}"></div>
        <div class="emergency-info">
          <strong>${e.title}</strong>
          <span>${e.location.city} · ${e.affected_people.toLocaleString()} affected · ${e.assigned_volunteers} volunteers</span>
        </div>
        <div class="emergency-meta">
          <span class="severity-badge ${e.severity}">${e.severity}</span><br>
          <span>${timeAgo(e.created_at)}</span>
        </div>
      </div>
    `).join('');
  }

  // ── Render Emergency Grid ──────────────────────────
  function renderEmergencyGrid(filter = 'all') {
    const grid = document.getElementById('emergency-grid');
    const filtered = filter === 'all' ? EMERGENCIES : EMERGENCIES.filter(e => e.severity === filter);
    grid.innerHTML = filtered.map(e => `
      <div class="emergency-detail-card ${e.severity}">
        <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:10px">
          <span style="font-size:24px">${typeEmoji(e.emergency_type)}</span>
          <span class="severity-badge ${e.severity}">${e.severity}</span>
        </div>
        <div class="emergency-title">${e.title}</div>
        <div class="emergency-desc">${e.description}</div>
        <div style="display:flex;gap:12px;margin-bottom:12px;flex-wrap:wrap">
          <span class="skill-tag"><i class="fas fa-location-dot"></i> ${e.location.city}</span>
          <span class="skill-tag"><i class="fas fa-users"></i> ${e.affected_people.toLocaleString()}</span>
          <span class="skill-tag"><i class="fas fa-people-group"></i> ${e.assigned_volunteers} deployed</span>
        </div>
        <div class="emergency-footer">
          <span>AI Confidence: ${((e.ai_severity_score || 0) * 100).toFixed(0)}%</span>
          <span>${timeAgo(e.created_at)}</span>
        </div>
      </div>
    `).join('');
  }

  // ── Render Volunteers ──────────────────────────────
  function renderVolunteers() {
    const grid = document.getElementById('volunteer-grid');
    grid.innerHTML = VOLUNTEERS.map(v => `
      <div class="volunteer-card">
        <div class="volunteer-header">
          <img class="volunteer-avatar" src="https://ui-avatars.com/api/?name=${encodeURIComponent(v.display_name)}&background=${v.status === 'on_task' ? '6366f1' : '22c55e'}&color=fff&size=44" alt="${v.display_name}">
          <div>
            <div class="volunteer-name">${v.display_name}</div>
            <div class="volunteer-role">${v.status === 'on_task' ? '🟢 On Task' : '⚪ Available'} · ${v.tasks_completed} tasks</div>
          </div>
        </div>
        <div class="skill-tags">${v.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
        <div style="margin-top:12px;display:flex;justify-content:space-between;font-size:12px;color:var(--text-secondary)">
          <span>Trust: ${v.trust_score}/100</span>
          <span>🌐 ${v.languages.join(', ')}</span>
        </div>
        <div class="trust-bar"><div class="trust-fill" style="width:${v.trust_score}%"></div></div>
      </div>
    `).join('');
  }

  // ── Render Activity Feed ───────────────────────────
  function renderActivity() {
    const feed = document.getElementById('activity-feed');
    feed.innerHTML = ACTIVITIES.map(a => `
      <div class="insight-item">
        <div class="insight-icon ${a.color}"><i class="fas ${a.icon}"></i></div>
        <div class="insight-content">
          <p style="color:var(--text-primary);font-size:13px">${a.text}</p>
          <span class="insight-time">${a.time}</span>
        </div>
      </div>
    `).join('');
  }

  // ── Filter Chips ───────────────────────────────────
  document.querySelectorAll('.filter-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      renderEmergencyGrid(chip.dataset.filter);
    });
  });

  // ── Modal ──────────────────────────────────────────
  const modal = document.getElementById('emergency-modal');
  document.getElementById('btn-report-emergency')?.addEventListener('click', () => modal.classList.add('active'));
  document.getElementById('btn-new-emergency')?.addEventListener('click', () => modal.classList.add('active'));
  document.getElementById('modal-close')?.addEventListener('click', () => modal.classList.remove('active'));
  modal?.addEventListener('click', e => { if (e.target === modal) modal.classList.remove('active'); });

  document.getElementById('emergency-form')?.addEventListener('submit', e => {
    e.preventDefault();
    const newE = {
      id: 'e' + (EMERGENCIES.length + 1),
      title: document.getElementById('em-title').value,
      emergency_type: document.getElementById('em-type').value,
      severity: 'analyzing',
      description: document.getElementById('em-description').value,
      location: { latitude: parseFloat(document.getElementById('em-lat').value) || 20.5, longitude: parseFloat(document.getElementById('em-lng').value) || 78.9, city: 'Reported' },
      affected_people: parseInt(document.getElementById('em-affected').value) || 0,
      status: 'active', created_at: new Date().toISOString(), assigned_volunteers: 0, ai_severity_score: null,
    };
    // Simulate AI prediction
    setTimeout(() => {
      const severities = ['critical', 'high', 'medium', 'low'];
      newE.severity = newE.affected_people > 1000 ? 'critical' : newE.affected_people > 100 ? 'high' : newE.affected_people > 10 ? 'medium' : 'low';
      newE.ai_severity_score = 0.7 + Math.random() * 0.25;
      EMERGENCIES.unshift(newE);
      renderEmergencyList();
      renderEmergencyGrid();
      document.getElementById('stat-active-emergencies').textContent = EMERGENCIES.length;
    }, 800);
    modal.classList.remove('active');
    e.target.reset();
  });

  // ── Notification Panel ─────────────────────────────
  document.getElementById('notification-bell')?.addEventListener('click', () => {
    document.getElementById('notification-panel').classList.toggle('active');
  });

  // ── AI Console ─────────────────────────────────────
  document.getElementById('btn-run-ai')?.addEventListener('click', async () => {
    const input = document.getElementById('ai-input').value.trim();
    if (!input) return;
    const output = document.getElementById('ai-output');
    output.innerHTML = '<div style="color:var(--accent)"><i class="fas fa-spinner fa-spin"></i> Running Gemini 2.0 Flash analysis...</div>';

    // Simulate AI response (replace with real API call in production)
    setTimeout(() => {
      const severity = input.length > 200 ? 'critical' : input.length > 100 ? 'high' : 'medium';
      const confidence = (0.85 + Math.random() * 0.12).toFixed(3);
      output.innerHTML = `<pre style="color:var(--success);white-space:pre-wrap">{
  "severity": "${severity}",
  "confidence_score": ${confidence},
  "reasoning": "Based on FEMA SLG-101 crisis assessment framework, the described situation indicates ${severity}-level severity due to scale of impact and infrastructure damage.",
  "estimated_response_time_hours": ${severity === 'critical' ? 1 : severity === 'high' ? 4 : 12},
  "recommended_resources": ["medical_supplies", "water", "shelter", "rescue_teams"],
  "escalation_needed": ${severity === 'critical'},
  "risk_factors": ["Infrastructure damage", "Population density", "Access limitations"],
  "immediate_actions": ["Deploy first responders", "Establish command center", "Activate volunteer network"],
  "ai_model": "gemini-2.0-flash",
  "processing_time_ms": ${(200 + Math.random() * 800).toFixed(0)}
}</pre>`;
    }, 1500);
  });

  document.getElementById('btn-test-severity')?.addEventListener('click', () => navigateTo('ai'));

  // ── Charts ─────────────────────────────────────────
  function initCharts() {
    const chartOpts = { responsive: true, plugins: { legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } } }, scales: { x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,.08)' } }, y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,.08)' } } } };

    // Trends
    const ctx1 = document.getElementById('chart-trends');
    if (ctx1 && !ctx1._chart) {
      ctx1._chart = new Chart(ctx1, { type: 'line', data: { labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], datasets: [{ label: 'Emergencies', data: [3,5,2,8,6,4,12], borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,.1)', fill: true, tension: .4 }, { label: 'Resolved', data: [2,4,2,6,5,4,8], borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,.1)', fill: true, tension: .4 }] }, options: chartOpts });
    }

    // Volunteers
    const ctx2 = document.getElementById('chart-volunteers');
    if (ctx2 && !ctx2._chart) {
      ctx2._chart = new Chart(ctx2, { type: 'bar', data: { labels: ['Medical','Rescue','Logistics','Engineering','Counseling','Transport'], datasets: [{ label: 'Deployed', data: [120,89,156,45,67,78], backgroundColor: 'rgba(99,102,241,.7)' }, { label: 'Available', data: [45,34,67,23,28,41], backgroundColor: 'rgba(99,102,241,.25)' }] }, options: chartOpts });
    }

    // Response time
    const ctx3 = document.getElementById('chart-response');
    if (ctx3 && !ctx3._chart) {
      ctx3._chart = new Chart(ctx3, { type: 'doughnut', data: { labels: ['< 5 min','5-15 min','15-30 min','30-60 min','> 60 min'], datasets: [{ data: [35,40,15,7,3], backgroundColor: ['#22c55e','#6366f1','#f59e0b','#ef4444','#dc2626'] }] }, options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } } } });
    }

    // Resources
    const ctx4 = document.getElementById('chart-resources');
    if (ctx4 && !ctx4._chart) {
      ctx4._chart = new Chart(ctx4, { type: 'radar', data: { labels: ['Food','Water','Medical','Shelter','Transport','Blood'], datasets: [{ label: 'Demand', data: [85,92,78,65,45,88], borderColor: '#ef4444', backgroundColor: 'rgba(239,68,68,.15)' }, { label: 'Supply', data: [70,60,82,55,50,40], borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,.15)' }] }, options: { responsive: true, scales: { r: { ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,.1)' }, pointLabels: { color: '#94a3b8' } } }, plugins: { legend: { labels: { color: '#94a3b8' } } } } });
    }
  }

  // ── Mini Map (Placeholder) ─────────────────────────
  function initMiniMap() {
    const el = document.getElementById('mini-map');
    if (el) el.innerHTML = '<div style="height:100%;display:grid;place-items:center;background:linear-gradient(135deg,#1a1a2e,#16213e);border-radius:8px"><div style="text-align:center;color:var(--text-muted)"><i class="fas fa-map-location-dot" style="font-size:48px;margin-bottom:12px;color:var(--accent);display:block"></i><p>Google Maps integration</p><p style="font-size:11px;margin-top:4px">Add GOOGLE_MAPS_API_KEY to enable</p></div></div>';
  }

  function initFullMap() {
    const el = document.getElementById('full-map');
    if (el && !el._init) {
      el._init = true;
      el.innerHTML = '<div style="height:100%;display:grid;place-items:center;background:linear-gradient(135deg,#1a1a2e,#16213e)"><div style="text-align:center;color:var(--text-muted);max-width:400px"><i class="fas fa-map-location-dot" style="font-size:64px;margin-bottom:16px;color:var(--accent);display:block"></i><h3 style="margin-bottom:8px;color:var(--text-primary)">Crisis Heatmap</h3><p>Real-time visualization of active emergencies using Google Maps Heatmap Layer, volunteer positions, and optimized dispatch routes.</p><p style="margin-top:12px;font-size:12px">Configure GOOGLE_MAPS_API_KEY in .env</p></div></div>';
    }
  }

  // ── Utils ──────────────────────────────────────────
  function timeAgo(iso) {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  }

  function typeEmoji(t) {
    const map = { flood: '🌊', earthquake: '🏚️', fire: '🔥', medical: '🏥', cyclone: '🌀', epidemic: '🦠', accident: '💥', landslide: '⛰️', violence: '⚠️', other: '📋' };
    return map[t] || '📋';
  }

  // ── Animate Stats ──────────────────────────────────
  function animateStats() {
    const targets = { 'stat-active-emergencies': 12, 'stat-active-volunteers': 847, 'stat-tasks-completed': 156 };
    Object.entries(targets).forEach(([id, target]) => {
      const el = document.getElementById(id);
      if (!el) return;
      let current = 0;
      const step = Math.ceil(target / 30);
      const interval = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = current;
        if (current >= target) clearInterval(interval);
      }, 30);
    });
  }

  // ── Initialize ─────────────────────────────────────
  renderEmergencyList();
  renderEmergencyGrid();
  renderVolunteers();
  renderActivity();
  initMiniMap();
  animateStats();
});
