"""
AI服务模块 - 提供与AI模型的交互接口

这个模块实现了与OpenAI API的交互，支持自定义提示词和上下文管理。
适配OpenAI API标准，同时支持替换为其他兼容OpenAI API的服务。
"""

import os
import json
import logging
import time
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv
# 尝试相对导入（用于主应用），如果失败则使用绝对导入（用于Docker容器）
try:
    from .prompt_generator import get_prompt_generator
except ImportError:
    from prompt_generator import get_prompt_generator

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIService")

# 调试信息
api_key = os.environ.get("OPENAI_API_KEY", "")
api_base = os.environ.get("OPENAI_API_BASE", "")
model = os.environ.get("OPENAI_MODEL", "")
logger.info(f"Loaded API config - Key: {'*' * min(20, len(api_key)) if api_key else 'None'}, Base: {api_base}, Model: {model}")

# 确保API密钥以sk-开头（如果是ModelScope）
if api_key and not api_key.startswith("sk-"):
    logger.warning("API密钥可能格式不正确，ModelScope的API密钥通常以'sk-'开头")


class AIService:
    """AI服务类 - 提供与LLM API的交互"""

    def __init__(self):
        """初始化AI服务"""
        # 从环境变量获取API密钥和配置
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.api_base = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        self.max_tokens = int(os.environ.get("OPENAI_MAX_TOKENS", "1024"))
        self.temperature = float(os.environ.get("OPENAI_TEMPERATURE", "0.7"))
        
        # 并发请求限制和重试配置
        self.max_retries = 3
        self.retry_delay = 2  # 秒
        self.timeout = 30  # 秒
        
        # HTTP会话
        self.session = None
        
        logger.info(f"AI服务初始化完成，使用模型: {self.model}")

    async def ensure_session(self):
        """确保HTTP会话已创建"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
            logger.info("AI服务HTTP会话已关闭")

    async def chat_completion(self, messages: List[Dict[str, str]], 
                              temperature: Optional[float] = None,
                              max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        发送聊天完成请求到OpenAI API
        
        参数:
            messages: 消息列表，包含角色和内容
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成令牌数
            
        返回:
            API响应的JSON对象
        """
        await self.ensure_session()
        
        # 使用提供的参数或默认值
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # 准备请求数据
        request_data = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
            "max_tokens": tokens
        }
        
        # 准备请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 执行请求，带重试
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"API请求失败 (尝试 {attempt+1}/{self.max_retries}): "
                                    f"状态码 {response.status}, 响应: {error_text}")
                        
                        # 处理特定错误码
                        if response.status == 429:  # 速率限制
                            wait_time = self.retry_delay * (2 ** attempt)
                            logger.info(f"达到速率限制，等待 {wait_time} 秒后重试")
                            await asyncio.sleep(wait_time)
                            continue
                        elif response.status >= 500:  # 服务器错误
                            wait_time = self.retry_delay * (2 ** attempt)
                            logger.info(f"服务器错误，等待 {wait_time} 秒后重试")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            # 其他错误不重试
                            return {
                                "error": True,
                                "status_code": response.status,
                                "message": error_text
                            }
            except Exception as e:
                logger.error(f"API请求发生异常 (尝试 {attempt+1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"等待 {wait_time} 秒后重试")
                    await asyncio.sleep(wait_time)
                else:
                    return {
                        "error": True,
                        "message": f"请求失败: {str(e)}"
                    }
        
        # 所有重试都失败
        return {
            "error": True,
            "message": "所有请求尝试均失败"
        }

    async def get_ai_response(self, student_model_summary: Dict[str, Any], 
                           user_message: str, 
                           conversation_history: Optional[List[Dict[str, str]]] = None,
                           code_context: Optional[Dict[str, Any]] = None,
                           task_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取针对用户消息的AI响应
        
        参数:
            student_model_summary: 学习者模型摘要
            user_message: 用户消息
            conversation_history: 可选的对话历史
            code_context: 可选的代码上下文
            task_info: 可选的任务信息
            
        返回:
            包含AI响应的字典
        """
        # 获取提示词生成器
        prompt_generator = get_prompt_generator()
        
        # 生成系统提示词
        system_prompt = prompt_generator.generate_system_prompt(
            student_model_summary, task_info or {}
        )
        
        # 生成用户提示词
        user_prompt = prompt_generator.generate_chat_prompt(
            student_model_summary, user_message, code_context
        )
        
        # 准备消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_prompt})
        
        # 发送请求到API
        start_time = time.time()
        response = await self.chat_completion(messages)
        
        # 处理响应
        if "error" in response and response["error"]:
            logger.error(f"AI请求失败: {response['message']}")
            return {
                "status": "error",
                "message": f"无法获取AI响应: {response.get('message', '未知错误')}",
                "suggestions": []
            }
        
        # 提取回复内容
        try:
            reply_content = response["choices"][0]["message"]["content"]
            
            # 尝试提取建议（如果格式允许）
            suggestions = self._extract_suggestions(reply_content)
            
            logger.info(f"AI响应生成成功，用时: {time.time() - start_time:.2f}秒")
            
            return {
                "status": "success",
                "reply": reply_content,
                "suggestions": suggestions,
                "model": self.model,
                "response_time": time.time() - start_time
            }
        except Exception as e:
            logger.error(f"处理AI响应时出错: {str(e)}")
            return {
                "status": "error",
                "message": f"处理AI响应时出错: {str(e)}",
                "suggestions": []
            }

    def _extract_suggestions(self, content: str) -> List[str]:
        """
        从AI回复中提取建议操作
        
        参数:
            content: AI回复内容
            
        返回:
            建议操作列表
        """
        suggestions = []
        
        # 查找"建议"、"建议操作"或"你可以"等关键词后的列表项
        lines = content.split('\n')
        capture_suggestions = False
        
        for line in lines:
            line = line.strip()
            
            # 检测建议部分的开始
            if any(marker in line.lower() for marker in ["建议:", "建议操作:", "你可以:", "你可以尝试:"]):
                capture_suggestions = True
                continue
                
            # 如果我们在建议部分，捕获列表项
            if capture_suggestions:
                # 检查是否为列表项（以-、*或数字+.开头）
                if line.startswith('-') or line.startswith('*') or line.startswith('>') or (len(line) > 2 and line[0].isdigit() and line[1] == '.'):
                    # 删除列表标记并清理
                    suggestion = line
                    if line.startswith('-'):
                        suggestion = line[1:].strip()
                    elif line.startswith('*'):
                        suggestion = line[1:].strip()
                    elif line.startswith('>'):
                        suggestion = line[1:].strip()
                    elif len(line) > 2 and line[0].isdigit() and line[1] == '.':
                        suggestion = line[2:].strip()
                        
                    if suggestion:
                        suggestions.append(suggestion)
                elif not line:
                    # 空行可能表示建议部分结束
                    continue
                else:
                    # 非列表项可能表示建议部分结束
                    capture_suggestions = False
        
        # 如果没有找到明确的建议，尝试提取一些关键操作
        if not suggestions:
            if "修复" in content or "修正" in content:
                suggestions.append("修复代码问题")
            if "添加" in content:
                suggestions.append("添加新功能")
            if "优化" in content or "改进" in content:
                suggestions.append("优化代码")
            if "学习" in content or "了解" in content:
                suggestions.append("学习相关知识")
        
        # 限制建议数量
        return suggestions[:5]

    async def get_error_feedback(self, student_model_summary: Dict[str, Any],
                               code_context: Dict[str, Any],
                               error_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取针对代码错误的AI反馈
        
        参数:
            student_model_summary: 学习者模型摘要
            code_context: 代码上下文
            error_info: 错误信息
            
        返回:
            包含AI反馈的字典
        """
        # 获取提示词生成器
        prompt_generator = get_prompt_generator()
        
        # 生成系统提示词
        system_prompt = prompt_generator.generate_system_prompt(
            student_model_summary, {"name": "错误诊断与修复"}
        )
        
        # 生成错误反馈提示词
        error_prompt = prompt_generator.generate_error_feedback_prompt(
            student_model_summary, code_context, error_info
        )
        
        # 准备消息列表
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": error_prompt}
        ]
        
        # 发送请求到API
        start_time = time.time()
        response = await self.chat_completion(messages)
        
        # 处理响应
        if "error" in response and response["error"]:
            logger.error(f"获取错误反馈失败: {response['message']}")
            return {
                "status": "error",
                "message": f"无法获取错误反馈: {response.get('message', '未知错误')}",
            }
        
        # 提取回复内容
        try:
            feedback_content = response["choices"][0]["message"]["content"]
            
            logger.info(f"错误反馈生成成功，用时: {time.time() - start_time:.2f}秒")
            
            return {
                "status": "success",
                "feedback": feedback_content,
                "model": self.model,
                "response_time": time.time() - start_time
            }
        except Exception as e:
            logger.error(f"处理错误反馈时出错: {str(e)}")
            return {
                "status": "error",
                "message": f"处理错误反馈时出错: {str(e)}",
            }


# 单例实例
_instance = None

def get_ai_service() -> AIService:
    """获取AI服务的单例实例"""
    global _instance
    if _instance is None:
        _instance = AIService()
    return _instance