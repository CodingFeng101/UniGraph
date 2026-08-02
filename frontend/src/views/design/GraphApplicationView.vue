<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="app" />

<div id="app-main" class="h-screen min-h-0 flex flex-col transition-all duration-300" style="margin-left:260px;">
  <div class="shrink-0 h-11 flex items-center px-6 justify-between">
    <div id="conversation-title-wrap" class="hidden flex items-center gap-1.5 cursor-pointer sidebar-collapsed-hide" style="max-width:300px;" @click="renameCurrentChat()" title="点击重命名">
      <span id="conversation-title" class="text-sm font-medium truncate" style="color:var(--claude-foreground);">新对话</span>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-muted-foreground);flex-shrink:0;"><polyline points="9 18 15 12 9 6"/></svg>
    </div>
    <button type="button" data-role="share-trigger" @click="toggleShareModal()" class="w-8 h-8 flex items-center justify-center rounded-lg cursor-pointer transition-colors hover:opacity-70" style="background:transparent;border:none;color:var(--claude-muted-foreground);" aria-label="分享对话">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
    </button>
  </div>

  <div class="flex-1 overflow-y-auto overflow-x-hidden" id="chat-container">
    <div id="chat-message-list" class="max-w-[680px] mx-auto px-8 py-6 space-y-6" style="visibility:hidden;">
      <div class="group">
        <div class="flex justify-end">
          <div class="max-w-[480px]">
            <div class="px-5 py-3 rounded-2xl" style="background:var(--claude-secondary);">
              <p class="text-[15px] leading-relaxed" style="color:var(--claude-foreground);">张磊负责了哪些项目？他与哪些部门有关联？</p>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-1 mt-1.5 opacity-0 transition-opacity duration-150 group-hover:opacity-100">
          <span class="text-[11px] mr-1.5" style="color:var(--claude-muted-foreground);">14:32</span>
          <button type="button" @click="copyMessage($event.currentTarget)" class="w-7 h-7 flex items-center justify-center rounded-md transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="复制">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </button>
          <button type="button" @click="showToast('编辑消息')" class="w-7 h-7 flex items-center justify-center rounded-md transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="编辑">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
        </div>
      </div>

      <div class="group">
        <div class="max-w-[680px] w-full">
          <div class="trace-section mb-1" style="">
            <button type="button" class="trace-toggle w-full flex items-center gap-2 px-0 py-1 text-left cursor-pointer" style="background:transparent;color:var(--claude-muted-foreground);border:none;" aria-expanded="true">
              <svg class="chevron-icon shrink-0" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="transform: rotate(180deg);"><polyline points="6 9 12 15 18 9"/></svg>
              <span class="text-[12px] font-medium" style="color:var(--claude-muted-foreground);">思考过程</span>
              <span class="text-[10px] ml-auto shrink-0 px-1.5 py-0.5 rounded-full" style="background:var(--claude-muted);color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">7/8</span>
            </button>
            <div class="trace-body pl-0 pr-0 pb-1 pt-1" style="max-height:800px;opacity:1;">
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5" style="background:var(--claude-success-500);">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary-foreground)" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  </div>
                  <div class="w-px flex-1 mt-1" style="background:var(--claude-border);"></div>
                </div>
                <div class="pb-3 flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <span class="text-xs" style="color:var(--claude-foreground);">解析查询</span>
                    <span class="text-[10px] shrink-0" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">09:45:12</span>
                  </div>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5" style="background:var(--claude-success-500);">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary-foreground)" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  </div>
                  <div class="w-px flex-1 mt-1" style="background:var(--claude-border);"></div>
                </div>
                <div class="pb-3 flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <span class="text-xs" style="color:var(--claude-foreground);">载入索引</span>
                    <span class="text-[10px] shrink-0" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">09:45:13</span>
                  </div>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5" style="background:var(--claude-success-500);">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary-foreground)" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  </div>
                  <div class="w-px flex-1 mt-1" style="background:var(--claude-border);"></div>
                </div>
                <div class="pb-3 flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <button type="button" class="trace-toggle flex items-center gap-1 text-xs cursor-pointer" style="color:var(--claude-foreground);background:none;border:none;padding:0;" aria-expanded="true">
                      <svg class="chevron-icon" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="transform: rotate(180deg);"><polyline points="6 9 12 15 18 9"/></svg>
                      召回实体
                    </button>
                    <span class="text-[10px] shrink-0" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">09:45:13</span>
                  </div>
                  <div class="step-detail mt-1.5 px-3 py-2 rounded-lg text-[11px] leading-relaxed" style="max-height:60px;opacity:1;background:var(--claude-card);color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);border:1px solid var(--claude-border);">
                    召回 12 个实体, 8 个关系
                  </div>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5" style="background:var(--claude-success-500);">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary-foreground)" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  </div>
                  <div class="w-px flex-1 mt-1" style="background:var(--claude-border);"></div>
                </div>
                <div class="pb-3 flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <button type="button" class="trace-toggle flex items-center gap-1 text-xs cursor-pointer" style="color:var(--claude-foreground);background:none;border:none;padding:0;" aria-expanded="true">
                      <svg class="chevron-icon" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="transform: rotate(180deg);"><polyline points="6 9 12 15 18 9"/></svg>
                      构建上下文
                    </button>
                    <span class="text-[10px] shrink-0" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">09:45:15</span>
                  </div>
                  <div class="step-detail mt-1.5 px-3 py-2 rounded-lg text-[11px] leading-relaxed" style="max-height:60px;opacity:1;background:var(--claude-card);color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);border:1px solid var(--claude-border);">
                    上下文窗口: 2048 tokens | 实体: Person_001, Project_012, Project_045, Department_003 | 关系路径: 6条
                  </div>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5" style="background:var(--claude-success-500);">
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary-foreground)" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
                  </div>
                  <div class="w-px flex-1 mt-1" style="background:var(--claude-border);"></div>
                </div>
                <div class="pb-3 flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <button type="button" class="trace-toggle flex items-center gap-1 text-xs cursor-pointer" style="color:var(--claude-foreground);background:none;border:none;padding:0;" aria-expanded="true">
                      <svg class="chevron-icon" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="transform: rotate(180deg);"><polyline points="6 9 12 15 18 9"/></svg>
                      执行推理
                    </button>
                    <span class="text-[10px] shrink-0" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">09:45:16</span>
                  </div>
                  <div class="step-detail mt-1.5 px-3 py-2 rounded-lg text-[11px] leading-relaxed space-y-0.5" style="max-height:120px;opacity:1;background:var(--claude-card);color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);border:1px solid var(--claude-border);">
                    <p>推理深度: 3 | 推理路径: 4条</p>
                    <p>1. Person_001 -> 负责 -> Project_012</p>
                    <p>2. Person_001 -> 负责 -> Project_045</p>
                    <p>3. Person_001 -> 属于 -> Department_003</p>
                    <p>4. Department_003 -> 协作 -> 产品部, 运维部</p>
                  </div>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5" style="background:var(--claude-brand-500);animation:trace-pulse 2s ease-in-out infinite;">
                    <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary-foreground)" stroke-width="3"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                  </div>
                  <div class="w-px flex-1 mt-1" style="background:var(--claude-border);"></div>
                </div>
                <div class="pb-3 flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-medium" style="color:var(--claude-brand-500);">生成回答</span>
                    <span class="text-[10px] shrink-0" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-mono);">09:45:18</span>
                  </div>
                  <div class="mt-1 flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full" style="background:var(--claude-brand-500);animation:dot-blink 1.2s infinite 0s;"></span>
                    <span class="text-[10px]" style="color:var(--claude-brand-500);">生成中...</span>
                  </div>
                </div>
              </div>
              <div class="flex gap-3">
                <div class="flex flex-col items-center">
                  <div class="w-4 h-4 rounded-full shrink-0 mt-0.5" style="background:var(--claude-muted);"></div>
                </div>
                <div class="pb-1 flex-1 min-w-0">
                  <span class="text-xs" style="color:var(--claude-muted-foreground);">整理来源</span>
                </div>
              </div>
            </div>
          </div>

          <div class="text-[15px] leading-[1.75] space-y-3" style="font-family:var(--claude-font-serif);color:var(--claude-card-foreground);">
            <p>根据知识图谱数据，张磊（Person_001）目前负责 <strong style="font-weight:600;">2 个核心项目</strong>。
              <span class="source-tag inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium align-middle whitespace-nowrap ml-1 cursor-pointer relative" style="background:var(--claude-accent);color:var(--claude-brand-700);" data-source-type="重点知识细节" data-source-title="重点知识细节" data-source-entities="Person_001" data-source-desc="从实体 Person_001 的属性中提取，确认该人员负责的项目数量为 2 个核心项目。">重点知识细节
                <div class="source-popup">
                  <div class="source-popup-title">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    重点知识细节
                  </div>
                  <div class="source-popup-row"><b>来源实体：</b></div>
                  <div><span class="source-popup-entity">Person_001</span></div>
                  <div class="source-popup-row" style="margin-top:6px;"><b>说明：</b>从实体 Person_001 的属性中提取，确认该人员负责的项目数量为 2 个核心项目。</div>
                </div>
              </span>
            </p>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] border whitespace-nowrap" style="border-color:var(--claude-border);color:var(--claude-brand-700);font-family:var(--claude-font-mono);background:var(--claude-background);">Person_001</span>
            <p>他主要负责的项目包括"智能制造平台"（Project_012）和"供应链优化系统"（Project_045），其中"智能制造平台"为公司级战略项目。
              <span class="source-tag inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium align-middle whitespace-nowrap ml-1 cursor-pointer relative" style="background:var(--claude-accent);color:var(--claude-brand-700);" data-source-type="具体信息来源" data-source-title="具体信息来源" data-source-entities="Project_012, Project_045" data-source-desc="通过 Person_001 → 负责 → Project_012/Project_045 的关系路径检索，确认具体项目名称及属性。">具体信息来源
                <div class="source-popup">
                  <div class="source-popup-title">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    具体信息来源
                  </div>
                  <div class="source-popup-row"><b>来源实体：</b></div>
                  <div><span class="source-popup-entity">Project_012</span><span class="source-popup-entity">Project_045</span></div>
                  <div class="source-popup-row" style="margin-top:6px;"><b>说明：</b>通过 Person_001 → 负责 → Project_012/Project_045 的关系路径检索，确认具体项目名称及属性。</div>
                </div>
              </span>
            </p>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] border whitespace-nowrap" style="border-color:var(--claude-border);color:var(--claude-brand-700);font-family:var(--claude-font-mono);background:var(--claude-background);">Project_012</span>
            <p>在部门关联方面，张磊隶属于技术研发部（Department_003），同时因跨部门协作项目与产品部、运维部存在协作关系。
              <span class="source-tag inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium align-middle whitespace-nowrap ml-1 cursor-pointer relative" style="background:var(--claude-accent);color:var(--claude-brand-700);" data-source-type="相关知识关联" data-source-title="相关知识关联" data-source-entities="Department_003" data-source-desc="通过 Person_001 → 属于 → Department_003 以及 Department_003 → 协作 → 产品部/运维部 的多跳关系推理得出。">相关知识关联
                <div class="source-popup">
                  <div class="source-popup-title">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    相关知识关联
                  </div>
                  <div class="source-popup-row"><b>来源实体：</b></div>
                  <div><span class="source-popup-entity">Department_003</span></div>
                  <div class="source-popup-row" style="margin-top:6px;"><b>说明：</b>通过 Person_001 → 属于 → Department_003 以及 Department_003 → 协作 → 产品部/运维部 的多跳关系推理得出。</div>
                </div>
              </span>
            </p>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] border whitespace-nowrap" style="border-color:var(--claude-border);color:var(--claude-brand-700);font-family:var(--claude-font-mono);background:var(--claude-background);">Department_003</span>
          </div>

          <div class="flex items-center gap-1 mt-2 opacity-0 transition-opacity duration-150 group-hover:opacity-100">
            <button type="button" @click="copyMessage($event.currentTarget)" class="w-7 h-7 flex items-center justify-center rounded-md transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="复制">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
            <button type="button" @click="showToast('重新生成')" class="w-7 h-7 flex items-center justify-center rounded-md transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="重新生成">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            </button>
          </div>
        </div>
      </div>

      <div class="group">
        <div class="flex justify-end">
          <div class="max-w-[480px]">
            <div class="px-5 py-3 rounded-2xl" style="background:var(--claude-secondary);">
              <p class="text-[15px] leading-relaxed" style="color:var(--claude-foreground);">他掌握哪些技能？</p>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-1 mt-1.5 opacity-0 transition-opacity duration-150 group-hover:opacity-100">
          <span class="text-[11px] mr-1.5" style="color:var(--claude-muted-foreground);">14:33</span>
          <button type="button" @click="copyMessage($event.currentTarget)" class="w-7 h-7 flex items-center justify-center rounded-md transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="复制">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          </button>
          <button type="button" @click="showToast('编辑消息')" class="w-7 h-7 flex items-center justify-center rounded-md transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="编辑">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
        </div>
      </div>

      <div>
        <div class="max-w-[680px] w-full">
          <div class="flex items-center gap-2 mb-3">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="color:var(--claude-muted-foreground);">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <span class="text-[15px]" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-serif);">正在检索</span>
            <span class="inline-flex gap-0.5">
              <span class="w-1 h-1 rounded-full" style="background:var(--claude-muted-foreground);animation:dot-blink 1.2s infinite 0s;"></span>
              <span class="w-1 h-1 rounded-full" style="background:var(--claude-muted-foreground);animation:dot-blink 1.2s infinite 0.2s;"></span>
              <span class="w-1 h-1 rounded-full" style="background:var(--claude-muted-foreground);animation:dot-blink 1.2s infinite 0.4s;"></span>
            </span>
          </div>
          <p class="text-[15px] leading-[1.75] mb-3" style="font-family:var(--claude-font-serif);color:var(--claude-card-foreground);">
            根据知识图谱中关于张磊（Person_001）的技能标签数据，他掌握的核心技能包括
          </p>
          <div class="flex flex-wrap gap-2">
            <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm" style="background:var(--claude-accent);color:var(--claude-brand-700);font-family:var(--claude-font-sans);">Python</span>
            <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm" style="background:var(--claude-accent);color:var(--claude-brand-700);font-family:var(--claude-font-sans);">Java</span>
            <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm" style="background:var(--claude-accent);color:var(--claude-brand-700);font-family:var(--claude-font-sans);">SQL</span>
            <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm" style="background:var(--claude-accent);color:var(--claude-brand-700);font-family:var(--claude-font-sans);">Neo4j</span>
            <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm" style="background:var(--claude-accent);color:var(--claude-brand-700);font-family:var(--claude-font-sans);">Docker</span>
            <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm" style="background:var(--claude-accent);color:var(--claude-brand-700);font-family:var(--claude-font-sans);">Kubernetes</span>
            <span class="inline-flex items-center px-3 py-1.5 rounded-lg text-sm" style="background:var(--claude-accent);color:var(--claude-brand-700);font-family:var(--claude-font-sans);">机器学习</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <aside id="chat-outline" class="chat-outline hidden" aria-label="对话问题目录"></aside>

  <div id="chat-composer-shell" class="chat-composer-shell shrink-0 pb-5 pt-2">
    <div class="max-w-[680px] mx-auto px-8">
      <div id="chat-composer" class="chat-composer rounded-2xl border px-4 pt-3.5 pb-3" style="background:var(--claude-card);border-color:var(--claude-border);">
        <div id="chat-attachment-list" class="chat-attachment-list hidden pb-3"></div>
        <input id="chat-attachment-input" type="file" class="hidden" multiple accept=".pdf,.doc,.docx,.txt,.md,.csv,.json,.png,.jpg,.jpeg" @change="handleChatAttachments($event.currentTarget)">

        <textarea id="message-input" rows="1" class="w-full resize-none text-[15px] leading-relaxed bg-transparent outline-none" style="color:var(--claude-foreground);min-height:24px;max-height:160px;font-family:var(--claude-font-sans);" placeholder="有什么可以帮你的？" @input="adjustTextareaHeight($event.currentTarget);updateSendBtn()"></textarea>

        <div class="flex items-center gap-2 pt-2">
          <button type="button" @click="triggerChatAttachments()" class="group relative w-8 h-8 inline-flex items-center justify-center transition-opacity hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);" aria-label="上传附件">
            <i data-lucide="plus" style="width:17px;height:17px;stroke-width:1.8;"></i>
            <span class="pointer-events-none absolute left-1/2 bottom-full mb-2 -translate-x-1/2 whitespace-nowrap rounded-lg px-2 py-1 text-[11px] opacity-0 transition-opacity group-hover:opacity-100" style="background:var(--claude-foreground);color:var(--claude-background);box-shadow:var(--claude-shadow-md);">上传附件（单个最大 50 MB）</span>
          </button>

          <div class="relative min-w-[190px]">
            <button type="button" data-role="kg-trigger" disabled @click="selectKnowledgeGraph()" class="h-8 w-[190px] flex items-center justify-between gap-2 px-2 text-[13px] transition-opacity disabled:cursor-not-allowed disabled:opacity-60" style="background:transparent;border:none;color:var(--claude-muted-foreground);" title="暂无可用索引">
              <span id="kg-selector-label" class="truncate">暂无可用索引</span>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div id="kg-selector-menu" class="hidden absolute left-0 bottom-full mb-2 w-[240px] max-h-56 overflow-y-auto rounded-xl p-1 z-50" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
          </div>

          <div class="flex-1"></div>

          <div class="relative">
            <button type="button" data-role="model-trigger" disabled @click="toggleModelDropdown()" class="h-8 inline-flex items-center gap-1.5 px-2 text-[13px] transition-opacity disabled:cursor-not-allowed disabled:opacity-60" style="background:transparent;border:none;color:var(--claude-muted-foreground);">
              <span id="model-value">暂无可用模型</span>
              <span id="effort-value" class="text-[12px]" style="color:var(--claude-muted-foreground);">Low</span>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div id="model-dropdown" class="hidden absolute bottom-full right-0 mb-2 w-56 rounded-xl z-50 p-1" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
              <div id="current-model-item" class="px-3 py-2 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]">
                <div class="flex items-center justify-between">
                  <span class="text-[13px] font-medium" style="color:var(--claude-muted-foreground);">暂无可用模型</span>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
              </div>
              <div style="border-top:1px solid var(--claude-border);margin:4px 4px;"></div>
              <div class="relative">
                <div id="effort-panel" class="hidden absolute left-full bottom-0 ml-2 w-72 rounded-xl p-2" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
                  <div class="px-3 py-1.5">
                    <p class="text-[11px] leading-snug" style="color:var(--claude-muted-foreground);">档位越高，知识图谱检索层级越深，回答耗时也会增加</p>
                  </div>
                  <div class="px-2 space-y-0.5">
                    <div class="px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectEffort('Low')">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-1.5">
                          <span class="text-[13px]" style="color:var(--claude-foreground);">Low · 1 跳</span>
                          <span class="text-[10px] px-1.5 py-0.5 rounded-full" style="background:var(--claude-accent);color:var(--claude-muted-foreground);">Default</span>
                        </div>
                        <svg class="effort-check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                      </div>
                    </div>
                    <div class="px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectEffort('Medium')">
                      <span class="text-[13px]" style="color:var(--claude-muted-foreground);">Medium · 2 跳</span>
                    </div>
                    <div class="px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectEffort('High')">
                      <span class="text-[13px]" style="color:var(--claude-muted-foreground);">High · 3 跳</span>
                    </div>
                    <div class="px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectEffort('Max')">
                      <span class="text-[13px]" style="color:var(--claude-muted-foreground);">Max · 4 跳</span>
                    </div>
                  </div>
                </div>
                <div class="px-3 py-2 cursor-pointer flex items-center justify-between rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="toggleEffortPanel()">
                  <span class="text-[13px]" style="color:var(--claude-foreground);">Effort</span>
                  <div class="flex items-center gap-2">
                    <span id="effort-label" class="text-[12px]" style="color:var(--claude-muted-foreground);">Low</span>
                    <svg id="effort-chevron" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                  </div>
                </div>
              </div>
              <div style="border-top:1px solid var(--claude-border);margin:4px 4px;"></div>
              <div class="relative">
                <div id="more-models-panel" class="hidden absolute left-full bottom-0 ml-2 w-56 rounded-xl p-2" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
                  <div class="px-2 space-y-0.5">
                    <div class="px-2.5 py-2 text-[12px]" style="color:var(--claude-muted-foreground);">请先在个人中心配置模型</div>
                  </div>
                </div>
                <div class="px-3 py-2 cursor-pointer flex items-center justify-between rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="toggleMoreModelsPanel()">
                  <span class="text-[13px]" style="color:var(--claude-foreground);">More models</span>
                  <svg id="more-chevron" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                </div>
              </div>
            </div>
          </div>

          <button id="send-btn" type="button" @click="sendMessage()" class="w-8 h-8 flex items-center justify-center rounded-[9px] transition-all cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;" aria-label="发送" title="发送">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.7"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

