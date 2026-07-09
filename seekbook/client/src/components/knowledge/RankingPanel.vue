<template>
  <aside class="ranking-panel">
    <section class="panel-card">
      <div class="panel-head">
        <h3>本周热门资料</h3>
      </div>
      <button
        v-for="(item, index) in hotMaterials"
        :key="item.id"
        type="button"
        class="rank-item"
        @click="goMaterial(item.id)"
      >
        <div class="rank-headline">
          <span class="rank-no" :class="rankClass(index)">{{ index + 1 }}</span>
          <strong>{{ item.title }}</strong>
        </div>
        <span>{{ item.downloads }} 下载 · {{ formatPrice(item.pricePoints) }}</span>
      </button>
    </section>

    <section class="panel-card">
      <div class="panel-head">
        <h3>热门讨论</h3>
      </div>
      <p v-if="!hotDiscussions.length" class="empty-copy">暂无热门讨论</p>
      <button
        v-for="(item, index) in hotDiscussions"
        :key="item.id"
        type="button"
        class="rank-item"
        @click="goDiscussion(item.id)"
      >
        <div class="discussion-rank-title">
          <span class="rank-no" :class="rankClass(index)">{{ index + 1 }}</span>
          <strong>{{ item.title }}</strong>
          <span class="mini-type" :class="discussionTypeClass(item.type)">{{ item.type }}</span>
        </div>
        <span>{{ item.replies }} 回复 · {{ item.likes }} 点赞</span>
      </button>
    </section>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

defineProps({
  hotMaterials: {
    type: Array,
    default: () => [],
  },
  hotDiscussions: {
    type: Array,
    default: () => [],
  },
  formatPrice: {
    type: Function,
    required: true,
  },
})

const router = useRouter()

const goMaterial = (id) => router.push(`/knowledge/material/${id}`)
const goDiscussion = (id) => router.push(`/knowledge/discussion/${id}`)

const rankClass = (index) => {
  if (index === 0) return 'is-first'
  if (index === 1) return 'is-second'
  if (index === 2) return 'is-third'
  return ''
}

const discussionTypeClass = (type) => {
  if (type === '求助') return 'is-help'
  if (type === '求资料') return 'is-request'
  return 'is-talk'
}
</script>

<style scoped>
.ranking-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.panel-card {
  padding: 16px 18px;
  border-radius: 22px;
  border: 1px solid rgba(224, 232, 255, 0.96);
  background: #fff;
  box-shadow: 0 18px 40px rgba(90, 107, 162, 0.12);
}

.panel-head {
  margin-bottom: 10px;
}

.panel-head h3 {
  color: #18233b;
  font-size: 18px;
}

.rank-item {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 11px 0;
  border: none;
  border-top: 1px solid #edf2ff;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.rank-item:first-of-type {
  border-top: none;
}

.rank-item strong {
  display: block;
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  color: #22304e;
  line-height: 1.45;
}

.rank-item span {
  color: #708096;
  font-size: 13px;
}

.rank-headline,
.discussion-rank-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rank-headline strong,
.discussion-rank-title strong {
  flex: 1;
}

.rank-no {
  width: 24px;
  height: 24px;
  display: inline-grid;
  place-items: center;
  flex-shrink: 0;
  border-radius: 999px;
  background: #f3f6ff;
  color: #5e7091;
  font-size: 12px;
  font-weight: 800;
}

.rank-no.is-first {
  background: #fff3d6;
  color: #b7791f;
}

.rank-no.is-second {
  background: #edf2f7;
  color: #516176;
}

.rank-no.is-third {
  background: #fdece5;
  color: #b45309;
}

.mini-type {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 0 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.mini-type.is-talk {
  background: #ecefff;
  color: #465ed2;
}

.mini-type.is-help {
  background: #fff1df;
  color: #d97706;
}

.mini-type.is-request {
  background: #edf8ef;
  color: #15803d;
}

.empty-copy {
  color: #708096;
  font-size: 13px;
}

@media (max-width: 1024px) {
  .ranking-panel {
    order: 3;
  }
}
</style>
