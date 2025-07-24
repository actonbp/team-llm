<template>
  <div class="dialog-overlay" @click="$emit('cancel')">
    <div class="dialog" @click.stop>
      <h2>{{ title }}</h2>
      <p>{{ message }}</p>
      <div class="dialog-actions">
        <button class="btn btn-secondary" @click="$emit('cancel')">
          Cancel
        </button>
        <button class="btn btn-danger" @click="$emit('confirm')">
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  message: {
    type: String,
    required: true,
  },
  confirmText: {
    type: String,
    default: 'Confirm',
  },
})

defineEmits(['confirm', 'cancel'])
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
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

  h2 {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
  }

  p {
    margin: 0 0 2rem 0;
    color: #666;
  }
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;

  &-secondary {
    background: #f5f5f5;
    color: #333;

    &:hover {
      background: #e5e5e5;
    }
  }

  &-danger {
    background: #f44336;
    color: white;

    &:hover {
      background: #d32f2f;
    }
  }
}
</style>