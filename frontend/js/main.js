/**
 * AI HTML学习平台的主JavaScript文件
 * 包含所有页面通用的功能
 */

// 模块集成API
const ModuleAPI = {
    /**
     * 将模块加载到容器中
     * @param {string} moduleName - 模块名称
     * @param {string} containerId - 容器ID
     * @returns {Promise<Object>} - 模块数据
     */
    async loadModule(moduleName, containerId) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error(`容器 ${containerId} 未找到`);
                return;
            }
            
            // 从API获取模块数据
            const data = await ApiClient.getModule(moduleName);
            
            console.log(`模块 ${moduleName} 数据:`, data);
            
            // 在实际实现中，这将动态加载模块
            container.innerHTML = `<p>模块'${moduleName}'加载成功</p>`;
            
            // 如果需要，初始化模块
            if (window[`init${moduleName}Module`]) {
                window[`init${moduleName}Module`](container, data);
            }
            
            return data;
        } catch (error) {
            console.error(`加载模块 ${moduleName} 时出错:`, error);
            return null;
        }
    },
    
    /**
     * 向模块发送数据
     * @param {string} moduleName - 模块名称
     * @param {Object} data - 要发送的数据
     * @returns {Promise<Object>} - 响应数据
     */
    async sendToModule(moduleName, data) {
        try {
            return await ApiClient.sendToModule(moduleName, data);
        } catch (error) {
            console.error(`向模块 ${moduleName} 发送数据时出错:`, error);
            return null;
        }
    }
};

// 实用函数
const Utils = {
    /**
     * 为嵌入内容创建iframe
     * @param {string} containerId - 容器ID
     * @param {string} srcUrl - iframe源URL
     * @returns {HTMLIFrameElement|null} - 创建的iframe元素
     */
    createIframe(containerId, srcUrl) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        
        const iframe = document.createElement('iframe');
        iframe.src = srcUrl;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        
        container.innerHTML = '';
        container.appendChild(iframe);
        
        return iframe;
    },
    
    /**
     * 添加带错误处理的事件监听器
     * @param {HTMLElement} element - 元素
     * @param {string} event - 事件名称
     * @param {Function} callback - 回调函数
     */
    addSafeEventListener(element, event, callback) {
        if (!element) {
            console.error(`元素未找到，事件: ${event}`);
            return;
        }
        
        element.addEventListener(event, function(e) {
            try {
                callback(e);
            } catch (error) {
                console.error(`${event} 处理程序中出错:`, error);
            }
        });
    }
};

// 初始化任何通用功能
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI HTML学习平台已初始化');
    
    // 向当前导航链接添加活动类
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath.split('/').pop()) {
            link.classList.add('active');
        }
    });
    
    // 检查API可用性
    ApiClient.isAvailable()
        .then(available => {
            if (!available) {
                console.warn('警告: 后端API不可用。某些功能可能不工作。');
                // 可以在此处添加用户通知
            }
        })
        .catch(error => {
            console.error('检查API可用性时出错:', error);
        });
});