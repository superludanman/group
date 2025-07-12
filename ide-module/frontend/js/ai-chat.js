/**
 * AI对话功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // AI聊天状态
    const chatState = {
        isExpanded: true,
        messages: [],
        isWaitingForResponse: false,
        backendUrl: 'http://localhost:8000' // 后端API地址，根据实际情况修改
    };

    // DOM元素
    const chatContainer = document.querySelector('.ai-chat-container');
    const chatMessages = document.getElementById('ai-chat-messages');
    const userMessageInput = document.getElementById('user-message');
    const sendMessageButton = document.getElementById('send-message');
    const toggleChatButton = document.getElementById('toggle-chat');

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

        // 展开/收起聊天窗口按钮事件
        toggleChatButton.addEventListener('click', function() {
            chatState.isExpanded = !chatState.isExpanded;
            chatMessages.style.display = chatState.isExpanded ? 'block' : 'none';
            document.querySelector('.ai-chat-input').style.display = chatState.isExpanded ? 'flex' : 'none';
            this.textContent = chatState.isExpanded ? '收起' : '展开';
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

            // 简单的关键词匹配
            if (userMessage.toLowerCase().includes('html')) {
                response = "HTML是构建网页的标准标记语言。通过各种标签，你可以定义页面的结构。例如，你可以使用<div>创建容器，使用<p>创建段落，或使用<h1>到<h6>创建标题。";
                suggestions = ["怎么创建链接？", "如何添加图片？", "表格怎么制作？"];
            } else if (userMessage.toLowerCase().includes('css')) {
                response = "CSS（层叠样式表）用于设置HTML元素的样式。你可以使用类选择器（.class）、ID选择器（#id）或元素选择器（如p, div）来应用样式。CSS可以控制颜色、字体、间距、布局等。";
                suggestions = ["如何居中元素？", "什么是Flexbox？", "CSS动画怎么做？"];
            } else if (userMessage.toLowerCase().includes('javascript') || userMessage.toLowerCase().includes('js')) {
                response = "JavaScript是一种编程语言，使网页具有交互性。你可以使用JavaScript来响应用户操作、动态修改页面内容、发送网络请求等。";
                suggestions = ["如何选择DOM元素？", "事件监听怎么写？", "怎么处理表单提交？"];
            } else if (userMessage.toLowerCase().includes('错误') || userMessage.toLowerCase().includes('error')) {
                response = "调试代码是编程过程中的重要部分。你可以使用浏览器的开发者工具来查看JavaScript错误，或者使用console.log()来打印变量值帮助调试。";
                suggestions = ["常见的HTML错误有哪些？", "怎么修复CSS不生效的问题？", "JavaScript语法错误怎么解决？"];
            } else {
                response = "我是你的AI助手，可以帮助你学习HTML、CSS和JavaScript。请告诉我你想了解什么，或者如果你遇到了代码问题，可以详细描述一下。";
                suggestions = ["HTML基础知识", "CSS布局技巧", "JavaScript交互功能"];
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
            const response = await fetch(`${chatState.backendUrl}/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message
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
                reply: '抱歉，AI助手暂时无法响应，请稍后再试。',
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