# 情绪识别模型使用说明

## 依赖要求
- Python 3.6+
- torch>=2.7.1
- transformers>=4.53.3

## 模型文件结构
```
best_model/
├── distilbert-base-uncased-emotion/  # 模型目录
│   ├── config.json
│   ├── model.safetensors             # 合并后的模型文件（由脚本生成）
│   ├── model_chunks/                 # 分割后的模型文件（用于版本控制）
│   │   ├── model.safetensors.part001
│   │   ├── model.safetensors.part002
│   │   └── ...
│   ├── preprocessor_config.json
│   └── tokenizer_config.json
├── merge_model.py    # 合并脚本
└── split_model.py    # 分割脚本
```

## 首次使用说明

### 1. 合并模型文件
在首次使用前，需要将分割的模型文件合并回原始文件：

```bash
# 在 best_model 目录下执行
cd backend/app/core/best_model
python merge_model.py distilbert-base-uncased-emotion/model_chunks
```

### 2. 验证模型
合并完成后，可以运行以下命令验证模型是否正常工作：

```bash
python -c "from transformers import pipeline; classifier = pipeline('text-classification', model='distilbert-base-uncased-emotion', device=-1); print(classifier('I love this!'))"
```

## 开发说明

### 重新分割模型文件
如果需要更新模型文件，请按以下步骤操作：

1. 将新模型文件保存为 `distilbert-base-uncased-emotion/model.safetensors`
2. 删除旧的 `model_chunks` 目录
3. 运行分割脚本：
   ```bash
   cd backend/app/core/best_model
   python split_model.py distilbert-base-uncased-emotion/model.safetensors
   ```
4. 提交更新后的 `model_chunks` 目录到版本控制

## API 使用

### 设置模型路径
```python
from pathlib import Path

# 设置模型路径 - 使用相对路径
current_dir = Path(__file__).parent
model_dir = current_dir / "distilbert-base-uncased-emotion"
```

### API 端点
```python
@api_router.post("/emotion")
async def emotion(request: Request):
    """
    情绪分析API端点
    """
    if not EMOTION_MODEL_AVAILABLE:
        return {
            "emotion": "未知",
            "state": "error",
            "message": "情绪识别模型不可用，请检查模型文件和依赖"
        }
    response = await request.json()
    text = response["text"]
    return await EmotionModel(text)
```

### 输入格式
```json
{
    "text": "需要分析情绪的文本内容"
}
```

### 输出格式
```json
{
    "emotion": "情绪标签",
    "state": "success/error",
    "message": "附加信息"
}
```

## 注意事项

1. 确保 `.gitignore` 中已添加 `model.safetensors` 文件
2. 合并后的模型文件较大，建议在 `.gitignore` 中忽略
3. 分片文件已按顺序命名，请勿手动修改文件名


