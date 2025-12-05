/**
 * OIDC Configuration for Keycloak
 */

export const OIDC_CONFIG = {
  authority: import.meta.env.VITE_OIDC_AUTHORITY || 'http://keycloak.localtest.me:{{ cookiecutter.keycloak_port }}/realms/{{ cookiecutter.keycloak_realm_name }}',
  client_id: import.meta.env.VITE_OIDC_CLIENT_ID || '{{ cookiecutter.keycloak_frontend_client_id }}',
  redirect_uri: import.meta.env.VITE_OIDC_REDIRECT_URI || 'http://localhost:{{ cookiecutter.frontend_port }}/auth/callback',
  post_logout_redirect_uri: import.meta.env.VITE_OIDC_POST_LOGOUT_REDIRECT_URI || 'http://localhost:{{ cookiecutter.frontend_port }}',
  response_type: 'code',
  scope: 'openid profile email',
  automaticSilentRenew: true,
  silentRequestTimeoutInSeconds: 10,
} as const
