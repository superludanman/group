// 渐进式文档模块（docs_module）集成脚本
// 依赖：main.html 右侧 info-panel 区域 knowledge-content

const DOCS_API_URL = 'http://localhost:8000/api/module/docs_module';

const DIFFICULTY = [
  { key: 'basic', label: '基础介绍', category: 'basic' },
  { key: 'intermediate', label: '语法和基本用法', category: 'basic' },
  { key: 'advanced', label: '实际应用', category: 'advanced' },
  { key: 'expert', label: '深入原理', category: 'advanced' }
];

let docsModuleState = {
  currentTag: null,
  currentLevelIndex: 0,
  contents: {},
  basicTimer: 0,
  advancedTimer: 0,
  basicInterval: null,
  advancedInterval: null
};

export function initDocsModule(containerId = 'knowledge-content') {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = `
    <div id="docs-module-ui">
      <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;">
        <input type="text" id="tag-id" placeholder="知识点分组ID" style="width:120px;">
        <button id="tag-btn">获取分组标签</button>
        <input type="text" id="tag-input" placeholder="组件名称" style="width:120px;">
        <button id="test-btn">查找组件</button>
        <input type="text" id="user-id" placeholder="用户ID" style="width:100px;">
      </div>
      <div id="tag-select-container"></div>
      <div id="doc-content" style="margin-top:16px;"></div>
      <div class="timer-display" style="margin-top:20px;display:flex;gap:24px;">
        <div class="timer-item"><span class="timer-label">基础内容：</span><span id="basic-time">00:00</span></div>
        <div class="timer-item"><span class="timer-label">进阶内容：</span><span id="advanced-time">00:00</span></div>
      </div>
    </div>
  `;
  // 事件绑定
  document.getElementById('tag-btn').onclick = onTagGroupSearch;
  document.getElementById('test-btn').onclick = onTagSearch;
}

async function onTagGroupSearch() {
  const tagId = document.getElementById('tag-id').value.trim();
  if (!tagId) {
    showError('请输入知识点分组ID');
    return;
  }
  // 读取 idTotag.json（假设已部署到 /Doc_Module/idTotag.json）
  try {
    const response = await fetch('./idTotag.json');
    if (!response.ok) throw new Error('获取标签分组失败');
    const data = await response.json();
    const tags = data['knowledge_map'][tagId];
    if (!tags || tags.length === 0) throw new Error('未找到相关标签');
    renderTagSelect(tags);
  } catch (e) {
    showError(e.message);
  }
}

function renderTagSelect(tags) {
  const container = document.getElementById('tag-select-container');
  container.innerHTML = `
    <div style="margin-bottom: 12px;">
      <label for="tag-select" style="font-weight:bold;">请选择标签：</label>
      <select id="tag-select"><option value="">-- 请选择 --</option>${tags.map(tag => `<option value="${tag}">${tag}</option>`).join('')}</select>
    </div>
  `;
  document.getElementById('tag-select').onchange = function(e) {
    if (e.target.value) loadDocumentForTag(e.target.value);
  };
}

async function onTagSearch() {
  const tagName = document.getElementById('tag-input').value.trim();
  if (!tagName) {
    showError('请输入组件名称');
    return;
  }
  await loadDocumentForTag(tagName);
}

async function loadDocumentForTag(tagName) {
  try {
    const response = await fetch(DOCS_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tag_name: tagName, action: 'docs_content' })
    });
    const contentsData = await response.json();
    if (contentsData.status !== 'success') throw new Error(contentsData.message || '未找到内容');
    docsModuleState.currentTag = { id: tagName, title: `${tagName} 组件` };
    docsModuleState.currentLevelIndex = 0;
    docsModuleState.contents = contentsData['data']['contents'];
    renderDocContent();
    startTimer();
  } catch (e) {
    showError(e.message);
  }
}

