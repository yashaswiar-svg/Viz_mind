const API_BASE_URL = '/api/v1';

function getAuthHeaders() {
  const token = localStorage.getItem('vizmind_access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJson(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    });

    if (response.status === 204) {
      return true;
    }

    const text = await response.text();
    let data = {};
    if (text && text.trim()) {
      try {
        data = JSON.parse(text);
      } catch (parseError) {
        console.warn(`Non-JSON response from ${url}:`, text);
        data = { message: text };
      }
    }

    if (!response.ok) {
      const errorMsg =
        data?.detail ||
        data?.error?.message ||
        data?.message ||
        (response.status === 401 ? 'Invalid credentials. Please check your email/password or create an account.' : `HTTP Error ${response.status}`);
      const err = new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
      err.code = data?.error?.code || 'API_ERROR';
      throw err;
    }

    return data;
  } catch (error) {
    console.error(`API Error (${url}):`, error);
    throw error;
  }
}

// Authentication APIs
export async function registerUser(email, password) {
  return fetchJson(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function loginUser(email, password) {
  return fetchJson(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function refreshUserToken(refreshToken) {
  return fetchJson(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
}

export async function getCurrentUser() {
  return fetchJson(`${API_BASE_URL}/auth/me`);
}

export async function deleteUserAccount() {
  return fetchJson(`${API_BASE_URL}/auth/me`, {
    method: 'DELETE',
  });
}

export async function getAppHealth() {
  return fetchJson(`${API_BASE_URL}/health`);
}

export async function getDbHealth() {
  return fetchJson(`${API_BASE_URL}/health/db`);
}

export async function uploadDataset(file, customName) {
  const formData = new FormData();
  formData.append('file', file);
  if (customName && customName.trim()) {
    formData.append('name', customName.trim());
  }

  const response = await fetch(`${API_BASE_URL}/datasets`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
    },
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    const errorMsg = data?.error?.message || `Upload failed (${response.status})`;
    const err = new Error(errorMsg);
    err.code = data?.error?.code || 'UPLOAD_ERROR';
    throw err;
  }

  return data;
}

export async function listDatasets(page = 1, pageSize = 20) {
  return fetchJson(`${API_BASE_URL}/datasets?page=${page}&page_size=${pageSize}`);
}

export async function getDataset(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}`);
}

export async function deleteDataset(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}`, {
    method: 'DELETE',
  });
}

export async function profileDataset(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/profile`, {
    method: 'POST',
  });
}

export async function getDatasetProfile(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/profile`);
}

export async function preprocessDataset(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/preprocess`, {
    method: 'POST',
  });
}

export async function getPreprocessingReport(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/preprocessing`);
}

export async function generateVisualizations(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/visualizations`, {
    method: 'POST',
  });
}

export async function getVisualizations(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/visualizations`);
}

export async function getVisualizationData(datasetId, visualizationId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/visualizations/${visualizationId}/data`);
}

export async function discoverPatterns(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/patterns`, {
    method: 'POST',
  });
}

export async function getPatterns(datasetId, filters = {}) {
  const queryParams = new URLSearchParams();
  if (filters.patternType) queryParams.append('pattern_type', filters.patternType);
  if (filters.strength) queryParams.append('strength', filters.strength);
  if (filters.significant !== undefined && filters.significant !== null) {
    queryParams.append('significant', filters.significant);
  }

  const queryStr = queryParams.toString() ? `?${queryParams.toString()}` : '';
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/patterns${queryStr}`);
}

export async function getPattern(datasetId, patternId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/patterns/${patternId}`);
}

// Phase 7 — Anomaly Detection & Prediction APIs
export async function runAnomalyDetection(datasetId, method = null) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/anomalies`, {
    method: 'POST',
    body: JSON.stringify(method ? { method } : {}),
  });
}

export async function getLatestAnomalies(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/anomalies`);
}

export async function runPrediction(datasetId, targetColumn = null, problemType = null) {
  const body = {};
  if (targetColumn) body.target_column = targetColumn;
  if (problemType) body.problem_type = problemType;

  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/predictions`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function getLatestPrediction(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/predictions`);
}

export async function getPredictionResults(datasetId, runId, offset = 0, limit = 50) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/predictions/${runId}/results?offset=${offset}&limit=${limit}`);
}

// Phase 8 — AI Insight Engine APIs
export async function generateInsights(datasetId, provider = null) {
  const body = provider ? { provider } : {};
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/insights`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function getInsights(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/insights`);
}

export async function getInsightDetail(datasetId, insightId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/insights/${insightId}`);
}

export async function getInsightRun(datasetId, runId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/insights/runs/${runId}`);
}

// Phase 9 — Natural-Language Data Analyst APIs
export async function createConversation(datasetId, title = 'New Conversation') {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/analyst/conversations`, {
    method: 'POST',
    body: JSON.stringify({ title }),
  });
}

export async function getConversations(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/analyst/conversations`);
}

export async function getConversation(datasetId, conversationId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/analyst/conversations/${conversationId}`);
}

export async function sendMessage(datasetId, conversationId, content) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/analyst/conversations/${conversationId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  });
}

export async function deleteConversation(datasetId, conversationId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/analyst/conversations/${conversationId}`, {
    method: 'DELETE',
  });
}

export async function getAnalystSuggestions(datasetId) {
  return fetchJson(`${API_BASE_URL}/datasets/${datasetId}/analyst/suggestions`);
}



