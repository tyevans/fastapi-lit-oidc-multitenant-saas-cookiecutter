import { LitElement, html, css } from 'lit'
import { customElement, state } from 'lit/decorators.js'
import { authStore } from '../auth'

/**
 * Auth Callback Handler Component
 *
 * Handles the OAuth callback after Keycloak redirects back.
 * Shows loading state while processing, then redirects to the app.
 */
@customElement('auth-callback')
export class AuthCallback extends LitElement {
  static styles = css`
    :host {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .container {
      background: white;
      padding: 2rem;
      border-radius: 0.5rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      text-align: center;
      max-width: 400px;
    }

    .loading {
      display: inline-block;
      width: 3rem;
      height: 3rem;
      border: 3px solid #e5e7eb;
      border-top-color: #667eea;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin-bottom: 1rem;
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }

    h2 {
      color: #374151;
      margin: 0 0 0.5rem 0;
      font-size: 1.25rem;
    }

    p {
      color: #6b7280;
      margin: 0;
      font-size: 0.875rem;
    }

    .error {
      color: #dc2626;
      background: #fef2f2;
      padding: 1rem;
      border-radius: 0.375rem;
      margin-top: 1rem;
    }

    .error-title {
      font-weight: 600;
      margin-bottom: 0.5rem;
    }

    .retry-btn {
      margin-top: 1rem;
      padding: 0.5rem 1rem;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 0.375rem;
      cursor: pointer;
      font-size: 0.875rem;
    }

    .retry-btn:hover {
      background: #5a67d8;
    }
  `

  @state()
  private isProcessing = true

  @state()
  private error: string | null = null

  async connectedCallback(): Promise<void> {
    super.connectedCallback()
    await this.handleCallback()
  }

  private async handleCallback(): Promise<void> {
    try {
      this.isProcessing = true
      this.error = null

      const user = await authStore.handleCallback()

      if (user) {
        // Get the return URL from state or default to home
        const returnUrl = (user.state as string) || '/'
        // Small delay to show success state
        setTimeout(() => {
          window.location.href = returnUrl
        }, 500)
      } else {
        this.error = 'Authentication failed. Please try again.'
        this.isProcessing = false
      }
    } catch (err) {
      console.error('Callback error:', err)
      this.error = err instanceof Error ? err.message : 'An unexpected error occurred'
      this.isProcessing = false
    }
  }

  private handleRetry(): void {
    window.location.href = '/'
  }

  render() {
    if (this.error) {
      return html`
        <div class="container">
          <div class="error">
            <div class="error-title">Authentication Error</div>
            <p>${this.error}</p>
          </div>
          <button class="retry-btn" @click=${this.handleRetry}>Return to Home</button>
        </div>
      `
    }

    return html`
      <div class="container">
        <div class="loading"></div>
        <h2>Signing you in...</h2>
        <p>Please wait while we complete the authentication.</p>
      </div>
    `
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'auth-callback': AuthCallback
  }
}
