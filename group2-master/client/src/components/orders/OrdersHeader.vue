<template>
  <section class="orders-header">
    <h1><i class="fas fa-clipboard-list"></i> {{ hero.title }}</h1>
    <p v-if="hero.description">{{ hero.description }}</p>
    <div class="orders-stats">
      <div v-for="stat in hero.stats" :key="stat.label" class="stat-item">
        <i :class="stat.icon"></i>
        <div><strong>{{ stat.value }}</strong><span>{{ stat.label }}</span></div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  hero: { type: Object, required: true },
})
</script>

<style scoped>
.orders-header {
  background: linear-gradient(135deg, var(--primary-blue) 0%, #3b82f6 100%);
  color: white;
  padding: 32px;
  border-radius: 16px;
  margin-bottom: 24px;
}

.orders-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.orders-header p {
  font-size: 15px;
  opacity: 0.9;
  margin-bottom: 24px;
}

.orders-stats {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.1);
  padding: 16px 20px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.stat-item i {
  font-size: 24px;
  opacity: 0.8;
}

.stat-item strong {
  font-size: 20px;
  font-weight: 700;
  display: block;
}

.stat-item span {
  font-size: 14px;
  opacity: 0.8;
}
</style>
