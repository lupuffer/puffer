/**
 * 求书平台 - AI客服助手脚本
 * 集成全局应用状态，实现AI客服交互功能
 */

document.addEventListener('DOMContentLoaded', function() {
    initAIChatbot();
});

function initAIChatbot() {
    // 发送消息
    const sendBtn = document.querySelector('.send-btn');
    const messageInput = document.getElementById('messageInput');

    if (sendBtn && messageInput) {
        sendBtn.addEventListener('click', function() {
            sendAIMessage();
        });

        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendAIMessage();
            }
        });
    }

    // 快捷提问按钮
    document.querySelectorAll('.quick-question-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const text = this.textContent.trim();
            // 提取问题文本
            const question = this.getAttribute('onclick')?.match(/'([^']+)'/)?.[1] || text;
            if (messageInput) {
                messageInput.value = question;
                sendAIMessage();
            }
        });
    });

    // 智能推荐按钮
    const recommendBtn = document.querySelector('.course-match .btn-primary');
    if (recommendBtn) {
        recommendBtn.addEventListener('click', function() {
            if (messageInput) {
                messageInput.value = '根据我的专业推荐教材';
                sendAIMessage();
            }
        });
    }

    // 查看推荐按钮
    const viewRecommendBtn = document.querySelector('.recommendation-card .btn-outline');
    if (viewRecommendBtn) {
        viewRecommendBtn.addEventListener('click', function() {
            AppActions.navigateTo('buy.html');
        });
    }

    // 生成示例推荐
    const generateBtn = document.querySelector('.results-controls .btn-outline');
    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            generateMockRecommendations();
        });
    }

    // 导出清单
    const exportBtn = document.querySelector('.results-controls .btn-primary');
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            AppActions.showToast('正在导出推荐清单...', 'info');
            setTimeout(() => {
                AppActions.showToast('推荐清单已导出', 'success');
            }, 1000);
        });
    }

    // 课表上传
    const uploadZone = document.getElementById('uploadZone');
    const timetableFile = document.getElementById('timetableFile');

    if (uploadZone && timetableFile) {
        uploadZone.addEventListener('click', () => timetableFile.click());

        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = 'var(--primary-blue)';
            uploadZone.style.backgroundColor = 'var(--light-blue)';
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.style.borderColor = '';
            uploadZone.style.backgroundColor = '';
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = '';
            uploadZone.style.backgroundColor = '';
            AppActions.showToast('课表上传成功！AI正在分析中...', 'success');
            setTimeout(() => {
                generateMockRecommendations();
            }, 2000);
        });

        timetableFile.addEventListener('change', function() {
            if (this.files.length > 0) {
                AppActions.showToast('课表上传成功！AI正在分析中...', 'success');
                setTimeout(() => {
                    generateMockRecommendations();
                }, 2000);
            }
        });
    }

    // 转接人工客服
    const transferBtn = document.querySelector('.support-option:first-child');
    if (transferBtn) {
        transferBtn.addEventListener('click', function() {
            transferToHuman();
        });
    }

    // 常见问题
    const faqBtn = document.querySelectorAll('.support-option')[1];
    if (faqBtn) {
        faqBtn.addEventListener('click', function() {
            showFAQ();
        });
    }

    // 使用教程
    const tutorialBtn = document.querySelectorAll('.support-option')[2];
    if (tutorialBtn) {
        tutorialBtn.addEventListener('click', function() {
            showTutorial();
        });
    }

    // 服务评价
    document.querySelectorAll('.rating-stars i').forEach(star => {
        star.addEventListener('click', function() {
            const rating = parseInt(this.getAttribute('onclick')?.match(/\d+/)?.[0] || 5);
            rateService(rating);
        });
    });

    // 反馈按钮
    const feedbackBtn = document.querySelector('.rating-section .btn-outline');
    if (feedbackBtn) {
        feedbackBtn.addEventListener('click', function() {
            showFeedbackForm();
        });
    }
}

