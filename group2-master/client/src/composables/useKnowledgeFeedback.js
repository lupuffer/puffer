import { ref } from 'vue'

const toasts = ref([])
const confirmState = ref({
  open: false,
  title: '',
  message: '',
  confirmText: '确认',
  cancelText: '取消',
})

let nextToastId = 1
let confirmResolver = null

const removeToast = (id) => {
  toasts.value = toasts.value.filter((toast) => toast.id !== id)
}

const showToast = (message, type = 'info', duration = 2600) => {
  const id = nextToastId++
  toasts.value.push({ id, message, type })
  window.setTimeout(() => removeToast(id), duration)
}

const requestConfirm = ({ title, message, confirmText = '确认', cancelText = '取消' }) => {
  confirmState.value = {
    open: true,
    title,
    message,
    confirmText,
    cancelText,
  }

  return new Promise((resolve) => {
    confirmResolver = resolve
  })
}

const settleConfirm = (accepted) => {
  if (confirmResolver) {
    confirmResolver(accepted)
  }

  confirmResolver = null
  confirmState.value = {
    ...confirmState.value,
    open: false,
  }
}

export const useKnowledgeFeedback = () => ({
  toasts,
  confirmState,
  showToast,
  requestConfirm,
  acceptConfirm: () => settleConfirm(true),
  cancelConfirm: () => settleConfirm(false),
  removeToast,
})
