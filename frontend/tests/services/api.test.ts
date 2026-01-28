import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { apiClient } from '../../src/services/api'

describe('API Client', () => {
  let mock: MockAdapter

  beforeEach(() => {
    mock = new MockAdapter(apiClient)
  })

  afterEach(() => {
    mock.restore()
  })

  describe('Configuration', () => {
    it('should have correct base URL', () => {
      expect(apiClient.defaults.baseURL).toBeDefined()
    })

    it('should have correct headers', () => {
      expect(apiClient.defaults.headers['Content-Type']).toBe('application/json')
    })

    it('should have timeout configured', () => {
      expect(apiClient.defaults.timeout).toBe(30000)
    })
  })

  describe('Request Interceptor', () => {
    it('should allow requests to pass through', async () => {
      mock.onGet('/test').reply(200, { data: 'success' })

      const response = await apiClient.get('/test')
      expect(response.status).toBe(200)
      expect(response.data).toEqual({ data: 'success' })
    })
  })

  describe('Response Interceptor', () => {
    it('should handle successful responses', async () => {
      mock.onGet('/success').reply(200, { message: 'success' })

      const response = await apiClient.get('/success')
      expect(response.status).toBe(200)
      expect(response.data.message).toBe('success')
    })

    it('should handle error responses', async () => {
      mock.onGet('/error').reply(500, { error: 'Server error' })

      await expect(apiClient.get('/error')).rejects.toThrow()
    })

    it('should handle network errors', async () => {
      mock.onGet('/network-error').networkError()

      await expect(apiClient.get('/network-error')).rejects.toThrow()
    })

    it('should handle timeout errors', async () => {
      mock.onGet('/timeout').timeout()

      await expect(apiClient.get('/timeout')).rejects.toThrow()
    })
  })

  describe('HTTP Methods', () => {
    it('should handle GET requests', async () => {
      mock.onGet('/users').reply(200, [{ id: 1, name: 'User' }])

      const response = await apiClient.get('/users')
      expect(response.data).toEqual([{ id: 1, name: 'User' }])
    })

    it('should handle POST requests', async () => {
      const postData = { name: 'New User' }
      mock.onPost('/users', postData).reply(201, { id: 2, ...postData })

      const response = await apiClient.post('/users', postData)
      expect(response.status).toBe(201)
      expect(response.data.name).toBe('New User')
    })

    it('should handle PUT requests', async () => {
      const putData = { name: 'Updated User' }
      mock.onPut('/users/1', putData).reply(200, { id: 1, ...putData })

      const response = await apiClient.put('/users/1', putData)
      expect(response.data.name).toBe('Updated User')
    })

    it('should handle DELETE requests', async () => {
      mock.onDelete('/users/1').reply(204)

      const response = await apiClient.delete('/users/1')
      expect(response.status).toBe(204)
    })
  })
})
