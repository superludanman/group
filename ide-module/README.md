# IDE 模块

这是一个轻量级的Web IDE模块，用于HTML、CSS和JavaScript的在线编辑和预览。该模块设计为可独立运行，也可集成到主项目中，提供代码编辑、预览和测试功能。

## 功能特点

- Monaco编辑器集成（与VS Code相同的编辑器引擎）
- 多标签页编辑（HTML、CSS、JavaScript、预览）
- 实时代码预览
- 测试要求和测试结果显示
- AI辅助修改建议
- 响应式界面设计
- 标准化API接口，方便与主项目集成

## 目录结构

```
ide-module/
├── backend/                # 后端服务
│   ├── Dockerfile          # 后端服务容器
│   ├── docker_manager.py   # Docker容器管理
│   ├── code_executor.py    # 代码执行服务
│   ├── app.py              # FastAPI应用
│   ├── requirements.txt    # 依赖项
│   ├── start.sh            # 启动脚本
│   ├── stop.sh             # 停止脚本
│   ├── .env.example        # 环境变量示例
│   └── sandbox/            # 沙箱环境
│       ├── Dockerfile.sandbox  # 沙箱容器
│       └── entrypoint.sh    # 容器入口脚本
├── frontend/               # 前端静态文件
│   ├── css/                # 样式文件
│   │   └── styles.css      # 主样式表
│   ├── js/                 # JavaScript文件
│   │   ├── editor.js       # Monaco编辑器配置
│   │   ├── preview.js      # 代码预览功能
│   │   ├── ai-chat.js      # AI对话功能
│   │   ├── toggle-panels.js # 面板折叠功能
│   │   ├── test-results.js  # 测试结果显示
│   │   └── api-interface.js # 与主项目通信的API接口
│   ├── index.html          # 主页面
│   └── demo.html           # API演示页面
└── README.md               # 文档
```

## 安装和运行

### 前提条件

- Docker 已安装并正在运行（如需后端功能）
- 现代浏览器（Chrome、Firefox、Edge等）

### 前端

前端部分使用纯HTML、CSS和JavaScript编写，无需构建步骤。Monaco编辑器通过CDN加载。

1. 直接在浏览器中打开`frontend/index.html`文件即可使用基本功能。
2. 若要启用后端功能（如AI助手和代码执行），需要同时运行后端服务。
3. 要查看API演示，可以打开`frontend/demo.html`。

### 后端与Docker沙箱

1. 配置环境变量：

   ```bash
   cd backend
   cp .env.example .env
   # 根据需要编辑.env文件
   ```

2. 使用启动脚本运行服务：

   ```bash
   cd backend
   
   # 设置代理（如果需要）
   export https_proxy=http://127.0.0.1:7897
   export http_proxy=http://127.0.0.1:7897
   
   # 使脚本可执行
   chmod +x start.sh stop.sh
   
   # 构建Docker镜像并启动服务
   ./start.sh
   ```

3. 停止服务：

   ```bash
   cd backend
   ./stop.sh
   ```

## API接口

### 后端 API

后端提供以下API接口：

- `GET /` - 健康检查端点
- `GET /containers` - 列出所有活动容器
- `POST /execute` - 执行代码并返回结果
- `POST /static-check` - 对代码进行静态检查
- `POST /ai/chat` - 与AI助手聊天
- `POST /cleanup/{session_id}` - 清理会话相关资源

### 前端 JavaScript API

在前端，我们提供了一个标准化的JavaScript API接口，用于与主项目通信。所有API都通过`window.AICodeIDE.API`对象暴露。

#### 初始化API

```javascript
AICodeIDE.API.initialize({
    allowedOrigins: ['https://example.com'] // 允许的来源域名
});
```

#### 更新测试要求

```javascript
// 直接在JavaScript中调用
AICodeIDE.API.updateTestRequirements('<div>新的测试要求内容</div>');

// 或通过跨窗口消息
window.postMessage({
    action: 'updateTestRequirements',
    data: {
        content: '<div>新的测试要求内容</div>'
    }
}, '*');
```

#### 更新测试结果

