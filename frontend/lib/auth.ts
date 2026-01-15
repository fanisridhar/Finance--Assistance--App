import { authAPI } from './api';

export const setAuthToken = (token: string) => {
  localStorage.setItem('access_token', token);
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const removeAuthToken = () => {
  localStorage.removeItem('access_token');
};

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};

export const login = async (email: string, password: string) => {
  const response = await authAPI.login(email, password);
  const { access_token } = response.data;
  setAuthToken(access_token);
  return response.data;
};

export const register = async (email: string, password: string, fullName?: string) => {
  const response = await authAPI.register(email, password, fullName);
  return response.data;
};

export const logout = () => {
  removeAuthToken();
  window.location.href = '/login';
};

