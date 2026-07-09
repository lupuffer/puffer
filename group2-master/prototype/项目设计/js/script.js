/**
 * 求书平台 - 首页脚本
 * 集成全局应用状态，实现首页交互功能
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化首页特定功能
    initHomePage();
});

function initHomePage() {
    // 为"查看相关二手书"按钮添加跳转
    document.querySelectorAll('.course-card .btn-primary').forEach(btn => {
        btn.addEventListener('click', function() {
            const courseCard = this.closest('.course-card');
            const courseName = courseCard.querySelector('h3').textContent;
            AppActions.navigateTo('buy.html', { q: courseName });
        });
    });

    // 为书籍卡片添加点击跳转到详情页
    document.querySelectorAll('.book-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // 如果点击的是按钮，不触发
            if (e.target.closest('button')) return;
            
            const title = this.querySelector('.book-info h3')?.textContent || '';
            const book = AppState.books.find(b => b.title === title);
            if (book) {
                AppActions.addBrowsingHistory(book);
                AppActions.navigateTo('book-detail.html', { id: book.id });
            }
        });
        card.style.cursor = 'pointer';
    });

    // 筛选标签点击
    document.querySelectorAll('.filter-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            // 切换active状态
            this.closest('.filter-tags')?.querySelectorAll('.filter-tag').forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            // 根据标签筛选
            const category = this.textContent.trim();
            if (category !== '全部') {
                const filtered = AppActions.filterBooks({ category: category });
                renderFilteredBooks(filtered);
            } else {
                renderFilteredBooks(AppState.books);
            }
        });
    });

    // 初始渲染所有书籍
    renderFilteredBooks(AppState.books);
}

function renderFilteredBooks(books) {
    const grid = document.querySelector('.books-grid');
    if (!grid) return;

    grid.innerHTML = books.map(book => `
        <div class="book-card" data-id="${book.id}">
            <div class="book-image">
                <img src="${book.image}" alt="${book.title}">
                <div class="book-condition">${book.condition}</div>
                ${book.hasNotes ? '<div class="book-notes"><i class="fas fa-sticky-note"></i> 有笔记</div>' : ''}
            </div>
            <div class="book-info">
                <h3>${book.title}</h3>
                <p class="book-author">${book.author}</p>
                <div class="book-meta">
                    <span><i class="fas fa-map-marker-alt"></i> ${book.campus}</span>
                </div>
                <div class="book-price">
                    <span class="price">¥${book.price.toFixed(2)}</span>
                    <button class="btn btn-primary btn-sm">查看详情</button>
                </div>
                <div class="book-seller">
                    <i class="fas fa-user-circle"></i>
                    <span>${book.seller} · 信誉等级: ${book.sellerReputation}</span>
                </div>
            </div>
        </div>
    `).join('');

    // 重新绑定点击事件
    grid.querySelectorAll('.book-card').forEach(card => {
        card.addEventListener('click', function() {
            const bookId = parseInt(this.dataset.id);
            const book = AppState.books.find(b => b.id === bookId);
            if (book) {
                AppActions.addBrowsingHistory(book);
                AppActions.navigateTo('book-detail.html', { id: book.id });
            }
        });
        card.style.cursor = 'pointer';
    });
}
