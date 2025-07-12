# IDE Module - AI HTML学习平台

该模块提供了一个在线代码编辑器，支持HTML、CSS和JavaScript的编辑、预览和AI辅助学习功能。整合了Docker沙箱环境用于安全执行用户代码。

## 功能特点

- Monaco编辑器集成（与VS Code相同的编辑器引擎）
- 实时代码预览
- Docker沙箱环境用于安全执行代码
- 多标签编辑（HTML/CSS/JavaScript）
- AI辅助对话功能
- 代码错误捕获和显示
- 响应式界面设计

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
│   │   └── ai-chat.js      # AI对话功能
│   └── index.html          # 主页面
└── README.md               # 文档
```

## 安装和运行

### 前提条件

- Docker 已安装并正在运行
- Python 3.8+ 
- Node.js 16+ (用于沙箱环境)

### 前端

前端部分使用纯HTML、CSS和JavaScript编写，无需构建步骤。Monaco编辑器通过CDN加载。

1. 直接在浏览器中打开`frontend/index.html`文件即可使用基本功能。
2. 若要启用后端功能（如AI助手和代码执行），需要同时运行后端服务。

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

### 构建和保存Docker镜像

如果想要预构建Docker镜像以便快速启动：

```bash
cd backend
# 仅构建镜像
./start.sh --build-only

# 构建并保存镜像到文件
./start.sh --build-only --save-images
```

保存的镜像可以在没有网络连接的情况下加载：

```bash
# 加载镜像
docker load -i sandbox_image.tar
```

## API接口

后端提供以下API接口：

- `GET /` - 健康检查端点
- `GET /containers` - 列出所有活动容器
- `POST /execute` - 执行代码并返回结果
- `POST /static-check` - 对代码进行静态检查
- `POST /ai/chat` - 与AI助手聊天
- `POST /cleanup/{session_id}` - 清理会话相关资源

## 集成指南

该模块设计为可独立运行，也可集成到主项目中。集成步骤：

1. **前端集成**：
   - 复制`frontend`目录下的文件到主项目对应位置
   - 修改`index.html`文件以符合主项目模板
   - 调整API端点路径以匹配主项目结构

2. **后端集成**：
   - 将`backend`目录中的Python模块集成到主项目的FastAPI应用中
   - 调整Docker配置以匹配主项目环境
   - 确保依赖项在主项目中可用

## 注意事项

- Docker构建时需要在宿主机上设置代理：
  ```
  export https_proxy=http://127.0.0.1:7897
  export http_proxy=http://127.0.0.1:7897
  ```
- 在生产环境中，应限制CORS设置并添加适当的安全措施
- AI助手目前使用模拟响应，实际部署时需替换为真实API调用
- 默认情况下，沙箱容器在5分钟不活动后自动清理

## 后续开发计划

1. 改进AI助手功能，集成实际的AI API
2. 增强代码静态检查功能
3. 添加代码片段库和模板
4. 实现用户代码保存和加载功能
5. 优化Docker容器池管理，提高性能