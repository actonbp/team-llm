<template>
  <div class="join-page">
    <div class="join-container">
      <h1>Join Experiment</h1>
      <p>Enter your access code to join the experiment</p>
      
      <form @submit.prevent="joinSession" class="join-form">
        <div class="form-group">
          <label for="accessCode">Access Code</label>
          <input
            id="accessCode"
            v-model="accessCode"
            type="text"
            placeholder="Enter access code"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="prolificId">Prolific ID (optional)</label>
          <input
            id="prolificId"
            v-model="prolificId"
            type="text"
            placeholder="Enter your Prolific ID"
          />
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Joining...' : 'Join Session' }}
        </button>
        
        <div v-if="error" class="error">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const accessCode = ref('')
const prolificId = ref('')
const loading = ref(false)
const error = ref('')

const joinSession = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await axios.post('/api/participants/join', {
      access_code: accessCode.value,
      external_id: prolificId.value
    })
    
    // Store participant info
    localStorage.setItem('participantId', response.data.participant_id)
    localStorage.setItem('sessionId', response.data.session_id)
    
    // Navigate to chat
    router.push({
      name: 'participant-chat',
      params: { sessionId: response.data.session_id }
    })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to join session'
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.join-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.join-container {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  
  h1 {
    font-size: 1.875rem;
    margin-bottom: 0.5rem;
    text-align: center;
  }
  
  p {
    color: #666;
    text-align: center;
    margin-bottom: 2rem;
  }
}

.join-form {
  .form-group {
    margin-bottom: 1.5rem;
    
    label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: 500;
      color: #374151;
    }
    
    input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #d1d5db;
      border-radius: 0.375rem;
      font-size: 1rem;
      
      &:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
    }
  }
  
  .btn {
    width: 100%;
    padding: 0.75rem;
    border: none;
    border-radius: 0.375rem;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    
    &.btn-primary {
      background: #3b82f6;
      color: white;
      
      &:hover:not(:disabled) {
        background: #2563eb;
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
  
  .error {
    margin-top: 1rem;
    padding: 0.75rem;
    background: #fee;
    border: 1px solid #fcc;
    border-radius: 0.375rem;
    color: #c00;
    text-align: center;
  }
}
</style>