import { validateUploadFiles } from '@/utils/upload';

export function createSchemaDocumentController(context) {
  let pendingUpdatePaths = [];
  const currentUuid = () => context.getCurrentSchemaUuid();
  const currentData = () => context.getCurrentSchemaData() || {};

  function parseJsonObject(value, fallback) {
    if (!value) return fallback;
    if (typeof value === 'object') return value;
    try { return JSON.parse(value); } catch { return fallback; }
  }

  function appendSuggestionInput(group, value) {
    if (!group) return;
    const wrapper = document.createElement('span');
    wrapper.className = 'inline-flex items-center gap-1 px-2 py-1 rounded-md';
    wrapper.style.cssText = 'background:var(--claude-secondary);border:1px solid var(--claude-border);';
    const input = document.createElement('input');
    input.type = 'text';
    input.value = value || '';
    input.className = 'w-24 bg-transparent border-none outline-none text-[11px]';
    input.style.color = 'var(--claude-foreground)';
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.textContent = '×';
    remove.className = 'cursor-pointer';
    remove.style.cssText = 'background:none;border:none;color:var(--claude-muted-foreground);';
    remove.onclick = () => wrapper.remove();
    wrapper.append(input, remove);
    group.appendChild(wrapper);
  }

  function populateArchSuggestionForm(detail) {
    const modal = document.getElementById('modal-update-arch');
    if (!modal) return;
    const modifyInfo = parseJsonObject(detail.modify_info, {});
    const groups = modal.querySelectorAll('.flex.flex-wrap.gap-1\\.5');
    const values = [
      modifyInfo.add_entity || modifyInfo.expected_entity_types || [],
      modifyInfo.del_entity || modifyInfo.unexpected_entity_types || [],
    ];
    groups.forEach((group, index) => {
      group.innerHTML = '';
      (values[index] || []).forEach((value) => appendSuggestionInput(group, value));
    });
    const textarea = modal.querySelector('textarea');
    if (textarea) textarea.value = detail.modify_suggestion || '';
  }

  function addSuggestionTag(groupIndex) {
    const modal = document.getElementById('modal-update-arch');
    const groups = modal ? modal.querySelectorAll('.flex.flex-wrap.gap-1\\.5') : [];
    appendSuggestionInput(groups[groupIndex], '');
    groups[groupIndex]?.querySelector('span:last-child input')?.focus();
  }

  function collectSuggestionInfo() {
    const modal = document.getElementById('modal-update-arch');
    const groups = modal ? modal.querySelectorAll('.flex.flex-wrap.gap-1\\.5') : [];
    const collect = (group) => Array.from(group?.querySelectorAll('input[type="text"]') || [])
      .map((input) => input.value.trim()).filter(Boolean);
    return { add_entity: collect(groups[0]), del_entity: collect(groups[1]) };
  }

  async function generateSuggestion() {
    const uuid = currentUuid();
    if (!uuid) return context.notify('请先选择知识架构');
    try {
      const task = await context.TaskManager.submit(
        'schema_graph.update_schema_graph_suggestion', '生成架构建议', currentData().name || uuid,
        { uuid, user_token: context.Auth.getToken() },
      );
      await task.completion;
      await context.loadSchemaDetail(uuid);
    } catch (error) { context.notify(error.message || '生成建议失败'); }
  }

  async function saveArchSuggestion() {
    const uuid = currentUuid();
    if (!uuid) return context.notify('请先选择知识架构');
    const modal = document.getElementById('modal-update-arch');
    const textarea = modal?.querySelector('textarea');
    try {
      const response = await context.KgBaseAPI.schemaGraph.updateDetail(uuid, {
        modify_info: JSON.stringify(collectSuggestionInfo()),
        modify_suggestion: textarea?.value || '',
      });
      if (response.code !== 200) throw new Error(response.msg || '保存失败');
      modal?.classList.add('hidden');
      await context.loadSchemaDetail(uuid);
      context.notify('已保存');
    } catch (error) { context.notify(error.message || '保存失败'); }
  }

  async function uploadFiles(files) {
    validateUploadFiles(files);
    const paths = [];
    for (const file of files) {
      const response = await context.API.uploadFile(file);
      if (response.code !== 200 || !response.data?.url) throw new Error(response.msg || '文件上传失败');
      paths.push(response.data.url);
    }
    return paths;
  }

  function triggerCreateArchFiles() { document.getElementById('create-arch-files')?.click(); }

  function handleCreateArchFiles(input) {
    const label = document.getElementById('create-arch-files-label');
    if (label) label.textContent = input.files?.length
      ? Array.from(input.files).map((file) => file.name).join('、') : '上传 PDF / Word / TXT 文档';
  }

  async function submitCreateArch() {
    if (document.getElementById('modal-new-arch')?.getAttribute('data-create-mode') === 'json') {
      return handleImportArchFile(document.getElementById('import-arch-file'), true);
    }
    const input = document.getElementById('create-arch-files');
    const name = document.getElementById('create-arch-name')?.value.trim() || '';
    const aim = document.getElementById('create-arch-aim')?.value.trim() || '';
    if (!name) return context.notify('请输入架构名称');
    if (!input.files?.length) return context.notify('请上传构建文档');
    try {
      const filePaths = await uploadFiles(input.files);
      document.getElementById('modal-new-arch')?.classList.add('hidden');
      const task = await context.TaskManager.submit('schema_graph.create_schema_graph', '创建知识架构', name, {
        user_token: context.Auth.getToken(),
        obj_data: { file_paths: filePaths, data: { kg_base_uuid: context.getKgBaseUuid(), name, aim } },
      });
      await task.completion;
      await context.loadSchemaGraphs({ name });
    } catch (error) {
      context.notify(error.message || '创建知识架构失败');
    } finally {
      input.value = '';
      handleCreateArchFiles(input);
    }
  }

  function triggerImportArchFile() { document.getElementById('import-arch-file')?.click(); }

  async function handleImportArchFile(input, shouldSubmit) {
    if (!input.files?.length) return;
    const label = document.getElementById('import-arch-file-label');
    if (label) label.textContent = input.files[0].name;
    if (!shouldSubmit) return;
    try {
      const filePaths = await uploadFiles(input.files);
      const response = await context.KgBaseAPI.schemaGraph.import({
        file_paths: filePaths,
        data: {
          kg_base_uuid: context.getKgBaseUuid(), name: input.files[0].name.replace(/\.json$/i, ''),
          aim: '', modify_info: '', modify_suggestion: '',
        },
      });
      if (response.code !== 200) throw new Error(response.msg || '导入知识架构失败');
      document.getElementById('modal-new-arch')?.classList.add('hidden');
      await context.loadSchemaGraphs();
      context.notify('知识架构已导入');
    } catch (error) {
      context.notify(error.message || '导入知识架构失败');
    } finally {
      input.value = '';
      if (label) label.textContent = '选择 JSON 文件';
    }
  }

  function renderArchFileList(files, status) {
    const list = document.getElementById('arch-file-list');
    if (!list) return;
    list.innerHTML = '';
    list.classList.toggle('hidden', !files.length);
    files.forEach((file) => {
      const item = document.createElement('div');
      item.className = 'flex items-center justify-between gap-3 px-3 py-2 rounded-lg text-xs';
      item.style.cssText = 'background:var(--claude-background);border:1px solid var(--claude-border);color:var(--claude-foreground);';
      const name = document.createElement('span');
      name.className = 'min-w-0 truncate';
      name.textContent = file.name;
      const state = document.createElement('span');
      state.className = 'shrink-0 text-[10px]';
      state.style.color = 'var(--claude-muted-foreground)';
      state.textContent = status === 'uploaded' ? '已上传' : '上传中...';
      item.append(name, state);
      list.appendChild(item);
    });
  }

  async function uploadArchFiles(files) {
    if (!files?.length) return;
    const selected = Array.from(files);
    renderArchFileList(selected, 'uploading');
    try {
      pendingUpdatePaths = await uploadFiles(selected);
      renderArchFileList(selected, 'uploaded');
      context.notify(`已上传 ${pendingUpdatePaths.length} 个文件`);
    } catch (error) {
      pendingUpdatePaths = [];
      renderArchFileList([], '');
      context.notify(error.message || '文件上传失败');
    }
  }

  async function submitArchUpdate() {
    const uuid = currentUuid();
    if (!uuid) return context.notify('请先选择知识架构');
    if (!pendingUpdatePaths.length) return context.notify('请先上传更新文档');
    const modal = document.getElementById('modal-update-arch');
    const textarea = modal?.querySelector('textarea');
    try {
      const task = await context.TaskManager.submit('schema_graph.update_schema_graph', '更新知识架构', currentData().name || uuid, {
        uuid,
        user_token: context.Auth.getToken(),
        obj_data: {
          file_paths: pendingUpdatePaths,
          data: { modify_suggestion: textarea?.value || '', modify_info: JSON.stringify(collectSuggestionInfo()) },
        },
      });
      modal?.classList.add('hidden');
      pendingUpdatePaths = [];
      renderArchFileList([], '');
      const fileInput = document.getElementById('arch-file-input');
      if (fileInput) fileInput.value = '';
      await task.completion;
      await context.loadSchemaDetail(uuid);
    } catch (error) { context.notify(error.message || '更新知识架构失败'); }
  }

  return {
    addSuggestionTag, generateSuggestion, handleCreateArchFiles, handleImportArchFile,
    populateArchSuggestionForm, saveArchSuggestion, submitArchUpdate, submitCreateArch,
    triggerCreateArchFiles, triggerImportArchFile, uploadArchFiles,
  };
}
