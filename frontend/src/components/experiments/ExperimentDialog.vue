<template>
  <div class="dialog-overlay" @click="close">
    <div class="dialog" @click.stop>
      <h2>{{ experiment ? 'Edit Experiment' : 'New Experiment' }}</h2>
      
      <form @submit.prevent="save">
        <div class="form-group">
          <label for="name">Name</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            placeholder="Enter experiment name"
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="form.description"
            rows="3"
            placeholder="Describe the experiment"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="version">Version</label>
          <input
            id="version"
            v-model="form.version"
            type="text"
            placeholder="1.0.0"
          />
        </div>

        <div class="form-section">
          <h3>Configuration</h3>
          
          <div class="form-group">
            <label>Import from YAML</label>
            <input
              type="file"
              accept=".yaml,.yml"
              @change="handleFileUpload"
            />
            <button
              v-if="yamlContent"
              type="button"
              class="btn btn-secondary btn-sm"
              @click="validateYaml"
            >
              Validate YAML
            </button>
          </div>

          <div v-if="validationResult" class="validation-result">
            <div v-if="validationResult.valid" class="success">
              ✅ YAML is valid
            </div>
            <div v-else class="error">
              ❌ YAML validation failed
            </div>
            <ul v-if="validationResult.errors.length > 0">
              <li v-for="error in validationResult.errors" :key="error" class="error">
                {{ error }}
              </li>
            </ul>
            <ul v-if="validationResult.warnings.length > 0">
              <li v-for="warning in validationResult.warnings" :key="warning" class="warning">
                ⚠️ {{ warning }}
              </li>
            </ul>
          </div>

          <div class="form-group">
            <label>Scenario Instructions</label>
            <textarea
              v-model="form.config.scenario.instructions"
              rows="4"
              placeholder="Instructions for participants"
            ></textarea>
          </div>

          <div class="form-group">
            <label>Completion Trigger</label>
            <input
              v-model="form.config.scenario.completionTrigger"
              type="text"
              placeholder="e.g., Task completed, Time limit reached"
            />
          </div>
        </div>

        <div class="form-section">
          <h3>Conditions</h3>
          <div v-for="(condition, index) in form.config.conditions" :key="index" class="condition-item">
            <input
              v-model="condition.name"
              type="text"
              placeholder="Condition name"
              class="condition-name"
            />
            <input
              v-model="condition.description"
              type="text"
              placeholder="Description"
              class="condition-desc"
            />
            <button type="button" class="btn-icon" @click="removeCondition(index)">
              🗑️
            </button>
          </div>
          <button type="button" class="btn btn-secondary btn-sm" @click="addCondition">
            + Add Condition
          </button>
        </div>

        <div class="dialog-actions">
          <button type="button" class="btn btn-secondary" @click="close">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useExperiments } from '@/composables/useExperiments'

const props = defineProps({
  experiment: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['save', 'close'])

const { validateExperiment, loading } = useExperiments()

const form = reactive({
  name: '',
  description: '',
  version: '1.0.0',
  config: {
    scenario: {
      instructions: '',
      completionTrigger: '',
    },
    conditions: [],
  },
})

const yamlContent = ref('')
const validationResult = ref(null)

// Initialize form with experiment data if editing
watch(() => props.experiment, (experiment) => {
  if (experiment) {
    form.name = experiment.name
    form.description = experiment.description || ''
    form.version = experiment.version || '1.0.0'
    form.config = experiment.config || {
      scenario: {
        instructions: '',
        completionTrigger: '',
      },
      conditions: [],
    }
  }
}, { immediate: true })

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (file) {
    yamlContent.value = await file.text()
    // Parse YAML and update form if valid
    validateYaml()
  }
}

const validateYaml = async () => {
  if (!yamlContent.value) return
  
  try {
    validationResult.value = await validateExperiment(yamlContent.value)
    
    if (validationResult.value.valid && validationResult.value.parsed_config) {
      const config = validationResult.value.parsed_config
      form.name = config.name || form.name
      form.description = config.description || form.description
      form.version = config.version || form.version
      form.config = config
    }
  } catch (error) {
    validationResult.value = {
      valid: false,
      errors: [error.message],
      warnings: [],
    }
  }
}

const addCondition = () => {
  form.config.conditions.push({
    name: '',
    description: '',
    parameters: {},
  })
}

const removeCondition = (index) => {
  form.config.conditions.splice(index, 1)
}

const save = () => {
  const experimentData = {
    name: form.name,
    description: form.description,
    version: form.version,
    config: form.config,
  }
  
  emit('save', experimentData)
}

const close = () => {
  emit('close')
}
</script>

<style lang="scss" scoped>
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  overflow: auto;
  padding: 2rem;
}

.dialog {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

  h2 {
    margin: 0 0 1.5rem 0;
    font-size: 1.5rem;
  }

  h3 {
    margin: 0 0 1rem 0;
    font-size: 1.25rem;
  }
}

.form-group {
  margin-bottom: 1.5rem;

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #333;
  }

  input,
  textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #e5e5e5;
    border-radius: 0.375rem;
    font-size: 1rem;

    &:focus {
      outline: none;
      border-color: #4CAF50;
    }
  }

  input[type="file"] {
    padding: 0.5rem;
  }
}

.form-section {
  border-top: 1px solid #e5e5e5;
  padding-top: 1.5rem;
  margin-top: 1.5rem;
}

.condition-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;

  .condition-name {
    flex: 1;
  }

  .condition-desc {
    flex: 2;
  }
}

.validation-result {
  margin: 1rem 0;
  padding: 1rem;
  border-radius: 0.375rem;
  background: #f5f5f5;

  .success {
    color: #4CAF50;
    font-weight: 500;
  }

  .error {
    color: #f44336;
  }

  .warning {
    color: #ff9800;
  }

  ul {
    margin: 0.5rem 0 0 1.5rem;
    padding: 0;
  }
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
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

    &:hover:not(:disabled) {
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
</style>