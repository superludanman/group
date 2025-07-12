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
        // 引入编程语言支持
        const jsDefaults = monaco.languages.typescript.javascriptDefaults;
        
        // 配置JS语言特性
        jsDefaults.setCompilerOptions({
            target: monaco.languages.typescript.ScriptTarget.ES2016,
            allowNonTsExtensions: true,
            moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
            module: monaco.languages.typescript.ModuleKind.CommonJS,
            noEmit: true,
            typeRoots: ["node_modules/@types"],
            jsx: monaco.languages.typescript.JsxEmit.React
        });

        // 启用JS语言的语法和语义验证
        jsDefaults.setDiagnosticsOptions({
            noSemanticValidation: false,
            noSyntaxValidation: false,
            diagnosticCodesToIgnore: [1005, 1068, 1109]
        });

        // 添加DOM类型定义
        jsDefaults.addExtraLib(
        `declare var document: {
            createElement(tagName: string): HTMLElement;
            querySelector(selectors: string): HTMLElement;
            querySelectorAll(selectors: string): HTMLElement[];
            getElementById(elementId: string): HTMLElement;
            body: HTMLElement;
        };

        interface HTMLElement {
            appendChild(node: HTMLElement): HTMLElement;
            innerHTML: string;
            style: any;
            onclick: Function;
            value: string;
            addEventListener(event: string, listener: Function): void;
        };

        declare var console: {
            log(...args: any[]): void;
            error(...args: any[]): void;
            warn(...args: any[]): void;
        };

        declare var window: {
            alert(message: string): void;
            addEventListener(event: string, listener: Function): void;
        };
        `, 'ts:dom.d.ts');
        
        // 配置编辑器主题
        monaco.editor.defineTheme('myCustomTheme', {
            base: 'vs',
            inherit: true,
            rules: [
                { token: 'comment', foreground: '008800', fontStyle: 'italic' },
                { token: 'keyword', foreground: '0000ff', fontStyle: 'bold' },
                { token: 'string', foreground: 'aa6600' },
                { token: 'number', foreground: '116644' },
                { token: 'identifier', foreground: '000000' },
                { token: 'type', foreground: '267f99' },
                { token: 'delimiter', foreground: '000000' },
                { token: 'delimiter.parenthesis', foreground: '000000' },
                { token: 'delimiter.curly', foreground: '000000' },
                { token: 'operator', foreground: '000000' },
                { token: 'function', foreground: '795e26' }
            ],
            colors: {
                'editor.background': '#f9f9f9',
                'editor.lineHighlightBackground': '#f0f0f0',
                'editorLineNumber.foreground': '#999999',
                'editor.selectionBackground': '#c0ddff',
                'editor.inactiveSelectionBackground': '#e5ebf1',
                'editorError.foreground': '#ff0000',
                'editorWarning.foreground': '#ffa500',
                'editorInfo.foreground': '#008800'
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
            formatOnPaste: true,
            formatOnType: true,
            autoIndent: 'full',
            semanticHighlighting: true,
            suggestOnTriggerCharacters: true,
            acceptSuggestionOnCommitCharacter: true,
            wordBasedSuggestions: true,
            parameterHints: { enabled: true },
            folding: true,
            renderValidationDecorations: 'on',
            fontSize: 14,
            fontFamily: "'Fira Code', Consolas, 'Courier New', monospace",
            fontLigatures: true,
            cursorBlinking: 'smooth'
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
                    
                    // 如果是JS标签页，启用特定的JS检查和格式化
                    if (tab === 'js') {
                        // 重新配置编辑器，使用全功能JS模式
                        const oldModel = editor.getModel();
                        const newModel = monaco.editor.createModel(editorState[tab], 'javascript');
                        editor.setModel(newModel);
                        oldModel.dispose(); // 处理旧模型以避免内存泄漏
                        
                        // 启用编辑器的JS语法高亮和检查
                        monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
                            noSemanticValidation: false,
                            noSyntaxValidation: false,
                            diagnosticCodesToIgnore: [1005, 1068, 1109]
                        });
                        
                        // 配置编辑器选项
                        editor.updateOptions({
                            suggestOnTriggerCharacters: true,
                            wordBasedSuggestions: true,
                            snippetSuggestions: 'inline',
                            suggest: {
                                showFunctions: true,
                                showVariables: true,
                                showClasses: true,
                                showWords: true,
                                showMethods: true,
                                showProperties: true
                            }
                        });
                        
                        // 如果编辑器已有内容，执行立即检查
                        if (editorState[tab] && editorState[tab].trim().length > 0) {
                            setTimeout(performStaticCheck, 300);
                        }
                    }
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
        try {
            // 添加心跳和消息传递功能的脚本
            const consoleOverrideScript = `
                // 重写控制台方法，安全地传递给父窗口
                (function() {
                    const originalConsoleLog = console.log;
                    const originalConsoleError = console.error;
                    const originalConsoleWarn = console.warn;
                    
                    // 重写console.log
                    console.log = function() {
                        originalConsoleLog.apply(this, arguments);
                        try {
                            const logData = Array.from(arguments).map(arg => {
                                if (typeof arg === 'object') {
                                    try { return JSON.stringify(arg); }
                                    catch (e) { return String(arg); }
                                }
                                return String(arg);
                            }).join(' ');
                            window.parent.postMessage({ type: 'log', content: logData }, '*');
                        } catch (e) { /* 忽略错误 */ }
                    };
                    
                    // 重写console.error
                    console.error = function() {
                        originalConsoleError.apply(this, arguments);
                        try {
                            const errorData = Array.from(arguments).map(arg => {
                                if (typeof arg === 'object') {
                                    try { return JSON.stringify(arg); }
                                    catch (e) { return String(arg); }
                                }
                                return String(arg);
                            }).join(' ');
                            window.parent.postMessage({ type: 'error', content: errorData }, '*');
                        } catch (e) { /* 忽略错误 */ }
                    };
                    
                    // 重写console.warn
                    console.warn = function() {
                        originalConsoleWarn.apply(this, arguments);
                        try {
                            const warnData = Array.from(arguments).map(arg => {
                                if (typeof arg === 'object') {
                                    try { return JSON.stringify(arg); }
                                    catch (e) { return String(arg); }
                                }
                                return String(arg);
                            }).join(' ');
                            window.parent.postMessage({ type: 'warn', content: warnData }, '*');
                        } catch (e) { /* 忽略错误 */ }
                    };
                    
                    // 添加事件监听
                    document.addEventListener('click', function(event) {
                        try {
                            const element = event.target;
                            const elementInfo = {
                                tagName: element.tagName.toLowerCase(),
                                id: element.id || '',
                                className: element.className || '',
                                text: element.textContent ? element.textContent.substring(0, 50) : ''
                            };
                            window.parent.postMessage({ 
                                type: 'interaction', 
                                action: 'click', 
                                data: elementInfo 
                            }, '*');
                        } catch (e) { /* 忽略错误 */ }
                    });
                    
                    // 发送心跳信号，防止连接中断
                    function sendHeartbeat() {
                        try {
                            window.parent.postMessage({ type: 'heartbeat' }, '*');
                        } catch (e) { /* 忽略错误 */ }
                    }
                    
                    // 立即发送一次心跳，然后每秒发送一次
                    sendHeartbeat();
                    setInterval(sendHeartbeat, 1000);
                })();
            `;
            
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
                        ${consoleOverrideScript}
                        
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

            // 直接写入Blob URL来避免跨域问题
            const blob = new Blob([content], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            previewFrame.src = url;
            
            // 清理旧的Blob URL
            previewFrame.onload = function() {
                URL.revokeObjectURL(url);
            };
            
            // 改进的心跳检测机制
            if (!window.hasHeartbeatListener) {
                // 使用自定义事件来接收心跳
                document.addEventListener('preview-heartbeat', function() {
                    window.lastPreviewHeartbeatTime = Date.now();
                    // 收到心跳，预览正常
                    console.log('预览心跳正常');
                });
                window.hasHeartbeatListener = true;
            }
            
            // 初始化心跳时间
            window.lastPreviewHeartbeatTime = Date.now();
            
            // 添加预览框架心跳检测
            if (window.localPreviewHeartbeatInterval) {
                clearInterval(window.localPreviewHeartbeatInterval);
            }
            
            window.localPreviewHeartbeatInterval = setInterval(() => {
                const currentTime = Date.now();
                const heartbeatTimeout = 8000; // 心跳超时时间，单位毫秒
                
                // 如果超过超时时间没有心跳，则重新加载预览
                if (currentTime - window.lastPreviewHeartbeatTime > heartbeatTimeout) {
                    console.log('预览心跳超时，尝试重新加载');
                    
                    // 尝试保持当前页面的段落和滚动位置
                    try {
                        // 更新预览
                        updateLocalPreview();
                        
                        // 重置心跳时间为当前时间
                        window.lastPreviewHeartbeatTime = currentTime;
                    } catch (e) {
                        console.error('重新加载预览出错:', e);
                    }
                }
            }, 2000); // 每2秒检查一次
        } catch (error) {
            console.error('生成预览出错:', error);
            showNotification('预览生成错误', 'error');
        }
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
        
        // 执行静态检查
        performStaticCheck();
        
        // 立即更新本地预览，提高响应速度
        updateLocalPreview();
        
        // 显示消息提示用户正在连接到后端
        showNotification('预览已更新，正在连接到沙箱环境...', 'info', 1000);
        
        // 准备代码提交数据
        const codeData = {
            html: editorState.html,
            css: editorState.css,
            js: editorState.js,
            session_id: editorState.sessionId
        };
        
        // 尝试调用后端API，异步连接到沙箱环境
        fetch(`${editorState.backendUrl}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(codeData),
            // 设置超时，快速失败如果后端不可达
            timeout: 2000
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
                    // 如果预览URL可用，更新到后端预览
                    updatePreviewWithBackendUrl(data.local_url || data.preview_url);
                    // 显示成功消息
                    showNotification('代码已在沙箱环境中运行', 'success');
                }
                // 注意：这里不再调用本地预览，因为我们已经在开始时调用过了
            } else {
                // 显示错误消息
                showNotification(`沙箱环境运行错误: ${data.message || '未知错误'}`, 'error');
                // 注意：不再调用本地预览，因为我们已经在开始时调用过了
            }
        })
        .catch(error => {
            console.error('运行代码出错:', error);
            showNotification(`沙箱环境连接错误，使用本地预览模式`, 'info');
            // 注意：不再调用本地预览，因为我们已经在开始时调用过了
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
        
        // 添加30秒的心跳检查，确保预览保持连接
        if (window.previewHeartbeatInterval) {
            clearInterval(window.previewHeartbeatInterval);
        }
        
        window.previewHeartbeatInterval = setInterval(() => {
            // 检查iframe是否可访问
            try {
                if (!previewFrame.contentWindow || previewFrame.contentWindow.closed) {
                    // 预览窗口不可访问，尝试重新加载
                    console.log('预览窗口不可访问，尝试重新加载');
                    previewFrame.src = url;
                }
            } catch (e) {
                // 跨域错误或其他错误，尝试重新加载
                console.log('预览窗口出错，尝试重新加载');
                previewFrame.src = url;
            }
        }, 5000); // 每5秒检查一次
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
        try {
            // 先进行前端静态检查
            const frontendErrors = [];
            const frontendWarnings = [];
            
            // HTML检查例子
            if (editorState.html.includes('</div>') && !editorState.html.includes('<div')) {
                frontendErrors.push({
                    line: editorState.html.split('\n').findIndex(line => line.includes('</div>')) + 1,
                    column: editorState.html.split('\n').find(line => line.includes('</div>')).indexOf('</div>') + 1,
                    message: 'HTML错误: 发现关闭标签</div>但没有对应的打开标签'
                });
            }
            
            // CSS检查例子
            if (editorState.css.includes('{') && !editorState.css.includes('}')) {
                frontendWarnings.push({
                    line: editorState.css.split('\n').findIndex(line => line.includes('{')) + 1,
                    column: editorState.css.split('\n').find(line => line.includes('{')).indexOf('{') + 1,
                    message: 'CSS警告: 发现没有关闭的大括号'
                });
            }
            
            // JavaScript检查增强
            if (editorState.activeTab === 'js') {
                const jsCode = editorState.js;
                
                // 检查括号匹配
                if ((jsCode.match(/\(/g) || []).length !== (jsCode.match(/\)/g) || []).length) {
                    frontendErrors.push({
                        line: 1,
                        column: 1,
                        message: 'JavaScript错误: 括号不匹配'
                    });
                }
                
                // 检查花括号匹配
                if ((jsCode.match(/\{/g) || []).length !== (jsCode.match(/\}/g) || []).length) {
                    frontendErrors.push({
                        line: 1,
                        column: 1,
                        message: 'JavaScript错误: 花括号不匹配'
                    });
                }
                
                // 检查方括号匹配
                if ((jsCode.match(/\[/g) || []).length !== (jsCode.match(/\]/g) || []).length) {
                    frontendErrors.push({
                        line: 1,
                        column: 1,
                        message: 'JavaScript错误: 方括号不匹配'
                    });
                }
                
                // 检查常见的语法错误模式
                if (jsCode.includes('var ') && jsCode.includes('let ')) {
                    frontendWarnings.push({
                        line: jsCode.split('\n').findIndex(line => line.includes('var ')) + 1,
                        column: 1,
                        message: 'JavaScript警告: 混合使用var和let可能引起变量作用域混乱'
                    });
                }
                
                // 检查未定义变量调用
                const variablePattern = /\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=/g;
                const calledVariables = Array.from(jsCode.matchAll(/\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(/g), m => m[1]);
                const definedVariables = Array.from(jsCode.matchAll(variablePattern), m => m[1]);
                
                // 排除内置函数
                const builtInFunctions = ['console', 'alert', 'document', 'window', 'parseInt', 'parseFloat', 'setTimeout', 'setInterval'];
                
                calledVariables.forEach(variable => {
                    if (!definedVariables.includes(variable) && !builtInFunctions.includes(variable)) {
                        frontendWarnings.push({
                            line: jsCode.split('\n').findIndex(line => line.includes(variable + '(')) + 1,
                            column: jsCode.split('\n').find(line => line.includes(variable + '(')).indexOf(variable),
                            message: `JavaScript警告: 可能调用了未定义的函数 '${variable}'`
                        });
                    }
                });
                
                // 检查没有完成的语句
                if (jsCode.trim().endsWith(';') && jsCode.trim().length > 1) {
                    frontendWarnings.push({
                        line: jsCode.split('\n').length,
                        column: jsCode.split('\n').pop().length,
                        message: 'JavaScript警告: 可能存在未完成的代码语句'
                    });
                }
            }
            
            // 显示前端检查结果
            showStaticCheckResults(frontendErrors, frontendWarnings);
            
            // 尝试调用后端静态检查 API
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
                body: JSON.stringify(codeData),
                // 设置超时，快速失败如果后端不可达
                timeout: 1000
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
                    // 合并前端和后端的错误和警告
                    const combinedErrors = [...frontendErrors, ...(data.errors || [])];
                    const combinedWarnings = [...frontendWarnings, ...(data.warnings || [])];
                    showStaticCheckResults(combinedErrors, combinedWarnings);
                }
            })
            .catch(error => {
                console.error('静态检查出错:', error);
                // 当后端静态检查失败时，保留前端检查结果
                // 静态检查失败时不显示错误通知，以免干扰用户
            });
        } catch (error) {
            console.error('静态检查错误:', error);
        }
    }
    
    // 显示静态检查结果
    function showStaticCheckResults(errors, warnings) {
        // 先清除所有现有的错误标记
        if (window.currentDecorations) {
            editor.deltaDecorations(window.currentDecorations, []);
        }
        
        // 准备新的装饰
        const decorations = [];
        const model = editor.getModel();
        
        // 如果没有错误或警告，则只清除装饰
        if (errors.length === 0 && warnings.length === 0) {
            window.currentDecorations = [];
            return;
        }
        
        // 创建VSCode风格的问题面板
        const problemsDiv = document.getElementById('problems-panel') || createProblemsPanel();
        problemsDiv.innerHTML = ''; // 清空现有内容
        
        // 添加错误标题
        if (errors.length > 0) {
            const errorHeader = document.createElement('div');
            errorHeader.className = 'problem-category';
            errorHeader.innerHTML = `<span class="problem-icon error">⚠️</span> 错误 (${errors.length})`;
            problemsDiv.appendChild(errorHeader);
            
            // 处理错误
            errors.forEach((error, index) => {
                if (error.line && error.column) {
                    // 创建错误装饰
                    const lineLength = model.getLineLength(error.line) || 1;
                    const endColumn = Math.min(error.column + 10, lineLength);
                    
                    decorations.push({
                        range: new monaco.Range(error.line, error.column, error.line, endColumn),
                        options: {
                            inlineClassName: 'monaco-error-squiggle',
                            hoverMessage: { value: error.message },
                            overviewRuler: {
                                color: '#FF0000',
                                position: monaco.editor.OverviewRulerLane.Right
                            },
                            minimap: {
                                color: '#FF0000',
                                position: monaco.editor.MinimapPosition.Inline
                            }
                        }
                    });
                    
                    // 添加到问题面板
                    const problemItem = document.createElement('div');
                    problemItem.className = 'problem-item';
                    problemItem.innerHTML = `
                        <span class="problem-icon error">⛔</span>
                        <span class="problem-message">${error.message}</span>
                        <span class="problem-location">[${error.line}:${error.column}]</span>
                    `;
                    problemItem.addEventListener('click', () => {
                        editor.revealPositionInCenter({ lineNumber: error.line, column: error.column });
                        editor.setPosition({ lineNumber: error.line, column: error.column });
                        editor.focus();
                    });
                    problemsDiv.appendChild(problemItem);
                }
            });
        }
        
        // 添加警告标题
        if (warnings.length > 0) {
            const warningHeader = document.createElement('div');
            warningHeader.className = 'problem-category';
            warningHeader.innerHTML = `<span class="problem-icon warning">⚠</span> 警告 (${warnings.length})`;
            problemsDiv.appendChild(warningHeader);
            
            // 处理警告
            warnings.forEach((warning, index) => {
                if (warning.line && warning.column) {
                    // 创建警告装饰
                    const lineLength = model.getLineLength(warning.line) || 1;
                    const endColumn = Math.min(warning.column + 10, lineLength);
                    
                    decorations.push({
                        range: new monaco.Range(warning.line, warning.column, warning.line, endColumn),
                        options: {
                            inlineClassName: 'monaco-warning-squiggle',
                            hoverMessage: { value: warning.message },
                            overviewRuler: {
                                color: '#FFA500',
                                position: monaco.editor.OverviewRulerLane.Right
                            },
                            minimap: {
                                color: '#FFA500',
                                position: monaco.editor.MinimapPosition.Inline
                            }
                        }
                    });
                    
                    // 添加到问题面板
                    const problemItem = document.createElement('div');
                    problemItem.className = 'problem-item';
                    problemItem.innerHTML = `
                        <span class="problem-icon warning">⚠</span>
                        <span class="problem-message">${warning.message}</span>
                        <span class="problem-location">[${warning.line}:${warning.column}]</span>
                    `;
                    problemItem.addEventListener('click', () => {
                        editor.revealPositionInCenter({ lineNumber: warning.line, column: warning.column });
                        editor.setPosition({ lineNumber: warning.line, column: warning.column });
                        editor.focus();
                    });
                    problemsDiv.appendChild(problemItem);
                }
            });
        }
        
        // 应用装饰
        window.currentDecorations = editor.deltaDecorations(window.currentDecorations || [], decorations);
        
        // 显示问题面板
        if (errors.length > 0 || warnings.length > 0) {
            problemsDiv.style.display = 'block';
        }
    }
    
    // 创建问题面板
    function createProblemsPanel() {
        const problemsDiv = document.createElement('div');
        problemsDiv.id = 'problems-panel';
        problemsDiv.className = 'problems-panel';
        
        // 添加标题栏
        const titleBar = document.createElement('div');
        titleBar.className = 'problems-titlebar';
        titleBar.innerHTML = `
            <span class="problems-title">问题</span>
            <button class="problems-close">×</button>
        `;
        problemsDiv.appendChild(titleBar);
        
        // 添加关闭按钮事件
        titleBar.querySelector('.problems-close').addEventListener('click', () => {
            problemsDiv.style.display = 'none';
        });
        
        // 添加到页面
        document.querySelector('.editor-container').appendChild(problemsDiv);
        
        return problemsDiv;
    }
    
    // 显示通知消息
    function showNotification(message, type = 'info', duration = 3000) {
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
        }, duration);
    }
    
    // 初始化预览
    setTimeout(updateLocalPreview, 1000);
    
    // CSS样式注入
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        /* Monaco Editor 错误和警告样式 */
        .monaco-error-squiggle {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 6 3' enable-background='new 0 0 6 3' height='3' width='6'%3E%3Cg fill='%23ff0000'%3E%3Cpolygon points='5.5,0 2.5,3 1.1,3 4.1,0'/%3E%3Cpolygon points='4,0 6,2 6,0.6 5.4,0'/%3E%3Cpolygon points='0,2 1,3 2.4,3 0,0.6'/%3E%3C/g%3E%3C/svg%3E") repeat-x bottom left;
        }

        .monaco-warning-squiggle {
            background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 6 3' enable-background='new 0 0 6 3' height='3' width='6'%3E%3Cg fill='%23ffa500'%3E%3Cpolygon points='5.5,0 2.5,3 1.1,3 4.1,0'/%3E%3Cpolygon points='4,0 6,2 6,0.6 5.4,0'/%3E%3Cpolygon points='0,2 1,3 2.4,3 0,0.6'/%3E%3C/g%3E%3C/svg%3E") repeat-x bottom left;
        }

        /* 问题面板样式 */
        .problems-panel {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 150px;
            background-color: #f8f8f8;
            border-top: 1px solid #e0e0e0;
            z-index: 10;
            overflow-y: auto;
            display: none;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 12px;
            color: #333;
        }

        .problems-titlebar {
            padding: 5px 10px;
            background-color: #eee;
            border-bottom: 1px solid #ddd;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .problems-title {
            font-weight: bold;
        }

        .problems-close {
            background: none;
            border: none;
            font-size: 16px;
            cursor: pointer;
            color: #777;
        }

        .problems-close:hover {
            color: #000;
        }

        .problem-category {
            padding: 5px 10px;
            background-color: #f0f0f0;
            font-weight: bold;
            border-bottom: 1px solid #ddd;
        }

        .problem-item {
            padding: 5px 10px 5px 30px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            display: flex;
            align-items: center;
        }

        .problem-item:hover {
            background-color: #e8e8e8;
        }

        .problem-icon {
            margin-right: 6px;
        }

        .problem-message {
            flex-grow: 1;
        }

        .problem-location {
            color: #777;
            margin-left: 10px;
        }

        .notification {
            transition: opacity 0.5s ease;
            opacity: 1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
    `;
    document.head.appendChild(styleElement);
});