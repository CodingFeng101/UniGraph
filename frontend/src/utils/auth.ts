const TOKEN_KEY = 'access_token';
const USER_KEY = 'user';

const isTokenValid = (token: string) => {
  try {
    const payload = token.split('.')[1];
    if (!payload) return false;

    const base64 = payload.replaceAll('-', '+').replaceAll('_', '/');
    const normalized = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    const decoded = JSON.parse(atob(normalized));
    return typeof decoded.exp === 'number' && decoded.exp * 1000 > Date.now();
  } catch {
    return false;
  }
};

const isLogin = () => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return false;
  if (isTokenValid(token)) return true;

  clearToken();
  localStorage.removeItem(USER_KEY);
  return false;
};

const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

const setToken = (token: string) => {
  localStorage.setItem(TOKEN_KEY, token);
};

const clearToken = () => {
  localStorage.removeItem(TOKEN_KEY);
};

const setUserInfo = (userInfo: string) => {
  localStorage.setItem(USER_KEY, userInfo);
};

const getUserInfo = () => {
  return localStorage.getItem(USER_KEY);
};

export { isLogin, getToken, setToken, clearToken, setUserInfo, getUserInfo };
