/**
 * 修改建议 AI对话功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // AI聊天状态
    const chatState = {
        messages: [],
        isWaitingForResponse: false,
        backendUrl: 'http://localhost:8080' // 后端API地址，根据实际情况修改
    };

    // DOM元素
    const suggestionsContainer = document.querySelector('.suggestions-container');
    const chatMessages = document.getElementById('ai-chat-messages');
    const userMessageInput = document.getElementById('user-message');
    const sendMessageButton = document.getElementById('send-message');

    // 初始化事件监听
    initChatEvents();

    // 初始化聊天界面
    function initChatEvents() {
        // 发送消息按钮点击事件
        sendMessageButton.addEventListener('click', function() {
            sendUserMessage();
        });

        // 输入框回车事件
        userMessageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendUserMessage();
            }
        });
    }

    // 发送用户消息
    function sendUserMessage() {
        const message = userMessageInput.value.trim();
        if (!message || chatState.isWaitingForResponse) return;

        // 添加用户消息到聊天窗口
        addUserMessage(message);

        // 清空输入框
        userMessageInput.value = '';

        // 设置等待状态
        chatState.isWaitingForResponse = true;
        sendMessageButton.disabled = true;
        sendMessageButton.textContent = '等待中...';

        // 模拟API请求（实际应该调用后端API）
        mockAIResponse(message);
    }

    // 添加用户消息到聊天窗口
    function addUserMessage(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'user-message';
        messageElement.innerHTML = `
            <div class="user-content">
                <p>${escapeHtml(text)}</p>
            </div>
            <div class="user-avatar">用</div>
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 添加到消息历史
        chatState.messages.push({
            role: 'user',
            content: text
        });
    }

    // 添加AI消息到聊天窗口
    function addAIMessage(text, suggestions = []) {
        const messageElement = document.createElement('div');
        messageElement.className = 'ai-message';
        
        let suggestionsHtml = '';
        if (suggestions.length > 0) {
            suggestionsHtml = '<div class="ai-suggestions"><p>建议操作：</p><ul>';
            suggestions.forEach(suggestion => {
                suggestionsHtml += `<li><a href="#" class="suggestion-link">${escapeHtml(suggestion)}</a></li>`;
            });
            suggestionsHtml += '</ul></div>';
        }

        messageElement.innerHTML = `
            <div class="ai-avatar">AI</div>
            <div class="ai-content">
                <p>${escapeHtml(text)}</p>
                ${suggestionsHtml}
            </div>
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // 添加事件监听器到建议链接
        const suggestionLinks = messageElement.querySelectorAll('.suggestion-link');
        suggestionLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                userMessageInput.value = this.textContent;
                userMessageInput.focus();
            });
        });

        // 添加到消息历史
        chatState.messages.push({
            role: 'assistant',
            content: text
        });
    }

    // 模拟AI响应（实际项目中应替换为真实API调用）
    function mockAIResponse(userMessage) {
        // 模拟网络延迟
        setTimeout(() => {
            let response, suggestions;

            // 简单的关键词匹配，现在的内容更加偏向代码修改建议
            if (userMessage.toLowerCase().includes('html')) {
                response = "你的HTML结构看起来不错，但是我有几点建议来提高可读性和语义化。考虑使用更多的语义化标签，例如用<section>来包裹相关内容，用<nav>来包裹导航链接。";
                suggestions = ["添加标题元素提高SEO", "改进表单的访问性", "优化图片标签的alt属性"];
            } else if (userMessage.toLowerCase().includes('css')) {
                response = "你的CSS可以通过使用变量来提高可维护性。我建议将重复的颜色值和间距值提取为变量，并考虑使用CSS Grid或Flexbox来简化你的布局。";
                suggestions = ["使用响应式单位提高适配性", "优化选择器提高性能", "添加过渡效果提升用户体验"];
            } else if (userMessage.toLowerCase().includes('javascript') || userMessage.toLowerCase().includes('js')) {
                response = "你的JavaScript代码可以通过以下方式改进：1) 使用现代ES6+语法，如箭头函数和解构赋值；2) 将特定功能封装成函数；3) 使用事件委托来减少事件监听器。";
                suggestions = ["使用Promise替代回调函数", "采用模块化组织代码", "优化DOM操作提高性能"];
            } else if (userMessage.toLowerCase().includes('错误') || userMessage.toLowerCase().includes('error')) {
                response = "我在你的代码中发现了一些问题：1) 缺少闭合标签，请检查HTML标签是否配对；2) CSS选择器可能存在拼写错误；3) JavaScript中可能存在变量未定义就使用的情况。";
                suggestions = ["修复HTML结构错误", "修正CSS选择器问题", "解决JavaScript变量作用域问题"];
            } else {
                response = "我已经分析了你的代码，有几点优化建议：1) 使用语义化标签提高可读性；2) 采用CSS变量管理样式；3) 采用事件委托优化事件处理；4) 添加适当的注释提高代码可维护性。";
                suggestions = ["如何提高代码可读性？", "响应式设计最佳实践", "如何优化页面加载速度？"];
            }

            // 添加AI响应到聊天窗口
            addAIMessage(response, suggestions);

            // 重置等待状态
            chatState.isWaitingForResponse = false;
            sendMessageButton.disabled = false;
            sendMessageButton.textContent = '发送';
        }, 1000);
    }

    // 实际的AI API调用（实际项目中使用）
    async function callAIAPI(message) {
        try {
            const response = await fetch(`${chatState.backendUrl}/ai/suggestions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    code: {
                        html: typeof editorState !== 'undefined' ? editorState.html : '',
                        css: typeof editorState !== 'undefined' ? editorState.css : '',
                        js: typeof editorState !== 'undefined' ? editorState.js : ''
                    }
                })
            });

            if (!response.ok) {
                throw new Error('API请求失败');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('AI API调用出错：', error);
            return {
                status: 'error',
                reply: '抱歉，修改建议生成失败，请稍后再试。',
                suggestions: []
            };
        }
    }

    // HTML转义函数，防止XSS攻击
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});