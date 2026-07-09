/**
 * 求书平台 - 书籍详情页脚本
 * 集成全局应用状态，实现书籍详情页交互功能
 */

document.addEventListener('DOMContentLoaded', function() {
    initBookDetail();
});

function initBookDetail() {
    // 获取URL参数中的书籍ID
    const params = AppActions.getUrlParams();
    const bookId = params.id || 1;
    
    // 加载书籍数据
    const book = AppActions.getBookDetail(bookId);
    if (book) {
        renderBookDetail(book);
        AppActions.addBrowsingHistory(book);
    }

    // 绑定交易控制台按钮
    const buyNowBtn = document.getElementById('buyNowBtn');
    const chatSellerBtn = document.getElementById('chatSellerBtn');
    const addToCartBtn = document.getElementById('addToCartBtn');
    const addToWishlistBtn = document.getElementById('addToWishlistBtn');
    const viewHistoryBtn = document.getElementById('viewHistoryBtn');
    const closeModalBtn = document.getElementById('closeModalBtn');

    if (buyNowBtn) {
        buyNowBtn.addEventListener('click', function() {
            const book = AppActions.getBookDetail(bookId);
            if (book) {
                // 创建订单并跳转到消息中心
                const order = AppActions.createOrder(book, {
                    name: book.seller,
                    campus: book.campus,
                    reputation: book.sellerReputation
                });
                AppActions.showToast(`已创建订单 ${order.orderNo}，请与卖家沟通`, 'success');
                setTimeout(() => {
                    AppActions.navigateTo('messages.html');
                }, 1000);
            }
        });
    }

    if (chatSellerBtn) {
        chatSellerBtn.addEventListener('click', function() {
            AppActions.navigateTo('messages.html');
        });
    }

    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
            const book = AppActions.getBookDetail(bookId);
            if (book) AppActions.addToCart(book);
        });
    }

    if (addToWishlistBtn) {
        addToWishlistBtn.addEventListener('click', function() {
            const book = AppActions.getBookDetail(bookId);
            if (book) AppActions.addToWishlist(book);
        });
    }

    if (viewHistoryBtn) {
        viewHistoryBtn.addEventListener('click', function() {
            const modal = document.getElementById('historyModal');
            if (modal) modal.style.display = 'flex';
        });
    }

    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', function() {
            const modal = document.getElementById('historyModal');
            if (modal) modal.style.display = 'none';
        });
    }

    // 点击模态框外部关闭
    window.addEventListener('click', function(e) {
        const modal = document.getElementById('historyModal');
        if (modal && e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // 关联资料下载按钮
    document.querySelectorAll('.material-card .btn-primary').forEach(btn => {
        btn.addEventListener('click', function() {
            const materialName = this.closest('.material-info')?.querySelector('h3')?.textContent || '资料';
            AppActions.showToast(`正在下载《${materialName}》...`, 'info');
        });
    });
}

function renderBookDetail(book) {
    // 更新页面标题
    document.title = `${book.title} - 求书平台`;

    // 更新面包屑
    const breadcrumb = document.querySelector('.breadcrumb');
    if (breadcrumb) {
        const lastSpan = breadcrumb.querySelector('span');
        if (lastSpan) lastSpan.textContent = book.title;
    }

    // 更新书籍主图
    const mainImage = document.querySelector('.book-image-large img');
    if (mainImage) {
        mainImage.src = book.image;
        mainImage.alt = book.title;
    }

    // 更新书籍徽章
    const badges = document.querySelector('.book-badges');
    if (badges) {
        badges.innerHTML = `
            <span class="badge condition">${book.condition}</span>
            ${book.hasNotes ? '<span class="badge notes"><i class="fas fa-sticky-note"></i> 有详细笔记</span>' : ''}
            <span class="badge campus"><i class="fas fa-map-marker-alt"></i> ${book.campus}</span>
        `;
    }

    // 更新标题
    const titleEl = document.querySelector('.book-basic-info h1');
    if (titleEl) titleEl.textContent = book.title;

    // 更新作者
    const authorEl = document.querySelector('.meta-item:nth-child(1) .meta-value');
    if (authorEl) authorEl.textContent = book.author;

    // 更新出版社
    const publisherEl = document.querySelector('.meta-item:nth-child(2) .meta-value');
    if (publisherEl) publisherEl.textContent = book.publisher;

    // 更新ISBN
    const isbnEl = document.querySelector('.meta-item:nth-child(3) .meta-value');
    if (isbnEl) isbnEl.textContent = book.isbn;

    // 更新卖家信息
    const sellerName = document.querySelector('.seller-text h4');
    if (sellerName) sellerName.textContent = book.seller;

    const reputationEl = document.querySelector('.reputation');
    if (reputationEl) {
        reputationEl.innerHTML = `<i class="fas fa-star"></i> 信誉等级: ${book.sellerReputation}`;
    }

    // 更新价格
    const priceAmount = document.querySelector('.price-amount');
    if (priceAmount) priceAmount.textContent = `¥${book.price.toFixed(2)}`;

    const originalPrice = document.querySelector('.current-price .original-price');
    if (originalPrice) originalPrice.textContent = `原价: ¥${book.originalPrice.toFixed(2)}`;

    // 更新节省百分比
    const savings = document.querySelector('.price-savings span');
    if (savings && book.originalPrice > 0) {
        const savedPercent = Math.round((1 - book.price / book.originalPrice) * 100);
        savings.textContent = `节省 ${savedPercent}%`;
    }

    // 更新书籍描述
    const descList = document.querySelector('.condition-details ul');
    if (descList) {
        descList.innerHTML = `
            <li><i class="fas fa-check-circle"></i> ${book.description}</li>
            <li><i class="fas fa-check-circle"></i> 无缺页、无涂鸦</li>
            <li><i class="fas fa-check-circle"></i> 书脊牢固，无松动</li>
        `;
    }

    // 更新卖家留言
    const notesContent = document.querySelector('.notes-content');
    if (notesContent) {
        notesContent.innerHTML = `
            <p>"这本书是我大二时的教材，我在上面做了详细的笔记，包括重点概念和考试重点。</p>
            <p>由于我已经升入大三，不再需要这本教材，希望它能帮助到正在学习的学弟学妹们。书保存得很好，除了我自己的笔记外，没有其他涂写。"</p>
        `;
    }
}
