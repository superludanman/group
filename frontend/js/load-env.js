/**
 * 前端环境变量加载脚本
 * 该脚本通过AJAX请求从服务器获取环境变量配置
 */

// 定义默认环境变量
const defaultEnv = {
    BACKEND_PORT: 8000,
    IDE_MODULE_PORT: 8080,
    FRONTEND_PORT: 9000,
    PREVIEW_PORT: 8081,
    OPENAI_API_BASE: 'https://api.openai.com/v1',
    OPENAI_MODEL: 'gpt-4o-mini',
    OPENAI_MAX_TOKENS: 1024,
    OPENAI_TEMPERATURE: 0.7
};

// 存储环境变量的对象
window.ENV_VARS = {...defaultEnv};

/**
 * 从服务器获取环境变量
 */
async function loadEnvVars() {
    try {
        // 尝试从服务器获取环境变量
        const response = await fetch('/api/env');
        if (response.ok) {
            const serverEnv = await response.json();
            // 合并服务器环境变量和默认环境变量
            window.ENV_VARS = {...defaultEnv, ...serverEnv};
        } else {
            console.warn('无法从服务器获取环境变量，使用默认值');
        }
    } catch (error) {
        console.warn('加载环境变量时出错，使用默认值:', error);
    }
    
    // 将环境变量设置为全局变量，保持与现有代码的兼容性
    window.BACKEND_PORT = window.ENV_VARS.BACKEND_PORT;
    window.IDE_MODULE_PORT = window.ENV_VARS.IDE_MODULE_PORT;
    window.FRONTEND_PORT = window.ENV_VARS.FRONTEND_PORT;
    window.PREVIEW_PORT = window.ENV_VARS.PREVIEW_PORT;
    
    console.log('环境变量已加载:', window.ENV_VARS);
}

// 在页面加载时自动加载环境变量
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadEnvVars);
} else {
    loadEnvVars();
}