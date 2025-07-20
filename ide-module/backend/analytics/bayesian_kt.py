"""
贝叶斯知识追踪算法实现

基于经典的BKT模型，包含四个核心参数：
- P(L0): 初始知识掌握概率
- P(T): 学会转移概率 (从未掌握到掌握)
- P(G): 猜测概率 (未掌握但答对)
- P(S): 失误概率 (已掌握但答错)

参考文献：
- Corbett, A. T., & Anderson, J. R. (1994). Knowledge tracing: Modeling the acquisition of procedural knowledge.
- Yudelson, M. V., Koedinger, K. R., & Gordon, G. J. (2013). Individualized bayesian knowledge tracing models.
"""

import numpy as np
import logging
import time
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from scipy.optimize import minimize
from sklearn.metrics import log_loss, accuracy_score
import math

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BayesianKT")


@dataclass
class BKTParameters:
    """BKT模型参数"""
    P_L0: float = 0.1    # 初始知识掌握概率
    P_T: float = 0.3     # 学会转移概率
    P_G: float = 0.1     # 猜测概率 (未掌握但答对)
    P_S: float = 0.1     # 失误概率 (已掌握但答错)
    
    def to_array(self) -> np.ndarray:
        """转换为numpy数组用于优化"""
        return np.array([self.P_L0, self.P_T, self.P_G, self.P_S])
    
    @classmethod
    def from_array(cls, params: np.ndarray) -> 'BKTParameters':
        """从numpy数组创建参数对象"""
        return cls(
            P_L0=params[0],
            P_T=params[1], 
            P_G=params[2],
            P_S=params[3]
        )


@dataclass
class LearningObservation:
    """学习观察数据"""
    timestamp: float
    correct: bool           # 是否答对
    response_time: float    # 响应时间(秒)
    difficulty: float       # 题目难度 0-1
    attempts: int          # 尝试次数
    hint_used: bool        # 是否使用提示
    confidence: float      # 学生自评信心度 0-1
    
    
