# AI 配置使用说明

## 1. 概述

本项目通过 `.env` 文件配置 AI 服务参数，该文件不会被 Git 追踪（已加入 `.gitignore`），以保护敏感信息。`.env.example` 文件提供了配置示例，供团队成员参考。

## 2. AI 配置参数

在 `.env` 文件中，有以下与 AI 相关的配置参数：

```env
# AI服务配置
OPENAI_API_KEY=sk-or-v1-。。。。。。                  # API密钥（请替换为自己的密钥）
OPENAI_API_BASE=https://openrouter.ai/api/v1         # API基础URL
OPENAI_MODEL=google/gemma-3-27b-it:free              # 使用的模型
OPENAI_MAX_TOKENS=1024                               # 最大生成令牌数
OPENAI_TEMPERATURE=0.7                               # 温度参数，控制生成内容的随机性
```

### 参数说明：

- `OPENAI_API_KEY`: 用于访问 AI 服务的 API 密钥
- `OPENAI_API_BASE`: AI 服务的基础 URL，可以是 OpenAI、Azure OpenAI 或其他兼容服务
- `OPENAI_MODEL`: 使用的模型名称，不同服务提供商支持的模型不同
- `OPENAI_MAX_TOKENS`: 限制 AI 生成内容的最大令牌数
- `OPENAI_TEMPERATURE`: 控制生成内容的随机性，值越高越随机（0-1）

## 3. 该如何测试AI模块？

### 3.1 获取 API 密钥

1. 如果已有 OpenAI API 密钥，可以直接使用
2. 如果没有 API 密钥，可以在群里询曹欣卓获取
3. 也可使用免费服务如 OpenRouter，在其网站注册获取 API 密钥

### 3.2 配置 .env 文件

1. 复制 `.env.example` 文件并重命名为 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，替换 `OPENAI_API_KEY` 为你自己的密钥：
   ```env
   OPENAI_API_KEY=sk-你的API密钥
   ```

3. 根据需要可以修改其他参数，如模型、最大令牌数等

### 3.3 启动项目并测试

1. 启动后端服务：
   ```bash
   cd backend
   python run.py
   ```

2. 启动前端服务：
   ```bash
   cd frontend
   # 根据项目配置启动前端服务
   ```

3. 在前端界面中打开 AI 聊天功能，输入消息测试 AI 回复

### 3.4 验证配置是否正确

1. 查看后端启动日志，确认是否正确加载了环境变量：
   ```
   INFO:     OPENAI_API_KEY: sk-or-v1-******
   INFO:     OPENAI_API_BASE: https://openrouter.ai/api/v1
   INFO:     OPENAI_MODEL: google/gemma-3-27b-it:free
   ```

2. 在前端界面中尝试与 AI 交互，观察是否有正确回复

## 4. 如何添加新的 AI 部件

### 4.1 统一使用现有 API

项目中的 AI 服务已经封装在 `backend/app/modules/ide_module_dir/ai_service.py` 中，建议所有新的 AI 功能都通过这个统一接口实现。

### 4.2 添加新的 AI 功能步骤

1. 在 `prompt_generator.py` 中添加新的提示词生成方法

2. 在 `ai_service.py` 中添加新的 AI 服务方法，例如：
   ```python
   async def get_new_ai_feature(self, params):
       # 生成提示词
       prompt = generate_new_feature_prompt(params)
       
       # 准备消息列表
       messages = [
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": prompt}
       ]
       
       # 发送请求到AI服务
       response = await self.chat_completion(messages)
       
       # 处理并返回结果
       return process_response(response)
   ```

3. 在 `ide_module.py` 中添加新的 API 端点：
   ```python
   @api_router.post("/module/ide/new-feature")
   async def new_feature_endpoint(request: Request):
       # 实现功能逻辑
       pass
   ```

4. 在前端对应的 JS 文件中添加调用新功能的代码

### 4.3 自定义 AI 服务提供商

如果需要更换 AI 服务提供商，只需修改 `.env` 文件中的以下参数：

```env
OPENAI_API_BASE=https://新的API服务地址/v1
OPENAI_MODEL=新的模型名称
```

确保新的服务提供商兼容 OpenAI API 格式。

## 5. 故障排除

### 5.1 常见问题

1. **API 密钥无效**
   - 检查 `.env` 文件中 `OPENAI_API_KEY` 是否正确配置
   - 确认密钥没有过期或被禁用

2. **无法连接到 API 服务**
   - 检查网络连接
   - 验证 `OPENAI_API_BASE` 地址是否正确
   - 确认服务提供商是否正常运行

3. **API 调用返回错误**
   - 查看后端日志中的详细错误信息
   - 检查是否超出使用限制（如速率限制）

### 5.2 日志查看

1. 后端日志：
   - 启动后端服务后，控制台会输出详细日志
   - 关键日志包括环境变量加载、API 请求和响应等

2. 前端日志：
   - 打开浏览器开发者工具的控制台查看日志
   - 查看网络请求以确认 API 调用是否成功

## 6. 安全注意事项

1. 切勿将包含真实 API 密钥的 `.env` 文件提交到版本控制系统