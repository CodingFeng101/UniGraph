#!/bin/sh
set -eu

config_json="$(jq -cn \
  --arg host_url "${VITE_HOST_URL:-}" \
  --arg api_base_url "${VITE_API_BASE_URL:-/knowg}" \
  --arg image_api "${VITE_SHOW_IMAGE_API:-/knowg/v1/image/}" \
  --arg user_info_url "${VITE_USER_INFO_SSO_URL:-/knowg/v1/sys/users/me}" \
  --arg auth_key "${VITE_AUTH_AES_SECRET_KEY:-}" \
  '{
    VITE_HOST_URL: $host_url,
    VITE_API_BASE_URL: $api_base_url,
    VITE_SHOW_IMAGE_API: $image_api,
    VITE_USER_INFO_SSO_URL: $user_info_url,
    VITE_AUTH_AES_SECRET_KEY: $auth_key
  }')"

printf 'window.FRONTEND_CONFIG = %s;\n' "$config_json" >/usr/share/nginx/html/config.js
