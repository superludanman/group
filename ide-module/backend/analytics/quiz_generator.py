"""
自动出题系统 - 基于学习者模型生成个性化测试题

支持的题目类型：
1. 代码填空题 - 给出部分代码，让学生填写关键部分
2. 错误修正题 - 给出有bug的代码，让学生找出并修正
3. 功能实现题 - 给出需求描述，让学生写代码实现
4. 概念问答题 - 在AI对话中进行概念验证(可选)
"""

import logging
import json
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuizGenerator")


class QuestionType(str, Enum):
    """题目类型枚举"""
    FILL_IN_BLANK = "fill_in_blank"     # 代码填空题
    ERROR_CORRECTION = "error_correction" # 错误修正题
    CODE_IMPLEMENTATION = "code_implementation" # 功能实现题
    CONCEPT_EXPLANATION = "concept_explanation" # 概念解释题


class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    EASY = "easy"         # 简单
    MEDIUM = "medium"     # 中等
    HARD = "hard"         # 困难


@dataclass
class CodeTemplate:
    """代码模板"""
    template: str           # 代码模板，包含占位符
    blanks: List[str]      # 需要填写的部分
    knowledge_points: List[str]  # 相关知识点
    difficulty: DifficultyLevel
    hints: List[str]       # 提示信息


@dataclass
class BuggyCode:
    """带错误的代码"""
    buggy_code: str        # 有错误的代码
    correct_code: str      # 正确的代码
    error_type: str        # 错误类型
    error_description: str # 错误描述
    knowledge_points: List[str]
    difficulty: DifficultyLevel


@dataclass
class ImplementationTask:
    """实现任务"""
    description: str       # 任务描述
    requirements: List[str] # 具体要求
    starter_code: str      # 起始代码
    expected_output: str   # 期望输出
    knowledge_points: List[str]
    difficulty: DifficultyLevel
    test_cases: List[Dict] # 测试用例


@dataclass
class Question:
    """题目数据结构"""
    id: str
    type: QuestionType
    title: str
    content: str
    knowledge_points: List[str]
    difficulty: DifficultyLevel
    estimated_time: int    # 预估完成时间（分钟）
    
    # 题目特定数据
    template: Optional[CodeTemplate] = None
    buggy_code: Optional[BuggyCode] = None
    implementation_task: Optional[ImplementationTask] = None
    
    # 评分相关
    max_score: int = 100
    scoring_criteria: Dict[str, int] = None


