import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let refreshSubscribers = [];

function onRefreshed(token) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(cb) {
  refreshSubscribers.push(cb);
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) throw new Error("No refresh token available");

  const response = await axios.post(`${baseURL}/accounts/refresh/`, { refresh });
  const access = response.data.access;
  if (access) {
    localStorage.setItem("access", access);
  }
  return access;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (!error.response || error.response.status !== 401) {
      return Promise.reject(error);
    }

    if (localStorage.getItem("pricepulse_guest") === "1" || !localStorage.getItem("refresh")) {
      return Promise.reject(error);
    }

    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    // Queue this request first, then kick off a single shared refresh.
    // Fixes hang where onRefreshed() fired before the initiator subscribed.
    return new Promise((resolve, reject) => {
      addRefreshSubscriber((token) => {
        if (!token) {
          reject(error);
          return;
        }
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${token}`;
        resolve(api(originalRequest));
      });

      if (!isRefreshing) {
        isRefreshing = true;
        refreshAccessToken()
          .then((newToken) => onRefreshed(newToken))
          .catch((refreshErr) => {
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");
            onRefreshed(null);
            window.location.href = "/login";
            reject(refreshErr);
          })
          .finally(() => {
            isRefreshing = false;
          });
      }
    });
  }
);

export default api;
