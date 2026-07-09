/**
 * 求书平台 - 个人中心脚本
 * 集成全局应用状态，实现个人中心交互功能
 */

document.addEventListener('DOMContentLoaded', function() {
    initProfilePage();
});

function initProfilePage() {
    // 更新用户信息
    updateUserInfo();

    // 更新交易统计
    updateTradeStats();

    // 更新最近交易
    updateRecentTransactions();

    // 侧边栏菜单切换
    document.querySelectorAll('.profile-menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 切换菜单高亮
            document.querySelectorAll('.profile-menu-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            // 切换标签页
            const tabId = this.dataset.tab;
            document.querySelectorAll('.profile-tab').forEach(tab => tab.classList.remove('active'));
            const targetTab = document.getElementById(`${tabId}-tab`);
            if (targetTab) {
                targetTab.classList.add('active');
                
                // 如果切换到订单标签，加载订单内容
                if (tabId === 'my-orders') {
                    loadOrdersContent();
                }
                // 如果切换到收藏标签，加载收藏内容
                if (tabId === 'my-favorites') {
                    loadFavoritesContent();
                }
                // 如果切换到出售标签，加载出售内容
                if (tabId === 'my-sales') {
                    loadSalesContent();
                }
            }
        });
    });

    // 个人信息编辑
    initProfileEdit();
}

function updateUserInfo() {
    const user = AppState.user;

    // 更新用户名
    const nameEl = document.querySelector('.profile-info h2');
    if (nameEl) nameEl.textContent = user.name;

    // 更新专业
    const majorEl = document.querySelector('.profile-major');
    if (majorEl) majorEl.textContent = `${user.college} · ${user.grade}`;

    // 更新信誉等级
    const repEl = document.querySelector('.profile-reputation span');
    if (repEl) repEl.textContent = `信誉等级: ${user.reputation}`;

    // 更新个人信息详情
    const detailLabels = document.querySelectorAll('.detail-label');
    const detailValues = document.querySelectorAll('.detail-value');
    
    const detailMap = {
        '学号': user.studentId,
        '学院': user.college,
        '年级': user.grade,
        '校区': user.campus,
        '邮箱': user.email,
        '手机': user.phone
    };

    detailLabels.forEach((label, index) => {
        const key = label.textContent.trim();
        if (detailMap[key] && detailValues[index]) {
            detailValues[index].textContent = detailMap[key];
        }
    });
}

function updateTradeStats() {
    const stats = AppActions.getOrderStats();
    const books = AppState.books;

    const statCards = document.querySelectorAll('.stat-card .stat-value');
    if (statCards.length >= 4) {
        statCards[0].textContent = stats.completed;
        statCards[1].textContent = books.length;
        statCards[2].textContent = stats.avgRating.toFixed(1);
        statCards[3].textContent = '1560'; // 积分余额
    }
}

