# 智能学习系统 - IDE模块

这是一个基于"人-LLM融合"理论的智能HTML学习系统，专为ACM CHI会议论文研究设计。系统通过实时行为分析、贝叶斯知识追踪和机器学习状态预测，为学习者提供个性化的编程教学体验。

## 🎯 核心创新

- **人-AI融合教学**: 基于控制理论的动态学习者建模
- **实时行为追踪**: 监控代码编辑、暂停、错误等学习行为  
- **贝叶斯知识追踪**: 使用MLE参数估计的真实BKT算法
- **机器学习状态预测**: Random Forest模型预测认知负荷和困惑程度
- **自适应出题系统**: 根据学习状态生成个性化测试题
- **个性化学习建议**: 基于多维度数据提供智能指导
- **学术研究支持**: 完整的离线评估系统，支持教育技术研究

## 🚀 系统特色

### v2.0 增强功能
- **单用户深度优化**: 专门为单学习者场景设计的高精度模型
- **多维度状态推理**: 实时评估认知负荷、困惑程度和专注度
- **智能UI适配**: 根据学习状态动态调整界面和内容难度
- **离线评估系统**: 为学术论文提供模型准确性验证
- **RESTful API**: 完整的v2 API支持二次开发和研究

### 传统功能
- Monaco编辑器集成（与VS Code相同的编辑器引擎）
- 多标签页编辑（HTML、CSS、JavaScript、预览）
- 实时代码预览
- 测试要求和测试结果显示
- AI辅助修改建议
- 响应式界面设计

## 目录结构

```
ide-module/
├── backend/                # 后端服务
│   ├── analytics/          # 🆕 智能分析模块
│   │   ├── behavior_logger.py    # 行为数据记录
│   │   ├── bayesian_kt.py        # 贝叶斯知识追踪
│   │   ├── ml_state_predictor.py # 机器学习状态预测
│   │   ├── quiz_generator.py     # 自适应出题系统
│   │   ├── single_user_model.py  # 单用户学习模型
│   │   ├── api_integration.py    # API集成服务
│   │   └── offline_evaluator.py  # 离线评估系统
│   ├── Dockerfile          # 后端服务容器
│   ├── docker_manager.py   # Docker容器管理
│   ├── code_executor.py    # 代码执行服务
│   ├── app.py              # FastAPI应用（含v2 API）
│   ├── requirements.txt    # 依赖项
│   ├── start.sh            # 启动脚本
│   ├── stop.sh             # 停止脚本
│   ├── .env.example        # 环境变量示例
│   └── sandbox/            # 沙箱环境
│       ├── Dockerfile.sandbox  # 沙箱容器
│       └── entrypoint.sh    # 容器入口脚本
├── frontend/               # 前端静态文件
│   ├── css/                # 样式文件
│   │   ├── styles.css      # 主样式表
│   │   └── markdown.css    # 🆕 Markdown渲染样式
│   ├── js/                 # JavaScript文件
│   │   ├── editor.js       # Monaco编辑器配置
│   │   ├── preview.js      # 代码预览功能
│   │   ├── ai-chat.js      # AI对话功能
│   │   ├── toggle-panels.js # 面板折叠功能
│   │   ├── test-results.js  # 测试结果显示
│   │   ├── api-interface.js # 与主项目通信的API接口
│   │   └── smart-learning.js # 🆕 智能学习助手
│   ├── index.html          # 主页面（已集成智能功能）
│   └── demo.html           # API演示页面
└── README.md               # 📖 详细使用教程
```

## 🚀 快速开始

### 环境要求

- **Python 3.12+** (支持智能分析功能)
- **Docker** (用于代码执行沙箱)
- **现代浏览器** (Chrome、Firefox、Edge等)

### 1. 依赖安装

```bash
# 进入后端目录
cd ide-module/backend

# 安装Python基础依赖
pip install -r requirements.txt

# 🆕 安装智能分析依赖
pip install scikit-learn matplotlib seaborn numpy pandas
```

### 2. 启动系统

```bash
# 启动后端服务（包含智能分析API）
python app.py

# 另开终端，启动前端服务
cd ../frontend
python -m http.server 3000
```

系统启动后：
- **后端API**: http://localhost:8080
- **前端界面**: http://localhost:3000
- **智能功能**: 自动激活，支持实时行为分析

### 3. 验证安装

```bash
# 检查v2 API状态
curl http://localhost:8080/api/v2/info

# 预期返回：智能分析功能列表和端点信息
```

## 📖 详细使用指南

### 第一步：打开学习界面

