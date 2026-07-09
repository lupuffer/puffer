import { computed, ref } from 'vue'

export const KNOWLEDGE_STORAGE_KEYS = {
  USER: 'qiushu_user',
  POINTS_BALANCE: 'qiushu_points_balance',
  CHECKINS: 'qiushu_checkins',
  MATERIALS: 'qiushu_materials',
  NEXT_MATERIAL_ID: 'qiushu_next_material_id',
  DISCUSSIONS: 'qiushu_discussions',
  NEXT_DISCUSSION_ID: 'qiushu_next_discussion_id',
  COMMENTS: 'qiushu_comments',
  NEXT_COMMENT_ID: 'qiushu_next_comment_id',
  LIKES: 'qiushu_likes',
  FAVORITES: 'qiushu_favorites',
  ENTITLEMENTS: 'qiushu_entitlements',
  VIEWS_DAILY: 'qiushu_views_daily',
  DOWNLOADS_DAILY: 'qiushu_downloads_daily',
  GUEST_ID: 'qiushu_guest_id',
}

export const MATERIAL_CATEGORIES = ['全部', '公共课', '专业课', '考研', '课堂笔记', '其他']
export const MATERIAL_SORTS = ['最新上传', '最多下载', '热度近7天']
export const DISCUSSION_TYPES = ['全部', '讨论', '求助', '求资料']
export const DISCUSSION_SORTS = ['最新发布', '热度近7天']

const POINTS_MAX = 100
const UPLOAD_REWARD = 10
const CHECKIN_REWARD = 5
const DEFAULT_PRICE_OPTIONS = [0, 5, 10, 15]
const REMOVED_TEST_MATERIALS = new Set(['11::222', '1111::2222', '线性代数提纲::', '线性代数提纲::提纲'])

const materials = ref([])
const discussions = ref([])
const comments = ref([])
const pointsByUser = ref({})
const checkins = ref([])
const likes = ref([])
const favorites = ref([])
const entitlements = ref([])
const viewsDaily = ref([])
const downloadsDaily = ref([])
const nextMaterialId = ref(1)
const nextDiscussionId = ref(1)
const nextCommentId = ref(1)

let initialized = false