function renderDocContent() {
  const docContent = document.getElementById('doc-content');
  if (!docsModuleState.currentTag) {
    docContent.innerHTML = '<div style="color:#999;">请选择标签</div>';
    return;
  }
  const level = DIFFICULTY[docsModuleState.currentLevelIndex];
  let content = docsModuleState.contents[level.key] || `暂无${level.label}内容。`;
  docContent.innerHTML = `
    <div class="header" style="display:flex;align-items:center;justify-content:space-between;">
      <h2 id="tag-title">${docsModuleState.currentTag.title}</h2>
      <div id="level-navigation" style="display:flex;align-items:center;gap:8px;">
        <span id="current-level">${level.label}</span>
        <span id="level-progress">${docsModuleState.currentLevelIndex+1}/${DIFFICULTY.length}</span>
        <button id="prev-btn" ${docsModuleState.currentLevelIndex===0?'disabled':''}>上一级</button>
        <button id="next-btn" ${docsModuleState.currentLevelIndex===DIFFICULTY.length-1?'disabled':''}>下一级</button>
      </div>
    </div>
    <div class="level-block" style="margin-top:12px;">
      <pre class="content-text" style="white-space:pre-wrap;font-size:15px;">${content}</pre>
    </div>
    <div id="completion-section" style="margin-top:16px;${docsModuleState.currentLevelIndex===3?'':'display:none;'}">
      <button id="complete-btn">阅读完毕</button>
    </div>
    <div id="statusContainer" class="status info" style="display:none;"></div>
  `;
  // 事件绑定
  document.getElementById('prev-btn').onclick = function() {
    if (docsModuleState.currentLevelIndex > 0) {
      docsModuleState.currentLevelIndex--;
      renderDocContent();
      startTimer();
    }
  };
  document.getElementById('next-btn').onclick = function() {
    if (docsModuleState.currentLevelIndex < DIFFICULTY.length-1) {
      docsModuleState.currentLevelIndex++;
      renderDocContent();
      startTimer();
    }
  };
  document.getElementById('complete-btn').onclick = async function(e) {
    e.preventDefault();
    stopTimer();
    await sendTimeToBackend();
    this.textContent = '您已完成此组件学习';
    this.disabled = true;
  };
  updateTimeDisplay();
}

function startTimer() {
  stopTimer();
  const level = DIFFICULTY[docsModuleState.currentLevelIndex];
  if (level.category === 'basic') {
    docsModuleState.basicInterval = setInterval(() => {
      docsModuleState.basicTimer++;
      updateTimeDisplay();
    }, 1000);
  } else {
    docsModuleState.advancedInterval = setInterval(() => {
      docsModuleState.advancedTimer++;
      updateTimeDisplay();
    }, 1000);
  }
}

function stopTimer() {
  clearInterval(docsModuleState.basicInterval);
  clearInterval(docsModuleState.advancedInterval);
}

function updateTimeDisplay() {
  document.getElementById('basic-time').textContent = formatTime(docsModuleState.basicTimer);
  document.getElementById('advanced-time').textContent = formatTime(docsModuleState.advancedTimer);
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

async function sendTimeToBackend() {
  const userId = document.getElementById('user-id').value.trim();
  try {
    const response = await fetch(DOCS_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ base_time: docsModuleState.basicTimer, advanced_time: docsModuleState.advancedTimer, action: 'record_time', user_id: userId })
    });
    const data = await response.json();
    docsModuleState.basicTimer = 0;
    docsModuleState.advancedTimer = 0;
    updateTimeDisplay();
    if (data.status !== 'success') showError(data.message || '时间记录失败');
  } catch (e) {
    showError('时间记录失败');
  }
}

function showError(msg) {
  let statusDiv = document.getElementById('statusContainer');
  if (!statusDiv) {
    statusDiv = document.createElement('div');
    statusDiv.id = 'statusContainer';
    statusDiv.className = 'status info';
    document.getElementById('doc-content').prepend(statusDiv);
  }
  statusDiv.textContent = msg;
  statusDiv.style.display = 'block';
  setTimeout(() => { statusDiv.style.display = 'none'; }, 3000);
} 