<AppSearchDialog />

<div id="share-modal" class="hidden fixed inset-0 z-[100] flex items-center justify-center px-4" style="background:rgba(24,22,20,0.34);" @click.self="toggleShareModal()">
  <div class="w-full max-w-[460px] rounded-2xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
    <div class="flex items-start justify-between px-5 pt-5 pb-4">
      <div>
        <h3 class="text-base font-semibold" style="color:var(--claude-foreground);">分享对话</h3>
        <p id="share-subtitle" class="text-xs mt-1" style="color:var(--claude-muted-foreground);">创建截至当前消息的只读快照</p>
      </div>
      <button @click="toggleShareModal()" class="p-1.5 rounded-lg transition-colors hover:bg-[var(--claude-muted)] active:scale-[0.98] cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);" aria-label="关闭分享窗口">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <div class="px-5 pb-5">
      <div class="flex gap-3 px-3.5 py-3 rounded-xl" style="background:var(--claude-muted);color:var(--claude-muted-foreground);">
        <svg class="mt-0.5 shrink-0" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 3l8 4v5c0 5-3.4 8-8 9-4.6-1-8-4-8-9V7l8-4z"/><path d="M9 12l2 2 4-4"/></svg>
        <p class="m-0 text-xs leading-5">获得链接的人可以查看当前对话和信息源。附件原文件、知识库内部标识和后续消息不会公开。</p>
      </div>

      <div id="share-empty-state" class="pt-4">
        <button @click="createShareLink()" class="w-full h-10 rounded-xl text-sm font-medium cursor-pointer transition-opacity hover:opacity-90 active:scale-[0.99]" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">创建分享链接</button>
      </div>

      <div id="share-active-state" class="hidden pt-4">
        <div class="flex items-center gap-2">
          <input type="text" id="share-link" readonly class="min-w-0 flex-1 h-10 px-3 text-xs rounded-xl border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
          <button @click="copyShareLink()" class="h-10 px-4 rounded-xl text-xs font-medium cursor-pointer active:scale-[0.98]" style="background:var(--claude-foreground);color:var(--claude-background);border:none;">复制链接</button>
        </div>
        <div class="flex items-center justify-between mt-3">
          <div class="flex items-center gap-3">
            <button @click="stopSharing()" class="h-8 px-1 text-xs cursor-pointer hover:opacity-75 active:scale-[0.98]" style="background:none;border:none;color:var(--claude-destructive);">停止分享</button>
            <button @click="rotateShareLink()" class="h-8 px-1 text-xs cursor-pointer hover:opacity-75 active:scale-[0.98]" style="background:none;border:none;color:var(--claude-muted-foreground);">重新生成链接</button>
          </div>
          <button @click="updateShareSnapshot()" class="h-8 px-3 rounded-lg text-xs cursor-pointer hover:bg-[var(--claude-muted)] active:scale-[0.98]" style="background:none;border:1px solid var(--claude-border);color:var(--claude-foreground);">更新快照</button>
        </div>
      </div>
    </div>
  </div>