const loadJson = (key, fallback) => {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

const saveJson = (key, value) => {
  localStorage.setItem(key, JSON.stringify(value))
}

const saveValue = (key, value) => {
  localStorage.setItem(key, String(value))
}

const todayKey = () => new Date().toISOString().slice(0, 10)

const createGuestId = () => `guest-${Math.random().toString(36).slice(2, 10)}`

const ensureGuestId = () => {
  const existing = localStorage.getItem(KNOWLEDGE_STORAGE_KEYS.GUEST_ID)
  if (existing) {
    return existing
  }

  const id = createGuestId()
  localStorage.setItem(KNOWLEDGE_STORAGE_KEYS.GUEST_ID, id)
  return id
}

const startOfNow = () => new Date().toISOString()

const shiftDays = (days) => {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString()
}

const calculateMaterialHeat = (material) =>
  (material.likes7d || 0) * 4 +
  (material.replies7d || 0) * 2 +
  (material.views7d || 0) +
  (material.downloads7d || 0) * 6

const calculateDiscussionHeat = (discussion) =>
  (discussion.likes7d || 0) * 5 + (discussion.replies7d || 0) * 3 + (discussion.views7d || 0)

const createSeedMaterials = () => {
  const seeds = [
    {
      title: '高等数学期末冲刺题集',
      category: '公共课',
      course: 'MATH101 高等数学',
      description: '整理了常见题型、易错点和压轴题思路，适合期末一周集中复习。',
      fileName: '高数期末冲刺题集.pdf',
      fileType: 'PDF',
      fileSize: 2_560_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 0,
      tags: ['期末复习', '高数', '真题'],
      authorId: 'seed-001',
      authorName: '林同学',
      createdAt: shiftDays(1),
      views: 86,
      downloads: 42,
      likes: 18,
      favorites: 11,
      views7d: 31,
      downloads7d: 18,
      likes7d: 7,
      replies7d: 0,
    },
    {
      title: '数据结构实验报告模板',
      category: '专业课',
      course: 'CS203 数据结构',
      description: '包含链表、栈队列、图结构实验报告模板和常见评分点提醒。',
      fileName: '数据结构实验报告模板.docx',
      fileType: 'Word',
      fileSize: 860_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 5,
      tags: ['实验报告', '数据结构'],
      authorId: 'seed-002',
      authorName: '周同学',
      createdAt: shiftDays(2),
      views: 74,
      downloads: 28,
      likes: 16,
      favorites: 9,
      views7d: 24,
      downloads7d: 12,
      likes7d: 5,
      replies7d: 0,
    },
    {
      title: '考研英语阅读精练笔记',
      category: '考研',
      course: '考研英语',
      description: '按题型整理的阅读笔记，包含长难句拆解和高频词组速记。',
      fileName: '考研英语阅读精练笔记.pdf',
      fileType: 'PDF',
      fileSize: 1_580_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 10,
      tags: ['考研', '英语', '阅读'],
      authorId: 'seed-003',
      authorName: '叶同学',
      createdAt: shiftDays(4),
      views: 121,
      downloads: 39,
      likes: 29,
      favorites: 21,
      views7d: 48,
      downloads7d: 16,
      likes7d: 10,
      replies7d: 0,
    },
    {
      title: '离散数学思维导图合集',
      category: '课堂笔记',
      course: 'CS112 离散数学',
      description: '章节思维导图和证明题套路总结，适合课后回顾和开卷复习。',
      fileName: '离散数学思维导图.png',
      fileType: '图片',
      fileSize: 1_120_000,
      previewUrl: '/images/book3.jpg',
      downloadUrl: '',
      pricePoints: 0,
      tags: ['离散数学', '思维导图'],
      authorId: 'seed-004',
      authorName: '陈同学',
      createdAt: shiftDays(0),
      views: 53,
      downloads: 22,
      likes: 9,
      favorites: 6,
      views7d: 19,
      downloads7d: 8,
      likes7d: 4,
      replies7d: 0,
    },
    {
      title: '计算机组成原理章节速查表',
      category: '专业课',
      course: '计算机组成原理',
      description: '覆盖数据表示、运算器、存储系统、指令系统与流水线的课堂速查笔记。',
      fileName: '计算机组成原理章节速查表.pdf',
      fileType: 'PDF',
      fileSize: 1_340_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 5,
      tags: ['组成原理', '速查表', '计算机'],
      authorId: 'seed-005',
      authorName: '顾同学',
      createdAt: shiftDays(1),
      views: 68,
      downloads: 24,
      likes: 14,
      favorites: 8,
      views7d: 22,
      downloads7d: 10,
      likes7d: 5,
      replies7d: 0,
    },
    {
      title: '概率论与数理统计公式卡片',
      category: '公共课',
      course: '概率论与数理统计',
      description: '按分布、数字特征、参数估计、假设检验整理常用公式和易混点。',
      fileName: '概率论与数理统计公式卡片.pdf',
      fileType: 'PDF',
      fileSize: 980_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 0,
      tags: ['概率论', '统计', '公式'],
      authorId: 'seed-006',
      authorName: '梁同学',
      createdAt: shiftDays(3),
      views: 92,
      downloads: 37,
      likes: 21,
      favorites: 13,
      views7d: 34,
      downloads7d: 15,
      likes7d: 8,
      replies7d: 0,
    },
    {
      title: '数据库系统 SQL 实验清单',
      category: '专业课',
      course: '数据库系统',
      description: '包含建表、查询、视图、事务与索引实验的检查清单和常见错误说明。',
      fileName: '数据库系统SQL实验清单.docx',
      fileType: 'Word',
      fileSize: 760_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 5,
      tags: ['数据库', 'SQL', '实验'],
      authorId: 'seed-007',
      authorName: '孟同学',
      createdAt: shiftDays(2),
      views: 81,
      downloads: 31,
      likes: 18,
      favorites: 10,
      views7d: 29,
      downloads7d: 13,
      likes7d: 6,
      replies7d: 0,
    },
    {
      title: 'Java 程序设计课堂样例合集',
      category: '专业课',
      course: 'Java程序设计',
      description: '整理面向对象、集合、异常、IO 与简单 Swing 示例代码，适合课后补齐练习。',
      fileName: 'Java程序设计课堂样例合集.zip',
      fileType: '压缩包',
      fileSize: 1_920_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 8,
      tags: ['Java', '样例代码', '程序设计'],
      authorId: 'seed-008',
      authorName: '陶同学',
      createdAt: shiftDays(5),
      views: 73,
      downloads: 26,
      likes: 15,
      favorites: 7,
      views7d: 21,
      downloads7d: 9,
      likes7d: 4,
      replies7d: 0,
    },
    {
      title: '微观经济学图形题整理',
      category: '专业课',
      course: '微观经济学',
      description: '需求供给、消费者选择、成本曲线、市场结构相关图形题和答题模板。',
      fileName: '微观经济学图形题整理.pdf',
      fileType: 'PDF',
      fileSize: 1_210_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 5,
      tags: ['微观经济学', '图形题', '经管'],
      authorId: 'seed-009',
      authorName: '沈同学',
      createdAt: shiftDays(1),
      views: 64,
      downloads: 22,
      likes: 12,
      favorites: 8,
      views7d: 20,
      downloads7d: 8,
      likes7d: 4,
      replies7d: 0,
    },
    {
      title: '管理学原理案例分析模板',
      category: '专业课',
      course: '管理学原理',
      description: '按计划、组织、领导、控制四类管理职能整理案例分析框架。',
      fileName: '管理学原理案例分析模板.docx',
      fileType: 'Word',
      fileSize: 640_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 0,
      tags: ['管理学', '案例分析'],
      authorId: 'seed-010',
      authorName: '秦同学',
      createdAt: shiftDays(2),
      views: 59,
      downloads: 18,
      likes: 11,
      favorites: 6,
      views7d: 18,
      downloads7d: 7,
      likes7d: 4,
      replies7d: 0,
    },
    {
      title: '会计学基础分录练习表',
      category: '专业课',
      course: '会计学基础',
      description: '按资产、负债、所有者权益、收入费用整理会计分录练习与答案。',
      fileName: '会计学基础分录练习表.xlsx',
      fileType: 'Excel',
      fileSize: 520_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 5,
      tags: ['会计学', '分录', '练习'],
      authorId: 'seed-011',
      authorName: '杜同学',
      createdAt: shiftDays(4),
      views: 71,
      downloads: 29,
      likes: 14,
      favorites: 9,
      views7d: 24,
      downloads7d: 11,
      likes7d: 5,
      replies7d: 0,
    },
    {
      title: '统计学 SPSS 操作笔记',
      category: '专业课',
      course: '统计学',
      description: '描述统计、相关分析、回归分析和假设检验的 SPSS 操作步骤截图版笔记。',
      fileName: '统计学SPSS操作笔记.pdf',
      fileType: 'PDF',
      fileSize: 1_680_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 8,
      tags: ['统计学', 'SPSS', '数据分析'],
      authorId: 'seed-012',
      authorName: '高同学',
      createdAt: shiftDays(3),
      views: 83,
      downloads: 35,
      likes: 17,
      favorites: 12,
      views7d: 28,
      downloads7d: 14,
      likes7d: 7,
      replies7d: 0,
    },
    {
      title: '大学英语听力课堂材料',
      category: '公共课',
      course: '大学英语',
      description: '课堂听力音频文本、关键词表和课后跟读材料，适合大学英语课程使用。',
      fileName: '大学英语听力课堂材料.pdf',
      fileType: 'PDF',
      fileSize: 900_000,
      previewUrl: '',
      downloadUrl: '',
      pricePoints: 0,
      tags: ['大学英语', '听力', '课堂材料'],
      authorId: 'seed-013',
      authorName: '许同学',
      createdAt: shiftDays(1),
      views: 77,
      downloads: 33,
      likes: 16,
      favorites: 10,
      views7d: 27,
      downloads7d: 12,
      likes7d: 6,
      replies7d: 0,
    },
  ]

  return seeds.map((item, index) => ({
    id: index + 1,
    ...item,
    heat7d: calculateMaterialHeat(item),
  }))
}

const createSeedDiscussions = () => {
  const seeds = [
    {
      type: '讨论',
      title: '高数二轮复习应该先刷题还是先回看错题？',
      content: '最近准备期末复习，想听听大家二轮复习的安排，尤其是公共课时间不太够的时候怎么取舍。',
      tags: ['高数', '期末'],
      authorId: 'seed-101',
      authorName: '赵同学',
      createdAt: shiftDays(0),
      views: 46,
      likes: 9,
      replies: 0,
      lastReplyAt: shiftDays(0),
      views7d: 18,
      likes7d: 4,
      replies7d: 0,
    },
    {
      type: '求助',
      title: '操作系统实验环境总是报权限错误，有同学遇到过吗？',
      content: '我在 Windows 上配实验环境时一直提示权限问题，想问下有没有可行的解决办法或者推荐的虚拟机配置。',
      tags: ['操作系统', '实验'],
      authorId: 'seed-102',
      authorName: '何同学',
      createdAt: shiftDays(2),
      views: 61,
      likes: 12,
      replies: 0,
      lastReplyAt: shiftDays(1),
      views7d: 23,
      likes7d: 6,
      replies7d: 0,
    },
    {
      type: '求资料',
      title: '求数据库系统期中复习提纲或往年题',
      content: '老师这学期讲得比较快，想找一份数据库系统期中或期末的复习提纲，往年题也可以。',
      tags: ['数据库', '复习资料'],
      authorId: 'seed-103',
      authorName: '孙同学',
      createdAt: shiftDays(3),
      views: 57,
      likes: 7,
      replies: 0,
      lastReplyAt: shiftDays(2),
      views7d: 21,
      likes7d: 3,
      replies7d: 0,
    },
  ]

  return seeds.map((item, index) => ({
    id: index + 1,
    ...item,
    heat7d: calculateDiscussionHeat(item),
  }))
}

const persistMaterials = () => {
  saveJson(KNOWLEDGE_STORAGE_KEYS.MATERIALS, materials.value)
  saveValue(KNOWLEDGE_STORAGE_KEYS.NEXT_MATERIAL_ID, nextMaterialId.value)
}

const persistDiscussions = () => {
  saveJson(KNOWLEDGE_STORAGE_KEYS.DISCUSSIONS, discussions.value)
  saveValue(KNOWLEDGE_STORAGE_KEYS.NEXT_DISCUSSION_ID, nextDiscussionId.value)
}

const persistComments = () => {
  saveJson(KNOWLEDGE_STORAGE_KEYS.COMMENTS, comments.value)
  saveValue(KNOWLEDGE_STORAGE_KEYS.NEXT_COMMENT_ID, nextCommentId.value)
}

const persistPoints = () => saveJson(KNOWLEDGE_STORAGE_KEYS.POINTS_BALANCE, pointsByUser.value)
const persistCheckins = () => saveJson(KNOWLEDGE_STORAGE_KEYS.CHECKINS, checkins.value)
const persistLikes = () => saveJson(KNOWLEDGE_STORAGE_KEYS.LIKES, likes.value)
const persistFavorites = () => saveJson(KNOWLEDGE_STORAGE_KEYS.FAVORITES, favorites.value)
const persistEntitlements = () => saveJson(KNOWLEDGE_STORAGE_KEYS.ENTITLEMENTS, entitlements.value)
const persistViewsDaily = () => saveJson(KNOWLEDGE_STORAGE_KEYS.VIEWS_DAILY, viewsDaily.value)
const persistDownloadsDaily = () => saveJson(KNOWLEDGE_STORAGE_KEYS.DOWNLOADS_DAILY, downloadsDaily.value)

const normalizeUser = (user) => {
  if (!user?.isLoggedIn) {
    return null
  }

  const id = user.id || user.email || user.name
  if (!id) {
    return null
  }

  const normalized = {
    id: String(id),
    name: user.name || '星河用户',
    isLoggedIn: true,
  }

  saveJson(KNOWLEDGE_STORAGE_KEYS.USER, normalized)
  return normalized
}

const getUserTrackerKey = (user) => {
  const normalized = normalizeUser(user)
  if (normalized) {
    return `user:${normalized.id}`
  }

  return `guest:${ensureGuestId()}`
}

const getPoints = (user) => {
  const normalized = normalizeUser(user)
  if (!normalized) {
    return 0
  }

  return pointsByUser.value[normalized.id] || 0
}

const setUserPoints = (userId, points) => {
  pointsByUser.value = {
    ...pointsByUser.value,
    [userId]: points,
  }
  persistPoints()
}

const awardPoints = (user, amount) => {
  const normalized = normalizeUser(user)
  if (!normalized) {
    return null
  }

  const current = pointsByUser.value[normalized.id] || 0
  const next = Math.min(POINTS_MAX, current + amount)
  setUserPoints(normalized.id, next)
  return {
    current,
    next,
    capped: current + amount > POINTS_MAX,
  }
}

const deductPoints = (user, amount) => {
  const normalized = normalizeUser(user)
  if (!normalized) {
    return null
  }

  const current = pointsByUser.value[normalized.id] || 0
  const next = Math.max(0, current - amount)
  setUserPoints(normalized.id, next)
  return { current, next }
}

const rebuildMaterialHeat = (material) => {
  material.heat7d = calculateMaterialHeat(material)
  return material
}

const rebuildDiscussionHeat = (discussion) => {
  discussion.heat7d = calculateDiscussionHeat(discussion)
  return discussion
}

const sortByNewest = (list) =>
  [...list].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())

