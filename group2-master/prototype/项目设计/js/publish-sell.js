/**
 * 求书平台 - 发布卖书脚本
 * 集成全局应用状态，实现发布卖书交互功能
 */

document.addEventListener('DOMContentLoaded', function() {
    initPublishPage();
});

function initPublishPage() {
    // 获取URL参数中的录入方式
    const params = AppActions.getUrlParams();
    const method = params.method || 'manual';

    // 根据录入方式显示提示
    if (method === 'scan') {
        setTimeout(() => {
            AppActions.showToast('正在启动摄像头扫码...', 'info');
            // 模拟扫码结果
            setTimeout(() => {
                document.getElementById('bookIsbn').value = '9787111636623';
                document.getElementById('bookTitle').value = '深入理解计算机系统';
                document.getElementById('bookAuthor').value = 'Randal E. Bryant';
                document.getElementById('bookPublisher').value = '机械工业出版社';
                AppActions.showToast('扫码成功！已自动填充书籍信息', 'success');
            }, 1500);
        }, 500);
    } else if (method === 'history') {
        // 从购买历史选择
        const recentBooks = AppState.orders.filter(o => o.status === 'completed').slice(0, 3);
        if (recentBooks.length > 0) {
            const bookList = recentBooks.map((b, i) => `${i + 1}. ${b.bookTitle} (¥${b.price})`).join('\n');
            const choice = prompt(`选择要上架的书籍：\n${bookList}\n\n请输入编号（1-${recentBooks.length}）：`);
            if (choice) {
                const index = parseInt(choice) - 1;
                if (index >= 0 && index < recentBooks.length) {
                    const book = recentBooks[index];
                    document.getElementById('bookTitle').value = book.bookTitle;
                    document.getElementById('bookAuthor').value = book.bookAuthor;
                    document.getElementById('bookIsbn').value = book.isbn;
                    document.getElementById('bookPrice').value = book.price;
                    AppActions.showToast(`已加载《${book.bookTitle}》的信息`, 'success');
                }
            }
        } else {
            AppActions.showToast('暂无购买历史记录', 'info');
        }
    }

    // 表单提交
    const publishForm = document.getElementById('publishForm');
    if (publishForm) {
        publishForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 收集表单数据
            const formData = {
                title: document.getElementById('bookTitle')?.value || '',
                author: document.getElementById('bookAuthor')?.value || '',
                isbn: document.getElementById('bookIsbn')?.value || '',
                price: parseFloat(document.getElementById('bookPrice')?.value) || 0,
                publisher: document.getElementById('bookPublisher')?.value || '',
                edition: document.getElementById('bookEdition')?.value || '',
                tradeMethod: document.querySelector('input[name="tradeMethod"]:checked')?.value || '',
                campus: document.querySelector('input[name="campus"]:checked')?.value || '',
                tradeTime: document.getElementById('tradeTime')?.value || '',
                condition: document.querySelector('input[name="condition"]:checked')?.value || '',
                hasNotes: document.querySelector('input[name="hasNotes"]:checked')?.value || '',
                notesDescription: document.getElementById('notesDescription')?.value || '',
                additionalInfo: document.getElementById('additionalInfo')?.value || '',
                courseTags: document.getElementById('courseTags')?.value || ''
            };

            // 验证必填字段
            if (!formData.title || !formData.author || !formData.isbn || !formData.price) {
                AppActions.showToast('请填写所有必填字段', 'error');
                return;
            }

            // 显示提交中
            const submitBtn = document.getElementById('submitBtn');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 提交中...';
                submitBtn.disabled = true;
            }

            // 模拟提交
            setTimeout(() => {
                AppActions.showToast('发布成功！您的卖书帖已提交审核', 'success');
                setTimeout(() => {
                    AppActions.navigateTo('profile.html');
                }, 1500);
            }, 1500);
        });
    }

    // 取消按钮
    const cancelBtn = document.getElementById('cancelBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            AppActions.navigateTo('sell.html');
        });
    }

    // 扫码按钮
    const scanBtn = document.getElementById('scanBtn');
    if (scanBtn) {
        scanBtn.addEventListener('click', function() {
            AppActions.showToast('扫码功能需要调用摄像头，请在移动设备上使用', 'info');
            // 模拟扫码
            document.getElementById('bookIsbn').value = '9787111636623';
            document.getElementById('bookTitle').value = '深入理解计算机系统';
            document.getElementById('bookAuthor').value = 'Randal E. Bryant';
            document.getElementById('bookPublisher').value = '机械工业出版社';
            AppActions.showToast('已自动填充书籍信息', 'success');
        });
    }

    // 图片上传
    const imageUploadArea = document.getElementById('imageUploadArea');
    const photoUpload = document.getElementById('photoUpload');
    const imagePreview = document.getElementById('imagePreview');

    if (imageUploadArea && photoUpload) {
        imageUploadArea.addEventListener('click', () => photoUpload.click());

        imageUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            imageUploadArea.style.borderColor = 'var(--primary-blue)';
            imageUploadArea.style.backgroundColor = 'var(--light-blue)';
        });

        imageUploadArea.addEventListener('dragleave', () => {
            imageUploadArea.style.borderColor = '';
            imageUploadArea.style.backgroundColor = '';
        });

        imageUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            imageUploadArea.style.borderColor = '';
            imageUploadArea.style.backgroundColor = '';
            handleFiles(e.dataTransfer.files);
        });

        photoUpload.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
    }

    let uploadedImages = [];

    function handleFiles(files) {
        if (files.length === 0) return;
        if (uploadedImages.length + files.length > 5) {
            AppActions.showToast('最多只能上传5张图片', 'error');
            return;
        }

        Array.from(files).forEach(file => {
            if (!file.type.startsWith('image/')) {
                AppActions.showToast(`文件 ${file.name} 不是图片格式`, 'error');
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                AppActions.showToast(`文件 ${file.name} 太大，请选择小于5MB的图片`, 'error');
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                uploadedImages.push({ id: Date.now() + Math.random(), name: file.name, data: e.target.result });
                updatePreview();
            };
            reader.readAsDataURL(file);
        });
        photoUpload.value = '';
    }

    function updatePreview() {
        if (!imagePreview) return;
        imagePreview.innerHTML = '';
        uploadedImages.forEach((image) => {
            const item = document.createElement('div');
            item.className = 'image-preview-item';
            item.innerHTML = `
                <img src="${image.data}" alt="书籍图片">
                <button type="button" class="remove-btn" data-id="${image.id}">
                    <i class="fas fa-times"></i>
                </button>
            `;
            imagePreview.appendChild(item);
        });

        imagePreview.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                uploadedImages = uploadedImages.filter(img => img.id != id);
                updatePreview();
            });
        });
    }

    // 校区选择交互
    document.querySelectorAll('.campus-option').forEach(option => {
        option.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                document.querySelectorAll('.campus-option').forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
            }
        });
    });
}
