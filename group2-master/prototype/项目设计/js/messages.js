/**
 * 求书平台 - 消息中心脚本
 * 集成全局应用状态，实现消息中心交互功能
 */

document.addEventListener('DOMContentLoaded', function() {
    initMessagesPage();
});

function initMessagesPage() {
    // 更新未读消息统计
    updateMessageStats();

    // 会话列表点击
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.addEventListener('click', function() {
            // 切换active状态
            document.querySelectorAll('.conversation-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            // 标记已读
            const name = this.querySelector('.conversation-header strong')?.textContent;
            if (name) {
                AppActions.markConversationRead(name);
                updateMessageStats();
            }
        });
    });

    // 发送消息
    const sendBtn = document.querySelector('.send-btn');
    const messageInput = document.getElementById('messageInput');

    if (sendBtn && messageInput) {
        sendBtn.addEventListener('click', function() {
            sendMessage();
        });

        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // 创建订单按钮
    const createOrderBtn = document.querySelector('.input-actions .btn-outline');
    if (createOrderBtn) {
        createOrderBtn.addEventListener('click', function() {
            const activeConv = document.querySelector('.conversation-item.active');
            const partnerName = activeConv?.querySelector('.conversation-header strong')?.textContent || '卖家';
            const bookTitle = activeConv?.querySelector('.book-title')?.textContent || '书籍';

            const book = AppState.books.find(b => b.title === bookTitle);
            if (book) {
                AppActions.createOrder(book, {
                    name: partnerName,
                    campus: book.campus,
                    reputation: book.sellerReputation
                });
                AppActions.showToast(`已创建订单，请等待${partnerName}确认`, 'success');
            }
        });
    }

    // 确认交易按钮
    const confirmBtn = document.querySelector('.input-actions .btn-primary');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            AppActions.showToast('交易已确认，请等待对方完成交付', 'success');
        });
    }

    // 查看订单按钮
    const viewOrderBtn = document.querySelector('.chat-actions .btn-outline:first-child');
    if (viewOrderBtn) {
        viewOrderBtn.addEventListener('click', function() {
            AppActions.navigateTo('orders.html');
        });
    }

    // 举报按钮
    const reportBtn = document.querySelector('.chat-actions .btn-outline:nth-child(2)');
    if (reportBtn) {
        reportBtn.addEventListener('click', function() {
            AppActions.showToast('已收到您的举报，平台将在24小时内处理', 'info');
        });
    }

    // 屏蔽按钮
    const blockBtn = document.querySelector('.chat-actions .btn-danger');
    if (blockBtn) {
        blockBtn.addEventListener('click', function() {
            if (confirm('确定要屏蔽该用户吗？')) {
                AppActions.showToast('已屏蔽该用户', 'info');
            }
        });
    }

    // 新会话按钮
    const newConvBtn = document.querySelector('.sidebar-header .btn-outline');
    if (newConvBtn) {
        newConvBtn.addEventListener('click', function() {
            const name = prompt('请输入对方姓名：');
            if (name) {
                AppActions.showToast(`已创建与${name}的新会话`, 'success');
            }
        });
    }
}

function updateMessageStats() {
    const unreadEl = document.querySelector('.messages-stats .stat-item:first-child strong');
    const activeEl = document.querySelector('.messages-stats .stat-item:nth-child(2) strong');

    if (unreadEl) {
        unreadEl.textContent = AppActions.getUnreadCount();
    }
    if (activeEl) {
        const active = document.querySelectorAll('.conversation-item:not(.completed)').length;
        activeEl.textContent = active;
    }
}

// 全局函数（供HTML onclick调用）
function sendMessage() {
    const input = document.getElementById('messageInput');
    if (!input || !input.value.trim()) return;

    const text = input.value.trim();
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    // 添加发送的消息
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message sent-message';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
        <div class="message-avatar">
            <i class="fas fa-user-circle"></i>
        </div>
    `;
    chatMessages.appendChild(messageDiv);

    // 清空输入
    input.value = '';

    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // 模拟对方回复
    setTimeout(() => {
        const replyDiv = document.createElement('div');
        replyDiv.className = 'message received-message';
        replyDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user-circle"></i>
            </div>
            <div class="message-content">
                <div class="message-text">好的，收到您的消息，我会尽快回复您！</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        `;
        chatMessages.appendChild(replyDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 1000);
}

