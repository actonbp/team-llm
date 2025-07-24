import { ref, onUnmounted } from 'vue'

export function useWebSocket(url = null) {
  const socket = ref(null)
  const isConnected = ref(false)
  const messages = ref([])
  const participants = ref([])
  const typingUsers = ref(new Set())
  
  const connect = (wsUrl = url) => {
    if (!wsUrl) {
      console.error('WebSocket URL is required')
      return
    }
    
    socket.value = new WebSocket(wsUrl)
    
    socket.value.onopen = () => {
      console.log('WebSocket connected')
      isConnected.value = true
    }
    
    socket.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleMessage(data)
    }
    
    socket.value.onclose = () => {
      console.log('WebSocket disconnected')
      isConnected.value = false
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
  
  const sendMessage = (message) => {
    if (socket.value && isConnected.value) {
      if (typeof message === 'string') {
        socket.value.send(JSON.stringify({
          type: 'chat',
          content: message
        }))
      } else {
        socket.value.send(JSON.stringify(message))
      }
    }
  }
  
  const sendTypingIndicator = (isTyping) => {
    if (socket.value && isConnected.value) {
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
    isConnected,
    messages,
    participants,
    typingUsers,
    connect,
    sendMessage,
    sendTypingIndicator,
    disconnect
  }
}