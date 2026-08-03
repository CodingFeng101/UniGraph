/**
 * 认证管理模块
 * 对接旧系统 JWT 认证机制
 */
import CryptoJS from 'crypto-js';
import { isLogin } from '@/utils/auth';
import { AppConfig } from './config';

const TOKEN_KEY = 'access_token';
const USER_KEY = 'user';

export const Auth = window.Auth = {
  /** 是否已登录 */
  isLogin() {
    return isLogin();
  },

  /** 获取 token */
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },

  /** 获取认证请求头 */
  getAuthHeader() {
    const token = this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  },

  /** 设置 token */
  setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  },

  /** 清除 token */
  clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  },

  /** 设置用户信息 */
  setUserInfo(info) {
    const incoming = typeof info === 'string' ? JSON.parse(info) : (info || {});
    const cached = this.getUserInfo() || {};
    const sameUser = Boolean(
      (cached.uuid && incoming.uuid && cached.uuid === incoming.uuid) ||
      (cached.user_uuid && incoming.user_uuid && cached.user_uuid === incoming.user_uuid) ||
      (cached.id && incoming.id && cached.id === incoming.id) ||
      (cached.username && incoming.username && cached.username === incoming.username)
    );
    const userInfo = {
      ...cached,
      ...incoming,
      avatar: incoming.avatar || (sameUser ? cached.avatar : null),
    };
    localStorage.setItem(USER_KEY, JSON.stringify(userInfo));
    window.dispatchEvent(new CustomEvent('unigraph:user-updated', { detail: userInfo }));
  },

  /** 获取用户信息 */
  getUserInfo() {
    const info = localStorage.getItem(USER_KEY);
    if (!info) return null;
    try {
      return JSON.parse(info);
    } catch {
      this.clearUserInfo();
      return null;
    }
  },

  /** 清除用户信息 */
  clearUserInfo() {
    localStorage.removeItem(USER_KEY);
  },

  /**
   * 检查登录状态，未登录则跳转登录页
   * @param {string} loginPath - 登录页路径（默认根据页面位置自动判断）
   */
  requireAuth(loginPath) {
    if (!this.isLogin()) {
      window.location.href = loginPath || `${import.meta.env.BASE_URL}login`;
      return false;
    }
    return true;
  },

  /** 退出登录 */
  async logout() {
    try {
      await fetch(`${AppConfig.API_BASE_URL}/v1/auth/logout`, {
        method: 'POST',
        headers: this.getAuthHeader(),
      });
    } catch (e) {
      // 忽略登出请求失败
    }
    this.clearToken();
    this.clearUserInfo();
    window.location.href = `${import.meta.env.BASE_URL}login`;
  },

  /**
   * AES-CBC 加密数据（与后端 decrypt_data 对应）
   * 需要引入 CryptoJS
   * @param {string} data - 明文数据
   * @returns {{ciphertext: string, iv: string}} Base64 编码的密文和 IV
   */
  encryptData(data) {
    if (!AppConfig.ENCRYPT_SECRET_KEY) {
      throw new Error('缺少 VITE_AUTH_AES_SECRET_KEY，请先完成前后端登录加密配置');
    }
    const key = CryptoJS.enc.Base64.parse(AppConfig.ENCRYPT_SECRET_KEY);
    const iv = CryptoJS.lib.WordArray.random(16);
    const encrypted = CryptoJS.AES.encrypt(data, key, { iv });
    return {
      ciphertext: encrypted.ciphertext.toString(CryptoJS.enc.Base64),
      iv: iv.toString(CryptoJS.enc.Base64),
    };
  },
};
