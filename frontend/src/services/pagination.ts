export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_prev: boolean
}

/**
 * Extract items from either an array or a paginated response.
 * This allows backward compatibility during the transition to paginated APIs.
 */
export function toItems<T>(data: T[] | PaginatedResponse<T>): T[] {
  if (Array.isArray(data)) {
    return data
  }
  return data?.items ?? []
}

/**
 * Convert array or paginated response to full pagination metadata.
 * Useful for components that need pagination information.
 */
export function toPagination<T>(data: T[] | PaginatedResponse<T>): PaginatedResponse<T> {
  if (Array.isArray(data)) {
    return {
      items: data,
      total: data.length,
      page: 1,
      page_size: data.length,
      total_pages: 1,
      has_next: false,
      has_prev: false
    }
  }
  return data
}
