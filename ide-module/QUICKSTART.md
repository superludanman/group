# 智能学习系统 - 快速开始指南

## 🎯 30秒体验智能学习

### 1. 启动系统
```bash
# 克隆项目后进入后端目录
cd ide-module/backend

# 安装依赖
pip install -r requirements.txt
pip install scikit-learn matplotlib seaborn numpy pandas

# 启动后端（包含智能分析API）
python app.py &

# 启动前端
cd ../frontend && python -m http.server 3000
```

### 2. 打开学习界面
- 浏览器访问: http://localhost:3000
- 智能助手自动激活，开始行为分析

### 3. 体验智能功能

**代码编辑追踪**:
```html
<!-- 在HTML编辑器中输入 -->
<h1>Hello AI Learning!</h1>
```
→ 系统自动记录编辑行为，分析学习状态

**查看智能状态**:
- 左侧"🧠智能助手"面板显示实时状态
- 认知负荷、专注度、知识水平动态更新

**自适应测试**:
- 点击"生成测试题" → 获得个性化题目
- 完成后获得智能反馈和建议

### 4. API测试
```bash
# 检查智能功能状态
curl http://localhost:8080/api/v2/info

# 获取学习者模型
curl http://localhost:8080/api/v2/student-model/main_student
```

## 🔍 核心特色一览

- **🧠 实时状态分析**: 认知负荷、困惑程度、专注度
- **📊 贝叶斯知识追踪**: BKT算法精确跟踪知识掌握
- **🤖 机器学习预测**: Random Forest模型状态推理
- **📝 自适应出题**: 基于学习状态的个性化测试
- **📈 学习进度可视化**: 详细的进度分析和建议

## 📚 详细文档

完整使用教程请查看: [README.md](README.md)

---
**快速上手版本** | v2.0 智能增强 | 适用于ACM CHI论文研究