const sortByDiscussionHeat = (list) =>
  [...list].sort((a, b) => {
    if ((b.heat7d || 0) !== (a.heat7d || 0)) {
      return (b.heat7d || 0) - (a.heat7d || 0)
    }
    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  })

const splitTags = (raw) => {
  if (!raw) {
    return []
  }

  return raw
    .split(/[，,]/)
    .map((tag) => tag.trim())
    .filter(Boolean)
}

const getMaterialRemovalKey = (material) =>
  `${trimText(material?.title)}::${trimText(material?.description)}`

const isRemovedTestMaterial = (material) =>
  REMOVED_TEST_MATERIALS.has(getMaterialRemovalKey(material))

const cleanupRemovedTestMaterials = () => {
  const removedMaterialIds = new Set(
    materials.value
      .filter((item) => isRemovedTestMaterial(item))
      .map((item) => Number(item.id)),
  )

  if (!removedMaterialIds.size) {
    return false
  }

  materials.value = materials.value.filter((item) => !removedMaterialIds.has(Number(item.id)))
  likes.value = likes.value.filter(
    (entry) => !(entry.targetType === 'material' && removedMaterialIds.has(Number(entry.targetId))),
  )
  favorites.value = favorites.value.filter((entry) => !removedMaterialIds.has(Number(entry.materialId)))
  entitlements.value = entitlements.value.filter((entry) => !removedMaterialIds.has(Number(entry.materialId)))
  comments.value = comments.value.filter(
    (item) => !(item.targetType === 'material' && removedMaterialIds.has(Number(item.targetId))),
  )

  return true
}