function startNewConversation() {
    const name = prompt('请输入对方姓名：');
    if (name) {
        AppActions.showToast(`已创建与${name}的新会话`, 'success');
    }
}

function viewOrderDetails() {
    AppActions.navigateTo('orders.html');
}

function reportUser() {
    AppActions.showToast('已收到您的举报，平台将在24小时内处理', 'info');
}

function blockUser() {
    if (confirm('确定要屏蔽该用户吗？')) {
        AppActions.showToast('已屏蔽该用户', 'info');
    }
}

function createOrder() {
    const activeConv = document.querySelector('.conversation-item.active');
    const partnerName = activeConv?.querySelector('.conversation-header strong')?.textContent || '卖家';
    const bookTitle = activeConv?.querySelector('.book-title')?.textContent || '书籍';

    const book = AppState.books.find(b => b.title === bookTitle);
    if (book) {
        AppActions.createOrder(book, {
            name: partnerName,
            campus: book.campus,
            reputation: book.sellerReputation
        });
        AppActions.showToast(`已创建订单，请等待${partnerName}确认`, 'success');
    }
}

function confirmTransaction() {
    AppActions.showToast('交易已确认，请等待对方完成交付', 'success');
}

// 交易确认卡片相关功能
let currentTradeCardId = null;

// 显示交易确认弹窗
function showTradeModal() {
    // 从商品信息条获取书籍信息
    const bookNameEl = document.querySelector('.book-name');
    const priceEl = document.querySelector('.product-price');
    
    if (bookNameEl) {
        document.getElementById('tradeBookName').value = bookNameEl.textContent.trim();
    }
    if (priceEl) {
        const price = priceEl.textContent.replace(/[^\d.]/g, '');
        document.getElementById('tradePrice').value = price;
    }
    
    // 设置默认交易时间为明天当前时间
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setMinutes(0);
    const timeStr = tomorrow.toISOString().slice(0, 16);
    document.getElementById('tradeTime').value = timeStr;
    
    document.getElementById('tradeModal').style.display = 'block';
}

// 关闭弹窗
function closeTradeModal() {
    document.getElementById('tradeModal').style.display = 'none';
}

// 发送交易确认卡片
function sendTradeCard() {
    const price = document.getElementById('tradePrice').value;
    const location = document.getElementById('tradeLocation').value;
    const time = document.getElementById('tradeTime').value;
    
    // 表单验证
    if (!price || parseFloat(price) <= 0) {
        alert('请输入有效的成交价格');
        return;
    }
    if (!location.trim()) {
        alert('请输入交易地点');
        return;
    }
    if (!time) {
        alert('请选择交易时间');
        return;
    }
    
    const cardData = {
        id: 'TC' + Date.now(),
        type: 'trade_card',
        bookName: document.getElementById('tradeBookName').value,
        price: price,
        tradeType: document.getElementById('tradeType').value,
        location: location,
        time: time,
        note: document.getElementById('tradeNote').value,
        status: 'pending', // pending/confirmed/rejected
        sender: 'me',
        createTime: new Date().toLocaleString('zh-CN')
    };
    
    // 保存到 localStorage
    saveTradeCard(cardData);
    
    // 添加到聊天界面
    renderTradeCard(cardData, 'sent');
    closeTradeModal();
    
    // 清空表单
    document.getElementById('tradeLocation').value = '';
    document.getElementById('tradeNote').value = '';
}

// 保存交易卡片到 localStorage
function saveTradeCard(cardData) {
    const conversationId = getCurrentConversationId();
    const key = 'trade_cards_' + conversationId;
    const existing = JSON.parse(localStorage.getItem(key) || '[]');
    existing.push(cardData);
    localStorage.setItem(key, JSON.stringify(existing));
}

