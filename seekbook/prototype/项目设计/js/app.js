/**
 * 求书平台 - 全局应用状态管理与页面交互系统
 * 实现所有页面间的数据共享、状态同步和导航交互
 */

// ============================================================
// 1. 全局应用状态
// ============================================================
const AppState = {
    // 用户状态
    user: {
        isLoggedIn: false,
        id: null,
        name: '张同学',
        email: 'zhang@zju.edu.cn',
        studentId: '3200100001',
        college: '计算机科学与技术学院',
        grade: '大三',
        campus: '紫金港校区',
        reputation: 'A+',
        avatar: null,
        phone: '138****5678'
    },

    // 购物车
    cart: {
        items: [],
        total: 0
    },

    // 收藏
    wishlist: [],

    // 消息未读数
    unreadMessages: {
        total: 12,
        conversations: {
            '张同学': 3,
            '李同学': 0,
            '王同学': 0,
            '赵同学': 0
        }
    },

    // 订单数据
    orders: [
        {
            id: 1,
            orderNo: '#20230415001',
            bookTitle: '数据结构（C语言版）',
            bookAuthor: '严蔚敏',
            bookImage: 'https://via.placeholder.com/80x100/4A90E2/FFFFFF?text=数据结构',
            isbn: '9787302147510',
            price: 35.00,
            status: 'pending',
            statusText: '待沟通',
            partner: '张同学',
            partnerCampus: '紫金港校区',
            partnerReputation: 'A+',
            tradeMethod: '当面交易',
            campus: '紫金港校区',
            createdAt: '2023-04-15 14:30',
            completedAt: null
        },
        {
            id: 2,
            orderNo: '#20230414002',
            bookTitle: '算法导论',
            bookAuthor: 'Thomas H. Cormen',
            bookImage: 'https://via.placeholder.com/80x100/50C878/FFFFFF?text=算法导论',
            isbn: '9787111187776',
            price: 85.00,
            status: 'confirmed',
            statusText: '待确认',
            partner: '李同学',
            partnerCampus: '玉泉校区',
            partnerReputation: 'A',
            tradeMethod: '邮寄交易',
            campus: '玉泉校区',
            createdAt: '2023-04-14 10:15',
            completedAt: null
        },
        {
            id: 3,
            orderNo: '#20230410003',
            bookTitle: '高等数学（第七版）',
            bookAuthor: '同济大学数学系',
            bookImage: 'https://via.placeholder.com/80x100/FF6B6B/FFFFFF?text=高等数学',
            isbn: '9787040396638',
            price: 45.00,
            status: 'completed',
            statusText: '已完成',
            partner: '王同学',
            partnerCampus: '紫金港校区',
            partnerReputation: 'A+',
            tradeMethod: '当面交易',
            campus: '紫金港校区',
            createdAt: '2023-04-10 14:00',
            completedAt: '2023-04-12 16:45',
            rating: 4.5
        },
        {
            id: 4,
            orderNo: '#20230405004',
            bookTitle: '大学物理（第五版）',
            bookAuthor: '张三慧',
            bookImage: 'https://via.placeholder.com/80x100/FFA500/FFFFFF?text=大学物理',
            isbn: '9787302173144',
            price: 38.00,
            status: 'cancelled',
            statusText: '已取消',
            partner: '赵同学',
            partnerCampus: '西溪校区',
            partnerReputation: 'B',
            tradeMethod: '当面交易',
            campus: '西溪校区',
            createdAt: '2023-04-05 09:20',
            completedAt: null,
            cancelReason: '买家改变主意'
        }
    ],

    // 书籍数据
    books: [
        {
            id: 1,
            title: '数据结构（C语言版）',
            author: '严蔚敏 编著',
            publisher: '清华大学出版社',
            isbn: '9787302147510',
            price: 35.00,
            originalPrice: 68.00,
            condition: '九成新',
            hasNotes: true,
            campus: '紫金港校区',
            rating: 4.8,
            seller: '张同学',
            sellerReputation: 'A+',
            image: 'https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=400&q=80',
            description: '封面完好，内页有少量铅笔标记，包含详细的手写笔记（约50页）',
            category: '计算机科学'
        },
        {
            id: 2,
            title: '算法导论',
            author: 'Thomas H. Cormen 等',
            publisher: '机械工业出版社',
            isbn: '9787111187776',
            price: 85.00,
            originalPrice: 128.00,
            condition: '良好',
            hasNotes: false,
            campus: '玉泉校区',
            rating: 4.9,
            seller: '李同学',
            sellerReputation: 'A',
            image: 'https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=400&q=80',
            description: '正常使用痕迹，无笔记，书页整洁',
            category: '计算机科学'
        },
        {
            id: 3,
            title: '高等数学（第七版）',
            author: '同济大学数学系',
            publisher: '高等教育出版社',
            isbn: '9787040396638',
            price: 45.00,
            originalPrice: 78.00,
            condition: '全新',
            hasNotes: true,
            campus: '紫金港校区',
            rating: 4.7,
            seller: '王同学',
            sellerReputation: 'A+',
            image: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&q=80',
            description: '全新未使用，附赠完整笔记',
            category: '数学'
        },
        {
            id: 4,
            title: '大学物理（第五版）',
            author: '张三慧',
            publisher: '清华大学出版社',
            isbn: '9787302173144',
            price: 38.00,
            originalPrice: 65.00,
            condition: '九成新',
            hasNotes: false,
            campus: '玉泉校区',
            rating: 4.6,
            seller: '赵同学',
            sellerReputation: 'B+',
            image: 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&q=80',
            description: '轻微使用痕迹，无笔记',
            category: '物理'
        },
        {
            id: 5,
            title: '大学英语四级考试指南',
            author: '教育部考试中心',
            publisher: '高等教育出版社',
            isbn: '9787040204568',
            price: 25.00,
            originalPrice: 48.00,
            condition: '良好',
            hasNotes: true,
            campus: '紫金港校区',
            rating: 4.5,
            seller: '孙同学',
            sellerReputation: 'A',
            image: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&q=80',
            description: '有重点标记和笔记',
            category: '英语'
        },
        {
            id: 6,
            title: '线性代数（第六版）',
            author: '同济大学数学系',
            publisher: '高等教育出版社',
            isbn: '9787040212181',
            price: 20.00,
            originalPrice: 42.00,
            condition: '一般',
            hasNotes: false,
            campus: '西溪校区',
            rating: 4.3,
            seller: '周同学',
            sellerReputation: 'B',
            image: 'https://images.unsplash.com/photo-1632516643771-68e14b8f5228?w=400&q=80',
            description: '有明显使用痕迹，无缺页',
            category: '数学'
        }
    ],

    // 浏览历史
    browsingHistory: [],

    // 搜索历史
    searchHistory: [],

    // 页面来源追踪（用于面包屑和返回导航）
    pageSource: {
        from: null,
        params: {}
    }
};

