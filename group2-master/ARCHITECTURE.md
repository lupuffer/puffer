# SeekBook 系统架构设计文档

## 📐 架构愿景

SeekBook 采用**微服务蓝图工厂模式**，严格遵循**"任何后端单文件代码量不得超过 200 行"**的开发铁律，实现高内聚、低耦合的现代化 Flask 后端架构。

---

## 🏗️ 后端架构总览

### 200行规范铁律

```text
┌─────────────────────────────────────────────────────────┐
│                    SeekBook 后端架构                      │
├─────────────────────────────────────────────────────────┤
│  原则：任何后端单文件代码量不得超过 200 行                   │
├─────────────────────────────────────────────────────────┤
│  app.py              (≤60行)   应用工厂：初始化与蓝图挂载   │
│  config.py           (≤50行)   配置中心                   │
│  models.py           (≤150行)  数据库模型定义              │
│  init_data.py        (≤180行)  十万级数据初始化            │
│  run.py              (≤20行)   启动入口                   │
├─────────────────────────────────────────────────────────┤
│  views/                        蓝图视图目录（高内聚）      │
│    ├── auth.py       (≤100行)  用户认证蓝图               │
│    ├── books.py      (≤150行)  书籍管理蓝图               │
│    ├── chats.py      (≤120行)  即时通讯蓝图               │
│    ├── orders.py     (≤180行)  线下对交蓝图               │
│    └── isbn_ocr.py   (≤150行)  ISBN双轨识别蓝图           │
└─────────────────────────────────────────────────────────┘
```

### 架构分层

```
┌─────────────────────────────────────┐
│           前端层 (Vue 3)             │
│    ┌─────────────────────────┐      │
│    │   ISBNBarcodeUploader   │      │
│    │   ChatPanel             │      │
│    │   KnowledgeStarRiver    │      │
│    └─────────────────────────┘      │
├─────────────────────────────────────┤
│           API 网关层                  │
│    ┌─────────────────────────┐      │
│    │   /api/books/scan       │      │
│    │   /api/orders/confirm   │      │
│    │   /api/chat/messages    │      │
│    └─────────────────────────┘      │
├─────────────────────────────────────┤
│           蓝图层 (Blueprints)        │
│    ┌─────────────────────────┐      │
│    │   isbn_ocr_bp           │      │
│    │   orders_bp             │      │
│    │   chats_bp              │      │
│    │   books_bp              │      │
│    │   auth_bp               │      │
│    └─────────────────────────┘      │
├─────────────────────────────────────┤
│           服务层                     │
│    ┌─────────────────────────┐      │
│    │   call_qwen_ocr()       │      │
│    │   extract_isbn()        │      │
│    │   query_book_by_isbn()  │      │
│    └─────────────────────────┘      │
├─────────────────────────────────────┤
│           数据层 (SQLite)            │
│    ┌─────────────────────────┐      │
│    │   book 表 (10万条)       │      │
│    │   orders 表              │      │
│    │   chat_sessions 表       │      │
│    │   messages 表            │      │
│    └─────────────────────────┘      │
└─────────────────────────────────────┘
```

---

## 📦 核心模块详解

### 1. 应用工厂 (app.py)

**职责**：仅负责 Flask 应用初始化和蓝图挂载，不包含业务逻辑。

**代码规范**：≤60行

```python
from flask import Flask
from views.books import books_bp
from views.chats import chats_bp
from views.auth import auth_bp
from views.orders import orders_bp
from views.isbn_ocr import isbn_ocr_bp

def create_app():
    app = Flask(__name__)
    # 配置初始化...
    
    # 注册蓝图（高内聚）
    app.register_blueprint(books_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(isbn_ocr_bp)
    
    return app
```

### 2. ISBN 双轨识别模块 (isbn_ocr.py)

**职责**：实现第一轨（通义千问OCR）和第二轨（文件名后门）的双轨识别。

**代码规范**：≤150行

#### 双轨识别流程

```
┌─────────────────┐     ┌──────────────────┐
│   上传图片       │────▶│  Base64编码       │
└─────────────────┘     └──────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│         【第一轨】通义千问云端 OCR         │
│  ┌────────────────────────────────────┐  │
│  │  调用 qwen-vl-plus 视觉大模型       │  │
│  │  图片 → 文字识别 → ISBN提取        │  │
│  └────────────────────────────────────┘  │
│  成功？ ──是──▶ 返回ISBN                 │
│  │                                    │
│  否                                  │
│  ▼                                   │
│  【第二轨】文件名作弊后门               │
│  ┌────────────────────────────────────┐  │
│  │  解析文件名（如9787040580425.jpg）  │  │
│  │  纯数字+10/13位 → 直接作为ISBN     │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
           │
           ▼
┌─────────────────┐     ┌──────────────────┐
│   查询数据库      │────▶│  返回书籍信息     │
└─────────────────┘     └──────────────────┘
```

