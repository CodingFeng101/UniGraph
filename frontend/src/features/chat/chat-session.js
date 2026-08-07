import { displayChatName } from '@/utils/chat-name';
import { normalizeChatSources as normalizeSources } from '@/utils/chat-content';

export function createChatSessionController(context) {
  // Update the top-bar conversation title
  function setConversationTitle(title) {
    var titleEl = document.getElementById('conversation-title');
    if (!titleEl) return;
    var rawTitle = String(title || '').trim();
    var normalizedTitle = rawTitle ? displayChatName(rawTitle) : '';
    var titleWrap = document.getElementById('conversation-title-wrap');
    var shouldShow = normalizedTitle !== '' && normalizedTitle !== '新对话' && normalizedTitle !== '对话';
    if (titleWrap) titleWrap.classList.toggle('hidden', !shouldShow);
    if (titleEl.tagName === 'INPUT') {
      var span = document.createElement('span');
      span.id = 'conversation-title';
      span.className = 'text-sm font-medium truncate';
      span.style.color = 'var(--claude-foreground)';
      span.textContent = normalizedTitle;
      titleEl.replaceWith(span);
      return;
    }
    titleEl.textContent = normalizedTitle;
  }

  function renameCurrentChat() {
    if (!context.currentChatUuid) return context.notify('请先开始一段对话');
    var title = document.getElementById('conversation-title');
    if (!title || title.tagName === 'INPUT') return;
    var input = document.createElement('input');
    input.id = 'conversation-title';
    input.value = context.currentChatName || title.textContent || '';
    input.maxLength = 64;
    input.className = 'h-8 w-[260px] px-2 rounded-md text-sm outline-none';
    input.style.cssText = 'background:var(--claude-background);border:1px solid var(--claude-primary);color:var(--claude-foreground);';
    title.replaceWith(input);
    input.focus();
    input.select();
    var done = false;
    async function finish(save) {
      if (done) return;
      done = true;
      var value = input.value.trim();
      if (save && value && value !== context.currentChatName) await persistChatName(context.currentChatUuid, value);
      else setConversationTitle(context.currentChatName);
    }
    input.addEventListener('click', function(event) { event.stopPropagation(); });
    input.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') finish(true);
      if (event.key === 'Escape') finish(false);
    });
    input.addEventListener('blur', function() { finish(true); });
  }

  // Update the knowledge-graph index indicator text
  function updateGraphIndicator(graph) {
    var label = document.getElementById('kg-selector-label');
    var trigger = document.querySelector('[data-role="kg-trigger"]');
    var hasGraph = Boolean(graph);
    if (label) label.textContent = graph?.name || '暂无可用索引';
    if (trigger) {
      trigger.disabled = !hasGraph;
      trigger.title = hasGraph ? '选择知识图谱索引' : '暂无已建立索引的图谱';
      trigger.style.color = hasGraph ? 'var(--claude-foreground)' : 'var(--claude-muted-foreground)';
    }
  }

  function chatNameFromMessage(message) {
    var compact = String(message || '').replace(/\s+/g, ' ').trim();
    return compact.slice(0, 24) || '新对话';
  }

  async function ensureCurrentChat(firstMessage) {
    if (context.currentChatUuid) return context.currentChatUuid;
    context.currentChatName = chatNameFromMessage(firstMessage);
    var response = await context.api.chatLibrary.create({
      kg_base_uuid: context.kgBaseUuid,
      name: context.currentChatName + '-' + Date.now().toString().slice(-6)
    });
    if (response.code !== 200 || !response.data) {
      throw new Error(response.msg || '创建对话失败');
    }
    context.setCurrentChatUuid(response.data);
    context.syncCurrentChatQuery(context.currentChatUuid);
    return context.currentChatUuid;
  }

  async function saveConversationMessage(role, content, sources) {
    if (!context.currentChatUuid) return;
    var response = await context.api.chatLibrary.appendMessage(context.currentChatUuid, {
      role: role,
      content: content,
      knowledge_graph_uuid: context.currentGraphUuid,
      model_name: role === 'assistant' ? document.getElementById('model-value')?.textContent || null : null,
      effort: role === 'assistant' ? context.getSelectedEffort() : null,
      sources: normalizeSources(sources),
    });
    if (response.code !== 200) throw new Error(response.msg || '保存对话失败');
    return response.data;
  }

  function parseStoredMessages(messages) {
    if (Array.isArray(messages)) return messages;
    if (!messages || typeof messages !== 'object') return [];
    var parsed = [];
    Object.keys(messages).sort().forEach(function(key) {
      var item = messages[key];
      if (typeof item === 'string') {
        try {
          item = JSON.parse(item);
        } catch (error) {
          item = { ai: item };
        }
      }
      if (item.user) parsed.push({ role: 'user', content: item.user });
      if (item.ai) parsed.push({ role: 'assistant', content: item.ai });
    });
    return parsed;
  }

  // Load knowledge graph list and select the first graph
  async function loadKnowledgeGraphs() {
    if (!context.kgBaseUuid) {
      context.notify('缺少知识库 UUID');
      return;
    }
    try {
      var basesResponse = await context.api.kgBase.getAll();
      if (basesResponse.code === 200 && Array.isArray(basesResponse.data)) {
        var graphGroups = await Promise.all(basesResponse.data.map(async function(base) {
          try {
            var graphResponse = await context.api.knowledgeGraph.getAll(base.uuid);
            if (graphResponse.code !== 200 || !Array.isArray(graphResponse.data)) return [];
            return graphResponse.data
              .filter(function(graph) { return Number(graph.index_status) === 1; })
              .map(function(graph) {
                return { ...graph, kg_base_uuid: base.uuid, kg_base_name: base.name || '' };
              });
          } catch {
            return [];
          }
        }));
        context.knowledgeGraphList = graphGroups.flat();
        context.chatStore.availableIndexes = context.knowledgeGraphList;
        var selectedGraph = context.knowledgeGraphList.find(function(graph) {
          return graph.uuid === context.currentGraphUuid;
        }) || context.knowledgeGraphList.find(function(graph) {
          return graph.kg_base_uuid === context.kgBaseUuid;
        }) || context.knowledgeGraphList[0] || null;
        context.setCurrentGraphUuid(selectedGraph?.uuid || null);
        updateGraphIndicator(selectedGraph);
        renderKnowledgeGraphMenu();
      } else {
        context.notify(basesResponse.msg || '加载知识图谱失败');
      }
    } catch (err) {
      console.error('Failed to load knowledge graphs:', err);
      context.notify('加载知识图谱列表失败');
    }
  }

  function selectKnowledgeGraph() {
    if (!context.knowledgeGraphList.length) {
      context.notify('所有知识库中暂无已建立索引的图谱');
      return;
    }
    renderKnowledgeGraphMenu();
    document.getElementById('kg-selector-menu')?.classList.toggle('hidden');
  }

  function renderKnowledgeGraphMenu() {
    var menu = document.getElementById('kg-selector-menu');
    if (!menu) return;
    if (!context.knowledgeGraphList.length) {
      menu.innerHTML = '';
      menu.classList.add('hidden');
      return;
    }
    menu.innerHTML = context.knowledgeGraphList.map(function(item) {
      var active = item.uuid === context.currentGraphUuid;
      return '<button type="button" data-kg-uuid="' + context.escapeHtml(item.uuid) + '" class="claude-menu-item w-full flex flex-col items-start gap-0.5 px-2 py-2 rounded-lg text-left cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);font-weight:' +
        (active ? '600' : '400') + ';">' +
        '<span class="text-xs truncate w-full">' + context.escapeHtml(item.name || '未命名图谱') + '</span>' +
        '<span class="text-[10px] truncate w-full" style="color:var(--claude-muted-foreground);font-weight:400;">' + context.escapeHtml(item.kg_base_name || '未命名知识库') + '</span></button>';
    }).join('');
    menu.querySelectorAll('[data-kg-uuid]').forEach(function(button) {
      button.onclick = function() {
        var graph = context.knowledgeGraphList.find(function(item) { return item.uuid === button.dataset.kgUuid; });
        if (!graph) return;
        context.setCurrentGraphUuid(graph.uuid);
        updateGraphIndicator(graph);
        menu.classList.add('hidden');
      };
    });
  }

  async function loadAvailableModels() {
    var panel = document.querySelector('#more-models-panel .px-2.space-y-0\\.5');
    try {
      var response = await context.api.llm.getProviders();
      if (response.code !== 200 || !Array.isArray(response.data)) return;
      var configuredProviders = response.data.filter(function(provider) {
        return provider.status !== 0 && provider.api_key && provider.api_url;
      });
      var details = await Promise.all(configuredProviders.map(async function(provider) {
        var detail = await context.api.llm.getProviderDetail(provider.uuid);
        return detail.code === 200 ? detail.data : null;
      }));
      var models = details.filter(Boolean).flatMap(function(provider) {
        return (provider.models || []).filter(function(model) {
          return model.status !== 0 && model.type === 'llm';
        });
      });
      if (!models.length) {
        context.availableLlmModels = [];
        context.selectedLlmModelUuid = null;
        var modelTrigger = document.querySelector('[data-role="model-trigger"]');
        if (modelTrigger) modelTrigger.disabled = true;
        document.getElementById('model-value').textContent = '暂无可用模型';
        var currentModel = document.getElementById('current-model-item');
        if (currentModel) currentModel.onclick = null;
        if (panel) panel.innerHTML = '<div class="px-2.5 py-2 text-[12px]" style="color:var(--claude-muted-foreground);">请先在个人中心配置模型</div>';
        return;
      }
      modelTrigger = document.querySelector('[data-role="model-trigger"]');
      if (modelTrigger) {
        modelTrigger.disabled = false;
        modelTrigger.style.color = 'var(--claude-foreground)';
      }
      context.availableLlmModels = models;
      context.selectedLlmModelUuid = models[0].uuid;
      document.getElementById('model-value').textContent = models[0].name;
      var current = document.getElementById('current-model-item');
      if (current) current.onclick = null;
      if (current) {
        var nameElement = current.querySelector('span');
        if (nameElement) nameElement.textContent = models[0].name;
      }
      context.renderOtherModels();
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  }

  // Load chat library history and render into the sidebar
  async function loadChatHistory() {
    try {
      var responses = await Promise.all([
        context.api.kgBase.getAll(),
        context.api.chatLibrary.getAllForUser(),
      ]);
      var basesResponse = responses[0];
      var chatsResponse = responses[1];
      if (basesResponse.code !== 200) throw new Error(basesResponse.msg || '加载知识库失败');
      if (chatsResponse.code !== 200) throw new Error(chatsResponse.msg || '加载历史对话失败');
      var bases = Array.isArray(basesResponse.data) ? basesResponse.data : [];
      var fallbackBaseUuid = bases[0]?.uuid || context.kgBaseUuid;
      context.chatHistoryItems = Array.isArray(chatsResponse.data)
        ? chatsResponse.data.map(function(item) {
            return { ...item, navigation_base_uuid: fallbackBaseUuid };
          })
        : [];
      context.chatStore.replaceItems(context.chatHistoryItems);
      renderChatHistory(context.chatHistoryItems);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  }

  function toggleChatSort() {
    context.chatSortAscending = !context.chatSortAscending;
    context.chatStore.sortAscending = context.chatSortAscending;
    context.chatHistoryItems.sort(function(left, right) {
      var leftTime = new Date(left.updated_time || left.created_time || 0).getTime();
      var rightTime = new Date(right.updated_time || right.created_time || 0).getTime();
      return context.chatSortAscending ? leftTime - rightTime : rightTime - leftTime;
    });
    renderChatHistory(context.chatHistoryItems);
  }

  // Render chat history items into the sidebar
  function renderChatHistory(list) {
    if (window.ChatSidebar?.render) {
      window.ChatSidebar.render();
      return;
    }
    var sidebarContent = document.querySelector('#app-sidebar .sidebar-content');
    if (!sidebarContent) return;
    var container = sidebarContent.getElementsByClassName('space-y-0.5')[0];
    if (!container) return;
    if (!list || list.length === 0) {
      container.innerHTML = '<div class="px-3 py-2 text-[12px]" style="color:var(--claude-muted-foreground);">暂无历史对话</div>';
      renderChatSearchResults([]);
      return;
    }
    function renderRows(rows) {
      return rows.map(function(item) {
        var name = displayChatName(item.name || item.title || '未命名对话');
        var uuid = item.uuid || '';
        var isActive = uuid === context.currentChatUuid;
        var bgStyle = (isActive || item.is_favorite) ? 'style="background:var(--claude-accent);"' : '';
        var itemKgBaseUuid = item.kg_base_uuid || context.kgBaseUuid;
        var chatHref = '/unigraph/unigraphs/' + encodeURIComponent(itemKgBaseUuid) + '/qa?chat=' + encodeURIComponent(uuid);
        var chatAction = itemKgBaseUuid === context.kgBaseUuid
          ? 'href="javascript:void(0)" onclick="switchChat(\'' + context.escapeQuotes(uuid) + '\', \'' + context.escapeQuotes(name) + '\')"'
          : 'href="' + chatHref + '"';
        return '<div data-chat-uuid="' + context.escapeHtml(uuid) + '" class="group relative px-3 py-2 rounded-lg transition-colors hover:bg-[var(--claude-accent)]" ' + bgStyle + '>' +
          '<a ' + chatAction + ' class="block" style="text-decoration:none;">' +
            '<p class="text-[15px] leading-[22px] font-normal truncate pr-7" style="color:var(--claude-foreground);">' + context.escapeHtml(name) + '</p>' +
          '</a>' +
          '<button type="button" onclick="event.stopPropagation();toggleChatMenu(this)" class="absolute right-2 top-1.5 flex w-6 h-6 items-center justify-center rounded-md claude-menu-item opacity-55 group-hover:opacity-100 transition-opacity" style="background:transparent;border:none;color:var(--claude-muted-foreground);font-size:18px;line-height:1;" aria-label="对话菜单">⋮</button>' +
          '<div class="chat-context-menu hidden absolute right-2 top-8 z-50 min-w-28 rounded-xl p-1" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">' +
            '<button type="button" onclick="event.stopPropagation();renameChat(\'' + context.escapeQuotes(uuid) + '\',\'' + context.escapeQuotes(name) + '\')" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-foreground);">重命名</button>' +
            '<button type="button" onclick="event.stopPropagation();favoriteChat(\'' + context.escapeQuotes(uuid) + '\',' + (!item.is_favorite) + ')" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-foreground);">' + (item.is_favorite ? '取消收藏' : '收藏') + '</button>' +
            '<button type="button" onclick="event.stopPropagation();deleteChat(\'' + context.escapeQuotes(uuid) + '\')" class="claude-menu-item w-full px-3 py-2 rounded-lg text-xs text-left" style="background:none;border:none;color:var(--claude-destructive);">删除</button>' +
          '</div>' +
        '</div>';
      }).join('');
    }
    var starred = list.filter(function(item) { return item.is_favorite; });
    var recent = list.filter(function(item) { return !item.is_favorite; });
    var recentHeading = '<div class="flex items-center justify-between px-3 pt-4 pb-1 text-[13px] font-normal" style="color:var(--claude-muted-foreground);">' +
      '<span>Recents</span>' +
      '<button type="button" onclick="toggleChatSort()" class="w-6 h-6 flex items-center justify-center rounded-md claude-menu-item cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);" aria-label="排序">' +
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><line x1="7" y1="3" x2="7" y2="21"/><circle cx="7" cy="8" r="2"/><line x1="17" y1="3" x2="17" y2="21"/><circle cx="17" cy="16" r="2"/></svg>' +
      '</button></div>';
    container.innerHTML =
      (starred.length ? '<div class="px-3 pt-1 pb-1 text-[13px] font-normal" style="color:var(--claude-muted-foreground);">Starred</div>' + renderRows(starred) : '') +
      recentHeading + renderRows(recent);
    renderChatSearchResults(list);
  }

  function toggleChatMenu(button) {
    var menu = button.nextElementSibling;
    var shouldOpen = menu?.classList.contains('hidden');
    document.querySelectorAll('.chat-context-menu').forEach(function(element) {
      element.classList.add('hidden');
    });
    if (shouldOpen) menu?.classList.remove('hidden');
  }

  document.addEventListener('click', function(event) {
    if (event.target.closest('.chat-context-menu')) return;
    document.querySelectorAll('.chat-context-menu').forEach(function(element) {
      element.classList.add('hidden');
    });
  });

  async function favoriteChat(uuid, isFavorite) {
    try {
      var response = await context.api.chatLibrary.setFavorite(uuid, isFavorite);
      if (response.code !== 200) throw new Error(response.msg || '收藏失败');
      await loadChatHistory();
    } catch (error) {
      context.notify(error.message || '收藏失败');
    }
  }

  function renderChatSearchResults(list) {
    var container = document.querySelector('#search-modal .max-h-\\[50vh\\]');
    if (!container) return;
    if (!list.length) {
      container.innerHTML = '<div class="px-4 py-8 text-center text-sm" style="color:var(--claude-muted-foreground);">暂无历史对话</div>';
      return;
    }
    container.innerHTML = '<div class="px-2 py-2">' + list.map(function(item) {
      var name = displayChatName(item.name || item.title || '未命名对话');
      var uuid = item.uuid || '';
      var itemKgBaseUuid = item.kg_base_uuid || context.kgBaseUuid;
      var chatHref = '/unigraph/unigraphs/' + encodeURIComponent(itemKgBaseUuid) + '/qa?chat=' + encodeURIComponent(uuid);
      var chatAction = itemKgBaseUuid === context.kgBaseUuid
        ? 'href="javascript:void(0)" onclick="switchChat(\'' + context.escapeQuotes(uuid) + '\',\'' + context.escapeQuotes(name) + '\');toggleSearchModal();"'
        : 'href="' + chatHref + '"';
      return '<a ' + chatAction + ' class="chat-search-item flex items-center justify-between cursor-pointer px-3 py-2.5 rounded-lg transition-colors hover:opacity-80" style="text-decoration:none;">' +
        '<span class="text-sm" style="color:var(--claude-foreground);">' + context.escapeHtml(name) + '</span>' +
        '<span class="text-xs" style="color:var(--claude-muted-foreground);">' + context.escapeHtml(item.updated_time || item.created_time || '') + '</span>' +
        '</a>';
    }).join('') + '</div>';
  }

  async function renameChat(uuid, oldName) {
    var row = document.querySelector('[data-chat-uuid="' + CSS.escape(uuid) + '"]');
    var title = row?.querySelector('p');
    if (!title) return;
    var input = document.createElement('input');
    input.type = 'text';
    input.value = oldName || '';
    input.maxLength = 64;
    input.style.cssText = 'width:100%;height:34px;padding:0 8px;border:1px solid #2f6feb;border-radius:7px;background:var(--claude-background);color:var(--claude-foreground);font-size:15px;outline:none;';
    title.replaceWith(input);
    input.focus();
    input.select();
    var finished = false;
    async function finish(save) {
      if (finished) return;
      finished = true;
      var name = input.value.trim();
      var displayName = save && name ? name : oldName;
      var title = document.createElement('p');
      title.className = 'text-[15px] leading-[22px] font-normal truncate pr-7';
      title.style.color = 'var(--claude-foreground)';
      title.textContent = displayName;
      input.replaceWith(title);
      if (!save || !name || name === oldName) {
        return;
      }
      await persistChatName(uuid, name);
    }
    input.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        finish(true);
      }
      if (event.key === 'Escape') {
        event.preventDefault();
        finish(false);
      }
    });
    input.addEventListener('blur', function() { finish(true); });
  }

  async function persistChatName(uuid, name) {
    try {
      var detail = await context.api.chatLibrary.getDetail(uuid);
      if (detail.code !== 200 || !detail.data) throw new Error(detail.msg || '加载对话失败');
      var response = await context.api.chatLibrary.update(uuid, {
        kg_base_uuid: detail.data.kg_base_uuid || context.kgBaseUuid,
        name: name,
        messages: detail.data.messages || {}
      });
      if (response.code !== 200) throw new Error(response.msg || '重命名失败');
      if (context.currentChatUuid === uuid) {
        context.currentChatName = name;
        setConversationTitle(name);
      }
      await loadChatHistory();
    } catch (error) {
      context.notify(error.message || '重命名失败');
    }
  }

  async function deleteChat(uuid) {
    if (!uuid || !await window.confirmAction({
      title: '删除对话',
      message: '确定要删除这段对话吗？',
      confirmText: '删除',
    })) return;
    try {
      var response = await context.api.chatLibrary.delete(uuid);
      if (response.code !== 200) throw new Error(response.msg || '删除对话失败');
      if (context.currentChatUuid === uuid) {
        context.setCurrentChatUuid(null);
        context.currentChatName = '新对话';
        context.clearChatContainer();
        context.renderEmptyState();
        context.syncCurrentChatQuery(null);
        setConversationTitle('新对话');
      }
      await loadChatHistory();
      context.notify('对话已删除');
    } catch (error) {
      context.notify(error.message || '删除对话失败');
    }
  }

  // Switch to a historical conversation
  async function switchChat(chatUuid, name) {
    if (!chatUuid) return;
    context.resetRecoveredAskState();
    context.setCurrentChatUuid(chatUuid);
    context.syncCurrentChatQuery(chatUuid);
    context.currentChatName = displayChatName(name || '对话');
    setConversationTitle(context.currentChatName);
    context.clearChatContainer();
    context.setChatMode(false);
    var loadedMessages = 0;
    try {
      var res = await context.api.chatLibrary.getDetail(chatUuid);
      if (res.code === 200 && res.data) {
        var messages = Array.isArray(res.data.conversation) && res.data.conversation.length
          ? res.data.conversation
          : parseStoredMessages(res.data.messages || res.data.chats || res.data.history || []);
        context.resetRecoveredAskState();
        context.setAnsweredMessageUuids(messages.reduce(function(answered, message, index) {
          var role = message.role || message.type || (message.is_user ? 'user' : 'assistant');
          if ((role === 'user' || role === 'human') && message.uuid) {
            var nextMessage = messages[index + 1];
            var nextRole = nextMessage && (nextMessage.role || nextMessage.type || (nextMessage.is_user ? 'user' : 'assistant'));
            if (nextMessage && nextRole !== 'user' && nextRole !== 'human') answered.push(message.uuid);
          }
          return answered;
        }, []));
        if (messages.length > 0) {
          loadedMessages = messages.length;
          messages.forEach(function(msg) {
            var role = msg.role || msg.type || (msg.is_user ? 'user' : 'assistant');
            var content = msg.content || msg.message || msg.answer || '';
            if (role === 'user' || role === 'human') {
              context.appendUserMessage(content, msg.uuid);
            } else {
              var sources = {};
              if (Array.isArray(msg.sources)) {
                msg.sources.forEach(function(source) {
                  sources[source.source_type] = source.content;
                });
              } else {
                sources = normalizeSources(msg.sources);
              }
              context.appendAIMessage(content, sources);
            }
          });
        }
      }
    } catch (err) {
      console.error('Failed to load chat detail:', err);
      context.notify('加载对话失败');
    }
    if (!loadedMessages) context.renderEmptyState();
    context.resumeActiveAskForCurrentChat();
    loadChatHistory();
  }

  return {
    deleteChat,
    ensureCurrentChat,
    favoriteChat,
    loadAvailableModels,
    loadChatHistory,
    loadKnowledgeGraphs,
    persistChatName,
    renameChat,
    renameCurrentChat,
    renderChatHistory,
    renderChatSearchResults,
    saveConversationMessage,
    selectKnowledgeGraph,
    setConversationTitle,
    switchChat,
    toggleChatMenu,
    toggleChatSort,
  };
}
