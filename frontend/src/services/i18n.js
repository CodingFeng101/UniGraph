const translations = new Map(Object.entries({
  '图知识库列表': 'Knowledge Bases',
  '信息': 'Info',
  '设计': 'Design',
  '构建': 'Build',
  '新建对话': 'New chat',
  '个人中心': 'Profile',
  '语言': 'Language',
  '主题': 'Theme',
  '亮色': 'Light',
  '暗色': 'Dark',
  '跟随系统': 'System',
  '中文': 'Chinese',
  '英文': 'English',
  '退出登录': 'Log out',
  '新增架构': 'New schema',
  '更新知识架构': 'Update schema',
  '新增实体类型': 'New entity type',
  '新增关系类型': 'New relation type',
  '导出架构': 'Export schema',
  '基于文档构建': 'Build from documents',
  '导入 JSON': 'Import JSON',
  '架构名称': 'Schema name',
  '需求': 'Requirements',
  '开始构建': 'Start building',
  '选择 JSON 文件': 'Select JSON file',
  '新增实体': 'New entity',
  '新增关系': 'New relation',
  '创建知识图谱': 'Create knowledge graph',
  '建立索引': 'Build index',
  '选择知识图谱': 'Select knowledge graph',
  '重命名': 'Rename',
  '收藏': 'Favorite',
  '取消收藏': 'Unfavorite',
  '删除': 'Delete',
  '编辑': 'Edit',
  '保存': 'Save',
  '取消': 'Cancel',
  '创建于': 'Created',
  '更新于': 'Updated',
  '架构': 'Schema',
  '知识图谱': 'Knowledge graphs',
  '描述': 'Description',
  '新建知识库': 'New knowledge base',
  '创建': 'Create',
  '知识库名称': 'Knowledge base name',
  '按时间从新到旧': 'Newest first',
  '按时间从旧到新': 'Oldest first',
  '按名称升序': 'Name A-Z',
  '按名称降序': 'Name Z-A',
  '后台任务': 'Background tasks',
  '模型配置': 'Model configuration',
  '昵称': 'Nickname',
  '邮箱': 'Email',
}));

const placeholders = new Map(Object.entries({
  '搜索知识库...': 'Search knowledge bases...',
  '搜索实体或关系类型...': 'Search entities or relation types...',
  '输入架构名称': 'Enter schema name',
  '描述需要抽取的实体类型、关系和目标': 'Describe entity types, relations, and goals',
  '输入消息...': 'Write a message...',
}));

const originalText = new WeakMap();
const originalPlaceholder = new WeakMap();
const selectors = 'button,button span,label,nav a,nav a span,h1,h2,h3,th,option,[data-i18n],#user-dropdown span,.sidebar-content > .flex span';

function translateElement(element, lang) {
  element.childNodes.forEach((node) => {
    if (node.nodeType !== Node.TEXT_NODE || !node.textContent.trim()) return;
    if (!originalText.has(node)) originalText.set(node, node.textContent);
    const source = originalText.get(node);
    const key = source.trim();
    let next = source;
    if (lang === 'en' && translations.has(key)) {
      next = source.replace(key, translations.get(key));
    }
    if (node.textContent !== next) node.textContent = next;
  });
  if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
    if (!originalPlaceholder.has(element)) originalPlaceholder.set(element, element.placeholder);
    const source = originalPlaceholder.get(element);
    const next = lang === 'en' ? (placeholders.get(source) || source) : source;
    if (element.placeholder !== next) element.placeholder = next;
  }
}

function applyLanguage(lang = localStorage.getItem('unigraph-language') || 'zh') {
  document.documentElement.dataset.language = lang;
  document.documentElement.lang = lang === 'en' ? 'en' : 'zh-CN';
  document.querySelectorAll(`${selectors},input[placeholder],textarea[placeholder]`)
    .forEach((element) => translateElement(element, lang));
}

let queued = false;
const observer = new MutationObserver(() => {
  if (queued) return;
  queued = true;
  requestAnimationFrame(() => {
    queued = false;
    applyLanguage();
  });
});

window.addEventListener('unigraph:language-change', (event) => applyLanguage(event.detail?.lang));
window.addEventListener('DOMContentLoaded', () => {
  applyLanguage();
  observer.observe(document.body, { childList: true, subtree: true });
});

export { applyLanguage };