1. **访问系统**: 浏览器打开 `http://localhost:3000`
2. **界面布局**:
   - **左侧面板**: 测试要求、🧠智能助手、AI对话
   - **右侧面板**: 代码编辑器（HTML/CSS/JS）和预览
   - **智能功能**: 后台自动运行的行为分析

### 第二步：体验智能学习

#### 2.1 代码编辑与行为追踪

```html
<!-- 在HTML编辑器中输入以下代码 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>我的第一个智能学习页面</title>
</head>
<body>
    <h1>欢迎使用智能学习系统!</h1>
    <p>系统正在分析您的学习行为...</p>
</body>
</html>
```

**系统自动记录**:
- ✅ 代码编辑模式（增删改）
- ✅ 编辑停顿时间（检测困惑）
- ✅ 语法错误检测和修复
- ✅ 光标移动模式分析

#### 2.2 智能状态监控

在**🧠智能助手**面板中观察：

```
实时学习状态:
├── 认知负荷: 中 ← 动态计算
├── 专注度: 中   ← 行为推断  
├── 知识水平: 1.0/5 ← BKT追踪
└── 困惑程度: 无 ← ML预测
```

系统会根据您的编程行为实时更新状态！

#### 2.3 自适应智能功能

**智能出题**:
1. 点击"生成测试题"
2. 系统根据您的认知负荷自动调整难度
3. 获得个性化的学习题目

**智能建议**:
- 认知负荷高时：推荐简单练习或休息
- 困惑程度高时：提供额外帮助和示例
- 学习顺利时：推荐更有挑战性的内容

### 第三步：高级智能功能

#### 3.1 贝叶斯知识追踪

系统使用标准BKT模型跟踪每个知识点：

```python
# BKT核心参数
P(L₀) = 0.1    # 初始掌握概率
P(T) = 0.2     # 学习转移概率  
P(G) = 0.25    # 猜测概率
P(S) = 0.1     # 失误概率

# 每次学习后更新掌握概率
P(L_new) = P(L|evidence) + P(T) × (1 - P(L|evidence))
```

#### 3.2 机器学习状态预测

系统使用Random Forest模型分析19维特征：

**特征工程**:
- 编辑频率和节奏
- 错误率和修复时间  
- 代码复杂度变化
- 交互行为模式
- 时间间隔分析

**预测输出**:
- 认知负荷等级 (low/medium/high)
- 困惑程度分数 (0-1)
- 学习状态置信度

#### 3.3 学习进度深度分析

点击"学习进度"查看完整分析：

```
📈 学习进度报告:
├── 整体进度
│   ├── 知识水平: 1.0/5
│   ├── 模型置信度: 0.30
│   └── 平均掌握度: 0.1 (BKT)
├── 知识点分析
│   ├── HTML基础: 需要练习 (掌握度 0.1)
│   ├── CSS基础: 需要练习 (掌握度 0.1)  
│   └── JS基础: 需要练习 (掌握度 0.1)
└── 个性化建议
    ├── 有7个知识点需要强化
    └── 建议通过代码示例学习
```

## 🔧 API接口详解

### v2 智能分析API

系统提供完整的RESTful API支持研究和集成：

#### 获取增强学习者模型
```bash
curl -X GET "http://localhost:8080/api/v2/student-model/main_student"

# 返回完整的学习者状态，包含BKT分析和ML预测
```

#### 记录学习行为  
```bash
curl -X POST "http://localhost:8080/api/v2/behavior/log" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "main_student",
    "session_id": "session_001", 
    "event_type": "code_edit",
    "event_data": {
      "code_before": "<div>Hello</div>",
      "code_after": "<div>Hello World</div>",
      "edit_length": 6,
      "language": "html"
    }
  }'
```

#### 生成自适应测试题
```bash
curl -X POST "http://localhost:8080/api/v2/quiz/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "main_student",
    "knowledge_points": ["html_basics"],
    "num_questions": 2
  }'

# 返回基于学习状态的个性化题目
```

#### 获取学习进度分析
```bash
curl -X GET "http://localhost:8080/api/v2/learning/progress/main_student"

# 返回BKT分析、ML状态、个性化建议等
```

### v1 传统API (向后兼容)

传统的IDE功能API继续支持：

- `GET /` - 健康检查
- `POST /execute` - 代码执行
- `POST /ai/chat` - AI对话
- `POST /static-check` - 静态检查

## 🎓 应用场景

### 1. 个人自主学习

**适用对象**: HTML/CSS/JavaScript初学者