const addPositiveId = (ids, value) => {
  const id = Number(value)
  if (Number.isFinite(id) && id > 0) {
    ids.add(id)
  }
}

const collectReservedMaterialIds = () => {
  const ids = new Set()

  materials.value.forEach((item) => addPositiveId(ids, item.id))
  comments.value
    .filter((item) => item.targetType === 'material')
    .forEach((item) => addPositiveId(ids, item.targetId))
  likes.value
    .filter((entry) => entry.targetType === 'material')
    .forEach((entry) => addPositiveId(ids, entry.targetId))
  favorites.value.forEach((entry) => addPositiveId(ids, entry.materialId))
  entitlements.value.forEach((entry) => addPositiveId(ids, entry.materialId))

  return ids
}

const nextAvailableMaterialId = (startAt, reservedIds) => {
  let nextId = Math.max(1, Number(startAt) || 1)
  while (reservedIds.has(nextId)) {
    nextId += 1
  }
  reservedIds.add(nextId)
  return nextId
}

const cleanupMaterialCommentArtifacts = (seedMaterials) => {
  const materialIds = new Set(materials.value.map((item) => Number(item.id)))
  const seedTitles = new Set(seedMaterials.map((item) => item.title))
  const seedMaterialIds = new Set(
    materials.value
      .filter((item) => seedTitles.has(item.title))
      .map((item) => Number(item.id)),
  )
  const removedCommentIds = new Set()

  comments.value.forEach((item) => {
    if (item.targetType !== 'material') {
      return
    }

    const targetId = Number(item.targetId)
    if (!materialIds.has(targetId) || (item.isDeleted && seedMaterialIds.has(targetId))) {
      addPositiveId(removedCommentIds, item.id)
    }
  })

  let changed = true
  while (changed) {
    changed = false
    comments.value.forEach((item) => {
      if (item.parentId !== null && removedCommentIds.has(Number(item.parentId)) && !removedCommentIds.has(Number(item.id))) {
        addPositiveId(removedCommentIds, item.id)
        changed = true
      }
    })
  }

  if (!removedCommentIds.size) {
    return false
  }

  comments.value = comments.value.filter((item) => !removedCommentIds.has(Number(item.id)))
  return true
}

const validateTags = (tags) => {
  if (tags.length > 5) {
    return '标签最多填写 5 个'
  }

  const invalid = tags.find((tag) => tag.length < 1 || tag.length > 10)
  if (invalid) {
    return '每个标签需控制在 1-10 个字'
  }

  return ''
}

const trimText = (value) => value?.trim() || ''

const detectFileType = (file) => {
  const name = file?.name?.toLowerCase() || ''
  const mime = file?.type?.toLowerCase() || ''

  if (mime.includes('pdf') || name.endsWith('.pdf')) return 'PDF'
  if (mime.includes('word') || name.endsWith('.doc') || name.endsWith('.docx')) return 'Word'
  if (mime.includes('presentation') || name.endsWith('.ppt') || name.endsWith('.pptx')) return 'PPT'
  if (mime.includes('sheet') || name.endsWith('.xls') || name.endsWith('.xlsx')) return 'Excel'
  if (mime.startsWith('image/') || /\.(png|jpg|jpeg|gif|webp)$/i.test(name)) return '图片'
  if (mime.includes('zip') || /\.(zip|rar|7z)$/i.test(name)) return 'ZIP'
  return '其他'
}

const isSupportedUploadType = (fileType) =>
  ['PDF', 'Word', 'PPT', 'Excel', '图片', 'ZIP', '其他'].includes(fileType)

const createPreviewUrl = (file, fileType) => {
  if (!file) {
    return ''
  }

  if (fileType === '图片' || fileType === 'PDF') {
    return URL.createObjectURL(file)
  }

  return ''
}

