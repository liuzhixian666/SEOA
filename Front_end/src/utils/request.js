import axios from 'axios';

// 创建axios实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/ceea/',
  timeout: 600000
});

// 检查token是否过期
function isTokenExpired() {
  const token = localStorage.getItem('token');
  console.log('Token from localStorage:', token ? 'Exists' : 'Not found');
  if (!token) {
    console.log('Token not found, returning true');
    return true;
  }
  try {
    console.log('Token found, parsing...');
    const parts = token.split('.');
    console.log('Token parts:', parts.length);
    if (parts.length !== 3) {
      console.log('Invalid token format');
      return true;
    }
    const payload = JSON.parse(atob(parts[1]));
    console.log('Token payload:', payload);
    const exp = payload.exp * 1000;
    const now = Date.now();
    console.log('Token expiration time:', new Date(exp));
    console.log('Current time:', new Date(now));
    console.log('Token expired:', now > exp);
    return now > exp;
  } catch (error) {
    console.error('Error parsing token:', error);
    return true;
  }
}

// 请求拦截器
request.interceptors.request.use(
  config => {
    console.log('Request URL:', config.url);
    console.log('Request method:', config.method);
    
    // 登录和注册请求不需要token
    const isAuthRequest = config.url === '/login' || config.url === '/register';
    
    if (!isAuthRequest) {
      // 检查token是否过期
      if (isTokenExpired()) {
        console.log('Token is expired, clearing localStorage');
        // 清除localStorage中的所有用户信息
        localStorage.clear();
        // 显示登录过期提示
        alert('登录过期，请重新登录！');
        window.location.reload();
        return Promise.reject(new Error('Token expired'));
      }
      // 从localStorage获取token
      const token = localStorage.getItem('token');
      console.log('Token being used:', token ? 'Exists' : 'Not found');
      if (token) {
        // 添加Authorization请求头
        config.headers.Authorization = `Bearer ${token}`;
        console.log('Added Authorization header');
      }
    }
    
    // 设置Content-Type为application/json，除非已经设置了其他类型（如multipart/form-data）
    if ((config.method === 'post' || config.method === 'put') && !config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json';
    }
    console.log('Request config:', config);
    return config;
  },
  error => {
    // 处理请求错误
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 直接返回响应数据
    return response.data;
  },
  error => {
    // 处理响应错误
    console.error('响应错误:', error);
    
    // 处理401 Unauthorized错误
    if (error.response && error.response.status === 401) {
      // 清除localStorage中的所有用户信息
      localStorage.clear();
      // 显示登录过期提示
      alert('登录过期，请重新登录！');
      window.location.reload();
      return Promise.resolve();
    }
    
    return Promise.reject(error);
  }
);

export default request;