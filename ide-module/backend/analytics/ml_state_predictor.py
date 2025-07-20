"""
机器学习状态预测模型

使用随机森林和其他ML算法来预测学习者的认知和情感状态
支持特征工程、模型训练、在线预测和不确定度估计
"""

import numpy as np
import logging
import time
import pickle
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error
from sklearn.feature_selection import SelectKBest, f_classif, f_regression
import joblib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MLStatePredictor")


@dataclass
class FeatureVector:
    """特征向量"""
    # 基础行为特征
    edit_frequency: float = 0.0          # 编辑频率 (次/分钟)
    edit_chars_per_minute: float = 0.0   # 编辑字符速度
    avg_pause_duration: float = 5.0      # 平均停顿时长
    error_rate: float = 0.0              # 错误率
    help_frequency: float = 0.0          # 求助频率
    
    # 时间模式特征
    session_duration: float = 0.0        # 会话持续时间
    active_time_ratio: float = 0.5       # 活跃时间比例
    
    # 代码质量特征
    code_length_variance: float = 0.0    # 代码长度方差
    syntax_error_ratio: float = 0.0      # 语法错误比例
    logical_error_ratio: float = 0.0     # 逻辑错误比例
    
    # 交互模式特征
    cursor_jump_frequency: float = 0.0   # 光标跳转频率
    backspace_frequency: float = 0.0     # 退格频率
    copy_paste_frequency: float = 0.0    # 复制粘贴频率
    
    # 学习历史特征
    recent_success_rate: float = 0.5      # 最近成功率
    learning_streak: int = 0              # 连续学习天数
    total_practice_time: float = 0.0      # 总练习时间
    
    # 上下文特征
    task_difficulty: float = 0.5          # 当前任务难度
    time_of_day: float = 12.0            # 学习时间 (0-24)
    day_of_week: int = 1                 # 周几 (1-7)
    
    def to_array(self) -> np.ndarray:
        """转换为numpy数组"""
        return np.array([
            self.edit_frequency, self.edit_chars_per_minute, self.avg_pause_duration,
            self.error_rate, self.help_frequency, self.session_duration,
            self.active_time_ratio, self.code_length_variance, self.syntax_error_ratio,
            self.logical_error_ratio, self.cursor_jump_frequency, self.backspace_frequency,
            self.copy_paste_frequency, self.recent_success_rate, self.learning_streak,
            self.total_practice_time, self.task_difficulty, self.time_of_day, self.day_of_week
        ])
    
    def to_dict(self) -> Dict[str, float]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def get_feature_names(cls) -> List[str]:
        """获取特征名称列表"""
        return [
            'edit_frequency', 'edit_chars_per_minute', 'avg_pause_duration',
            'error_rate', 'help_frequency', 'session_duration',
            'active_time_ratio', 'code_length_variance', 'syntax_error_ratio',
            'logical_error_ratio', 'cursor_jump_frequency', 'backspace_frequency',
            'copy_paste_frequency', 'recent_success_rate', 'learning_streak',
            'total_practice_time', 'task_difficulty', 'time_of_day', 'day_of_week'
        ]


@dataclass
class PredictionResult:
    """预测结果"""
    prediction: Union[str, float]  # 预测值
    confidence: float              # 置信度 0-1
    probabilities: Optional[Dict[str, float]] = None  # 类别概率分布
    feature_importance: Optional[Dict[str, float]] = None  # 特征重要性


