# IDE Module - AI HTML学习平台

该模块提供了一个在线代码编辑器，支持HTML、CSS和JavaScript的编辑、预览和AI辅助学习功能。

## 功能特点

- Monaco编辑器集成（与VS Code相同的编辑器引擎）
- 实时代码预览
- 多标签编辑（HTML/CSS/JavaScript）
- AI辅助对话功能
- 代码错误捕获和显示
- 响应式界面设计

## 目录结构

```
ide-module/
├── backend/              # 后端服务
│   ├── Dockerfile        # 代码沙箱环境
│   ├── requirements.txt  # Python依赖
│   └── app.py            # FastAPI应用
├── frontend/             # 前端静态文件
│   ├── css/              # 样式文件
│   │   └── styles.css    # 主样式表
│   ├── js/               # JavaScript文件
│   │   ├── editor.js     # Monaco编辑器配置
│   │   ├── preview.js    # 代码预览功能
│   │   └── ai-chat.js    # AI对话功能
│   └── index.html        # 主页面
└── README.md             # 文档
```

## 安装和运行

### 前端

前端部分使用纯HTML、CSS和JavaScript编写，无需构建步骤。Monaco编辑器通过CDN加载。

1. 直接在浏览器中打开`frontend/index.html`文件即可使用基本功能。
2. 若要启用后端功能（如AI助手和代码执行），需要同时运行后端服务。

### 后端

后端使用Python的FastAPI框架开发。

1. 安装依赖：
   ```
   cd backend
   pip install -r requirements.txt
   ```

2. 运行服务：
   ```
   uvicorn app:app --reload --host 0.0.0.0 --port 8080
   ```

### Docker沙箱环境

沙箱环境使用Docker容器进行隔离，确保代码执行的安全性。

1. 构建Docker镜像：
   ```
   cd backend
   export https_proxy=http://127.0.0.1:7897
   export http_proxy=http://127.0.0.1:7897
   docker build -t ide-module-sandbox .
   ```

2. 运行Docker容器：
   ```
   docker run -p 8080:8080 ide-module-sandbox
   ```

## 集成指南

该模块设计为可独立运行，也可集成到主项目中。集成步骤：

1. **前端集成**：
   - 复制`frontend`目录下的文件到主项目对应位置
   - 修改`index.html`文件以符合主项目模板
   - 调整API端点路径以匹配主项目结构

2. **后端集成**：
   - 将`backend/app.py`中的API路由集成到主项目的FastAPI应用中
   - 调整Docker配置以匹配主项目环境
   - 确保依赖项在主项目中可用

## API接口

后端提供以下API接口：

- `GET /` - 健康检查端点
- `POST /execute` - 执行代码并返回结果
- `POST /ai/chat` - 与AI助手聊天
- `POST /static-check` - 对代码进行静态检查

## 后续开发计划

1. 完善AI助手功能，集成实际的AI API
2. 实现Docker沙箱的完整代码执行环境
3. 添加代码片段库和模板
4. 改进错误处理和调试功能
5. 增加用户代码保存和加载功能

## 注意事项

- Docker构建时需要在宿主机上设置代理：
  ```
  export https_proxy=http://127.0.0.1:7897
  export http_proxy=http://127.0.0.1:7897
  ```
- 在生产环境中，应限制CORS设置并添加适当的安全措施
- AI助手目前使用模拟响应，实际部署时需替换为真实API调用