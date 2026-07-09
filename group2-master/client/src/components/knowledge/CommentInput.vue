<template>
  <div class="comment-input-box">
    <div v-if="replyTarget" class="reply-banner">
      <span>回复 @{{ replyTarget.authorName }}</span>
      <button type="button" @click="$emit('cancel-reply')">取消回复</button>
    </div>

    <div class="input-shell">
      <textarea
        :value="modelValue"
        :placeholder="placeholder"
        rows="4"
        maxlength="500"
        @input="$emit('update:modelValue', $event.target.value)"
        @focus="$emit('focus')"
      ></textarea>
      <div class="input-foot">
        <span>{{ modelValue.length }}/500</span>
        <button type="button" class="submit-btn" @click="$emit('submit')">发布</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '写下你的回复…',
  },
  replyTarget: {
    type: Object,
    default: null,
  },
})

defineEmits(['update:modelValue', 'submit', 'cancel-reply', 'focus'])
</script>

<style scoped>
.comment-input-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reply-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 14px;
  background: #eef3ff;
  color: #41526b;
  font-size: 13px;
  font-weight: 700;
}

.reply-banner button,
.submit-btn {
  border: none;
  cursor: pointer;
}

.reply-banner button {
  color: #3557d1;
  background: transparent;
  font-weight: 700;
}

.input-shell {
  padding: 14px;
  border-radius: 18px;
  border: 1px solid #dce5ff;
  background: #fff;
}

.input-shell textarea {
  width: 100%;
  min-height: 108px;
  border: none;
  resize: vertical;
  color: #2d3b58;
  line-height: 1.8;
}

.input-shell textarea:focus {
  outline: none;
}

.input-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 10px;
  color: #73839c;
  font-size: 12px;
}

.submit-btn {
  min-height: 38px;
  padding: 0 16px;
  border-radius: 12px;
  color: #fff;
  font-weight: 700;
  background: linear-gradient(135deg, #2f80ed 0%, #6f84ff 64%, #a78bfa 100%);
}
</style>
