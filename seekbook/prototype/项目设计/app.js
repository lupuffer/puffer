// ==================== 星辰书链 - 核心应用逻辑 ====================
// 纯前端实现，无框架，无var，Promise数据加载

// 数据配置
const CONFIG = {
  TOTAL_BOOKS: 100000,
  BATCH_SIZE: 5000,
  PAGE_SIZE: 20,
  STORAGE_KEY: 'qiushu_data',
  USER_KEY: 'qiushu_user',
  SESSION_KEY: 'qiushu_session'
};

// 书籍模板
const BOOK_TEMPLATES = [
  {t: "数据结构", a: "严蔚敏", c: "计算机"},
  {t: "算法导论", a: "Cormen", c: "计算机"},
  {t: "高等数学", a: "同济大学", c: "数学"},
  {t: "线性代数", a: "同济大学", c: "数学"},
  {t: "大学物理", a: "程守洙", c: "物理"},
  {t: "操作系统", a: "Silberschatz", c: "计算机"},
  {t: "计算机网络", a: "谢希仁", c: "计算机"},
  {t: "Java编程", a: "Bruce Eckel", c: "计算机"},
  {t: "概率统计", a: "盛骤", c: "数学"},
  {t: "英语四级", a: "新东方", c: "外语"}
];

const CAMPUSES = ["紫金港", "玉泉", "西溪", "华家池", "之江"];
const CONDITIONS = ["全新", "九成新", "八成新", "七成新", "六成新"];
const IMAGES = ["book1.jpg", "book2.jpg", "book3.jpg"];

// ==================== Promise数据生成器 ====================

const DataGenerator = {
  // 分批生成书籍数据
  generateBooks(start, count) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const books = [];
        for (let i = start; i < start + count && i < CONFIG.TOTAL_BOOKS; i++) {
          const tmpl = BOOK_TEMPLATES[i % BOOK_TEMPLATES.length];
          const price = Math.floor(Math.random() * 50) + 10;
          const sellerId = (i % 1000) + 1;
          
          books.push({
            id: i + 1,
            title: tmpl.t + (Math.floor(i / 10) > 0 ? " 第" + (Math.floor(i / 10) + 1) + "册" : ""),
            author: tmpl.a,
            isbn: "9787" + String(Math.floor(Math.random() * 1000000000)).padStart(9, '0'),
            price: price,
            originalPrice: price * 2 + Math.floor(Math.random() * 30),
            campus: CAMPUSES[i % CAMPUSES.length],
            condition: CONDITIONS[i % CONDITIONS.length],
            hasNotes: i % 3 === 0,
            tradeType: ["face", "ship", "both"][i % 3],
            sellerId: sellerId,
            sellerName: "卖家" + sellerId,
            sellerReputation: 70 + Math.floor(Math.random() * 30),
            image: IMAGES[i % IMAGES.length],
            status: "active",
            category: tmpl.c,
            publishTime: new Date(Date.now() - Math.floor(Math.random() * 30) * 86400000).toISOString().split('T')[0]
          });
        }
        resolve(books);
      }, 0);
    });
  },

  // 生成用户数据
  generateUsers() {
    const users = [];
    for (let i = 1; i <= 1000; i++) {
      users.push({
        id: i,
        name: "用户" + i,
        email: "user" + i + "@zju.edu.cn",
        campus: CAMPUSES[i % CAMPUSES.length],
        reputation: 70 + Math.floor(Math.random() * 30),
        joinTime: new Date(Date.now() - Math.floor(Math.random() * 365) * 86400000).toISOString().split('T')[0],
        isZjuAuth: i % 5 !== 0 // 80%是浙大认证用户
      });
    }
    return users;
  },

  // 生成交易记录
  generateOrders() {
    const orders = [];
    const statuses = ["pending", "confirmed", "delivering", "completed", "cancelled"];
    for (let i = 1; i <= 5000; i++) {
      orders.push({
        id: "ORD" + String(i).padStart(6, '0'),
        bookId: Math.floor(Math.random() * CONFIG.TOTAL_BOOKS) + 1,
        buyerId: Math.floor(Math.random() * 1000) + 1,
        sellerId: Math.floor(Math.random() * 1000) + 1,
        price: Math.floor(Math.random() * 50) + 10,
        status: statuses[Math.floor(Math.random() * statuses.length)],
        createTime: new Date(Date.now() - Math.floor(Math.random() * 30) * 86400000).toISOString().split('T')[0]
      });
    }
    return orders;
  }
};

