<template>
  <div class="chat-page">
    <div class="chat-container">
      <!-- Chat Header -->
      <div class="chat-header">
        <h2>Team Discussion</h2>
        <div class="session-info">
          Session: {{ sessionId }}
        </div>
      </div>
      
      <!-- Main Content -->
      <div class="chat-content">
        <!-- Sidebar -->
        <div class="sidebar">
          <div class="panel">
            <h3>Task Instructions</h3>
            <p>{{ taskInstructions }}</p>
          </div>
          
          <div class="panel">
            <h3>Your Information</h3>
            <p>{{ participantInfo }}</p>
          </div>
          
          <div class="panel">
            <h3>Team Members</h3>
            <ul class="team-members">
              <li v-for="participant in participants" :key="participant.participant_id">
                {{ participant.participant_name }}
              </li>
            </ul>
          </div>
        </div>
        
        <!-- Chat Area -->
        <div class="chat-area">
          <div class="messages" ref="messagesContainer">
            <div
              v-for="message in messages"
              :key="message.message_id"
              class="message"
              :class="{ 'own-message': message.participant_id === participantId }"
            >
              <div class="message-header">
                <span class="participant-name">{{ message.participant_name }}</span>
                <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="message-content">
                {{ message.content }}
              </div>
            </div>
            
            <div v-if="typingUsers.size > 0" class="typing-indicator">
              Someone is typing...
            </div>
          </div>
          
          <!-- Input Area -->
          <div class="input-area">
            <input
              v-model="messageInput"
              @keyup.enter="sendMessage"
              @input="handleTyping"
              type="text"
              placeholder="Type your message..."
              class="message-input"
            />
            <button @click="sendMessage" class="send-button">Send</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useWebSocket } from '@/composables/useWebSocket'

const route = useRoute()
const sessionId = ref(route.params.sessionId)
const participantId = ref(localStorage.getItem('participantId'))

// Chat state
const messageInput = ref('')
const messagesContainer = ref(null)
const taskInstructions = ref('Loading...')
const participantInfo = ref('Loading...')

// WebSocket connection
const {
  connected,
  messages,
  participants,
  typingUsers,
  connect,
  sendMessage: wsSendMessage,
  sendTypingIndicator
} = useWebSocket(sessionId.value, participantId.value)

// Initialize connection
onMounted(() => {
  connect()
})

// Auto-scroll to bottom on new messages
watch(messages, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})

// Typing indicator
let typingTimeout
const handleTyping = () => {
  sendTypingIndicator(true)
  clearTimeout(typingTimeout)
  typingTimeout = setTimeout(() => {
    sendTypingIndicator(false)
  }, 1000)
}

// Send message
const sendMessage = () => {
  if (messageInput.value.trim()) {
    wsSendMessage(messageInput.value)
    messageInput.value = ''
    sendTypingIndicator(false)
  }
}

// Format timestamp
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}
</script>

<style lang="scss" scoped>
.chat-page {
  height: 100vh;
  background: #f5f5f5;
}

.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header {
  background: white;
  border-bottom: 1px solid #e5e5e5;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h2 {
    margin: 0;
    font-size: 1.5rem;
  }
  
  .session-info {
    color: #666;
    font-size: 0.875rem;
  }
}

.chat-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background: white;
  border-right: 1px solid #e5e5e5;
  padding: 1rem;
  overflow-y: auto;
  
  .panel {
    margin-bottom: 2rem;
    
    h3 {
      font-size: 1rem;
      margin-bottom: 0.5rem;
      color: #374151;
    }
    
    p {
      color: #666;
      font-size: 0.875rem;
      line-height: 1.5;
    }
  }
  
  .team-members {
    list-style: none;
    
    li {
      padding: 0.5rem 0;
      color: #666;
    }
  }
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  
  .message {
    margin-bottom: 1rem;
    
    &.own-message {
      .message-content {
        background: #3b82f6;
        color: white;
        margin-left: auto;
        margin-right: 0;
      }
    }
  }
  
  .message-header {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
    font-size: 0.875rem;
    
    .participant-name {
      font-weight: 500;
      color: #374151;
    }
    
    .timestamp {
      color: #9ca3af;
    }
  }
  
  .message-content {
    background: white;
    padding: 0.75rem;
    border-radius: 0.5rem;
    max-width: 70%;
    word-wrap: break-word;
  }
  
  .typing-indicator {
    color: #666;
    font-style: italic;
    font-size: 0.875rem;
  }
}

.input-area {
  background: white;
  border-top: 1px solid #e5e5e5;
  padding: 1rem;
  display: flex;
  gap: 0.5rem;
  
  .message-input {
    flex: 1;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 1rem;
    
    &:focus {
      outline: none;
      border-color: #3b82f6;
    }
  }
  
  .send-button {
    padding: 0.75rem 1.5rem;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
    
    &:hover {
      background: #2563eb;
    }
  }
}
</style>