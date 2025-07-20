"""
API集成模块 - 将改进的学习者模型和自动出题系统集成到现有API中

提供新的API端点：
1. /api/v2/student-model - 获取改进的学习者模型信息
2. /api/v2/behavior/log - 记录用户行为数据
3. /api/v2/quiz/generate - 生成自适应测试题
4. /api/v2/quiz/evaluate - 评估测试答案
5. /api/v2/learning/progress - 获取学习进度分析
"""

import logging
import time
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel

# 导入新的系统组件
try:
    from analytics.behavior_logger import get_behavior_logger, BehaviorEvent, EventType
    from analytics.improved_student_model import get_improved_student_model_service
    from analytics.quiz_generator import get_quiz_generator, get_quiz_evaluator, Question, QuestionType
    from analytics.single_user_model import get_single_user_model
except ImportError as e:
    logging.error(f"导入分析模块失败: {e}")
    # 为了兼容性，创建空的替代品
    def get_behavior_logger(): return None
    def get_improved_student_model_service(): return None
    def get_quiz_generator(): return None
    def get_quiz_evaluator(): return None
    def get_single_user_model(): return None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APIIntegration")


# API数据模型
class BehaviorLogRequest(BaseModel):
    """行为日志请求模型"""
    student_id: str
    session_id: str
    event_type: str
    event_data: Dict[str, Any]


class QuizGenerationRequest(BaseModel):
    """出题请求模型"""
    student_id: str
    knowledge_points: List[str]
    num_questions: int = 3


class QuizAnswer(BaseModel):
    """题目答案模型"""
    question_id: str
    question_type: str
    answer_data: Dict[str, Any]  # 根据题型不同，包含不同的答案数据


class QuizEvaluationRequest(BaseModel):
    """评估请求模型"""
    student_id: str
    session_id: str
    answers: List[QuizAnswer]


class PerformanceUpdateRequest(BaseModel):
    """表现更新请求模型"""
    student_id: str
    session_id: str
    knowledge_point_id: str
    performance_data: Dict[str, Any]


