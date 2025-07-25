import { ElementSelector } from './element-selector.js';
// 定义消息类型常量
export const MESSAGE_TYPES = {
    START: 'SW_SELECT_START',
    STOP: 'SW_SELECT_STOP',
    CHOSEN: 'SW_SELECT_CHOSEN',
};
/**
 * 在嵌入页中初始化元素选择器
 * 监听来自父页面的消息，并控制选择器的启动和停止
 */
export function initIframeSelector(options = {}) {
    const { allowed = true, allowedOrigins = ['*'], customStyles = {}, allowedTags = [] } = options;
    // 如果不允许被调用，直接返回空函数
    if (!allowed) {
        return () => { };
    }
    let selector = null;
    // 消息处理函数
    const handleMessage = (event) => {
        // 验证来源
        if (allowedOrigins[0] !== '*' && !allowedOrigins.includes(event.origin)) {
            return;
        }
        // 尝试解析消息数据
        let message;
        try {
            message = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        }
        catch (e) {
            // 非JSON消息，忽略
            return;
        }
        // 处理消息类型
        switch (message.type) {
            case MESSAGE_TYPES.START:
                // 启动选择器
                if (selector) {
                    // 已存在选择器，先销毁
                    selector.stop();
                }
                // 类型守卫，确保message类型为SelectStartMessage
                const startMessage = message;
                selector = new ElementSelector({
                    ignoreSelectors: startMessage.ignore,
                    allowedTags: startMessage.allowedTags || allowedTags, // 新增
                    onElementSelected: (element, info) => {
                        // 选中元素后，向父页面发送信息
                        window.parent.postMessage({
                            type: MESSAGE_TYPES.CHOSEN,
                            payload: info
                        }, '*');
                    }
                });
                selector.start();
                break;
            case MESSAGE_TYPES.STOP:
                // 停止选择器
                if (selector) {
                    selector.stop();
                    selector = null;
                }
                break;
        }
    };
    // 添加消息监听
    window.addEventListener('message', handleMessage);
    // 返回清理函数
    return () => {
        window.removeEventListener('message', handleMessage);
        if (selector) {
            selector.stop();
            selector = null;
        }
    };
}
/**
 * 在主站点创建选择器桥接
 * 用于控制iframe中的元素选择器
 */
export function createSelectorBridge(options) {
    const { iframeWindow, targetOrigin = '*', ignoreSelectors = ['.sw-selector', '.sw-highlight'], onChosen, onError } = options;
    // 验证iframe窗口
    if (!iframeWindow) {
        throw new Error('Invalid iframe window');
    }
    // 消息处理函数
    const handleMessage = (event) => {
        // 尝试解析消息数据
        let message;
        try {
            message = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        }
        catch (e) {
            return;
        }
        // 处理元素选中消息
        if (message.type === MESSAGE_TYPES.CHOSEN && onChosen) {
            // 类型守卫，确保message类型为SelectChosenMessage
            const chosenMessage = message;
            onChosen(chosenMessage.payload);
        }
    };
    // 添加消息监听
    window.addEventListener('message', handleMessage);
    // 返回控制API
    return {
        /**
         * 启动选择器
         */
        start(allowedTags = []) {
            try {
                iframeWindow.postMessage({
                    type: MESSAGE_TYPES.START,
                    ignore: ignoreSelectors,
                    allowedTags // 新增
                }, targetOrigin);
            }
            catch (error) {
                if (onError) {
                    onError(error instanceof Error ? error : new Error(String(error)));
                }
            }
        },
        /**
         * 停止选择器
         */
        stop() {
            try {
                iframeWindow.postMessage({
                    type: MESSAGE_TYPES.STOP
                }, targetOrigin);
            }
            catch (error) {
                if (onError) {
                    onError(error instanceof Error ? error : new Error(String(error)));
                }
            }
        },
        /**
         * 销毁桥接
         */
        destroy() {
            window.removeEventListener('message', handleMessage);
        }
    };
}