function updateRecentTransactions() {
    const transactionsList = document.querySelector('.transactions-list');
    if (!transactionsList) return;

    // 获取最近的订单
    const recentOrders = AppState.orders.slice(0, 3);

    transactionsList.innerHTML = recentOrders.map(order => {
        const isSuccess = order.status === 'completed';
        const isPending = order.status === 'pending' || order.status === 'confirmed';
        
        return `
            <div class="transaction-item" onclick="AppActions.navigateTo('orders.html')" style="cursor: pointer;">
                <div class="transaction-icon ${isSuccess ? 'success' : isPending ? 'pending' : 'cancelled'}">
                    <i class="fas ${isSuccess ? 'fa-check-circle' : isPending ? 'fa-clock' : 'fa-times-circle'}"></i>
                </div>
                <div class="transaction-details">
                    <h4>${isSuccess ? '购买' : isPending ? '购买' : '取消'}《${order.bookTitle}》</h4>
                    <p class="transaction-date">${order.createdAt}</p>
                    <p class="transaction-amount">¥${order.price.toFixed(2)}</p>
                    ${isPending ? `<span class="transaction-status">${order.statusText}</span>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

function loadOrdersContent() {
    const ordersContent = document.querySelector('#my-orders-tab .orders-content');
    if (!ordersContent) return;

    const stats = AppActions.getOrderStats();
    
    ordersContent.innerHTML = `
        <div class="profile-section">
            <h3><i class="fas fa-clipboard-list"></i> 我的订单</h3>
            <div class="stats-grid" style="margin-bottom: 24px;">
                <div class="stat-card" onclick="AppActions.navigateTo('orders.html')" style="cursor: pointer;">
                    <div class="stat-icon"><i class="fas fa-clock"></i></div>
                    <div class="stat-content">
                        <span class="stat-value">${stats.pending}</span>
                        <span class="stat-label">进行中</span>
                    </div>
                </div>
                <div class="stat-card" onclick="AppActions.navigateTo('orders.html')" style="cursor: pointer;">
                    <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                    <div class="stat-content">
                        <span class="stat-value">${stats.completed}</span>
                        <span class="stat-label">已完成</span>
                    </div>
                </div>
                <div class="stat-card" onclick="AppActions.navigateTo('orders.html')" style="cursor: pointer;">
                    <div class="stat-icon"><i class="fas fa-star"></i></div>
                    <div class="stat-content">
                        <span class="stat-value">${stats.avgRating.toFixed(1)}</span>
                        <span class="stat-label">平均评分</span>
                    </div>
                </div>
                <div class="stat-card" onclick="AppActions.navigateTo('orders.html')" style="cursor: pointer;">
                    <div class="stat-icon"><i class="fas fa-percentage"></i></div>
                    <div class="stat-content">
                        <span class="stat-value">${stats.completionRate}%</span>
                        <span class="stat-label">完成率</span>
                    </div>
                </div>
            </div>
            <div style="text-align: center; padding: 20px;">
                <button class="btn btn-primary" onclick="AppActions.navigateTo('orders.html')">
                    <i class="fas fa-external-link-alt"></i> 查看全部订单
                </button>
            </div>
        </div>
    `;
}

function loadFavoritesContent() {
    const tab = document.querySelector('#my-favorites-tab .profile-section');
    if (!tab) return;

    const wishlist = AppState.wishlist;

    if (wishlist.length === 0) {
        tab.innerHTML = `
            <h3><i class="fas fa-heart"></i> 我的收藏</h3>
            <div class="empty-state" style="text-align: center; padding: 40px;">
                <i class="fas fa-heart" style="font-size: 48px; color: #d1d5db; margin-bottom: 16px;"></i>
                <p style="color: #6b7280;">还没有收藏的书籍</p>
                <p style="color: #9ca3af; font-size: 14px;">在书籍详情页点击"加入收藏"即可收藏</p>
                <button class="btn btn-primary" onclick="AppActions.navigateTo('buy.html')" style="margin-top: 16px;">
                    <i class="fas fa-shopping-cart"></i> 去逛逛
                </button>
            </div>
        `;
        return;
    }

    tab.innerHTML = `
        <h3><i class="fas fa-heart"></i> 我的收藏 (${wishlist.length})</h3>
        <div class="books-grid" style="margin-top: 20px;">
            ${wishlist.map(book => `
                <div class="book-card" onclick="AppActions.navigateTo('book-detail.html', {id: ${book.id}})" style="cursor: pointer;">
                    <div class="book-image">
                        <img src="${book.image}" alt="${book.title}">
                        <div class="book-condition">${book.condition}</div>
                    </div>
                    <div class="book-info">
                        <h3>${book.title}</h3>
                        <p class="book-author">${book.author}</p>
                        <div class="book-price">
                            <span class="price">¥${book.price.toFixed(2)}</span>
                        </div>
                        <button class="btn btn-outline btn-sm" onclick="event.stopPropagation(); AppActions.removeFromWishlist(${book.id}); loadFavoritesContent();">
                            <i class="fas fa-trash"></i> 取消收藏
                        </button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function loadSalesContent() {
    const tab = document.querySelector('#my-sales-tab .profile-section');
    if (!tab) return;

    tab.innerHTML = `
        <h3><i class="fas fa-tag"></i> 我的出售</h3>
        <div class="empty-state" style="text-align: center; padding: 40px;">
            <i class="fas fa-tag" style="font-size: 48px; color: #d1d5db; margin-bottom: 16px;"></i>
            <p style="color: #6b7280;">您还没有上架任何书籍</p>
            <p style="color: #9ca3af; font-size: 14px;">点击下方按钮开始出售您的二手书</p>
            <button class="btn btn-primary" onclick="AppActions.navigateTo('sell.html')" style="margin-top: 16px;">
                <i class="fas fa-plus"></i> 发布卖书
            </button>
        </div>
    `;
}

function initProfileEdit() {
    // 为个人信息添加编辑功能
    const detailItems = document.querySelectorAll('.detail-item');
    detailItems.forEach(item => {
        item.addEventListener('dblclick', function() {
            const value = this.querySelector('.detail-value');
            const label = this.querySelector('.detail-label')?.textContent;
            if (value && label !== '学号') {
                const current = value.textContent;
                const newValue = prompt(`编辑${label}`, current);
                if (newValue && newValue !== current) {
                    value.textContent = newValue;
                    AppActions.showToast(`${label}已更新`, 'success');
                }
            }
        });
        item.title = '双击编辑';
        item.style.cursor = 'pointer';
    });
}
