import { initObservability } from './observability'
import { LitElement, html, css } from 'lit'
import { customElement, state } from 'lit/decorators.js'
import './components/health-check'
import './components/login-button'
import './components/auth-callback'
import './components/user-profile'
import './components/todo-list'
import './style.css'

// Initialize observability before any other code runs
initObservability()

type Route = 'home' | 'callback' | 'profile'

/**
 * Main Application Component
 *
 * Handles routing and authentication state.
 */
@customElement('app-root')
export class AppRoot extends LitElement {
  static styles = css`
    :host {
      display: block;
      min-height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .header {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      padding: 1.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }

    .header-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }

    .logo-section {
      display: flex;
      flex-direction: column;
    }

    .logo {
      font-size: 1.5rem;
      font-weight: bold;
      color: white;
    }

    .subtitle {
      color: rgba(255, 255, 255, 0.8);
      font-size: 0.875rem;
    }

    .nav {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .nav-link {
      color: white;
      text-decoration: none;
      padding: 0.5rem 1rem;
      border-radius: 0.375rem;
      font-size: 0.875rem;
      cursor: pointer;
      transition: background 0.2s;
    }

    .nav-link:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    .nav-link.active {
      background: rgba(255, 255, 255, 0.2);
    }

    .content {
      padding: 2rem 1rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    .page-title {
      color: white;
      font-size: 1.5rem;
      margin-bottom: 1.5rem;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }
  `

  @state()
  private currentRoute: Route = 'home'

  connectedCallback(): void {
    super.connectedCallback()
    this.handleRoute()
    window.addEventListener('popstate', () => this.handleRoute())
  }

  private handleRoute(): void {
    const path = window.location.pathname

    if (path === '/auth/callback') {
      this.currentRoute = 'callback'
    } else if (path === '/profile') {
      this.currentRoute = 'profile'
    } else {
      this.currentRoute = 'home'
    }
  }

  private navigate(route: Route): void {
    const path = route === 'home' ? '/' : `/${route}`
    window.history.pushState({}, '', path)
    this.currentRoute = route
  }

  private renderNav() {
    return html`
      <nav class="nav">
        <span
          class="nav-link ${this.currentRoute === 'home' ? 'active' : ''}"
          @click=${() => this.navigate('home')}
        >
          Home
        </span>
        <span
          class="nav-link ${this.currentRoute === 'profile' ? 'active' : ''}"
          @click=${() => this.navigate('profile')}
        >
          Profile
        </span>
        <login-button></login-button>
      </nav>
    `
  }

  private renderPage() {
    switch (this.currentRoute) {
      case 'callback':
        return html`<auth-callback></auth-callback>`

      case 'profile':
        return html`
          <h1 class="page-title">Your Profile</h1>
          <user-profile></user-profile>
        `

      case 'home':
      default:
        return html`
          <h1 class="page-title">Todo Application</h1>
          <div class="grid">
            <health-check></health-check>
            <todo-list></todo-list>
          </div>
        `
    }
  }

  render() {
    // Auth callback page has its own full-screen layout
    if (this.currentRoute === 'callback') {
      return html`<auth-callback></auth-callback>`
    }

    return html`
      <div class="header">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo">{{ cookiecutter.project_name }}</div>
            <div class="subtitle">Frontend Application</div>
          </div>
          ${this.renderNav()}
        </div>
      </div>
      <div class="content">
        ${this.renderPage()}
      </div>
    `
  }
}

declare global {
  interface HTMLElementTagNameMap {
    'app-root': AppRoot
  }
}