const safeDownload = (material) => {
  const link = document.createElement('a')
  const defaultName = material.fileName || `${material.title}.txt`

  if (material.downloadUrl) {
    link.href = material.downloadUrl
  } else if (material.previewUrl && material.fileType === '图片') {
    link.href = material.previewUrl
  } else {
    const blob = new Blob(
      [
        `知识星河模拟下载\n\n标题：${material.title}\n分类：${material.category}\n说明：${material.description}\n上传者：${material.authorName}`,
      ],
      { type: 'text/plain;charset=utf-8' },
    )
    link.href = URL.createObjectURL(blob)
  }

  link.download = defaultName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const hasLikeRecord = (targetType, targetId, userId) =>
  likes.value.some((entry) => entry.targetType === targetType && entry.targetId === targetId && entry.userId === userId)

const hasFavoriteRecord = (materialId, userId) =>
  favorites.value.some((entry) => entry.materialId === materialId && entry.userId === userId)

const hasEntitlement = (materialId, userId) =>
  entitlements.value.some((entry) => entry.materialId === materialId && entry.userId === userId)

const updateMaterial = (materialId, updater) => {
  const nextList = materials.value.map((item) => {
    if (item.id !== materialId) {
      return item
    }

    return updater({ ...item })
  })
  materials.value = nextList
  persistMaterials()
  return materials.value.find((item) => item.id === materialId) || null
}

const updateDiscussion = (discussionId, updater) => {
  const nextList = discussions.value.map((item) => {
    if (item.id !== discussionId) {
      return item
    }

    return updater({ ...item })
  })
  discussions.value = nextList
  persistDiscussions()
  return discussions.value.find((item) => item.id === discussionId) || null
}

const updateComment = (commentId, updater) => {
  comments.value = comments.value.map((item) => {
    if (item.id !== commentId) {
      return item
    }
    return updater({ ...item })
  })
  persistComments()
  return comments.value.find((item) => item.id === commentId) || null
}

const recordDailyAction = (recordsRef, persist, payload) => {
  const exists = recordsRef.value.some(
    (entry) =>
      (entry.targetType || entry.scope) === payload.targetType &&
      entry.targetId === payload.targetId &&
      (entry.userId || entry.userKey) === payload.userId &&
      entry.date === payload.date,
  )

  if (exists) {
    return false
  }

  recordsRef.value = [...recordsRef.value, payload]
  persist()
  return true
}

const ensureKnowledgeState = () => {
  if (initialized || typeof window === 'undefined') {
    return
  }

  ensureGuestId()

  const seedMaterials = createSeedMaterials()
  materials.value = loadJson(KNOWLEDGE_STORAGE_KEYS.MATERIALS, seedMaterials)
  discussions.value = loadJson(KNOWLEDGE_STORAGE_KEYS.DISCUSSIONS, createSeedDiscussions())
  comments.value = loadJson(KNOWLEDGE_STORAGE_KEYS.COMMENTS, [])
  pointsByUser.value = loadJson(KNOWLEDGE_STORAGE_KEYS.POINTS_BALANCE, {})
  checkins.value = loadJson(KNOWLEDGE_STORAGE_KEYS.CHECKINS, [])
  likes.value = loadJson(KNOWLEDGE_STORAGE_KEYS.LIKES, [])
  favorites.value = loadJson(KNOWLEDGE_STORAGE_KEYS.FAVORITES, [])
  entitlements.value = loadJson(KNOWLEDGE_STORAGE_KEYS.ENTITLEMENTS, [])
  viewsDaily.value = loadJson(KNOWLEDGE_STORAGE_KEYS.VIEWS_DAILY, [])
  downloadsDaily.value = loadJson(KNOWLEDGE_STORAGE_KEYS.DOWNLOADS_DAILY, [])
  const materialTitles = new Set(materials.value.map((item) => item.title))
  const reservedMaterialIds = collectReservedMaterialIds()
  let nextSeedId = Math.max(
    Number(localStorage.getItem(KNOWLEDGE_STORAGE_KEYS.NEXT_MATERIAL_ID) || 0),
    Math.max(0, ...reservedMaterialIds) + 1,
  )
  seedMaterials.forEach((item) => {
    if (materialTitles.has(item.title)) return
    nextSeedId = nextAvailableMaterialId(nextSeedId, reservedMaterialIds)
    materials.value.push({ ...item, id: nextSeedId })
    materialTitles.add(item.title)
    nextSeedId += 1
  })
  const didCleanupMaterials = cleanupRemovedTestMaterials()
  const didCleanupComments = cleanupMaterialCommentArtifacts(seedMaterials)
  const finalReservedMaterialIds = collectReservedMaterialIds()
  nextMaterialId.value = Math.max(
    Number(localStorage.getItem(KNOWLEDGE_STORAGE_KEYS.NEXT_MATERIAL_ID) || 0),
    Math.max(0, ...finalReservedMaterialIds) + 1,
  )
  nextDiscussionId.value = Number(
    localStorage.getItem(KNOWLEDGE_STORAGE_KEYS.NEXT_DISCUSSION_ID) || discussions.value.length + 1,
  )
  nextCommentId.value = Number(localStorage.getItem(KNOWLEDGE_STORAGE_KEYS.NEXT_COMMENT_ID) || 1)

  persistMaterials()
  persistDiscussions()
  persistComments()
  if (didCleanupMaterials || didCleanupComments) {
    persistLikes()
    persistFavorites()
    persistEntitlements()
  }
  initialized = true
}

const createMaterial = async (payload, user, options = {}) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能上传资料' }
  }

  const title = trimText(payload.title)
  const category = trimText(payload.category)
  const course = trimText(payload.course)
  const description = trimText(payload.description)
  const file = payload.file
  const tags = splitTags(payload.tags)
  const tagsError = validateTags(tags)

  if (!title || title.length > 50) {
    return { ok: false, code: 'validation_error', message: '资料标题需填写 1-50 个字' }
  }

  if (!MATERIAL_CATEGORIES.includes(category) || category === '全部') {
    return { ok: false, code: 'validation_error', message: '请选择资料分类' }
  }

  if (!description || description.length > 500) {
    return { ok: false, code: 'validation_error', message: '资料描述需填写 1-500 个字' }
  }

  if (!file) {
    return { ok: false, code: 'validation_error', message: '请上传资料文件' }
  }

  const fileType = detectFileType(file)
  if (!isSupportedUploadType(fileType)) {
    return { ok: false, code: 'validation_error', message: '文件类型不在支持范围内' }
  }

  if (file.size > 50 * 1024 * 1024) {
    return { ok: false, code: 'validation_error', message: '文件大小不能超过 50MB' }
  }

  if (tagsError) {
    return { ok: false, code: 'validation_error', message: tagsError }
  }

  const pricePoints = DEFAULT_PRICE_OPTIONS.includes(Number(payload.pricePoints)) ? Number(payload.pricePoints) : 0
  if (options.validateOnly) {
    return { ok: true, pricePoints }
  }

  const material = rebuildMaterialHeat({
    id: nextMaterialId.value,
    backendId: Number(options.backendId || 0) || null,
    title,
    category,
    course,
    description,
    fileName: file.name,
    fileType,
    fileSize: file.size,
    previewUrl: createPreviewUrl(file, fileType),
    downloadUrl: '',
    pricePoints,
    tags,
    authorId: normalized.id,
    authorName: normalized.name,
    createdAt: startOfNow(),
    views: 0,
    downloads: 0,
    likes: 0,
    favorites: 0,
    views7d: 0,
    downloads7d: 0,
    likes7d: 0,
    replies7d: 0,
  })

  materials.value = [material, ...materials.value]
  nextMaterialId.value += 1
  persistMaterials()

  const reward = options.skipPointAward ? null : awardPoints(user, UPLOAD_REWARD)
  const pointsMessage = reward?.capped
    ? `上传成功，本次积分+${UPLOAD_REWARD}，但当前积分已达上限 ${POINTS_MAX}`
    : `上传成功，积分+${UPLOAD_REWARD}，当前积分 ${reward?.next || 0}/${POINTS_MAX}`

  return {
    ok: true,
    material,
    message: options.message || pointsMessage,
    points: options.points ?? reward?.next ?? 0,
  }
}

