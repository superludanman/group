/**
 * 修改建议 AI对话功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // AI聊天状态
    const chatState = {
        messages: [],
        isWaitingForResponse: false,
        backendUrl: 'http://localhost:8080', // 后端API地址，根据实际情况修改
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

    // DOM元素
    const suggestionsContainer = document.querySelector('.suggestions-container');
    const chatMessages = document.getElementById('ai-chat-messages');
    const userMessageInput = document.getElementById('user-message');
    const sendMessageButton = document.getElementById('send-message');

    // 初始化事件监听
    initChatEvents();
    
    // 初始化用户行为跟踪
    initUserBehaviorTracking();

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

    
    // 实际的AI API调用
    async function callAIAPI(message) {
        try {
            // 获取当前代码状态
            const codeState = {
                html: typeof editorState !== 'undefined' ? editorState.html : '',
                css: typeof editorState !== 'undefined' ? editorState.css : '',
                js: typeof editorState !== 'undefined' ? editorState.js : ''
            };
            
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

            const data = await response.json();
            
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
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
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
    
    // HTML转义函数，防止XSS攻击
    function escapeHtml(unsafe) {
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
    
    // 导出功能供其他模块使用
    window.AIChat = {
        submitCodeForFeedback: submitCodeForFeedback,
        addAIMessage: addAIMessage,
        logUserActivity: logUserActivity
    };
});