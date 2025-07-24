<template>
  <div class="detail-overlay" @click="$emit('close')">
    <div class="detail-panel" @click.stop>
      <div class="panel-header">
        <h2>{{ experiment.name }}</h2>
        <button class="btn-icon" @click="$emit('close')">✕</button>
      </div>

      <div class="panel-content">
        <div class="info-section">
          <h3>Details</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>Version</label>
              <span>{{ experiment.version }}</span>
            </div>
            <div class="info-item">
              <label>Created</label>
              <span>{{ formatDate(experiment.created_at) }}</span>
            </div>
            <div class="info-item">
              <label>Created By</label>
              <span>{{ experiment.created_by || 'System' }}</span>
            </div>
            <div class="info-item">
              <label>ID</label>
              <span class="mono">{{ experiment.id }}</span>
            </div>
          </div>
          
          <div v-if="experiment.description" class="description">
            <label>Description</label>
            <p>{{ experiment.description }}</p>
          </div>
        </div>

        <div class="info-section">
          <h3>Scenario</h3>
          <div v-if="experiment.config?.scenario">
            <div class="scenario-field">
              <label>Instructions</label>
              <p>{{ experiment.config.scenario.instructions || 'No instructions provided' }}</p>
            </div>
            <div class="scenario-field">
              <label>Completion Trigger</label>
              <p>{{ experiment.config.scenario.completionTrigger || 'Not specified' }}</p>
            </div>
          </div>
          <p v-else class="empty">No scenario configuration</p>
        </div>

        <div class="info-section">
          <h3>Conditions ({{ conditions.length }})</h3>
          <div v-if="loadingConditions" class="loading">
            Loading conditions...
          </div>
          <div v-else-if="conditions.length > 0" class="conditions-list">
            <div v-for="condition in conditions" :key="condition.id" class="condition-card">
              <div class="condition-header">
                <h4>{{ condition.name }}</h4>
                <code class="access-code">{{ condition.access_code }}</code>
              </div>
              <p v-if="condition.description">{{ condition.description }}</p>
              <div v-if="condition.parameters && Object.keys(condition.parameters).length > 0" class="parameters">
                <label>Parameters:</label>
                <pre>{{ JSON.stringify(condition.parameters, null, 2) }}</pre>
              </div>
            </div>
          </div>
          <p v-else class="empty">No conditions defined</p>
          
          <button class="btn btn-secondary btn-sm" @click="showAddCondition = true">
            + Add Condition
          </button>
        </div>

        <div class="info-section">
          <h3>Roles</h3>
          <div v-if="experiment.config?.roles && experiment.config.roles.length > 0" class="roles-list">
            <div v-for="(role, index) in experiment.config.roles" :key="index" class="role-item">
              <span class="role-type" :class="role.type.toLowerCase()">{{ role.type }}</span>
              <span class="role-name">{{ role.name }}</span>
              <span v-if="role.model" class="role-model">{{ role.model }}</span>
            </div>
          </div>
          <p v-else class="empty">No roles defined</p>
        </div>

        <div class="info-section">
          <h3>Ethics</h3>
          <div v-if="experiment.config?.ethics">
            <div class="ethics-item">
              <label>Requires Consent</label>
              <span>{{ experiment.config.ethics.requiresConsent ? 'Yes' : 'No' }}</span>
            </div>
            <div v-if="experiment.config.ethics.consentFormPath" class="ethics-item">
              <label>Consent Form</label>
              <span>{{ experiment.config.ethics.consentFormPath }}</span>
            </div>
            <div v-if="experiment.config.ethics.dataRetentionDays" class="ethics-item">
              <label>Data Retention</label>
              <span>{{ experiment.config.ethics.dataRetentionDays }} days</span>
            </div>
          </div>
          <p v-else class="empty">No ethics configuration</p>
        </div>

        <div class="panel-actions">
          <button class="btn btn-primary" @click="startSession">
            Start New Session
          </button>
          <button class="btn btn-secondary" @click="exportConfig">
            Export Config
          </button>
        </div>
      </div>
    </div>

    <!-- Add Condition Dialog -->
    <ConditionDialog
      v-if="showAddCondition"
      :experimentId="experiment.id"
      @save="handleConditionSave"
      @close="showAddCondition = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useExperiments } from '@/composables/useExperiments'
