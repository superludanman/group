import os
import sys
import torch
from pathlib import Path

# 设置环境变量
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["PYTHONWARNINGS"] = "ignore"

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

# 设置日志级别
from transformers.utils import logging
logging.set_verbosity_error()

# 获取当前文件所在目录的绝对路径
current_dir = Path(__file__).parent.absolute()

# 设置模型路径 - 使用相对路径
model_dir = current_dir / "best_model" / "bert-base-uncased"

print(f"正在从 {model_dir} 加载模型...")

# 加载模型和tokenizer
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    
    # 1. 首先尝试加载tokenizer
    print("正在加载tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    print("tokenizer加载成功！")
    
    # 2. 检查是否有可用的GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 3. 加载模型
    print("正在加载模型...")
    model = AutoModelForSequenceClassification.from_pretrained(
        model_dir,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )
    
    # 4. 将模型移到适当的设备
    model = model.to(device)
    
    model.eval()
    print("模型加载成功！")
    
except Exception as e:
    print(f"加载模型时出错: {str(e)}", file=sys.stderr)
    print("\n可能的原因：")
    print("1. 模型文件不完整或已损坏")
    print("2. 内存不足，请关闭其他程序释放内存")
    print("3. 模型路径不正确")
    print("\n请检查以上问题后重试。")
    sys.exit(1)

# 情感标签映射
label_map = {0: '负面', 1: '中性', 2: '正面'}

async def EmotionModel(text):
    """
    情感分析函数
    
    参数:
        text (str): 需要分析的文本
        
    返回:
        dict: 包含情感分析结果的字典
            {
                'emotion': str,  # 情感标签
                'state': str,    # 状态: 'success' 或 'error'
                'message': str   # 详细信息
            }
    """
    try:
        if not text or not isinstance(text, str):
            return {
                'emotion': '未知',
                'state': 'error',
                'message': '输入文本不能为空或非字符串'
            }
            
        # 文本编码
        encoding = tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=128,
            truncation=True,
            padding='max_length',
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        # 准备输入
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        # 模型推理
        with torch.no_grad():
            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            pred = torch.argmax(logits, dim=1).item()
            
        # 获取情感标签
        emotion = label_map.get(pred, "未知")
        
        return {
            'emotion': emotion,
            'state': 'success',
            'message': f'情感分析结果: {emotion}'
        }
        
    except Exception as e:
        error_msg = f'情感分析失败: {str(e)}'
        print(error_msg, file=sys.stderr)
        return {
            'emotion': '未知',
            'state': 'error',
            'message': error_msg
        }

# 测试代码
if __name__ == "__main__":
    test_texts = [
        "I love this product!",
        "This is terrible!",
        "I feel okay about this.",
        ""  # 测试空字符串
    ]
    
    for text in test_texts:
        print(f"\n分析文本: {text}")
        result = EmotionModel(text)
        print(f"结果: {result}")