</div>


<TaskCenter />


  </div>
</template>

<script>
import { createGraphApplicationViewController } from '@/controllers/GraphApplicationView.js';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'GraphApplicationView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({ controller: null }),
  mounted() {
    document.title = "知识图谱应用";
    document.body.className = "h-screen overflow-hidden min-h-0";
    this.controller = createGraphApplicationViewController();
  },
  beforeUnmount() {
    this.controller?.destroy?.();
  },
  methods: {
    adjustTextareaHeight(...args) {
      return this.controller?.adjustTextareaHeight(...args);
    },
    copyMessage(...args) {
      return this.controller?.copyMessage(...args);
    },
    copyShareLink(...args) {
      return this.controller?.copyShareLink(...args);
    },
    createShareLink(...args) {
      return this.controller?.createShareLink(...args);
    },
    handleChatAttachments(...args) {
      return this.controller?.handleChatAttachments(...args);
    },
    selectEffort(...args) {
      return this.controller?.selectEffort(...args);
    },
    selectKnowledgeGraph(...args) {
      return this.controller?.selectKnowledgeGraph(...args);
    },
    renameCurrentChat(...args) {
      return this.controller?.renameCurrentChat(...args);
    },
    rotateShareLink(...args) {
      return this.controller?.rotateShareLink(...args);
    },
    selectModel(...args) {
      return this.controller?.selectModel(...args);
    },
    sendMessage(...args) {
      return this.controller?.sendMessage(...args);
    },
    showToast(...args) {
      return this.controller?.showToast(...args);
    },
    triggerChatAttachments(...args) {
      return this.controller?.triggerChatAttachments(...args);
    },
    toggleEffortPanel(...args) {
      return this.controller?.toggleEffortPanel(...args);
    },
    toggleModelDropdown(...args) {
      return this.controller?.toggleModelDropdown(...args);
    },
    toggleMoreModelsPanel(...args) {
      return this.controller?.toggleMoreModelsPanel(...args);
    },
    toggleShareModal(...args) {
      return this.controller?.toggleShareModal(...args);
    },
    stopSharing(...args) {
      return this.controller?.stopSharing(...args);
    },
    updateShareSnapshot(...args) {
      return this.controller?.updateShareSnapshot(...args);
    },
    updateSendBtn(...args) {
      return this.controller?.updateSendBtn(...args);
    },
  },
};
</script>