class FeatureEngineer:
    """特征工程器"""
    
    def __init__(self, mode: str = "classification", k: int = 15):
        """初始化特征工程器
        
        Args:
            mode: "classification" 或 "regression"
            k:    选择前 k 个最重要特征
        """
        self.mode = mode
        self.scaler = StandardScaler()
        if k and k > 0:
            if mode == "classification":
                self.feature_selector = SelectKBest(f_classif, k=k)
            else:
                self.feature_selector = SelectKBest(f_regression, k=k)
        else:
            self.feature_selector = None
        self.is_fitted = False
        logger.info(f"特征工程器已初始化, mode={mode}")
    
    def extract_features_from_behavior(self, behavior_data: Dict[str, Any],
                                     session_summary: Dict[str, Any]) -> FeatureVector:
        """从行为数据中提取特征"""
        
        # 从行为信号中提取
        cognitive_signals = behavior_data.get('cognitive_load_signals', {})
        confusion_signals = behavior_data.get('confusion_signals', {})
        engagement_signals = behavior_data.get('engagement_signals', {})
        
        # 从会话摘要中提取
        edit_freq = session_summary.get('edit_frequency', 0.0)
        error_rate = session_summary.get('error_rate', 0.0)
        help_freq = session_summary.get('help_frequency', 0.0)
        
        # 时间特征
        now = time.localtime()
        hour = now.tm_hour
        weekday = now.tm_wday + 1
        
        return FeatureVector(
            edit_frequency=edit_freq,
            edit_chars_per_minute=session_summary.get('edit_chars_per_minute', 0.0),
            avg_pause_duration=cognitive_signals.get('avg_pause_duration', 5.0),
            error_rate=error_rate,
            help_frequency=help_freq,
            session_duration=session_summary.get('session_duration', 0.0),
            active_time_ratio=engagement_signals.get('activity_ratio', 0.5),
            code_length_variance=confusion_signals.get('edit_randomness', 0.0),
            syntax_error_ratio=min(error_rate, 1.0),  # 简化，假设都是语法错误
            logical_error_ratio=0.0,
            cursor_jump_frequency=0.0,  # 暂时设为0，需要前端支持
            backspace_frequency=0.0,
            copy_paste_frequency=0.0,
            recent_success_rate=session_summary.get('recent_success_rate', 0.5),
            learning_streak=0,  # 需要历史数据
            total_practice_time=session_summary.get('session_duration', 0.0),
            task_difficulty=0.5,  # 需要任务信息
            time_of_day=hour,
            day_of_week=weekday
        )
    
    def fit_transform(self, features: List[FeatureVector], y: Optional[Union[List, np.ndarray]] = None) -> np.ndarray:
        """拟合并转换特征
        
        若 y 为空或标签只有一个类别，则跳过特征选择，仅做标准化。
        """
        if not features:
            raise ValueError("特征列表不能为空")
        
        X = np.array([f.to_array() for f in features])
        X_scaled = self.scaler.fit_transform(X)
        
        if self.feature_selector and y is not None and len(set(y)) > 1:
            X_selected = self.feature_selector.fit_transform(X_scaled, y)
        else:
            X_selected = X_scaled
        
        self.is_fitted = True
        logger.info(f"特征工程拟合完成，特征维度: {X_selected.shape[1]}")
        return X_selected
    
    def transform(self, features: List[FeatureVector]) -> np.ndarray:
        """转换特征"""
        if not self.is_fitted:
            raise ValueError("特征工程器尚未拟合")
        
        X = np.array([f.to_array() for f in features])
        X_scaled = self.scaler.transform(X)
        if self.feature_selector:
            X_selected = self.feature_selector.transform(X_scaled)
        else:
            X_selected = X_scaled
        return X_selected
    
    def get_selected_features(self) -> List[str]:
        """获取选中的特征名称"""
        if not self.is_fitted:
            return []
        
        if not self.feature_selector:
            return FeatureVector.get_feature_names()
        feature_names = FeatureVector.get_feature_names()
        selected_indices = self.feature_selector.get_support(indices=True)
        return [feature_names[i] for i in selected_indices]


