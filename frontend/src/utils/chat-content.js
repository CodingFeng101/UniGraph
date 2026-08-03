import DOMPurify from 'dompurify';
import MarkdownIt from 'markdown-it';

const markdown = new MarkdownIt({ breaks: true, linkify: true });

const sourceLabels = {
  Reports: '整体知识概览',
  Sources: '具体信息来源',
  Relationships: '相关知识关联',
  Entities: '重点知识细节',
};

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[character]);
}

export function renderChatMarkdown(text) {
  if (text == null || text === '') return '';
  try {
    return DOMPurify.sanitize(markdown.render(String(text)));
  } catch {
    return escapeHtml(text).replace(/\n/g, '<br>');
  }
}

export function normalizeChatSources(sources) {
  const input = Array.isArray(sources)
    ? sources.reduce((result, source) => {
        if (source?.source_type) result[source.source_type] = source.content;
        return result;
      }, {})
    : (sources && typeof sources === 'object' ? sources : {});
  return {
    Reports: input.Reports != null ? input.Reports : (input.Communities || []),
    Sources: input.Sources || [],
    Relationships: input.Relationships || [],
    Entities: input.Entities || [],
  };
}

function parseSourceContent(content) {
  if (typeof content !== 'string') return content;
  try {
    return JSON.parse(content);
  } catch {
    return content;
  }
}

function sourceRecords(content) {
  const parsed = parseSourceContent(content);
  if (Array.isArray(parsed)) return parsed;
  if (!parsed || typeof parsed !== 'object') return [];

  const columns = Object.keys(parsed);
  if (!columns.length) return [];
  const knownColumns = ['id', 'text', 'entity_type', 'entity_name', 'name', 'source', 'target'];
  const isColumnOriented = columns.some((column) => knownColumns.includes(column));
  if (!isColumnOriented && columns.every((key) => parsed[key] && typeof parsed[key] === 'object' && !Array.isArray(parsed[key]))) {
    return columns.map((key) => ({ ...parsed[key], id: parsed[key].id ?? key }));
  }
  const rowKeys = new Set();
  columns.forEach((column) => {
    const values = parsed[column];
    if (values && typeof values === 'object' && !Array.isArray(values)) {
      Object.keys(values).forEach((key) => rowKeys.add(key));
    }
  });
  if (!rowKeys.size) return [parsed];
  return Array.from(rowKeys).map((rowKey) => {
    const row = { id: rowKey };
    columns.forEach((column) => {
      const values = parsed[column];
      row[column] = values && typeof values === 'object' ? values[rowKey] : values;
    });
    return row;
  });
}

function findSourceRecord(sources, type, recordId) {
  const normalizedId = String(recordId ?? '').trim();
  return sourceRecords(sources[type]).find((record) => String(record?.id ?? '').trim() === normalizedId);
}

function sourceRecordFields(type, record) {
  if (!record) return [['记录状态', '未在本次检索上下文中找到对应记录']];
  if (type === 'Relationships') {
    return [
      ['关系', record.name],
      ['起点实体', record.source],
      ['终点实体', record.target],
    ].filter((field) => field[1] != null && String(field[1]).trim() !== '');
  }
  if (type === 'Entities') {
    return [
      ['实体类型', record.entity_type],
      ['实体名称', record.entity_name],
      ['知识属性', record.text],
    ].filter((field) => field[1] != null && String(field[1]).trim() !== '');
  }
  return [['原文片段', record.text || '该记录没有可展示的文本片段']];
}

function overviewSections(record) {
  const text = String(record?.text || '该记录没有可展示的概览内容').trim();
  const sections = [];
  let current = null;
  text.split(/\r?\n/).forEach((line) => {
    const match = line.match(/^\s*(社区名称|社区摘要|详细摘要(?:[（(]\d+[）)])?|摘要说明(?:[（(]\d+[）)])?)\s*[:：]\s*(.*)$/);
    if (match) {
      current = { label: match[1], value: match[2].trim() };
      sections.push(current);
      return;
    }
    if (!line.trim()) {
      if (current?.value && !current.value.endsWith('\n')) current.value += '\n';
      return;
    }
    if (!current) {
      current = { label: '概览补充', value: line.trim() };
      sections.push(current);
      return;
    }
    current.value += (current.value.endsWith('\n') ? '' : ' ') + line.trim();
  });
  return sections.length ? sections : [{ label: '概览摘要', value: text }];
}

function renderOverviewText(value) {
  return String(value || '').split(/\n+/).map((paragraph) => paragraph.trim()).filter(Boolean)
    .map((paragraph) => '<span class="source-popup-overview__paragraph">' + escapeHtml(paragraph) + '</span>')
    .join('');
}

