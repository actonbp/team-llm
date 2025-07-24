import { ref } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const request = async (endpoint, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const url = `${API_BASE_URL}${endpoint}`
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const get = (endpoint, params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `${endpoint}?${queryString}` : endpoint
    return request(url, { method: 'GET' })
  }

  const post = (endpoint, data) => {
    return request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  const put = (endpoint, data) => {
    return request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  const del = (endpoint) => {
    return request(endpoint, { method: 'DELETE' })
  }

  return {
    loading,
    error,
    get,
    post,
    put,
    del,
  }
}