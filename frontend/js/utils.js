/**
 * 从坐标获取目标元素，排除工具栏自身元素
 * @param x 客户端X坐标
 * @param y 客户端Y坐标
 * @returns 坐标所在的HTML元素
 */
export function getElementAtPoint(x, y) {
    // 使用elementsFromPoint获取坐标处所有元素的堆栈
    const elementsStack = document.elementsFromPoint(x, y);
    // 寻找符合条件的第一个元素:
    // - 不在SVG内
    // - 不在选择器工具自身
    // - 确实在指定坐标内
    const refElement = elementsStack.find((element) => !element.closest('svg') &&
        !element.closest('.sw-selector') && // 自定义类名以避免与其他组件冲突
        isElementAtPoint(element, x, y)) || document.body;
    return refElement;
}
/**
 * 检查指定元素是否确实包含指定的点
 * @param element 要检查的元素
 * @param clientX X坐标
 * @param clientY Y坐标
 * @returns 如果元素包含该点则为true
 */
export function isElementAtPoint(element, clientX, clientY) {
    const boundingRect = element.getBoundingClientRect();
    const isInHorizontalBounds = clientX >= boundingRect.left &&
        clientX <= boundingRect.left + boundingRect.width;
    const isInVerticalBounds = clientY >= boundingRect.top &&
        clientY <= boundingRect.top + boundingRect.height;
    return isInHorizontalBounds && isInVerticalBounds;
}
/**
 * 计算点到元素的相对偏移百分比
 * @param element 参考元素
 * @param x X坐标
 * @param y Y坐标
 * @returns 偏移百分比
 */
export function getOffsetsFromPointToElement(element, x, y) {
    const elementBounds = element.getBoundingClientRect();
    const offsetTop = ((y - elementBounds.top) * 100) / elementBounds.height;
    const offsetLeft = ((x - elementBounds.left) * 100) / elementBounds.width;
    return {
        offsetTop,
        offsetLeft,
    };
}
/**
 * 生成元素的XPath，用于唯一定位元素
 * @param element 目标元素
 * @returns XPath字符串
 */
export function getElementXPath(element) {
    if (!element || element.nodeType !== Node.ELEMENT_NODE) {
        return '';
    }
    // 如果元素有id属性，直接使用id生成简短XPath
    if (element.id) {
        return `//*[@id="${element.id}"]`;
    }
    // 否则，需要通过节点位置生成完整路径
    const paths = [];
    // 循环向上查找父元素
    for (; element && element.nodeType === Node.ELEMENT_NODE; element = element.parentNode) {
        let index = 0;
        let hasFollowingSiblings = false;
        // 计算同类型的兄弟元素位置
        for (let sibling = element.previousSibling; sibling; sibling = sibling.previousSibling) {
            if (sibling.nodeType !== Node.ELEMENT_NODE)
                continue;
            if (sibling.tagName === element.tagName) {
                index++;
            }
        }
        // 检查是否有后续同类型兄弟元素
        for (let sibling = element.nextSibling; sibling && !hasFollowingSiblings; sibling = sibling.nextSibling) {
            if (sibling.nodeType !== Node.ELEMENT_NODE)
                continue;
            if (sibling.tagName === element.tagName) {
                hasFollowingSiblings = true;
            }
        }
        const tagName = element.tagName.toLowerCase();
        const pathIndex = (index || hasFollowingSiblings) ? `[${index + 1}]` : '';
        paths.unshift(tagName + pathIndex);
        // 如果遇到有id的元素，可以提前停止
        if (element.id) {
            paths.unshift(`*[@id="${element.id}"]`);
            break;
        }
    }
    return '/' + paths.join('/');
}
/**
 * 获取元素的基本信息，便于序列化传递
 * @param element 目标元素
 * @returns 元素的JSON表示
 */
export function getElementInfo(element) {
    const bbox = element.getBoundingClientRect();
    return {
        selector: getElementXPath(element),
        outerHTML: element.outerHTML.slice(0, 500), // 限制长度，避免过大
        bbox: {
            x: bbox.left,
            y: bbox.top,
            width: bbox.width,
            height: bbox.height
        },
        tagName: element.tagName.toLowerCase(),
        id: element.id || undefined,
        classList: Array.from(element.classList),
        pageURL: window.location.href
    };
}
