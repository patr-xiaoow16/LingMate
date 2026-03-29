const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
}

export const api = {
  getHome() {
    return request("/home");
  },
  importMaterial(payload) {
    return request("/import", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  getAnalysis(lessonId) {
    return request(`/lessons/${lessonId}/analysis`);
  },
  startLesson(lessonId) {
    return request(`/lessons/${lessonId}/start`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  },
  getWorkspace(lessonId, moduleIndex = null) {
    const suffix = moduleIndex ? `?module=${moduleIndex}` : "";
    return request(`/lessons/${lessonId}/workspace${suffix}`);
  },
  completeModule(lessonId, moduleKey) {
    return request(`/lessons/${lessonId}/modules/${moduleKey}/complete`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  },
  moduleAction(lessonId, moduleKey, payload) {
    return request(`/lessons/${lessonId}/modules/${moduleKey}/action`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  getReport(lessonId) {
    return request(`/lessons/${lessonId}/report`);
  },
};
