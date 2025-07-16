"""
动态提示词生成器 - 根据学习者模型生成适合的提示词

这个模块负责根据学习者模型状态动态生成适合学习者的提示词模板。
提示词包括学习者状态描述、教学策略指导和任务详情。
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from student_model import (
    KnowledgeLevel, CognitiveLoad, ConfusionLevel,
    FrustrationLevel, FocusLevel, LearningPreference
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PromptGenerator")


class PromptGenerator:
    """动态提示词生成器类"""

    def __init__(self):
        """初始化提示词生成器"""
        logger.info("动态提示词生成器已初始化")

    def generate_system_prompt(self, student_model_summary: Dict[str, Any], 
                               task_info: Dict[str, Any]) -> str:
        """
        生成系统提示词，包含学习者模型信息和教学指导
        
        参数:
            student_model_summary: 学习者模型摘要
            task_info: 当前任务信息
            
        返回:
            完整的系统提示词
        """
        # 基础系统提示词
        base_prompt = """你是一个专业的Web开发教学助手，名为"WebDev导师"。你的目标是帮助学生学习HTML、CSS和JavaScript，并引导他们完成交互式编程任务。请使用以下学习者模型信息来调整你的回复方式，使其更适合学生的当前状态和需求。"""
        
        # 学习者模型描述
        student_model_prompt = self._generate_student_model_description(student_model_summary)
        
        # 教学策略指导
        teaching_strategy = self._generate_teaching_strategy(student_model_summary)
        
        # 任务信息
        task_prompt = self._generate_task_description(task_info)
        
        # 组合完整提示词
        full_prompt = f"""{base_prompt}

            {student_model_prompt}

            {teaching_strategy}

            {task_prompt}

            请记住始终以中文回复，并根据学习者的状态调整你的回复风格和内容。"""

        logger.info("已生成系统提示词")
        return full_prompt

    def _generate_student_model_description(self, model_summary: Dict[str, Any]) -> str:
        """生成学习者模型描述部分"""
        cognitive_state = model_summary["cognitive_state"]
        emotional_state = model_summary["emotional_state"]
        learning_prefs = model_summary["learning_preferences"]
        
        # 知识水平描述
        knowledge_level = cognitive_state["knowledge_level"]
        if knowledge_level < 1.5:
            knowledge_desc = "初学者，几乎没有Web开发经验"
        elif knowledge_level < 2.5:
            knowledge_desc = "新手，对Web开发有基本了解"
        elif knowledge_level < 3.5:
            knowledge_desc = "中级学习者，已掌握基础Web开发概念"
        elif knowledge_level < 4.5:
            knowledge_desc = "高级学习者，有较丰富的Web开发经验"
        else:
            knowledge_desc = "专家级学习者，精通Web开发"
            
        # 认知负荷描述
        cognitive_load = cognitive_state["cognitive_load"]
        confusion = cognitive_state["confusion_level"]
        
        if cognitive_load == "high":
            cognitive_desc = "目前处于高认知负荷状态，难以处理复杂信息"
        elif cognitive_load == "medium":
            cognitive_desc = "认知负荷适中，可以接收适量新信息"
        else:
            cognitive_desc = "认知负荷较低，可以处理更多新概念"
            
        if confusion == "severe":
            confusion_desc = "对当前内容感到非常困惑"
        elif confusion == "moderate":
            confusion_desc = "对一些概念有困惑"
        elif confusion == "slight":
            confusion_desc = "对少数细节有些许困惑"
        else:
            confusion_desc = "理解清晰，没有明显困惑"
            
        # 情感状态描述
        frustration = emotional_state["frustration_level"]
        focus = emotional_state["focus_level"]
        
        if frustration == "high":
            emotion_desc = "学习者感到非常沮丧，需要积极的鼓励和支持"
        elif frustration == "medium":
            emotion_desc = "学习者有一定挫折感，需要一些鼓励"
        elif frustration == "low":
            emotion_desc = "学习者有轻微挫折感，但仍能继续学习"
        else:
            emotion_desc = "学习者情绪积极，没有明显挫折感"
            
        if focus == "low":
            focus_desc = "注意力不集中，需要简短清晰的指导"
        elif focus == "medium":
            focus_desc = "注意力一般，可以接收中等长度的解释"
        else:
            focus_desc = "注意力集中，可以接收详细解释"
            
        # 学习偏好描述
        main_pref = learning_prefs["main_preference"]
        if main_pref == "code_examples":
            pref_desc = "偏好通过代码示例学习"
        elif main_pref == "text_explanations":
            pref_desc = "偏好详细的文字解释"
        elif main_pref == "analogies":
            pref_desc = "偏好通过类比和比喻理解概念"
        elif main_pref == "visual_aids":
            pref_desc = "偏好通过视觉辅助（图表、图示）学习"
        elif main_pref == "interactive":
            pref_desc = "偏好交互式、实践性学习方式"
        else:
            pref_desc = "没有明显的学习偏好"
        
        # 组合描述
        return f"""## 学习者模型