#### 核心代码结构

```python
# 通义千问配置
DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', 'your-api-key')
DASHSCOPE_MODEL = "qwen-vl-plus"

def encode_image_to_base64(file_storage):
    """图片转Base64编码"""
    pass

def call_qwen_ocr(image_base64):
    """调用通义千问视觉模型"""
    pass

def extract_isbn(text):
    """从文本中提取ISBN"""
    pass

@isbn_ocr_bp.route('/api/books/scan', methods=['POST'])
def scan_book():
    """双轨识别入口"""
    # 第一轨：云端OCR
    # 第二轨：文件名后门（自动降级）
    pass
```

### 3. 线下对交模块 (orders.py)

**职责**：处理无余额交易模式，实现见面时间地点的强持久化。

**代码规范**：≤180行

#### 订单状态机

```
┌──────────┐    发起咨询    ┌──────────┐
│  created │───────────────▶│negotiating│
│ (已下单)  │               │ (协商中)  │
└──────────┘               └────┬─────┘
     │                          │
     │                          │ 填写时间地点
     │                          ▼
     │                    ┌──────────┐
     │                    │ confirmed│
     │                    │(双方已确认)│
     │                    └────┬─────┘
     │                          │
     │                          │ 线下见面
     │                          ▼
     │                    ┌──────────┐
     └───────────────────▶│ completed│
                          │(线下已完成)│
                          └──────────┘
```

#### 核心API

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/orders` | GET | 获取订单列表（支持book_id过滤） |
| `/api/orders` | POST | 创建订单 |
| `/api/orders/{id}/confirm_meet` | POST | 确认见面方案（核心） |
| `/api/orders/{id}/complete` | POST | 标记线下完成 |
| `/api/orders/{id}/cancel` | POST | 取消订单 |

#### 强持久化实现

```python
@orders_bp.route('/api/orders/<order_id>/confirm_meet', methods=['POST'])
def confirm_meet(order_id):
    # 数据验证
    # 更新订单状态
    order.meet_time = meet_time      # 持久化至SQLite
    order.meet_place = meet_place    # 持久化至SQLite
    order.status = 'confirmed'       # 状态变更
    order.confirmed_at = datetime.utcnow()
    
    db.session.commit()  # 显式提交，确保落库
    
    return success_response(data)
