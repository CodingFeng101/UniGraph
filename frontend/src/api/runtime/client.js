/**
 * API 请求封装
 * 基于原生 fetch，对接旧系统 FastAPI 后端
 * 响应格式统一为 { code, msg, data }
 */
import { Auth } from './auth';
import { AppConfig } from './config';

export const API = window.API = {
  /**
   * 发送请求
   * @param {string} method - HTTP 方法
   * @param {string} path - API 路径（相对于 API_BASE_URL，如 /v1/kg/base/all/）
   * @param {object} options - fetch 选项
   * @returns {Promise<object>} 响应数据 { code, msg, data }
   */
  async request(method, path, options = {}) {
    const token = Auth.getToken();
    const headers = {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const config = { method, headers, ...options };

    // 处理请求体
    if (options.body !== undefined) {
      if (options.body instanceof FormData) {
        config.body = options.body;
      } else if (typeof options.body === 'object') {
        config.body = JSON.stringify(options.body);
      } else {
        config.body = options.body;
      }
    }

    try {
      const response = await fetch(`${AppConfig.API_BASE_URL}${path}`, config);

      // 401 未授权，跳转登录
      if (response.status === 401 && path !== '/v1/auth/login') {
        Auth.clearToken();
        Auth.clearUserInfo();
        const redirect = `${window.location.pathname}${window.location.search}${window.location.hash}`;
        window.location.replace(`${import.meta.env.BASE_URL}login?redirect=${encodeURIComponent(redirect)}`);
        return { code: 401, msg: '认证已失效，请重新登录', data: null };
      }

      // blob 响应（文件下载）
      if (response.headers.get('content-type')?.includes('application/octet-stream')) {
        const blob = await response.blob();
        return { code: 200, msg: 'success', data: blob };
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      return { code: 500, msg: error.message || '网络请求失败', data: null };
    }
  },

  /** GET 请求 */
  get(path, options) {
    return this.request('GET', path, options);
  },

  /** POST 请求 */
  post(path, body, options) {
    return this.request('POST', path, { ...options, body });
  },

  /** PUT 请求 */
  put(path, body, options) {
    return this.request('PUT', path, { ...options, body });
  },

  /** PATCH 请求 */
  patch(path, body, options) {
    return this.request('PATCH', path, { ...options, body });
  },

  /** DELETE 请求 */
  delete(path, options) {
    return this.request('DELETE', path, options);
  },

  /**
   * SSE 流式请求（NDJSON 格式，用于知识图谱问答）
   * @param {string} path - API 路径
   * @param {object} body - 请求体
   * @param {function} onEvent - 事件回调
   * @returns {Promise<object>} 最终结果
   */
  async stream(path, body, onEvent) {
    const token = Auth.getToken();
    const response = await fetch(`${AppConfig.HOST_URL}/knowg${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ ...body, user_token: token }),
    });

    if (!response.ok || !response.body) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    return new Promise((resolve, reject) => {
      let settled = false;
      const handleMessage = (event) => {
        if (onEvent) onEvent(event);
        if (event.type === 'final_result') {
          settled = true;
          resolve(event.data);
        } else if (event.type === 'error') {
          settled = true;
          reject(new Error(event.msg || event.message || '请求失败'));
        }
      };

      (async () => {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          lines.filter((line) => line.trim()).forEach((line) => {
            try {
              handleMessage(JSON.parse(line));
            } catch (e) {
              // 忽略解析错误
            }
          });
        }
        if (buffer.trim()) {
          try {
            handleMessage(JSON.parse(buffer));
          } catch (e) {
            // 忽略
          }
        }
        if (!settled) reject(new Error('Response stream ended before completion'));
      })();
    });
  },

  /**
   * 文件上传
   * @param {File} file - 文件对象
   * @returns {Promise<object>} 上传结果
   */
  uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    return this.post('/v1/file/upload', formData);
  },
};
