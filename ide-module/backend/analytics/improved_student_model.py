"""
行为数据采集和日志系统

这个模块负责记录所有用户交互行为，为学习者模型提供丰富的数据源。
采集的数据包括编辑行为、停顿模式、错误恢复、求助行为等。
"""

import logging
import json
import time
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BehaviorLogger")


class EventType(str, Enum):
    """事件类型枚举"""

    # 编辑相关
    CODE_EDIT = "code_edit"  # 代码编辑
    CODE_DELETE = "code_delete"  # 代码删除
    CODE_PASTE = "code_paste"  # 代码粘贴

    # 思考相关
    PAUSE_START = "pause_start"  # 开始停顿
    PAUSE_END = "pause_end"  # 结束停顿
    CURSOR_MOVE = "cursor_move"  # 光标移动

    # 错误相关
    ERROR_OCCUR = "error_occur"  # 错误发生
    ERROR_FIXED = "error_fixed"  # 错误修复

    # 交互相关
    HELP_REQUEST = "help_request"  # 请求帮助
    AI_CHAT = "ai_chat"  # AI对话
    CODE_EXECUTE = "code_execute"  # 代码执行

    # 任务相关
    TASK_START = "task_start"  # 任务开始
    TASK_COMPLETE = "task_complete"  # 任务完成
    TASK_ABANDON = "task_abandon"  # 任务放弃


@dataclass
class BehaviorEvent:
    """行为事件数据结构"""

    timestamp: float
    student_id: str
    session_id: str
    event_type: EventType
    duration: Optional[float] = None  # 事件持续时间（秒）

    # 代码上下文
    code_before: Optional[str] = None
    code_after: Optional[str] = None
    cursor_position: Optional[Dict[str, int]] = None  # {line: int, column: int}

    # 事件特定数据
    edit_length: Optional[int] = None  # 编辑字符数
    error_type: Optional[str] = None  # 错误类型
    help_query: Optional[str] = None  # 求助内容
    ai_response: Optional[str] = None  # AI回复

    # 环境信息
    current_task: Optional[str] = None  # 当前任务
    knowledge_points: Optional[List[str]] = None  # 相关知识点

    # 元数据
    metadata: Optional[Dict[str, Any]] = None