**学习流程**:
1. 按教程完成基础练习
2. 观察智能助手的实时反馈  
3. 根据个性化建议调整学习策略
4. 完成自适应测试验证掌握程度

**智能化优势**:
- 实时检测学习困惑，及时提供帮助
- 根据认知负荷调整内容难度
- 个性化学习路径推荐

### 2. 教育研究实验

**适用对象**: 教育技术研究者

**实验设计**:
```python
# 对照实验设计
对照组: 传统编程学习环境
实验组: 智能自适应学习系统

# 收集数据
学习效果数据: 完成时间、准确率、知识掌握度
行为数据: 编辑模式、错误模式、求助频率  
用户体验: 满意度、认知负荷、学习偏好

# 分析指标
学习效率提升: 时间效率对比
学习效果提升: 知识掌握对比
用户体验提升: 满意度和认知负荷对比
```

**CHI论文支持**:
- 完整的离线评估系统
- 模型准确性验证数据
- 统计显著性分析工具

### 3. 智能教学系统集成

**适用对象**: 在线教育平台

**集成方式**:
```javascript
// iframe集成智能学习模块
<iframe src="/ide-module/frontend/index.html"></iframe>

// 监听学习状态变化
window.addEventListener('message', function(event) {
    if (event.data.action === 'learningStateUpdate') {
        const { cognitiveLoad, confusionLevel } = event.data;
        
        // 根据状态调整教学策略
        if (cognitiveLoad === 'high') {
            showHelpSuggestion();
        }
    }
});
```

## 📊 学术研究功能

### 离线评估系统

用于验证模型准确性和生成论文数据：

```python
from analytics.offline_evaluator import get_offline_evaluator, GroundTruthData

# 创建评估器
evaluator = get_offline_evaluator()

# 添加真实标签数据  
ground_truth = GroundTruthData(
    student_id='student_001',
    knowledge_point='html_basics',
    true_cognitive_load='high',
    true_confusion_level='moderate', 
    true_mastery_level=0.7,
    actual_performance=True
)
evaluator.add_ground_truth(ground_truth)

# 生成评估报告
report = evaluator.generate_evaluation_report()

# 获取论文就绪的指标
print(f"BKT准确率: {report['bkt_model_evaluation']['accuracy']}")
print(f"ML预测精度: {report['ml_model_evaluation']['precision']}")
```

### CHI论文数据收集

```python
from analytics.offline_evaluator import CHIPaperDataCollector

collector = CHIPaperDataCollector(evaluator)

# 对照实验数据收集
comparison = collector.collect_comparative_study_data(
    control_group_data=traditional_learning_data,
    experimental_group_data=smart_learning_data
)

# 获取论文关键发现
findings = comparison['paper_ready_metrics']['key_findings']
# 例如: ["学习效率提升: 15.2%", "认知负荷降低: 23.1%"]
```

## 🔍 故障排除

### 常见问题解决

**Q1: 智能功能不工作**
```bash
# 检查v2 API状态
curl http://localhost:8080/api/v2/info

# 预期返回: "analytics_available": true
```

**Q2: 机器学习模型未训练**
- 正常现象，需要收集足够行为数据后自动训练
- 初期使用基于规则的预测，随着数据增加切换到ML模型

**Q3: BKT追踪不准确**
- 确保有足够的学习表现数据
- 检查知识点定义是否与学习内容匹配

### 性能监控

```bash
# 查看系统日志
tail -f logs/behavior/*.log

# 检查模型状态
ls models/  # ML模型文件

# 查看评估报告
ls evaluation_data/  # 离线评估结果
```

## 🎯 系统价值

### 对学习者

1. **个性化学习体验**: 根据学习状态实时调整
2. **智能困惑检测**: 及时发现并解决学习难点
3. **科学学习指导**: 基于数据的客观建议
4. **学习效果可视化**: 清晰的进度追踪

### 对教育者  

1. **学习行为洞察**: 深度理解学习过程
2. **教学策略优化**: 数据驱动的教学改进
3. **个性化干预**: 精准的学习支持
4. **效果评估工具**: 科学的教学评价

### 对研究者

1. **创新技术验证**: 人-AI融合教学模式
2. **大规模数据采集**: 丰富的学习行为数据  
3. **模型效果评估**: 完整的评估框架
4. **论文支撑工具**: CHI等顶级会议发表支持

---

**系统版本**: v2.0 (智能增强版)  
**发布日期**: 2025-07-20  
**研究支持**: ACM CHI会议论文项目  
**技术特色**: 人-LLM融合 + 贝叶斯知识追踪 + 机器学习状态预测

