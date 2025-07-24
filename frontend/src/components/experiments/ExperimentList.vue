<template>
  <div class="experiment-list">
    <div class="list-header">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search experiments..."
          class="search-input"
          @input="debouncedSearch"
        />
      </div>
      <button class="btn btn-primary" @click="showCreateDialog = true">
        New Experiment
      </button>
    </div>

    <div v-if="loading" class="loading-state">
      Loading experiments...
    </div>

    <div v-else-if="error" class="error-state">
      <p>Error loading experiments: {{ error }}</p>
      <button class="btn btn-secondary" @click="loadExperiments">
        Retry
      </button>
    </div>

    <div v-else-if="experiments.length === 0" class="empty-state">
      <p>No experiments found.</p>
      <button class="btn btn-primary" @click="showCreateDialog = true">
        Create your first experiment
      </button>
    </div>

    <div v-else class="experiments-grid">
      <div
        v-for="experiment in experiments"
        :key="experiment.id"
        class="experiment-card"
        @click="selectExperiment(experiment)"
      >
        <div class="card-header">
          <h3>{{ experiment.name }}</h3>
          <span class="version">v{{ experiment.version }}</span>
        </div>
        <p class="description">{{ experiment.description }}</p>
        <div class="card-footer">
          <div class="meta">
            <span class="conditions">
              {{ experiment.conditions?.length || 0 }} conditions
            </span>
            <span class="created">
              Created {{ formatDate(experiment.created_at) }}
            </span>
          </div>
          <div class="actions" @click.stop>
            <button class="btn-icon" @click="editExperiment(experiment)">
              ✏️
            </button>
            <button class="btn-icon" @click="deleteExperiment(experiment)">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="pagination.total > pagination.pageSize" class="pagination">
      <button
        class="btn btn-secondary"
        :disabled="pagination.page === 1"
        @click="changePage(pagination.page - 1)"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ pagination.page }} of {{ totalPages }}
      </span>
      <button
        class="btn btn-secondary"
        :disabled="pagination.page === totalPages"
        @click="changePage(pagination.page + 1)"
      >
        Next
      </button>
    </div>

    <!-- Create/Edit Dialog -->
    <ExperimentDialog
      v-if="showCreateDialog || editingExperiment"
      :experiment="editingExperiment"
      @save="handleSave"
      @close="closeDialog"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog
      v-if="deletingExperiment"
      title="Delete Experiment"
      :message="`Are you sure you want to delete '${deletingExperiment.name}'?`"
      @confirm="confirmDelete"
      @cancel="deletingExperiment = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useExperiments } from '@/composables/useExperiments'
import ExperimentDialog from './ExperimentDialog.vue'
import ConfirmDialog from '../common/ConfirmDialog.vue'

const emit = defineEmits(['select'])

const {
  experiments,
  pagination,
  loading,
  error,
  listExperiments,
  createExperiment,
  updateExperiment,
  deleteExperiment: deleteExp,
} = useExperiments()

const searchQuery = ref('')
const showCreateDialog = ref(false)
const editingExperiment = ref(null)
const deletingExperiment = ref(null)

const totalPages = computed(() => 
  Math.ceil(pagination.total / pagination.pageSize)
)

let searchTimeout
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadExperiments()
  }, 300)
}

const loadExperiments = async () => {
  await listExperiments({
    page: pagination.page,
    pageSize: pagination.pageSize,
    search: searchQuery.value,
  })
}

const changePage = (page) => {
  pagination.page = page
  loadExperiments()
}

const selectExperiment = (experiment) => {
  emit('select', experiment)
}

const editExperiment = (experiment) => {
  editingExperiment.value = experiment
}

const handleSave = async (experimentData) => {
  if (editingExperiment.value) {
    await updateExperiment(editingExperiment.value.id, experimentData)
  } else {
    await createExperiment(experimentData)
  }
  closeDialog()
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingExperiment.value = null
}

const confirmDelete = async () => {
  if (deletingExperiment.value) {
    await deleteExp(deletingExperiment.value.id)
    deletingExperiment.value = null
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

onMounted(() => {
  loadExperiments()
})
</script>

<style lang="scss" scoped>
.experiment-list {
  padding: 1rem;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;

  .search-bar {
    flex: 1;
    max-width: 400px;
  }

  .search-input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid #e5e5e5;
    border-radius: 0.5rem;
    font-size: 1rem;

    &:focus {
      outline: none;
      border-color: #4CAF50;
    }
  }
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;

  &-primary {
    background: #4CAF50;
    color: white;

    &:hover {
      background: #45a049;
    }
  }

  &-secondary {
    background: #f5f5f5;
    color: #333;

    &:hover {
      background: #e5e5e5;
    }
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-icon {
  padding: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  opacity: 0.7;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.error-state {
  color: #f44336;
}

.experiments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.experiment-card {
  background: white;
  border: 1px solid #e5e5e5;
  border-radius: 0.5rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #4CAF50;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;

    h3 {
      font-size: 1.25rem;
      margin: 0;
    }

    .version {
      font-size: 0.875rem;
      color: #666;
      background: #f5f5f5;
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
    }
  }

  .description {
    color: #666;
    margin-bottom: 1rem;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .meta {
      display: flex;
      gap: 1rem;
      font-size: 0.875rem;
      color: #999;
    }

    .actions {
      display: flex;
      gap: 0.5rem;
    }
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;

  .page-info {
    color: #666;
  }
}
</style>