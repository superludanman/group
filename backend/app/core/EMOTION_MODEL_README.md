# 情绪识别模型使用说明

## 依赖要求
- torch>=2.7.1
- transformers>=4.53.3

## 模型文件要求
本模块需要BERT模型文件才能正常工作。有两种方式可以使用模型：

### 方式一：下载模型文件（推荐用于生产环境）
1. 下载BERT模型文件到目录：`backend/app/core/best_model/bert-base-uncased/`
2. 确保目录结构如下：
   ```
   backend/app/core/best_model/bert-base-uncased/
   ├── config.json
   ├── pytorch_model.bin
   ├── tokenizer.json
   ├── tokenizer_config.json
   └── vocab.txt
   ```

### 方式二：使用在线模型（推荐用于开发环境）
修改`EmotionModel.py`文件中的以下代码：
```python
# 原代码
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModelForSequenceClassification.from_pretrained(model_dir, ...)

# 修改为
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", ...)
```

注意：使用在线模型会在首次运行时自动下载模型文件，需要网络连接。

## 错误处理
如果模型加载失败，程序会输出错误信息并退出。常见原因：
1. 模型文件不完整或已损坏
2. 内存不足，请关闭其他程序释放内存
3. 模型路径不正确