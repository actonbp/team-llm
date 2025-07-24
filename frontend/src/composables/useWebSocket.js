import { ref, onUnmounted } from 'vue'

export function useWebSocket(sessionId, participantId) {
  const socket = ref(null)
  const connected = ref(false)
  const messages = ref([])
  const participants = ref([])
  const typingUsers = ref(new Set())
  
  const connect = () => {
    const wsUrl = `ws://localhost:8000/ws/chat/${sessionId}?participant_id=${participantId}`
    socket.value = new WebSocket(wsUrl)
    
    socket.value.onopen = () => {
      console.log('WebSocket connected')
      connected.value = true
    }
    
    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleMessage(data)
    }
    
    socket.value.onclose = () => {
      console.log('WebSocket disconnected')
      connected.value = false
    }
    
    socket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }
  
  const handleMessage = (data) => {
    switch (data.type) {
      case 'chat':
        messages.value.push(data)
        break
        
      case 'participant_joined':
        // Handle participant joining
        break
        
      case 'participant_left':
        // Handle participant leaving
        break
        
      case 'typing':
        if (data.is_typing) {
          typingUsers.value.add(data.participant_id)
        } else {
          typingUsers.value.delete(data.participant_id)
        }
        break
        
      case 'session_info':
        participants.value = data.participants
        break
    }
  }
  
  const sendMessage = (content) => {
    if (socket.value && connected.value) {
      socket.value.send(JSON.stringify({
        type: 'chat',
        content
      }))
    }
  }
  
  const sendTypingIndicator = (isTyping) => {
    if (socket.value && connected.value) {
      socket.value.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping
      }))
    }
  }
  
  const disconnect = () => {
    if (socket.value) {
      socket.value.close()
    }
  }
  
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    connected,
    messages,
    participants,
    typingUsers,
    connect,
    sendMessage,
    sendTypingIndicator,
    disconnect
  }
}