/**
 * 面板折叠功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const toggleRequirementsBtn = document.getElementById('toggle-requirements');
    const requirementsContent = document.getElementById('test-requirements-content');
    const toggleResultsBtn = document.getElementById('toggle-results');
    const resultsContent = document.getElementById('test-results-content');
    const previewButton = document.getElementById('preview-button');
    
    // 测试要求折叠功能
    toggleRequirementsBtn.addEventListener('click', function() {
        if (requirementsContent.style.display === 'none') {
            requirementsContent.style.display = 'block';
            toggleRequirementsBtn.textContent = '收起';
        } else {
            requirementsContent.style.display = 'none';
            toggleRequirementsBtn.textContent = '查看提示';
        }
        
        // 在测试要求折叠时，调整修改建议区域的高度
        const suggestionsContainer = document.querySelector('.suggestions-container');
        const chatMessages = document.querySelector('.ai-chat-messages');
        if (requirementsContent.style.display === 'none') {
            suggestionsContainer.style.flexGrow = '3'; // 显著增加修改建议区域的占比
            // 使聊天消息区域也变大
            if (chatMessages) {
                chatMessages.style.flex = '1 1 auto';
                chatMessages.style.minHeight = '300px';
            }
        } else {
            suggestionsContainer.style.flexGrow = '1'; // 恢复默认占比
            if (chatMessages) {
                chatMessages.style.flex = '';
                chatMessages.style.minHeight = '';
            }
        }
    });
    
    // 测试结果折叠功能
    toggleResultsBtn.addEventListener('click', function() {
        if (resultsContent.style.display === 'none') {
            resultsContent.style.display = 'block';
            toggleResultsBtn.textContent = '收起';
        } else {
            resultsContent.style.display = 'none';
            toggleResultsBtn.textContent = '查看提示';
        }
        
        // 在测试结果折叠时，调整修改建议区域的高度
        const suggestionsContainer = document.querySelector('.suggestions-container');
        const chatMessages = document.querySelector('.ai-chat-messages');
        if (resultsContent.style.display === 'none') {
            suggestionsContainer.style.flexGrow = '3'; // 显著增加修改建议区域的占比
            // 使聊天消息区域也变大
            if (chatMessages) {
                chatMessages.style.flex = '1 1 auto';
                chatMessages.style.minHeight = '300px';
            }
        } else {
            suggestionsContainer.style.flexGrow = '1'; // 恢复默认占比
            if (chatMessages) {
                chatMessages.style.flex = '';
                chatMessages.style.minHeight = '';
            }
        }
    });
    
    // 预览按钮功能 - 更新预览窗口
    previewButton.addEventListener('click', function() {
        // 此处调用updateLocalPreview函数，该函数在editor.js中定义
        if (typeof updateLocalPreview === 'function') {
            updateLocalPreview();
        } else {
            // 如果函数不可用，则尝试触发运行按钮点击
            document.getElementById('run-button').click();
        }
    });
    
    // 初始化面板状态
    if (requirementsContent && toggleRequirementsBtn) {
        requirementsContent.style.display = 'block';
        toggleRequirementsBtn.textContent = '收起';
    }
    
    if (resultsContent && toggleResultsBtn) {
        resultsContent.style.display = 'none';
        toggleResultsBtn.textContent = '查看提示';
    }
    
    // 触发一次折叠事件，确保修改建议区域显示正确
    setTimeout(function() {
        if (toggleResultsBtn) {
            // 默认就是折叠状态，直接调整大小
            const suggestionsContainer = document.querySelector('.suggestions-container');
            const chatMessages = document.querySelector('.ai-chat-messages');
            if (suggestionsContainer) {
                suggestionsContainer.style.flexGrow = '3';
            }
            if (chatMessages) {
                chatMessages.style.flex = '1 1 auto';
                chatMessages.style.minHeight = '300px';
            }
        }
    }, 100);
    
    // 添加窗口调整事件，确保响应式设计
    window.addEventListener('resize', function() {
        // 如果测试要求或测试结果折叠，继续保持修改建议区域的扩展状态
        if (resultsContent && resultsContent.style.display === 'none') {
            const suggestionsContainer = document.querySelector('.suggestions-container');
            const chatMessages = document.querySelector('.ai-chat-messages');
            if (suggestionsContainer) {
                suggestionsContainer.style.flexGrow = '3';
            }
            if (chatMessages) {
                chatMessages.style.flex = '1 1 auto';
                chatMessages.style.minHeight = '300px';
            }
        }
    });
    
    // 增加一些示例内容到测试要求和测试结果区域
    if (requirementsContent) {
        requirementsContent.innerHTML = `
            <div class="requirement-content">
                <p>任务目标：创建一个简单的网页，包含标题、段落和按钮元素。</p>
                <ol>
                    <li>创建一个标题，文本为“我的第一个网页”</li>
                    <li>添加一个段落，包含一些描述性文字</li>
                    <li>创建一个按钮，文本为“点击我”</li>
                    <li>为按钮添加点击事件，点击时显示一个警告框</li>
                </ol>
            </div>
        `;
    }
    
    if (resultsContent) {
        resultsContent.innerHTML = `
            <div class="result-item success">
                <span class="result-icon">✓</span>
                <span class="result-message">标题已正确创建</span>
            </div>
            <div class="result-item error">
                <span class="result-icon">✗</span>
                <span class="result-message">按钮点击事件未实现</span>
            </div>
        `;
    }
});