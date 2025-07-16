/**
 * 测试结果展示功能
 */
document.addEventListener('DOMContentLoaded', function() {
    // 全局暴露显示测试结果函数
    window.showTestResults = function() {
        const resultsContent = document.getElementById('test-results-content');
        if (!resultsContent) return;
        
        // 清空现有内容
        resultsContent.innerHTML = '';
        
        // 从编辑器获取当前代码
        const htmlCode = typeof editorState !== 'undefined' ? editorState.html : '';
        const cssCode = typeof editorState !== 'undefined' ? editorState.css : '';
        const jsCode = typeof editorState !== 'undefined' ? editorState.js : '';
        
        // 模拟测试分析
        const testResults = analyzeCode(htmlCode, cssCode, jsCode);
        
        // 显示整体测试状态
        const statusDiv = document.createElement('div');
        statusDiv.className = `test-status ${testResults.pass ? 'pass' : 'fail'}`;
        statusDiv.textContent = testResults.pass ? '测试通过' : '测试失败';
        resultsContent.appendChild(statusDiv);
        
        // 添加测试详情
        testResults.items.forEach(item => {
            const resultItem = document.createElement('div');
            resultItem.className = `result-item ${item.status}`;
            resultItem.innerHTML = `
                <span class="result-icon">${item.status === 'success' ? '✓' : '✗'}</span>
                <span class="result-message">${item.message}</span>
            `;
            resultsContent.appendChild(resultItem);
        });
        
        // 确保测试结果区域展开
        const toggleResultsBtn = document.getElementById('toggle-results');
        if (toggleResultsBtn && resultsContent.style.display === 'none') {
            toggleResultsBtn.click();
        }
    };
    
    /**
     * 分析代码并返回测试结果
     */
    function analyzeCode(html, css, js) {
        const results = {
            pass: false,
            items: []
        };
        
        // 检查HTML
        if (html.includes('<h1>') || html.includes('<h2>') || html.includes('<h3>')) {
            results.items.push({
                status: 'success',
                message: '标题元素已正确实现'
            });
        } else {
            results.items.push({
                status: 'error',
                message: '缺少标题元素，请添加h1-h6标签'
            });
        }
        
        // 检查按钮
        if (html.includes('<button')) {
            results.items.push({
                status: 'success',
                message: '按钮元素已添加'
            });
        } else {
            results.items.push({
                status: 'error',
                message: '缺少按钮元素'
            });
        }
        
        // 检查CSS
        if (css.includes('color') || css.includes('background')) {
            results.items.push({
                status: 'success',
                message: 'CSS样式已正确应用'
            });
        } else {
            results.items.push({
                status: 'warning',
                message: '建议添加更多样式，如颜色或背景'
            });
        }
        
        // 检查JS
        if (js.includes('addEventListener')) {
            results.items.push({
                status: 'success',
                message: '事件监听器已正确实现'
            });
        } else {
            results.items.push({
                status: 'error',
                message: '缺少事件监听器，请使用addEventListener'
            });
        }
        
        // 判断整体测试是否通过
        const errors = results.items.filter(item => item.status === 'error');
        results.pass = errors.length === 0;
        
        return results;
    }
});