class CognitiveLoadPredictor:
    """认知负荷预测器"""
    
    def __init__(self):
        """初始化认知负荷预测器"""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.feature_engineer = FeatureEngineer(mode="classification")
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
        # 认知负荷类别
        self.load_levels = ['low', 'medium', 'high']
        
        logger.info("认知负荷预测器已初始化")
    
    def train(self, features: List[FeatureVector], labels: List[str]) -> Dict[str, float]:
        """训练模型"""
        if len(features) != len(labels):
            raise ValueError("特征和标签数量不匹配")
        
        if len(features) < 10:
            logger.warning("训练样本过少，预测可能不准确")
        
        try:
            # 标签编码
            y = self.label_encoder.fit_transform(labels)
            # 特征工程
            X = self.feature_engineer.fit_transform(features, y)
            
            # 训练模型
            self.model.fit(X, y)
            self.is_trained = True
            
            # 交叉验证评估
            cv_scores = cross_val_score(self.model, X, y, cv=min(5, len(features)))
            avg_score = np.mean(cv_scores)
            
            logger.info(f"认知负荷预测器训练完成，交叉验证准确率: {avg_score:.3f}")
            
            return {
                'accuracy': avg_score,
                'std': np.std(cv_scores),
                'n_samples': len(features),
                'n_features': X.shape[1]
            }
            
        except Exception as e:
            logger.error(f"认知负荷预测器训练失败: {e}")
            raise
    
    def predict(self, feature: FeatureVector) -> PredictionResult:
        """预测认知负荷"""
        if not self.is_trained:
            # 如果未训练，使用规则基预测
            return self._rule_based_prediction(feature)
        
        try:
            # 特征转换
            X = self.feature_engineer.transform([feature])
            
            # 预测
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            
            # 转换回标签
            predicted_label = self.label_encoder.inverse_transform([prediction])[0]
            
            # 置信度 (最高概率)
            confidence = np.max(probabilities)
            
            # 概率分布
            class_labels = self.label_encoder.inverse_transform(range(len(probabilities)))
            prob_dict = {label: prob for label, prob in zip(class_labels, probabilities)}
            
            # 特征重要性
            feature_importance = dict(zip(
                self.feature_engineer.get_selected_features(),
                self.model.feature_importances_
            ))
            
            return PredictionResult(
                prediction=predicted_label,
                confidence=confidence,
                probabilities=prob_dict,
                feature_importance=feature_importance
            )
            
        except Exception as e:
            logger.error(f"认知负荷预测失败: {e}")
            return self._rule_based_prediction(feature)
    
    def _rule_based_prediction(self, feature: FeatureVector) -> PredictionResult:
        """基于规则的认知负荷预测（备用方案）"""
        # 简单的规则基预测
        score = (
            (feature.edit_frequency / 10) * 0.3 +
            (feature.error_rate) * 0.4 +
            max(0, 1 - feature.avg_pause_duration / 30) * 0.3
        )
        
        if score > 0.7:
            prediction = 'high'
            confidence = min(score, 0.9)
        elif score > 0.4:
            prediction = 'medium'
            confidence = 0.7
        else:
            prediction = 'low'
            confidence = min(1 - score, 0.9)
        
        return PredictionResult(
            prediction=prediction,
            confidence=confidence,
            probabilities={
                'low': max(0, 1 - score),
                'medium': max(0, 1 - abs(score - 0.5) * 2),
                'high': max(0, score)
            }
        )


class ConfusionPredictor:
    """困惑程度预测器"""
    
    def __init__(self):
        """初始化困惑程度预测器"""
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.feature_engineer = FeatureEngineer(mode="regression")
        self.is_trained = False
        
        logger.info("困惑程度预测器已初始化")
    
    def train(self, features: List[FeatureVector], scores: List[float]) -> Dict[str, float]:
        """训练模型"""
        if len(features) != len(scores):
            raise ValueError("特征和分数数量不匹配")
        
        try:
            y = np.array(scores)
            # 特征工程
            X = self.feature_engineer.fit_transform(features, y)
            
            # 训练模型
            self.model.fit(X, y)
            self.is_trained = True
            
            # 评估
            y_pred = self.model.predict(X)
            mse = mean_squared_error(y, y_pred)
            
            logger.info(f"困惑程度预测器训练完成，MSE: {mse:.3f}")
            
            return {
                'mse': mse,
                'n_samples': len(features),
                'n_features': X.shape[1]
            }
            
        except Exception as e:
            logger.error(f"困惑程度预测器训练失败: {e}")
            raise
    
    def predict(self, feature: FeatureVector) -> PredictionResult:
        """预测困惑程度分数 (0-1)"""
        if not self.is_trained:
            return self._rule_based_confusion_prediction(feature)
        
        try:
            X = self.feature_engineer.transform([feature])
            preds = np.array([est.predict(X)[0] for est in self.model.estimators_])
            score = float(np.clip(preds.mean(), 0, 1))
            std = preds.std()
            confidence = float(np.clip(1 - std, 0.1, 0.95))
            
            return PredictionResult(
                prediction=score,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"困惑程度预测失败: {e}")
            return self._rule_based_confusion_prediction(feature)
    
    def _rule_based_confusion_prediction(self, feature: FeatureVector) -> PredictionResult:
        """基于规则的困惑程度预测"""
        score = (
            feature.help_frequency / 5 * 0.4 +
            feature.error_rate * 0.3 +
            feature.code_length_variance * 0.3
        )
        
        score = max(0, min(score, 1))
        
        return PredictionResult(
            prediction=score,
            confidence=0.6
        )


