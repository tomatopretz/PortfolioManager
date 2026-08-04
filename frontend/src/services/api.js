const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

const fetchJson = async (path, options = {}) => {
  const response = await fetch(`${apiUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  // A 5xx from a proxy can arrive as HTML; surface the status rather than a JSON parse error.
  let data;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new ApiError(data?.error || `API error: ${response.status}`, response.status, data);
  }

  return data;
};

export const get = (path) => fetchJson(path, { method: 'GET' });

export const post = (path, body) => fetchJson(path, { method: 'POST', body: JSON.stringify(body) });

export const patch = (path, body) =>
  fetchJson(path, {
    method: 'PATCH',
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });
