

# api_integration.py
# 这个文件是整个动态反馈系统的核心调度器。

import time

# 从我们的分析模块中导入核心功能
# 注意：为了让这个导入能够工作，analytics文件夹需要是一个Python包（包含一个__init__.py文件）
# 并且该模块需要被添加到Python的搜索路径中。
from analytics.ml_state_predictor import evaluate_student_state, log_behavior
from prompt_generator import generate_error_feedback_prompt

def get_adaptive_ai_feedback(user_id, task_id, user_code, error_message):
    """
    获取一个根据学习者当前状态动态调整的AI反馈提示。
    这是提供给主应用(app.py)调用的主接口。

    Args:
        user_id (str): 用户的唯一标识符。
        task_id (str): 当前任务的唯一标识符。
        user_code (str): 用户提交的完整代码。
        error_message (str): 从沙箱环境返回的原始错误信息。

    Returns:
        str: 一个完整的、可以直接发送给大语言模型(LLM)的自适应Prompt。
    """
    # 1. 记录这次提交行为，这是让状态评估器工作的基础
    # 注意：这里的success是硬编码为False，因为这个函数本身就是处理错误反馈的
    log_behavior(
        event='code_submission',
        user_id=user_id,
        task_id=task_id,
        data={'success': False, 'error': error_message, 'code': user_code}
    )

    # 2. 调用状态评估器，获取对学习者当前状态的判断
    student_state = evaluate_student_state(user_id, task_id)
    print(f"[Integration Log] Evaluated state for {user_id}: {student_state}") # 打印日志，方便调试

    # 3. 调用提示生成器，传入状态和错误信息，获取动态生成的Prompt
    adaptive_prompt = generate_error_feedback_prompt(
        error_message=error_message,
        user_code=user_code,
        student_state=student_state
    )

    # 4. 返回最终的Prompt
    return adaptive_prompt

# --- 模拟一个完整的用户交互场景 ---
if __name__ == '__main__':
    USER = 'student_B'
    TASK = 'css_grid_challenge'
    SAMPLE_CODE = "<div class=\"grid-container\">\n  <div class=\"item1\">1</div>\n</div>"
    SAMPLE_ERROR = "Error: Grid item is not aligning as expected."

    print("--- 模拟场景开始 ---")
    print(f"用户 {USER} 开始挑战任务 {TASK}\n")

    # 第一次提交，失败
    print("--- 1. 第一次提交 (失败) ---")
    prompt1 = get_adaptive_ai_feedback(USER, TASK, SAMPLE_CODE, SAMPLE_ERROR)
    print("\n[Generated Prompt 1]:")
    print(prompt1)
    print("\n" + "="*60 + "\n")
    time.sleep(2) # 模拟思考时间

    # 第二次提交，再次失败
    print("--- 2. 第二次提交 (失败) ---")
    prompt2 = get_adaptive_ai_feedback(USER, TASK, SAMPLE_CODE, "Error: Still not working.")
    print("\n[Generated Prompt 2]:")
    print(prompt2)
    print("\n" + "="*60 + "\n")
    time.sleep(2)

    # 第三次提交，仍然失败 -> 触发“高困惑度”
    print("--- 3. 第三次提交 (失败) -> 触发高困惑度 ---")
    prompt3 = get_adaptive_ai_feedback(USER, TASK, SAMPLE_CODE, "Error: I am lost.")
    print("\n[Generated Prompt 3]:")
    print(prompt3)
    print("\n" + "="*60 + "\n")
    time.sleep(1) # 模拟急躁下的快速提交

    # 第四次提交，快速失败 -> 触发“高沮丧度”
    print("--- 4. 第四次提交 (快速失败) -> 触发高沮丧度 ---")
    prompt4 = get_adaptive_ai_feedback(USER, TASK, SAMPLE_CODE, "Error: Why!??")
    print("\n[Generated Prompt 4]:")
    print(prompt4)
    print("\n--- 模拟场景结束 ---")
