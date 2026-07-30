const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export const fetchJson = async (path, options = {}) => {
  const url = `${apiUrl}${path}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new ApiError(
      data.error || `API error: ${response.status}`,
      response.status,
      data
    );
  }

  return data;
};

export const get = (path) => fetchJson(path, { method: 'GET' });

export const post = (path, body) =>
  fetchJson(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });

export default {
  get,
  post,
  ApiError,
};
