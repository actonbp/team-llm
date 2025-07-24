<template>
  <div class="session-monitor">
    <div class="monitor-header">
      <button class="btn-back" @click="$emit('close')">← Back</button>
      <h2>{{ session.experiment?.name || 'Session Monitor' }}</h2>
      <div class="session-status">
        <span :class="['status', session.status]">{{ session.status }}</span>
        <code class="access-code">{{ session.access_code }}</code>
      </div>
    </div>

    <div class="monitor-content">
      <div class="chat-section">
        <div class="chat-header">
          <h3>Chat Activity</h3>
          <div class="connection-status" :class="{ connected: isConnected }">
            <span class="dot"></span>
            {{ isConnected ? 'Connected' : 'Disconnected' }}
          </div>
        </div>
        
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="no-messages">
            No messages yet. Waiting for participants to start chatting...
          </div>
          
          <div
            v-for="message in messages"
            :key="message.id"
            class="message"
            :class="{ 'ai-message': message.participant?.type === 'AI' }"
          >
            <div class="message-header">
              <span class="participant-name">{{ message.participant?.name || 'Unknown' }}</span>
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            </div>
            <div class="message-content">{{ message.content }}</div>
          </div>

          <div v-if="typingParticipants.length > 0" class="typing-indicator">
            <span v-for="p in typingParticipants" :key="p.id">
              {{ p.name }} is typing...
            </span>
          </div>
        </div>
      </div>

      <div class="sidebar">
        <div class="participants-section">
          <h3>Participants ({{ participants.length }})</h3>
          <div class="participants-list">
            <div
              v-for="participant in participants"
              :key="participant.id"
              class="participant-item"
              :class="{ 
                active: participant.isActive,
                ai: participant.type === 'AI'
              }"
            >
              <div class="participant-avatar">
                {{ getInitials(participant.name) }}
              </div>
              <div class="participant-info">
                <div class="participant-name">{{ participant.name }}</div>
                <div class="participant-meta">
                  <span class="participant-type">{{ participant.type }}</span>
                  <span v-if="participant.message_count" class="message-count">
                    {{ participant.message_count }} messages
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="session-info">
          <h3>Session Info</h3>
          <div class="info-item">
            <span class="label">Duration:</span>
            <span>{{ sessionDuration }}</span>
          </div>
          <div class="info-item">
            <span class="label">Messages:</span>
            <span>{{ messages.length }}</span>
          </div>
          <div class="info-item">
            <span class="label">Condition:</span>
            <span>{{ session.condition?.name || 'Default' }}</span>
          </div>
        </div>

        <div class="session-actions">
          <button 
            v-if="session.status === 'active'"
            class="btn btn-danger"
            @click="endSession"
          >
            End Session
          </button>
          <button 
            class="btn btn-secondary"
            @click="exportChat"
          >
            Export Chat
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'
import { useSessions } from '@/composables/useSessions'

