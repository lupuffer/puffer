<template>
  <section class="community-intro">
    <div class="intro-content">
      <h1><i class="fas fa-graduation-cap"></i> {{ hero.title }}</h1>
      <p class="intro-subtitle">{{ hero.subtitle }}</p>
      <p class="intro-description">{{ hero.description }}</p>
      <div class="intro-stats">
        <div v-for="stat in hero.stats" :key="stat.label" class="stat-item">
          <i :class="stat.icon"></i>
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
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
.community-intro {
  background: linear-gradient(135deg, #1a56db 0%, #3b82f6 100%);
  color: white;
  padding: 28px 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  text-align: center;
}

.intro-content h1 {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.intro-subtitle {
  font-size: 15px;
  font-weight: 500;
  opacity: 0.9;
  margin-bottom: 10px;
}

.intro-description {
  font-size: 14px;
  opacity: 0.8;
  max-width: 500px;
  margin: 0 auto 16px;
  line-height: 1.5;
}

.intro-stats {
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-item i {
  font-size: 20px;
  opacity: 0.8;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
}

.stat-label {
  font-size: 13px;
  opacity: 0.8;
}
</style>
