/**
 * 求书平台 - 订单页面脚本
 * 集成全局应用状态，实现订单页面交互功能
 */

document.addEventListener('DOMContentLoaded', function() {
    initOrdersPage();
});

function initOrdersPage() {
    // 更新订单统计
    updateOrderStats();

    // 渲染订单列表
    renderOrders();

    // 筛选标签点击
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            const status = this.dataset.status;
            renderOrders(status);
        });
    });

    // 搜索功能
    const searchInput = document.querySelector('.filter-search .search-input');
    const searchBtn = document.querySelector('.filter-search .btn-primary');
    
    if (searchInput && searchBtn) {
        const doSearch = function() {
            const query = searchInput.value.trim().toLowerCase();
            renderOrders('all', query);
        };
        searchBtn.addEventListener('click', doSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') doSearch();
        });
    }
}

function updateOrderStats() {
    const stats = AppActions.getOrderStats();
    
    const statEls = document.querySelectorAll('.orders-stats .stat-item strong');
    if (statEls.length >= 4) {
        statEls[0].textContent = stats.pending;
        statEls[1].textContent = stats.completed;
        statEls[2].textContent = stats.avgRating.toFixed(1);
        statEls[3].textContent = `${stats.completionRate}%`;
    }
}

function renderOrders(filterStatus = 'all', searchQuery = '') {
    let orders = [...AppState.orders];

    // 筛选状态
    if (filterStatus !== 'all') {
        orders = orders.filter(o => o.status === filterStatus);
    }

    // 搜索
    if (searchQuery) {
        orders = orders.filter(o =>
            o.orderNo.toLowerCase().includes(searchQuery) ||
            o.bookTitle.toLowerCase().includes(searchQuery) ||
            o.partner.toLowerCase().includes(searchQuery)
        );
    }

    // 分组
    const pendingOrders = orders.filter(o => o.status === 'pending' || o.status === 'confirmed' || o.status === 'delivery');
    const completedOrders = orders.filter(o => o.status === 'completed');
    const cancelledOrders = orders.filter(o => o.status === 'cancelled');

    // 渲染进行中订单
    const pendingSection = document.querySelector('.order-section:first-child .order-cards');
    if (pendingSection) {
        if (pendingOrders.length > 0) {
            pendingSection.innerHTML = pendingOrders.map(order => renderOrderCard(order)).join('');
        } else {
            pendingSection.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>暂无进行中的订单</p></div>';
        }
    }

    // 渲染已完成订单
    const completedSection = document.querySelectorAll('.order-section')[1]?.querySelector('.order-cards');
    if (completedSection) {
        if (completedOrders.length > 0) {
            completedSection.innerHTML = completedOrders.map(order => renderOrderCard(order)).join('');
        } else {
            completedSection.innerHTML = '<div class="empty-state"><i class="fas fa-check-circle"></i><p>暂无已完成订单</p></div>';
        }
    }

    // 渲染已取消订单
    const cancelledSection = document.querySelectorAll('.order-section')[2]?.querySelector('.order-cards');
    if (cancelledSection) {
        if (cancelledOrders.length > 0) {
            cancelledSection.innerHTML = cancelledOrders.map(order => renderOrderCard(order)).join('');
        } else {
            cancelledSection.innerHTML = '<div class="empty-state"><i class="fas fa-times-circle"></i><p>暂无已取消订单</p></div>';
        }
    }

    // 重新绑定事件
    bindOrderEvents();
}

function renderOrderCard(order) {
    const statusClass = order.status;
    const actions = getOrderActions(order);

    return `
        <div class="order-card status-${statusClass}" data-order-id="${order.id}">
            <div class="order-header">
                <div class="order-info">
                    <strong>订单号: ${order.orderNo}</strong>
                    <span class="order-time">创建时间: ${order.createdAt}</span>
                </div>
                <div class="order-status">
                    <span class="status-badge">${order.statusText}</span>
                </div>
            </div>
            <div class="order-content">
                <div class="order-book">
                    <div class="book-image">
                        <img src="${order.bookImage}" alt="${order.bookTitle}">
                    </div>
                    <div class="book-details">
                        <h4>${order.bookTitle}</h4>
                        <p>作者: ${order.bookAuthor}</p>
                        <p>ISBN: ${order.isbn}</p>
                    </div>
                </div>
                <div class="order-partner">
                    <div class="partner-info">
                        <i class="fas fa-user-circle"></i>
                        <div>
                            <strong>${order.partner}</strong>
                            <span>${order.partnerCampus} · 信誉等级: ${order.partnerReputation}</span>
                        </div>
                    </div>
                    <div class="partner-contact">
                        <button class="btn btn-outline btn-sm contact-btn">
                            <i class="fas fa-comment"></i> 联系${order.status === 'completed' ? '对方' : '卖家'}
                        </button>
                    </div>
                </div>
                <div class="order-details">
                    <div class="detail-item">
                        <span>价格</span>
                        <strong>¥${order.price.toFixed(2)}</strong>
                    </div>
                    <div class="detail-item">
                        <span>交易方式</span>
                        <strong>${order.tradeMethod}</strong>
                    </div>
                    <div class="detail-item">
                        <span>校区</span>
                        <strong>${order.campus}</strong>
                    </div>
                </div>
            </div>
            <div class="order-actions">
                ${actions}
            </div>
        </div>
    `;
}

