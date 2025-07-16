"""
学习者模型模块 - 用于跟踪和管理学习者的状态

这个模块实现了学习者模型，包括认知状态、情感状态和学习偏好。
模型基于用户行为数据进行更新，并为AI系统提供适应性教学指导。
"""

import logging
import json
import time
from typing import Dict, List, Any, Optional
from enum import Enum
from pydantic import BaseModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StudentModel")


class KnowledgeLevel(str, Enum):
    """知识掌握程度枚举"""
    NOVICE = "novice"         # 初学者
    BEGINNER = "beginner"     # 新手
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"     # 高级
    EXPERT = "expert"         # 专家


class CognitiveLoad(str, Enum):
    """认知负荷程度枚举"""
    LOW = "low"               # 低负荷
    MEDIUM = "medium"         # 中等负荷
    HIGH = "high"             # 高负荷


class ConfusionLevel(str, Enum):
    """困惑程度枚举"""
    NONE = "none"             # 无困惑
    SLIGHT = "slight"         # 轻微困惑
    MODERATE = "moderate"     # 中度困惑
    SEVERE = "severe"         # 严重困惑


class FrustrationLevel(str, Enum):
    """挫折感程度枚举"""
    NONE = "none"             # 无挫折感
    LOW = "low"               # 低挫折感
    MEDIUM = "medium"         # 中等挫折感
    HIGH = "high"             # 高挫折感


class FocusLevel(str, Enum):
    """专注度枚举"""
    LOW = "low"               # 低专注度
    MEDIUM = "medium"         # 中等专注度
    HIGH = "high"             # 高专注度


class LearningPreference(str, Enum):
    """学习偏好枚举"""
    CODE_EXAMPLES = "code_examples"  # 代码示例
    TEXT_EXPLANATIONS = "text_explanations"  # 文字解释
    ANALOGIES = "analogies"   # 比喻
    VISUAL_AIDS = "visual_aids"  # 视觉辅助
    INTERACTIVE = "interactive"  # 交互式学习


class KnowledgePoint(BaseModel):
    """知识点模型"""
    id: str
    name: str
    level: KnowledgeLevel = KnowledgeLevel.NOVICE
    last_updated: float = 0
    confidence: float = 0.0  # 0-1之间，表示模型对该评估的信心


class CognitiveState(BaseModel):
    """认知状态模型"""
    knowledge_points: Dict[str, KnowledgePoint] = {}
    cognitive_load: CognitiveLoad = CognitiveLoad.MEDIUM
    confusion_level: ConfusionLevel = ConfusionLevel.NONE
    last_updated: float = 0


class EmotionalState(BaseModel):
    """情感状态模型"""
    frustration_level: FrustrationLevel = FrustrationLevel.NONE
    focus_level: FocusLevel = FocusLevel.MEDIUM
    last_updated: float = 0


class LearningProfile(BaseModel):
    """学习偏好模型"""
    preferences: Dict[LearningPreference, float] = {}  # 偏好类型 -> 强度值(0-1)
    last_updated: float = 0


class StudentModel(BaseModel):
    """学习者模型"""
    id: str
    cognitive_state: CognitiveState = CognitiveState()
    emotional_state: EmotionalState = EmotionalState()
    learning_profile: LearningProfile = LearningProfile()
    created_at: float = 0
    last_activity: float = 0

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        """初始化学习者模型"""
        now = time.time()
        if "created_at" not in data:
            data["created_at"] = now
        if "last_activity" not in data:
            data["last_activity"] = now
            
        # 初始化学习偏好
        if "learning_profile" not in data:
            data["learning_profile"] = LearningProfile(
                preferences={
                    LearningPreference.CODE_EXAMPLES: 0.33,
                    LearningPreference.TEXT_EXPLANATIONS: 0.33,
                    LearningPreference.ANALOGIES: 0.33,
                    LearningPreference.VISUAL_AIDS: 0.33,
                    LearningPreference.INTERACTIVE: 0.33
                },
                last_updated=now
            )
            
        super().__init__(**data)


