<template>
  <aside class="recycle-sidebar">
    <div v-for="card in cards" :key="card.title" class="recycle-card-small">
      <div class="icon"><i :class="card.icon"></i></div>
      <h4>{{ card.title }}</h4>
      <p v-for="line in card.description.split('\n')" :key="line">{{ line }}</p>
      <button class="btn btn-outline btn-sm" type="button">{{ card.button }}</button>
    </div>
    <div v-if="tip" class="info-tip-small">
      <i class="fas fa-lightbulb"></i>
      <span>{{ tip }}</span>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  cards: { type: Array, required: true },
  tip: { type: String, default: '' },
})
</script>

<style scoped>
.recycle-sidebar {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recycle-card-small {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--gray-200);
  text-align: center;
}

.recycle-card-small .icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--light-blue);
  color: var(--primary-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 10px;
  font-size: 18px;
}

.recycle-card-small h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 6px;
}

.recycle-card-small p {
  font-size: 12px;
  color: var(--gray-500);
  line-height: 1.5;
}

.recycle-card-small .btn-sm {
  width: 100%;
  padding: 8px 12px;
  font-size: 12px;
  margin-top: 12px;
  border-radius: 8px;
  background: white;
  color: var(--gray-700);
  border: 1px solid var(--gray-300);
  cursor: pointer;
}

.info-tip-small {
  background: var(--light-blue);
  border-left: 3px solid var(--primary-blue);
  padding: 10px 12px;
  border-radius: 0 8px 8px 0;
  font-size: 12px;
  color: var(--gray-700);
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-tip-small i {
  color: var(--accent-orange);
  font-size: 14px;
}

@media (max-width: 1024px) {
  .recycle-sidebar {
    flex-direction: row;
  }

  .recycle-card-small {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .recycle-sidebar {
    flex-direction: column;
  }
}
</style>
