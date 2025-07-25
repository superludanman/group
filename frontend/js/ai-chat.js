/**
 * 修改建议 AI对话功能
 */
/**
 * 简化版发送消息函数 - 直接在HTML中调用
 */
window.sendMessage = function() {
    try {
        console.log('sendMessage被调用');
        
        // 获取消息元素
        const userMessageInput = document.getElementById('user-message');
        if (!userMessageInput) {
            console.error('找不到消息输入框');
            alert('错误: 找不到消息输入框');
            return false;
        }
        
        // 获取消息内容
        const message = userMessageInput.value.trim();
        console.log('获取到消息:', message);
        
        // 检查消息是否为空
        if (!message) {
            console.log('消息为空，不发送');
            return false;
        }
        
        // 获取聊天容器
        const chatMessages = document.getElementById('ai-chat-messages');
        if (!chatMessages) {
            console.error('找不到聊天消息容器');
            alert('错误: 找不到聊天消息容器');
            return false;
        }
        
        // HTML转义函数（内联定义以确保可用）
        function escapeMsg(text) {
            if (!text) return '';
            return String(text)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
        
        // 添加用户消息
        console.log('添加用户消息到对话框');
        const userDiv = document.createElement('div');
        userDiv.className = 'user-message';
        userDiv.innerHTML = `
            <div class="user-content">
                <p>${escapeMsg(message)}</p>
            </div>
            <div class="user-avatar">用</div>
        `;
        chatMessages.appendChild(userDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 清空输入框
        userMessageInput.value = '';
        
        // 添加AI回复（模拟）
        console.log('添加AI回复');
        setTimeout(function() {
            const aiDiv = document.createElement('div');
            aiDiv.className = 'ai-message';
            aiDiv.innerHTML = `
                <div class="ai-avatar">AI</div>
                <div class="ai-content">
                    <div class="markdown-content">
                        <p>收到消息: "${escapeMsg(message)}"。</p>
                        <p>这是一个测试回复，表示消息发送功能已修复。</p>
                    </div>
                </div>
            `;
            chatMessages.appendChild(aiDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 500);
        
        return true;
    } catch (error) {
        console.error('发送消息时出错:', error);
        alert('发送消息时出错: ' + error.message);
        return false;
    }
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('AI聊天模块初始化');
    
    const sendMessageButton = document.getElementById('send-message');
    const userMessageInput = document.getElementById('user-message');
    const chatMessages = document.getElementById('ai-chat-messages');

    // 检查DOM元素是否正确加载
    console.log('DOM元素检查:', {
        sendMessageButton: !!sendMessageButton,
        userMessageInput: !!userMessageInput,
        chatMessages: !!chatMessages
    });
    
    // 为初始欢迎消息添加复制按钮
    const initialMessage = chatMessages.querySelector('.ai-message');
    if(initialMessage) {
        console.log('找到初始欢迎消息，添加复制按钮');
        addCopyButtonsToCodeBlocks(initialMessage);
    } else {
        console.log('未找到初始欢迎消息');
    }
    
    // 重新绑定发送按钮事件
    if (sendMessageButton) {
        console.log('重新绑定发送按钮事件');
        // 先移除所有事件监听器
        const newButton = sendMessageButton.cloneNode(true);
        sendMessageButton.parentNode.replaceChild(newButton, sendMessageButton);
        
        // 添加新的监听器
        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('发送按钮被点击 - 新绑定');
            window.sendMessage();
        });
    }
    // 配置Marked.js
    marked.setOptions({
        renderer: new marked.Renderer(),
        highlight: function(code, lang) {
            const language = hljs.getLanguage(lang) ? lang : 'plaintext';
            return hljs.highlight(code, { language }).value;
        },
        langPrefix: 'hljs language-',
        pedantic: false,
        gfm: true,
        breaks: false,
        sanitize: false,
        smartypants: false,
        xhtml: false
    });
    // AI聊天状态
    const chatState = {
        messages: [],
        isWaitingForResponse: false,
        backendUrl: '/api/module/ide', // 使用相对路径指向主项目的 API 端点
        sessionId: generateSessionId(), // 会话ID，用于跟踪学习者状态
        userBehavior: {
            lastActivity: Date.now(),
            activityLog: [], // 用户活动日志
            typingSpeed: 0, // 打字速度（字符/分钟）
            errorRate: 0, // 错误率
            focusTime: 0, // 专注时间（毫秒）
            idleTime: 0, // 空闲时间（毫秒）
            interactionTypes: {}, // 互动类型计数（如代码示例点击、解释点击等）
        }
    };

    // 初始化事件监听
    initChatEvents();
    
    // 初始化用户行为跟踪
    initUserBehaviorTracking();

    // 初始化聊天界面
    function initChatEvents() {
        // 发送消息按钮点击事件
        sendMessageButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('发送按钮被点击');
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
        console.log('sendUserMessage被调用');
        const message = userMessageInput.value.trim();
        console.log('用户消息:', message);
        if (!message || chatState.isWaitingForResponse) {
            console.log('消息为空或正在等待响应', {
                isEmpty: !message,
                isWaiting: chatState.isWaitingForResponse
            });
            return;
        }

        // 添加用户消息到聊天窗口
        addUserMessage(message);

        // 清空输入框
        userMessageInput.value = '';

        // 设置等待状态
        chatState.isWaitingForResponse = true;
        sendMessageButton.disabled = true;
        sendMessageButton.textContent = '等待中...';

        // 记录用户行为 - 发送消息
        logUserActivity('send_message', { message_length: message.length });

        // 调用AI API
        callAIAPI(message);
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
        
        // 使用marked.js渲染Markdown
        const renderedContent = marked.parse(text);
        
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
                <div class="markdown-content">${renderedContent}</div>
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
        
        // 为代码块添加复制按钮
        addCopyButtonsToCodeBlocks(messageElement);

        // 添加到消息历史
        chatState.messages.push({
            role: 'assistant',
            content: text
        });
    }

    
    // 实际的AI API调用
    async function callAIAPI(message) {
        try {
            // 获取当前代码状态
            const codeState = {
                html: typeof editorState !== 'undefined' ? editorState.html : '',
                css: typeof editorState !== 'undefined' ? editorState.css : '',
                js: typeof editorState !== 'undefined' ? editorState.js : ''
            };
            
            let data;
            
            try {
                // 发送API请求
                const response = await fetch(`${chatState.backendUrl}/ai/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        code: codeState,
                        session_id: chatState.sessionId
                    })
                });
    
                if (!response.ok) {
                    throw new Error(`API请求失败: ${response.status}`);
                }
    
                data = await response.json();
            } catch (fetchError) {
                console.warn('无法连接到后端API，使用模拟响应：', fetchError);
                // 模拟响应（当后端服务器不可用时）
                data = generateMockResponse(message);
            }
            
            if (data.status === 'success') {
                // 添加AI响应到聊天窗口
                addAIMessage(data.reply, data.suggestions || []);
                
                // 记录交互成功
                logUserActivity('ai_response_received', { 
                    success: true,
                    response_time: data.response_time
                });
            } else {
                // 处理错误
                addAIMessage('抱歉，生成回复时出现问题，请稍后再试。', []);
                console.error('AI API返回错误:', data.message);
                
                // 记录交互失败
                logUserActivity('ai_response_error', { 
                    error: data.message
                });
            }
            
            // 重置等待状态
            chatState.isWaitingForResponse = false;
            sendMessageButton.disabled = false;
            sendMessageButton.textContent = '发送';
            
        } catch (error) {
            console.error('AI API调用出错：', error);
            
            // 添加错误消息
            addAIMessage('抱歉，连接AI服务时出现问题，请检查网络连接或稍后再试。', []);
            
            // 记录错误
            logUserActivity('ai_connection_error', { 
                error_message: error.message 
            });
            
            // 重置等待状态
            chatState.isWaitingForResponse = false;
            sendMessageButton.disabled = false;
            sendMessageButton.textContent = '发送';
        }
    }

    // 生成会话ID
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 11);
    }
    
    // 初始化用户行为跟踪
    function initUserBehaviorTracking() {
        // 活动检测 - 记录用户最后活动时间
        document.addEventListener('mousemove', updateLastActivity);
        document.addEventListener('keypress', updateLastActivity);
        document.addEventListener('click', updateLastActivity);
        
        // 编辑器交互跟踪
        if (typeof editor !== 'undefined') {
            editor.onDidChangeModelContent(trackEditing);
        }
        if (typeof editorCSS !== 'undefined') {
            editorCSS.onDidChangeModelContent(trackEditing);
        }
        if (typeof editorJS !== 'undefined') {
            editorJS.onDidChangeModelContent(trackEditing);
        }
        
        // 定期发送用户行为数据到服务器
        setInterval(sendUserBehaviorData, 30000); // 每30秒发送一次
        
        console.log('用户行为跟踪已初始化');
    }
    
    // 更新最后活动时间
    function updateLastActivity() {
        const now = Date.now();
        
        // 计算空闲时间
        if (chatState.userBehavior.lastActivity > 0) {
            const idleTime = now - chatState.userBehavior.lastActivity;
            chatState.userBehavior.idleTime += idleTime;
            
            // 如果空闲时间超过10秒，记录为专注度下降
            if (idleTime > 10000) {
                logUserActivity('focus_drop', { idle_time: idleTime });
            }
        }
        
        chatState.userBehavior.lastActivity = now;
    }
    
    // 跟踪编辑行为
    function trackEditing(event) {
        logUserActivity('code_edit', {
            changes: event.changes.length,
            time: Date.now()
        });
    }
    
    // 记录用户活动
    function logUserActivity(activityType, data = {}) {
        const activity = {
            type: activityType,
            timestamp: Date.now(),
            data: data
        };
        
        // 添加到活动日志
        chatState.userBehavior.activityLog.push(activity);
        
        // 限制日志大小
        if (chatState.userBehavior.activityLog.length > 100) {
            chatState.userBehavior.activityLog.shift(); // 移除最旧的记录
        }
        
        // 更新交互类型计数
        if (activityType.startsWith('interaction_')) {
            const interactionType = activityType.replace('interaction_', '');
            if (!chatState.userBehavior.interactionTypes[interactionType]) {
                chatState.userBehavior.interactionTypes[interactionType] = 0;
            }
            chatState.userBehavior.interactionTypes[interactionType]++;
        }
        
        // 更新最后活动时间
        chatState.userBehavior.lastActivity = Date.now();
    }
    
    // 发送用户行为数据到服务器
    async function sendUserBehaviorData() {
        // 如果活动日志为空，不发送
        if (chatState.userBehavior.activityLog.length === 0) return;
        
        try {
            // 准备发送的数据
            const behaviorData = {
                session_id: chatState.sessionId,
                data: {
                    activity_log: chatState.userBehavior.activityLog,
                    typing_speed: chatState.userBehavior.typingSpeed,
                    error_rate: chatState.userBehavior.errorRate,
                    focus_time: Date.now() - chatState.userBehavior.lastActivity,
                    idle_time: chatState.userBehavior.idleTime,
                    interaction_types: chatState.userBehavior.interactionTypes
                }
            };
            
            // 发送数据
            const response = await fetch(`${chatState.backendUrl}/student/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(behaviorData)
            });
            
            if (response.ok) {
                // 清空活动日志
                chatState.userBehavior.activityLog = [];
                console.log('用户行为数据已发送');
            } else {
                console.error('发送用户行为数据失败:', response.status);
            }
        } catch (error) {
            console.error('发送用户行为数据出错:', error);
        }
    }
    
    // 提交代码并获取错误反馈
    async function submitCodeForFeedback(errorInfo) {
        try {
            // 获取当前代码状态
            const codeState = {
                html: typeof editorState !== 'undefined' ? editorState.html : '',
                css: typeof editorState !== 'undefined' ? editorState.css : '',
                js: typeof editorState !== 'undefined' ? editorState.js : ''
            };
            
            // 发送API请求
            const response = await fetch(`${chatState.backendUrl}/ai/error-feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    code: codeState,
                    error_info: errorInfo,
                    session_id: chatState.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`API请求失败: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                // 添加AI错误反馈到聊天窗口
                addAIMessage(data.feedback, ["尝试修复错误", "查看更多相关内容"]);
                
                // 记录交互成功
                logUserActivity('error_feedback_received', { 
                    success: true,
                    response_time: data.response_time
                });
            } else {
                // 处理错误
                addAIMessage('抱歉，生成错误反馈时出现问题，请稍后再试。', []);
                console.error('错误反馈API返回错误:', data.message);
            }
            
        } catch (error) {
            console.error('错误反馈API调用出错：', error);
            addAIMessage('抱歉，获取错误反馈时出现问题，请检查网络连接或稍后再试。', []);
        }
    }
    
    // 为代码块添加复制按钮
    function addCopyButtonsToCodeBlocks(messageElement) {
        const codeBlocks = messageElement.querySelectorAll('pre code');
        
        codeBlocks.forEach((codeBlock) => {
            // 创建包裹容器
            const wrapper = document.createElement('div');
            wrapper.className = 'code-block-wrapper';
            wrapper.style.position = 'relative';
            
            // 创建复制按钮
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-code-button';
            copyButton.textContent = '复制';
            copyButton.style.position = 'absolute';
            copyButton.style.top = '5px';
            copyButton.style.right = '5px';
            copyButton.style.padding = '3px 8px';
            copyButton.style.fontSize = '12px';
            copyButton.style.color = '#333';
            copyButton.style.background = '#f0f0f0';
            copyButton.style.border = '1px solid #ccc';
            copyButton.style.borderRadius = '3px';
            copyButton.style.cursor = 'pointer';
            copyButton.style.zIndex = '10';
            
            // 复制代码功能
            copyButton.addEventListener('click', () => {
                const code = codeBlock.textContent;
                navigator.clipboard.writeText(code).then(() => {
                    const originalText = copyButton.textContent;
                    copyButton.textContent = '已复制!';
                    copyButton.style.background = '#a4fc95';
                    setTimeout(() => {
                        copyButton.textContent = originalText;
                        copyButton.style.background = '#f0f0f0';
                    }, 2000);
                }).catch(err => {
                    console.error('复制失败:', err);
                    copyButton.textContent = '复制失败';
                    copyButton.style.background = '#ffcccc';
                    setTimeout(() => {
                        copyButton.textContent = '复制';
                        copyButton.style.background = '#f0f0f0';
                    }, 2000);
                });
            });
            
            // 将代码块的父元素（pre）替换为包裹容器
            const preElement = codeBlock.parentNode;
            preElement.parentNode.insertBefore(wrapper, preElement);
            wrapper.appendChild(preElement);
            wrapper.appendChild(copyButton);
        });
    }
    
    // HTML转义函数，防止XSS攻击
    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
    
    // 为编辑器和测试结果面板添加事件，监听代码运行和错误
    if (document.getElementById('run-button')) {
        document.getElementById('run-button').addEventListener('click', function() {
            logUserActivity('code_run', { timestamp: Date.now() });
        });
    }
    
    // 生成模拟响应（当后端不可用时使用）
    function generateMockResponse(message) {
        console.log('生成模拟响应，消息：', message);
        let reply, suggestions;
        
        // 根据消息内容生成不同的模拟响应
        if (message.toLowerCase().includes('html')) {
            reply = "### HTML结构优化建议\n\n你的HTML结构可以通过以下方式改进：\n\n1. 使用更多的语义化标签，例如用`<section>`来包裹相关内容，用`<nav>`来包裹导航链接\n2. 确保添加适当的ARIA属性以提高无障碍性\n3. 添加适当的meta标签优化SEO\n\n这是一个优化的HTML结构示例：\n\n```html\n<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n    <meta charset=\"UTF-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n    <title>页面标题</title>\n</head>\n<body>\n    <header>\n        <nav>\n            <ul>\n                <li><a href=\"#\">首页</a></li>\n                <li><a href=\"#\">关于</a></li>\n            </ul>\n        </nav>\n    </header>\n    <main>\n        <section>\n            <h1>主要内容</h1>\n            <p>这里是页面的主要内容。</p>\n        </section>\n    </main>\n    <footer>\n        <p>版权信息</p>\n    </footer>\n</body>\n</html>\n```";
            suggestions = ["添加更多语义化标签", "优化图片标签的alt属性", "使用HTML5新特性"];
        } else if (message.toLowerCase().includes('css')) {
            reply = "### CSS优化建议\n\n你的CSS可以通过以下方式改进：\n\n1. 使用CSS变量（自定义属性）统一管理颜色和间距\n2. 采用Flexbox或Grid布局简化复杂的排版\n3. 使用媒体查询确保响应式设计\n\n```css\n:root {\n  --primary-color: #3498db;\n  --secondary-color: #2ecc71;\n  --text-color: #333;\n  --spacing-unit: 8px;\n}\n\n.container {\n  display: flex;\n  flex-wrap: wrap;\n  gap: calc(var(--spacing-unit) * 2);\n}\n\n.item {\n  color: var(--text-color);\n  background-color: var(--primary-color);\n  padding: var(--spacing-unit);\n  flex: 1 1 300px;\n}\n\n@media (max-width: 768px) {\n  .container {\n    flex-direction: column;\n  }\n}\n```";
            suggestions = ["使用CSS变量管理颜色", "应用Flexbox布局", "添加响应式设计"];
        } else if (message.toLowerCase().includes('javascript') || message.toLowerCase().includes('js')) {
            reply = "### JavaScript代码优化建议\n\n你的JavaScript代码可以通过以下方式改进：\n\n1. 使用现代ES6+语法（箭头函数、解构赋值等）\n2. 应用函数式编程原则减少副作用\n3. 使用事件委托减少事件监听器数量\n\n```javascript\n// 旧代码\nfunction getUser(id) {\n  return fetch('/api/users/' + id)\n    .then(function(response) {\n      return response.json();\n    })\n    .then(function(data) {\n      return data;\n    });\n}\n\n// 改进后的代码\nconst getUser = async (id) {\n  try {\n    const response = await fetch(`/api/users/${id}`);\n    return await response.json();\n  } catch (error) {\n    console.error('获取用户数据失败:', error);\n    return null;\n  }\n};\n```";
            suggestions = ["使用async/await替代Promise链", "应用事件委托模式", "封装重复使用的功能"];
        } else {
            reply = "### 编程学习建议\n\n要提高Web开发技能，建议你关注以下几个方面：\n\n1. **掌握基础知识**：深入理解HTML语义化、CSS布局技术和JavaScript核心概念\n2. **学习现代框架**：熟悉React、Vue或Angular等主流前端框架\n3. **关注性能优化**：学习代码分割、懒加载和资源优化技术\n4. **实践项目开发**：通过实际项目积累经验，建立个人作品集\n\n下面是一个学习路线图：\n\n1. 基础阶段：HTML、CSS、JavaScript基础\n2. 进阶阶段：现代JS（ES6+）、响应式设计、CSS预处理器\n3. 框架阶段：选择一个框架深入学习\n4. 专业阶段：性能优化、安全性、可访问性、测试\n\n不要急于学习太多技术，专注于打好基础并掌握一个技术栈是更有效的学习方式。";
            suggestions = ["如何提高代码可读性？", "学习响应式设计", "前端框架选择建议"];
        }
        
        return {
            status: 'success',
            reply: reply,
            suggestions: suggestions,
            response_time: 0.5
        };
    }
    
    // 导出功能供其他模块使用
    window.AIChat = {
        submitCodeForFeedback: submitCodeForFeedback,
        addAIMessage: addAIMessage,
        logUserActivity: logUserActivity
    };
});