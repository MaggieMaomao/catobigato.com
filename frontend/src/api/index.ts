/**
 * Axios-based API client for CatobiGato backend.
 * All API calls go through this client with proper auth token injection.
 */

import axios from "axios";
import keycloak from "../auth/keycloak";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { "Content-Type": "application/json" },
  withCredentials: false,
});

// ── Auth token interceptor ──────────────────────────────────────────────────
// Automatically attaches Keycloak access token to every request
api.interceptors.request.use(async (config) => {
  if (keycloak.authenticated && keycloak.token) {
    // Ensure token is still valid (refresh if needed)
    try {
      const refreshed = await keycloak.updateToken(300);
      if (refreshed) {
        config.headers.Authorization = `Bearer ${keycloak.token}`;
      }
    } catch {
      // Token refresh failed — try anyway with current token
      config.headers.Authorization = `Bearer ${keycloak.token}`;
    }
  }
  return config;
});

// ── Error handler interceptor ──────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If 401, try to refresh token once
    if (error.response?.status === 401 && keycloak.authenticated) {
      try {
        const refreshed = await keycloak.updateToken(300);
        if (refreshed) {
          // Retry original request with new token
          error.config.headers.Authorization = `Bearer ${keycloak.token}`;
          return api.request(error.config);
        }
      } catch {
        // Refresh failed — redirect to login
        keycloak.login();
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth ───────────────────────────────────────────────────────────────────
export const authApi = {
  getProfile: () => api.get("/accounts/profile/"),
  updateProfile: (data: object) => api.put("/accounts/profile/", data),
  getPublicProfile: (userId: string) => api.get(`/accounts/profile/${userId}/`),
};

// ── Calculator ─────────────────────────────────────────────────────────────
export const calculatorApi = {
  evaluate: (expression: string, mode = "basic") =>
    api.post("/calculator/evaluate/", { expression, mode }),
  simplify: (expression: string) =>
    api.post("/calculator/simplify/", { expression }),
  factor: (expression: string) =>
    api.post("/calculator/factor/", { expression }),
  expand: (expression: string) =>
    api.post("/calculator/expand/", { expression }),
  solve: (equation: string, variable = "x") =>
    api.post("/calculator/solve/", { equation, variable }),
  derivative: (expression: string, variable = "x", order = 1) =>
    api.post("/calculator/derivative/", { expression, variable, order }),
  integrate: (
    expression: string,
    variable = "x",
    lower?: number,
    upper?: number
  ) => api.post("/calculator/integrate/", { expression, variable, lower, upper }),
  plot: (
    expression: string,
    variable = "x",
    xRange = [-10, 10],
    numPoints = 500
  ) =>
    api.post("/calculator/plot/", {
      expression,
      variable,
      x_range: xRange,
      num_points: numPoints,
    }),
  // Custom functions
  listFunctions: () => api.get("/calculator/functions/"),
  createFunction: (data: object) => api.post("/calculator/functions/", data),
  updateFunction: (id: string, data: object) =>
    api.put(`/calculator/functions/${id}/`, data),
  deleteFunction: (id: string) =>
    api.delete(`/calculator/functions/${id}/`),
  evaluateFunction: (id: string, params: object) =>
    api.post(`/calculator/functions/${id}/evaluate/`, { params }),
  // History
  getHistory: () => api.get("/calculator/history/"),
  clearHistory: () => api.delete("/calculator/history/"),
};

// ── Learning ────────────────────────────────────────────────────────────────
export const learningApi = {
  // Notes
  listNotes: (params?: object) => api.get("/learning/notes/", { params }),
  getNote: (id: string) => api.get(`/learning/notes/${id}/`),
  createNote: (data: object) => api.post("/learning/notes/", data),
  updateNote: (id: string, data: object) =>
    api.put(`/learning/notes/${id}/`, data),
  deleteNote: (id: string) => api.delete(`/learning/notes/${id}/`),
  // Questions
  listQuestions: (params?: object) =>
    api.get("/learning/questions/", { params }),
  getQuestion: (id: string) => api.get(`/learning/questions/${id}/`),
  createQuestion: (data: object) => api.post("/learning/questions/", data),
  // Question sets
  listQuestionSets: (params?: object) =>
    api.get("/learning/question-sets/", { params }),
  getQuestionSet: (id: string) =>
    api.get(`/learning/question-sets/${id}/`),
  createQuestionSet: (data: object) =>
    api.post("/learning/question-sets/", data),
};

// ── Social ──────────────────────────────────────────────────────────────────
export const socialApi = {
  follow: (userId: string) => api.post(`/accounts/follow/${userId}/`),
  unfollow: (userId: string) => api.delete(`/accounts/follow/${userId}/`),
  getFollowers: () => api.get("/accounts/followers/"),
  getFollowing: () => api.get("/accounts/following/"),
  checkFollowStatus: (userId: string) =>
    api.get(`/accounts/follow-status/${userId}/`),
};

// ── Visual Math ──────────────────────────────────────────────────────────────
export const visualMathApi = {
  solve: (data: {
    user_input: string;
    mode?: string;
    output_mode?: string;
    quality?: string;
    image_base64?: string;
  }) => api.post("/visual-math/solve/", data),
  getAnimationStatus: (projectId: string) =>
    api.get(`/visual-math/animations/${projectId}/status/`),
  listSketches: () => api.get("/visual-math/sketches/"),
  getSketch: (id: string) => api.get(`/visual-math/sketches/${id}/`),
  createSketch: (data: object) => api.post("/visual-math/sketches/", data),
  listAnimations: () => api.get("/visual-math/animations/"),
};

export default api;