class APIIntegrationService:
    """API集成服务 - 单用户优化版本"""
    
    def __init__(self):
        """初始化API集成服务"""
        self.behavior_logger = get_behavior_logger()
        self.student_model_service = get_improved_student_model_service()
        self.quiz_generator = get_quiz_generator()
        self.quiz_evaluator = get_quiz_evaluator()
        self.single_user_model = get_single_user_model()  # 新增单用户模型
        
        # 题目缓存，用于评估时查找题目信息
        self.question_cache: Dict[str, Question] = {}
        
        # 单用户简化设置
        self.default_student_id = "main_student"
        
        logger.info("API集成服务已初始化（单用户优化版本）")
    
    async def get_student_model_summary(self, student_id: str) -> Dict[str, Any]:
        """获取学习者模型摘要 - 使用单用户增强模型"""
        try:
            if not self.single_user_model:
                raise HTTPException(status_code=503, detail="单用户学习模型服务不可用")
            
            # 使用单用户模型获取增强摘要
            summary = self.single_user_model.get_model_summary()
            
            # 添加API版本信息
            summary['api_version'] = 'v2_single_user'
            summary['enhanced_features'] = [
                'bayesian_knowledge_tracking',
                'ml_state_prediction',
                'single_user_optimization',
                'persistent_learning_data',
                'personalized_recommendations'
            ]
            
            return summary
            
        except Exception as e:
            logger.error(f"获取学习者模型失败: {e}")
            raise HTTPException(status_code=500, detail="获取学习者模型失败")
    
    async def log_behavior_event(self, request: BehaviorLogRequest) -> Dict[str, Any]:
        """记录用户行为事件"""
        try:
            if not self.behavior_logger:
                raise HTTPException(status_code=503, detail="行为日志服务不可用")
            
            # 解析事件数据
            event_type = EventType(request.event_type)
            event_data = request.event_data
            
            # 创建行为事件
            event = BehaviorEvent(
                timestamp=event_data.get('timestamp', time.time()),
                student_id=request.student_id,
                session_id=request.session_id,
                event_type=event_type,
                duration=event_data.get('duration'),
                code_before=event_data.get('code_before'),
                code_after=event_data.get('code_after'),
                cursor_position=event_data.get('cursor_position'),
                edit_length=event_data.get('edit_length'),
                error_type=event_data.get('error_type'),
                help_query=event_data.get('help_query'),
                ai_response=event_data.get('ai_response'),
                current_task=event_data.get('current_task'),
                knowledge_points=event_data.get('knowledge_points'),
                metadata=event_data.get('metadata')
            )
            
            # 记录事件
            self.behavior_logger.log_event(event)
            
            # 如果有学习者模型服务，基于行为数据更新模型
            if self.student_model_service:
                self.student_model_service.update_from_behavior_data(
                    request.student_id, request.session_id
                )
            
            return {
                'status': 'success',
                'message': '行为数据已记录',
                'event_id': f"{request.session_id}_{event.timestamp}"
            }
            
        except ValueError as e:
            logger.error(f"无效的事件类型: {e}")
            raise HTTPException(status_code=400, detail=f"无效的事件类型: {request.event_type}")
        except Exception as e:
            logger.error(f"记录行为事件失败: {e}")
            raise HTTPException(status_code=500, detail="记录行为事件失败")
    
    async def generate_adaptive_quiz(self, request: QuizGenerationRequest) -> Dict[str, Any]:
        """生成自适应测试题"""
        try:
            if not self.quiz_generator or not self.student_model_service:
                raise HTTPException(status_code=503, detail="出题服务不可用")
            
            # 获取学习者模型
            student_model_summary = self.student_model_service.get_model_summary(request.student_id)
            
            # 生成题目
            questions = self.quiz_generator.generate_adaptive_quiz(
                student_model_summary=student_model_summary,
                target_knowledge_points=request.knowledge_points,
                num_questions=request.num_questions
            )
            
            # 缓存题目用于后续评估
            for question in questions:
                self.question_cache[question.id] = question
            
            # 转换为API响应格式
            questions_data = []
            for question in questions:
                question_data = {
                    'id': question.id,
                    'type': question.type.value,
                    'title': question.title,
                    'content': question.content,
                    'knowledge_points': question.knowledge_points,
                    'difficulty': question.difficulty.value,
                    'estimated_time': question.estimated_time,
                    'max_score': question.max_score
                }
                
                # 根据题型添加特定数据
                if question.type == QuestionType.FILL_IN_BLANK and question.template:
                    question_data['template'] = {
                        'code_template': question.template.template,
                        'blank_count': len(question.template.blanks),
                        'hints': question.template.hints
                    }
                elif question.type == QuestionType.ERROR_CORRECTION and question.buggy_code:
                    question_data['buggy_code'] = {
                        'code': question.buggy_code.buggy_code,
                        'error_type': question.buggy_code.error_type,
                        'error_description': question.buggy_code.error_description
                    }
                elif question.type == QuestionType.CODE_IMPLEMENTATION and question.implementation_task:
                    question_data['implementation_task'] = {
                        'description': question.implementation_task.description,
                        'requirements': question.implementation_task.requirements,
                        'starter_code': question.implementation_task.starter_code,
                        'test_cases': question.implementation_task.test_cases
                    }
                
                questions_data.append(question_data)
            
            return {
                'status': 'success',
                'questions': questions_data,
                'total_questions': len(questions_data),
                'generation_metadata': {
                    'student_knowledge_level': student_model_summary['cognitive_state']['knowledge_level'],
                    'cognitive_load': student_model_summary['cognitive_state']['cognitive_load'],
                    'confusion_level': student_model_summary['cognitive_state']['confusion_level'],
                    'adaptive_adjustments_applied': True
                }
            }
            
        except Exception as e:
            logger.error(f"生成测试题失败: {e}")
            raise HTTPException(status_code=500, detail="生成测试题失败")
    
    async def evaluate_quiz_answers(self, request: QuizEvaluationRequest) -> Dict[str, Any]:
        """评估测试答案"""
        try:
            if not self.quiz_evaluator or not self.student_model_service:
                raise HTTPException(status_code=503, detail="评估服务不可用")
            
            evaluation_results = []
            total_score = 0
            total_max_score = 0
            
            for answer in request.answers:
                # 从缓存中获取题目
                question = self.question_cache.get(answer.question_id)
                if not question:
                    logger.warning(f"未找到题目: {answer.question_id}")
                    continue
                
                # 根据题型评估答案
                if answer.question_type == QuestionType.FILL_IN_BLANK.value:
                    result = self.quiz_evaluator.evaluate_fill_in_blank(
                        question, answer.answer_data.get('answers', [])
                    )
                elif answer.question_type == QuestionType.ERROR_CORRECTION.value:
                    result = self.quiz_evaluator.evaluate_error_correction(
                        question, answer.answer_data.get('corrected_code', '')
                    )
                elif answer.question_type == QuestionType.CODE_IMPLEMENTATION.value:
                    result = self.quiz_evaluator.evaluate_code_implementation(
                        question, answer.answer_data.get('implementation_code', '')
                    )
                else:
                    # 概念题等其他类型，暂时给予通过分数
                    result = {
                        'score': question.max_score * 0.8,
                        'feedback': '概念题需要人工评估'
                    }
                
                # 更新学习者模型
                performance_data = {
                    'success': result.get('score', 0) >= question.max_score * 0.6,
                    'score': result.get('score', 0) / question.max_score,
                    'attempts': 1,
                    'time_spent': answer.answer_data.get('time_spent', 0),
                    'difficulty': question.difficulty.value
                }
                
                for knowledge_point in question.knowledge_points:
                    self.student_model_service.update_from_performance(
                        request.student_id, request.session_id, 
                        knowledge_point, performance_data
                    )
                
                # 收集评估结果
                evaluation_results.append({
                    'question_id': answer.question_id,
                    'question_type': answer.question_type,
                    'score': result.get('score', 0),
                    'max_score': question.max_score,
                    'feedback': result.get('feedback', ''),
                    'suggestions': result.get('suggestions', []),
                    'knowledge_points': question.knowledge_points
                })
                
                total_score += result.get('score', 0)
                total_max_score += question.max_score
            
            # 计算整体表现
            overall_percentage = (total_score / total_max_score) * 100 if total_max_score > 0 else 0
            
            # 生成学习建议
            learning_suggestions = self._generate_learning_suggestions(
                overall_percentage, evaluation_results
            )
            
            return {
                'status': 'success',
                'evaluation_results': evaluation_results,
                'overall_score': total_score,
                'overall_max_score': total_max_score,
                'overall_percentage': overall_percentage,
                'learning_suggestions': learning_suggestions,
                'next_steps': self._generate_next_steps(overall_percentage)
            }
            
        except Exception as e:
            logger.error(f"评估测试答案失败: {e}")
            raise HTTPException(status_code=500, detail="评估测试答案失败")
    
    async def update_performance(self, request: PerformanceUpdateRequest) -> Dict[str, Any]:
        """更新学习表现"""
        try:
            if not self.student_model_service:
                raise HTTPException(status_code=503, detail="学习者模型服务不可用")
            
            self.student_model_service.update_from_performance(
                request.student_id,
                request.session_id,
                request.knowledge_point_id,
                request.performance_data
            )
            
            return {
                'status': 'success',
                'message': '学习表现已更新'
            }
            
        except Exception as e:
            logger.error(f"更新学习表现失败: {e}")
            raise HTTPException(status_code=500, detail="更新学习表现失败")
    
    async def get_learning_progress(self, student_id: str) -> Dict[str, Any]:
        """获取学习进度分析 - 使用单用户增强分析"""
        try:
            if not self.single_user_model:
                raise HTTPException(status_code=503, detail="单用户学习模型服务不可用")
            
            # 获取增强的学习者模型摘要
            model_summary = self.single_user_model.get_model_summary()
            
            # 获取个性化建议
            recommendations = self.single_user_model.get_personalized_recommendations()
            
            # 获取BKT分析
            bkt_analysis = model_summary.get('bkt_analysis', {})
            
            # 构建进度分析
            knowledge_trends = {}
            knowledge_points = model_summary.get('knowledge_points', {})
            
            for kp_id, kp_data in knowledge_points.items():
                # 获取预测信息
                prediction = self.single_user_model.predict_next_performance(kp_id)
                
                knowledge_trends[kp_id] = {
                    'current_level': kp_data.get('mastery_score', 1.0),
                    'confidence': kp_data.get('confidence', 0.5),
                    'practice_frequency': kp_data.get('performance_count', 0),
                    'last_practiced': kp_data.get('last_practiced', 0),
                    'predicted_success_rate': prediction.get('predicted_success_probability', 0.5),
                    'bkt_mastery_probability': prediction.get('estimated_mastery_level', 0.5),
                    'trend': 'improving' if kp_data.get('confidence', 0) > 0.6 else 'needs_practice'
                }
            
            return {
                'status': 'success',
                'student_id': student_id,
                'model_type': 'single_user_enhanced',
                'overall_progress': {
                    'knowledge_level': model_summary.get('cognitive_state', {}).get('knowledge_level', 1.0),
                    'overall_confidence': model_summary.get('overall_confidence', 0.3),
                    'cognitive_load': model_summary.get('cognitive_state', {}).get('cognitive_load', 'medium'),
                    'focus_level': model_summary.get('emotional_state', {}).get('focus_level', 'medium'),
                    'average_mastery': bkt_analysis.get('average_mastery', 0.1),
                    'well_mastered_count': bkt_analysis.get('well_mastered_count', 0),
                    'struggling_count': bkt_analysis.get('struggling_count', 0)
                },
                'knowledge_trends': knowledge_trends,
                'bkt_analysis': bkt_analysis,
                'ml_model_status': model_summary.get('ml_model_status', {}),
                'recommendations': recommendations,
                'advanced_features': {
                    'bayesian_tracking_active': True,
                    'ml_prediction_active': model_summary.get('ml_model_status', {}).get('cognitive_load_trained', False),
                    'single_user_optimization': True
                }
            }
            
        except Exception as e:
            logger.error(f"获取学习进度失败: {e}")
            raise HTTPException(status_code=500, detail="获取学习进度失败")
    
    def _generate_learning_suggestions(self, overall_percentage: float, 
                                     evaluation_results: List[Dict]) -> List[str]:
        """生成学习建议"""
        suggestions = []
        
        if overall_percentage >= 90:
            suggestions.append("🎉 表现优秀！可以尝试更具挑战性的内容")
        elif overall_percentage >= 75:
            suggestions.append("👍 掌握得不错，继续保持")
        elif overall_percentage >= 60:
            suggestions.append("📚 基础掌握可以，建议加强练习")
        else:
            suggestions.append("🔄 建议重新学习基础概念")
        
        # 分析具体知识点
        weak_areas = []
        for result in evaluation_results:
            if result['score'] / result['max_score'] < 0.6:
                weak_areas.extend(result['knowledge_points'])
        
        if weak_areas:
            weak_areas_unique = list(set(weak_areas))
            suggestions.append(f"需要重点关注: {', '.join(weak_areas_unique)}")
        
        return suggestions
    
    def _generate_next_steps(self, overall_percentage: float) -> List[str]:
        """生成下一步建议"""
        if overall_percentage >= 80:
            return [
                "可以开始学习下一个主题",
                "尝试更复杂的项目练习",
                "复习并巩固已学知识"
            ]
        elif overall_percentage >= 60:
            return [
                "继续当前主题的练习",
                "重点攻克薄弱知识点",
                "多做实践练习"
            ]
        else:
            return [
                "回顾基础概念",
                "寻求帮助和指导",
                "放慢学习节奏，确保理解"
            ]
    
    def _generate_learning_recommendations(self, model_summary: Dict, 
                                         learning_signals: Dict) -> List[str]:
        """生成个性化学习建议"""
        recommendations = []
        
        # 基于认知负荷的建议
        cognitive_load = model_summary['cognitive_state']['cognitive_load']
        if cognitive_load == 'high':
            recommendations.append("🧠 当前认知负荷较高，建议适当休息")
            recommendations.append("📖 选择较简单的练习题")
        elif cognitive_load == 'low':
            recommendations.append("🚀 可以尝试更具挑战性的内容")
        
        # 基于困惑程度的建议
        confusion_level = model_summary['cognitive_state']['confusion_level']
        if confusion_level in ['moderate', 'severe']:
            recommendations.append("❓ 建议寻求帮助或查看更多示例")
            recommendations.append("📝 多做基础练习题")
        
        # 基于学习偏好的建议
        main_preference = model_summary['learning_preferences']['main_preference']
        if main_preference == 'code_examples':
            recommendations.append("💻 为你推荐更多代码示例")
        elif main_preference == 'text_explanations':
            recommendations.append("📚 为你推荐详细的概念解释")
        
        # 基于行为模式的建议
        if learning_signals.get('engagement_signals', {}).get('activity_ratio', 0) < 0.5:
            recommendations.append("⏰ 建议保持专注，减少分心")
        
        return recommendations


# 单例实例
_api_integration_instance = None

def get_api_integration_service() -> APIIntegrationService:
    """获取API集成服务的单例实例"""
    global _api_integration_instance
    if _api_integration_instance is None:
        _api_integration_instance = APIIntegrationService()
    return _api_integration_instance


# 为了避免循环导入，这里只定义接口，实际的路由注册在app.py中进行
API_ROUTES = {
    'GET /api/v2/student-model/{student_id}': 'get_student_model_summary',
    'POST /api/v2/behavior/log': 'log_behavior_event', 
    'POST /api/v2/quiz/generate': 'generate_adaptive_quiz',
    'POST /api/v2/quiz/evaluate': 'evaluate_quiz_answers',
    'POST /api/v2/performance/update': 'update_performance',
    'GET /api/v2/learning/progress/{student_id}': 'get_learning_progress'
}