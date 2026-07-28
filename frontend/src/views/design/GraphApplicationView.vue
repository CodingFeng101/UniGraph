<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="app" />

<div id="app-main" class="h-screen min-h-0 flex flex-col transition-all duration-300" style="margin-left:260px;">
  <div class="shrink-0 h-11 flex items-center px-6 justify-between">
    <div class="flex items-center gap-1.5 cursor-pointer sidebar-collapsed-hide" style="max-width:300px;" @click="renameCurrentChat()" title="点击重命名">
      <span id="conversation-title" class="text-sm font-medium truncate" style="color:var(--claude-foreground);">新对话</span>
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-muted-foreground);flex-shrink:0;"><polyline points="9 18 15 12 9 6"/></svg>
    </div>
    <button type="button" data-role="share-trigger" @click="toggleShareModal()" class="w-8 h-8 flex items-center justify-center rounded-lg cursor-pointer transition-colors hover:opacity-70" style="background:transparent;border:none;color:var(--claude-muted-foreground);" aria-label="分享对话">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
    </button>
  </div>

  <div class="flex-1 overflow-y-auto" id="chat-container">
    <div class="max-w-[680px] mx-auto px-8 py-6 space-y-6">
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
                    <span class="text-xs" style="color:var(--claude-foreground);">接收问题</span>
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
              <span class="source-tag inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium align-middle whitespace-nowrap ml-1 cursor-pointer relative" style="background:var(--claude-accent);color:var(--claude-brand-700);" data-source-type="细节重点" data-source-title="细节重点" data-source-entities="Person_001" data-source-desc="从实体 Person_001 的属性中提取，确认该人员负责的项目数量为 2 个核心项目。">细节重点
                <div class="source-popup">
                  <div class="source-popup-title">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    细节重点
                  </div>
                  <div class="source-popup-row"><b>来源实体：</b></div>
                  <div><span class="source-popup-entity">Person_001</span></div>
                  <div class="source-popup-row" style="margin-top:6px;"><b>说明：</b>从实体 Person_001 的属性中提取，确认该人员负责的项目数量为 2 个核心项目。</div>
                </div>
              </span>
            </p>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] border whitespace-nowrap" style="border-color:var(--claude-border);color:var(--claude-brand-700);font-family:var(--claude-font-mono);background:var(--claude-background);">Person_001</span>
            <p>他主要负责的项目包括"智能制造平台"（Project_012）和"供应链优化系统"（Project_045），其中"智能制造平台"为公司级战略项目。
              <span class="source-tag inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium align-middle whitespace-nowrap ml-1 cursor-pointer relative" style="background:var(--claude-accent);color:var(--claude-brand-700);" data-source-type="具体来源" data-source-title="具体来源" data-source-entities="Project_012, Project_045" data-source-desc="通过 Person_001 → 负责 → Project_012/Project_045 的关系路径检索，确认具体项目名称及属性。">具体来源
                <div class="source-popup">
                  <div class="source-popup-title">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    具体来源
                  </div>
                  <div class="source-popup-row"><b>来源实体：</b></div>
                  <div><span class="source-popup-entity">Project_012</span><span class="source-popup-entity">Project_045</span></div>
                  <div class="source-popup-row" style="margin-top:6px;"><b>说明：</b>通过 Person_001 → 负责 → Project_012/Project_045 的关系路径检索，确认具体项目名称及属性。</div>
                </div>
              </span>
            </p>
            <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] border whitespace-nowrap" style="border-color:var(--claude-border);color:var(--claude-brand-700);font-family:var(--claude-font-mono);background:var(--claude-background);">Project_012</span>
            <p>在部门关联方面，张磊隶属于技术研发部（Department_003），同时因跨部门协作项目与产品部、运维部存在协作关系。
              <span class="source-tag inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium align-middle whitespace-nowrap ml-1 cursor-pointer relative" style="background:var(--claude-accent);color:var(--claude-brand-700);" data-source-type="知识关联" data-source-title="知识关联" data-source-entities="Department_003" data-source-desc="通过 Person_001 → 属于 → Department_003 以及 Department_003 → 协作 → 产品部/运维部 的多跳关系推理得出。">知识关联
                <div class="source-popup">
                  <div class="source-popup-title">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                    知识关联
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

  <div class="shrink-0 pb-5 pt-2">
    <div class="max-w-[680px] mx-auto px-8">
      <div class="rounded-2xl border px-4 pt-3.5 pb-3" style="background:var(--claude-card);border-color:var(--claude-border);">
        <textarea id="message-input" rows="1" class="w-full resize-none text-[15px] leading-relaxed bg-transparent outline-none" style="color:var(--claude-foreground);min-height:24px;max-height:160px;font-family:var(--claude-font-sans);" placeholder="有什么可以帮你的？" @input="adjustTextareaHeight($event.currentTarget);updateSendBtn()"></textarea>

        <div id="chat-attachment-list" class="hidden flex flex-wrap gap-1.5 pt-2"></div>
        <input id="chat-attachment-input" type="file" class="hidden" multiple accept=".pdf,.doc,.docx,.txt,.md,.csv,.json,.png,.jpg,.jpeg" @change="handleChatAttachments($event.currentTarget)">

        <div class="flex items-center gap-2 pt-2">
          <button type="button" @click="triggerChatAttachments()" class="group relative w-8 h-8 inline-flex items-center justify-center rounded-full transition-colors cursor-pointer" style="background:var(--claude-secondary);border:none;color:var(--claude-foreground);" aria-label="上传附件">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M21.44 11.05 12.25 20.24a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
            <span class="pointer-events-none absolute left-1/2 bottom-full mb-2 -translate-x-1/2 whitespace-nowrap rounded-lg px-2 py-1 text-[11px] opacity-0 transition-opacity group-hover:opacity-100" style="background:var(--claude-foreground);color:var(--claude-background);box-shadow:var(--claude-shadow-md);">上传附件</span>
          </button>

          <div class="relative">
            <button type="button" data-role="kg-trigger" @click="selectKnowledgeGraph()" class="h-8 flex items-center gap-1.5 px-2.5 rounded-full text-[12px] transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);border:none;color:var(--claude-foreground);" title="选择知识图谱索引">
              <span id="kg-status-dot" class="w-1.5 h-1.5 rounded-full shrink-0" style="background:var(--claude-success-500);"></span>
              <span id="kg-selector-label">选择知识图谱</span>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div id="kg-selector-menu" class="hidden absolute left-0 bottom-full mb-2 w-48 max-h-56 overflow-y-auto rounded-xl p-1 z-50" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
          </div>

          <div class="flex-1"></div>

          <div class="relative">
            <button type="button" data-role="model-trigger" @click="toggleModelDropdown()" class="h-8 inline-flex items-center gap-1.5 px-3 rounded-full text-[13px] cursor-pointer transition-colors" style="background:var(--claude-accent);border:none;color:var(--claude-foreground);">
              <span id="model-value">UG-4o</span>
              <span id="effort-value" class="text-[11px]" style="color:var(--claude-muted-foreground);">Low</span>
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div id="model-dropdown" class="hidden absolute bottom-full right-0 mb-2 w-56 rounded-xl z-50 p-1" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
              <div id="current-model-item" class="px-3 py-2 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectModel($event.currentTarget,'UG-4o')">
                <div class="flex items-center justify-between">
                  <span class="text-[13px] font-medium" style="color:var(--claude-foreground);">UG-4o</span>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                </div>
              </div>
              <div style="border-top:1px solid var(--claude-border);margin:4px 4px;"></div>
              <div class="relative">
                <div id="effort-panel" class="hidden absolute left-full bottom-0 ml-2 w-72 rounded-xl p-2" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
                  <div class="px-3 py-1.5">
                    <p class="text-[11px] leading-snug" style="color:var(--claude-muted-foreground);">Higher effort means more thorough responses, but takes longer</p>
                  </div>
                  <div class="px-2 space-y-0.5">
                    <div class="px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectEffort('Low')">
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-1.5">
                          <span class="text-[13px]" style="color:var(--claude-foreground);">Low</span>
                          <span class="text-[10px] px-1.5 py-0.5 rounded-full" style="background:var(--claude-accent);color:var(--claude-muted-foreground);">Default</span>
                        </div>
                        <svg class="effort-check" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-primary)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                      </div>
                    </div>
                    <div class="px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectEffort('Medium')">
                      <span class="text-[13px]" style="color:var(--claude-muted-foreground);">Medium</span>
                    </div>
                    <div class="px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectEffort('High')">
                      <span class="text-[13px]" style="color:var(--claude-muted-foreground);">High</span>
                    </div>
                    <div class="px-2.5 py-1.5 cursor-pointer rounded-lg transition-colors hover:bg-[var(--claude-secondary)]" @click="selectEffort('Max')">
                      <span class="text-[13px]" style="color:var(--claude-muted-foreground);">Max</span>
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

          <button type="button" @click="showToast('语音输入')" class="w-8 h-8 flex items-center justify-center rounded-lg transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-muted-foreground);" aria-label="语音输入" title="语音">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
          </button>

          <button id="send-btn" type="button" @click="sendMessage()" class="w-9 h-9 flex items-center justify-center rounded-[10px] transition-all cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;" aria-label="发送" title="发送">
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.7"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>
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