class BehaviorLogger:
    """行为数据采集器"""

    def __init__(self, log_dir: str = "logs/behavior"):
        """初始化行为日志器"""
        self.log_dir = log_dir
        self.ensure_log_directory()

        # 会话数据缓存
        self.session_cache: Dict[str, List[BehaviorEvent]] = {}

        # 实时计算的统计数据
        self.session_stats: Dict[str, Dict] = {}

        logger.info(f"行为日志器初始化完成，日志目录：{self.log_dir}")

    def ensure_log_directory(self):
        """确保日志目录存在"""
        os.makedirs(self.log_dir, exist_ok=True)

    def log_event(self, event: BehaviorEvent) -> None:
        """记录单个行为事件"""
        try:
            # 添加到会话缓存
            if event.session_id not in self.session_cache:
                self.session_cache[event.session_id] = []
            self.session_cache[event.session_id].append(event)

            # 更新实时统计
            self._update_session_stats(event)

            # 持久化到文件
            self._persist_event(event)

            logger.debug(f"记录行为事件：{event.event_type} - 学生：{event.student_id}")

        except Exception as e:
            logger.error(f"记录行为事件失败：{e}")

    def log_code_edit(
        self,
        student_id: str,
        session_id: str,
        code_before: str,
        code_after: str,
        cursor_pos: Dict[str, int],
        current_task: str = None,
    ) -> None:
        """记录代码编辑事件"""

        # 计算编辑特征
        edit_length = abs(len(code_after) - len(code_before))

        event = BehaviorEvent(
            timestamp=time.time(),
            student_id=student_id,
            session_id=session_id,
            event_type=EventType.CODE_EDIT,
            code_before=code_before,
            code_after=code_after,
            cursor_position=cursor_pos,
            edit_length=edit_length,
            current_task=current_task,
        )

        self.log_event(event)

    def log_pause(
        self,
        student_id: str,
        session_id: str,
        duration: float,
        cursor_pos: Dict[str, int],
    ) -> None:
        """记录思考停顿事件"""

        event = BehaviorEvent(
            timestamp=time.time(),
            student_id=student_id,
            session_id=session_id,
            event_type=EventType.PAUSE_END,
            duration=duration,
            cursor_position=cursor_pos,
            metadata={"pause_category": self._categorize_pause(duration)},
        )

        self.log_event(event)

    def log_error_event(
        self,
        student_id: str,
        session_id: str,
        error_type: str,
        error_message: str,
        code_context: str,
    ) -> None:
        """记录错误事件"""

        event = BehaviorEvent(
            timestamp=time.time(),
            student_id=student_id,
            session_id=session_id,
            event_type=EventType.ERROR_OCCUR,
            error_type=error_type,
            code_before=code_context,
            metadata={
                "error_message": error_message,
                "error_severity": self._categorize_error_severity(error_type),
            },
        )

        self.log_event(event)

    def log_help_request(
        self, student_id: str, session_id: str, help_query: str, ai_response: str = None
    ) -> None:
        """记录求助事件"""

        event = BehaviorEvent(
            timestamp=time.time(),
            student_id=student_id,
            session_id=session_id,
            event_type=EventType.HELP_REQUEST,
            help_query=help_query,
            ai_response=ai_response,
            metadata={
                "query_length": len(help_query),
                "query_complexity": self._analyze_query_complexity(help_query),
            },
        )

        self.log_event(event)

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """获取会话行为摘要"""
        if session_id not in self.session_cache:
            return {}

        events = self.session_cache[session_id]
        if not events:
            return {}

        # 计算会话统计
        session_duration = events[-1].timestamp - events[0].timestamp

        # 编辑行为统计
        edit_events = [e for e in events if e.event_type == EventType.CODE_EDIT]
        total_edits = len(edit_events)
        total_edit_chars = sum(e.edit_length or 0 for e in edit_events)

        # 停顿行为统计
        pause_events = [e for e in events if e.event_type == EventType.PAUSE_END]
        avg_pause_duration = sum(e.duration or 0 for e in pause_events) / max(
            len(pause_events), 1
        )

        # 错误行为统计
        error_events = [e for e in events if e.event_type == EventType.ERROR_OCCUR]
        error_rate = len(error_events) / max(total_edits, 1)

        # 求助行为统计
        help_events = [e for e in events if e.event_type == EventType.HELP_REQUEST]
        help_frequency = len(help_events) / max(
            session_duration / 60, 1
        )  # 每分钟求助次数

        return {
            "session_duration": session_duration,
            "total_events": len(events),
            "edit_frequency": total_edits
            / max(session_duration / 60, 1),  # 每分钟编辑次数
            "edit_chars_per_minute": total_edit_chars / max(session_duration / 60, 1),
            "avg_pause_duration": avg_pause_duration,
            "error_rate": error_rate,
            "help_frequency": help_frequency,
            "event_type_distribution": self._get_event_type_distribution(events),
        }

    def extract_learning_signals(
        self, student_id: str, time_window: float = 300
    ) -> Dict[str, Any]:
        """提取最近时间窗口内的学习信号"""
        current_time = time.time()
        recent_events = []

        # 收集所有会话的最近事件
        for _, events in self.session_cache.items():
            for event in events:
                if (
                    event.student_id == student_id
                    and current_time - event.timestamp <= time_window
                ):
                    recent_events.append(event)

        if not recent_events:
            return {}

        # 分析学习信号
        return {
            "cognitive_load_signals": self._extract_cognitive_load_signals(
                recent_events
            ),
            "confusion_signals": self._extract_confusion_signals(recent_events),
            "engagement_signals": self._extract_engagement_signals(recent_events),
            "learning_preference_signals": self._extract_preference_signals(
                recent_events
            ),
        }

    def _update_session_stats(self, event: BehaviorEvent) -> None:
        """更新会话实时统计"""
        session_id = event.session_id

        if session_id not in self.session_stats:
            self.session_stats[session_id] = {
                "start_time": event.timestamp,
                "last_activity": event.timestamp,
                "event_counts": {},
                "total_edits": 0,
                "total_errors": 0,
                "total_help_requests": 0,
            }

        stats = self.session_stats[session_id]
        stats["last_activity"] = event.timestamp

        # 更新事件计数
        event_type = event.event_type.value
        stats["event_counts"][event_type] = stats["event_counts"].get(event_type, 0) + 1

        # 更新特定统计
        if event.event_type == EventType.CODE_EDIT:
            stats["total_edits"] += 1
        elif event.event_type == EventType.ERROR_OCCUR:
            stats["total_errors"] += 1
        elif event.event_type == EventType.HELP_REQUEST:
            stats["total_help_requests"] += 1

    def _persist_event(self, event: BehaviorEvent) -> None:
        """持久化事件到文件"""
        try:
            # 按日期组织日志文件
            date_str = datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"behavior_{date_str}.jsonl")

            # 转换为JSON并追加到文件
            event_json = json.dumps(asdict(event), ensure_ascii=False)

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(event_json + "\n")

        except Exception as e:
            logger.error(f"持久化事件失败：{e}")

    def _categorize_pause(self, duration: float) -> str:
        """分类停顿类型"""
        if duration < 2:
            return "brief"  # 短暂停顿
        elif duration < 10:
            return "thinking"  # 思考停顿
        elif duration < 30:
            return "confused"  # 困惑停顿
        else:
            return "distracted"  # 分心停顿

    def _categorize_error_severity(self, error_type: str) -> str:
        """分类错误严重程度"""
        syntax_errors = ["SyntaxError", "ReferenceError"]
        logic_errors = ["TypeError", "AttributeError"]

        if error_type in syntax_errors:
            return "syntax"
        elif error_type in logic_errors:
            return "logic"
        else:
            return "other"

    def _analyze_query_complexity(self, query: str) -> str:
        """分析求助查询的复杂度"""
        word_count = len(query.split())

        if word_count < 5:
            return "simple"
        elif word_count < 15:
            return "moderate"
        else:
            return "complex"

    def _get_event_type_distribution(
        self, events: List[BehaviorEvent]
    ) -> Dict[str, float]:
        """获取事件类型分布"""
        total = len(events)
        if total == 0:
            return {}

        distribution = {}
        for event in events:
            event_type = event.event_type.value
            distribution[event_type] = distribution.get(event_type, 0) + 1

        # 转换为比例
        for event_type in distribution:
            distribution[event_type] /= total

        return distribution

    def _extract_cognitive_load_signals(
        self, events: List[BehaviorEvent]
    ) -> Dict[str, float]:
        """提取认知负荷信号"""
        edit_events = [e for e in events if e.event_type == EventType.CODE_EDIT]
        pause_events = [e for e in events if e.event_type == EventType.PAUSE_END]
        error_events = [e for e in events if e.event_type == EventType.ERROR_OCCUR]

        if not edit_events:
            return {}

        # 编辑频率（高频可能表示焦虑或试错）
        edit_frequency = len(edit_events) / max(
            (events[-1].timestamp - events[0].timestamp) / 60, 1
        )

        # 平均停顿时长（长停顿可能表示困难）
        avg_pause = sum(e.duration or 0 for e in pause_events) / max(
            len(pause_events), 1
        )

        # 错误率
        error_rate = len(error_events) / len(edit_events)

        return {
            "edit_frequency": edit_frequency,
            "avg_pause_duration": avg_pause,
            "error_rate": error_rate,
            "rapid_editing": 1.0 if edit_frequency > 10 else 0.0,  # 每分钟超过10次编辑
            "long_pauses": 1.0 if avg_pause > 15 else 0.0,  # 平均停顿超过15秒
        }

    def _extract_confusion_signals(
        self, events: List[BehaviorEvent]
    ) -> Dict[str, float]:
        """提取困惑信号"""
        edit_events = [e for e in events if e.event_type == EventType.CODE_EDIT]
        help_events = [e for e in events if e.event_type == EventType.HELP_REQUEST]
        error_events = [e for e in events if e.event_type == EventType.ERROR_OCCUR]

        if not edit_events:
            return {}

        # 求助频率激增
        session_duration = (events[-1].timestamp - events[0].timestamp) / 60
        help_frequency = len(help_events) / max(session_duration, 1)

        # 重复性错误（简化版：错误事件密集程度）
        error_clustering = 0.0
        if len(error_events) > 1:
            error_intervals = []
            for i in range(1, len(error_events)):
                interval = error_events[i].timestamp - error_events[i - 1].timestamp
                error_intervals.append(interval)
            avg_error_interval = sum(error_intervals) / len(error_intervals)
            error_clustering = (
                1.0 if avg_error_interval < 30 else 0.0
            )  # 错误间隔小于30秒

        # 编辑无规律性（简化版：编辑长度方差）
        edit_lengths = [e.edit_length or 0 for e in edit_events]
        edit_variance = 0.0
        if len(edit_lengths) > 1:
            avg_length = sum(edit_lengths) / len(edit_lengths)
            variance = sum((x - avg_length) ** 2 for x in edit_lengths) / len(
                edit_lengths
            )
            edit_variance = min(variance / 100, 1.0)  # 归一化

        return {
            "help_frequency": help_frequency,
            "error_clustering": error_clustering,
            "edit_randomness": edit_variance,
            "high_help_seeking": 1.0
            if help_frequency > 2
            else 0.0,  # 每分钟超过2次求助
        }

    def _extract_engagement_signals(
        self, events: List[BehaviorEvent]
    ) -> Dict[str, float]:
        """提取参与度信号"""
        if not events:
            return {}

        session_duration = events[-1].timestamp - events[0].timestamp
        active_events = [
            e
            for e in events
            if e.event_type
            in [EventType.CODE_EDIT, EventType.CODE_EXECUTE, EventType.AI_CHAT]
        ]

        # 活跃时间比例
        activity_ratio = len(active_events) / max(len(events), 1)

        # 任务专注度（简化版：活跃事件密度）
        activity_density = len(active_events) / max(session_duration / 60, 1)

        return {
            "activity_ratio": activity_ratio,
            "activity_density": activity_density,
            "sustained_engagement": 1.0
            if activity_density > 5
            else 0.0,  # 每分钟超过5个活跃事件
        }

    def _extract_preference_signals(
        self, events: List[BehaviorEvent]
    ) -> Dict[str, float]:
        """提取学习偏好信号"""
        help_events = [e for e in events if e.event_type == EventType.HELP_REQUEST]

        if not help_events:
            return {}

        # 分析求助内容偏好（简化版）
        code_related_queries = 0
        concept_related_queries = 0

        for event in help_events:
            query = event.help_query or ""
            if any(
                keyword in query.lower()
                for keyword in ["代码", "语法", "实现", "怎么写"]
            ):
                code_related_queries += 1
            elif any(
                keyword in query.lower()
                for keyword in ["什么是", "为什么", "概念", "理解"]
            ):
                concept_related_queries += 1

        total_queries = len(help_events)

        return {
            "prefers_code_examples": code_related_queries / max(total_queries, 1),
            "prefers_explanations": concept_related_queries / max(total_queries, 1),
        }


# 单例实例
_behavior_logger_instance = None


def get_behavior_logger() -> BehaviorLogger:
    """获取行为日志器的单例实例"""
    global _behavior_logger_instance
    if _behavior_logger_instance is None:
        _behavior_logger_instance = BehaviorLogger()
    return _behavior_logger_instance
