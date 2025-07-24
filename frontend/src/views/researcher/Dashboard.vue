<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Researcher Dashboard</h1>
      <p>Manage experiments and monitor sessions</p>
    </div>
    
    <div class="dashboard-content">
      <div class="tabs">
        <button 
          class="tab" 
          :class="{ active: activeTab === 'experiments' }"
          @click="activeTab = 'experiments'"
        >
          Experiments
        </button>
        <button 
          class="tab" 
          :class="{ active: activeTab === 'sessions' }"
          @click="activeTab = 'sessions'"
        >
          Active Sessions
        </button>
        <button 
          class="tab" 
          :class="{ active: activeTab === 'participants' }"
          @click="activeTab = 'participants'"
        >
          Participants
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'experiments'" class="section">
          <ExperimentList @select="selectExperiment" />
        </div>
        
        <div v-else-if="activeTab === 'sessions'" class="section">
          <h2>Active Sessions</h2>
          <p>Session monitoring coming soon...</p>
        </div>

        <div v-else-if="activeTab === 'participants'" class="section">
          <h2>Participants</h2>
          <p>Participant management coming soon...</p>
        </div>
      </div>
    </div>

    <!-- Experiment Detail Modal -->
    <ExperimentDetail 
      v-if="selectedExperiment"
      :experiment="selectedExperiment"
      @close="selectedExperiment = null"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ExperimentList from '@/components/experiments/ExperimentList.vue'
import ExperimentDetail from '@/components/experiments/ExperimentDetail.vue'

const activeTab = ref('experiments')
const selectedExperiment = ref(null)

const selectExperiment = (experiment) => {
  selectedExperiment.value = experiment
}
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
  
  .tabs {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    border-bottom: 2px solid #e5e5e5;
    
    .tab {
      padding: 1rem 2rem;
      background: none;
      border: none;
      border-bottom: 3px solid transparent;
      font-size: 1rem;
      font-weight: 500;
      color: #666;
      cursor: pointer;
      transition: all 0.2s;
      
      &:hover {
        color: #333;
      }
      
      &.active {
        color: #4CAF50;
        border-bottom-color: #4CAF50;
      }
    }
  }
  
  .tab-content {
    .section {
      background: white;
      border-radius: 0.5rem;
      padding: 1.5rem;
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
}
</style>