class BayesianKnowledgeTracker:
    """贝叶斯知识追踪器"""
    
    def __init__(self, knowledge_point_id: str, initial_params: Optional[BKTParameters] = None):
        """
        初始化BKT追踪器
        
        Args:
            knowledge_point_id: 知识点标识
            initial_params: 初始BKT参数，如果为None则使用默认值
        """
        self.knowledge_point_id = knowledge_point_id
        self.params = initial_params or BKTParameters()
        
        # 学习轨迹
        self.observations: List[LearningObservation] = []
        self.mastery_probabilities: List[float] = []  # 每次观察后的掌握概率
        
        # 当前状态
        self.current_mastery_prob = self.params.P_L0
        
        logger.info(f"初始化BKT追踪器: {knowledge_point_id}, P(L0)={self.params.P_L0:.3f}")
    
    def update_mastery(self, observation: LearningObservation) -> float:
        """
        基于新观察更新知识掌握概率
        
        Args:
            observation: 学习观察数据
            
        Returns:
            更新后的掌握概率
        """
        # 记录观察
        self.observations.append(observation)
        
        # 计算观察概率 P(correct|L_t-1)
        if observation.correct:
            # 答对的概率 = 已掌握且不失误 + 未掌握但猜对
            p_correct_given_mastery = 1 - self.params.P_S
            p_correct_given_no_mastery = self.params.P_G
        else:
            # 答错的概率 = 已掌握但失误 + 未掌握且猜错
            p_correct_given_mastery = self.params.P_S
            p_correct_given_no_mastery = 1 - self.params.P_G
        
        # 贝叶斯更新：P(L_t|evidence) = P(evidence|L_t) * P(L_t-1) / P(evidence)
        numerator = p_correct_given_mastery * self.current_mastery_prob
        denominator = (p_correct_given_mastery * self.current_mastery_prob + 
                      p_correct_given_no_mastery * (1 - self.current_mastery_prob))
        
        # 避免除零
        if denominator < 1e-10:
            denominator = 1e-10
            
        posterior_mastery = numerator / denominator
        
        # 应用学习转移：P(L_t) = P(L_t|evidence) + P(T) * (1 - P(L_t|evidence))
        self.current_mastery_prob = posterior_mastery + self.params.P_T * (1 - posterior_mastery)
        
        # 记录轨迹
        self.mastery_probabilities.append(self.current_mastery_prob)
        
        logger.debug(f"BKT更新 {self.knowledge_point_id}: 答对={observation.correct}, "
                    f"掌握概率={self.current_mastery_prob:.3f}")
        
        return self.current_mastery_prob
    
    def predict_performance(self, difficulty: float = 0.5) -> Tuple[float, float]:
        """
        预测下一次答题表现
        
        Args:
            difficulty: 题目难度
            
        Returns:
            (答对概率, 掌握概率)
        """
        # 基础答对概率
        base_prob = (self.current_mastery_prob * (1 - self.params.P_S) + 
                    (1 - self.current_mastery_prob) * self.params.P_G)
        
        # 难度调整 (简单的线性调整)
        difficulty_factor = 1.0 - difficulty * 0.3  # 难度越高，答对概率越低
        adjusted_prob = base_prob * difficulty_factor
        
        return min(max(adjusted_prob, 0.01), 0.99), self.current_mastery_prob
    
    def get_learning_trajectory(self) -> Dict[str, Any]:
        """获取学习轨迹分析"""
        if not self.observations:
            return {}
        
        # 计算学习指标
        correct_answers = [obs.correct for obs in self.observations]
        accuracy = sum(correct_answers) / len(correct_answers)
        
        # 学习速度 (掌握概率增长率)
        if len(self.mastery_probabilities) > 1:
            initial_prob = self.mastery_probabilities[0]
            final_prob = self.mastery_probabilities[-1]
            learning_rate = (final_prob - initial_prob) / len(self.mastery_probabilities)
        else:
            learning_rate = 0.0
        
        # 稳定性 (最近几次的方差)
        recent_probs = self.mastery_probabilities[-5:] if len(self.mastery_probabilities) >= 5 else self.mastery_probabilities
        stability = 1.0 - (np.var(recent_probs) if len(recent_probs) > 1 else 0.0)
        
        return {
            'total_attempts': len(self.observations),
            'accuracy': accuracy,
            'current_mastery': self.current_mastery_prob,
            'learning_rate': learning_rate,
            'stability': stability,
            'mastery_trajectory': self.mastery_probabilities,
            'observation_timestamps': [obs.timestamp for obs in self.observations]
        }