学习者当前状态:
- 知识水平: {knowledge_desc}
- 认知状态: {cognitive_desc}，{confusion_desc}
- 情感状态: {emotion_desc}，{focus_desc}
- 学习偏好: {pref_desc}

知识点掌握情况:
{self._format_knowledge_points(model_summary["knowledge_points"])}
"""

    def _format_knowledge_points(self, knowledge_points: Dict[str, Any]) -> str:
        """格式化知识点掌握情况"""
        result = []
        for kp_id, kp_data in knowledge_points.items():
            level_text = {
                "novice": "初学 (需要基础概念解释)",
                "beginner": "新手 (需要详细指导)",
                "intermediate": "中级 (需要适度指导)",
                "advanced": "高级 (只需少量提示)",
                "expert": "专家 (可自行解决问题)"
            }.get(kp_data["level"], "未知")
            
            result.append(f"- {kp_data['name']}: {level_text}")
            
        return "\n".join(result)

    def _generate_teaching_strategy(self, model_summary: Dict[str, Any]) -> str:
        """生成教学策略指导"""
        cognitive_state = model_summary["cognitive_state"]
        emotional_state = model_summary["emotional_state"]
        learning_prefs = model_summary["learning_preferences"]
        
        # 根据认知负荷和困惑程度调整解释详细程度
        if cognitive_state["cognitive_load"] == "high" or cognitive_state["confusion_level"] in ["severe", "moderate"]:
            explanation_strategy = "- 使用简单、直接的语言，避免技术术语\n- 将复杂概念分解成小步骤\n- 优先解释最基础的概念"
        elif cognitive_state["cognitive_load"] == "medium" or cognitive_state["confusion_level"] == "slight":
            explanation_strategy = "- 使用中等复杂度的解释\n- 可以引入适量技术术语，但需要解释\n- 提供具体示例来强化概念"
        else:
            explanation_strategy = "- 可以使用更技术性的语言\n- 可以介绍高级概念和最佳实践\n- 提供深入的解释和背景知识"
            
        # 根据情感状态调整反馈方式
        if emotional_state["frustration_level"] in ["high", "medium"]:
            feedback_strategy = "- 提供大量积极鼓励和肯定\n- 强调已经取得的进步\n- 设定小而可达成的目标来建立信心"
        else:
            feedback_strategy = "- 提供直接、具体的反馈\n- 指出可以改进的地方\n- 鼓励尝试更具挑战性的任务"
            
        # 根据专注度调整内容长度
        if emotional_state["focus_level"] == "low":
            content_strategy = "- 保持回复简短明了\n- 使用列表和标题增强可读性\n- 一次只介绍一个概念"
        elif emotional_state["focus_level"] == "medium":
            content_strategy = "- 提供中等长度的回复\n- 使用小标题组织内容\n- 每次最多介绍2-3个相关概念"
        else:
            content_strategy = "- 可以提供较长、较详细的回复\n- 深入探讨相关概念\n- 可以引入额外的延伸知识"
            
        # 根据学习偏好调整教学方法
        main_pref = learning_prefs["main_preference"]
        
        if main_pref == "code_examples":
            method_strategy = "- 提供大量代码示例\n- 使用注释解释代码的关键部分\n- 展示代码的不同变体"
        elif main_pref == "text_explanations":
            method_strategy = "- 提供详细的文字解释\n- 使用明确的定义和概念说明\n- 通过逻辑推理解释概念"
        elif main_pref == "analogies":
            method_strategy = "- 使用类比和比喻解释技术概念\n- 将Web开发概念与日常生活经验联系\n- 使用故事和场景说明"
        elif main_pref == "visual_aids":
            method_strategy = "- 描述可视化的概念模型\n- 推荐使用图表和图示理解代码结构\n- 参考界面元素和布局"
        elif main_pref == "interactive":
            method_strategy = "- 鼓励实践和实验\n- 提出小型挑战和练习\n- 引导通过尝试和错误学习"
        else:
            method_strategy = "- 混合使用多种教学方法\n- 结合代码示例和文字解释\n- 灵活调整教学策略"
        
        # 组合教学策略
        return f"""## 教学策略

基于学习者当前状态，请采用以下教学策略:

