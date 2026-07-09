const CREDIT_LABELS = [
  [90, '极好'],
  [80, '良好'],
  [70, '一般'],
  [60, '较差'],
]

export const normalizeCreditScore = (value, fallback = 100) => {
  const score = Number(value)
  if (!Number.isFinite(score)) return fallback
  return Math.min(100, Math.max(0, Math.round(score)))
}

export const getCreditLabel = (value) => {
  const score = normalizeCreditScore(value, 100)
  for (const [threshold, label] of CREDIT_LABELS) {
    if (score >= threshold) return label
  }
  return '很差'
}
