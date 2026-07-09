import { getKnowledgeDiscussions, getKnowledgeMaterials, getMyKnowledgeUploads } from '@/services/api'

export const makeMaterialSignature = (item = {}) =>
  [
    String(item.title || '').trim(),
    String(item.course || item.courseName || '').trim(),
    String(item.category || '').trim(),
    String(item.description || '').trim(),
  ].join('::')

export const makeDiscussionSignature = (item = {}) =>
  [
    String(item.title || '').trim(),
    String(item.type || '').trim(),
    String(item.content || '').trim(),
  ].join('::')

export async function fetchAllPages(loader, params = {}) {
  const allItems = []
  let page = 1
  let totalPages = 1

  while (page <= totalPages) {
    const response = await loader({
      ...params,
      page,
      page_size: 50,
    })
    const data = response?.data || {}
    allItems.push(...(data.items || []))
    totalPages = Math.max(1, Number(data.totalPages || 1))
    page += 1
  }

  return allItems
}

export async function resolveBackendMaterialByRecord(material, options = {}) {
  if (!material) {
    return null
  }

  const backendId = Number(material.backendId || 0)
  if (backendId) {
    return { ...material, id: backendId }
  }

  const loader = options.mineOnly ? getMyKnowledgeUploads : getKnowledgeMaterials
  const materials = await fetchAllPages(loader)
  const signature = makeMaterialSignature(material)
  return materials.find((item) => makeMaterialSignature(item) === signature) || null
}

export async function resolveBackendDiscussionByRecord(discussion) {
  if (!discussion) {
    return null
  }

  const discussions = await fetchAllPages(getKnowledgeDiscussions)
  const signature = makeDiscussionSignature(discussion)
  return discussions.find((item) => makeDiscussionSignature(item) === signature) || null
}
