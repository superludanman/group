/**
 * Monaco编辑器初始化和管理
 */
document.addEventListener('DOMContentLoaded', function() {
    // 编辑器状态
    let editorState = {
        activeTab: 'html',
        html: '<div class="demo">\n  <h1>欢迎使用HTML编辑器</h1>\n  <p>这是一个用于学习HTML、CSS和JavaScript的在线编辑器。</p>\n  <button id="demo-button">点击我</button>\n</div>',
        css: '.demo {\n  max-width: 600px;\n  margin: 20px auto;\n  padding: 20px;\n  font-family: Arial, sans-serif;\n  background-color: #f7f7f7;\n  border-radius: 8px;\n  box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n}\n\nh1 {\n  color: #10a37f;\n}\n\nbutton {\n  background-color: #10a37f;\n  color: white;\n  border: none;\n  padding: 8px 16px;\n  border-radius: 4px;\n  cursor: pointer;\n}\n\nbutton:hover {\n  background-color: #0e906f;\n}',
        js: 'document.getElementById("demo-button").addEventListener("click", function() {\n  alert("按钮被点击了！");\n});',
        sessionId: null,
        isRunning: false,
        backendUrl: 'http://localhost:8080' // 后端API地址
    };

    // 编辑器实例
    let editor = null;

    // 初始化Monaco编辑器
    require(['vs/editor/editor.main'], function() {
        // 配置编辑器主题
        monaco.editor.defineTheme('myCustomTheme', {
            base: 'vs',
            inherit: true,
            rules: [],
            colors: {
                'editor.background': '#f9f9f9',
                'editor.lineHighlightBackground': '#f0f0f0',
                'editorLineNumber.foreground': '#999999',
                'editor.selectionBackground': '#c0ddff',
            }
        });

        // 创建编辑器实例
        editor = monaco.editor.create(document.getElementById('monaco-editor'), {
            value: editorState.html,
            language: 'html',
            theme: 'myCustomTheme',
            automaticLayout: true,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            renderLineHighlight: 'all',
            renderWhitespace: 'none',
            lineNumbers: 'on',
            tabSize: 2,
        });

        // 监听编辑器内容变化
        editor.onDidChangeModelContent(function(e) {
            // 保存当前编辑器内容到状态
            editorState[editorState.activeTab] = editor.getValue();
            
            // 添加防抖，避免频繁请求
            clearTimeout(window.staticCheckTimer);
            window.staticCheckTimer = setTimeout(function() {
                performStaticCheck();
            }, 1000); // 1秒后执行静态检查
        });

        // 初始化编辑器标签切换
        initEditorTabs();

        // 初始化按钮事件
        initButtons();
    });

    // 初始化编辑器标签切换
    function initEditorTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tab = this.getAttribute('data-tab');
                
                // 保存当前编辑器内容
                if (editor) {
                    editorState[editorState.activeTab] = editor.getValue();
                }
                
                // 更新活动标签
                editorState.activeTab = tab;
                
                // 更新标签按钮状态
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // 更新编辑器内容和语言
                if (editor) {
                    const model = editor.getModel();
                    monaco.editor.setModelLanguage(model, tab);
                    editor.setValue(editorState[tab]);
                }
            });
        });
    }

    // 初始化按钮事件
    function initButtons() {
        // 运行按钮
        document.getElementById('run-button').addEventListener('click', function() {
            runCodeOnBackend();
        });

        // 刷新预览按钮
        document.getElementById('refresh-preview').addEventListener('click', function() {
            updateLocalPreview();
        });

        // 重置按钮
        document.getElementById('reset-button').addEventListener('click', function() {
            if (confirm('确定要重置编辑器吗？所有更改将丢失。')) {
                resetEditor();
            }
        });

        // 移动端菜单切换
        document.querySelector('.mobile-menu-toggle').addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('mobile-open');
        });
    }

    // 本地预览更新（仅用于快速刷新和初始化）
    function updateLocalPreview() {
        const previewFrame = document.getElementById('preview-frame');
        const content = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    ${editorState.css}
                </style>
            </head>
            <body>
                ${editorState.html}
                <script>
                    try {
                        ${editorState.js}
                    } catch (error) {
                        console.error('JavaScript错误:', error);
                        const errorDiv = document.createElement('div');
                        errorDiv.style.position = 'fixed';
                        errorDiv.style.bottom = '10px';
                        errorDiv.style.left = '10px';
                        errorDiv.style.right = '10px';
                        errorDiv.style.padding = '10px';
                        errorDiv.style.backgroundColor = '#ffebee';
                        errorDiv.style.color = '#c62828';
                        errorDiv.style.border = '1px solid #ef9a9a';
                        errorDiv.style.borderRadius = '4px';
                        errorDiv.style.zIndex = '9999';
                        errorDiv.textContent = 'JavaScript错误: ' + error.message;
                        document.body.appendChild(errorDiv);
                    }
                </script>
            </body>
            </html>
        `;

        // 获取预览框架的文档对象
        const frameDoc = previewFrame.contentDocument || previewFrame.contentWindow.document;
        
        // 写入HTML内容
        frameDoc.open();
        frameDoc.write(content);
        frameDoc.close();
    }
    
    // 在后端运行代码并更新预览
    function runCodeOnBackend() {
        if (editorState.isRunning) {
            return; // 防止重复点击
        }
        
        // 设置运行状态
        editorState.isRunning = true;
        const runButton = document.getElementById('run-button');
        runButton.textContent = '运行中...';
        runButton.disabled = true;
        
        // 准备代码提交数据
        const codeData = {
            html: editorState.html,
            css: editorState.css,
            js: editorState.js,
            session_id: editorState.sessionId
        };
        
        // 调用后端API
        fetch(`${editorState.backendUrl}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(codeData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`服务器响应错误: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // 处理成功响应
            if (data.status === 'success') {
                // 保存会话ID以供后续请求使用
                editorState.sessionId = data.container_id;
                
                // 更新预览框
                if (data.preview_url) {
                    updatePreviewWithBackendUrl(data.local_url || data.preview_url);
                } else {
                    // 如果没有预览URL，使用本地预览
                    updateLocalPreview();
                }
                
                // 显示成功消息
                showNotification('代码已成功运行', 'success');
            } else {
                // 显示错误消息
                showNotification(`运行错误: ${data.message || '未知错误'}`, 'error');
                // 使用本地预览作为备选
                updateLocalPreview();
            }
        })
        .catch(error => {
            console.error('运行代码出错:', error);
            showNotification(`请求错误: ${error.message}`, 'error');
            // 出错时使用本地预览
            updateLocalPreview();
        })
        .finally(() => {
            // 重置运行状态
            editorState.isRunning = false;
            runButton.textContent = '运行';
            runButton.disabled = false;
        });
    }
    
    // 使用后端URL更新预览框
    function updatePreviewWithBackendUrl(url) {
        const previewFrame = document.getElementById('preview-frame');
        previewFrame.src = url;
    }

    // 重置编辑器
    function resetEditor() {
        // 重置编辑器状态
        editorState = {
            activeTab: 'html',
            html: '<div class="demo">\n  <h1>欢迎使用HTML编辑器</h1>\n  <p>这是一个用于学习HTML、CSS和JavaScript的在线编辑器。</p>\n  <button id="demo-button">点击我</button>\n</div>',
            css: '.demo {\n  max-width: 600px;\n  margin: 20px auto;\n  padding: 20px;\n  font-family: Arial, sans-serif;\n  background-color: #f7f7f7;\n  border-radius: 8px;\n  box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n}\n\nh1 {\n  color: #10a37f;\n}\n\nbutton {\n  background-color: #10a37f;\n  color: white;\n  border: none;\n  padding: 8px 16px;\n  border-radius: 4px;\n  cursor: pointer;\n}\n\nbutton:hover {\n  background-color: #0e906f;\n}',
            js: 'document.getElementById("demo-button").addEventListener("click", function() {\n  alert("按钮被点击了！");\n});',
            sessionId: null,
            isRunning: false,
            backendUrl: 'http://localhost:8080'
        };

        // 更新编辑器内容
        if (editor) {
            const model = editor.getModel();
            monaco.editor.setModelLanguage(model, 'html');
            editor.setValue(editorState.html);
        }

        // 更新标签按钮状态
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(btn => btn.classList.remove('active'));
        document.querySelector('[data-tab="html"]').classList.add('active');

        // 更新预览
        updateLocalPreview();
        
        // 清理后端会话
        if (editorState.sessionId) {
            fetch(`${editorState.backendUrl}/cleanup/${editorState.sessionId}`, {
                method: 'POST'
            }).catch(error => console.error('清理会话失败:', error));
        }
    }

    // 执行静态检查
    function performStaticCheck() {
        // 准备代码提交数据
        const codeData = {
            html: editorState.html,
            css: editorState.css,
            js: editorState.js,
            session_id: editorState.sessionId
        };
        
        // 调用后端API
        fetch(`${editorState.backendUrl}/static-check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(codeData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`服务器响应错误: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // 处理静态检查结果
            if (data.status === 'success') {
                showStaticCheckResults(data.errors || [], data.warnings || []);
            }
        })
        .catch(error => {
            console.error('静态检查出错:', error);
            // 静态检查失败时不显示错误通知，以免干扰用户
        });
    }
    
    // 显示静态检查结果
    function showStaticCheckResults(errors, warnings) {
        // 将来可以实现在编辑器中显示错误和警告
        if (errors.length > 0 || warnings.length > 0) {
            // 添加编辑器装饰，显示错误和警告
            const model = editor.getModel();
            const decorations = [];
            
            // 处理错误
            errors.forEach(error => {
                if (error.line && error.column) {
                    decorations.push({
                        range: new monaco.Range(error.line, error.column, error.line, error.column + 1),
                        options: {
                            isWholeLine: true,
                            className: 'monaco-error-line',
                            hoverMessage: { value: error.message }
                        }
                    });
                }
            });
            
            // 处理警告
            warnings.forEach(warning => {
                if (warning.line && warning.column) {
                    decorations.push({
                        range: new monaco.Range(warning.line, warning.column, warning.line, warning.column + 1),
                        options: {
                            isWholeLine: true,
                            className: 'monaco-warning-line',
                            hoverMessage: { value: warning.message }
                        }
                    });
                }
            });
            
            // 应用装饰
            if (decorations.length > 0) {
                editor.deltaDecorations([], decorations);
            }
        }
    }
    
    // 显示通知消息
    function showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // 添加到页面
        document.body.appendChild(notification);
        
        // 添加样式
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.right = '20px';
        notification.style.padding = '10px 15px';
        notification.style.borderRadius = '4px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '200px';
        notification.style.textAlign = 'center';
        
        // 根据类型设置样式
        if (type === 'success') {
            notification.style.backgroundColor = '#d4edda';
            notification.style.color = '#155724';
            notification.style.border = '1px solid #c3e6cb';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#f8d7da';
            notification.style.color = '#721c24';
            notification.style.border = '1px solid #f5c6cb';
        } else {
            notification.style.backgroundColor = '#d1ecf1';
            notification.style.color = '#0c5460';
            notification.style.border = '1px solid #bee5eb';
        }
        
        // 自动移除
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s ease';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }
    
    // 初始化预览
    setTimeout(updateLocalPreview, 1000);
    
    // CSS样式注入
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .monaco-error-line {
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 2px solid red;
        }
        .monaco-warning-line {
            background-color: rgba(255, 255, 0, 0.1);
            border-left: 2px solid orange;
        }
        .notification {
            transition: opacity 0.5s ease;
            opacity: 1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
    `;
    document.head.appendChild(styleElement);
});