const createDiscussion = (payload, user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能发讨论' }
  }

  const type = trimText(payload.type)
  const title = trimText(payload.title)
  const content = trimText(payload.content)
  const tags = splitTags(payload.tags)
  const tagsError = validateTags(tags)

  if (!DISCUSSION_TYPES.includes(type) || type === '全部') {
    return { ok: false, code: 'validation_error', message: '请选择讨论类型' }
  }

  if (!title) {
    return { ok: false, code: 'validation_error', message: '请输入讨论标题' }
  }

  if (title.length > 50) {
    return { ok: false, code: 'validation_error', message: '标题不能超过 50 字' }
  }

  if (!content) {
    return { ok: false, code: 'validation_error', message: '请输入正文内容' }
  }

  if (content.length > 1000) {
    return { ok: false, code: 'validation_error', message: '正文不能超过 1000 字' }
  }

  if (tagsError) {
    return {
      ok: false,
      code: 'validation_error',
      message: tags.length > 5 ? '最多添加 5 个标签' : '单个标签不能超过 10 字',
    }
  }

  const discussion = rebuildDiscussionHeat({
    id: nextDiscussionId.value,
    type,
    title,
    content,
    tags,
    authorId: normalized.id,
    authorName: normalized.name,
    createdAt: startOfNow(),
    views: 0,
    likes: 0,
    replies: 0,
    lastReplyAt: null,
    views7d: 0,
    likes7d: 0,
    replies7d: 0,
  })

  discussions.value = [discussion, ...discussions.value]
  nextDiscussionId.value += 1
  persistDiscussions()

  return {
    ok: true,
    discussion,
    message: '发布成功。',
  }
}

const toggleMaterialLike = (materialId, user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能点赞' }
  }

  const liked = hasLikeRecord('material', materialId, normalized.id)

  if (liked) {
    likes.value = likes.value.filter(
      (entry) => !(entry.targetType === 'material' && entry.targetId === materialId && entry.userId === normalized.id),
    )
  } else {
    likes.value = [...likes.value, { targetType: 'material', targetId: materialId, userId: normalized.id }]
  }
  persistLikes()

  const material = updateMaterial(materialId, (item) => {
    item.likes = Math.max(0, (item.likes || 0) + (liked ? -1 : 1))
    item.likes7d = Math.max(0, (item.likes7d || 0) + (liked ? -1 : 1))
    return rebuildMaterialHeat(item)
  })

  return { ok: true, liked: !liked, material }
}

const toggleDiscussionLike = (discussionId, user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能点赞' }
  }

  const liked = hasLikeRecord('discussion', discussionId, normalized.id)

  if (liked) {
    likes.value = likes.value.filter(
      (entry) => !(entry.targetType === 'discussion' && entry.targetId === discussionId && entry.userId === normalized.id),
    )
  } else {
    likes.value = [...likes.value, { targetType: 'discussion', targetId: discussionId, userId: normalized.id }]
  }
  persistLikes()

  const discussion = updateDiscussion(discussionId, (item) => {
    item.likes = Math.max(0, (item.likes || 0) + (liked ? -1 : 1))
    item.likes7d = Math.max(0, (item.likes7d || 0) + (liked ? -1 : 1))
    return rebuildDiscussionHeat(item)
  })

  return { ok: true, liked: !liked, discussion }
}

const toggleMaterialFavorite = (materialId, user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能收藏' }
  }

  const favorited = hasFavoriteRecord(materialId, normalized.id)

  if (favorited) {
    favorites.value = favorites.value.filter(
      (entry) => !(entry.materialId === materialId && entry.userId === normalized.id),
    )
  } else {
    favorites.value = [...favorites.value, { materialId, userId: normalized.id }]
  }
  persistFavorites()

  const material = updateMaterial(materialId, (item) => {
    item.favorites = Math.max(0, (item.favorites || 0) + (favorited ? -1 : 1))
    return item
  })

  return { ok: true, favorited: !favorited, material }
}

const recordMaterialView = (materialId, user) => {
  ensureKnowledgeState()

  const didRecord = recordDailyAction(viewsDaily, persistViewsDaily, {
    targetType: 'material',
    targetId: materialId,
    userId: getUserTrackerKey(user),
    date: todayKey(),
  })

  if (!didRecord) {
    return false
  }

  updateMaterial(materialId, (item) => {
    item.views = (item.views || 0) + 1
    item.views7d = (item.views7d || 0) + 1
    return rebuildMaterialHeat(item)
  })
  return true
}

const recordDiscussionView = (discussionId, user) => {
  ensureKnowledgeState()

  const didRecord = recordDailyAction(viewsDaily, persistViewsDaily, {
    targetType: 'discussion',
    targetId: discussionId,
    userId: getUserTrackerKey(user),
    date: todayKey(),
  })

  if (!didRecord) {
    return false
  }

  updateDiscussion(discussionId, (item) => {
    item.views = (item.views || 0) + 1
    item.views7d = (item.views7d || 0) + 1
    return rebuildDiscussionHeat(item)
  })
  return true
}

const executeDownload = (materialId, user, confirmed = false, options = {}) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能下载资料' }
  }

  const material = materials.value.find((item) => item.id === materialId)
  if (!material) {
    return { ok: false, code: 'not_found', message: '资料不存在或已被删除' }
  }

  const alreadyEntitled = hasEntitlement(materialId, normalized.id)
  const pricePoints = material.pricePoints || 0

  if (pricePoints > 0 && !alreadyEntitled && !confirmed) {
    return {
      ok: false,
      code: 'confirm_required',
      title: '确认下载',
      message: `本次下载将消耗 ${pricePoints} 积分，下载后可永久再次下载。`,
    }
  }

  if (pricePoints > 0 && !alreadyEntitled) {
    if (!options.skipPointValidation) {
      const balance = getPoints(user)
      if (balance < pricePoints) {
        return {
          ok: false,
          code: 'insufficient_points',
          shortfall: pricePoints - balance,
        message: `积分不足，还差 ${pricePoints - balance} 分`,
      }
    }

    }

    if (!options.skipPointDeduction) {
      deductPoints(user, pricePoints)
    }
    entitlements.value = [...entitlements.value, { materialId, userId: normalized.id, createdAt: startOfNow() }]
    persistEntitlements()
  }

  safeDownload(material)

  const isUniqueDownload = recordDailyAction(downloadsDaily, persistDownloadsDaily, {
    targetType: 'material',
    targetId: materialId,
    userId: `user:${normalized.id}`,
    date: todayKey(),
  })

  const updatedMaterial = isUniqueDownload
    ? updateMaterial(materialId, (item) => {
        item.downloads = (item.downloads || 0) + 1
        item.downloads7d = (item.downloads7d || 0) + 1
        return rebuildMaterialHeat(item)
      })
    : materials.value.find((item) => item.id === materialId)

  if (pricePoints > 0 && !alreadyEntitled) {
    return {
      ok: true,
      material: updatedMaterial,
      message: `下载成功，已扣除 ${pricePoints} 积分`,
    }
  }

  return {
    ok: true,
    material: updatedMaterial,
    message: '下载成功。',
  }
}