function sendAIMessage() {
    const input = document.getElementById('messageInput');
    if (!input || !input.value.trim()) return;

    const text = input.value.trim();
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    // 移除快捷问题区域
    const quickQuestions = chatMessages.querySelector('.quick-questions');
    if (quickQuestions) quickQuestions.remove();

    // 添加用户消息
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.innerHTML = `
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
        <div class="message-avatar">
            <i class="fas fa-user-circle"></i>
        </div>
    `;
    chatMessages.appendChild(userDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    input.value = '';

    // 模拟AI回复
    setTimeout(() => {
        const reply = getAIResponse(text);
        const botDiv = document.createElement('div');
        botDiv.className = 'message bot-message';
        botDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${reply}</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        `;
        chatMessages.appendChild(botDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 800 + Math.random() * 500);
}

function getAIResponse(question) {
    const q = question.toLowerCase();
    
    if (q.includes('发布') && q.includes('卖书')) {
        return `📚 <strong>发布卖书指南：</strong><br><br>
        1. 点击导航栏"我要卖书"<br>
        2. 选择录入方式（扫码/手动输入ISBN/从购买历史选择）<br>
        3. 填写书籍信息（书名、作者、ISBN、价格等）<br>
        4. 选择交易方式和校区<br>
        5. 上传书籍实拍照片<br>
        6. 点击"提交发布"<br><br>
        💡 提示：填写ISBN后系统会自动填充书籍信息哦！`;
    }
    
    if (q.includes('数据结构') || q.includes('课程') && q.includes('教材')) {
        const books = AppState.books.filter(b => b.category === '计算机科学');
        let reply = `📖 <strong>为您推荐以下教材：</strong><br><br>`;
        books.forEach((b, i) => {
            reply += `${i + 1}. 《${b.title}》- ${b.author}<br>`;
            reply += `   💰 ¥${b.price.toFixed(2)} | 📍 ${b.campus} | ⭐ ${b.rating}分<br>`;
            reply += `   <button class="btn btn-primary btn-sm" onclick="AppActions.navigateTo('book-detail.html', {id: ${b.id}})">查看详情</button><br><br>`;
        });
        reply += `💡 您也可以到<a href="buy.html" style="color: var(--primary-blue);">我要买书</a>页面查看更多选择！`;
        return reply;
    }
    
    if (q.includes('联系') && q.includes('卖家')) {
        return `💬 <strong>联系卖家方式：</strong><br><br>
        1. 在书籍详情页点击"私聊卖家"按钮<br>
        2. 进入消息中心与卖家沟通<br>
        3. 通过平台站内信协商交易细节<br><br>
        🔒 建议使用平台内置聊天工具沟通，保障交易安全！`;
    }
    
    if (q.includes('安全') || q.includes('交易安全')) {
        return `🛡️ <strong>平台交易安全保障：</strong><br><br>
        ✅ 浙大实名认证，确保用户真实身份<br>
        ✅ 所有交易通过平台担保，资金安全有保障<br>
        ✅ 平台内置聊天工具，保留沟通记录<br>
        ✅ 交易纠纷可申请平台介入处理<br>
        ✅ 信誉评价系统，帮助您选择可靠的交易对象<br><br>
        💪 我们致力于为您提供安全、可靠的交易环境！`;
    }
    
    if (q.includes('订单') || q.includes('查看')) {
        return `📋 <strong>查看订单方法：</strong><br><br>
        1. 点击导航栏"个人中心"<br>
        2. 选择"我的订单"标签<br>
        3. 可按状态筛选（待沟通/待确认/待交付/已完成）<br><br>
        🔗 点击下方按钮直接查看：<br>
        <button class="btn btn-primary btn-sm" onclick="AppActions.navigateTo('orders.html')">查看我的订单</button>`;
    }
    
    if (q.includes('转接') || q.includes('人工') || q.includes('真人')) {
        return `👨‍💼 <strong>正在为您转接人工客服...</strong><br><br>
        当前排队人数：<strong>2人</strong><br>
        预计等待时间：<strong>约2分钟</strong><br><br>
        转接后您可以：<br>
        📞 咨询复杂问题<br>
        ⚠️ 反馈平台问题<br>
        💡 提出建议意见<br><br>
        <em>请稍候，客服人员即将接入...</em>`;
    }
    
    if (q.includes('高等数学') || q.includes('数学')) {
        const books = AppState.books.filter(b => b.category === '数学');
        let reply = `📖 <strong>为您推荐以下数学教材：</strong><br><br>`;
        books.forEach((b, i) => {
            reply += `${i + 1}. 《${b.title}》- ${b.author}<br>`;
            reply += `   💰 ¥${b.price.toFixed(2)} | 📍 ${b.campus} | ⭐ ${b.rating}分<br>`;
            reply += `   <button class="btn btn-primary btn-sm" onclick="AppActions.navigateTo('book-detail.html', {id: ${b.id}})">查看详情</button><br><br>`;
        });
        return reply;
    }
    
    if (q.includes('你好') || q.includes('您好') || q.includes('嗨')) {
        return `您好！😊 很高兴为您服务！<br><br>
        请问有什么可以帮助您的？您可以：<br>
        📚 查询特定教材的二手信息<br>
        🔍 根据课程推荐教材<br>
        💰 了解价格参考<br>
        📝 获取平台使用指导<br><br>
        或者直接点击下方的快捷问题，快速获取答案！`;
    }

    // 默认回复
    const defaultReplies = [
        `感谢您的提问！🤔<br><br>关于"${question}"，我建议您可以：<br><br>
        1. 📚 在<a href="buy.html" style="color: var(--primary-blue);">我要买书</a>页面搜索相关书籍<br>
        2. 💬 在消息中心联系卖家咨询详情<br>
        3. 📋 查看<a href="orders.html" style="color: var(--primary-blue);">我的订单</a>了解交易状态<br><br>
        如果还有其他问题，随时问我哦！`,
        
        `收到您的问题！😊<br><br>
        为了更好地帮助您，我建议：<br><br>
        🔍 在搜索框中输入具体书名或ISBN<br>
        📖 浏览<a href="buy.html" style="color: var(--primary-blue);">二手书列表</a>查看所有在售书籍<br>
        💡 查看<a href="knowledge.html" style="color: var(--primary-blue);">知识遗产社区</a>获取学习资料<br><br>
        或者您可以换一种方式描述您的问题~`,
        
        `好的，让我来帮您！👍<br><br>
        关于"${question}"，您可以尝试以下操作：<br><br>
        1. 使用首页的搜索功能查找相关书籍<br>
        2. 在<a href="buy.html" style="color: var(--primary-blue);">我要买书</a>页面使用筛选功能<br>
        3. 查看<a href="profile.html" style="color: var(--primary-blue);">个人中心</a>管理您的交易<br><br>
        如果问题仍未解决，可以转接人工客服哦！`
    ];
    
    return defaultReplies[Math.floor(Math.random() * defaultReplies.length)];
}

// 全局函数
function askQuickQuestion(question) {
    const input = document.getElementById('messageInput');
    if (input) {
        input.value = question;
        sendAIMessage();
    }
}

function sendMessage() {
    sendAIMessage();
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendAIMessage();
    }
}

function transferToHuman() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const botDiv = document.createElement('div');
    botDiv.className = 'message bot-message';
    botDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-text">
                👨‍💼 <strong>正在为您转接人工客服...</strong><br><br>
                当前排队人数：<strong>2人</strong><br>
                预计等待时间：<strong>约2分钟</strong><br><br>
                <em>请稍候，客服人员即将接入...</em>
            </div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
    `;
    chatMessages.appendChild(botDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showFAQ() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const faqContent = `
        <strong>📋 常见问题：</strong><br><br>
        <strong>Q: 如何发布卖书信息？</strong><br>
        A: 点击"我要卖书"，选择录入方式，填写信息后提交即可。<br><br>
        <strong>Q: 交易安全吗？</strong><br>
        A: 平台提供浙大实名认证、交易担保等安全保障。<br><br>
        <strong>Q: 如何联系卖家？</strong><br>
        A: 在书籍详情页点击"私聊卖家"或通过消息中心联系。<br><br>
        <strong>Q: 如何查看订单状态？</strong><br>
        A: 在个人中心的"我的订单"中查看所有订单状态。<br><br>
        <strong>Q: 什么是书籍电子身份证？</strong><br>
        A: 每本书都有唯一的电子身份证，记录完整的流转历史。<br><br>
        <button class="btn btn-primary btn-sm" onclick="askQuickQuestion('还有其他问题')">还有其他问题？</button>
    `;

    const botDiv = document.createElement('div');
    botDiv.className = 'message bot-message';
    botDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${faqContent}</div>
            <div class="message-time">${getCurrentTime()}</div>
        </div>
    `;
    chatMessages.appendChild(botDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTutorial() {
    AppActions.showToast('正在加载使用教程...', 'info');
    setTimeout(() => {
        AppActions.showToast('教程视频已加载，请在页面中查看', 'success');
    }, 1000);
}

function rateService(rating) {
    const stars = document.querySelectorAll('.rating-stars i');
    stars.forEach((star, index) => {
        if (index < rating) {
            star.className = 'fas fa-star';
            star.style.color = '#f59e0b';
        } else {
            star.className = 'far fa-star';
            star.style.color = '#d1d5db';
        }
    });
    AppActions.showToast(`感谢您的${rating}星评价！`, 'success');
}

function showFeedbackForm() {
    const feedback = prompt('请描述您的反馈意见：');
    if (feedback) {
        AppActions.showToast('感谢您的反馈！我们会不断改进', 'success');
    }
}

function generateMockRecommendations() {
    const container = document.getElementById('recommendationResults');
    if (!container) return;

    container.innerHTML = `
        <div class="recommendation-list">
            <div class="recommendation-header">
                <h4>📋 基于课表的教材推荐清单</h4>
                <p>共检测到 <strong>6</strong> 门课程，推荐 <strong>8</strong> 本教材</p>
            </div>
            <div class="recommendation-items">
                <div class="recommendation-item">
                    <div class="rec-course">
                        <span class="course-badge">必修</span>
                        <strong>数据结构与算法</strong>
                        <small>CS101</small>
                    </div>
                    <div class="rec-books">
                        <div class="rec-book">
                            <span>《数据结构（C语言版）》- 严蔚敏</span>
                            <span class="rec-price">二手价 ¥35.00</span>
                            <button class="btn btn-primary btn-sm" onclick="AppActions.navigateTo('book-detail.html', {id: 1})">查看</button>
                        </div>
                        <div class="rec-book">
                            <span>《算法导论》- Thomas H. Cormen</span>
                            <span class="rec-price">二手价 ¥85.00</span>
                            <button class="btn btn-primary btn-sm" onclick="AppActions.navigateTo('book-detail.html', {id: 2})">查看</button>
                        </div>
                    </div>
                </div>
                <div class="recommendation-item">
                    <div class="rec-course">
                        <span class="course-badge">必修</span>
                        <strong>高等数学</strong>
                        <small>MATH201</small>
                    </div>
                    <div class="rec-books">
                        <div class="rec-book">
                            <span>《高等数学（第七版）》- 同济大学</span>
                            <span class="rec-price">二手价 ¥45.00</span>
                            <button class="btn btn-primary btn-sm" onclick="AppActions.navigateTo('book-detail.html', {id: 3})">查看</button>
                        </div>
                    </div>
                </div>
                <div class="recommendation-item">
                    <div class="rec-course">
                        <span class="course-badge">必修</span>
                        <strong>大学物理</strong>
                        <small>PHYS101</small>
                    </div>
                    <div class="rec-books">
                        <div class="rec-book">
                            <span>《大学物理（第五版）》- 张三慧</span>
                            <span class="rec-price">二手价 ¥38.00</span>
                            <button class="btn btn-primary btn-sm" onclick="AppActions.navigateTo('book-detail.html', {id: 4})">查看</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="recommendation-summary">
                <p><strong>预计总花费：</strong>¥203.00（比原价节省 ¥278.00）</p>
                <button class="btn btn-primary" onclick="AppActions.navigateTo('buy.html')">
                    <i class="fas fa-shopping-cart"></i> 一键购买全部
                </button>
            </div>
        </div>
    `;
}

function exportRecommendations() {
    AppActions.showToast('正在导出推荐清单...', 'info');
    setTimeout(() => {
        AppActions.showToast('推荐清单已导出为PDF', 'success');
    }, 1000);
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