class QuizGenerator:
    """自动出题生成器"""
    
    def __init__(self):
        """初始化出题系统"""
        self.question_templates = self._load_question_templates()
        self.difficulty_adjustments = {
            DifficultyLevel.EASY: {'time_multiplier': 0.8, 'hint_level': 3},
            DifficultyLevel.MEDIUM: {'time_multiplier': 1.0, 'hint_level': 2},
            DifficultyLevel.HARD: {'time_multiplier': 1.5, 'hint_level': 1}
        }
        logger.info("自动出题系统已初始化")
    
    def generate_adaptive_quiz(self, student_model_summary: Dict[str, Any],
                             target_knowledge_points: List[str],
                             num_questions: int = 3) -> List[Question]:
        """
        基于学习者模型生成自适应测试题
        
        Args:
            student_model_summary: 学习者模型摘要
            target_knowledge_points: 目标知识点
            num_questions: 题目数量
            
        Returns:
            生成的题目列表
        """
        questions = []
        
        # 分析学习者状态
        avg_knowledge_level = student_model_summary['cognitive_state']['knowledge_level']
        confusion_level = student_model_summary['cognitive_state']['confusion_level']
        cognitive_load = student_model_summary['cognitive_state']['cognitive_load']
        main_preference = student_model_summary['learning_preferences']['main_preference']
        
        # 确定难度分布
        difficulty_distribution = self._determine_difficulty_distribution(
            avg_knowledge_level, confusion_level, cognitive_load
        )
        
        # 确定题型分布
        question_type_distribution = self._determine_question_type_distribution(
            main_preference, avg_knowledge_level
        )
        
        # 生成题目
        for i in range(num_questions):
            # 选择知识点
            kp = target_knowledge_points[i % len(target_knowledge_points)]
            
            # 选择难度
            difficulty = self._select_difficulty(difficulty_distribution)
            
            # 选择题型
            question_type = self._select_question_type(question_type_distribution)
            
            # 生成题目
            question = self._generate_question(kp, difficulty, question_type, student_model_summary)
            
            if question:
                questions.append(question)
                logger.info(f"生成题目: {question.type} - {kp} - {difficulty}")
        
        return questions
    
    def _determine_difficulty_distribution(self, knowledge_level: float,
                                         confusion_level: str, 
                                         cognitive_load: str) -> Dict[DifficultyLevel, float]:
        """确定难度分布"""
        
        # 基础分布
        if knowledge_level < 2.0:  # 初学者
            base_distribution = {
                DifficultyLevel.EASY: 0.7,
                DifficultyLevel.MEDIUM: 0.3,
                DifficultyLevel.HARD: 0.0
            }
        elif knowledge_level < 3.5:  # 中级
            base_distribution = {
                DifficultyLevel.EASY: 0.4,
                DifficultyLevel.MEDIUM: 0.5,
                DifficultyLevel.HARD: 0.1
            }
        else:  # 高级
            base_distribution = {
                DifficultyLevel.EASY: 0.2,
                DifficultyLevel.MEDIUM: 0.5,
                DifficultyLevel.HARD: 0.3
            }
        
        # 根据认知状态调整
        if confusion_level in ["moderate", "severe"] or cognitive_load == "high":
            # 困惑或认知负荷高时，降低难度
            base_distribution[DifficultyLevel.EASY] += 0.2
            base_distribution[DifficultyLevel.HARD] = max(0, base_distribution[DifficultyLevel.HARD] - 0.2)
        
        # 归一化
        total = sum(base_distribution.values())
        if total == 0:
            # 回退到均匀分布
            n = len(base_distribution)
            return {k: 1.0 / n for k in base_distribution}
        return {k: v/total for k, v in base_distribution.items()}
    
    def _determine_question_type_distribution(self, main_preference: str,
                                            knowledge_level: float) -> Dict[QuestionType, float]:
        """确定题型分布"""
        
        # 基础分布
        base_distribution = {
            QuestionType.FILL_IN_BLANK: 0.4,
            QuestionType.ERROR_CORRECTION: 0.3,
            QuestionType.CODE_IMPLEMENTATION: 0.2,
            QuestionType.CONCEPT_EXPLANATION: 0.1
        }
        
        # 根据学习偏好调整
        if main_preference == "code_examples":
            base_distribution[QuestionType.FILL_IN_BLANK] += 0.2
            base_distribution[QuestionType.CODE_IMPLEMENTATION] += 0.1
        elif main_preference == "text_explanations":
            base_distribution[QuestionType.CONCEPT_EXPLANATION] += 0.2
        
        # 根据知识水平调整
        if knowledge_level < 2.0:  # 初学者多做填空题
            base_distribution[QuestionType.FILL_IN_BLANK] += 0.2
            base_distribution[QuestionType.CODE_IMPLEMENTATION] -= 0.1
        elif knowledge_level > 3.5:  # 高级多做实现题
            base_distribution[QuestionType.CODE_IMPLEMENTATION] += 0.2
            base_distribution[QuestionType.FILL_IN_BLANK] -= 0.1
        
        # 归一化
        total = sum(max(0, v) for v in base_distribution.values())
        if total == 0:
            n = len(base_distribution)
            return {k: 1.0 / n for k in base_distribution}
        return {k: max(0, v)/total for k, v in base_distribution.items()}
    
    def _select_difficulty(self, distribution: Dict[DifficultyLevel, float]) -> DifficultyLevel:
        """根据概率分布选择难度"""
        rand = random.random()
        cumulative = 0
        
        for difficulty, prob in distribution.items():
            cumulative += prob
            if rand <= cumulative:
                return difficulty
        
        return DifficultyLevel.MEDIUM  # 默认
    
    def _select_question_type(self, distribution: Dict[QuestionType, float]) -> QuestionType:
        """根据概率分布选择题型"""
        rand = random.random()
        cumulative = 0
        
        for question_type, prob in distribution.items():
            cumulative += prob
            if rand <= cumulative:
                return question_type
        
        return QuestionType.FILL_IN_BLANK  # 默认
    
    def _generate_question(self, knowledge_point: str, difficulty: DifficultyLevel,
                          question_type: QuestionType, student_model: Dict) -> Optional[Question]:
        """生成具体题目"""
        
        templates = self.question_templates.get(knowledge_point, {}).get(question_type, [])
        if not templates:
            logger.warning(f"没有找到 {knowledge_point} - {question_type} 的题目模板")
            return None
        
        # 筛选符合难度的模板
        suitable_templates = [t for t in templates if t['difficulty'] == difficulty]
        if not suitable_templates:
            suitable_templates = templates  # 如果没有符合难度的，使用所有模板
        
        # 随机选择模板
        template_data = random.choice(suitable_templates)
        
        # 根据题型生成题目
        if question_type == QuestionType.FILL_IN_BLANK:
            return self._generate_fill_in_blank(template_data, knowledge_point, difficulty)
        elif question_type == QuestionType.ERROR_CORRECTION:
            return self._generate_error_correction(template_data, knowledge_point, difficulty)
        elif question_type == QuestionType.CODE_IMPLEMENTATION:
            return self._generate_code_implementation(template_data, knowledge_point, difficulty)
        elif question_type == QuestionType.CONCEPT_EXPLANATION:
            return self._generate_concept_explanation(template_data, knowledge_point, difficulty)
        
        return None
    
    def _generate_fill_in_blank(self, template_data: Dict, knowledge_point: str,
                               difficulty: DifficultyLevel) -> Question:
        """生成代码填空题"""
        
        question_id = f"fill_{knowledge_point}_{int(time.time())}"
        
        code_template = CodeTemplate(
            template=template_data['template'],
            blanks=template_data['blanks'],
            knowledge_points=[knowledge_point],
            difficulty=difficulty,
            hints=template_data.get('hints', [])
        )
        
        return Question(
            id=question_id,
            type=QuestionType.FILL_IN_BLANK,
            title=f"{knowledge_point} - 代码填空题",
            content=template_data['description'],
            knowledge_points=[knowledge_point],
            difficulty=difficulty,
            estimated_time=template_data.get('estimated_time', 5),
            template=code_template,
            max_score=100,
            scoring_criteria={
                'correctness': 70,
                'style': 20,
                'efficiency': 10
            }
        )
    
    def _generate_error_correction(self, template_data: Dict, knowledge_point: str,
                                  difficulty: DifficultyLevel) -> Question:
        """生成错误修正题"""
        
        question_id = f"error_{knowledge_point}_{int(time.time())}"
        
        buggy_code_obj = BuggyCode(
            buggy_code=template_data['buggy_code'],
            correct_code=template_data['correct_code'],
            error_type=template_data['error_type'],
            error_description=template_data['error_description'],
            knowledge_points=[knowledge_point],
            difficulty=difficulty
        )
        
        return Question(
            id=question_id,
            type=QuestionType.ERROR_CORRECTION,
            title=f"{knowledge_point} - 错误修正题",
            content=template_data['description'],
            knowledge_points=[knowledge_point],
            difficulty=difficulty,
            estimated_time=template_data.get('estimated_time', 8),
            buggy_code=buggy_code_obj,
            max_score=100,
            scoring_criteria={
                'error_identification': 50,
                'correction_accuracy': 40,
                'explanation_quality': 10
            }
        )
    
    def _generate_code_implementation(self, template_data: Dict, knowledge_point: str,
                                    difficulty: DifficultyLevel) -> Question:
        """生成功能实现题"""
        
        question_id = f"impl_{knowledge_point}_{int(time.time())}"
        
        implementation_task = ImplementationTask(
            description=template_data['description'],
            requirements=template_data['requirements'],
            starter_code=template_data.get('starter_code', ''),
            expected_output=template_data['expected_output'],
            knowledge_points=[knowledge_point],
            difficulty=difficulty,
            test_cases=template_data.get('test_cases', [])
        )
        
        return Question(
            id=question_id,
            type=QuestionType.CODE_IMPLEMENTATION,
            title=f"{knowledge_point} - 功能实现题",
            content=template_data['description'],
            knowledge_points=[knowledge_point],
            difficulty=difficulty,
            estimated_time=template_data.get('estimated_time', 15),
            implementation_task=implementation_task,
            max_score=100,
            scoring_criteria={
                'functionality': 60,
                'code_quality': 25,
                'edge_cases': 15
            }
        )
    
    def _generate_concept_explanation(self, template_data: Dict, knowledge_point: str,
                                    difficulty: DifficultyLevel) -> Question:
        """生成概念解释题"""
        
        question_id = f"concept_{knowledge_point}_{int(time.time())}"
        
        return Question(
            id=question_id,
            type=QuestionType.CONCEPT_EXPLANATION,
            title=f"{knowledge_point} - 概念验证",
            content=template_data['question'],
            knowledge_points=[knowledge_point],
            difficulty=difficulty,
            estimated_time=template_data.get('estimated_time', 3),
            max_score=100,
            scoring_criteria={
                'understanding': 60,
                'explanation_clarity': 25,
                'examples': 15
            }
        )
    
    def _load_question_templates(self) -> Dict[str, Dict[QuestionType, List[Dict]]]:
        """加载题目模板"""
        # 这里是题目模板数据，实际应该从配置文件或数据库加载
        return {
            'html_basics': {
                QuestionType.FILL_IN_BLANK: [
                    {
                        'template': '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="____">
    <title>____</title>
</head>
<body>
    <____>欢迎来到我的网站</____>
</body>
</html>''',
                        'blanks': ['UTF-8', '我的网站', 'h1', 'h1'],
                        'description': '完成这个基本的HTML页面结构',
                        'difficulty': DifficultyLevel.EASY,
                        'estimated_time': 3,
                        'hints': ['字符编码常用UTF-8', '标题标签用于重要内容']
                    }
                ],
                QuestionType.ERROR_CORRECTION: [
                    {
                        'buggy_code': '''<html>
<head>
    <title>测试页面</title>
<body>
    <h1>标题
    <p>这是一个段落</p>
</body>
</html>''',
                        'correct_code': '''<html>
<head>
    <title>测试页面</title>
</head>
<body>
    <h1>标题</h1>
    <p>这是一个段落</p>
</body>
</html>''',
                        'description': '修复这个HTML代码中的错误',
                        'error_type': 'structural',
                        'error_description': '缺少闭合标签',
                        'difficulty': DifficultyLevel.EASY,
                        'estimated_time': 5
                    }
                ],
                QuestionType.CODE_IMPLEMENTATION: [
                    {
                        'description': '创建一个简单的个人介绍页面',
                        'requirements': [
                            '包含页面标题',
                            '有一个主标题显示你的名字',
                            '有一个段落介绍你自己',
                            '包含一个无序列表显示你的兴趣爱好'
                        ],
                        'starter_code': '<!DOCTYPE html>\n<html>\n<!-- 在这里开始编写 -->\n</html>',
                        'expected_output': '一个包含个人信息的网页',
                        'difficulty': DifficultyLevel.MEDIUM,
                        'estimated_time': 10,
                        'test_cases': [
                            {'input': '', 'expected': '包含h1标签', 'type': 'structure'},
                            {'input': '', 'expected': '包含ul标签', 'type': 'structure'}
                        ]
                    }
                ],
                QuestionType.CONCEPT_EXPLANATION: [
                    {
                        'question': '请解释HTML中<div>和<span>元素的区别，并说明何时使用它们？',
                        'difficulty': DifficultyLevel.MEDIUM,
                        'estimated_time': 3
                    }
                ]
            },
            'css_basics': {
                QuestionType.FILL_IN_BLANK: [
                    {
                        'template': '''body {
    font-family: ____;
    margin: ____;
    padding: ____;
}

.container {
    width: ____;
    margin: 0 ____;
}''',
                        'blanks': ['Arial, sans-serif', '0', '20px', '80%', 'auto'],
                        'description': '完成这个基本的CSS样式',
                        'difficulty': DifficultyLevel.EASY,
                        'estimated_time': 4
                    }
                ]
            }
        }


class QuizEvaluator:
    """题目评估器"""
    
    def __init__(self):
        """初始化评估器"""
        logger.info("题目评估器已初始化")
    
    def evaluate_fill_in_blank(self, question: Question, student_answers: List[str]) -> Dict[str, Any]:
        """评估填空题"""
        if not question.template:
            return {'score': 0, 'feedback': '题目数据错误'}
        
        correct_answers = question.template.blanks
        
        if len(student_answers) != len(correct_answers):
            return {
                'score': 0,
                'feedback': f'答案数量不正确，应该有{len(correct_answers)}个空白'
            }
        
        correct_count = 0
        detailed_feedback = []
        
        for i, (student_answer, correct_answer) in enumerate(zip(student_answers, correct_answers)):
            if self._is_answer_correct(student_answer.strip(), correct_answer.strip()):
                correct_count += 1
                detailed_feedback.append(f'第{i+1}空: ✓ 正确')
            else:
                detailed_feedback.append(f'第{i+1}空: ✗ 错误，正确答案是 "{correct_answer}"')
        
        score = (correct_count / len(correct_answers)) * question.max_score
        
        return {
            'score': score,
            'correct_count': correct_count,
            'total_count': len(correct_answers),
            'accuracy': correct_count / len(correct_answers),
            'feedback': '\\n'.join(detailed_feedback),
            'suggestions': self._generate_suggestions(question, score)
        }
    
    def evaluate_error_correction(self, question: Question, corrected_code: str) -> Dict[str, Any]:
        """评估错误修正题"""
        if not question.buggy_code:
            return {'score': 0, 'feedback': '题目数据错误'}
        
        # 简化的评估逻辑，实际应该更复杂
        correct_code = question.buggy_code.correct_code.strip()
        student_code = corrected_code.strip()
        
        # 检查是否修复了关键错误
        similarity = self._calculate_code_similarity(student_code, correct_code)
        
        if similarity > 0.9:
            score = question.max_score
            feedback = "完全正确！成功修复了所有错误。"
        elif similarity > 0.7:
            score = question.max_score * 0.8
            feedback = "基本正确，但还有一些小问题。"
        elif similarity > 0.5:
            score = question.max_score * 0.6
            feedback = "部分正确，修复了主要错误。"
        else:
            score = question.max_score * 0.3
            feedback = "仍有重要错误未修复。"
        
        return {
            'score': score,
            'similarity': similarity,
            'feedback': feedback,
            'suggestions': self._generate_suggestions(question, score)
        }
    
    def evaluate_code_implementation(self, question: Question, student_code: str) -> Dict[str, Any]:
        """评估代码实现题"""
        if not question.implementation_task:
            return {'score': 0, 'feedback': '题目数据错误'}
        
        # 这里需要实际执行代码并检查结果
        # 为了演示，使用简化的评估逻辑
        
        requirements = question.implementation_task.requirements
        met_requirements = []
        
        # 检查每个要求是否满足（简化版）
        for requirement in requirements:
            if self._check_requirement(student_code, requirement):
                met_requirements.append(requirement)
        
        score = (len(met_requirements) / len(requirements)) * question.max_score
        
        feedback_lines = []
        for req in requirements:
            if req in met_requirements:
                feedback_lines.append(f"✓ {req}")
            else:
                feedback_lines.append(f"✗ {req}")
        
        return {
            'score': score,
            'met_requirements': len(met_requirements),
            'total_requirements': len(requirements),
            'feedback': '\\n'.join(feedback_lines),
            'suggestions': self._generate_suggestions(question, score)
        }
    
    def _is_answer_correct(self, student_answer: str, correct_answer: str) -> bool:
        """检查答案是否正确"""
        # 简化的答案比较，实际可能需要更复杂的逻辑
        return student_answer.lower() == correct_answer.lower()
    
    def _calculate_code_similarity(self, code1: str, code2: str) -> float:
        """计算代码相似度"""
        # 简化的相似度计算
        lines1 = set(line.strip() for line in code1.split('\\n') if line.strip())
        lines2 = set(line.strip() for line in code2.split('\\n') if line.strip())
        
        if not lines2:
            return 0.0
        
        intersection = len(lines1.intersection(lines2))
        union = len(lines1.union(lines2))
        
        return intersection / union if union > 0 else 0.0
    
    def _check_requirement(self, code: str, requirement: str) -> bool:
        """检查代码是否满足特定要求"""
        # 简化的要求检查逻辑
        code_lower = code.lower()
        
        if '标题' in requirement:
            return '<h1>' in code_lower or '<title>' in code_lower
        elif '段落' in requirement:
            return '<p>' in code_lower
        elif '列表' in requirement:
            return '<ul>' in code_lower or '<ol>' in code_lower or '<li>' in code_lower
        
        return False
    
    def _generate_suggestions(self, question: Question, score: float) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        if score < 60:
            suggestions.append("建议回顾相关知识点的基础概念")
            if question.template and question.template.hints:
                suggestions.extend([f"提示：{hint}" for hint in question.template.hints])
        elif score < 80:
            suggestions.append("基础掌握不错，可以尝试更复杂的练习")
        else:
            suggestions.append("掌握得很好！可以尝试挑战更高难度的题目")
        
        return suggestions


# 单例实例
_quiz_generator_instance = None
_quiz_evaluator_instance = None

def get_quiz_generator() -> QuizGenerator:
    """获取出题生成器的单例实例"""
    global _quiz_generator_instance
    if _quiz_generator_instance is None:
        _quiz_generator_instance = QuizGenerator()
    return _quiz_generator_instance

def get_quiz_evaluator() -> QuizEvaluator:
    """获取题目评估器的单例实例"""
    global _quiz_evaluator_instance
    if _quiz_evaluator_instance is None:
        _quiz_evaluator_instance = QuizEvaluator()
    return _quiz_evaluator_instance