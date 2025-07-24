<template>
  <div class="session-list">
    <div class="list-header">
      <h2>Active Sessions</h2>
      <div class="filters">
        <select v-model="statusFilter" @change="applyFilters" class="filter-select">
          <option value="">All Status</option>
          <option value="waiting">Waiting</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
        </select>
        <button class="btn btn-secondary" @click="refreshSessions">
          🔄 Refresh
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      Loading sessions...
    </div>

    <div v-else-if="error" class="error-state">
      <p>Error loading sessions: {{ error }}</p>
      <button class="btn btn-secondary" @click="loadSessions">
        Retry
      </button>
    </div>

    <div v-else-if="sessions.length === 0" class="empty-state">
      <p>No active sessions at the moment.</p>
    </div>

    <div v-else class="sessions-grid">
      <div
        v-for="session in sessions"
        :key="session.id"
        class="session-card"
        :class="{ active: session.status === 'active' }"
        @click="selectSession(session)"
      >
        <div class="card-header">
          <div class="session-info">
            <h3>{{ session.experiment?.name || 'Unknown Experiment' }}</h3>
            <span class="condition">{{ session.condition?.name || 'Default' }}</span>
          </div>
          <span :class="['status', session.status]">
            {{ session.status }}
          </span>
        </div>
        
        <div class="session-meta">
          <div class="meta-item">
            <span class="label">Access Code:</span>
            <code>{{ session.access_code }}</code>
          </div>
          <div class="meta-item">
            <span class="label">Participants:</span>
            <span>{{ session.participant_count || 0 }} / {{ session.max_participants || '∞' }}</span>
          </div>
          <div class="meta-item">
            <span class="label">Started:</span>
            <span>{{ formatTime(session.created_at) }}</span>
          </div>
        </div>

        <div class="participants-preview">
          <div 
            v-for="participant in session.participants?.slice(0, 3)" 
            :key="participant.id"
            class="participant-avatar"
            :title="participant.name"
          >
            {{ getInitials(participant.name) }}
          </div>
          <div v-if="session.participants?.length > 3" class="more-participants">
            +{{ session.participants.length - 3 }}
          </div>
        </div>

        <div class="card-actions" @click.stop>
          <button 
            v-if="session.status === 'active'" 
            class="btn btn-sm btn-primary"
            @click="monitorSession(session)"
          >
            Monitor
          </button>
          <button 
            v-if="session.status === 'waiting'" 
            class="btn btn-sm btn-secondary"
            @click="copyAccessCode(session.access_code)"
          >
            Copy Code
          </button>
          <button 
            v-if="session.status === 'completed'" 
            class="btn btn-sm btn-secondary"
            @click="viewResults(session)"
          >
            View Results
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useSessions } from '@/composables/useSessions'

const emit = defineEmits(['select', 'monitor'])

const {
  sessions,
  loading,
  error,
  listSessions,
  setFilters,
} = useSessions()

const statusFilter = ref('')
let refreshInterval = null

const loadSessions = async () => {
  await listSessions()
}

const refreshSessions = () => {
  loadSessions()
}

const applyFilters = () => {
  setFilters({ status: statusFilter.value || null })
}

const selectSession = (session) => {
  emit('select', session)
}

const monitorSession = (session) => {
  emit('monitor', session)
}

const copyAccessCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code)
    // Could add a toast notification here
    console.log('Access code copied!')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const viewResults = (session) => {
  // TODO: Navigate to results view
  console.log('View results for session:', session.id)
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) { // Less than 1 minute
    return 'Just now'
  } else if (diff < 3600000) { // Less than 1 hour
    const minutes = Math.floor(diff / 60000)
    return `${minutes}m ago`
  } else if (diff < 86400000) { // Less than 1 day
    const hours = Math.floor(diff / 3600000)
    return `${hours}h ago`
  } else {
    return date.toLocaleDateString()
  }
}

const getInitials = (name) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

onMounted(() => {
  loadSessions()
  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(refreshSessions, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style lang="scss" scoped>
.session-list {
  height: 100%;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;

  h2 {
    margin: 0;
    font-size: 1.5rem;
  }

  .filters {
    display: flex;
    gap: 1rem;
    align-items: center;
  }
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e5e5;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: #4CAF50;
  }
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

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1.5rem;
}

.session-card {
  background: white;
  border: 2px solid #e5e5e5;
  border-radius: 0.75rem;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #4CAF50;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  &.active {
    border-color: #4CAF50;
    background: #f8fff9;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;

  .session-info {
    flex: 1;

    h3 {
      margin: 0 0 0.25rem 0;
      font-size: 1.125rem;
    }

    .condition {
      font-size: 0.875rem;
      color: #666;
    }
  }

  .status {
    padding: 0.25rem 0.75rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;

    &.waiting {
      background: #fff3cd;
      color: #856404;
    }

    &.active {
      background: #d4edda;
      color: #155724;
    }

    &.completed {
      background: #cce5ff;
      color: #004085;
    }
  }
}

.session-meta {
  margin-bottom: 1rem;

  .meta-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;

    .label {
      color: #666;
    }

    code {
      background: #f5f5f5;
      padding: 0.125rem 0.5rem;
      border-radius: 0.25rem;
      font-family: monospace;
      font-weight: 500;
    }
  }
}

.participants-preview {
  display: flex;
  gap: -0.5rem;
  margin-bottom: 1rem;

  .participant-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #4CAF50;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 500;
    border: 2px solid white;
    margin-right: -0.5rem;

    &:nth-child(even) {
      background: #2196F3;
    }

    &:nth-child(3n) {
      background: #FF9800;
    }
  }

  .more-participants {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #666;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    border: 2px solid white;
  }
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
</style>