# IDE-Module 分阶段 Debug 构建报告 (2025-07-17)

## 1. 模块定位
IDE-Module 旨在为 **AI HTML 学习平台** 提供一套「在线编写-运行-调试-AI 辅助-测试反馈」的一站式 Web IDE，支持独立部署，也能通过 API / iframe 嵌入主站。

## 2. 分阶段构建进度
| 阶段 | 核心目标 | 状态 |
| ---- | -------- | ---- |
| P0 — 骨架搭建 | • 前端基本布局 (左侧 AI Chat / 右侧 Monaco 编辑器 / 底部测试区)<br>• FastAPI 服务启动<br>• Docker 沙箱容器原型 | ✅ 完成 |
| P1 — 实时预览 | • `preview.js` 注入 iframe 实时渲染<br>• 多标签同步保存 HTML/CSS/JS | ✅ 完成 |
| P2 — 代码执行 & 静态检查 | • `code_executor.py` 使用沙箱容器运行 JS<br>• `static-check` API 提供 ESLint 结果 | 🚧 90% |
| P3 — AI Error Feedback | • `ai_error_feedback` 端点<br>• Prompt 生成器 + 学习者模型 | 🚧 60% |
| P4 — 测试用例系统 | • 测试要求/结果面板<br>• 结果展示组件状态色 (success/warning/error) | ⏳ 计划中 |

## 3. 架构概览
```
ide-module/
├── frontend           # 纯静态, CDN 加载 Monaco
│   ├── index.html     # 主 UI
│   ├── js/            # 模块化脚本
│   └── css/           # 响应式样式
└── backend            # FastAPI + Docker
    ├── app.py         # API 入口
    ├── code_executor.py
    ├── docker_manager.py
    └── sandbox/       # 隔离执行环境
```

* **前端**: Iframe 集成友好, 暴露 `window.AICodeIDE.API` 统一接口
* **后端**: 按职责拆分
  * `docker_manager` 管理容器池与镜像缓存
  * `code_executor` 提供执行 & 静态分析协程
  * `ai_service` 聚合 Prompt-Gen / Student-Model / LLM

## 4. 关键实现
### 4.1 前端
* **Monaco** in-browser IDE, 语法高亮 & IntelliSense
* **折叠面板** (`toggle-panels.js`) 显示/隐藏测试或 AI 区域
* **跨窗口消息**：`postMessage` 方便父级页面调用

### 4.2 后端
* **异步执行**：`async def execute_code`，最大并发安全
* **Docker-in-Docker**：沙箱镜像 (`sandbox/Dockerfile.sandbox`) 体积 < 80 MB
* **热启动**：启动脚本 `start.sh` 自动构建镜像 + 重用已存在容器
* **AI Pipeline**：Prompt → LLM → 后处理，输出 json 结构，前端即可渲染

## 5. Demo 流程 (本地)
```bash
# 前端
open ide-module/frontend/index.html

# 后端
cd ide-module/backend
cp .env.example .env
./start.sh  # 首次约 2-3 分钟
```
浏览器步骤：HTML/CSS/JS 编辑 → 自动预览 → 点击 Run → 服务器返回执行结果 / ESLint 输出 → 若报错可请求 AI 修复建议。

## 6. 主要收获
1. 完成 Monaco + Docker 沙箱打通，实现安全执行
2. 提炼跨窗口消息协议，后续主站接入零成本
3. 通过分阶段 debug，将风险前置并保持可演示性

## 7. 待办与风险
| 待办 | 优先级 | 风险 |
| ---- | ------ | ---- |
| ESLint 依赖镜像精简 | High | 镜像体积过大影响冷启动 |
| AI 模型接入真实 OpenAI API | High | 费用控制 & 速率限制 |
| TestCase DSL 设计 | Medium | 规范过重导致学习成本高 |
| 多用户隔离 & 资源限额 | Medium | 容器逃逸 / 资源耗尽 |

## 8. 下周计划
1. 完成 P2 代码执行边缘用例 & 错误格式化
2. 接入 GPT-4o 进行 AI Debug／Code Review
3. 设计并实现首批 5 个自动测试用例模板
4. 前端支持代码持久化 (localStorage + 导入/导出)

---
> 截至 2025-07-17，IDE-Module 已达到可用原型，可在组会上现场演示实时编辑-预览-执行全流程。
