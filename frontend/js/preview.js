/**
 * 代码预览功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 初始化预览框架
    const previewFrame = document.getElementById('preview-frame');
    
    // 添加消息事件监听，来自iframe的消息
    window.addEventListener('message', function(event) {
        // 处理来自iframe的消息
        if (event.data && typeof event.data === 'object') {
            // 处理不同类型的消息
            if (event.data.type === 'log') {
                console.log('Preview log:', event.data.content);
                // logToAI('log', event.data.content);
            } else if (event.data.type === 'error') {
                console.error('Preview error:', event.data.content);
                // logToAI('error', event.data.content);
            } else if (event.data.type === 'warn') {
                console.warn('Preview warning:', event.data.content);
                // logToAI('warn', event.data.content);
            } else if (event.data.type === 'interaction') {
                console.log('Preview interaction:', event.data.action, event.data.data);
                // logInteraction(event.data.action, event.data.data);
            } else if (event.data.type === 'heartbeat') {
                // 心跳信息，可以用于检测预览是否正常
                // console.log('Preview heartbeat received');
                document.dispatchEvent(new CustomEvent('preview-heartbeat'));
            }
        } else if (event.data === 'preview-heartbeat') {
            // 兼容旧的心跳格式
            document.dispatchEvent(new CustomEvent('preview-heartbeat'));
        }
    });
    
    // 初始化预览心跳检测
    document.addEventListener('preview-heartbeat', function() {
        // 浏览器控制台可以查看此信息
        // console.log('Preview is active');
    });
    
    // 当iframe加载完成时注入远程控制脚本
    previewFrame.addEventListener('load', function() {
        try {
            // 注入消息传递脚本到iframe
            // 由于沙箱限制，我们不再直接操作iframe内容
            // 而是在HTML内容中已经添加了必要的脚本
        } catch (e) {
            console.error('Error setting up preview frame:', e);
        }
    });
    
    // 向AI助手发送日志（实际实现需与后端API集成）
    function logToAI(type, data) {
        // 后续实现与AI API的集成
        console.log(`[AI日志] 类型: ${type}, 数据: ${data}`);
    }
    
    // 向AI助手发送交互信息（实际实现需与后端API集成）
    function logInteraction(type, data) {
        // 后续实现与AI API的集成
        console.log(`[AI交互] 类型: ${type}, 数据:`, data);
    }
});