class BKTParameterEstimator:
    """BKT参数估计器"""
    
    def __init__(self):
        """初始化参数估计器"""
        self.fitted_params: Dict[str, BKTParameters] = {}
        logger.info("BKT参数估计器已初始化")
    
    def fit_parameters(self, knowledge_point_id: str, 
                      observations: List[LearningObservation],
                      method: str = 'mle') -> BKTParameters:
        """
        基于观察数据估计BKT参数
        
        Args:
            knowledge_point_id: 知识点ID
            observations: 观察数据列表
            method: 估计方法 ('mle' for Maximum Likelihood Estimation)
            
        Returns:
            估计的BKT参数
        """
        if not observations:
            logger.warning(f"知识点 {knowledge_point_id} 没有观察数据，使用默认参数")
            return BKTParameters()
        
        if method == 'mle':
            return self._fit_mle(knowledge_point_id, observations)
        else:
            raise ValueError(f"不支持的参数估计方法: {method}")
    
    def _fit_mle(self, knowledge_point_id: str, 
                observations: List[LearningObservation]) -> BKTParameters:
        """最大似然估计BKT参数"""
        
        def negative_log_likelihood(params_array: np.ndarray) -> float:
            """负对数似然函数"""
            # 参数约束
            if not all(0.01 <= p <= 0.99 for p in params_array):
                return 1e6
            
            params = BKTParameters.from_array(params_array)
            
            # 创建临时追踪器
            tracker = BayesianKnowledgeTracker(knowledge_point_id, params)
            
            log_likelihood = 0.0
            
            for obs in observations:
                # 计算当前观察的概率
                if obs.correct:
                    prob = (tracker.current_mastery_prob * (1 - params.P_S) + 
                           (1 - tracker.current_mastery_prob) * params.P_G)
                else:
                    prob = (tracker.current_mastery_prob * params.P_S + 
                           (1 - tracker.current_mastery_prob) * (1 - params.P_G))
                
                # 避免log(0)
                prob = max(prob, 1e-10)
                log_likelihood += math.log(prob)
                
                # 更新状态
                tracker.update_mastery(obs)
            
            return -log_likelihood
        
        # 初始参数猜测
        initial_guess = np.array([0.1, 0.3, 0.1, 0.1])
        
        # 参数边界
        bounds = [(0.01, 0.99), (0.01, 0.99), (0.01, 0.99), (0.01, 0.99)]
        
        try:
            # 优化
            result = minimize(negative_log_likelihood, initial_guess, 
                            method='L-BFGS-B', bounds=bounds)
            
            if result.success:
                fitted_params = BKTParameters.from_array(result.x)
                self.fitted_params[knowledge_point_id] = fitted_params
                
                logger.info(f"成功拟合 {knowledge_point_id} 的BKT参数: "
                           f"P(L0)={fitted_params.P_L0:.3f}, P(T)={fitted_params.P_T:.3f}, "
                           f"P(G)={fitted_params.P_G:.3f}, P(S)={fitted_params.P_S:.3f}")
                
                return fitted_params
            else:
                logger.warning(f"参数优化失败: {result.message}")
                return BKTParameters()
                
        except Exception as e:
            logger.error(f"参数拟合异常: {e}")
            return BKTParameters()


