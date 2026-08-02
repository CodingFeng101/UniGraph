const localBackendHost = window.location.hostname || '127.0.0.1';
const localBackendOrigin = `http://${localBackendHost}:8000`;

window.FRONTEND_CONFIG = window.FRONTEND_CONFIG || {
  VITE_HOST_URL: localBackendOrigin,
  VITE_API_BASE_URL: `${localBackendOrigin}/knowg`,
  VITE_SHOW_IMAGE_API: `${localBackendOrigin}/knowg/v1/image/`,
  VITE_USER_INFO_SSO_URL: `${localBackendOrigin}/knowg/v1/sys/users/me`,
  VITE_AUTH_AES_SECRET_KEY: '',
};