// 获取当前会话ID
function getCurrentConversationId() {
    const activeItem = document.querySelector('.conversation-item.active');
    if (activeItem) {
        const onclick = activeItem.getAttribute('onclick');
        const match = onclick.match(/selectConversation\(this,\s*['"](\w+)['"]\)/);
        return match ? match[1] : 'default';
    }
    return 'default';
}

// 渲染交易卡片消息
function renderTradeCard(data, direction) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const tradeTypeText = data.tradeType === 'face' ? '当面交易' : '邮寄';
    const timeStr = data.time ? new Date(data.time).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }) : '';
    
    const statusConfig = {
        pending: { text: '等待对方确认', class: 'status-pending' },
        confirmed: { text: '已确认', class: 'status-confirmed' },
        rejected: { text: '已拒绝', class: 'status-rejected' }
    };
    const status = statusConfig[data.status] || statusConfig.pending;
    
    // 判断当前用户是否是发送方
    const isSender = data.sender === 'me';
    const showActions = data.status === 'pending' && !isSender;
    
    const cardHTML = `
        <div class="trade-card-message" data-card-id="${data.id}">
            <div class="trade-card-header">
                <i class="fas fa-clipboard-check"></i>
                <span>交易确认单</span>
            </div>
            <div class="trade-card-content">
                <p><span class="label">书籍：</span>${data.bookName}</p>
                <p><span class="label">价格：</span>¥${data.price}</p>
                <p><span class="label">方式：</span>${tradeTypeText}</p>
                ${data.location ? `<p><span class="label">地点：</span>${data.location}</p>` : ''}
                ${timeStr ? `<p><span class="label">时间：</span>${timeStr}</p>` : ''}
                ${data.note ? `<p><span class="label">备注：</span>${data.note}</p>` : ''}
            </div>
            <div class="trade-card-status ${status.class}">
                ${status.text}
            </div>
            ${showActions ? `
                <div class="trade-card-actions">
                    <button class="btn-confirm" onclick="confirmTradeCard('${data.id}')">确认交易</button>
                    <button class="btn-reject" onclick="rejectTradeCard('${data.id}')">拒绝</button>
                </div>
            ` : ''}
        </div>
    `;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${direction === 'sent' ? 'sent' : 'received'}`;
    
    if (direction === 'sent') {
        messageDiv.innerHTML = `
            <div>
                ${cardHTML}
                <div class="message-time">${new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'})}</div>
            </div>
            <div class="message-avatar">
                <i class="fas fa-user-circle"></i>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-user-circle"></i>
            </div>
            <div>
                ${cardHTML}
                <div class="message-time">${new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'})}</div>
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 确认交易卡片
function confirmTradeCard(cardId) {
    updateTradeCardStatus(cardId, 'confirmed');
    if (typeof AppActions !== 'undefined' && AppActions.showToast) {
        AppActions.showToast('交易已确认，请按时完成交易', 'success');
    } else {
        alert('交易已确认，请按时完成交易');
    }
}

// 拒绝交易卡片
function rejectTradeCard(cardId) {
    updateTradeCardStatus(cardId, 'rejected');
    if (typeof AppActions !== 'undefined' && AppActions.showToast) {
        AppActions.showToast('已拒绝交易，可与对方重新协商', 'info');
    } else {
        alert('已拒绝交易，可与对方重新协商');
    }
}

// 更新交易卡片状态
function updateTradeCardStatus(cardId, status) {
    const conversationId = getCurrentConversationId();
    const key = 'trade_cards_' + conversationId;
    const cards = JSON.parse(localStorage.getItem(key) || '[]');
    
    const card = cards.find(c => c.id === cardId);
    if (card) {
        card.status = status;
        localStorage.setItem(key, JSON.stringify(cards));
        
        // 更新UI
        const cardEl = document.querySelector(`[data-card-id="${cardId}"]`);
        if (cardEl) {
            const statusEl = cardEl.querySelector('.trade-card-status');
            const actionsEl = cardEl.querySelector('.trade-card-actions');
            
            const statusConfig = {
                confirmed: { text: '已确认', class: 'status-confirmed' },
                rejected: { text: '已拒绝', class: 'status-rejected' }
            };
            
            if (statusConfig[status]) {
                statusEl.className = `trade-card-status ${statusConfig[status].class}`;
                statusEl.textContent = statusConfig[status].text;
            }
            
            if (actionsEl) {
                actionsEl.remove();
            }
        }
    }
}

// 加载历史交易卡片
function loadTradeCards() {
    const conversationId = getCurrentConversationId();
    const key = 'trade_cards_' + conversationId;
    const cards = JSON.parse(localStorage.getItem(key) || '[]');
    
    cards.forEach(card => {
        renderTradeCard(card, card.sender === 'me' ? 'sent' : 'received');
    });
}

// 工具函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getCurrentTime() {
    const now = new Date();
    return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 加载历史交易卡片
    setTimeout(loadTradeCards, 100);
});