const checkIn = (user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能签到' }
  }

  const today = todayKey()
  const alreadyCheckedIn = checkins.value.some((entry) => entry.userId === normalized.id && entry.date === today)

  if (alreadyCheckedIn) {
    return {
      ok: false,
      code: 'already_checked_in',
      message: '今日已签到',
    }
  }

  checkins.value = [...checkins.value, { userId: normalized.id, date: today }]
  persistCheckins()

  const reward = awardPoints(user, CHECKIN_REWARD)
  return {
    ok: true,
    points: reward?.next || 0,
    message: reward?.capped
      ? `签到成功，积分已达上限 ${POINTS_MAX}，超出部分不计入`
      : `签到成功 +${CHECKIN_REWARD}，当前积分 ${reward?.next || 0}/${POINTS_MAX}`,
  }
}

const isCheckedInToday = (user) => {
  const normalized = normalizeUser(user)
  if (!normalized) {
    return false
  }

  return checkins.value.some((entry) => entry.userId === normalized.id && entry.date === todayKey())
}

const isMaterialLiked = (materialId, user) => {
  const normalized = normalizeUser(user)
  return normalized ? hasLikeRecord('material', materialId, normalized.id) : false
}

const isDiscussionLiked = (discussionId, user) => {
  const normalized = normalizeUser(user)
  return normalized ? hasLikeRecord('discussion', discussionId, normalized.id) : false
}

const isMaterialFavorited = (materialId, user) => {
  const normalized = normalizeUser(user)
  return normalized ? hasFavoriteRecord(materialId, normalized.id) : false
}

const isMaterialEntitled = (materialId, user) => {
  const normalized = normalizeUser(user)
  return normalized ? hasEntitlement(materialId, normalized.id) : false
}

const getDiscussionComments = (discussionId) =>
  comments.value.filter((item) => item.targetType === 'discussion' && item.targetId === Number(discussionId))

const getCommentsByTarget = (targetType, targetId) =>
  comments.value.filter((item) => item.targetType === targetType && item.targetId === Number(targetId))

const getTopLevelComments = (targetType, targetId) =>
  sortByNewest(getCommentsByTarget(targetType, targetId).filter((item) => item.parentId === null))

const getRepliesByParentId = (parentId) =>
  [...comments.value]
    .filter((item) => item.parentId === Number(parentId))
    .sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())

const getCommentById = (commentId) => comments.value.find((item) => item.id === Number(commentId)) || null

const syncDiscussionReplyStats = (discussionId, createdAt = startOfNow()) => {
  updateDiscussion(discussionId, (item) => {
    item.replies = (item.replies || 0) + 1
    item.replies7d = (item.replies7d || 0) + 1
    item.lastReplyAt = createdAt
    item.updatedAt = createdAt
    return rebuildDiscussionHeat(item)
  })
}

const syncMaterialReplyStats = (materialId) => {
  updateMaterial(materialId, (item) => {
    item.replies7d = (item.replies7d || 0) + 1
    return rebuildMaterialHeat(item)
  })
}

const createComment = ({ targetType, targetId, parentId = null, content }, user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能回复' }
  }

  const normalizedContent = trimText(content)
  if (!normalizedContent) {
    return { ok: false, code: 'validation_error', message: '请输入回复内容' }
  }

  if (normalizedContent.length > 500) {
    return { ok: false, code: 'validation_error', message: '回复内容不能超过 500 字' }
  }

  if (!['material', 'discussion'].includes(targetType)) {
    return { ok: false, code: 'validation_error', message: '评论目标无效' }
  }

  let replyParentId = null
  if (parentId !== null) {
    const parentComment = getCommentById(parentId)
    if (!parentComment || parentComment.parentId !== null) {
      return { ok: false, code: 'validation_error', message: '只能回复顶层评论' }
    }

    if (parentComment.isDeleted) {
      return { ok: false, code: 'validation_error', message: '该评论已删除，不能继续回复' }
    }

    replyParentId = parentComment.id
  }

  const createdAt = startOfNow()
  const comment = {
    id: nextCommentId.value,
    backendId: null,
    targetType,
    targetId: Number(targetId),
    parentId: replyParentId,
    authorId: normalized.id,
    authorName: normalized.name,
    content: normalizedContent,
    createdAt,
    isDeleted: false,
  }

  comments.value = [...comments.value, comment]
  nextCommentId.value += 1
  persistComments()

  if (targetType === 'discussion') {
    syncDiscussionReplyStats(Number(targetId), createdAt)
  } else {
    syncMaterialReplyStats(Number(targetId))
  }

  return {
    ok: true,
    comment,
    message: '回复成功',
  }
}

const bindCommentBackendId = (commentId, backendId, parentBackendId = null) => {
  if (!backendId) {
    return null
  }

  return updateComment(commentId, (item) => ({
    ...item,
    backendId: Number(backendId),
    parentBackendId: parentBackendId ? Number(parentBackendId) : item.parentBackendId || null,
  }))
}

const deleteComment = (commentId, user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: '登录后才能删除回复' }
  }

  const comment = getCommentById(commentId)
  if (!comment) {
    return { ok: false, code: 'not_found', message: '评论不存在' }
  }

  if (comment.authorId !== normalized.id) {
    return { ok: false, code: 'forbidden', message: '只能删除自己的评论或回复' }
  }

  if (comment.isDeleted) {
    return { ok: false, code: 'already_deleted', message: '该评论已删除' }
  }

  const updated = updateComment(commentId, (item) => ({
    ...item,
    isDeleted: true,
  }))

  return {
    ok: true,
    comment: updated,
    message: '已删除',
  }
}

