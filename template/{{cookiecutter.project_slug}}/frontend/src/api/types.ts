/**
 * API Response Types
 */

export interface HealthResponse {
  status: string
  timestamp: string
  version?: string
}

export interface ApiError {
  message: string
  status: number
  timestamp: string
}

export type ApiResponse<T> = {
  success: true
  data: T
} | {
  success: false
  error: ApiError
}

/**
 * Todo Types
 */
export interface PublicTodo {
  id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
}

export interface UserTodo extends PublicTodo {
  user_id: string
  tenant_id: string
  updated_at: string
}

export interface CreateTodoRequest {
  title: string
  description?: string
  completed?: boolean
}

export interface UpdateTodoRequest {
  title?: string
  description?: string
  completed?: boolean
}

/**
 * Auth Types
 */
export interface ProtectedResponse {
  message: string
  user_id: string
  tenant_id: string
  email: string | null
}
