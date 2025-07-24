<template>
  <div class="home">
    <div class="hero">
      <h1>Team-LLM Platform</h1>
      <p>Multi-Agent Team Experiment Platform for Human-AI Collaboration Research</p>
      
      <div class="actions">
        <router-link to="/join" class="btn btn-primary">
          Join as Participant
        </router-link>
        <router-link to="/researcher" class="btn btn-secondary">
          Researcher Dashboard
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
// Home page component
</script>

<style lang="scss" scoped>
.home {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.hero {
  text-align: center;
  max-width: 600px;
  padding: 2rem;
  
  h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #333;
  }
  
  p {
    font-size: 1.2rem;
    color: #666;
    margin-bottom: 2rem;
  }
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
  
  &.btn-primary {
    background: #3b82f6;
    color: white;
    
    &:hover {
      background: #2563eb;
    }
  }
  
  &.btn-secondary {
    background: #6b7280;
    color: white;
    
    &:hover {
      background: #4b5563;
    }
  }
}
</style>