// ==================== 数据存储管理器 ====================

const DataStore = {
  // 内存数据缓存
  cache: {
    books: [],
    users: [],
    orders: [],
    currentUser: null,
    messages: [],
    tradeCards: []
  },

  // 初始化数据
  async init() {
    // 从localStorage加载或生成
    let data = JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEY));
    
    if (!data) {
      data = {
        users: DataGenerator.generateUsers(),
        orders: DataGenerator.generateOrders(),
        messages: [],
        tradeCards: []
      };
      localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(data));
    }
    
    this.cache.users = data.users;
    this.cache.orders = data.orders;
    this.cache.messages = data.messages || [];
    this.cache.tradeCards = data.tradeCards || [];
    
    // 加载当前用户
    this.cache.currentUser = JSON.parse(localStorage.getItem(CONFIG.USER_KEY));
    
    return this.cache;
  },

  // 保存到localStorage
  save() {
    const data = {
      users: this.cache.users,
      orders: this.cache.orders,
      messages: this.cache.messages,
      tradeCards: this.cache.tradeCards
    };
    localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(data));
  },

  // 设置当前用户
  setCurrentUser(user) {
    this.cache.currentUser = user;
    if (user) {
      localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(CONFIG.USER_KEY);
    }
  },

  // 添加交易卡片
  addTradeCard(card) {
    this.cache.tradeCards.push(card);
    this.save();
  },

  // 更新交易卡片状态
  updateTradeCard(cardId, status) {
    const card = this.cache.tradeCards.find(c => c.id === cardId);
    if (card) {
      card.status = status;
      card.updateTime = new Date().toISOString();
      this.save();
      return card;
    }
    return null;
  },

  // 获取会话的交易卡片
  getTradeCards(conversationId) {
    return this.cache.tradeCards.filter(c => c.conversationId === conversationId);
  }
};

// ==================== 书籍数据加载器 ====================

const BookLoader = {
  // 分批加载所有书籍
  async loadAll(onProgress) {
    const books = [];
    const batches = Math.ceil(CONFIG.TOTAL_BOOKS / CONFIG.BATCH_SIZE);
    
    for (let i = 0; i < batches; i++) {
      const start = i * CONFIG.BATCH_SIZE;
      const batch = await DataGenerator.generateBooks(start, CONFIG.BATCH_SIZE);
      books.push(...batch);
      
      if (onProgress) {
        onProgress({
          loaded: books.length,
          total: CONFIG.TOTAL_BOOKS,
          percent: Math.floor(((i + 1) / batches) * 100)
        });
      }
      
      // 每批加载后让出时间片，避免阻塞UI
      await new Promise(r => setTimeout(r, 0));
    }
    
    DataStore.cache.books = books;
    return books;
  },

  // 搜索书籍
  search(keyword, filters = {}) {
    let result = DataStore.cache.books;
    
    if (keyword) {
      const k = keyword.toLowerCase();
      result = result.filter(b => 
        b.title.toLowerCase().includes(k) ||
        b.author.toLowerCase().includes(k) ||
        b.isbn.includes(k)
      );
    }
    
    if (filters.campus) {
      result = result.filter(b => b.campus === filters.campus);
    }
    
    if (filters.category) {
      result = result.filter(b => b.category === filters.category);
    }
    
    if (filters.minPrice !== undefined) {
      result = result.filter(b => b.price >= filters.minPrice);
    }
    
    if (filters.maxPrice !== undefined) {
      result = result.filter(b => b.price <= filters.maxPrice);
    }
    
    // 排序
    if (filters.sort === 'price-asc') {
      result.sort((a, b) => a.price - b.price);
    } else if (filters.sort === 'price-desc') {
      result.sort((a, b) => b.price - a.price);
    } else if (filters.sort === 'reputation') {
      result.sort((a, b) => b.sellerReputation - a.sellerReputation);
    } else {
      result.sort((a, b) => b.id - a.id);
    }
    
    return result;
  },

  // 分页获取
  getPage(page, pageSize = CONFIG.PAGE_SIZE, filtered = null) {
    const books = filtered || DataStore.cache.books;
    const start = (page - 1) * pageSize;
    return books.slice(start, start + pageSize);
  },

  // 根据ID获取
  getById(id) {
    return DataStore.cache.books.find(b => b.id === parseInt(id));
  }
};

