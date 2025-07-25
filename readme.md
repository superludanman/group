# AI动态闭环学习系统

## 项目结构

```
.
├── backend/                # 后端代码
│   ├── app/                # FastAPI应用
│   │   ├── api/            # API端点
│   │   ├── core/           # 核心功能和配置
│   │   ├── modules/        # 可扩展模块系统
│   │   └── main.py         # 主应用入口
│   ├── requirements.txt    # 后端依赖
│   └── run.py              # 启动脚本
│
├── frontend/               # 前端代码
│   ├── css/                # CSS样式表
│   │   ├── main.css        # 基本样式
│   │   └── template.css    # 模板样式
│   ├── js/                 # JavaScript文件
│   ├── images/             # 图像资源
│   ├── pages/              # HTML页面
│   │   └── preview-example.html  # 示例实现
│   ├── template.html       # 主模板文件
│   ├── template-blank.html # 空白集成模板
│   └── index.html          # 首页
|
├── Git团队协作指南.md       
├── 模块集成指南.md         
└── 前端模板使用指南.md    
```

## 开始使用

### 前提条件

- Python 3.8或更高版本
- pip（Python包管理器）
- 现代网页浏览器

### 安装

1. 克隆仓库
2. 为后端创建虚拟环境：
   ```
   cd backend
   python -m venv venv
   ```
3. 激活虚拟环境：
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. 安装后端依赖：
   ```
   pip install -r requirements.txt
   ```

### 运行应用

1. 启动后端：
   ```
   cd backend
   python run.py
   ```
   后端服务器将在http://localhost:8002上可用（默认端口，可通过.env文件配置）

2. 打开前端：
   - 直接在浏览器中打开`frontend/index.html`文件
   - 或者使用简单的HTTP服务器：
     ```
     cd frontend
     python -m http.server 9000
     ```
     然后访问http://localhost:9000（默认端口，可通过.env文件配置）

## 前后端分离架构

本项目采用前后端分离的架构，便于团队协作和扩展：

1. **后端（Backend）**：
   - 使用FastAPI框架
   - 提供RESTful API
   - 包含模块系统，允许团队成员添加新功能
   - 在端口8002上运行（默认，可通过.env文件配置）

2. **前端（Frontend）**：
   - 纯HTML、CSS和JavaScript
   - 通过API与后端通信
   - 可以独立于后端开发和部署
   - 可以在任何静态文件服务器上运行

## 前端设计

1. **竖向进度导航**：
   - 左侧固定的垂直导航栏
   - 清晰显示学习流程中的各个步骤
   - 自动标记已完成和当前步骤

2. **简约设计风格**：
   - 简洁的色彩方案（主色调：#10a37f）
   - 清晰的视觉层次
   - 专注于内容的布局
   - 响应式设计，适配各种设备

3. **模板系统**：
   - 提供了完整模板和空白模板
   - 统一的设计语言
   - 易于集成自定义组件

详细的前端模板使用说明可以在[前端模板使用指南](./前端模板使用指南.md)中找到。

## 模块集成指南

本项目提供了两种集成方式：

1. **后端模块集成**：
   - 在`backend/app/modules/`目录中创建Python模块
   - 实现GET和POST处理程序
   - 使用模块加载器注册模块
   - 详细指南参见[模块集成指南](./模块集成指南.md)

2. **前端模块集成**：
   - 基于`frontend/template-blank.html`创建新页面
   - 在`.component-area`中添加自定义组件
   - 添加必要的CSS和JavaScript
   - 详细指南参见[前端模板使用指南](./前端模板使用指南.md)

## 团队协作

这个框架设计用于团队协作，具有以下特点：

1. **前后端分离**：前端和后端团队可以独立工作
2. **模块化架构**：新功能可以作为独立模块添加
3. **清晰的API**：定义良好的API使集成更容易
4. **统一的设计**：共享模板确保一致的外观和用户体验
5. **详细文档**：提供了集成指南和示例

## 计划功能

框架为以下关键功能提供了占位符：

1. **预览模块**：在教授之前向用户展示最终结果
2. **编辑器模块**：带有AI辅助的在线IDE，用于编写HTML代码
3. **沙盒模块**：带有AI反馈的安全代码测试环境
4. **总结模块**：生成所学概念的思维导图和总结

## 技术详情

- **后端**：FastAPI (Python)
- **前端**：HTML、CSS、JavaScript（无框架）
- **API通信**：RESTful JSON API
- **模块系统**：自定义模块加载器，支持动态注册