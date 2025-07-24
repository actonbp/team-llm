import { ref, reactive } from 'vue'
import { useApi } from './useApi'

export function useExperiments() {
  const api = useApi()
  const experiments = ref([])
  const currentExperiment = ref(null)
  const pagination = reactive({
    page: 1,
    pageSize: 20,
    total: 0,
  })

  const listExperiments = async (params = {}) => {
    const { page = 1, pageSize = 20, search = '' } = params
    const response = await api.get('/experiments', {
      page,
      page_size: pageSize,
      ...(search && { search }),
    })
    
    experiments.value = response.experiments
    pagination.page = response.page
    pagination.pageSize = response.page_size
    pagination.total = response.total
    
    return response
  }

  const getExperiment = async (experimentId) => {
    const response = await api.get(`/experiments/${experimentId}`)
    currentExperiment.value = response
    return response
  }

  const createExperiment = async (experimentData) => {
    const response = await api.post('/experiments', experimentData)
    await listExperiments() // Refresh the list
    return response
  }

  const updateExperiment = async (experimentId, experimentData) => {
    const response = await api.put(`/experiments/${experimentId}`, experimentData)
    if (currentExperiment.value?.id === experimentId) {
      currentExperiment.value = response
    }
    await listExperiments() // Refresh the list
    return response
  }

  const deleteExperiment = async (experimentId) => {
    await api.del(`/experiments/${experimentId}`)
    if (currentExperiment.value?.id === experimentId) {
      currentExperiment.value = null
    }
    await listExperiments() // Refresh the list
  }

  const importExperiment = async (yamlContent) => {
    const response = await api.post('/experiments/import', {
      yaml_content: yamlContent,
    })
    await listExperiments() // Refresh the list
    return response
  }

  const validateExperiment = async (yamlContent) => {
    return await api.post('/experiments/validate', {
      yaml_content: yamlContent,
    })
  }

  const getExperimentConditions = async (experimentId) => {
    return await api.get(`/experiments/${experimentId}/conditions`)
  }

  const createCondition = async (experimentId, conditionData) => {
    return await api.post(`/experiments/${experimentId}/conditions`, conditionData)
  }

  return {
    experiments,
    currentExperiment,
    pagination,
    loading: api.loading,
    error: api.error,
    listExperiments,
    getExperiment,
    createExperiment,
    updateExperiment,
    deleteExperiment,
    importExperiment,
    validateExperiment,
    getExperimentConditions,
    createCondition,
  }
}