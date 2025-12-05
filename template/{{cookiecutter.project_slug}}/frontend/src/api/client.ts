import type { ApiResponse, ApiError } from './types'
import { authService } from '../auth'

/**
 * API Client Configuration
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Custom error class for API errors
 */
export class ApiClientError extends Error {
  constructor(
    message: string,
    public status: number,
    public timestamp: string
  ) {
    super(message)
    this.name = 'ApiClientError'
  }
}

/**
 * API Client for backend communication
 *
 * Automatically includes auth tokens in requests when available.
 */
class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Get headers for requests, including auth token if available
   */
  private async getHeaders(includeAuth: boolean = true): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (includeAuth) {
      const token = await authService.getAccessToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    return headers
  }

  /**
   * Make a GET request to the API
   * @param endpoint - API endpoint
   * @param options - Request options
   * @param options.authenticated - Whether to include auth token (default: true)
   */
  async get<T>(
    endpoint: string,
    options: { authenticated?: boolean } = {}
  ): Promise<ApiResponse<T>> {
    const { authenticated = true } = options

    try {
      const headers = await this.getHeaders(authenticated)
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'GET',
        headers,
      })

      const data = await response.json()

      if (!response.ok) {
        const error: ApiError = {
          message: data.detail || data.message || 'An error occurred',
          status: response.status,
          timestamp: new Date().toISOString(),
        }
        return { success: false, error }
      }

      return { success: true, data }
    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'Network error occurred',
        status: 0,
        timestamp: new Date().toISOString(),
      }
      return { success: false, error: apiError }
    }
  }

  /**
   * Make a POST request to the API
   * @param endpoint - API endpoint
   * @param body - Request body
   * @param options - Request options
   * @param options.authenticated - Whether to include auth token (default: true)
   */
  async post<T, B = unknown>(
    endpoint: string,
    body?: B,
    options: { authenticated?: boolean } = {}
  ): Promise<ApiResponse<T>> {
    const { authenticated = true } = options

    try {
      const headers = await this.getHeaders(authenticated)
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers,
        body: body ? JSON.stringify(body) : undefined,
      })

      const data = await response.json()

      if (!response.ok) {
        const error: ApiError = {
          message: data.detail || data.message || 'An error occurred',
          status: response.status,
          timestamp: new Date().toISOString(),
        }
        return { success: false, error }
      }

      return { success: true, data }
    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'Network error occurred',
        status: 0,
        timestamp: new Date().toISOString(),
      }
      return { success: false, error: apiError }
    }
  }

  /**
   * Make a PUT request to the API
   */
  async put<T, B = unknown>(
    endpoint: string,
    body?: B,
    options: { authenticated?: boolean } = {}
  ): Promise<ApiResponse<T>> {
    const { authenticated = true } = options

    try {
      const headers = await this.getHeaders(authenticated)
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'PUT',
        headers,
        body: body ? JSON.stringify(body) : undefined,
      })

      const data = await response.json()

      if (!response.ok) {
        const error: ApiError = {
          message: data.detail || data.message || 'An error occurred',
          status: response.status,
          timestamp: new Date().toISOString(),
        }
        return { success: false, error }
      }

      return { success: true, data }
    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'Network error occurred',
        status: 0,
        timestamp: new Date().toISOString(),
      }
      return { success: false, error: apiError }
    }
  }

  /**
   * Make a DELETE request to the API
   */
  async delete<T>(
    endpoint: string,
    options: { authenticated?: boolean } = {}
  ): Promise<ApiResponse<T>> {
    const { authenticated = true } = options

    try {
      const headers = await this.getHeaders(authenticated)
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'DELETE',
        headers,
      })

      // Handle 204 No Content
      if (response.status === 204) {
        return { success: true, data: undefined as T }
      }

      const data = await response.json()

      if (!response.ok) {
        const error: ApiError = {
          message: data.detail || data.message || 'An error occurred',
          status: response.status,
          timestamp: new Date().toISOString(),
        }
        return { success: false, error }
      }

      return { success: true, data }
    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'Network error occurred',
        status: 0,
        timestamp: new Date().toISOString(),
      }
      return { success: false, error: apiError }
    }
  }

  /**
   * Get the base URL
   */
  getBaseUrl(): string {
    return this.baseUrl
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