```javascript
// 直接在JavaScript中调用
AICodeIDE.API.updateTestResults('<div class="result-item success">测试通过</div>');

// 或通过跨窗口消息
window.postMessage({
    action: 'updateTestResults',
    data: {
        content: '<div class="result-item success">测试通过</div>'
    }
}, '*');

// 或传递结构化测试结果对象
window.postMessage({
    action: 'updateTestResults',
    data: {
        results: {
            pass: true,
            items: [
                { status: 'success', message: '标题元素已正确实现' },
                { status: 'error', message: '缺少按钮元素' }
            ]
        }
    }
}, '*');
```

#### 获取代码

```javascript
// 直接在JavaScript中调用
const { success, code } = AICodeIDE.API.getCode();
if (success) {
    console.log(code.html, code.css, code.js);
}

// 或通过跨窗口消息
window.postMessage({
    action: 'getCode',
    data: {}
}, '*');
// 需要监听返回消息
```

#### 设置代码

```javascript
// 直接在JavaScript中调用
AICodeIDE.API.setCode({
    html: '<div>Hello</div>',
    css: 'div { color: red; }',
    js: 'console.log("Hello");'
});

// 或通过跨窗口消息
window.postMessage({
    action: 'setCode',
    data: {
        html: '<div>Hello</div>',
        css: 'div { color: red; }',
        js: 'console.log("Hello");'
    }
}, '*');
```

## 集成指南

该模块设计为可独立运行，也可集成到主项目中。集成步骤：

### 使用iframe集成

最简单的集成方式是使用iframe将IDE模块嵌入到主项目中：

```html
<iframe id="ide-frame" src="/path/to/ide-module/frontend/index.html"></iframe>

<script>
    const ideFrame = document.getElementById('ide-frame');
    
    // 监听IDE就绪消息
    window.addEventListener('message', function(event) {
        if (event.data.action === 'ideReady') {
            console.log('IDE已就绪', event.data);
            
            // 设置测试要求
            ideFrame.contentWindow.postMessage({
                action: 'updateTestRequirements',
                data: {
                    content: '<p>完成以下任务：...</p>'
                }
            }, '*');
        }
    });
    
    // 获取代码
    function getCodeFromIDE() {
        ideFrame.contentWindow.postMessage({
            action: 'getCode',
            data: {}
        }, '*');
    }
    
    // 监听IDE返回的代码
    window.addEventListener('message', function(event) {
        if (event.data.action === 'getCodeResponse') {
            console.log('获取到代码', event.data);
        }
    });
</script>
```

### 直接集成

如果需要更深度的集成：

1. **前端集成**：
   - 复制`frontend`目录下的文件到主项目对应位置
   - 修改`index.html`文件以符合主项目模板
   - 调整API端点路径以匹配主项目结构

2. **后端集成**：
   - 将`backend`目录中的Python模块集成到主项目的FastAPI应用中
   - 调整Docker配置以匹配主项目环境
   - 确保依赖项在主项目中可用

## 测试结果状态显示

测试结果支持以下状态：

- `success`: 成功/通过 (绿色)
- `error`: 错误/失败 (红色)
- `warning`: 警告 (黄色)

可以使用以下HTML结构显示测试结果：

```html
<div class="result-item success">
    <span class="result-icon">✓</span>
    <span class="result-message">测试通过</span>
</div>

<div class="result-item error">
    <span class="result-icon">✗</span>
    <span class="result-message">测试失败</span>
</div>

<div class="result-item warning">
    <span class="result-icon">⚠</span>
    <span class="result-message">测试警告</span>
</div>
```

## 注意事项

- Docker构建时需要在宿主机上设置代理：
  ```
  export https_proxy=http://127.0.0.1:7897
  export http_proxy=http://127.0.0.1:7897
  ```
- 在生产环境中，应限制CORS设置并添加适当的安全措施
- 应当限制`allowedOrigins`以只接受来自指定域名的消息
- AI助手目前使用模拟响应，实际部署时需替换为真实API调用
- 默认情况下，测试结果区域是折叠的，更新测试结果时会自动展开
- API就绪后会向父窗口发送`ideReady`消息，建议在收到此消息后再进行交互

## 后续开发计划

1. 改进AI助手功能，集成实际的AI API
2. 增强代码静态检查功能
3. 添加代码片段库和模板
4. 实现用户代码保存和加载功能
5. 优化Docker容器池管理，提高性能