// ============================================================
// 2. 状态管理方法
// ============================================================
const AppActions = {
    // 用户登录
    login(userData) {
        AppState.user = { ...AppState.user, ...userData, isLoggedIn: true };
        this.saveState();
        this.updateUI();
    },

    // 用户登出
    logout() {
        AppState.user.isLoggedIn = false;
        this.saveState();
        this.updateUI();
    },

    // 添加到购物车
    addToCart(book) {
        const existing = AppState.cart.items.find(item => item.id === book.id);
        if (existing) {
            existing.quantity += 1;
        } else {
            AppState.cart.items.push({ ...book, quantity: 1 });
        }
        this.updateCartTotal();
        this.saveState();
        this.updateUI();
        this.showToast(`《${book.title}》已加入购物车`, 'success');
    },

    // 从购物车移除
    removeFromCart(bookId) {
        AppState.cart.items = AppState.cart.items.filter(item => item.id !== bookId);
        this.updateCartTotal();
        this.saveState();
        this.updateUI();
    },

    // 更新购物车总计
    updateCartTotal() {
        AppState.cart.total = AppState.cart.items.reduce(
            (sum, item) => sum + item.price * item.quantity, 0
        );
    },

    // 添加到收藏
    addToWishlist(book) {
        if (!AppState.wishlist.find(item => item.id === book.id)) {
            AppState.wishlist.push(book);
            this.saveState();
            this.updateUI();
            this.showToast(`《${book.title}》已加入收藏`, 'success');
        } else {
            this.showToast(`《${book.title}》已在收藏列表中`, 'info');
        }
    },

    // 从收藏移除
    removeFromWishlist(bookId) {
        AppState.wishlist = AppState.wishlist.filter(item => item.id !== bookId);
        this.saveState();
        this.updateUI();
    },

    // 添加浏览历史
    addBrowsingHistory(book) {
        AppState.browsingHistory = AppState.browsingHistory.filter(item => item.id !== book.id);
        AppState.browsingHistory.unshift(book);
        if (AppState.browsingHistory.length > 20) {
            AppState.browsingHistory.pop();
        }
        this.saveState();
    },

    // 添加搜索历史
    addSearchHistory(query) {
        AppState.searchHistory = AppState.searchHistory.filter(item => item !== query);
        AppState.searchHistory.unshift(query);
        if (AppState.searchHistory.length > 10) {
            AppState.searchHistory.pop();
        }
        this.saveState();
    },

    // 更新订单状态
    updateOrderStatus(orderId, newStatus, statusText) {
        const order = AppState.orders.find(o => o.id === orderId);
        if (order) {
            order.status = newStatus;
            if (statusText) order.statusText = statusText;
            if (newStatus === 'completed') {
                order.completedAt = new Date().toISOString().split('T')[0];
            }
            this.saveState();
            this.updateUI();
        }
    },

    // 创建订单
    createOrder(bookData, partner) {
        const newOrder = {
            id: AppState.orders.length + 1,
            orderNo: `#${new Date().getFullYear()}${String(new Date().getMonth() + 1).padStart(2, '0')}${String(new Date().getDate()).padStart(2, '0')}${String(AppState.orders.length + 1).padStart(3, '0')}`,
            bookTitle: bookData.title,
            bookAuthor: bookData.author,
            bookImage: bookData.image || 'https://via.placeholder.com/80x100/4A90E2/FFFFFF?text=书籍',
            isbn: bookData.isbn || '',
            price: bookData.price,
            status: 'pending',
            statusText: '待沟通',
            partner: partner.name,
            partnerCampus: partner.campus || '紫金港校区',
            partnerReputation: partner.reputation || 'A',
            tradeMethod: '当面交易',
            campus: partner.campus || '紫金港校区',
            createdAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
            completedAt: null
        };
        AppState.orders.unshift(newOrder);
        this.saveState();
        this.updateUI();
        return newOrder;
    },

    // 获取未读消息数
    getUnreadCount() {
        return AppState.unreadMessages.total;
    },

    // 标记消息已读
    markConversationRead(userName) {
        if (AppState.unreadMessages.conversations[userName]) {
            AppState.unreadMessages.total -= AppState.unreadMessages.conversations[userName];
            AppState.unreadMessages.conversations[userName] = 0;
            this.saveState();
            this.updateUI();
        }
    },

    // 保存状态到 localStorage
    saveState() {
        try {
            localStorage.setItem('seekbook_app_state', JSON.stringify(AppState));
        } catch (e) {
            console.warn('Failed to save state:', e);
        }
    },

    // 从 localStorage 加载状态
    loadState() {
        try {
            const saved = localStorage.getItem('seekbook_app_state');
            if (saved) {
                const parsed = JSON.parse(saved);
                Object.assign(AppState, parsed);
            }
        } catch (e) {
            console.warn('Failed to load state:', e);
        }
    },

    // 更新所有UI组件
    updateUI() {
        // 更新导航栏用户状态
        this.updateNavAuth();
        // 更新未读消息徽标
        this.updateUnreadBadge();
        // 更新购物车徽标
        this.updateCartBadge();
    },

    // 更新导航栏认证状态
    updateNavAuth() {
        const navAuth = document.querySelector('.nav-auth');
        if (!navAuth) return;

        if (AppState.user.isLoggedIn) {
            navAuth.innerHTML = `
                <div class="auth-badge">
                    <i class="fas fa-check-circle"></i>
                    <span>${AppState.user.name}</span>
                </div>
                <button class="btn btn-outline" onclick="AppActions.logout()">
                    <i class="fas fa-sign-out-alt"></i> 退出
                </button>
            `;
        } else {
            navAuth.innerHTML = `
                <div class="auth-badge">
                    <i class="fas fa-check-circle"></i>
                    <span>浙大实名认证</span>
                </div>
                <button class="btn btn-outline" onclick="location.href='login.html'">
                    <i class="fas fa-sign-in-alt"></i> 登录
                </button>
            `;
        }
    },

    // 更新未读消息徽标
    updateUnreadBadge() {
        const msgLink = document.querySelector('a[href="messages.html"]');
        if (msgLink) {
            const count = this.getUnreadCount();
            let badge = msgLink.querySelector('.unread-badge-nav');
            if (count > 0) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'unread-badge-nav';
                    msgLink.appendChild(badge);
                }
                badge.textContent = count > 99 ? '99+' : count;
            } else if (badge) {
                badge.remove();
            }
        }
    },

    // 更新购物车徽标
    updateCartBadge() {
        const cartLink = document.querySelector('a[href="buy.html"]');
        if (cartLink) {
            const count = AppState.cart.items.length;
            let badge = cartLink.querySelector('.cart-badge-nav');
            if (count > 0) {
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'cart-badge-nav';
                    cartLink.appendChild(badge);
                }
                badge.textContent = count;
            } else if (badge) {
                badge.remove();
            }
        }
    },

    // 显示Toast通知
    showToast(message, type = 'info') {
        // 移除已存在的toast样式
        if (!document.querySelector('#app-toast-styles')) {
            const style = document.createElement('style');
            style.id = 'app-toast-styles';
            style.textContent = `
                .app-toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 8px;
                    padding: 16px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    min-width: 300px;
                    max-width: 400px;
                    z-index: 10000;
                    animation: appToastSlideIn 0.3s ease;
                }
                .app-toast-success { border-left: 4px solid #10b981; }
                .app-toast-info { border-left: 4px solid #3b82f6; }
                .app-toast-error { border-left: 4px solid #ef4444; }
                .app-toast-content {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                .app-toast-content i { font-size: 20px; }
                .app-toast-success .app-toast-content i { color: #10b981; }
                .app-toast-info .app-toast-content i { color: #3b82f6; }
                .app-toast-error .app-toast-content i { color: #ef4444; }
                .app-toast-close {
                    background: none;
                    border: none;
                    font-size: 20px;
                    color: #6b7280;
                    cursor: pointer;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                }
                .app-toast-close:hover { background-color: #f3f4f6; }
                @keyframes appToastSlideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }

        const toast = document.createElement('div');
        toast.className = `app-toast app-toast-${type}`;
        const iconMap = { success: 'check-circle', info: 'info-circle', error: 'exclamation-circle' };
        toast.innerHTML = `
            <div class="app-toast-content">
                <i class="fas fa-${iconMap[type] || 'info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="app-toast-close">&times;</button>
        `;
        document.body.appendChild(toast);

        toast.querySelector('.app-toast-close').addEventListener('click', () => toast.remove());
        setTimeout(() => {
            if (toast.parentNode) toast.remove();
        }, 3000);
    },

    // 页面间导航（带参数）
    navigateTo(page, params = {}) {
        let url = page;
        const queryString = Object.entries(params)
            .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
            .join('&');
        if (queryString) url += `?${queryString}`;
        window.location.href = url;
    },

    // 获取URL参数
    getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params.entries()) {
            result[key] = value;
        }
        return result;
    },

    // 搜索书籍
    searchBooks(query) {
        if (!query.trim()) return AppState.books;
        const q = query.toLowerCase().trim();
        return AppState.books.filter(book =>
            book.title.toLowerCase().includes(q) ||
            book.author.toLowerCase().includes(q) ||
            book.isbn.includes(q) ||
            book.category.toLowerCase().includes(q) ||
            book.publisher.toLowerCase().includes(q)
        );
    },

    // 按条件筛选书籍
    filterBooks(filters = {}) {
        let results = [...AppState.books];

        if (filters.category) {
            results = results.filter(b => b.category === filters.category);
        }
        if (filters.campus) {
            results = results.filter(b => b.campus.includes(filters.campus));
        }
        if (filters.condition) {
            results = results.filter(b => b.condition === filters.condition);
        }
        if (filters.hasNotes) {
            results = results.filter(b => b.hasNotes);
        }
        if (filters.minPrice !== undefined) {
            results = results.filter(b => b.price >= filters.minPrice);
        }
        if (filters.maxPrice !== undefined) {
            results = results.filter(b => b.price <= filters.maxPrice);
        }
        if (filters.keyword) {
            const q = filters.keyword.toLowerCase();
            results = results.filter(b =>
                b.title.toLowerCase().includes(q) ||
                b.author.toLowerCase().includes(q) ||
                b.isbn.includes(q)
            );
        }

        return results;
    },

    // 获取书籍详情
    getBookDetail(bookId) {
        return AppState.books.find(b => b.id === parseInt(bookId)) || AppState.books[0];
    },

    // 获取订单统计
    getOrderStats() {
        const total = AppState.orders.length;
        const pending = AppState.orders.filter(o => o.status === 'pending' || o.status === 'confirmed').length;
        const completed = AppState.orders.filter(o => o.status === 'completed').length;
        const cancelled = AppState.orders.filter(o => o.status === 'cancelled').length;
        const ratings = AppState.orders.filter(o => o.rating).map(o => o.rating);
        const avgRating = ratings.length ? (ratings.reduce((a, b) => a + b, 0) / ratings.length) : 0;
        const completionRate = total ? Math.round((completed / total) * 100) : 0;

        return { total, pending, completed, cancelled, avgRating, completionRate };
    }
};

// ============================================================
// 3. 初始化
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    // 加载保存的状态
    AppActions.loadState();

    // 更新UI
    AppActions.updateUI();

    // 添加导航栏徽标样式
    const badgeStyle = document.createElement('style');
    badgeStyle.textContent = `
        .unread-badge-nav, .cart-badge-nav {
            position: absolute;
            top: -6px;
            right: -10px;
            background: #ef4444;
            color: white;
            font-size: 11px;
            font-weight: 600;
            min-width: 18px;
            height: 18px;
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0 4px;
            box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
        }
        .nav-link {
            position: relative;
        }
    `;
    document.head.appendChild(badgeStyle);

    // 初始化导航栏高亮
    initNavHighlight();

    // 初始化面包屑导航
    initBreadcrumb();

    // 初始化搜索功能（全局）
    initGlobalSearch();
});

// 导航栏高亮
function initNavHighlight() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        link.classList.toggle('active', href === currentPage);
    });
}

// 面包屑导航
function initBreadcrumb() {
    const breadcrumb = document.querySelector('.breadcrumb');
    if (!breadcrumb) return;

    const pageNames = {
        'index.html': '首页',
        'buy.html': '我要买书',
        'sell.html': '我要卖书',
        'knowledge.html': '知识遗产社区',
        'messages.html': '消息中心',
        'profile.html': '个人中心',
        'orders.html': '我的订单',
        'book-detail.html': '书籍详情',
        'publish-sell.html': '发布卖书',
        'login.html': '登录',
        'ai-chatbot.html': 'AI客服助手'
    };

    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const pageName = pageNames[currentPage] || '未知页面';

    // 如果面包屑只有首页和当前页，确保当前页名称正确
    const spans = breadcrumb.querySelectorAll('span');
    if (spans.length === 1 && spans[0]) {
        spans[0].textContent = pageName;
    }
}

// 全局搜索功能
function initGlobalSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = this.value.trim();
                if (query) {
                    AppActions.addSearchHistory(query);
                    AppActions.navigateTo('buy.html', { q: query });
                }
            }
        });

        // 为搜索按钮添加事件
        const searchBox = input.closest('.search-box');
        if (searchBox) {
            const searchBtn = searchBox.querySelector('.search-btn');
            if (searchBtn) {
                searchBtn.addEventListener('click', function() {
                    const query = input.value.trim();
                    if (query) {
                        AppActions.addSearchHistory(query);
                        AppActions.navigateTo('buy.html', { q: query });
                    }
                });
            }
        }
    });
}

// ============================================================
// 4. 导出全局接口
// ============================================================
window.AppState = AppState;
window.AppActions = AppActions;
