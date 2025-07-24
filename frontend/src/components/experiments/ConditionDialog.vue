<template>
  <div class="dialog-overlay" @click="close">
    <div class="dialog" @click.stop>
      <h2>Add Condition</h2>
      
      <form @submit.prevent="save">
        <div class="form-group">
          <label for="name">Name</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            required
            placeholder="e.g., Control Group, Treatment A"
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="form.description"
            rows="3"
            placeholder="Describe this condition"
          ></textarea>
        </div>

        <div class="form-group">
          <label>Parameters</label>
          <div class="parameters-editor">
            <div v-for="(param, index) in parameters" :key="index" class="parameter-item">
              <input
                v-model="param.key"
                type="text"
                placeholder="Parameter name"
                class="param-key"
              />
              <input
                v-model="param.value"
                type="text"
                placeholder="Value"
                class="param-value"
              />
              <button type="button" class="btn-icon" @click="removeParameter(index)">
                🗑️
              </button>
            </div>
            <button type="button" class="btn btn-secondary btn-sm" @click="addParameter">
              + Add Parameter
            </button>
          </div>
        </div>

        <div class="dialog-actions">
          <button type="button" class="btn btn-secondary" @click="close">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary">
            Create Condition
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  experimentId: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['save', 'close'])

const form = reactive({
  name: '',
  description: '',
})

const parameters = ref([])

const addParameter = () => {
  parameters.value.push({ key: '', value: '' })
}

const removeParameter = (index) => {
  parameters.value.splice(index, 1)
}

const save = () => {
  // Convert parameters array to object
  const parametersObj = {}
  parameters.value.forEach(param => {
    if (param.key) {
      parametersObj[param.key] = param.value
    }
  })

  const conditionData = {
    name: form.name,
    description: form.description,
    parameters: parametersObj,
  }
  
  emit('save', conditionData)
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
  z-index: 1001;
}

.dialog {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

  h2 {
    margin: 0 0 1.5rem 0;
    font-size: 1.5rem;
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
}

.parameters-editor {
  border: 1px solid #e5e5e5;
  border-radius: 0.375rem;
  padding: 1rem;
}

.parameter-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;

  .param-key {
    flex: 1;
  }

  .param-value {
    flex: 2;
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
  font-size: 1.2rem;
  opacity: 0.7;
  transition: opacity 0.2s;

  &:hover {
    opacity: 1;
  }
}
</style>