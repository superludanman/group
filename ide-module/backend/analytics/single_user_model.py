"""
单用户场景的简化学习者模型

专门为单个学习者设计的深度建模系统，集成贝叶斯知识追踪和机器学习预测
"""

import logging
import time
import os
from typing import Dict, List, Any, Optional
from analytics.improved_student_model import ImprovedStudentModel, ImprovedStudentModelService
from analytics.bayesian_kt import get_adaptive_bkt_system, create_bkt_observation
from analytics.ml_state_predictor import get_ml_state_predictor, FeatureVector

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SingleUserModel")


class SingleUserLearningModel:
    """单用户学习模型 - 简化版本"""
    
    def __init__(self, student_id: str = "main_student"):
        """
        初始化单用户学习模型
        
        Args:
            student_id: 学生ID，默认为主学生
        """
        self.student_id = student_id
        self.session_id = f"session_{int(time.time())}"  # 当前会话
        
        # 核心组件
        self.base_model_service = ImprovedStudentModelService()
        self.bkt_system = get_adaptive_bkt_system()
        self.ml_predictor = get_ml_state_predictor()
        
        # 简化的状态缓存
        self.current_model = None
        self.last_update_time = 0
        
        # 数据目录
        self.data_dir = "data/single_user"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化
        self._initialize_model()
        
        logger.info(f"单用户学习模型初始化完成: {student_id}")
    
    def _initialize_model(self):
        """初始化学习者模型"""
        # 获取基础模型
        self.current_model = self.base_model_service.get_model(self.student_id)
        
        # 尝试加载历史数据
        self._load_persistent_data()
        
        logger.info("学习者模型初始化完成")
    
    def update_from_behavior(self, behavior_data: Dict[str, Any],
                            session_summary: Dict[str, Any]) -> None:
        """
        从行为数据更新模型
        
        Args:
            behavior_data: 行为数据
            session_summary: 会话摘要
        """
        try:
            # 1. 更新基础模型
            self.base_model_service.update_from_behavior_data(
                self.student_id, self.session_id
            )
            
            # 2. 提取特征用于ML预测
            feature_vector = self._extract_features(behavior_data, session_summary)
            
            # 3. 使用ML模型预测状态
            ml_predictions = self.ml_predictor.predict_states(feature_vector)
            
            # 4. 融合ML预测结果到基础模型
            self._integrate_ml_predictions(ml_predictions)
            
            # 5. 更新时间戳
            self.last_update_time = time.time()
            
            # 6. 保存数据（定期）
            if self.last_update_time % 60 < 1:  # 大约每分钟保存一次
                self._save_persistent_data()
            
            logger.info("学习者模型更新完成")
            
        except Exception as e:
            logger.error(f"更新学习者模型失败: {e}")
    
    def update_from_performance(self, knowledge_point_id: str,
                              performance_data: Dict[str, Any]) -> None:
        """
        从学习表现更新模型
        
        Args:
            knowledge_point_id: 知识点ID
            performance_data: 表现数据
        """
        try:
            # 1. 更新基础模型
            self.base_model_service.update_from_performance(
                self.student_id, self.session_id, 
                knowledge_point_id, performance_data
            )
            
            # 2. 更新BKT模型
            bkt_observation = create_bkt_observation(performance_data)
            mastery_prob = self.bkt_system.update_knowledge(
                knowledge_point_id, bkt_observation
            )
            
            # 3. 将BKT结果同步到基础模型
            self._sync_bkt_to_base_model(knowledge_point_id, mastery_prob)
            
            # 4. 为ML模型添加训练样本
            self._add_ml_training_sample(performance_data)
            
            logger.info(f"知识点 {knowledge_point_id} 更新完成，掌握概率: {mastery_prob:.3f}")
            
        except Exception as e:
            logger.error(f"更新知识点表现失败: {e}")
    
    def get_model_summary(self) -> Dict[str, Any]:
        """获取完整的模型摘要"""
        try:
            # 获取基础摘要
            base_summary = self.base_model_service.get_model_summary(self.student_id)
            
            # 获取BKT摘要
            knowledge_points = list(base_summary.get('knowledge_points', {}).keys())
            bkt_summary = self.bkt_system.get_overall_mastery(knowledge_points)
            
            # 获取ML模型状态
            ml_status = self.ml_predictor.get_model_status()
            
            # 融合摘要
            enhanced_summary = base_summary.copy()
            enhanced_summary.update({
                'model_type': 'single_user_enhanced',
                'last_update': self.last_update_time,
                'session_id': self.session_id,
                'bkt_analysis': bkt_summary,
                'ml_model_status': ml_status,
                'enhancement_features': [
                    'bayesian_knowledge_tracking',
                    'ml_state_prediction', 
                    'single_user_optimization',
                    'persistent_data_storage'
                ]
            })
            
            return enhanced_summary
            
        except Exception as e:
            logger.error(f"获取模型摘要失败: {e}")
            return self.base_model_service.get_model_summary(self.student_id)
    
    def predict_next_performance(self, knowledge_point_id: str,
                               task_difficulty: float = 0.5) -> Dict[str, Any]:
        """
        预测下一次学习表现
        
        Args:
            knowledge_point_id: 知识点ID
            task_difficulty: 任务难度
            
        Returns:
            预测结果
        """
        try:
            # BKT预测
            bkt_success_prob, bkt_mastery_prob = self.bkt_system.predict_performance(
                knowledge_point_id, task_difficulty
            )
            
            # 基础模型知识点信息
            base_summary = self.base_model_service.get_model_summary(self.student_id)
            kp_info = base_summary.get('knowledge_points', {}).get(knowledge_point_id, {})
            
            return {
                'knowledge_point': knowledge_point_id,
                'predicted_success_probability': bkt_success_prob,
                'estimated_mastery_level': bkt_mastery_prob,
                'current_knowledge_level': kp_info.get('mastery_score', 1.0),
                'confidence': kp_info.get('confidence', 0.5),
                'task_difficulty': task_difficulty,
                'prediction_timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"预测表现失败: {e}")
            return {
                'knowledge_point': knowledge_point_id,
                'predicted_success_probability': 0.5,
                'estimated_mastery_level': 0.5,
                'error': str(e)
            }
    
    def get_personalized_recommendations(self) -> List[str]:
        """获取个性化学习建议"""
        try:
            base_summary = self.get_model_summary()
            recommendations = []
            
            # 基于认知负荷的建议
            cognitive_load = base_summary.get('cognitive_state', {}).get('cognitive_load')
            if cognitive_load == 'high':
                recommendations.append("当前认知负荷较高，建议适当休息或选择较简单的练习")
            elif cognitive_load == 'low':
                recommendations.append("当前状态良好，可以尝试更有挑战性的任务")
            
            # 基于困惑程度的建议
            confusion_level = base_summary.get('cognitive_state', {}).get('confusion_level')
            if confusion_level in ['moderate', 'severe']:
                recommendations.append("检测到学习困惑，建议回顾基础概念或寻求帮助")
            
            # 基于知识点掌握情况的建议
            bkt_analysis = base_summary.get('bkt_analysis', {})
            struggling_count = bkt_analysis.get('struggling_count', 0)
            well_mastered_count = bkt_analysis.get('well_mastered_count', 0)
            
            if struggling_count > 0:
                recommendations.append(f"有 {struggling_count} 个知识点需要加强练习")
            
            if well_mastered_count > 0:
                recommendations.append(f"已经很好掌握了 {well_mastered_count} 个知识点，可以进入下一阶段")
            
            # 基于学习偏好的建议
            main_preference = base_summary.get('learning_preferences', {}).get('main_preference')
            if main_preference == 'code_examples':
                recommendations.append("建议通过更多代码示例来学习")
            elif main_preference == 'text_explanations':
                recommendations.append("建议多阅读详细的概念解释")
            
            return recommendations[:5]  # 最多返回5条建议
            
        except Exception as e:
            logger.error(f"生成个性化建议失败: {e}")
            return ["继续努力学习，保持良好的学习习惯！"]
    
    def _extract_features(self, behavior_data: Dict[str, Any],
                         session_summary: Dict[str, Any]) -> FeatureVector:
        """提取ML模型特征"""
        try:
            from analytics.ml_state_predictor import FeatureEngineer
            feature_engineer = FeatureEngineer()
            return feature_engineer.extract_features_from_behavior(behavior_data, session_summary)
        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            return FeatureVector()  # 返回默认特征
    
    def _integrate_ml_predictions(self, ml_predictions: Dict[str, Any]) -> None:
        """将ML预测结果集成到基础模型"""
        try:
            if not ml_predictions:
                return
            
            model = self.base_model_service.get_model(self.student_id)
            
            # 认知负荷预测
            if 'cognitive_load' in ml_predictions:
                cog_pred = ml_predictions['cognitive_load']
                if cog_pred.confidence > 0.7:  # 高置信度才应用
                    model.cognitive_state.cognitive_load = cog_pred.prediction
                    model.cognitive_state.load_confidence = cog_pred.confidence
            
            # 困惑程度预测
            if 'confusion' in ml_predictions:
                conf_pred = ml_predictions['confusion']
                if conf_pred.confidence > 0.7:
                    confusion_score = conf_pred.prediction
                    model.cognitive_state.confusion_score = confusion_score
                    
                    # 转换为离散状态
                    if confusion_score > 0.7:
                        model.cognitive_state.confusion_level = "severe"
                    elif confusion_score > 0.5:
                        model.cognitive_state.confusion_level = "moderate"
                    elif confusion_score > 0.2:
                        model.cognitive_state.confusion_level = "slight"
                    else:
                        model.cognitive_state.confusion_level = "none"
            
            logger.debug("ML预测结果已集成到基础模型")
            
        except Exception as e:
            logger.error(f"集成ML预测失败: {e}")
    
    def _sync_bkt_to_base_model(self, knowledge_point_id: str, mastery_prob: float) -> None:
        """同步BKT结果到基础模型"""
        try:
            model = self.base_model_service.get_model(self.student_id)
            
            if knowledge_point_id in model.cognitive_state.knowledge_points:
                kp = model.cognitive_state.knowledge_points[knowledge_point_id]
                
                # 将BKT概率转换为5分制分数
                kp.mastery_score = mastery_prob * 5.0
                kp.confidence = min(kp.confidence + 0.05, 1.0)  # 略微增加置信度
                kp.last_updated = time.time()
                
                logger.debug(f"BKT结果已同步到知识点 {knowledge_point_id}")
            
        except Exception as e:
            logger.error(f"同步BKT结果失败: {e}")
    
    def _add_ml_training_sample(self, performance_data: Dict[str, Any]) -> None:
        """为ML模型添加训练样本"""
        try:
            # 这里简化为基于表现推断状态标签
            success = performance_data.get('success', False)
            difficulty = performance_data.get('difficulty', 0.5)
            
            # 简单的状态推断
            if success and difficulty > 0.7:
                cognitive_load = 'low'
                confusion_score = 0.1
            elif not success and difficulty > 0.5:
                cognitive_load = 'high'
                confusion_score = 0.8
            else:
                cognitive_load = 'medium'
                confusion_score = 0.4
            
            # 添加训练样本（使用默认特征）
            feature = FeatureVector()
            self.ml_predictor.add_training_sample(
                feature, cognitive_load, confusion_score, 0.7
            )
            
            # 定期训练模型
            if len(self.ml_predictor.training_data['features']) >= 20:
                self.ml_predictor.train_models()
            
        except Exception as e:
            logger.error(f"添加ML训练样本失败: {e}")
    
    def _save_persistent_data(self) -> None:
        """保存持久化数据"""
        try:
            # 保存BKT数据
            bkt_file = os.path.join(self.data_dir, 'bkt_data.json')
            self.bkt_system.export_learning_data(bkt_file)
            
            # 保存ML模型
            self.ml_predictor.save_models()
            
            logger.debug("持久化数据保存完成")
            
        except Exception as e:
            logger.error(f"保存持久化数据失败: {e}")
    
    def _load_persistent_data(self) -> None:
        """加载持久化数据"""
        try:
            # 加载ML模型
            self.ml_predictor.load_models()
            
            logger.debug("持久化数据加载完成")
            
        except Exception as e:
            logger.error(f"加载持久化数据失败: {e}")
    
    def export_learning_analytics(self) -> Dict[str, Any]:
        """导出学习分析数据"""
        try:
            summary = self.get_model_summary()
            
            # 导出BKT数据
            bkt_data = self.bkt_system.export_learning_data()
            
            # 组合分析数据
            analytics = {
                'export_timestamp': time.time(),
                'student_id': self.student_id,
                'session_id': self.session_id,
                'model_summary': summary,
                'bkt_detailed_data': bkt_data,
                'ml_model_status': self.ml_predictor.get_model_status(),
                'recommendations': self.get_personalized_recommendations()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"导出学习分析数据失败: {e}")
            return {}


# 单例实例
_single_user_model = None

def get_single_user_model(student_id: str = "main_student") -> SingleUserLearningModel:
    """获取单用户学习模型的单例实例"""
    global _single_user_model
    if _single_user_model is None:
        _single_user_model = SingleUserLearningModel(student_id)
    return _single_user_model