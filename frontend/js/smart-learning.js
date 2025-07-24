/**
 * 智能学习助手 - 集成行为追踪、学习者模型和自动出题系统
 * 
 * 功能：
 * 1. 实时行为数据采集
 * 2. 学习者状态监控
 * 3. 自适应出题和评估
 * 4. 个性化学习建议
 */

class SmartLearningAssistant {
    constructor() {
        // 基础配置
        this.studentId = 'student_001';  // 单用户场景
        this.sessionId = this.generateSessionId();
        this.apiBase = '';  // 使用相对路径
        
        // 行为追踪
        this.behaviorTracker = null;
        this.lastCodeContent = { html: '', css: '', js: '' };
        this.startTime = Date.now();
        this.lastActivityTime = Date.now();
        
        // 学习状态
        this.currentLearnerModel = null;
        this.currentQuiz = null;
        
        // 事件监听器
        this.eventListeners = new Map();
        
        this.initialize();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    async initialize() {
        console.log('🧠 智能学习助手初始化中...');
        
        try {
            // 检查v2 API是否可用
            await this.checkApiStatus();
            
            // 初始化行为追踪
            this.initializeBehaviorTracking();
            
            // 创建智能功能UI
            this.createSmartUI();
            
            // 获取初始学习者模型
            await this.refreshLearnerModel();
            
            console.log('✅ 智能学习助手初始化完成');
            
        } catch (error) {
            console.error('❌ 智能学习助手初始化失败:', error);
            this.showErrorMessage('智能功能初始化失败，将使用基础功能');
        }
    }
    
    async checkApiStatus() {
        const response = await fetch(`${this.apiBase}/api/v2/info`);
        if (!response.ok) {
            throw new Error('v2 API不可用');
        }
        const data = await response.json();
        console.log('📊 v2 API状态:', data);
        return data;
    }
    
    initializeBehaviorTracking() {
        // 监听代码编辑事件
        this.setupEditorTracking();
        
        // 监听用户交互事件
        this.setupInteractionTracking();
        
        // 设置定期状态更新
        setInterval(() => this.updateLearnerModel(), 30000); // 每30秒更新一次
        
        console.log('👀 行为追踪已启动');
    }
    
    setupEditorTracking() {
        // 监听Monaco编辑器变化
        const checkEditorChanges = () => {
            if (window.htmlEditor || window.cssEditor || window.jsEditor) {
                // HTML编辑器
                if (window.htmlEditor && !this.eventListeners.has('html')) {
                    const listener = () => this.onCodeEdit('html');
                    window.htmlEditor.onDidChangeModelContent(listener);
                    this.eventListeners.set('html', listener);
                }
                
                // CSS编辑器
                if (window.cssEditor && !this.eventListeners.has('css')) {
                    const listener = () => this.onCodeEdit('css');
                    window.cssEditor.onDidChangeModelContent(listener);
                    this.eventListeners.set('css', listener);
                }
                
                // JS编辑器
                if (window.jsEditor && !this.eventListeners.has('js')) {
                    const listener = () => this.onCodeEdit('js');
                    window.jsEditor.onDidChangeModelContent(listener);
                    this.eventListeners.set('js', listener);
                }
            } else {
                // 编辑器还未初始化，等待
                setTimeout(checkEditorChanges, 1000);
            }
        };
        
        checkEditorChanges();
    }
    
    setupInteractionTracking() {
        // 监听AI对话
        const originalSendMessage = window.sendMessage;
        if (originalSendMessage) {
            window.sendMessage = () => {
                this.onHelpRequest();
                return originalSendMessage();
            };
        }
        
        // 监听按钮点击
        document.addEventListener('click', (event) => {
            if (event.target.matches('.btn, button')) {
                this.onUserInteraction('button_click', event.target.textContent);
            }
        });
        
        // 监听页面焦点变化
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.onPauseStart();
            } else {
                this.onPauseEnd();
            }
        });
        
        // 监听键盘事件
        document.addEventListener('keydown', (event) => {
            this.lastActivityTime = Date.now();
            
            // 检测特殊按键
            if (event.key === 'Backspace') {
                this.onBackspace();
            } else if (event.ctrlKey && event.key === 'v') {
                this.onPaste();
            }
        });
    }
    
    async onCodeEdit(language) {
        const currentCode = this.getCurrentCode();
        const previousCode = this.lastCodeContent[language] || '';
        
        // 计算编辑差异
        const editLength = Math.abs(currentCode[language].length - previousCode.length);
        
        // 记录编辑事件
        await this.logBehaviorEvent('code_edit', {
            timestamp: Date.now() / 1000,
            code_before: previousCode,
            code_after: currentCode[language],
            edit_length: editLength,
            language: language,
            current_task: this.getCurrentTask()
        });
        
        // 更新缓存
        this.lastCodeContent = currentCode;
        
        // 检查是否有语法错误
        this.checkForErrors(currentCode);
    }
    
    async onHelpRequest() {
        const userMessage = document.getElementById('user-message')?.value || '';
        
        await this.logBehaviorEvent('help_request', {
            timestamp: Date.now() / 1000,
            help_query: userMessage,
            current_task: this.getCurrentTask()
        });
    }
    
    async onPauseStart() {
        this.pauseStartTime = Date.now();
    }
    
    async onPauseEnd() {
        if (this.pauseStartTime) {
            const duration = (Date.now() - this.pauseStartTime) / 1000;
            
            await this.logBehaviorEvent('pause_end', {
                timestamp: Date.now() / 1000,
                duration: duration
            });
            
            this.pauseStartTime = null;
        }
    }
    
    async onBackspace() {
        // 简单计数退格操作
        this.backspaceCount = (this.backspaceCount || 0) + 1;
    }
    
    async onPaste() {
        await this.logBehaviorEvent('code_paste', {
            timestamp: Date.now() / 1000,
            current_task: this.getCurrentTask()
        });
    }
    
    async onUserInteraction(type, details) {
        this.lastActivityTime = Date.now();
        
        // 记录一般交互事件
        if (Math.random() < 0.1) { // 采样记录，避免过多事件
            await this.logBehaviorEvent('user_interaction', {
                timestamp: Date.now() / 1000,
                interaction_type: type,
                details: details
            });
        }
    }
    
    getCurrentCode() {
        return {
            html: window.htmlEditor ? window.htmlEditor.getValue() : '',
            css: window.cssEditor ? window.cssEditor.getValue() : '',
            js: window.jsEditor ? window.jsEditor.getValue() : ''
        };
    }
    
    getCurrentTask() {
        // 从测试要求中提取当前任务
        const requirementsElement = document.getElementById('test-requirements-content');
        if (requirementsElement) {
            const text = requirementsElement.textContent || '';
            if (text.includes('HTML')) return 'html_basics';
            if (text.includes('CSS')) return 'css_basics';
            if (text.includes('JavaScript')) return 'js_basics';
        }
        return 'general_practice';
    }
    
    async checkForErrors(code) {
        // 简单的语法错误检查
        const errors = [];
        
        // HTML错误检查
        const htmlErrors = this.checkHTMLErrors(code.html);
        errors.push(...htmlErrors);
        
        // CSS错误检查
        const cssErrors = this.checkCSSErrors(code.css);
        errors.push(...cssErrors);
        
        // 如果发现错误，记录
        for (const error of errors) {
            await this.logBehaviorEvent('error_occur', {
                timestamp: Date.now() / 1000,
                error_type: error.type,
                error_message: error.message,
                code_context: error.context
            });
        }
    }
    
    checkHTMLErrors(html) {
        const errors = [];
        
        // 检查未闭合标签
        const openTags = html.match(/<[^/>][^>]*>/g) || [];
        const closeTags = html.match(/<\/[^>]+>/g) || [];
        
        if (openTags.length > closeTags.length) {
            errors.push({
                type: 'SyntaxError',
                message: '可能存在未闭合的HTML标签',
                context: html.substring(0, 100)
            });
        }
        
        return errors;
    }
    
    checkCSSErrors(css) {
        const errors = [];
        
        // 检查未闭合的大括号
        const openBraces = (css.match(/\{/g) || []).length;
        const closeBraces = (css.match(/\}/g) || []).length;
        
        if (openBraces !== closeBraces) {
            errors.push({
                type: 'SyntaxError',
                message: '可能存在未闭合的CSS大括号',
                context: css.substring(0, 100)
            });
        }
        
        return errors;
    }
    
    async logBehaviorEvent(eventType, eventData) {
        try {
            const response = await fetch(`${this.apiBase}/api/v2/behavior/log`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: this.studentId,
                    session_id: this.sessionId,
                    event_type: eventType,
                    event_data: eventData
                })
            });
            
            if (!response.ok) {
                console.warn('行为事件记录失败:', response.status);
            }
            
        } catch (error) {
            console.warn('行为事件记录异常:', error);
        }
    }
    
    async refreshLearnerModel() {
        try {
            const response = await fetch(`${this.apiBase}/api/v2/student-model/${this.studentId}`);
            if (response.ok) {
                this.currentLearnerModel = await response.json();
                this.updateLearnerModelDisplay();
            }
        } catch (error) {
            console.warn('获取学习者模型失败:', error);
        }
    }
    
    async updateLearnerModel() {
        await this.refreshLearnerModel();
    }
    
    updateLearnerModelDisplay() {
        if (!this.currentLearnerModel) return;
        
        const cognitive = this.currentLearnerModel.cognitive_state || {};
        const emotional = this.currentLearnerModel.emotional_state || {};
        
        // 更新状态显示
        const statusElement = document.getElementById('learning-status');
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="status-item">
                    <span class="status-label">认知负荷:</span>
                    <span class="status-value status-${cognitive.cognitive_load}">${this.translateStatus(cognitive.cognitive_load)}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">专注度:</span>
                    <span class="status-value status-${emotional.focus_level}">${this.translateStatus(emotional.focus_level)}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">知识水平:</span>
                    <span class="status-value">${(cognitive.knowledge_level || 1).toFixed(1)}/5</span>
                </div>
            `;
        }
        
        // 根据状态调整UI
        this.adaptUIToLearnerState();
    }
    
    adaptUIToLearnerState() {
        if (!this.currentLearnerModel) return;
        
        const cognitive = this.currentLearnerModel.cognitive_state || {};
        const emotional = this.currentLearnerModel.emotional_state || {};
        
        // 根据认知负荷调整界面
        if (cognitive.cognitive_load === 'high') {
            this.showLearningTip('检测到认知负荷较高，建议适当休息或降低任务难度');
        }
        
        // 根据困惑程度提供帮助
        if (cognitive.confusion_level === 'severe') {
            this.suggestHelp('似乎遇到了困难，要不要看看相关的示例或寻求帮助？');
        }
        
        // 根据专注度调整
        if (emotional.focus_level === 'low') {
            this.showFocusTip('注意力似乎有些分散，尝试专注于当前任务');
        }
    }
    
    translateStatus(status) {
        const translations = {
            'low': '低',
            'medium': '中',
            'high': '高',
            'none': '无',
            'slight': '轻微',
            'moderate': '中度',
            'severe': '严重'
        };
        return translations[status] || status;
    }
    
    async generateAdaptiveQuiz() {
        try {
            const response = await fetch(`${this.apiBase}/api/v2/quiz/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: this.studentId,
                    knowledge_points: [this.getCurrentTask()],
                    num_questions: 2
                })
            });
            
            if (response.ok) {
                this.currentQuiz = await response.json();
                this.displayQuiz();
            } else {
                throw new Error('生成测试题失败');
            }
            
        } catch (error) {
            console.error('生成自适应测试题失败:', error);
            this.showErrorMessage('生成测试题失败，请稍后重试');
        }
    }
    
    displayQuiz() {
        if (!this.currentQuiz || !this.currentQuiz.questions) return;
        
        const quizContainer = document.getElementById('quiz-container');
        if (!quizContainer) return;
        
        const questions = this.currentQuiz.questions;
        let quizHTML = '<div class="quiz-header"><h3>📝 智能测试题</h3></div>';
        
        questions.forEach((question, index) => {
            quizHTML += `
                <div class="quiz-question" data-question-id="${question.id}">
                    <h4>题目 ${index + 1}: ${question.title}</h4>
                    <p>${question.content}</p>
                    <div class="quiz-difficulty">难度: ${this.translateDifficulty(question.difficulty)}</div>
                    
                    ${this.renderQuestionInput(question)}
                    
                    <div class="quiz-actions">
                        <button class="btn btn-primary" onclick="smartAssistant.submitAnswer('${question.id}')">提交答案</button>
                    </div>
                </div>
            `;
        });
        
        quizHTML += `
            <div class="quiz-actions">
                <button class="btn btn-secondary" onclick="smartAssistant.closeQuiz()">关闭测试</button>
            </div>
        `;
        
        quizContainer.innerHTML = quizHTML;
        quizContainer.style.display = 'block';
    }
    
    renderQuestionInput(question) {
        switch (question.type) {
            case 'fill_in_blank':
                if (question.template) {
                    return `
                        <div class="code-template">
                            <pre><code>${question.template.code_template}</code></pre>
                        </div>
                        <div class="fill-blanks">
                            ${question.template.blank_count ? 
                                Array.from({length: question.template.blank_count}, (_, i) => 
                                    `<input type="text" class="blank-input" placeholder="填空 ${i+1}" data-blank="${i}">`
                                ).join('') : ''
                            }
                        </div>
                    `;
                }
                break;
                
            case 'error_correction':
                if (question.buggy_code) {
                    return `
                        <div class="buggy-code">
                            <h5>请修正以下代码的错误：</h5>
                            <textarea class="code-input" rows="10">${question.buggy_code.code}</textarea>
                        </div>
                    `;
                }
                break;
                
            case 'code_implementation':
                if (question.implementation_task) {
                    return `
                        <div class="implementation-task">
                            <h5>实现要求：</h5>
                            <ul>
                                ${question.implementation_task.requirements.map(req => `<li>${req}</li>`).join('')}
                            </ul>
                            <textarea class="code-input" rows="15">${question.implementation_task.starter_code || ''}</textarea>
                        </div>
                    `;
                }
                break;
                
            default:
                return '<textarea class="answer-input" rows="5" placeholder="请输入您的答案..."></textarea>';
        }
        
        return '<div class="question-error">题目格式错误</div>';
    }
    
    translateDifficulty(difficulty) {
        const levels = {
            'easy': '简单',
            'medium': '中等', 
            'hard': '困难'
        };
        return levels[difficulty] || difficulty;
    }
    
    async submitAnswer(questionId) {
        // 收集答案
        const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
        if (!questionElement) return;
        
        const question = this.currentQuiz.questions.find(q => q.id === questionId);
        if (!question) return;
        
        let answerData = {};
        
        // 根据题型收集答案
        switch (question.type) {
            case 'fill_in_blank':
                const blankInputs = questionElement.querySelectorAll('.blank-input');
                answerData.answers = Array.from(blankInputs).map(input => input.value);
                break;
                
            case 'error_correction':
                const codeInput = questionElement.querySelector('.code-input');
                answerData.corrected_code = codeInput ? codeInput.value : '';
                break;
                
            case 'code_implementation':
                const implInput = questionElement.querySelector('.code-input');
                answerData.implementation_code = implInput ? implInput.value : '';
                break;
                
            default:
                const answerInput = questionElement.querySelector('.answer-input');
                answerData.answer_text = answerInput ? answerInput.value : '';
        }
        
        answerData.time_spent = 60; // 简化为固定时间
        
        try {
            // 提交评估
            const response = await fetch(`${this.apiBase}/api/v2/quiz/evaluate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    student_id: this.studentId,
                    session_id: this.sessionId,
                    answers: [{
                        question_id: questionId,
                        question_type: question.type,
                        answer_data: answerData
                    }]
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this.displayQuizResult(questionId, result);
                
                // 更新学习者模型
                setTimeout(() => this.refreshLearnerModel(), 1000);
            }
            
        } catch (error) {
            console.error('提交答案失败:', error);
            this.showErrorMessage('提交答案失败，请重试');
        }
    }
    
    displayQuizResult(questionId, result) {
        const questionElement = document.querySelector(`[data-question-id="${questionId}"]`);
        if (!questionElement) return;
        
        const evaluation = result.evaluation_results[0];
        const score = evaluation.score;
        const maxScore = evaluation.max_score;
        const percentage = (score / maxScore * 100).toFixed(1);
        
        const resultHTML = `
            <div class="quiz-result">
                <div class="score">得分: ${score}/${maxScore} (${percentage}%)</div>
                <div class="feedback">${evaluation.feedback}</div>
                ${evaluation.suggestions.length > 0 ? `
                    <div class="suggestions">
                        <h5>建议:</h5>
                        <ul>
                            ${evaluation.suggestions.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
        
        const actionsDiv = questionElement.querySelector('.quiz-actions');
        if (actionsDiv) {
            actionsDiv.innerHTML = resultHTML;
        }
    }
    
    closeQuiz() {
        const quizContainer = document.getElementById('quiz-container');
        if (quizContainer) {
            quizContainer.style.display = 'none';
        }
    }
    
    createSmartUI() {
        // 在左侧面板添加智能功能区域
        const leftPanel = document.querySelector('.left-panel');
        if (!leftPanel) return;
        
        const smartSection = document.createElement('div');
        smartSection.className = 'smart-learning-container';
        smartSection.innerHTML = `
            <div class="panel-header">
                <h2>🧠 智能助手</h2>
                <button id="toggle-smart" class="btn btn-small">展开</button>
            </div>
            <div class="panel-content" id="smart-content">
                <!-- 学习状态显示 -->
                <div class="learning-status" id="learning-status">
                    <div class="status-item">
                        <span class="status-label">状态:</span>
                        <span class="status-value">初始化中...</span>
                    </div>
                </div>
                
                <!-- 智能功能按钮 -->
                <div class="smart-actions">
                    <button class="btn btn-primary" onclick="smartAssistant.generateAdaptiveQuiz()">生成测试题</button>
                    <button class="btn btn-secondary" onclick="smartAssistant.showLearningProgress()">学习进度</button>
                    <button class="btn btn-secondary" onclick="smartAssistant.refreshLearnerModel()">刷新状态</button>
                </div>
                
                <!-- 学习提示 -->
                <div class="learning-tips" id="learning-tips"></div>
                
                <!-- 测试题容器 -->
                <div class="quiz-container" id="quiz-container" style="display: none;"></div>
            </div>
        `;
        
        // 插入到修改建议容器之前
        const suggestionsContainer = document.querySelector('.suggestions-container');
        if (suggestionsContainer) {
            leftPanel.insertBefore(smartSection, suggestionsContainer);
        } else {
            leftPanel.appendChild(smartSection);
        }
        
        // 添加切换功能
        const toggleButton = document.getElementById('toggle-smart');
        const smartContent = document.getElementById('smart-content');
        
        if (toggleButton && smartContent) {
            toggleButton.addEventListener('click', () => {
                if (smartContent.style.display === 'none') {
                    smartContent.style.display = 'block';
                    toggleButton.textContent = '收起';
                } else {
                    smartContent.style.display = 'none';
                    toggleButton.textContent = '展开';
                }
            });
        }
        
        // 添加相关CSS样式
        this.addSmartStyles();
    }
    
    addSmartStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .smart-learning-container {
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                overflow: hidden;
            }
            
            .learning-status {
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
                margin-bottom: 15px;
            }
            
            .status-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
                font-size: 14px;
            }
            
            .status-label {
                font-weight: bold;
                color: #666;
            }
            
            .status-value {
                font-weight: bold;
            }
            
            .status-low { color: #28a745; }
            .status-medium { color: #ffc107; }
            .status-high { color: #dc3545; }
            
            .smart-actions {
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin-bottom: 15px;
            }
            
            .smart-actions .btn {
                font-size: 12px;
                padding: 8px 12px;
            }
            
            .learning-tips {
                background: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 10px;
                margin-bottom: 15px;
                border-radius: 4px;
                font-size: 14px;
                display: none;
            }
            
            .quiz-container {
                background: #f8f9fa;
                border-radius: 4px;
                padding: 15px;
                margin-top: 15px;
            }
            
            .quiz-question {
                background: white;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 15px;
                border: 1px solid #ddd;
            }
            
            .quiz-difficulty {
                font-size: 12px;
                color: #666;
                margin-bottom: 10px;
            }
            
            .code-template {
                background: #f4f4f4;
                padding: 10px;
                border-radius: 4px;
                margin: 10px 0;
                font-family: monospace;
            }
            
            .fill-blanks {
                display: flex;
                flex-direction: column;
                gap: 8px;
                margin: 10px 0;
            }
            
            .blank-input, .code-input, .answer-input {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: monospace;
            }
            
            .quiz-result {
                background: #e8f5e8;
                border: 1px solid #4caf50;
                border-radius: 4px;
                padding: 10px;
                margin-top: 10px;
            }
            
            .quiz-result .score {
                font-weight: bold;
                color: #2e7d32;
                margin-bottom: 8px;
            }
            
            .quiz-result .feedback {
                margin-bottom: 8px;
                font-size: 14px;
            }
            
            .quiz-result .suggestions ul {
                margin: 5px 0;
                padding-left: 20px;
            }
            
            .quiz-result .suggestions li {
                font-size: 13px;
                margin-bottom: 3px;
            }
        `;
        
        document.head.appendChild(style);
    }
    
    showLearningTip(message) {
        const tipsElement = document.getElementById('learning-tips');
        if (tipsElement) {
            tipsElement.innerHTML = `💡 ${message}`;
            tipsElement.style.display = 'block';
            
            // 5秒后隐藏
            setTimeout(() => {
                tipsElement.style.display = 'none';
            }, 5000);
        }
    }
    
    suggestHelp(message) {
        this.showLearningTip(message);
        
        // 可以在这里添加更多帮助建议的逻辑
    }
    
    showFocusTip(message) {
        this.showLearningTip(message);
    }
    
    showErrorMessage(message) {
        console.error(message);
        this.showLearningTip(`❌ ${message}`);
    }
    
    async showLearningProgress() {
        try {
            const response = await fetch(`${this.apiBase}/api/v2/learning/progress/${this.studentId}`);
            if (response.ok) {
                const progress = await response.json();
                this.displayLearningProgress(progress);
            }
        } catch (error) {
            console.error('获取学习进度失败:', error);
            this.showErrorMessage('获取学习进度失败');
        }
    }
    
    displayLearningProgress(progress) {
        const overall = progress.overall_progress || {};
        const trends = progress.knowledge_trends || {};
        const recommendations = progress.recommendations || [];
        
        let progressHTML = `
            <div class="progress-header">
                <h3>📈 学习进度分析</h3>
            </div>
            <div class="progress-overall">
                <div class="progress-item">
                    <span>整体知识水平:</span>
                    <span>${(overall.knowledge_level || 1).toFixed(1)}/5</span>
                </div>
                <div class="progress-item">
                    <span>模型置信度:</span>
                    <span>${(overall.overall_confidence || 0.3).toFixed(2)}</span>
                </div>
            </div>
            
            <div class="knowledge-trends">
                <h4>知识点掌握情况:</h4>
        `;
        
        for (const [kpId, trend] of Object.entries(trends)) {
            progressHTML += `
                <div class="trend-item">
                    <span>${trend.name || kpId}:</span>
                    <span class="trend-${trend.trend}">${(trend.current_level || 0).toFixed(1)}/5</span>
                </div>
            `;
        }
        
        progressHTML += '</div>';
        
        if (recommendations.length > 0) {
            progressHTML += `
                <div class="progress-recommendations">
                    <h4>个性化建议:</h4>
                    <ul>
                        ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        progressHTML += '<button class="btn btn-secondary" onclick="smartAssistant.closeProgress()">关闭</button>';
        
        // 显示在quiz容器中
        const container = document.getElementById('quiz-container');
        if (container) {
            container.innerHTML = progressHTML;
            container.style.display = 'block';
        }
    }
    
    closeProgress() {
        this.closeQuiz(); // 复用关闭方法
    }
}

// 全局实例
let smartAssistant = null;

// 在页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    // 等待其他组件初始化完成
    setTimeout(() => {
        smartAssistant = new SmartLearningAssistant();
        
        // 暴露到全局作用域供其他脚本使用
        window.smartAssistant = smartAssistant;
    }, 2000);
});

console.log('🚀 智能学习助手模块已加载');