<style>

@keyframes trace-pulse { 0%,100%{opacity:1;} 50%{opacity:0.5;} }
@keyframes dot-blink { 0%,80%,100%{opacity:0.3;} 40%{opacity:1;} }
@keyframes thinking-log-enter { from { opacity: 0; } to { opacity: 1; } }
@keyframes thinking-spin { to { transform: rotate(360deg); } }
#app-main { position: relative; }
.chat-composer-shell { position: relative; z-index: 35; }
.chat-composer { box-shadow: var(--claude-shadow-sm); will-change: transform, opacity; }
#app-main.chat-is-empty #chat-container { pointer-events: none; }
#app-main.chat-is-empty .chat-composer-shell {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0 2vh;
  pointer-events: none;
}
#app-main.chat-is-empty .chat-composer-shell > div { width: min(760px, calc(100% - 48px)); max-width: none; pointer-events: auto; }
#app-main.chat-is-empty .chat-composer { min-height: 100px; padding: 14px 20px 12px; border-radius: 20px; }
#app-main.chat-is-empty #message-input { min-height: 34px !important; font-size: 16px; }
.chat-empty-state {
  position: absolute;
  left: 50%;
  top: calc(50% - 120px);
  transform: translateX(-50%);
  color: var(--claude-foreground);
  font-family: var(--claude-font-serif);
  font-size: clamp(28px, 2.25vw, 42px);
  line-height: 1.12;
  white-space: nowrap;
}
.chat-attachment-list { display: flex; flex-wrap: wrap; gap: 10px; }
.chat-attachment-list.hidden { display: none; }
.chat-attachment-card {
  position: relative;
  width: 150px;
  height: 116px;
  padding: 14px 12px 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: visible;
  border: 1px solid var(--claude-border);
  border-radius: 12px;
  background: var(--claude-background);
  box-shadow: var(--claude-shadow-sm);
  will-change: transform, opacity;
}
.chat-attachment-card__name { overflow: hidden; color: var(--claude-foreground); font-size: 12px; line-height: 1.45; text-overflow: ellipsis; white-space: nowrap; }
.chat-attachment-card__type { align-self: flex-start; padding: 2px 6px; border: 1px solid var(--claude-border); border-radius: 5px; color: var(--claude-muted-foreground); font-size: 10px; line-height: 1; }
.chat-attachment-card__remove {
  position: absolute;
  left: -8px;
  top: -8px;
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  border: 1px solid var(--claude-border);
  border-radius: 50%;
  color: var(--claude-muted-foreground);
  background: var(--claude-card);
  box-shadow: var(--claude-shadow-xs);
  cursor: pointer;
}
.chat-sent-attachments { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }
.chat-sent-attachments + p { margin-top: 10px; }
.chat-sent-file {
  width: 148px;
  min-height: 82px;
  padding: 11px;
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  grid-template-rows: minmax(0, 1fr) auto;
  column-gap: 9px;
  border: 1px solid var(--claude-border);
  border-radius: 12px;
  color: var(--claude-foreground);
  background: var(--claude-card);
  box-shadow: var(--claude-shadow-xs);
  text-decoration: none;
  transition: border-color .16s ease, transform .16s ease, box-shadow .16s ease;
}
.chat-sent-file:hover { border-color: color-mix(in srgb, var(--claude-primary) 45%, var(--claude-border)); box-shadow: var(--claude-shadow-sm); transform: translateY(-1px); }
.chat-sent-file__icon { grid-row: 1 / 3; align-self: start; width: 24px; height: 24px; color: var(--claude-muted-foreground); }
.chat-sent-file__name { min-width: 0; overflow: hidden; align-self: start; font-size: 12px; line-height: 1.4; text-overflow: ellipsis; white-space: nowrap; }
.chat-sent-file__type { justify-self: start; padding: 2px 5px; border: 1px solid var(--claude-border); border-radius: 5px; color: var(--claude-muted-foreground); font-size: 9px; line-height: 1; }
.chat-outline {
  position: fixed;
  z-index: 34;
  right: 18px;
  top: 76px;
  bottom: 112px;
  width: 42px;
}
.chat-outline__rail { height: 100%; display: flex; flex-direction: column; align-items: flex-end; justify-content: center; gap: 7px; }
.chat-outline__marker { width: 28px; height: 3px; padding: 0; border: 0; border-radius: 999px; background: color-mix(in srgb, var(--claude-muted-foreground) 48%, transparent); cursor: pointer; transition: width .16s ease, background-color .16s ease; }
.chat-outline__marker:hover, .chat-outline__marker.is-active { width: 34px; background: var(--claude-foreground); }
.chat-outline__panel {
  position: absolute;
  right: 0;
  top: 50%;
  width: 360px;
  max-height: min(540px, calc(100vh - 180px));
  padding: 12px;
  overflow-y: auto;
  border: 1px solid var(--claude-border);
  border-radius: 18px;
  background: var(--claude-card);
  box-shadow: var(--claude-shadow-lg);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-50%) translateX(8px);
  pointer-events: none;
  transition: opacity .18s ease, transform .18s ease, visibility .18s;
}
.chat-outline:hover .chat-outline__panel, .chat-outline:focus-within .chat-outline__panel { opacity: 1; visibility: visible; transform: translateY(-50%) translateX(0); pointer-events: auto; }
.chat-outline__title { margin: 2px 6px 8px; color: var(--claude-muted-foreground); font-size: 12px; }
.chat-outline__item { width: 100%; padding: 9px 10px; overflow: hidden; border: 0; border-radius: 10px; color: var(--claude-foreground); background: transparent; font-size: 13px; line-height: 1.35; text-align: left; text-overflow: ellipsis; white-space: nowrap; cursor: pointer; }
.chat-outline__item:hover { background: var(--claude-secondary); }
.chat-user-message { scroll-margin-top: 72px; }
.chat-user-message.is-editing .chat-user-message-shell { width: 100%; max-width: 100%; }
.chat-user-message.is-editing .chat-user-bubble {
  padding: 10px;
  border: 1px solid var(--claude-border);
  border-radius: 16px;
  background: var(--claude-secondary) !important;
  box-shadow: var(--claude-shadow-sm);
}
.chat-user-message.is-editing .chat-sent-attachments { justify-content: flex-start; margin-bottom: 10px; }
.chat-inline-edit__input {
  width: 100%;
  min-height: 46px;
  max-height: 180px;
  padding: 10px 12px;
  resize: none;
  overflow-y: auto;
  border: 1.5px solid var(--claude-primary);
  border-radius: 12px;
  outline: none;
  background: var(--claude-card);
  color: var(--claude-foreground);
  font-family: var(--claude-font-sans);
  font-size: 15px;
  line-height: 1.5;
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--claude-primary) 10%, transparent);
}
.chat-inline-edit__actions { display: flex; justify-content: flex-end; gap: 9px; margin-top: 10px; }
.chat-inline-edit__button {
  height: 36px;
  padding: 0 16px;
  border: 1px solid var(--claude-border);
  border-radius: 10px;
  background: var(--claude-card);
  color: var(--claude-foreground);
  font-size: 13px;
  font-weight: 550;
  cursor: pointer;
}
.chat-inline-edit__button:hover { background: var(--claude-accent); }
.chat-inline-edit__save { border-color: transparent; background: var(--claude-foreground); color: var(--claude-background); }
.chat-inline-edit__save:hover { background: color-mix(in srgb, var(--claude-foreground) 88%, transparent); }
.chat-inline-edit__save:disabled { opacity: .55; cursor: wait; }
@media (max-width: 900px) { .chat-outline { display: none !important; } }
.ai-thinking { width: min(100%, 680px); }
.ai-thinking-summary {
  width: fit-content;
  max-width: 100%;
  display: flex;
  align-items: center;
  gap: 7px;
  list-style: none;
  color: var(--claude-muted-foreground);
  font-family: var(--claude-font-sans);
  font-size: 13px;
  line-height: 1.5;
  cursor: pointer;
  user-select: none;
}
.ai-thinking-summary::-webkit-details-marker { display: none; }
.ai-thinking-summary__status { width: 15px; height: 15px; display: grid; flex: none; place-items: center; }
.ai-thinking-summary__status svg { width: 14px; height: 14px; stroke-width: 1.7; }
.ai-thinking[data-state="running"] .ai-thinking-summary__status svg { animation: thinking-spin 1.35s linear infinite; }
.ai-thinking[data-state="error"] .ai-thinking-summary__status { color: var(--claude-destructive); }
.ai-thinking-summary__text { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ai-thinking-summary__chevron { width: 13px; height: 13px; flex: none; transition: transform .16s ease; }
.ai-thinking[open] .ai-thinking-summary__chevron { transform: rotate(90deg); }
.ai-thinking-body { padding: 15px 0 2px 5px; }
.ai-thinking-log { width: 100%; display: grid; }
.ai-thinking-log__item {
  position: relative;
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  column-gap: 12px;
  padding: 0 0 18px;
  color: var(--claude-muted-foreground);
  font-family: var(--claude-font-sans);
  font-size: 13px;
  line-height: 1.55;
  animation: thinking-log-enter .18s ease-out both;
}
.ai-thinking-log__item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 7px;
  top: 18px;
  bottom: 0;
  width: 1px;
  background: var(--claude-border);
}
.ai-thinking-log__marker {
  position: relative;
  z-index: 1;
  width: 15px;
  height: 15px;
  display: grid;
  place-items: center;
  color: var(--claude-muted-foreground);
}
.ai-thinking-log__marker svg { width: 14px; height: 14px; stroke-width: 1.7; }
.ai-thinking-log__item.is-current .ai-thinking-log__marker { color: var(--claude-primary); }
.ai-thinking-log__item.is-current .ai-thinking-log__marker svg { animation: thinking-pulse 1.2s ease-in-out infinite; }
.ai-thinking-log__item.is-complete .ai-thinking-log__marker { color: color-mix(in srgb, var(--claude-primary) 68%, var(--claude-muted-foreground)); }
.ai-thinking-log__item.is-error .ai-thinking-log__marker { color: var(--claude-destructive); }
.ai-thinking-log__content { min-width: 0; }
.ai-thinking-log__label { color: var(--claude-foreground); font-size: 13px; font-weight: 400; }
.ai-thinking-log__item.is-error .ai-thinking-log__label { color: var(--claude-destructive); }
.ai-thinking-log__detail {
  margin-top: 7px;
  color: var(--claude-muted-foreground);
  font-size: 12px;
  line-height: 1.65;
  white-space: pre-wrap;
}
.ai-thinking-log__item.is-context .ai-thinking-log__detail {
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--claude-secondary);
  color: var(--claude-foreground);
  font-family: var(--claude-font-sans);
}
.ai-thinking-log__item.is-error .ai-thinking-log__detail { color: var(--claude-destructive); }
.ai-answer-error {
  width: fit-content;
  max-width: 100%;
  display: inline-flex;
  align-items: flex-start;
  gap: 7px;
  padding: 8px 10px;
  border: 1px solid color-mix(in srgb, var(--claude-destructive) 28%, var(--claude-border));
  border-radius: 10px;
  color: var(--claude-destructive);
  background: color-mix(in srgb, var(--claude-destructive) 5%, var(--claude-card));
  font-family: var(--claude-font-sans);
  font-size: 12px;
  line-height: 1.5;
}
.ai-answer-error svg { width: 14px; height: 14px; flex: none; margin-top: 2px; }
@media (prefers-reduced-motion: reduce) {
  .ai-thinking[data-state="running"] .ai-thinking-summary__status svg { animation: none; }
}
.source-popup-row {
  display: block;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-size: 11px;
  line-height: 1.6;
  color: var(--claude-muted-foreground);
}
.streaming-caret { display: inline-block; width: 2px; height: 1em; margin-left: 2px; vertical-align: -.12em; border-radius: 2px; background: var(--claude-primary); animation: streaming-caret-blink .8s steps(1) infinite; }
@keyframes thinking-pulse { 0%, 100% { opacity: .48; transform: scale(.94); } 50% { opacity: 1; transform: scale(1); } }
@keyframes streaming-caret-blink { 0%, 52% { opacity: 1; } 53%, 100% { opacity: .18; } }
.source-popup-row b {
  font-weight: 500;
  color: var(--claude-foreground);
}
.source-popup-entity {
  display: inline-block;
  font-family: var(--claude-font-mono);
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 4px;
  background: var(--claude-secondary);
  color: var(--claude-secondary-foreground);
  margin-right: 3px;
  margin-top: 2px;
}
.sidebar-logo { display: flex; }
#app-sidebar.sidebar-collapsed { width: 48px; }
#app-sidebar.sidebar-collapsed .sidebar-text { display: none; }
#app-sidebar.sidebar-collapsed .sidebar-logo { display: none; }
#app-sidebar.sidebar-collapsed nav a span { display: none; }
#app-sidebar.sidebar-collapsed .sidebar-content { display: none; }
#app-sidebar.sidebar-collapsed .sidebar-collapsed-hide,
#app-sidebar.sidebar-collapsed ~ #app-main .sidebar-collapsed-hide { display: none; }
#app-sidebar.sidebar-collapsed .h-12 { justify-content: center; }
#app-sidebar.sidebar-collapsed .sidebar-toggle-btn {
  position: relative;
  margin: 0;
}
#app-sidebar.sidebar-collapsed .sidebar-toggle-btn::after {
  content: attr(data-title);
  position: absolute;
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 6px;
  background: var(--claude-card);
  color: var(--claude-foreground);
  border: 1px solid var(--claude-border);
  box-shadow: var(--claude-shadow-lg);
  z-index: 100;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s;
}
#app-sidebar.sidebar-collapsed .sidebar-toggle-btn:hover::after {
  opacity: 1;
}
#app-sidebar.sidebar-collapsed nav a {
  position: relative;
}
#app-sidebar.sidebar-collapsed nav a:hover::after {
  content: attr(data-title);
  position: absolute;
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 6px;
  background: var(--claude-card);
  color: var(--claude-foreground);
  border: 1px solid var(--claude-border);
  box-shadow: var(--claude-shadow-lg);
  z-index: 100;
}
#app-sidebar.sidebar-collapsed button[data-title]:hover::after {
  content: attr(data-title);
  position: absolute;
  left: calc(100% + 8px);
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  border-radius: 6px;
  background: var(--claude-card);
  color: var(--claude-foreground);
  border: 1px solid var(--claude-border);
  box-shadow: var(--claude-shadow-lg);
  z-index: 100;
}

</style>
