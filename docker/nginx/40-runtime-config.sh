#!/bin/sh
set -eu

cat >/usr/share/nginx/html/config.js <<EOF
window.FRONTEND_CONFIG = {
  VITE_HOST_URL: "${VITE_HOST_URL:-}",
  VITE_API_BASE_URL: "${VITE_API_BASE_URL:-/knowg}",
  VITE_SHOW_IMAGE_API: "${VITE_SHOW_IMAGE_API:-/knowg/v1/image/}",
  VITE_USER_INFO_SSO_URL: "${VITE_USER_INFO_SSO_URL:-/knowg/v1/sys/users/me}"
};
EOF
