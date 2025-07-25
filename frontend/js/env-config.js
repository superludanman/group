/**
 * 前端环境变量配置
 * 该模块提供从环境变量或默认值获取配置参数的功能
 */

// 默认配置
const defaultConfig = {
    BACKEND_PORT: 8002,
    IDE_MODULE_PORT: 8080,
    FRONTEND_PORT: 9000
};

// 从全局变量或默认值获取配置
function getConfig(key) {
    // 首先检查全局变量（由启动脚本设置或可用于测试）
    if (typeof window !== 'undefined' && typeof window[key] !== 'undefined') {
        return window[key];
    }
    
    // 然后检查环境变量（通过构建工具注入）
    if (typeof process !== 'undefined' && process.env && process.env[key]) {
        return process.env[key];
    }
    
    // 最后使用默认值
    return defaultConfig[key];
}

// 获取所有配置
function getAllConfig() {
    return {
        BACKEND_PORT: getConfig('BACKEND_PORT'),
        IDE_MODULE_PORT: getConfig('IDE_MODULE_PORT'),
        FRONTEND_PORT: getConfig('FRONTEND_PORT')
    };
}

// 导出公共API
window.envConfig = {
    get: getConfig,
    getAll: getAllConfig
};

// 在页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('环境配置已加载:', getAllConfig());
});