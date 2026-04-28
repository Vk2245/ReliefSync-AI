/**
 * ReliefSync-AI API Client
 * Handles all communication with the FastAPI backend.
 */
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8080/api/v1'
  : '/api/v1';

class ReliefSyncAPI {
  constructor() {
    this.token = localStorage.getItem('rs_token') || '';
  }

  get headers() {
    const h = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  async request(method, path, body = null) {
    const opts = { method, headers: this.headers };
    if (body) opts.body = JSON.stringify(body);
    try {
      const res = await fetch(`${API_BASE}${path}`, opts);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return res.json();
    } catch (e) {
      console.error(`API ${method} ${path}:`, e);
      throw e;
    }
  }

  // Emergencies
  createEmergency(data) { return this.request('POST', '/emergencies/', data); }
  listEmergencies(params = '') { return this.request('GET', `/emergencies/?${params}`); }
  getEmergency(id) { return this.request('GET', `/emergencies/${id}`); }
  updateStatus(id, status) { return this.request('PATCH', `/emergencies/${id}/status?new_status=${status}`); }
  predictDemand(id, hours = 24) { return this.request('POST', `/emergencies/${id}/predict-demand`, { emergency_id: id, prediction_hours: hours }); }

  // Volunteers
  registerVolunteer(data) { return this.request('POST', '/volunteers/register', data); }
  listVolunteers() { return this.request('GET', '/volunteers/'); }
  matchVolunteers(taskId, emergencyId) { return this.request('POST', '/volunteers/match', { task_id: taskId, emergency_id: emergencyId }); }

  // Tasks
  createTask(data) { return this.request('POST', '/tasks/', data); }
  listTasks(emergencyId = '') { return this.request('GET', `/tasks/?emergency_id=${emergencyId}`); }
  assignVolunteer(taskId, volId) { return this.request('POST', `/tasks/${taskId}/assign/${volId}`); }
  completeTask(taskId) { return this.request('PATCH', `/tasks/${taskId}/complete`); }

  // Analytics
  getDashboard() { return this.request('GET', '/analytics/dashboard'); }
  translate(text, from, to) { return this.request('POST', '/translate', { text, source_language: from, target_language: to }); }

  // Resources
  createResource(data) { return this.request('POST', '/resources', data); }
  listResources() { return this.request('GET', '/resources'); }

  // Organizations
  createOrg(data) { return this.request('POST', '/organizations', data); }

  // Health
  health() { return this.request('GET', '/../health'); }
}

window.api = new ReliefSyncAPI();
