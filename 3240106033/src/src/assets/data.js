import { ref } from 'vue'

export function useData() {
  const info = ref({
    name: { zh: '', en: '' },
    status: '',
    school: { name: '', url: '' },
    major: '',
    hometown: '',
    enrollment: '',
    graduation: '',
    contact: { email: '', phone: '', address: '' },
    avatar: '',
    education: [],
    research: { quote: '', areas: [] },
    awards: []
  })

  const books = ref([])

  async function loadData() {
    try {
      const infoResponse = await fetch('/info.json')
      if (infoResponse.ok) {
        const infoData = await infoResponse.json()
        info.value = infoData
      }

      const booksResponse = await fetch('/books.json')
      if (booksResponse.ok) {
        const booksData = await booksResponse.json()
        books.value = booksData
      }
    } catch (error) {
      console.error('加载数据失败:', error)
    }
  }

  return {
    info,
    books,
    loadData
  }
}