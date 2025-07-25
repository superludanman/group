/**
 * API接口模块 - 用于与主项目进行通信
 * 这个文件提供标准化的接口，用于集成到主项目中
 */

// IDE接口命名空间 - 防止全局变量污染
window.AICodeIDE = window.AICodeIDE || {};

/**
 * API接口类 - 提供与主项目通信的标准化方法
 */
AICodeIDE.API = (function() {
    // 私有变量
    let initialized = false;
    let messageHandlers = {};
    let apiConfig = {
        allowedOrigins: ['*'] // 默认允许所有来源，实际使用时应当限制
    };
    
    /**
     * 初始化API接口
     * @param {Object} config 配置对象
     */
    function initialize(config = {}) {
        if (initialized) {
            console.warn('API接口已经初始化');
            return;
        }
        
        // 合并配置
        apiConfig = Object.assign(apiConfig, config);
        
        // 设置跨窗口消息监听器
        window.addEventListener('message', handleExternalMessage);
        
        // 注册默认处理程序
        registerDefaultHandlers();
        
        initialized = true;
        console.log('IDE API接口已初始化');
        
        // 通知父窗口API已准备就绪
        sendReadyMessage();
    }
    
    /**
     * 处理来自外部的消息
     * @param {MessageEvent} event 消息事件
     */
    function handleExternalMessage(event) {
        // 验证消息来源
        if (apiConfig.allowedOrigins[0] !== '*' && 
            !apiConfig.allowedOrigins.includes(event.origin)) {
            console.warn(`拒绝来自未授权来源的消息: ${event.origin}`);
            return;
        }
        
        const { action, data } = event.data || {};
        
        // 忽略没有action的消息
        if (!action) return;
        
        console.log(`收到外部消息: ${action}`, data);
        
        // 查找并执行对应的处理程序
        if (messageHandlers[action]) {
            messageHandlers[action](data, event);
        } else {
            console.warn(`未找到消息处理程序: ${action}`);
        }
    }
    
    /**
     * 注册默认处理程序
     */
    function registerDefaultHandlers() {
        // 更新测试要求
        registerMessageHandler('updateTestRequirements', function(data) {
            if (!data || !data.content) {
                console.error('缺少测试要求内容');
                return { success: false, message: '缺少必要参数' };
            }
            
            try {
                const requirementsContent = document.getElementById('test-requirements-content');
                if (requirementsContent) {
                    requirementsContent.innerHTML = data.content;
                    return { success: true };
                } else {
                    return { success: false, message: '找不到测试要求容器' };
                }
            } catch (error) {
                console.error('更新测试要求失败:', error);
                return { success: false, message: error.message };
            }
        });
        
        // 更新测试结果
        registerMessageHandler('updateTestResults', function(data) {
            if (!data) {
                return { success: false, message: '缺少测试结果数据' };
            }
            
            try {
                // 如果提供了showTestResults函数，则使用它更新测试结果
                if (typeof window.showTestResults === 'function' && data.results) {
                    window.showTestResults(data.results);
                    return { success: true };
                }
                
                // 否则直接更新HTML内容
                if (data.content) {
                    const resultsContent = document.getElementById('test-results-content');
                    if (resultsContent) {
                        resultsContent.innerHTML = data.content;
                        
                        // 确保测试结果区域展开
                        const toggleResultsBtn = document.getElementById('toggle-results');
                        if (toggleResultsBtn && resultsContent.style.display === 'none') {
                            toggleResultsBtn.click();
                        }
                        
                        return { success: true };
                    } else {
                        return { success: false, message: '找不到测试结果容器' };
                    }
                }
                
                return { success: false, message: '缺少content或results参数' };
            } catch (error) {
                console.error('更新测试结果失败:', error);
                return { success: false, message: error.message };
            }
        });
        
        // 获取当前代码
        registerMessageHandler('getCode', function() {
            try {
                // 检查编辑器状态是否可用
                if (typeof window.editorState !== 'undefined') {
                    return {
                        success: true,
                        code: {
                            html: window.editorState.html || '',
                            css: window.editorState.css || '',
                            js: window.editorState.js || ''
                        }
                    };
                } else {
                    return { success: false, message: '编辑器状态不可用' };
                }
            } catch (error) {
                console.error('获取代码失败:', error);
                return { success: false, message: error.message };
            }
        });
        
        // 设置代码
        registerMessageHandler('setCode', function(data) {
            if (!data) {
                return { success: false, message: '缺少代码数据' };
            }
            
            try {
                // 检查编辑器实例和编辑器状态是否可用
                if (typeof window.editor === 'undefined' || 
                    typeof window.editorCSS === 'undefined' || 
                    typeof window.editorJS === 'undefined' || 
                    typeof window.editorState === 'undefined') {
                    return { success: false, message: '编辑器不可用' };
                }
                
                // 更新编辑器状态
                if (data.html !== undefined) {
                    window.editorState.html = data.html;
                    window.editor.setValue(data.html);
                }
                
                if (data.css !== undefined) {
                    window.editorState.css = data.css;
                    window.editorCSS.setValue(data.css);
                }
                
                if (data.js !== undefined) {
                    window.editorState.js = data.js;
                    window.editorJS.setValue(data.js);
                }
                
                // 更新预览
                if (typeof window.updateLocalPreview === 'function') {
                    window.updateLocalPreview();
                }
                
                return { success: true };
            } catch (error) {
                console.error('设置代码失败:', error);
                return { success: false, message: error.message };
            }
        });
    }
    
    /**
     * 注册消息处理程序
     * @param {string} action 动作名称
     * @param {Function} handler 处理函数
     */
    function registerMessageHandler(action, handler) {
        if (typeof handler !== 'function') {
            console.error(`处理程序必须是函数: ${action}`);
            return;
        }
        
        messageHandlers[action] = handler;
    }
    
    /**
     * 向父窗口发送消息
     * @param {string} action 动作名称
     * @param {*} data 数据
     */
    function sendMessage(action, data = {}) {
        if (!initialized) {
            console.warn('API接口尚未初始化');
            return;
        }
        
        if (window.parent && window.parent !== window) {
            window.parent.postMessage({ action, data }, '*');
            console.log(`向父窗口发送消息: ${action}`, data);
        } else {
            console.warn('找不到父窗口，无法发送消息');
        }
    }
    
    /**
     * 向父窗口发送API就绪消息
     */
    function sendReadyMessage() {
        sendMessage('ideReady', {
            version: '1.0.0',
            capabilities: ['updateTestRequirements', 'updateTestResults', 'getCode', 'setCode']
        });
    }
    
    /**
     * 暴露给外部直接调用的API函数
     */
    
    // 更新测试要求
    function updateTestRequirements(content) {
        return messageHandlers.updateTestRequirements({ content });
    }
    
    // 更新测试结果
    function updateTestResults(content) {
        return messageHandlers.updateTestResults({ content });
    }
    
    // 获取当前代码
    function getCode() {
        return messageHandlers.getCode();
    }
    
    // 设置代码
    function setCode(code) {
        return messageHandlers.setCode(code);
    }
    
    // 公开API
    return {
        initialize,
        registerMessageHandler,
        sendMessage,
        updateTestRequirements,
        updateTestResults,
        getCode,
        setCode
    };
})();

// 页面加载完成后自动初始化API
document.addEventListener('DOMContentLoaded', function() {
    // 可以从页面参数或配置中获取允许的来源
    const allowedOrigins = ['*']; // 在生产环境中应限制为特定域名
    
    AICodeIDE.API.initialize({
        allowedOrigins
    });
    
    console.log('IDE API模块已加载');
});