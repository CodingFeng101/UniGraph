import { AppConfig } from '@/api/runtime/config';

export function resolveImageUrl(path) {
  if (!path) return '';
  if (/^(https?:|data:|blob:)/i.test(path)) return path;

  const backendOrigin = AppConfig.HOST_URL || window.location.origin;
  if (path.startsWith('/knowg/')) {
    return new URL(path, backendOrigin).href;
  }

  const imageBase = new URL(AppConfig.SHOW_IMAGE_API || '/knowg/v1/image/', backendOrigin);
  return new URL(path.replace(/^\/+/, ''), imageBase.href.replace(/\/?$/, '/')).href;
}
