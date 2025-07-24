import { ref, reactive } from 'vue'
import { useApi } from './useApi'

export function useSessions() {
  const api = useApi()
  const sessions = ref([])
  const currentSession = ref(null)
  const sessionStats = ref(null)
  
  const filters = reactive({
    experimentId: null,
    status: null,
    conditionId: null,
  })

  const listSessions = async (params = {}) => {
    const queryParams = {
      ...params,
      ...(filters.experimentId && { experiment_id: filters.experimentId }),
      ...(filters.status && { status: filters.status }),
      ...(filters.conditionId && { condition_id: filters.conditionId }),
    }
    
    const response = await api.get('/sessions', queryParams)
    sessions.value = response.sessions || []
    return response
  }

  const getSession = async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}`)
    currentSession.value = response
    return response
  }

  const createSession = async (conditionId, maxParticipants = null) => {
    const data = {
      condition_id: conditionId,
      ...(maxParticipants && { max_participants: maxParticipants }),
    }
    const response = await api.post('/sessions', data)
    await listSessions() // Refresh list
    return response
  }

  const completeSession = async (sessionId, triggeredBy) => {
    const response = await api.post(`/sessions/${sessionId}/complete`, {
      triggered_by: triggeredBy,
    })
    if (currentSession.value?.id === sessionId) {
      currentSession.value = response
    }
    await listSessions() // Refresh list
    return response
  }

  const getSessionStats = async (sessionId) => {
    const response = await api.get(`/sessions/${sessionId}/stats`)
    sessionStats.value = response
    return response
  }

  const joinSession = async (accessCode, participantName, email = null) => {
    const data = {
      access_code: accessCode,
      participant_name: participantName,
      consent_given: true,
      ...(email && { email }),
    }
    return await api.post('/sessions/join', data)
  }

  const leaveSession = async (sessionId, participantId) => {
    return await api.post(`/sessions/${sessionId}/leave`, {
      participant_id: participantId,
    })
  }

  const setFilters = (newFilters) => {
    Object.assign(filters, newFilters)
    listSessions()
  }

  const clearFilters = () => {
    filters.experimentId = null
    filters.status = null
    filters.conditionId = null
    listSessions()
  }

  return {
    sessions,
    currentSession,
    sessionStats,
    filters,
    loading: api.loading,
    error: api.error,
    listSessions,
    getSession,
    createSession,
    completeSession,
    getSessionStats,
    joinSession,
    leaveSession,
    setFilters,
    clearFilters,
  }
}