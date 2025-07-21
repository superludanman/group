
import time
from collections import deque

# 这是一个模拟的日志记录器，实际应用中应从您的日志系统中获取数据
# 每一条日志是一个字典，包含时间戳、事件类型、用户ID、任务ID和相关数据
# 例如:
# {'timestamp': time.time(), 'event': 'code_submission', 'user_id': 'user1', 'task_id': 'task1', 'data': {'success': False, 'error': 'SyntaxError'}}
# {'timestamp': time.time(), 'event': 'request_hint', 'user_id': 'user1', 'task_id': 'task1', 'data': {}}
BEHAVIOR_LOGS = deque() 

def log_behavior(event, user_id, task_id, data):
    """向全局日志中添加一条新的行为记录"""
    log_entry = {
        'timestamp': time.time(),
        'event': event,
        'user_id': user_id,
        'task_id': task_id,
        'data': data
    }
    BEHAVIOR_LOGS.append(log_entry)
    # 为了防止内存无限增长，可以只保留最近一段时间的日志
    # 此处保留最近1000条记录
    if len(BEHAVIOR_LOGS) > 1000:
        BEHAVIOR_LOGS.popleft()

def evaluate_student_state(user_id, task_id, recent_seconds=300):
    """
    基于启发式规则评估学习者的状态。
    这取代了需要大量数据训练的机器学习模型。
    
    Args:
        user_id (str): 要评估的用户的ID。
        task_id (str): 当前任务的ID。
        recent_seconds (int): 分析最近多少秒的行为数据。

    Returns:
        dict: 包含学习者状态标签的字典。
              例如: {'confusion': 'high', 'frustration': 'low'}
    """
    state = {'confusion': 'low', 'frustration': 'low'}
    now = time.time()
    
    # 1. 筛选出与当前用户、任务和时间窗口相关的日志
    relevant_logs = [
        log for log in BEHAVIOR_LOGS 
        if log['user_id'] == user_id 
        and log['task_id'] == task_id 
        and (now - log['timestamp']) <= recent_seconds
    ]
    
    if not relevant_logs:
        return state

    # 2. 提取提交代码的日志
    submission_logs = sorted(
        [log for log in relevant_logs if log['event'] == 'code_submission'],
        key=lambda x: x['timestamp']
    )

    # 3. 应用启发式规则
    
    # 规则 A: 检测“困惑” (Confusion)
    # 如果在时间窗口内，错误提交次数达到一定阈值，且没有成功过
    error_submissions = [s for s in submission_logs if not s['data']['success']]
    successful_submissions = [s for s in submission_logs if s['data']['success']]
    
    if len(error_submissions) >= 3 and not successful_submissions:
        state['confusion'] = 'high'
    elif len(error_submissions) >= 1 and not successful_submissions:
        state['confusion'] = 'medium'

    # 规则 B: 检测“沮丧” (Frustration)
    # 如果在很短的时间内（例如60秒）连续出现多次错误提交
    if len(error_submissions) >= 2:
        # 检查最近两次错误提交的时间差
        last_error_time = error_submissions[-1]['timestamp']
        second_last_error_time = error_submissions[-2]['timestamp']
        if (last_error_time - second_last_error_time) < 60: # 60秒内连续犯错
            state['frustration'] = 'high'
            # 如果短时间内犯错次数更多，可能更沮丧
            if len(error_submissions) >= 4 and (last_error_time - error_submissions[-4]['timestamp']) < 120:
                 state['frustration'] = 'very_high'

    return state

# --- 模拟使用 ---
if __name__ == '__main__':
    # 模拟一个学习过程
    USER = 'student_A'
    TASK = 'flexbox_intro'

    # 初始状态
    print(f"Initial state: {evaluate_student_state(USER, TASK)}")

    # 第一次尝试，错了
    log_behavior('code_submission', USER, TASK, {'success': False, 'error': 'SyntaxError'})
    time.sleep(10)
    print(f"State after 1st error: {evaluate_student_state(USER, TASK)}")

    # 第二次尝试，又错了
    log_behavior('code_submission', USER, TASK, {'success': False, 'error': 'TypeError'})
    time.sleep(10)
    print(f"State after 2nd error: {evaluate_student_state(USER, TASK)}")

    # 第三次尝试，还是错了 (触发高困惑度)
    log_behavior('code_submission', USER, TASK, {'success': False, 'error': 'ValueError'})
    print(f"State after 3rd error (high confusion): {evaluate_student_state(USER, TASK)}")
    
    # 在高困惑度下，短时间内再次提交错误 (触发高沮丧度)
    time.sleep(5)
    log_behavior('code_submission', USER, TASK, {'success': False, 'error': 'NameError'})
    print(f"State after 4th rapid error (high frustration): {evaluate_student_state(USER, TASK)}")

