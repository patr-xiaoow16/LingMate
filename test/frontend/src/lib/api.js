const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

async function request(path, options = {}) {
  const isFormData = typeof FormData !== "undefined" && options.body instanceof FormData;
  const response = await fetch(`${API_BASE}${path}`, {
    headers: isFormData
      ? { ...(options.headers || {}) }
      : {
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
  importAudio(file) {
    const formData = new FormData();
    formData.append("mode", "audio_upload");
    formData.append("file", file);
    return request("/import/audio", {
      method: "POST",
      body: formData,
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
  submitNote(lessonId, moduleKey, message) {
    return request(`/lessons/${lessonId}/notes`, {
      method: "POST",
      body: JSON.stringify({
        action: "ai_note",
        label: String(moduleKey),
        message,
      }),
    });
  },
  deleteNote(lessonId, submissionId) {
    return request(`/lessons/${lessonId}/notes/${submissionId}`, {
      method: "DELETE",
    });
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