function renderOverviewRecord(record, index, showIndex) {
  if (!record) {
    return '<span class="source-popup-record source-popup-overview-record"><span class="source-popup-field__value">未在本次检索上下文中找到对应记录</span></span>';
  }
  const sections = overviewSections(record);
  const nameSection = sections.find((section) => section.label === '社区名称');
  const contentSections = sections.filter((section) => section !== nameSection);
  return '<span class="source-popup-record source-popup-overview-record">' +
    (showIndex ? '<span class="source-popup-overview__index">概览 ' + (index + 1) + '</span>' : '') +
    (nameSection ? '<span class="source-popup-overview__heading">' + escapeHtml(nameSection.value) + '</span>' : '') +
    '<span class="source-popup-overview__sections">' + contentSections.map((section) =>
      '<span class="source-popup-overview__section' + (section.label === '社区摘要' ? ' is-summary' : '') + '">' +
      '<span class="source-popup-overview__label">' + escapeHtml(section.label) + '</span>' +
      '<span class="source-popup-overview__text">' + renderOverviewText(section.value) + '</span></span>').join('') +
    '</span></span>';
}

function renderCitationBadge(type, recordIds, sources) {
  const label = sourceLabels[type];
  const ids = Array.isArray(recordIds) ? recordIds : [recordIds];
  const records = ids.map((recordId, index) => {
    const record = findSourceRecord(sources, type, recordId);
    if (type === 'Reports') return renderOverviewRecord(record, index, ids.length > 1);
    const fields = sourceRecordFields(type, record).map((field) =>
      '<span class="source-popup-field"><span class="source-popup-field__label">' + escapeHtml(field[0]) + '</span>' +
      '<span class="source-popup-field__value">' + escapeHtml(field[1]) + '</span></span>').join('');
    return '<span class="source-popup-record">' +
      (ids.length > 1 ? '<span class="source-popup-record__id">#' + escapeHtml(recordId) + '</span>' : '') +
      '<span class="source-popup-fields">' + fields + '</span></span>';
  }).join('');
  const hasRecord = ids.some((recordId) => findSourceRecord(sources, type, recordId));
  const summary = ids.length > 1 ? `${ids.length} 条` : `#${ids[0]}`;
  const typeClass = type === 'Reports' ? ' citation-tag--overview' : '';
  return '<button type="button" class="source-tag citation-tag' + typeClass + (hasRecord ? '' : ' is-missing') + '" data-citation data-source-type="' +
    escapeHtml(type) + '" aria-expanded="false" aria-label="查看引用 ' +
    escapeHtml(`${label}，${ids.length} 条`) + '"><span class="citation-tag__label">' + escapeHtml(label) + '</span>' +
    '<span class="source-popup" role="tooltip" popover="manual"><span class="source-popup-title"><span>' + escapeHtml(label) +
    '</span><span class="source-popup-id">' + escapeHtml(summary) + '</span></span><span class="source-popup-records">' + records +
    '</span></span></button>';
}

export function renderAnswerWithCitations(text, rawSources) {
  if (text == null || text === '') return '';
  const sources = normalizeChatSources(rawSources);
  const citations = [];
  const prepared = String(text).replace(/(?:\[|【)Data\s*[:：]\s*([^】\]]+)(?:\]|】)/gi, (original, citationBody) => {
    const groups = [];
    const groupPattern = /(Reports|Sources|Relationships|Entities|Communities)\s*[(（]([^）)]+)[)）]/gi;
    let match;
    while ((match = groupPattern.exec(String(citationBody))) !== null) {
      const canonicalType = match[1].toLowerCase() === 'communities'
        ? 'Reports'
        : Object.keys(sourceLabels).find((type) => type.toLowerCase() === match[1].toLowerCase());
      if (!canonicalType) continue;
      const recordIds = match[2].split(/[,，、]/).map((id) => id.trim()).filter(Boolean);
      if (!recordIds.length) continue;
      const previousGroup = groups[groups.length - 1];
      if (previousGroup?.type === canonicalType) previousGroup.recordIds.push(...recordIds);
      else groups.push({ type: canonicalType, recordIds });
    }
    if (!groups.length) return original;
    const badges = groups.map((group) => renderCitationBadge(group.type, group.recordIds, sources));
    const placeholder = `@@UNIGRAPH_CITATION_${citations.length}@@`;
    citations.push('<span class="citation-group" aria-label="信息来源">' + badges.join('') + '</span>');
    return placeholder;
  });
  let rendered = renderChatMarkdown(prepared);
  citations.forEach((citation, index) => {
    rendered = rendered.replace(`@@UNIGRAPH_CITATION_${index}@@`, citation);
  });
  return rendered;
}
