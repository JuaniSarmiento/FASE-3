/**
 * Auth Service - Authentication & Authorization
 */
import apiClient from './client';

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  roles: string[];
  created_at: string;
  is_active: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role?: string;
}

class AuthService {
  /**
   * Login
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await apiClient.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    // Store token
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  }

  /**
   * Register
   */
  async register(data: RegisterRequest): Promise<User> {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  }

  /**
   * Logout
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Check if authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Get user profile
   */
  async getProfile(): Promise<User> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  }

  /**
   * Refresh token
   */
  async refreshToken(): Promise<{ access_token: string }> {
    const response = await apiClient.post('/auth/refresh');
    
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    
    return response.data;
  }
}

export const authService = new AuthService();
