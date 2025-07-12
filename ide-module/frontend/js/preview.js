/**
 * 代码预览功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 初始化预览框架
    const previewFrame = document.getElementById('preview-frame');
    
    // 添加错误捕获
    previewFrame.addEventListener('load', function() {
        // 添加控制台输出捕获
        if (previewFrame.contentWindow) {
            const originalConsoleLog = previewFrame.contentWindow.console.log;
            const originalConsoleError = previewFrame.contentWindow.console.error;
            const originalConsoleWarn = previewFrame.contentWindow.console.warn;
            
            // 重写console.log
            previewFrame.contentWindow.console.log = function() {
                // 调用原始console.log
                originalConsoleLog.apply(this, arguments);
                
                // 捕获日志并发送给AI助手
                const logData = Array.from(arguments).map(arg => {
                    if (typeof arg === 'object') {
                        try {
                            return JSON.stringify(arg);
                        } catch (e) {
                            return String(arg);
                        }
                    }
                    return String(arg);
                }).join(' ');
                
                // 将日志发送给AI助手（示例实现）
                // logToAI('log', logData);
            };
            
            // 重写console.error
            previewFrame.contentWindow.console.error = function() {
                // 调用原始console.error
                originalConsoleError.apply(this, arguments);
                
                // 捕获错误并发送给AI助手
                const errorData = Array.from(arguments).map(arg => {
                    if (typeof arg === 'object') {
                        try {
                            return JSON.stringify(arg);
                        } catch (e) {
                            return String(arg);
                        }
                    }
                    return String(arg);
                }).join(' ');
                
                // 将错误发送给AI助手（示例实现）
                // logToAI('error', errorData);
            };
            
            // 重写console.warn
            previewFrame.contentWindow.console.warn = function() {
                // 调用原始console.warn
                originalConsoleWarn.apply(this, arguments);
                
                // 捕获警告并发送给AI助手
                const warnData = Array.from(arguments).map(arg => {
                    if (typeof arg === 'object') {
                        try {
                            return JSON.stringify(arg);
                        } catch (e) {
                            return String(arg);
                        }
                    }
                    return String(arg);
                }).join(' ');
                
                // 将警告发送给AI助手（示例实现）
                // logToAI('warn', warnData);
            };
        }
    });
    
    // 初始化DOM事件监听
    previewFrame.addEventListener('load', function() {
        if (previewFrame.contentWindow && previewFrame.contentWindow.document) {
            const frameDocument = previewFrame.contentWindow.document;
            
            // 监听所有DOM元素的点击事件
            frameDocument.addEventListener('click', function(event) {
                // 获取被点击元素的信息
                const elementInfo = getElementInfo(event.target);
                
                // 将点击信息发送给AI助手（示例实现）
                // logInteraction('click', elementInfo);
            }, true);
            
            // 监听表单提交事件
            frameDocument.addEventListener('submit', function(event) {
                // 防止表单实际提交
                event.preventDefault();
                
                // 获取表单信息
                const formInfo = getFormInfo(event.target);
                
                // 将表单提交信息发送给AI助手（示例实现）
                // logInteraction('submit', formInfo);
            }, true);
            
            // 可以添加更多事件监听，如键盘事件、焦点事件等
        }
    });
    
    // 获取HTML元素信息
    function getElementInfo(element) {
        if (!element) return null;
        
        try {
            // 收集元素的基本属性
            const info = {
                tagName: element.tagName.toLowerCase(),
                id: element.id || '',
                className: element.className || '',
                text: element.textContent ? element.textContent.substring(0, 50) : '',
                attributes: {}
            };
            
            // 收集所有属性
            for (let i = 0; i < element.attributes.length; i++) {
                const attr = element.attributes[i];
                info.attributes[attr.name] = attr.value;
            }
            
            return info;
        } catch (e) {
            console.error('获取元素信息出错：', e);
            return { error: e.message };
        }
    }
    
    // 获取表单信息
    function getFormInfo(formElement) {
        if (!formElement || formElement.tagName !== 'FORM') return null;
        
        try {
            const formData = new FormData(formElement);
            const formInfo = {
                id: formElement.id || '',
                name: formElement.name || '',
                method: formElement.method || 'get',
                action: formElement.action || '',
                fields: {}
            };
            
            // 收集表单字段
            for (let [name, value] of formData.entries()) {
                formInfo.fields[name] = value;
            }
            
            return formInfo;
        } catch (e) {
            console.error('获取表单信息出错：', e);
            return { error: e.message };
        }
    }
    
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