<div id="toast-container" class="fixed bottom-6 right-6 z-[100] flex flex-col gap-2"></div>

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
@keyframes thinking-log-enter { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.ai-thinking-log { margin: 8px 0 0 22px; display: grid; gap: 5px; }
.ai-thinking-log__item { display: grid; grid-template-columns: 8px auto; align-items: center; column-gap: 7px; color: var(--claude-muted-foreground); font-size: 12px; line-height: 1.35; transition: opacity .18s ease; animation: thinking-log-enter .22s ease-out both; }
.ai-thinking-log__dot { width: 5px; height: 5px; border-radius: 50%; background: var(--claude-accent); }
.ai-thinking-log__detail { grid-column: 2; color: color-mix(in srgb, var(--claude-muted-foreground) 78%, transparent); font-size: 11px; }
.source-popup {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  min-width: 240px;
  max-width: 300px;
  padding: 12px 14px;
  border-radius: 12px;
  z-index: 100;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s ease;
  background: var(--claude-card);
  border: 1px solid var(--claude-border);
  box-shadow: var(--claude-shadow-lg);
}
.source-tag:hover .source-popup { opacity: 1; }
.source-popup::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: var(--claude-border);
}
.source-popup-title {
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--claude-brand-700);
}
.source-popup-row {
  font-size: 11px;
  line-height: 1.6;
  color: var(--claude-muted-foreground);
}
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