class MLStatePredictor:
    """机器学习状态预测器 - 统一接口"""
    
    def __init__(self, model_dir: str = "models"):
        """
        初始化ML状态预测器
        
        Args:
            model_dir: 模型保存目录
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # 子预测器
        self.cognitive_load_predictor = CognitiveLoadPredictor()
        self.confusion_predictor = ConfusionPredictor()
        
        # 训练数据缓存
        self.training_data = {
            'features': [],
            'cognitive_load_labels': [],
            'confusion_scores': [],
            'focus_scores': []
        }
        
        logger.info(f"ML状态预测器已初始化，模型目录: {model_dir}")
    
    def add_training_sample(self, feature: FeatureVector,
                           cognitive_load: str,
                           confusion_score: float,
                           focus_score: float) -> None:
        """添加训练样本"""
        self.training_data['features'].append(feature)
        self.training_data['cognitive_load_labels'].append(cognitive_load)
        self.training_data['confusion_scores'].append(confusion_score)
        self.training_data['focus_scores'].append(focus_score)
        
        logger.debug(f"添加训练样本，当前样本数: {len(self.training_data['features'])}")
    
    def train_models(self) -> Dict[str, Dict[str, float]]:
        """训练所有模型"""
        if len(self.training_data['features']) < 5:
            logger.warning("训练样本不足，跳过模型训练")
            return {}
        
        results = {}
        
        try:
            # 训练认知负荷预测器
            cog_results = self.cognitive_load_predictor.train(
                self.training_data['features'],
                self.training_data['cognitive_load_labels']
            )
            results['cognitive_load'] = cog_results
            
            # 训练困惑程度预测器
            conf_results = self.confusion_predictor.train(
                self.training_data['features'],
                self.training_data['confusion_scores']
            )
            results['confusion'] = conf_results
            
            logger.info("所有ML模型训练完成")
            
            # 保存模型
            self.save_models()
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
        
        return results
    
    def predict_states(self, feature: FeatureVector) -> Dict[str, PredictionResult]:
        """预测所有状态"""
        results = {}
        
        # 预测认知负荷
        results['cognitive_load'] = self.cognitive_load_predictor.predict(feature)
        
        # 预测困惑程度
        results['confusion'] = self.confusion_predictor.predict(feature)
        
        return results
    
    def save_models(self) -> None:
        """保存模型到文件"""
        try:
            # 保存认知负荷预测器
            if self.cognitive_load_predictor.is_trained:
                joblib.dump(
                    self.cognitive_load_predictor,
                    os.path.join(self.model_dir, 'cognitive_load_predictor.pkl')
                )
            
            # 保存困惑预测器
            if self.confusion_predictor.is_trained:
                joblib.dump(
                    self.confusion_predictor,
                    os.path.join(self.model_dir, 'confusion_predictor.pkl')
                )
            
            # 保存训练数据
            with open(os.path.join(self.model_dir, 'training_data.pkl'), 'wb') as f:
                pickle.dump(self.training_data, f)
            
            logger.info("模型保存完成")
            
        except Exception as e:
            logger.error(f"模型保存失败: {e}")
    
    def load_models(self) -> bool:
        """从文件加载模型"""
        try:
            # 加载认知负荷预测器
            cog_path = os.path.join(self.model_dir, 'cognitive_load_predictor.pkl')
            if os.path.exists(cog_path):
                self.cognitive_load_predictor = joblib.load(cog_path)
            
            # 加载困惑预测器
            conf_path = os.path.join(self.model_dir, 'confusion_predictor.pkl')
            if os.path.exists(conf_path):
                self.confusion_predictor = joblib.load(conf_path)
            
            # 加载训练数据
            data_path = os.path.join(self.model_dir, 'training_data.pkl')
            if os.path.exists(data_path):
                with open(data_path, 'rb') as f:
                    self.training_data = pickle.load(f)
            
            logger.info("模型加载完成")
            return True
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """获取模型状态"""
        return {
            'cognitive_load_trained': self.cognitive_load_predictor.is_trained,
            'confusion_trained': self.confusion_predictor.is_trained,
            'training_samples': len(self.training_data['features']),
            'model_dir': self.model_dir
        }


# 单例实例
_ml_state_predictor = None

def get_ml_state_predictor() -> MLStatePredictor:
    """获取ML状态预测器的单例实例"""
    global _ml_state_predictor
    if _ml_state_predictor is None:
        _ml_state_predictor = MLStatePredictor()
        # 尝试加载已有模型
        _ml_state_predictor.load_models()
    return _ml_state_predictor