import { copyText } from '@/utils/clipboard';

let mermaidModulePromise;
let diagramSequence = 0;

function codeLanguage(code) {
  const languageClass = Array.from(code.classList).find((name) => name.startsWith('language-'));
  return languageClass ? languageClass.slice('language-'.length) : 'code';
}

function addCopyButton(container, content, label = '复制') {
  if (container.querySelector(':scope > .chat-content-copy')) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'chat-content-copy';
  button.textContent = label;
  button.setAttribute('aria-label', label);
  button.addEventListener('click', async () => {
    await copyText(content());
    button.textContent = '已复制';
    window.setTimeout(() => { button.textContent = label; }, 1200);
  });
  container.appendChild(button);
}

async function renderMermaidDiagram(element) {
  if (['rendering', 'complete'].includes(element.dataset.mermaidState)) return;
  const source = decodeURIComponent(element.dataset.mermaidSource || '');
  if (!source.trim()) return;
  element.dataset.mermaidState = 'rendering';
  try {
    mermaidModulePromise ||= import('mermaid/dist/mermaid.core.mjs').then(({ default: mermaid }) => {
      mermaid.initialize({ startOnLoad: false, securityLevel: 'strict', theme: 'neutral' });
      return mermaid;
    });
    const mermaid = await mermaidModulePromise;
    const { svg } = await mermaid.render(`unigraph-mermaid-${++diagramSequence}`, source);
    if (!element.isConnected) return;
    element.innerHTML = `<div class="chat-mermaid__canvas">${svg}</div>`;
    element.dataset.mermaidState = 'complete';
  } catch {
    if (!element.isConnected) return;
    element.dataset.mermaidState = 'error';
    element.innerHTML = '<pre class="chat-mermaid__source"><code></code></pre>';
    element.querySelector('code').textContent = source;
  }
  addCopyButton(element, () => source, '复制源码');
}

export function enhanceChatContent(root) {
  if (!root) return;
  root.querySelectorAll('.chat-code-block').forEach((block) => {
    const code = block.querySelector('code');
    if (!code) return;
    block.dataset.language = codeLanguage(code);
    addCopyButton(block, () => code.textContent || '');
  });
  root.querySelectorAll('.chat-mermaid').forEach(renderMermaidDiagram);
}