// ==================== 用户认证管理 ====================

const Auth = {
  // 登录
  login(email, password) {
    const user = DataStore.cache.users.find(u => u.email === email);
    if (user) {
      // 模拟密码验证（实际应该加密）
      DataStore.setCurrentUser(user);
      return { success: true, user };
    }
    return { success: false, message: "邮箱或密码错误" };
  },

  // 浙大统一认证登录
  loginZju() {
    // 模拟浙大认证，随机选择一个浙大用户
    const zjuUsers = DataStore.cache.users.filter(u => u.isZjuAuth);
    const user = zjuUsers[Math.floor(Math.random() * zjuUsers.length)];
    DataStore.setCurrentUser(user);
    return { success: true, user };
  },

  // 注册
  register(userData) {
    const exists = DataStore.cache.users.find(u => u.email === userData.email);
    if (exists) {
      return { success: false, message: "邮箱已注册" };
    }
    
    const newUser = {
      id: DataStore.cache.users.length + 1,
      ...userData,
      reputation: 80,
      joinTime: new Date().toISOString().split('T')[0],
      isZjuAuth: false
    };
    
    DataStore.cache.users.push(newUser);
    DataStore.save();
    DataStore.setCurrentUser(newUser);
    return { success: true, user: newUser };
  },

  // 登出
  logout() {
    DataStore.setCurrentUser(null);
  },

  // 检查登录状态
  isLoggedIn() {
    return !!DataStore.cache.currentUser;
  },

  // 获取当前用户
  getCurrentUser() {
    return DataStore.cache.currentUser;
  }
};

// ==================== 交易确认卡片管理 ====================

const TradeCard = {
  // 创建交易卡片
  create(data) {
    const card = {
      id: 'TC' + Date.now(),
      bookId: data.bookId,
      bookTitle: data.bookTitle,
      price: data.price,
      tradeType: data.tradeType,
      location: data.location,
      time: data.time,
      note: data.note || '',
      status: 'pending', // pending, confirmed, rejected
      senderId: data.senderId,
      receiverId: data.receiverId,
      conversationId: data.conversationId,
      createTime: new Date().toISOString(),
      updateTime: null
    };
    
    DataStore.addTradeCard(card);
    return card;
  },

  // 确认交易
  confirm(cardId) {
    return DataStore.updateTradeCard(cardId, 'confirmed');
  },

  // 拒绝交易
  reject(cardId) {
    return DataStore.updateTradeCard(cardId, 'rejected');
  },

  // 获取卡片HTML
  render(card, isReceiver) {
    const typeText = { face: '当面交易', ship: '邮寄', both: '均可' };
    const statusConfig = {
      pending: { text: '等待确认', class: 'status-pending' },
      confirmed: { text: '已确认', class: 'status-confirmed' },
      rejected: { text: '已拒绝', class: 'status-rejected' }
    };
    const status = statusConfig[card.status];
    
    return `
      <div class="trade-card ${status.class}" data-id="${card.id}">
        <div class="trade-card-header">
          <i class="fas fa-clipboard-check"></i>
          <span>交易确认单</span>
        </div>
        <div class="trade-card-body">
          <p><span>书籍：</span>${card.bookTitle}</p>
          <p><span>价格：</span>¥${card.price}</p>
          <p><span>方式：</span>${typeText[card.tradeType]}</p>
          <p><span>地点：</span>${card.location}</p>
          <p><span>时间：</span>${card.time}</p>
          ${card.note ? `<p><span>备注：</span>${card.note}</p>` : ''}
        </div>
        <div class="trade-card-status">${status.text}</div>
        ${isReceiver && card.status === 'pending' ? `
          <div class="trade-card-actions">
            <button class="btn-confirm" onclick="handleConfirmTrade('${card.id}')">
              <i class="fas fa-check"></i> 确认
            </button>
            <button class="btn-reject" onclick="handleRejectTrade('${card.id}')">
              <i class="fas fa-times"></i> 拒绝
            </button>
          </div>
        ` : ''}
      </div>
    `;
  }
};

// ==================== 导出全局对象 ====================

window.QS = {
  CONFIG,
  DataGenerator,
  DataStore,
  BookLoader,
  Auth,
  TradeCard
};