import ConditionDialog from './ConditionDialog.vue'

const props = defineProps({
  experiment: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close'])

const { getExperimentConditions, createCondition } = useExperiments()

const conditions = ref([])
const loadingConditions = ref(true)
const showAddCondition = ref(false)

const loadConditions = async () => {
  loadingConditions.value = true
  try {
    conditions.value = await getExperimentConditions(props.experiment.id)
  } catch (error) {
    console.error('Failed to load conditions:', error)
  } finally {
    loadingConditions.value = false
  }
}

const handleConditionSave = async (conditionData) => {
  await createCondition(props.experiment.id, conditionData)
  await loadConditions()
  showAddCondition.value = false
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const startSession = () => {
  // TODO: Implement session creation
  console.log('Start session for experiment:', props.experiment.id)
}

const exportConfig = () => {
  const dataStr = JSON.stringify(props.experiment.config, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `${props.experiment.name.replace(/\s+/g, '_')}_config.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

onMounted(() => {
  loadConditions()
})
</script>

<style lang="scss" scoped>
.detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: flex-end;
  z-index: 999;
}

.detail-panel {
  background: white;
  width: 600px;
  max-width: 90vw;
  height: 100vh;
  overflow-y: auto;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem;
  border-bottom: 1px solid #e5e5e5;
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;

  h2 {
    margin: 0;
    font-size: 1.5rem;
  }
}

.panel-content {
  padding: 2rem;
}

.info-section {
  margin-bottom: 2.5rem;

  h3 {
    margin: 0 0 1rem 0;
    font-size: 1.25rem;
    color: #333;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.info-item {
  label {
    display: block;
    font-size: 0.875rem;
    color: #666;
    margin-bottom: 0.25rem;
  }

  span {
    font-size: 1rem;
    color: #333;
  }

  .mono {
    font-family: monospace;
    font-size: 0.875rem;
  }
}

.description {
  margin-top: 1rem;

  label {
    display: block;
    font-size: 0.875rem;
    color: #666;
    margin-bottom: 0.5rem;
  }

  p {
    margin: 0;
    color: #333;
    line-height: 1.5;
  }
}

.scenario-field {
  margin-bottom: 1rem;

  label {
    display: block;
    font-size: 0.875rem;
    color: #666;
    margin-bottom: 0.5rem;
  }

  p {
    margin: 0;
    color: #333;
    line-height: 1.5;
  }
}

.conditions-list {
  margin-bottom: 1rem;
}

.condition-card {
  background: #f5f5f5;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 0.75rem;

  .condition-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;

    h4 {
      margin: 0;
      font-size: 1rem;
    }
  }

  .access-code {
    background: white;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-family: monospace;
  }

  p {
    margin: 0 0 0.5rem 0;
    color: #666;
    font-size: 0.875rem;
  }

  .parameters {
    margin-top: 0.5rem;

    label {
      display: block;
      font-size: 0.75rem;
      color: #666;
      margin-bottom: 0.25rem;
    }

    pre {
      background: white;
      padding: 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.75rem;
      overflow-x: auto;
      margin: 0;
    }
  }
}

.roles-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.role-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;

  .role-type {
    padding: 0.25rem 0.75rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: 500;

    &.human {
      background: #e3f2fd;
      color: #1976d2;
    }

    &.ai {
      background: #f3e5f5;
      color: #7b1fa2;
    }
  }

  .role-name {
    font-weight: 500;
  }

  .role-model {
    font-size: 0.875rem;
    color: #666;
  }
}

.ethics-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;

  label {
    font-size: 0.875rem;
    color: #666;
  }

  span {
    font-size: 0.875rem;
    color: #333;
  }
}

.empty {
  color: #999;
  font-style: italic;
}

.loading {
  color: #666;
  padding: 1rem;
  text-align: center;
}

.panel-actions {
  display: flex;
  gap: 1rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e5e5;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;

  &-sm {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
  }

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
}

.btn-icon {
  padding: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.5rem;
  opacity: 0.7;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }
}
</style>