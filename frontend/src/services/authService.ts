/**
 * Authentication service for API communication.
 * Handles user signup, login, and token management.
 */

import axios from 'axios';
import { UserSignup, UserLogin, TokenResponse, UserResponse } from '@/types/auth';

const API_BASE_URL = '/api/v1';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      // Redirect to login could be handled here
    }
    return Promise.reject(error);
  }
);

export const authService = {
  /**
   * Register a new user account.
   * 
   * @param userData - User registration data
   * @returns Promise with token response
   */
  async signup(userData: UserSignup): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>('/auth/signup', userData);
      const { access_token, user } = response.data;
      
      // Store token and user in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Signup failed');
      }
      throw new Error('Network error during signup');
    }
  },

  /**
   * Authenticate user with email and password.
   * 
   * @param credentials - User login credentials
   * @returns Promise with token response
   */
  async login(credentials: UserLogin): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>('/auth/login', credentials);
      const { access_token, user } = response.data;
      
      // Store token and user in localStorage
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Login failed');
      }
      throw new Error('Network error during login');
    }
  },

  /**
   * Get current user profile.
   * 
   * @returns Promise with user data
   */
  async getCurrentUser(): Promise<UserResponse> {
    try {
      const response = await apiClient.get<UserResponse>('/auth/me');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch user profile');
      }
      throw new Error('Network error fetching user profile');
    }
  },

  /**
   * Log out the current user.
   * Clears stored authentication data.
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  /**
   * Get stored authentication token.
   * 
   * @returns Stored token or null
   */
  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  /**
   * Get stored user data.
   * 
   * @returns Stored user or null
   */
  getStoredUser(): UserResponse | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  },
};

