/**
 * 预览页面的JavaScript代码
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('预览页面已初始化');
    
    // 获取DOM元素
    const nextStepButton = document.getElementById('next-step');
    const previewFrame = document.getElementById('preview-frame');
    const aiExplanation = document.getElementById('ai-explanation');
    const moduleContainer = document.getElementById('preview-module-container');
    
    // 使用占位符内容初始化
    if (previewFrame) {
        previewFrame.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <p>预览内容将在此处显示。</p>
                <p>此区域将包含嵌入式网页供用户查看。</p>
            </div>
        `;
    }
    
    // 示例解释内容
    const explanations = [
        "这是一个带有页眉、导航和内容部分的基本HTML网页。",
        "注意导航菜单如何帮助用户在页面之间移动。让我们探索如何使用HTML创建它。",
        "布局使用CSS Grid以响应式方式组织内容。让我们看看它是如何工作的。"
    ];
    
    let currentStep = 0;
    
    // 处理下一步按钮点击
    if (nextStepButton) {
        nextStepButton.addEventListener('click', function() {
            currentStep = (currentStep + 1) % explanations.length;
            
            if (aiExplanation) {
                aiExplanation.innerHTML = `<p>${explanations[currentStep]}</p>`;
            }
            
            console.log(`移动到预览步骤 ${currentStep + 1}`);
        });
    }
    
    // 从后端加载示例数据
    async function loadPreviewExample() {
        try {
            // 从API获取预览模块数据
            const moduleData = await ApiClient.getModule('preview_module');
            console.log('预览模块数据:', moduleData);
            
            if (moduleData && moduleData.status === 'active') {
                // 获取当前示例
                const exampleId = moduleData.data.current_example;
                
                // 获取特定示例数据
                const exampleData = await ApiClient.sendToModule('preview_module', {
                    action: 'get_example',
                    example_id: exampleId
                });
                
                if (exampleData && exampleData.status === 'success') {
                    // 显示示例
                    displayExample(exampleData.example);
                }
            }
        } catch (error) {
            console.error('加载预览示例时出错:', error);
            
            // 显示错误消息
            if (previewFrame) {
                previewFrame.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: red;">
                        <p>加载预览内容时出错。</p>
                        <p>请确保后端服务器正在运行。</p>
                    </div>
                `;
            }
        }
    }
    
    // 显示预览示例
    function displayExample(example) {
        if (!example) return;
        
        if (previewFrame) {
            // 显示HTML内容
            previewFrame.innerHTML = `
                <div style="padding: 1rem;">
                    <h3>${example.name}</h3>
                    <div class="example-preview" style="border: 1px solid #ddd; padding: 1rem; margin: 1rem 0;">
                        ${example.html}
                    </div>
                </div>
            `;
        }
        
        if (aiExplanation) {
            // 显示解释
            aiExplanation.innerHTML = `<p>${example.explanation}</p>`;
        }
    }
    
    // 加载下一个示例
    async function loadNextExample() {
        try {
            // 获取当前示例
            const moduleData = await ApiClient.getModule('preview_module');
            const currentExampleId = moduleData.data.current_example;
            
            // 请求下一个示例
            const nextExampleData = await ApiClient.sendToModule('preview_module', {
                action: 'next_example',
                example_id: currentExampleId
            });
            
            if (nextExampleData && nextExampleData.status === 'success') {
                // 显示下一个示例
                displayExample(nextExampleData.example);
            }
        } catch (error) {
            console.error('加载下一个示例时出错:', error);
        }
    }
    
    // 加载预览模块
    if (moduleContainer) {
        // 向用户显示加载消息
        moduleContainer.innerHTML = '<p>正在加载预览模块...</p>';
        
        // 尝试从后端加载数据
        loadPreviewExample();
    }
    
    // 如果有下一步按钮，将其重新连接到加载下一个示例
    if (nextStepButton) {
        // 移除旧的事件监听器
        nextStepButton.replaceWith(nextStepButton.cloneNode(true));
        
        // 获取新的按钮引用
        const newNextStepButton = document.getElementById('next-step');
        
        // 添加新的事件监听器
        if (newNextStepButton) {
            newNextStepButton.addEventListener('click', loadNextExample);
        }
    }
});