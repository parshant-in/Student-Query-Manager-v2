export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message)
    this.name = 'ApiError'
  }
}

interface RequestOptions extends RequestInit {
  token?: string | null
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token, headers, ...init } = options
  const isFormData = typeof FormData !== 'undefined' && init.body instanceof FormData
  const response = await fetch(path, {
    ...init,
    headers: {
      ...(init.body && !isFormData ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  })

  if (!response.ok) {
    let message = `Request failed (${response.status}). Please try again.`
    try {
      const body: unknown = await response.json()
      if (typeof body === 'object' && body !== null && 'detail' in body) {
        const detail = (body as { detail?: unknown }).detail
        if (typeof detail === 'string') message = detail
        else if (Array.isArray(detail)) message = detail.map((item) => {
          if (typeof item === 'object' && item !== null && 'msg' in item) return String(item.msg)
          return String(item)
        }).join(' ')
      }
    } catch {
      // Keep the useful status-based message when the server has no JSON body.
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}
