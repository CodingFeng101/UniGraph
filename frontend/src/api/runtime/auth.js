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
    localStorage.setItem(USER_KEY, typeof info === 'string' ? info : JSON.stringify(info));
  },

  /** 获取用户信息 */
  getUserInfo() {
    const info = localStorage.getItem(USER_KEY);
    return info ? JSON.parse(info) : null;
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
    const key = CryptoJS.enc.Base64.parse(AppConfig.ENCRYPT_SECRET_KEY);
    const iv = CryptoJS.lib.WordArray.random(16);
    const encrypted = CryptoJS.AES.encrypt(data, key, { iv });
    return {
      ciphertext: encrypted.ciphertext.toString(CryptoJS.enc.Base64),
      iv: iv.toString(CryptoJS.enc.Base64),
    };
  },
};
