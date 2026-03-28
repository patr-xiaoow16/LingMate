const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const config = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  };

  const response = await fetch(`${API_BASE}${path}`, config);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

export const api = {
  getHome() {
    return request("/home");
  },
  importLesson(payload) {
    return request("/import", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  getAnalysis(lessonId) {
    return request(`/lessons/${lessonId}/analysis`);
  },
  startLesson(lessonId) {
    return request(`/lessons/${lessonId}/start`, { method: "POST" });
  },
  getWorkspace(lessonId, moduleKey) {
    const query = moduleKey ? `?module=${moduleKey}` : "";
    return request(`/lessons/${lessonId}/workspace${query}`);
  },
  coachModule(lessonId, moduleKey, text) {
    return request(`/lessons/${lessonId}/modules/${moduleKey}/coach`, {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  },
  completeModule(lessonId, moduleKey) {
    return request(`/lessons/${lessonId}/modules/${moduleKey}/complete`, {
      method: "POST",
    });
  },
  getReport(lessonId) {
    return request(`/lessons/${lessonId}/report`);
  },
  getReview(lessonId) {
    const query = lessonId ? `?lesson_id=${lessonId}` : "";
    return request(`/review${query}`);
  },
};
