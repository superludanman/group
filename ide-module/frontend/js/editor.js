/**
 * Monaco编辑器初始化和管理
 */
document.addEventListener('DOMContentLoaded', function() {
    // 编辑器状态
    let editorState = {
        activeTab: 'html',
        html: '<div class="demo">\n  <h1>欢迎使用HTML编辑器</h1>\n  <p>这是一个用于学习HTML、CSS和JavaScript的在线编辑器。</p>\n  <button id="demo-button">点击我</button>\n</div>',
        css: '.demo {\n  max-width: 600px;\n  margin: 20px auto;\n  padding: 20px;\n  font-family: Arial, sans-serif;\n  background-color: #f7f7f7;\n  border-radius: 8px;\n  box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n}\n\nh1 {\n  color: #10a37f;\n}\n\nbutton {\n  background-color: #10a37f;\n  color: white;\n  border: none;\n  padding: 8px 16px;\n  border-radius: 4px;\n  cursor: pointer;\n}\n\nbutton:hover {\n  background-color: #0e906f;\n}',
        js: 'document.getElementById("demo-button").addEventListener("click", function() {\n  alert("按钮被点击了！");\n});'
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
            updatePreview();
        });

        // 刷新预览按钮
        document.getElementById('refresh-preview').addEventListener('click', function() {
            updatePreview();
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

    // 更新预览
    function updatePreview() {
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

    // 重置编辑器
    function resetEditor() {
        // 重置编辑器状态
        editorState = {
            activeTab: 'html',
            html: '<div class="demo">\n  <h1>欢迎使用HTML编辑器</h1>\n  <p>这是一个用于学习HTML、CSS和JavaScript的在线编辑器。</p>\n  <button id="demo-button">点击我</button>\n</div>',
            css: '.demo {\n  max-width: 600px;\n  margin: 20px auto;\n  padding: 20px;\n  font-family: Arial, sans-serif;\n  background-color: #f7f7f7;\n  border-radius: 8px;\n  box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n}\n\nh1 {\n  color: #10a37f;\n}\n\nbutton {\n  background-color: #10a37f;\n  color: white;\n  border: none;\n  padding: 8px 16px;\n  border-radius: 4px;\n  cursor: pointer;\n}\n\nbutton:hover {\n  background-color: #0e906f;\n}',
            js: 'document.getElementById("demo-button").addEventListener("click", function() {\n  alert("按钮被点击了！");\n});'
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
        updatePreview();
    }

    // 初始化预览
    setTimeout(updatePreview, 1000);
});