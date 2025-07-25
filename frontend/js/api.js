/**
 * API 客户端
 * 封装与后端API交互的函数
 */

// 从环境变量或默认值获取后端端口
const backendPort = (typeof window !== 'undefined' && window.ENV_VARS) ? 
                   window.ENV_VARS.BACKEND_PORT : 
                   (typeof window !== 'undefined' && window.envConfig ? 
                    window.envConfig.get('BACKEND_PORT') : 8002);

// API基础URL
const API_BASE_URL = `http://localhost:${backendPort}/api`;

// API客户端对象
const ApiClient = {
    /**
     * 发送GET请求到API
     * @param {string} endpoint - API端点
     * @returns {Promise<Object>} - 响应数据
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            
            if (!response.ok) {
                throw new Error(`API错误: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`请求失败: ${endpoint}`, error);
            throw error;
        }
    },
    
    /**
     * 发送POST请求到API
     * @param {string} endpoint - API端点
     * @param {Object} data - 要发送的数据
     * @returns {Promise<Object>} - 响应数据
     */
    async post(endpoint, data) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`API错误: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`请求失败: ${endpoint}`, error);
            throw error;
        }
    },
    
    /**
     * 获取模块数据
     * @param {string} moduleName - 模块名称
     * @returns {Promise<Object>} - 模块数据
     */
    async getModule(moduleName) {
        return this.get(`/module/${moduleName}`);
    },
    
    /**
     * 向模块发送数据
     * @param {string} moduleName - 模块名称
     * @param {Object} data - 要发送的数据
     * @returns {Promise<Object>} - 模块响应
     */
    async sendToModule(moduleName, data) {
        return this.post(`/module/${moduleName}`, data);
    },
    
    /**
     * 检查API是否可用
     * @returns {Promise<boolean>} - API是否可用
     */
    async isAvailable() {
        try {
            const response = await this.get('/health');
            return response.status === 'ok';
        } catch (error) {
            console.error('API不可用:', error);
            return false;
        }
    }
};