function getOrderActions(order) {
    switch(order.status) {
        case 'pending':
            return `
                <button class="btn btn-outline cancel-order-btn">
                    <i class="fas fa-times"></i> 取消订单
                </button>
                <button class="btn btn-primary confirm-order-btn">
                    <i class="fas fa-check"></i> 确认交易
                </button>
            `;
        case 'confirmed':
            return `
                <button class="btn btn-outline cancel-order-btn">
                    <i class="fas fa-times"></i> 取消订单
                </button>
                <button class="btn btn-primary confirm-delivery-btn">
                    <i class="fas fa-truck"></i> 确认交付
                </button>
            `;
        case 'completed':
            return `
                <button class="btn btn-outline view-detail-btn">
                    <i class="fas fa-eye"></i> 查看详情
                </button>
                <button class="btn btn-primary rate-order-btn">
                    <i class="fas fa-star"></i> 评价订单
                </button>
            `;
        case 'cancelled':
            return `
                <button class="btn btn-outline view-detail-btn">
                    <i class="fas fa-eye"></i> 查看详情
                </button>
                <button class="btn btn-outline relist-btn">
                    <i class="fas fa-redo"></i> 重新上架
                </button>
            `;
        default:
            return `
                <button class="btn btn-outline view-detail-btn">
                    <i class="fas fa-eye"></i> 查看详情
                </button>
            `;
    }
}

function bindOrderEvents() {
    // 联系卖家/买家
    document.querySelectorAll('.contact-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            AppActions.navigateTo('messages.html');
        });
    });

    // 取消订单
    document.querySelectorAll('.cancel-order-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (confirm('确定要取消该订单吗？')) {
                const card = this.closest('.order-card');
                const orderId = parseInt(card?.dataset.orderId);
                if (orderId) {
                    AppActions.updateOrderStatus(orderId, 'cancelled', '已取消');
                    renderOrders();
                    AppActions.showToast('订单已取消', 'info');
                }
            }
        });
    });

    // 确认交易
    document.querySelectorAll('.confirm-order-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const card = this.closest('.order-card');
            const orderId = parseInt(card?.dataset.orderId);
            if (orderId) {
                AppActions.updateOrderStatus(orderId, 'confirmed', '待确认');
                renderOrders();
                AppActions.showToast('交易已确认，请等待交付', 'success');
            }
        });
    });

    // 确认交付
    document.querySelectorAll('.confirm-delivery-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const card = this.closest('.order-card');
            const orderId = parseInt(card?.dataset.orderId);
            if (orderId) {
                AppActions.updateOrderStatus(orderId, 'completed', '已完成');
                renderOrders();
                AppActions.showToast('交易已完成！请对本次交易进行评价', 'success');
            }
        });
    });

    // 查看详情
    document.querySelectorAll('.view-detail-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const card = this.closest('.order-card');
            const orderId = parseInt(card?.dataset.orderId);
            const order = AppState.orders.find(o => o.id === orderId);
            if (order) {
                AppActions.showToast(`订单 ${order.orderNo}: ${order.statusText}`, 'info');
            }
        });
    });

    // 评价订单
    document.querySelectorAll('.rate-order-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            AppActions.showToast('感谢您的评价！您的反馈帮助我们做得更好', 'success');
        });
    });

    // 重新上架
    document.querySelectorAll('.relist-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            AppActions.navigateTo('publish-sell.html');
        });
    });
}

// 全局函数（供HTML onclick调用）
function cancelOrder(orderId) {
    if (confirm('确定要取消该订单吗？')) {
        AppActions.updateOrderStatus(orderId, 'cancelled', '已取消');
        renderOrders();
        AppActions.showToast('订单已取消', 'info');
    }
}

function confirmOrder(orderId) {
    AppActions.updateOrderStatus(orderId, 'confirmed', '待确认');
    renderOrders();
    AppActions.showToast('交易已确认，请等待交付', 'success');
}

function confirmDelivery(orderId) {
    AppActions.updateOrderStatus(orderId, 'completed', '已完成');
    renderOrders();
    AppActions.showToast('交易已完成！请对本次交易进行评价', 'success');
}

function viewOrderDetails(orderId) {
    const order = AppState.orders.find(o => o.id === orderId);
    if (order) {
        AppActions.showToast(`订单 ${order.orderNo}: ${order.statusText}`, 'info');
    }
}

function rateOrder(orderId) {
    AppActions.showToast('感谢您的评价！您的反馈帮助我们做得更好', 'success');
}

function relistBook(orderId) {
    AppActions.navigateTo('publish-sell.html');
}
