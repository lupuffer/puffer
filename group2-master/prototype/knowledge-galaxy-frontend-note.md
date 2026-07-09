# 知识星河前后端对接说明

知识星河这一块现在已经不再只是前端 `localStorage` 演示，核心的“我的数据”和用户动作都已经接入后端数据库。

## 已接入的数据库表

- `knowledge_materials`
  资料表，包含标签、积分价格、浏览量、点赞量等字段
- `knowledge_discussions`
  讨论表
- `knowledge_comments`
  评论表
- `knowledge_material_favorites`
  资料收藏表
- `knowledge_material_entitlements`
  资料兑换 / 下载权益表
- `knowledge_material_likes`
  资料点赞表
- `knowledge_discussion_likes`
  讨论点赞表
- `knowledge_checkins`
  每日签到表
- `knowledge_point_ledger`
  积分账本表，记录加分/扣分明细和余额
- `knowledge_ranks`
  排行榜表

## 已接通的后端接口

- `GET /api/knowledge/materials`
  获取资料列表，支持分页和筛选
- `POST /api/knowledge/materials`
  创建资料，并发放上传积分奖励
- `POST /api/knowledge/materials/:id/download`
  记录资料下载 / 兑换权益，并处理积分扣减
- `POST /api/knowledge/materials/:id/favorite`
  收藏或取消收藏资料
- `POST /api/knowledge/materials/:id/like`
  点赞或取消点赞资料
- `GET /api/knowledge/discussions`
  获取讨论列表，支持分页和筛选
- `POST /api/knowledge/discussions`
  创建讨论
- `POST /api/knowledge/discussions/:id/like`
  点赞或取消点赞讨论
- `POST /api/knowledge/comments`
  创建评论 / 回复
- `DELETE /api/knowledge/comments/:id`
  删除自己的评论 / 回复
- `GET /api/knowledge/points`
  获取当前积分余额、是否已签到、最近积分账本
- `POST /api/knowledge/checkin`
  每日签到并发放积分
- `GET /api/knowledge/ranks`
  获取知识星河排行榜
- `GET /api/knowledge/me/overview`
  获取我的贡献统计、积分余额、今日签到状态
- `GET /api/knowledge/me/uploads`
  获取我的上传
- `GET /api/knowledge/me/discussions`
  获取我的讨论
- `GET /api/knowledge/me/favorites`
  获取我的收藏
- `GET /api/knowledge/me/redeems`
  获取我的兑换 / 已拥有资料

## 当前已完成的同步动作

- 上传资料：
  先写入当前页面，再同步到后端资料表
- 发布讨论：
  先写入当前页面，再同步到后端讨论表
- 资料点赞 / 取消点赞：
  当前页状态和后端点赞表同步
- 讨论点赞 / 取消点赞：
  当前页状态和后端点赞表同步
- 收藏 / 取消收藏：
  当前页状态和后端收藏表同步
- 资料下载 / 兑换：
  当前页状态和后端权益表、积分账本同步
- 新增评论：
  当前页状态和后端评论表同步
- 删除评论：
  当前页状态和后端评论删除接口同步
- 每日签到：
  当前页状态和后端签到表、积分账本同步
- “我的上传 / 我的讨论 / 我的收藏 / 我的兑换”：
  已改为优先读取后端真实记录

## 自动补同步策略

- 登录后会自动检查当前浏览器里的本地上传、讨论、收藏、兑换记录。
- 如果这些记录此前只存在于本地，会自动尝试补写到后端数据库。
- 收藏和兑换会先按资料内容匹配到后端真实资料，再执行后端同步。
- 评论同步时会记录后端 `commentId`，方便后续删除评论时准确删除后端记录。

## 目前仍需注意

- 如果后端服务正在重载、返回空响应，或某条记录在本地与后端之间无法匹配，前端会先保留本地成功状态，并提示“后端同步稍后重试”。
- 积分账本接口已经接上，但当前页面还没有单独做一个完整的“积分明细”可视化面板；如果后续要展示最近签到、上传奖励、下载扣分流水，可以直接基于 `GET /api/knowledge/points` 增加前端卡片或弹层。
