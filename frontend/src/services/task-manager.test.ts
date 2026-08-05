import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it } from 'vitest';

const source = readFileSync(resolve(process.cwd(), 'src/services/task-manager.js'), 'utf8');

describe('task submission security boundary', () => {
  it('sends the complete payload but persists only a sanitized copy', () => {
    expect(source).toContain('KgBaseAPI.task.submit(name, kwargs || {})');
    expect(source).toContain("requiresUserToken = Object.prototype.hasOwnProperty.call(kwargs || {}, 'user_token')");
    expect(source).toContain('if (task.requiresUserToken) retryKwargs.user_token = Auth.getToken()');
    expect(source).toContain('taskStore.persist((task) => ({ ...task, kwargs: sanitizeKwargs(task.kwargs) }))');
    expect(source).toContain('delete safe.user_token');
  });
});

describe('task completion notifications', () => {
  it('only shows the completion toast once', () => {
    expect(source).toContain('if (task.completionNotified) return false');
    expect(source).toContain('if (notifyCompletion(task)) notify(');
  });

  it('does not resume private tasks on a public shared-chat page', () => {
    expect(source).toContain("return /\\/share\\/[^/]+\\/?$/.test(window.location.pathname)");
    expect(source).toContain('Auth.isLogin() && !isSharedChatPage()');
  });
});

describe('stale question tasks', () => {
  it('does not keep a conversation locked after a question stops progressing', () => {
    expect(source).toContain('const QUESTION_STALE_MS = 15 * 60 * 1000');
    expect(source).toContain("task?.name !== 'knowledge_graph.ask'");
    expect(source).toContain('!isQuestionTaskStale(task)');
  });
});
