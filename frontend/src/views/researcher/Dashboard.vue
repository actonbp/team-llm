<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Researcher Dashboard</h1>
      <p>Manage experiments and monitor sessions</p>
    </div>
    
    <div class="dashboard-content">
      <div class="section">
        <h2>Experiments</h2>
        <p>Experiment management coming soon...</p>
      </div>
      
      <div class="section">
        <h2>Active Sessions</h2>
        <p>Session monitoring coming soon...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
// Researcher dashboard component
</script>

<style lang="scss" scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.dashboard-header {
  background: white;
  border-bottom: 1px solid #e5e5e5;
  padding: 2rem;
  
  h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }
  
  p {
    color: #666;
  }
}

.dashboard-content {
  padding: 2rem;
  
  .section {
    background: white;
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    
    h2 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
    }
    
    p {
      color: #666;
    }
  }
}
</style>