class AdaptiveBKTSystem:
    """自适应BKT系统 - 管理多个知识点的BKT追踪"""
    
    def __init__(self):
        """初始化自适应BKT系统"""
        self.trackers: Dict[str, BayesianKnowledgeTracker] = {}
        self.parameter_estimator = BKTParameterEstimator()
        
        # 系统配置
        self.min_observations_for_fitting = 10  # 最少观察数才进行参数拟合
        self.refit_interval = 20  # 每20次观察重新拟合一次参数
        
        logger.info("自适应BKT系统已初始化")
    
    def get_tracker(self, knowledge_point_id: str) -> BayesianKnowledgeTracker:
        """获取或创建知识点追踪器"""
        if knowledge_point_id not in self.trackers:
            # 检查是否有已拟合的参数
            if knowledge_point_id in self.parameter_estimator.fitted_params:
                params = self.parameter_estimator.fitted_params[knowledge_point_id]
            else:
                params = BKTParameters()
            
            self.trackers[knowledge_point_id] = BayesianKnowledgeTracker(
                knowledge_point_id, params
            )
        
        return self.trackers[knowledge_point_id]
    
    def update_knowledge(self, knowledge_point_id: str, 
                        observation: LearningObservation) -> float:
        """更新知识点掌握情况"""
        tracker = self.get_tracker(knowledge_point_id)
        mastery_prob = tracker.update_mastery(observation)
        
        # 检查是否需要重新拟合参数
        if (len(tracker.observations) >= self.min_observations_for_fitting and 
            len(tracker.observations) % self.refit_interval == 0):
            
            self._refit_parameters(knowledge_point_id)
        
        return mastery_prob
    
    def predict_performance(self, knowledge_point_id: str, 
                          difficulty: float = 0.5) -> Tuple[float, float]:
        """预测知识点表现"""
        tracker = self.get_tracker(knowledge_point_id)
        return tracker.predict_performance(difficulty)
    
    def get_overall_mastery(self, knowledge_point_ids: List[str]) -> Dict[str, Any]:
        """获取整体掌握情况"""
        overall_stats = {}
        
        for kp_id in knowledge_point_ids:
            if kp_id in self.trackers:
                tracker = self.trackers[kp_id]
                trajectory = tracker.get_learning_trajectory()
                overall_stats[kp_id] = {
                    'mastery_probability': tracker.current_mastery_prob,
                    'trajectory': trajectory
                }
            else:
                overall_stats[kp_id] = {
                    'mastery_probability': 0.1,  # 默认初始值
                    'trajectory': {}
                }
        
        # 计算平均掌握度
        mastery_probs = [stats['mastery_probability'] for stats in overall_stats.values()]
        average_mastery = sum(mastery_probs) / len(mastery_probs) if mastery_probs else 0.1
        
        return {
            'knowledge_points': overall_stats,
            'average_mastery': average_mastery,
            'total_knowledge_points': len(knowledge_point_ids),
            'well_mastered_count': sum(1 for p in mastery_probs if p > 0.8),
            'struggling_count': sum(1 for p in mastery_probs if p < 0.3)
        }
    
    def _refit_parameters(self, knowledge_point_id: str) -> None:
        """重新拟合知识点的BKT参数"""
        if knowledge_point_id not in self.trackers:
            return
        
        tracker = self.trackers[knowledge_point_id]
        
        try:
            # 拟合新参数
            new_params = self.parameter_estimator.fit_parameters(
                knowledge_point_id, tracker.observations
            )
            
            # 更新追踪器参数
            tracker.params = new_params
            
            logger.info(f"重新拟合 {knowledge_point_id} 的BKT参数完成")
            
        except Exception as e:
            logger.error(f"重新拟合参数失败: {e}")
    
    def export_learning_data(self, filename: str = None) -> Dict[str, Any]:
        """导出学习数据用于分析"""
        export_data = {
            'timestamp': time.time(),
            'trackers': {},
            'fitted_parameters': {}
        }
        
        # 导出追踪器数据
        for kp_id, tracker in self.trackers.items():
            export_data['trackers'][kp_id] = {
                'parameters': asdict(tracker.params),
                'observations': [asdict(obs) for obs in tracker.observations],
                'mastery_probabilities': tracker.mastery_probabilities,
                'current_mastery': tracker.current_mastery_prob,
                'trajectory': tracker.get_learning_trajectory()
            }
        
        # 导出拟合参数
        for kp_id, params in self.parameter_estimator.fitted_params.items():
            export_data['fitted_parameters'][kp_id] = asdict(params)
        
        # 保存到文件
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                logger.info(f"学习数据已导出到: {filename}")
            except Exception as e:
                logger.error(f"导出数据失败: {e}")
        
        return export_data


# 单例实例
_adaptive_bkt_system = None

def get_adaptive_bkt_system() -> AdaptiveBKTSystem:
    """获取自适应BKT系统的单例实例"""
    global _adaptive_bkt_system
    if _adaptive_bkt_system is None:
        _adaptive_bkt_system = AdaptiveBKTSystem()
    return _adaptive_bkt_system


# 辅助函数：从通用数据创建BKT观察
def create_bkt_observation(performance_data: Dict[str, Any]) -> LearningObservation:
    """从通用性能数据创建BKT观察"""
    return LearningObservation(
        timestamp=performance_data.get('timestamp', time.time()),
        correct=performance_data.get('success', False),
        response_time=performance_data.get('time_spent', 30.0),
        difficulty=performance_data.get('difficulty', 0.5),
        attempts=performance_data.get('attempts', 1),
        hint_used=performance_data.get('hint_used', False),
        confidence=performance_data.get('confidence', 0.5)
    )