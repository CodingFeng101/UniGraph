const TOKEN_KEY = 'access_token';
const USER_KEY = 'user'

const isLogin = () => {
  return !!localStorage.getItem(TOKEN_KEY);
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
}

const getUserInfo = () =>{
  return localStorage.getItem(USER_KEY);
}

export { isLogin, getToken, setToken, clearToken, setUserInfo, getUserInfo };
