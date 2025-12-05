/**
 * Auth Store - Reactive authentication state management
 *
 * Provides a simple reactive store for auth state that components can subscribe to.
 */

import { authService, type AuthUser } from './service'

export interface AuthState {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

type AuthStateListener = (state: AuthState) => void

class AuthStore {
  private state: AuthState = {
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  }

  private listeners: Set<AuthStateListener> = new Set()

  constructor() {
    // Subscribe to auth service events
    authService.subscribe(() => this.refreshState())

    // Initialize state
    this.refreshState()
  }

  /**
   * Get current auth state
   */
  getState(): AuthState {
    return { ...this.state }
  }

  /**
   * Subscribe to state changes
   */
  subscribe(listener: AuthStateListener): () => void {
    this.listeners.add(listener)
    // Immediately notify with current state
    listener(this.getState())
    return () => this.listeners.delete(listener)
  }

  /**
   * Refresh state from auth service
   */
  async refreshState(): Promise<void> {
    try {
      const user = await authService.getUser()
      const isAuthenticated = user !== null && !user.expired

      this.state = {
        user,
        isAuthenticated,
        isLoading: false,
        error: null,
      }
    } catch (error) {
      this.state = {
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      }
    }

    this.notifyListeners()
  }

  private notifyListeners(): void {
    const state = this.getState()
    this.listeners.forEach((listener) => listener(state))
  }

  /**
   * Login action
   */
  async login(returnUrl?: string): Promise<void> {
    this.state = { ...this.state, isLoading: true, error: null }
    this.notifyListeners()

    try {
      await authService.login(returnUrl)
    } catch (error) {
      this.state = {
        ...this.state,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed',
      }
      this.notifyListeners()
    }
  }

  /**
   * Handle OAuth callback
   */
  async handleCallback(): Promise<AuthUser | null> {
    this.state = { ...this.state, isLoading: true, error: null }
    this.notifyListeners()

    try {
      const user = await authService.handleCallback()
      this.state = {
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      }
      this.notifyListeners()
      return user
    } catch (error) {
      this.state = {
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Callback failed',
      }
      this.notifyListeners()
      return null
    }
  }

  /**
   * Logout action
   */
  async logout(): Promise<void> {
    this.state = { ...this.state, isLoading: true, error: null }
    this.notifyListeners()

    try {
      await authService.logout()
    } catch (error) {
      // Even if logout fails at Keycloak, clear local state
      await authService.removeUser()
      this.state = {
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      }
      this.notifyListeners()
    }
  }
}

// Singleton instance
export const authStore = new AuthStore()
