

# prompt_generator.py

# 这是一个新增的函数，核心是根据学习者状态调整反馈策略
def generate_adaptive_feedback(state, error_message, user_code):
    """
    根据学习者状态（困惑度、沮丧度）生成动态调整的反馈提示。

    Args:
        state (dict): 从 ml_state_predictor.py 的 evaluate_student_state 返回的状态字典。
        error_message (str): 代码执行返回的原始错误信息。
        user_code (str): 用户提交的代码。

    Returns:
        str: 一个为当前学习者状态量身定制的、完整的Prompt。
    """
    
    # 1. 根据状态选择不同的“开场白”和“鼓励语”
    if state.get('frustration', 'low') in ['high', 'very_high']:
        opening = "别灰心，这个问题确实有点棘手，很多开发者都会在这里卡住。我们换个角度看看，也许会有新发现。"
    elif state.get('confusion', 'low') == 'high':
        opening = "看起来我们遇到了一点挑战。没关系，这是学习过程中的正常部分。让我们把问题分解一下，一步步来解决。"
    elif state.get('confusion', 'low') == 'medium':
        opening = "很棒的尝试！我们离成功又近了一步。这里有个小细节可能需要我们注意一下。"
    else:
        opening = "继续保持！我们来看看如何改进。"

    # 2. 构建核心的指令部分
    core_instruction = f"""
    我是一名正在学习前端开发的学生。我尝试运行下面的代码片段时遇到了问题。

    我的代码是:
    ```html
    {user_code}
    ```

    系统返回的错误是:
    ```
    {error_message}
    ```
    """

    # 3. 根据状态调整“教学策略”
    if state.get('confusion', 'low') == 'high':
        # 高困惑度：要求更详细、更基础的解释
        strategy = "请你扮演一位非常有耐心的导师，用最简单易懂的比喻，帮我解释一下为什么会产生这个错误？请不要直接给我最终代码，而是引导我思考，并给我一个最小的、可以正确运行的例子作为参考。"
    else:
        # 默认策略：直接解释错误并给出修改建议
        strategy = "请帮我解释这个错误的原因，并指出我应该修改代码的哪个部分才能修复它。"

    # 4. 组合成最终的Prompt
    final_prompt = f"{opening}\n\n{core_instruction}\n\n{strategy}"
    return final_prompt


def generate_error_feedback_prompt(error_message, user_code, student_state):
    """为代码错误生成反馈提示（现在是动态的）"""
    # 直接调用新的适应性函数
    return generate_adaptive_feedback(student_state, error_message, user_code)

def generate_quiz_prompt(topic, student_state):
    """生成测验题的提示（也可以根据状态调整难度）"""
    if student_state.get('mastery', 'developing') == 'emerging': # 假设我们未来会评估掌握度
        difficulty = "一个与这个知识点相关的、稍微有些挑战性的问题"
    else:
        difficulty = "一个关于这个知识点的基础问题"
    
    return f"请为我生成一个关于 '{topic}' 的{difficulty}，来检验我的学习效果。请提供问题描述和需要我填写的代码框架。"

# --- 模拟使用 ---
if __name__ == '__main__':
    sample_code = "<div class='container'>...</div>"
    sample_error = "SyntaxError: Unexpected token '<'"

    print("--- 场景1: 初次犯错 (低困惑, 低沮丧) ---")
    state1 = {'confusion': 'low', 'frustration': 'low'}
    prompt1 = generate_error_feedback_prompt(sample_error, sample_code, state1)
    print(prompt1)

    print("\n" + "-"*50 + "\n")

    print("--- 场景2: 多次犯错 (高困惑) ---")
    state2 = {'confusion': 'high', 'frustration': 'low'}
    prompt2 = generate_error_feedback_prompt(sample_error, sample_code, state2)
    print(prompt2)

    print("\n" + "-"*50 + "\n")

    print("--- 场景3: 连续快速犯错 (高沮丧) ---")
    state3 = {'confusion': 'high', 'frustration': 'high'}
    prompt3 = generate_error_feedback_prompt(sample_error, sample_code, state3)
    print(prompt3)