const props = defineProps({
  session: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['close', 'update'])

const { completeSession } = useSessions()
const messagesContainer = ref(null)

// WebSocket connection
const wsUrl = computed(() => {
  const baseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'
  return `${baseUrl}/session/${props.session.id}?participant_id=monitor`
})

const { 
  isConnected, 
  messages: wsMessages, 
  connect, 
  disconnect, 
  sendMessage 
} = useWebSocket(wsUrl.value)

const messages = ref([])
const participants = ref([])
const typingParticipants = ref([])
const sessionStartTime = ref(new Date(props.session.created_at))

const sessionDuration = computed(() => {
  const now = new Date()
  const diff = now - sessionStartTime.value
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`
  }
  return `${minutes}m`
})

// Handle incoming WebSocket messages
watch(wsMessages, (newMessages) => {
  newMessages.forEach(msg => {
    switch (msg.type) {
      case 'session_info':
        participants.value = msg.participants || []
        messages.value = msg.message_history || []
        break
        
      case 'chat':
        messages.value.push(msg)
        scrollToBottom()
        break
        
      case 'participant_joined':
        const newParticipant = {
          id: msg.participant_id,
          name: msg.participant_name || msg.participant?.name,
          type: msg.participant?.type || 'HUMAN',
          isActive: true,
          message_count: 0,
        }
        participants.value.push(newParticipant)
        break
        
      case 'participant_left':
        const index = participants.value.findIndex(p => p.id === msg.participant_id)
        if (index !== -1) {
          participants.value[index].isActive = false
        }
        break
        
      case 'typing':
        handleTypingIndicator(msg)
        break
        
      case 'session_completed':
        emit('update', { ...props.session, status: 'completed' })
        break
    }
  })
})

const handleTypingIndicator = (msg) => {
  const participant = participants.value.find(p => p.id === msg.participant_id)
  if (!participant) return
  
  if (msg.is_typing) {
    if (!typingParticipants.value.find(p => p.id === participant.id)) {
      typingParticipants.value.push(participant)
    }
    // Clear typing after 3 seconds
    setTimeout(() => {
      const index = typingParticipants.value.findIndex(p => p.id === participant.id)
      if (index !== -1) {
        typingParticipants.value.splice(index, 1)
      }
    }, 3000)
  } else {
    const index = typingParticipants.value.findIndex(p => p.id === participant.id)
    if (index !== -1) {
      typingParticipants.value.splice(index, 1)
    }
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getInitials = (name) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const endSession = async () => {
  if (confirm('Are you sure you want to end this session?')) {
    try {
      await completeSession(props.session.id, 'monitor')
      emit('close')
    } catch (error) {
      console.error('Failed to end session:', error)
    }
  }
}

const exportChat = () => {
  const chatData = {
    session: {
      id: props.session.id,
      experiment: props.session.experiment?.name,
      condition: props.session.condition?.name,
      access_code: props.session.access_code,
      created_at: props.session.created_at,
    },
    participants: participants.value,
    messages: messages.value,
  }
  
  const dataStr = JSON.stringify(chatData, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `session_${props.session.id}_chat.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

onMounted(() => {
  connect()
})

onUnmounted(() => {
  disconnect()
})
</script>

<style lang="scss" scoped>
.session-monitor {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  z-index: 1000;
}

.monitor-header {
  background: white;
  border-bottom: 1px solid #e5e5e5;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;

  h2 {
    margin: 0;
    flex: 1;
  }

  .btn-back {
    background: none;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    color: #666;

    &:hover {
      color: #333;
    }
  }
}

.session-status {
  display: flex;
  align-items: center;
  gap: 1rem;

  .status {
    padding: 0.25rem 0.75rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;

    &.active {
      background: #d4edda;
      color: #155724;
    }

    &.completed {
      background: #cce5ff;
      color: #004085;
    }
  }

  .access-code {
    background: #f5f5f5;
    padding: 0.25rem 0.75rem;
    border-radius: 0.25rem;
    font-family: monospace;
  }
}

.monitor-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  margin: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chat-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
  }
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #666;

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #dc3545;
  }

  &.connected .dot {
    background: #28a745;
  }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.no-messages {
  text-align: center;
  color: #999;
  padding: 3rem;
}

.message {
  margin-bottom: 1.5rem;

  &.ai-message {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 3px solid #6c757d;
  }
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;

  .participant-name {
    font-weight: 500;
    color: #333;
  }

  .message-time {
    font-size: 0.75rem;
    color: #999;
  }
}

.message-content {
  color: #333;
  line-height: 1.5;
}

.typing-indicator {
  font-style: italic;
  color: #666;
  font-size: 0.875rem;
}

.sidebar {
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem 1rem 1rem 0;
}

.participants-section,
.session-info {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  h3 {
    margin: 0 0 1rem 0;
    font-size: 1.125rem;
  }
}

.participants-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.participant-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 0.375rem;

  &.ai {
    background: #f8f9fa;
  }

  &:not(.active) {
    opacity: 0.5;
  }
}

.participant-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #4CAF50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 500;
}

.participant-info {
  flex: 1;

  .participant-name {
    font-weight: 500;
    color: #333;
  }

  .participant-meta {
    display: flex;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: #666;
  }
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;

  .label {
    color: #666;
  }
}

.session-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: auto;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;

  &-secondary {
    background: #f5f5f5;
    color: #333;

    &:hover {
      background: #e5e5e5;
    }
  }

  &-danger {
    background: #dc3545;
    color: white;

    &:hover {
      background: #c82333;
    }
  }
}
</style>