const deleteMaterial = (materialId, user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: 'Please log in before deleting materials.' }
  }

  const targetId = Number(materialId)
  const material = materials.value.find((item) => Number(item.id) === targetId)
  if (!material) {
    return { ok: false, code: 'not_found', message: 'Material was not found.' }
  }

  if (String(material.authorId) !== normalized.id) {
    return { ok: false, code: 'forbidden', message: 'You can only delete materials you uploaded.' }
  }

  materials.value = materials.value.filter((item) => Number(item.id) !== targetId)
  likes.value = likes.value.filter((entry) => !(entry.targetType === 'material' && Number(entry.targetId) === targetId))
  favorites.value = favorites.value.filter((entry) => Number(entry.materialId) !== targetId)
  entitlements.value = entitlements.value.filter((entry) => Number(entry.materialId) !== targetId)
  comments.value = comments.value.map((item) =>
    item.targetType === 'material' && Number(item.targetId) === targetId ? { ...item, isDeleted: true } : item,
  )
  persistMaterials()
  persistLikes()
  persistFavorites()
  persistEntitlements()
  persistComments()

  return { ok: true, material, message: 'Material deleted.' }
}

const deleteDiscussion = (discussionId, user) => {
  ensureKnowledgeState()

  const normalized = normalizeUser(user)
  if (!normalized) {
    return { ok: false, code: 'login_required', message: 'Please log in before deleting discussions.' }
  }

  const targetId = Number(discussionId)
  const discussion = discussions.value.find((item) => Number(item.id) === targetId)
  if (!discussion) {
    return { ok: false, code: 'not_found', message: 'Discussion was not found.' }
  }

  if (String(discussion.authorId) !== normalized.id) {
    return { ok: false, code: 'forbidden', message: 'You can only delete discussions you created.' }
  }

  discussions.value = discussions.value.filter((item) => Number(item.id) !== targetId)
  likes.value = likes.value.filter((entry) => !(entry.targetType === 'discussion' && Number(entry.targetId) === targetId))
  comments.value = comments.value.map((item) =>
    item.targetType === 'discussion' && Number(item.targetId) === targetId ? { ...item, isDeleted: true } : item,
  )
  persistDiscussions()
  persistLikes()
  persistComments()

  return { ok: true, discussion, message: 'Discussion deleted.' }
}

const getMaterialById = (materialId) => materials.value.find((item) => item.id === Number(materialId)) || null
const getDiscussionById = (discussionId) => discussions.value.find((item) => item.id === Number(discussionId)) || null

const formatDateTime = (value) => {
  if (!value) {
    return '--'
  }

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

const formatRelativeTime = (value) => {
  if (!value) {
    return '--'
  }

  const diff = Date.now() - new Date(value).getTime()
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour

  if (diff < hour) {
    const count = Math.max(1, Math.floor(diff / minute))
    return `${count} 分钟前`
  }

  if (diff < day) {
    return `${Math.floor(diff / hour)} 小时前`
  }

  if (diff < 7 * day) {
    return `${Math.floor(diff / day)} 天前`
  }

  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
  }).format(new Date(value))
}

const formatPrice = (pricePoints) => (pricePoints > 0 ? `${pricePoints}积分` : '免费')

const formatFileSize = (size) => {
  if (!size) {
    return '--'
  }

  if (size >= 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(1)} MB`
  }

  if (size >= 1024) {
    return `${Math.round(size / 1024)} KB`
  }

  return `${size} B`
}

const getDownloadButtonMeta = (material, user) => {
  if (!material) {
    return { text: '下载', tone: 'free' }
  }

  if (material.pricePoints === 0) {
    return { text: '立即下载', tone: 'free' }
  }

  if (isMaterialEntitled(material.id, user)) {
    return { text: '再次下载', tone: 'owned' }
  }

  const loggedIn = Boolean(normalizeUser(user))
  if (loggedIn && getPoints(user) < material.pricePoints) {
    return { text: `下载（需 ${material.pricePoints} 积分）`, tone: 'insufficient' }
  }

  return { text: `下载（需 ${material.pricePoints} 积分）`, tone: 'points' }
}

export const useKnowledgeGalaxy = () => {
  ensureKnowledgeState()

  const stats = computed(() => {
    const contributorSet = new Set(materials.value.map((item) => item.authorId))
    return {
      materialCount: materials.value.length,
      contributorCount: contributorSet.size,
      totalDownloads: materials.value.reduce((sum, item) => sum + (item.downloads || 0), 0),
      discussionCount: discussions.value.length,
    }
  })

  const rankingMaterials = computed(() => [...materials.value].sort((a, b) => b.heat7d - a.heat7d).slice(0, 5))
  const downloadMaterials = computed(() => [...materials.value].sort((a, b) => b.downloads - a.downloads).slice(0, 5))
  const rankingDiscussions = computed(() => sortByDiscussionHeat(discussions.value).slice(0, 5))
  const sortedDiscussions = computed(() => sortByDiscussionHeat(discussions.value))

  const filterDiscussions = ({ type = '全部', keyword = '', sort = '最新发布' } = {}) => {
    const loweredKeyword = trimText(keyword).toLowerCase()
    let list = [...discussions.value]

    if (type !== '全部') {
      list = list.filter((item) => item.type === type)
    }

    if (loweredKeyword) {
      list = list.filter((item) => {
        const haystack = [item.title, item.content, ...(item.tags || [])].join(' ').toLowerCase()
        return haystack.includes(loweredKeyword)
      })
    }

    return sort === '热度近7天' ? sortByDiscussionHeat(list) : sortByNewest(list)
  }

  return {
    materials,
    discussions,
    comments,
    stats,
    rankingMaterials,
    downloadMaterials,
    rankingDiscussions,
    sortedDiscussions,
    getPoints,
    isCheckedInToday,
    createMaterial,
    createDiscussion,
    createComment,
    bindCommentBackendId,
    deleteComment,
    deleteMaterial,
    deleteDiscussion,
    toggleMaterialLike,
    toggleDiscussionLike,
    toggleMaterialFavorite,
    recordMaterialView,
    recordDiscussionView,
    executeDownload,
    checkIn,
    isMaterialLiked,
    isDiscussionLiked,
    isMaterialFavorited,
    isMaterialEntitled,
    getMaterialById,
    getDiscussionById,
    getCommentsByTarget,
    getTopLevelComments,
    getRepliesByParentId,
    getCommentById,
    getDownloadButtonMeta,
    filterDiscussions,
    formatDateTime,
    formatRelativeTime,
    formatPrice,
    formatFileSize,
    splitTags,
    POINTS_MAX,
  }
}
