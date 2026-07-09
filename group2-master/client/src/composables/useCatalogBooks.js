import { ref } from 'vue'

const DEFAULT_CATALOG_PATH = '/data.json'
const LOCAL_CONDITIONS = ['new', 'like-new', 'good', 'fair']
const LOCAL_CAMPUSES = ['zijingang', 'yuquan', 'xixi', 'zhijiang', 'huajiachi']
const LOCAL_SELLERS = ['seller_001', 'seller_002', 'seller_003', 'seller_004', 'seller_005']

const CONDITION_LABELS = {
  new: '全新',
  'like-new': '九成新',
  good: '良好',
  fair: '一般',
}

const CAMPUS_LABELS = {
  zijingang: '紫金港校区',
  yuquan: '玉泉校区',
  xixi: '西溪校区',
  zhijiang: '之江校区',
  huajiachi: '华家池校区',
}

const SELLER_LABELS = {
  seller_001: { name: '目录卖家 A', reputation: 'A', creditScore: 102 },
  seller_002: { name: '目录卖家 B', reputation: 'A', creditScore: 98 },
  seller_003: { name: '目录卖家 C', reputation: 'B+', creditScore: 87 },
  seller_004: { name: '目录卖家 D', reputation: 'A+', creditScore: 105 },
  seller_005: { name: '目录卖家 E', reputation: 'B', creditScore: 82 },
}

const catalogBooks = ref([])
const catalogLoading = ref(false)
let catalogPromise = null

const truncateOneDecimal = (value) => Math.floor(Number(value || 0) * 10) / 10

export const normalizeCatalogImage = (path = '') => {
  if (!path) return ''
  if (path.startsWith('./images/')) return path.replace('./images/', '/images/')
  if (/^book\d+\.jpg$/.test(path)) return `/images/${path}`
  return path
}

const normalizeCatalogBook = (item) => {
  const id = Number(item.id || 0)
  const condition = LOCAL_CONDITIONS[id % LOCAL_CONDITIONS.length]
  const campus = LOCAL_CAMPUSES[id % LOCAL_CAMPUSES.length]
  const sellerId = LOCAL_SELLERS[id % LOCAL_SELLERS.length]
  const seller = SELLER_LABELS[sellerId]
  const image = normalizeCatalogImage(item.image || item.img)

  return {
    ...item,
    id,
    name: item.name || `商品${id}`,
    title: item.title || item.name || `商品${id}`,
    author: item.author || `作者${((id - 1) % 10) + 1}`,
    publisher: item.publisher || 'SeekBook Catalog',
    edition: item.edition || 'Catalog Edition',
    isbn: item.isbn || `9787${String(id).padStart(9, '0')}`.slice(-13),
    price: truncateOneDecimal(item.price || 0),
    image,
    img: normalizeCatalogImage(item.img),
    coverImage: normalizeCatalogImage(item.coverImage || image),
    condition,
    conditionLabel: CONDITION_LABELS[condition],
    campus,
    campusLabel: CAMPUS_LABELS[campus],
    tradeMethod: 'face',
    tradeMethodLabel: '当面交易',
    hasNotes: id % 7 === 0,
    sellerId,
    seller: {
      id: sellerId,
      name: seller.name,
      reputation: seller.reputation,
      creditScore: seller.creditScore,
    },
    sellerReputation: seller.reputation,
    sellerCreditScore: seller.creditScore,
    createdAt: '2024-01-01T00:00:00',
  }
}

export const loadCatalogBooks = async (source = DEFAULT_CATALOG_PATH) => {
  if (catalogBooks.value.length) return catalogBooks.value
  if (catalogPromise) return catalogPromise

  catalogLoading.value = true
  catalogPromise = fetch(source)
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Failed to fetch catalog: ${response.status}`)
      }

      const data = await response.json()
      if (!Array.isArray(data)) {
        throw new Error('Catalog payload is not an array')
      }

      catalogBooks.value = data.map(normalizeCatalogBook)
      return catalogBooks.value
    })
    .catch((error) => {
      console.error('加载十万级目录失败', error)
      catalogBooks.value = []
      return catalogBooks.value
    })
    .finally(() => {
      catalogLoading.value = false
      catalogPromise = null
    })

  return catalogPromise
}

export const useCatalogBooks = () => ({
  catalogBooks,
  catalogLoading,
  loadCatalogBooks,
})

export { catalogBooks }
