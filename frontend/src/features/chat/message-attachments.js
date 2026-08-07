export function parseMessageAttachments(text) {
  const source = String(text || '');
  const marker = source.match(/(?:^|\n)附件[：:]\s*\n/);
  if (!marker || marker.index == null) return { body: source.trim(), attachments: [] };
  const body = source.slice(0, marker.index).trim();
  const attachmentBlock = source.slice(marker.index + marker[0].length);
  const attachments = attachmentBlock.split('\n').map((line) => {
    const match = line.trim().match(/^-\s+(.+?):\s+(\S+)\s*$/);
    if (!match) return null;
    const name = match[1].trim();
    return {
      name,
      url: match[2].trim(),
      extension: (name.split('.').pop() || 'FILE').toUpperCase(),
    };
  }).filter(Boolean);
  return { body, attachments };
}

export function composeMessageText(body, attachments) {
  const attachmentText = (attachments || []).map((attachment) => (
    `- ${attachment.name}: ${attachment.url}`
  )).join('\n');
  return body + (attachmentText ? `${body ? '\n\n' : ''}附件：\n${attachmentText}` : '');
}
