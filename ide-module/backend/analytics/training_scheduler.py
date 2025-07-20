"""TrainingScheduler
统一处理数据持久化和增量训练调度的工具类。

实现功能：
1. 定时持久化：根据设定的 save_interval_secs 判断是否需要保存。
2. 增量训练触发：根据训练样本阈值 train_sample_threshold 判断是否需要触发训练。
3. 训练数据裁剪：限定缓存大小，避免内存无界增长。
"""
from __future__ import annotations

import time
from typing import Dict, List, Any


class TrainingScheduler:
    """调度器：决定何时保存模型、何时训练模型，并裁剪训练缓存"""

    def __init__(
        self,
        save_interval_secs: int = 60,
        train_sample_threshold: int = 20,
        max_buffer_size: int = 500,
    ) -> None:
        self.save_interval_secs = save_interval_secs
        self.train_sample_threshold = train_sample_threshold
        self.max_buffer_size = max_buffer_size
        self._last_save_ts = time.time()

    # ---------- 保存调度 ----------
    def should_save(self) -> bool:
        """判断是否达到保存间隔"""
        return (time.time() - self._last_save_ts) >= self.save_interval_secs

    def mark_saved(self) -> None:
        """更新最后保存时间戳"""
        self._last_save_ts = time.time()

    # ---------- 训练调度 ----------
    def should_train(self, sample_count: int) -> bool:
        """判断样本数是否达到训练阈值"""
        return sample_count >= self.train_sample_threshold

    # ---------- 缓存裁剪 ----------
    def trim_buffer(self, training_data: Dict[str, List[Any]]) -> None:
        """将 training_data 中的各数组裁剪到不超过 max_buffer_size"""
        current_size = len(training_data.get("features", []))
        if current_size <= self.max_buffer_size:
            return
        # 需要删除的数量
        excess = current_size - self.max_buffer_size
        for key, arr in training_data.items():
            # 移除最旧的 excess 条
            del arr[:excess]