class StudentModelService:
    """学习者模型服务"""
    def __init__(self):
        self.models: Dict[str, StudentModel] = {}
        self.default_knowledge_points = [
            {"id": "html_basics", "name": "HTML基础"},
            {"id": "css_basics", "name": "CSS基础"},
            {"id": "js_basics", "name": "JavaScript基础"},
            {"id": "dom_manipulation", "name": "DOM操作"},
            {"id": "event_handling", "name": "事件处理"},
            {"id": "responsive_design", "name": "响应式设计"},
            {"id": "web_accessibility", "name": "Web无障碍性"},
        ]
        logger.info("学习者模型服务已初始化")

    def get_model(self, student_id: str) -> StudentModel:
        """获取学习者模型，如果不存在则创建新模型"""
        if student_id not in self.models:
            # 创建新模型
            model = StudentModel(id=student_id)
            
            # 初始化默认知识点
            for kp in self.default_knowledge_points:
                model.cognitive_state.knowledge_points[kp["id"]] = KnowledgePoint(
                    id=kp["id"],
                    name=kp["name"],
                    level=KnowledgeLevel.NOVICE,
                    last_updated=time.time(),
                    confidence=0.5
                )
                
            self.models[student_id] = model
            logger.info(f"为学生 {student_id} 创建了新的模型")
        else:
            # 更新最后活动时间
            self.models[student_id].last_activity = time.time()
            
        return self.models[student_id]

    def update_from_code_submission(self, student_id: str, code_data: Dict[str, Any], test_results: Dict[str, Any]) -> None:
        """根据代码提交和测试结果更新学习者模型"""
        model = self.get_model(student_id)
        now = time.time()
        
        # 更新知识点掌握情况
        if "relevant_knowledge_points" in test_results:
            for kp_id, result in test_results["relevant_knowledge_points"].items():
                if kp_id in model.cognitive_state.knowledge_points:
                    kp = model.cognitive_state.knowledge_points[kp_id]
                    
                    # 根据测试结果调整知识水平
                    if result["score"] > 0.8:
                        kp.level = KnowledgeLevel.ADVANCED if kp.level != KnowledgeLevel.EXPERT else KnowledgeLevel.EXPERT
                    elif result["score"] > 0.6:
                        kp.level = KnowledgeLevel.INTERMEDIATE
                    elif result["score"] > 0.4:
                        kp.level = KnowledgeLevel.BEGINNER
                    else:
                        kp.level = KnowledgeLevel.NOVICE
                        
                    kp.last_updated = now
                    kp.confidence = min(kp.confidence + 0.1, 1.0)  # 增加信心度
        
        # 更新认知负荷
        if "errors" in test_results:
            error_count = len(test_results["errors"])
            if error_count > 5:
                model.cognitive_state.cognitive_load = CognitiveLoad.HIGH
            elif error_count > 2:
                model.cognitive_state.cognitive_load = CognitiveLoad.MEDIUM
            else:
                model.cognitive_state.cognitive_load = CognitiveLoad.LOW
                
        # 更新困惑程度
        if "attempts" in test_results and "success" in test_results:
            attempts = test_results["attempts"]
            success = test_results["success"]
            
            if not success and attempts > 3:
                model.cognitive_state.confusion_level = ConfusionLevel.SEVERE
            elif not success and attempts > 2:
                model.cognitive_state.confusion_level = ConfusionLevel.MODERATE
            elif not success and attempts > 1:
                model.cognitive_state.confusion_level = ConfusionLevel.SLIGHT
            else:
                model.cognitive_state.confusion_level = ConfusionLevel.NONE
                
        model.cognitive_state.last_updated = now
        
        # 更新情感状态
        if "attempts" in test_results and "success" in test_results:
            attempts = test_results["attempts"]
            success = test_results["success"]
            
            if not success and attempts > 3:
                model.emotional_state.frustration_level = FrustrationLevel.HIGH
            elif not success and attempts > 2:
                model.emotional_state.frustration_level = FrustrationLevel.MEDIUM
            elif not success and attempts > 1:
                model.emotional_state.frustration_level = FrustrationLevel.LOW
            else:
                model.emotional_state.frustration_level = FrustrationLevel.NONE
                
        model.emotional_state.last_updated = now
        
        logger.info(f"已更新学生 {student_id} 的模型（代码提交）")

    def update_from_behavior(self, student_id: str, behavior_data: Dict[str, Any]) -> None:
        """根据行为数据更新学习者模型"""
        model = self.get_model(student_id)
        now = time.time()
        
        # 更新专注度
        if "idle_time" in behavior_data:
            idle_time = behavior_data["idle_time"]
            if idle_time > 300:  # 5分钟无操作
                model.emotional_state.focus_level = FocusLevel.LOW
            elif idle_time > 120:  # 2分钟无操作
                model.emotional_state.focus_level = FocusLevel.MEDIUM
            else:
                model.emotional_state.focus_level = FocusLevel.HIGH
                
        # 更新学习偏好
        if "interaction_type" in behavior_data:
            interaction = behavior_data["interaction_type"]
            if interaction in [p.value for p in LearningPreference]:
                pref = LearningPreference(interaction)
                # 增加相应偏好的权重
                for p in model.learning_profile.preferences:
                    if p == pref:
                        model.learning_profile.preferences[p] = min(model.learning_profile.preferences[p] + 0.05, 1.0)
                    else:
                        # 轻微降低其他偏好的权重，保持总和稳定
                        model.learning_profile.preferences[p] = max(model.learning_profile.preferences[p] - 0.01, 0.0)
                        
                model.learning_profile.last_updated = now
                
        model.emotional_state.last_updated = now
        logger.info(f"已更新学生 {student_id} 的模型（行为数据）")

    def get_model_summary(self, student_id: str) -> Dict[str, Any]:
        """获取学习者模型摘要，用于生成提示词"""
        model = self.get_model(student_id)
        
        # 计算平均知识水平
        knowledge_levels = {
            KnowledgeLevel.NOVICE: 1,
            KnowledgeLevel.BEGINNER: 2,
            KnowledgeLevel.INTERMEDIATE: 3,
            KnowledgeLevel.ADVANCED: 4,
            KnowledgeLevel.EXPERT: 5
        }
        
        total_level = 0
        count = 0
        
        for kp in model.cognitive_state.knowledge_points.values():
            total_level += knowledge_levels[kp.level]
            count += 1
            
        avg_knowledge_level = total_level / max(count, 1)
        
        # 获取主要学习偏好
        main_preference = max(model.learning_profile.preferences.items(), 
                            key=lambda x: x[1])[0] if model.learning_profile.preferences else None
        
        summary = {
            "student_id": model.id,
            "cognitive_state": {
                "knowledge_level": avg_knowledge_level,  # 1-5的平均值
                "cognitive_load": model.cognitive_state.cognitive_load,
                "confusion_level": model.cognitive_state.confusion_level
            },
            "emotional_state": {
                "frustration_level": model.emotional_state.frustration_level,
                "focus_level": model.emotional_state.focus_level
            },
            "learning_preferences": {
                "main_preference": main_preference.value if main_preference else None,
                "preferences": {k.value: v for k, v in model.learning_profile.preferences.items()}
            },
            "knowledge_points": {
                kp_id: {
                    "name": kp.name,
                    "level": kp.level,
                    "confidence": kp.confidence
                } for kp_id, kp in model.cognitive_state.knowledge_points.items()
            }
        }
        
        return summary


# 单例实例
_instance = None

def get_student_model_service() -> StudentModelService:
    """获取学习者模型服务的单例实例"""
    global _instance
    if _instance is None:
        _instance = StudentModelService()
    return _instance