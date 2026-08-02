/**
 * UniGraph 全局配置
 * 对接旧系统后端 API
 */
const runtimeConfig = window.FRONTEND_CONFIG || {};
const browserHost = window.location.hostname || '127.0.0.1';
const browserProtocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
const defaultBackend = `${browserProtocol}//${browserHost}:8000`;

export const AppConfig = window.AppConfig = {
  // 后端 API 基础地址（本地启动，端口8000）
  API_BASE_URL: runtimeConfig.VITE_API_BASE_URL || `${defaultBackend}/knowg`,
  // 后端主机地址（用于 SSE 流式请求）
  HOST_URL: runtimeConfig.VITE_HOST_URL || defaultBackend,
  // 图片显示 API
  SHOW_IMAGE_API: runtimeConfig.VITE_SHOW_IMAGE_API || `${defaultBackend}/knowg/v1/image/`,
  // API 版本前缀
  API_V1: '/v1',
  // kgbase 模块前缀
  KG_PREFIX: '/v1/kg',
  // 登录加密密钥（AES-256-CBC，与后端一致）
  ENCRYPT_SECRET_KEY: runtimeConfig.VITE_AUTH_AES_SECRET_KEY || import.meta.env.VITE_AUTH_AES_SECRET_KEY || '',
};