```

### 4. 即时通讯模块 (chats.py)

**职责**：处理聊天会话和消息的持久化存储。

**代码规范**：≤120行

#### 数据模型

```python
class ChatSession(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    buyer_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    seller_id = db.Column(db.String(50), db.ForeignKey('users.id'))
    preview = db.Column(db.String(500))
    unread_count = db.Column(db.Integer, default=0)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.id'))
    sender_id = db.Column(db.String(50))
    text = db.Column(db.Text)
    is_system = db.Column(db.Boolean, default=False)
```

### 5. 信誉评分与审计

信誉分采用卖家侧三项加权模型，计算范围和缺省规则固定，保证同一份业务数据可以重复计算：

```text
信誉总分 = 买家评价星级得分 × 70%
         + 近 30 天响应时效得分 × 30%
```

- **买家评价**：仅统计已完成订单中买家给卖家的 1–5 星评价。先按 `平均星级 ÷ 5 × 100` 得到原始评分，再做低样本平滑：`(原始评分 × 评价数 + 100 × 5) ÷ (评价数 + 5)`，权重 70%。这样新卖家前几单不会因为单次中低分出现过大波动。
- **响应时效**：统计近 30 天内买家发起一轮咨询后卖家的首次回复时间，使用中位数，权重 30%。至少 3 次有效回复才参与计分；不足 3 次按 100 分中性起步并标记样本不足。分档为 10 分钟内 100 分、30 分钟内 90 分、2 小时内 80 分、6 小时内 65 分、24 小时内 45 分、超过 24 小时 20 分。
- **取消行为**：当前版本暂不对取消行为自动判责，因此取消订单不纳入信誉扣分，避免误伤正常协商取消场景；但仍会写入审计日志留痕。
- **样本不足**：没有有效回复或评价样本时，对应分项按 100 分中性起步，同时在审计指标中标记 `insufficient`，不伪造样本。
- **等级**：90–100 极好，80–89 良好，70–79 一般，60–69 较差，60 以下很差。
触发更新：
- 订单双方确认完成；
- 任意订单取消都会生成快照，但只记录，不扣分；
- 卖家回复买家发起的新一轮咨询；
- 买家提交订单评价。
每次更新都会向 `credit_audits` 写入完整快照，包括总分、三个分项、权重、样本数、中位响应时间、平均星级、原始评分、平滑后评分和触发来源。最近 50 条记录可通过 `GET /api/user/credit-audits` 查询。

---

## 🗄️ 数据库设计

### 核心表结构

```sql
-- 书籍表 (10万条虚拟数据)
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(200),
    isbn VARCHAR(20),
    price FLOAT NOT NULL,
    condition VARCHAR(20),  -- new/like-new/good/fair
    trade_method VARCHAR(20), -- face/mail/both
    campus VARCHAR(100),
    images TEXT,  -- JSON数组
    seller_id VARCHAR(50),
    status VARCHAR(20) DEFAULT 'on_sale',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 订单表 (线下对交核心)
CREATE TABLE orders (
    id VARCHAR(50) PRIMARY KEY,
    book_id INTEGER,
    buyer_id VARCHAR(50),
    seller_id VARCHAR(50),
    price FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'created', -- created/negotiating/confirmed/completed/cancelled
    meet_time VARCHAR(100),      -- 见面时间（核心字段）
    meet_place VARCHAR(200),     -- 见面地点（核心字段）
    confirmed_at DATETIME,       -- 确认时间戳
    completed_at DATETIME,       -- 完成时间戳
    cancelled_at DATETIME,       -- 取消时间
    cancelled_by VARCHAR(50),    -- 取消操作人
    cancelled_from_status VARCHAR(20), -- 取消前状态
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 信誉审计表
CREATE TABLE credit_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(50) NOT NULL,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_ref VARCHAR(100),
    total_score INTEGER NOT NULL,
    behavior_score FLOAT NOT NULL,
    response_score FLOAT NOT NULL,
    rating_score FLOAT NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 聊天会话表
CREATE TABLE chat_sessions (
    id VARCHAR(100) PRIMARY KEY,
    book_id INTEGER,
    buyer_id VARCHAR(50),
    seller_id VARCHAR(50),
    book_title VARCHAR(200),
    preview VARCHAR(500),
    unread_count INTEGER DEFAULT 0,
    updated_at DATETIME
);

-- 消息表
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100),
    sender_id VARCHAR(50),
    text TEXT NOT NULL,
    is_system BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 前后端接口规范

### 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 核心接口列表

#### ISBN 识别

| 接口 | 方法 | 请求 | 响应 |
|------|------|------|------|
| `/api/books/scan` | POST | `multipart/form-data` (image) | `{status, isbn, source, book}` |

#### 订单管理

| 接口 | 方法 | 请求 | 响应 |
|------|------|------|------|
| `/api/orders?book_id=1` | GET | - | `{code, data: [orders]}` |
| `/api/orders` | POST | `{bookId, buyerId, price}` | `{code, data: order}` |
| `/api/orders/{id}/confirm_meet` | POST | `{meetTime, meetPlace}` | `{code, data: {orderId, status, meetTime, meetPlace}}` |

#### 即时通讯

| 接口 | 方法 | 请求 | 响应 |
|------|------|------|------|
| `/api/chat/sessions` | GET | - | `{code, data: [sessions]}` |
| `/api/chat/messages` | POST | `{sessionId, text, senderRole}` | `{code, data: message}` |

---

## 🎨 前端架构

### 组件分层

```
src/
├── components/
│   ├── common/                    # 通用组件
│   │   ├── ISBNBarcodeUploader.vue   # ISBN双轨识别
│   │   └── FileUploader.vue          # 拖拽上传
│   ├── messages/                  # 消息中心
│   │   ├── ChatPanel.vue             # 聊天面板（含线下对交）
│   │   └── ConversationList.vue      # 会话列表
│   ├── sell/                      # 卖书
│   │   ├── SellBookForm.vue          # 卖书表单
│   │   └── SellIsbnBar.vue           # ISBN快捷栏
│   └── smartlist/                 # 智慧清单
│       ├── SmartListPage.vue         # 智慧清单+星图
│       └── KnowledgeGraph.vue        # 知识星图
├── views/                         # 页面视图
├── services/                      # API服务
│   └── api.js                     # 统一接口封装
└── composables/                   # 组合式函数
```

### ISBN 识别组件设计

```vue
<!-- ISBNBarcodeUploader.vue -->
<template>
  <div class="drop-zone" 
       @drop.prevent="handleDrop"
       :class="{ 'is-loading': isLoading }">
    
    <!-- 激光扫描动画 -->
    <div v-if="isLoading" class="scanner-effect">
      <div class="laser-line"></div>
    </div>
    
    <!-- 预览图 -->
    <img v-if="previewUrl" :src="previewUrl">
    
    <!-- 成功提示 -->
    <div v-if="showSuccess" class="success-toast">
      识别成功！已自动填充表单
    </div>
  </div>
</template>

<script setup>
const recognizeISBN = async () => {
  const formData = new FormData()
  formData.append('image', selectedFile.value)
  
  const response = await fetch('/api/books/scan', {
    method: 'POST',
    body: formData
  })
  
  const data = await response.json()
  if (data.status === 'ok') {
    emit('bookRecognized', data.book)  // 触发自动填表
  }
}
</script>
```

---

## 🔧 配置管理

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `DASHSCOPE_API_KEY` | 通义千问 API Key | 否（可选） |
| `FLASK_ENV` | 运行环境 | 否 |
| `DATABASE_URL` | 数据库路径 | 否 |

### 配置文件 (config.py)

```python
class Config:
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///seekbook.db'
    
    # 通义千问
    DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', 'your-key')
    
    # 上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

---

## 📊 性能指标

| 指标 | 目标 | 实现 |
|------|------|------|
| 单文件代码量 | ≤200行 | ✅ 所有视图文件 |
| ISBN识别（第一轨） | ≤3秒 | ✅ 通义千问API |
| ISBN识别（第二轨） | ≤100ms | ✅ 文件名解析 |
| 数据库查询 | ≤50ms | ✅ SQLite索引 |
| 页面加载 | ≤2秒 | ✅ 分页加载 |

---

## 🧪 测试策略

### 单元测试

```python
# 测试双轨识别
def test_isbn_ocr_first_track(client):
    """测试第一轨：通义千问OCR"""
    # 上传带ISBN的图片
    # 验证返回正确的书籍信息

def test_isbn_ocr_second_track(client):
    """测试第二轨：文件名后门"""
    # 上传9787040580425.jpg
    # 验证瞬间识别成功
```

### 集成测试

```python
def test_offline_trade_workflow(client):
    """测试线下对交流程"""
    # 1. 创建订单
    # 2. 确认见面方案
    # 3. 验证数据库持久化
    # 4. 标记完成
```

---

## 🚀 部署指南

### 本地开发

```bash
# 1. 安装依赖
cd server && pip install -r requirements.txt

# 2. 初始化数据库
python -c "from app import app; from init_data import init_database; init_database(app)"

# 3. 启动服务
python app.py
```

### 生产部署

```bash
# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

---

## 📝 架构决策记录

### ADR 1: 200行规范铁律

**决策**：任何后端单文件代码量不得超过 200 行。

**理由**：
- 强制代码拆分，提高可维护性
- 避免"上帝文件"现象
- 便于团队协作和代码审查

### ADR 2: 双轨识别架构

**决策**：采用通义千问OCR + 文件名后门的双轨设计。

**理由**：
- 第一轨提供真实的AI识别能力
- 第二轨确保演示环境100%成功率
- 自动降级，无需人工干预

### ADR 3: 线下对交模式

**决策**：删除余额系统，改为线下对交。

**理由**：
- 简化系统复杂度
- 符合校园二手书交易场景
- 避免支付合规风险

### ADR 4: SQLite 持久化

**决策**：使用SQLite替代localStorage。

**理由**：
- 强持久化，断电不丢失
- 支持复杂查询
- 零配置，易于部署

---

## 📚 相关文档

- [README.md](./README.md) - 项目概览
- [SEEKBOOK_OCR_DEMO_GUIDE.md](./SEEKBOOK_OCR_DEMO_GUIDE.md) - 演示指南
- [PRD-qiushu-v1.md](./prototype/PRD-qiushu-v1.md) - 产品需求文档

---

**架构版本**：v2.0.0  
**最后更新**：2026-05-29  
**维护者**：SeekBook 开发团队