### 解释复杂度:
{explanation_strategy}

### 反馈方式:
{feedback_strategy}

### 内容长度:
{content_strategy}

### 教学方法:
{method_strategy}
"""

    def _generate_task_description(self, task_info: Dict[str, Any]) -> str:
        """生成任务描述部分"""
        if not task_info:
            return "## 当前任务\n\n回答学生的问题并提供适当的指导。"
            
        task_name = task_info.get("name", "未命名任务")
        task_description = task_info.get("description", "无描述")
        task_objectives = task_info.get("objectives", [])
        
        objectives_text = ""
        if task_objectives:
            objectives_text = "任务目标:\n" + "\n".join([f"- {obj}" for obj in task_objectives])
        
        return f"""## 当前任务

任务: {task_name}

描述: {task_description}

{objectives_text}

请基于学习者当前状态，提供最适合的指导帮助完成此任务。
"""

    def generate_chat_prompt(self, student_model_summary: Dict[str, Any], 
                             user_message: str, code_context: Dict[str, Any] = None) -> str:
        """
        生成聊天提示词，包含用户消息和代码上下文
        
        参数:
            student_model_summary: 学习者模型摘要
            user_message: 用户发送的消息
            code_context: 当前代码上下文（HTML、CSS、JS等）
            
        返回:
            格式化的用户提示词
        """
        prompt = user_message
        
        # 添加代码上下文
        if code_context:
            html_code = code_context.get("html", "")
            css_code = code_context.get("css", "")
            js_code = code_context.get("js", "")
            
            code_blocks = []
            
            if html_code:
                code_blocks.append(f"HTML 代码:\n```html\n{html_code}\n```")
            if css_code:
                code_blocks.append(f"CSS 代码:\n```css\n{css_code}\n```")
            if js_code:
                code_blocks.append(f"JavaScript 代码:\n```javascript\n{js_code}\n```")
                
            if code_blocks:
                prompt += "\n\n当前代码:\n" + "\n\n".join(code_blocks)
        
        logger.info("已生成聊天提示词")
        return prompt

    def generate_error_feedback_prompt(self, student_model_summary: Dict[str, Any], 
                                     code_context: Dict[str, Any], 
                                     error_info: Dict[str, Any]) -> str:
        """
        生成错误反馈提示词，帮助学生理解和修复错误
        
        参数:
            student_model_summary: 学习者模型摘要
            code_context: 当前代码上下文
            error_info: 错误信息详情
            
        返回:
            错误反馈提示词
        """
        # 基本错误情况描述
        error_type = error_info.get("type", "未知错误")
        error_message = error_info.get("message", "无错误信息")
        error_location = error_info.get("location", {})
        line = error_location.get("line", "未知")
        column = error_location.get("column", "未知")
        
        # 根据学习者知识水平调整错误解释的复杂度
        knowledge_level = student_model_summary["cognitive_state"]["knowledge_level"]
        
        if knowledge_level < 2.5:  # 初学者和新手
            error_explanation_request = "请以非常简单直观的方式解释这个错误，避免使用技术术语。使用类比或日常生活的例子来帮助理解问题所在。"
        elif knowledge_level < 4.0:  # 中级
            error_explanation_request = "请解释这个错误，可以使用一些基本的技术术语，但需要确保概念清晰。提供具体的修复步骤。"
        else:  # 高级和专家
            error_explanation_request = "请提供对此错误的技术性解释，可以使用行业术语和最佳实践。讨论潜在的根本原因和优化方案。"
        
        # 获取代码上下文
        html_code = code_context.get("html", "")
        css_code = code_context.get("css", "")
        js_code = code_context.get("js", "")
        
        # 组装提示词
        prompt = f"""我在运行代码时遇到了错误，需要帮助理解和修复。

错误类型: {error_type}
错误信息: {error_message}
错误位置: 第 {line} 行，第 {column} 列

当前代码:
"""
        
        if html_code:
            prompt += f"\nHTML 代码:\n```html\n{html_code}\n```"
        if css_code:
            prompt += f"\nCSS 代码:\n```css\n{css_code}\n```"
        if js_code:
            prompt += f"\nJavaScript 代码:\n```javascript\n{js_code}\n```"
            
        prompt += f"\n\n{error_explanation_request}\n\n请提供修复建议和正确的代码示例。"
        
        logger.info("已生成错误反馈提示词")
        return prompt


# 单例实例
_instance = None

def get_prompt_generator() -> PromptGenerator:
    """获取提示词生成器的单例实例"""
    global _instance
    if _instance is None:
        _instance = PromptGenerator()
    return _instance