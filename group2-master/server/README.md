# SeekBook Flask 后端

二手书交易平台的 Flask 后端服务，使用 SQLite 数据库存储数据。

## 项目结构

```
server/
├── app.py              # Flask 应用主文件
├── config.py           # 配置文件
├── models/             # 数据库模型包
├── init_data.py        # 初始化数据
├── run.py              # 启动脚本
├── requirements.txt    # 依赖包
└── uploads/            # 上传文件目录（自动生成）
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动服务

```bash
python run.py
```

服务将在 http://localhost:5000 启动

## API 接口列表

### 用户相关
- `GET /api/user/current` - 获取当前用户信息
- `GET /api/user/stats` - 获取收益、交易和当前信誉分项
- `GET /api/user/credit-audits` - 获取最近 50 条信誉计算审计日志

### 书籍相关
- `GET /api/books` - 获取书籍列表（支持搜索、筛选、分页）
- `GET /api/books/<id>` - 获取书籍详情
- `POST /api/books` - 发布新书籍
- `PUT /api/books/<id>` - 更新书籍信息
- `DELETE /api/books/<id>` - 下架书籍
- `GET /api/books/my` - 获取我发布的书籍

### 收藏相关
- `GET /api/favorites` - 获取收藏列表
- `POST /api/favorites` - 添加收藏
- `DELETE /api/favorites/<book_id>` - 取消收藏
- `GET /api/favorites/<book_id>/check` - 检查是否已收藏

### 聊天相关
- `GET /api/chat/sessions` - 获取聊天会话列表
- `POST /api/chat/sessions` - 创建聊天会话
- `GET /api/chat/sessions/<id>/messages` - 获取会话消息
- `POST /api/chat/messages` - 发送消息

### 订单相关
- `GET /api/orders` - 获取订单列表
- `POST /api/orders` - 创建订单
- `GET /api/orders/<id>` - 获取订单详情
- `PUT /api/orders/<id>/status` - 更新订单状态
- `POST /api/orders/<id>/rate` - 对已完成订单评价；同一用户不可重复评价

```text
信誉总分 = 买家评价星级 × 70% + 近30天响应时效 × 30%
```

- 评分分只使用买家给卖家的 1–5 星评价，并先按 `平均星级 ÷ 5 × 100` 计算原始分。
- 为了避免前几笔订单波动过大，买家评分会做低样本平滑：`(原始评分 × 评价数 + 100 × 5) ÷ (评价数 + 5)`。
- 响应时效使用近 30 天首次回复时间的中位数，至少 3 次有效回复后参与计分。
- 无有效样本的分项按 100 分中性起步，并在审计快照中标记样本不足。
- 当前版本暂不对取消行为自动判责，因此取消订单不纳入信誉扣分，避免误伤正常协商取消场景。
- 每次订单完成、订单取消、有效回复或买家评价都会写入 `credit_audits`；审计快照会同时保留原始评分和平滑后评分。取消只留痕，不扣分。


### 数据相关
- `GET /api/data/catalog` - 获取书籍目录数据
- `GET /api/health` - 健康检查
- `POST /api/init` - 初始化数据库

## 默认数据

启动时会自动创建：
- 用户1: user_001 (用户001, 默认买家)
- 用户2: seller_001 (卖家A, 卖家)
- 10本示例书籍数据

## 数据库

使用 SQLite 数据库，文件位于 `server/seekbook.db`

如需重新初始化数据，调用：
```bash
curl -X POST http://localhost:5000/api/init
```

## 跨域配置

默认允许以下地址访问：
- http://localhost:5173
- http://127.0.0.1:5173

如需修改，请编辑 `config.py` 中的 `CORS_ORIGINS`
