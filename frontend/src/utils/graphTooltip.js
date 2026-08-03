function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function getTooltipKind(type) {
  const label = String(type || '');
  if (label.includes('关系类型')) return '关系类型';
  if (label.includes('关系')) return '关系';
  if (label.includes('实体类型')) return '实体类型';
  return '实体';
}

function getPlainLines(bodyHtml) {
  const container = document.createElement('div');
  container.innerHTML = String(bodyHtml || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n');
  return (container.textContent || '')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}

function parseLine(line) {
  const separatorIndex = line.search(/[:：=]/);
  if (separatorIndex < 0) {
    if (line.includes('→')) return { key: '实体', value: line };
    return { key: '信息', value: line };
  }
  return {
    key: line.slice(0, separatorIndex).trim(),
    value: line.slice(separatorIndex + 1).trim(),
  };
}

function normalizeRows(bodyHtml, kind) {
  const rows = getPlainLines(bodyHtml).map(parseLine);
  const isRelationship = kind.includes('关系');
  const fixedKeys = isRelationship
    ? new Set(['实体', '起始', '头实体', '目标', '尾实体', '类型', '来源', '描述', '定义'])
    : new Set(['属性', '来源', '关联关系']);
  const result = [];

  rows.forEach((row) => {
    if (!fixedKeys.has(row.key)) {
      result.push(row);
      return;
    }
    const keyMap = { '起始': '头实体', '目标': '尾实体', '描述': '定义' };
    result.push({ key: keyMap[row.key] || row.key, value: row.value });
  });

  return result.slice(0, 5);
}

export function renderGraphTooltipContent(title, type, bodyHtml) {
  const kind = getTooltipKind(type);
  const titleElement = document.getElementById('tooltip-title');
  const typeElement = document.getElementById('tooltip-type');
  const badgeElement = document.getElementById('tooltip-badge');
  const bodyElement = document.getElementById('tooltip-body');
  if (!titleElement || !typeElement || !badgeElement || !bodyElement) return;

  titleElement.textContent = title || '';
  typeElement.textContent = String(type || '').replace(/\s*\((?:实体|关系)\)\s*$/, '') || kind;
  badgeElement.textContent = kind;
  bodyElement.innerHTML = normalizeRows(bodyHtml, kind).map((row) => (
    '<div class="graph-hover-card__row">' +
      '<span class="graph-hover-card__key">' + escapeHtml(row.key) + '</span>' +
      '<span class="graph-hover-card__value">' + escapeHtml(row.value || '—') + '</span>' +
    '</div>'
  )).join('');
}
