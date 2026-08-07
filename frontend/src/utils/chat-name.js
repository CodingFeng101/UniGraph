export function displayChatName(name) {
  return String(name || '未命名对话').replace(/-\d{6}$/, '');
}
