<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="design" />

<AppSearchDialog />

<div id="app-main" class="h-screen min-h-0 flex flex-col transition-all duration-300" style="margin-left:260px;">
  <header class="h-14 flex items-center justify-between px-5 shrink-0 min-w-0" style="background:var(--claude-card);">
    <div class="flex items-center gap-2">
      <div class="relative" id="arch-dropdown-wrapper-top">
        <button id="arch-dropdown-trigger" type="button" disabled @click="toggleArchDropdown('arch-dropdown-top')" class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg transition-colors w-[240px] disabled:cursor-not-allowed disabled:opacity-60" style="background:var(--claude-accent);border:1px solid var(--claude-border);">
          <span class="text-xs font-medium truncate flex-1 text-left" style="color:var(--claude-muted-foreground);">暂无知识架构</span>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2.5" class="shrink-0"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div id="arch-dropdown-top" class="hidden absolute left-0 top-full mt-1 rounded-lg overflow-hidden z-50 w-[240px]" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <button type="button" @click="openModal('modal-new-arch')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增架构
      </button>
      <button type="button" @click="showElement('modal-update-arch')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
        更新知识架构
      </button>
      <button type="button" @click="openModal('modal-entity')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增实体类型
      </button>
      <button type="button" @click="openModal('modal-relation')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增关系类型
      </button>
      <button type="button" @click="exportArchitecture()" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>
        导出架构
      </button>
    </div>
  </header>

  <div class="flex flex-1 min-h-0">
    <div class="flex-1 relative min-w-0 overflow-hidden" style="background:var(--claude-secondary);">
      <div class="absolute top-4 left-4 z-10">
        <div class="flex items-center gap-2 h-9 w-[240px] px-3 rounded-lg" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-md);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input type="text" id="search-input" @input="filterGraph(false)" @keyup.enter="filterGraph(true)" class="flex-1 min-w-0 text-xs bg-transparent outline-none" style="color:var(--claude-foreground);" placeholder="搜索实体或关系类型...">
        </div>
      </div>

      <svg id="graph-canvas" width="100%" height="100%" viewBox="0 0 800 600" style="background:var(--claude-background);transition:transform 0.2s ease;">
        <defs>
          <pattern id="dotgrid" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
            <circle cx="12" cy="12" r="1" fill="var(--claude-muted)" opacity="0.4"/>
          </pattern>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto" fill="var(--claude-muted-foreground)">
            <polygon points="0 0, 10 3.5, 0 7"/>
          </marker>
          <marker id="arrowhead-active" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto" fill="var(--claude-brand-500)">
            <polygon points="0 0, 10 3.5, 0 7"/>
          </marker>
          <filter id="node-shadow" x="-15%" y="-15%" width="130%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="rgba(0,0,0,0.06)"/>
          </filter>
          <filter id="node-shadow-active" x="-20%" y="-20%" width="140%" height="150%">
            <feDropShadow dx="0" dy="3" stdDeviation="8" flood-color="rgba(201,100,66,0.18)"/>
          </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#dotgrid)"/>

        <g id="graph-root" transform="scale(1)">
        <g @mouseenter="showTooltip($event,'安装','关系类型','起始: 数控机床<br>目标: 主轴<br>描述: 数控机床安装主轴')">
          <line x1="470" y1="170" x2="570" y2="260" stroke="var(--claude-muted-foreground)" stroke-width="1.5" marker-end="url(#arrowhead)" opacity="0.5"/>
          <rect x="495" y="196" width="52" height="22" rx="4" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <text x="521" y="211" text-anchor="middle" font-size="11" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-sans);">安装</text>
        </g>

        <g @mouseenter="showTooltip($event,'使用','关系类型','起始: 数控机床<br>目标: 刀具<br>描述: 数控机床使用刀具')">
          <line x1="370" y1="190" x2="370" y2="425" stroke="var(--claude-muted-foreground)" stroke-width="1.5" marker-end="url(#arrowhead)" opacity="0.5"/>
          <rect x="374" y="295" width="52" height="22" rx="4" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <text x="400" y="310" text-anchor="middle" font-size="11" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-sans);">使用</text>
        </g>

        <g @mouseenter="showTooltip($event,'操作','关系类型','起始: 操作人员<br>目标: 数控机床<br>描述: 操作人员操作数控机床')">
          <line x1="230" y1="270" x2="320" y2="175" stroke="var(--claude-brand-500)" stroke-width="2" marker-end="url(#arrowhead-active)" opacity="0.7"/>
          <rect x="247" y="210" width="52" height="22" rx="4" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <text x="273" y="225" text-anchor="middle" font-size="11" fill="var(--claude-brand-500)" style="font-family:var(--claude-font-sans);">操作</text>
        </g>

        <g class="graph-node" data-label="数控机床" @mouseenter="showTooltip($event,'数控机床','实体类型','属性: 型号, 制造商, 额定功率<br>来源: AI 文档抽取<br>关联关系: 3 条')">
          <rect x="295" y="60" width="210" height="110" rx="12" fill="var(--claude-card)" stroke="var(--claude-brand-500)" stroke-width="2.5" filter="url(#node-shadow-active)"/>
          <circle cx="315" cy="83" r="4" fill="var(--claude-brand-500)"/>
          <text x="400" y="90" text-anchor="middle" font-size="14" font-weight="600" fill="var(--claude-foreground)" style="font-family:var(--claude-font-sans);">数控机床</text>
          <line x1="315" y1="102" x2="485" y2="102" stroke="var(--claude-border)" stroke-width="1"/>
          <text x="320" y="120" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">型号</text>
          <text x="320" y="138" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">制造商</text>
          <text x="320" y="156" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">额定功率</text>
        </g>

        <g class="graph-node" data-label="主轴" @mouseenter="showTooltip($event,'主轴','实体类型','属性: 转速, 功率<br>来源: AI 文档抽取<br>关联关系: 1 条')">
          <rect x="555" y="250" width="170" height="100" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1.5" filter="url(#node-shadow)"/>
          <text x="640" y="280" text-anchor="middle" font-size="14" font-weight="600" fill="var(--claude-foreground)" style="font-family:var(--claude-font-sans);">主轴</text>
          <line x1="575" y1="290" x2="705" y2="290" stroke="var(--claude-border)" stroke-width="1"/>
          <text x="580" y="308" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">转速</text>
          <text x="580" y="326" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">功率</text>
        </g>

        <g class="graph-node" data-label="刀具" @mouseenter="showTooltip($event,'刀具','实体类型','属性: 类型, 材料<br>来源: AI 文档抽取<br>关联关系: 1 条')">
          <rect x="315" y="430" width="170" height="100" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1.5" filter="url(#node-shadow)"/>
          <text x="400" y="460" text-anchor="middle" font-size="14" font-weight="600" fill="var(--claude-foreground)" style="font-family:var(--claude-font-sans);">刀具</text>
          <line x1="335" y1="470" x2="465" y2="470" stroke="var(--claude-border)" stroke-width="1"/>
          <text x="340" y="488" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">类型</text>
          <text x="340" y="506" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">材料</text>
        </g>

        <g class="graph-node" data-label="操作人员" @mouseenter="showTooltip($event,'操作人员','实体类型','属性: 姓名, 工号, 技能等级<br>来源: AI 文档抽取<br>关联关系: 1 条')">
          <rect x="75" y="240" width="180" height="120" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1.5" filter="url(#node-shadow)"/>
          <text x="165" y="270" text-anchor="middle" font-size="14" font-weight="600" fill="var(--claude-foreground)" style="font-family:var(--claude-font-sans);">操作人员</text>
          <line x1="95" y1="280" x2="235" y2="280" stroke="var(--claude-border)" stroke-width="1"/>
          <text x="100" y="298" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">姓名</text>
          <text x="100" y="316" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">工号</text>
          <text x="100" y="334" font-size="10" fill="var(--claude-muted-foreground)" style="font-family:var(--claude-font-mono);">技能等级</text>
        </g>
        </g>
      </svg>

      <div id="canvas-tooltip" class="hidden graph-hover-card" @mouseleave="hideTooltip()">
        <div class="graph-hover-card__header">
          <div class="min-w-0">
            <p id="tooltip-title" class="graph-hover-card__title"></p>
            <p id="tooltip-type" class="graph-hover-card__type"></p>
          </div>
          <span id="tooltip-badge" class="graph-hover-card__badge"></span>
        </div>
        <div id="tooltip-body" class="graph-hover-card__body"></div>
        <div class="graph-hover-card__actions">
          <button type="button" @click="hideTooltip();editSelectedElement()" class="graph-hover-card__action">
            <i data-lucide="pencil-line" aria-hidden="true"></i><span>编辑</span>
          </button>
          <button type="button" @click="hideTooltip();deleteSelectedElement()" class="graph-hover-card__action graph-hover-card__action--delete">
            <i data-lucide="trash-2" aria-hidden="true"></i><span>删除</span>
          </button>
        </div>
      </div>

      <div class="absolute bottom-4 left-4 z-10">
        <div class="flex items-center gap-1 p-1 rounded-lg" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-sm);">
          <button data-graph-style="database" type="button" @click="changeStyle('database')" class="px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">数据库</button>
          <button data-graph-style="minimal" type="button" @click="changeStyle('minimal')" class="px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;color:var(--claude-muted-foreground);border:none;">简约</button>
          <button data-graph-style="colorful" type="button" @click="changeStyle('colorful')" class="px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;color:var(--claude-muted-foreground);border:none;">多彩</button>
          <button data-graph-style="load" type="button" @click="changeStyle('load')" class="px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;color:var(--claude-muted-foreground);border:none;">负载</button>
        </div>
      </div>

      <div class="absolute bottom-4 right-4 z-10">
        <div class="flex flex-row gap-0.5 rounded-lg overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-sm);">
          <button type="button" @click="zoomIn()" class="w-8 h-8 flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
          </button>
          <div style="width:1px;background:var(--claude-border);"></div>
          <button type="button" @click="zoomOut()" class="w-8 h-8 flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/></svg>
          </button>
          <div style="width:1px;background:var(--claude-border);"></div>
          <button type="button" @click="resetZoom()" class="w-8 h-8 flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);" aria-label="适应画布" title="适应画布">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

<TaskCenter />



<div id="modal-entity" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:420px;">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom:1px solid var(--claude-border);">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">新增实体类型</h3>
      <button @click="closeModal('modal-entity')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="px-5 py-4 space-y-4">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">实体类型名称</label>
        <input type="text" id="entity-name" placeholder="如：设备、人员" class="w-full h-9 px-3 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">属性列表</label>
        <div class="space-y-2" id="modal-entity-attrs">
          <div class="flex items-center gap-2">
            <input type="text" placeholder="属性名称" class="flex-1 h-8 px-2.5 text-xs rounded-md border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
            <button type="button" @click="removeAttr($event.currentTarget)" class="w-7 h-7 rounded flex items-center justify-center cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
          </div>
        </div>
        <button type="button" @click="addAttr()" class="flex items-center gap-1 text-xs font-medium mt-2 cursor-pointer" style="color:var(--claude-brand-500);background:none;border:none;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          添加属性
        </button>
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 px-5 py-3" style="border-top:1px solid var(--claude-border);">
      <button @click="closeModal('modal-entity')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="addEntity()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">确认添加</button>
    </div>
  </div>
</div>

<div id="modal-relation" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:440px;">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom:1px solid var(--claude-border);">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">新增关系类型</h3>
      <button @click="closeModal('modal-relation')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="px-5 py-4 space-y-4">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">起始实体类型</label>
        <div class="relative">
          <input id="relation-source-input" type="text" autocomplete="off" placeholder="搜索或选择起始实体类型" @focus="showRelationEntityList('source')" @input="filterRelationEntityList('source')" class="w-full h-9 px-3 text-sm rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
          <div id="relation-source-dropdown" class="hidden absolute left-0 top-full mt-1 rounded-lg overflow-x-hidden overflow-y-auto overscroll-contain z-50 w-full max-h-52" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">关系名称</label>
        <input type="text" id="relation-name" placeholder="如：安装、使用" class="w-full h-9 px-3 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">目标实体类型</label>
        <div class="relative">
          <input id="relation-target-input" type="text" autocomplete="off" placeholder="搜索或选择目标实体类型" @focus="showRelationEntityList('target')" @input="filterRelationEntityList('target')" class="w-full h-9 px-3 text-sm rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
          <div id="relation-target-dropdown" class="hidden absolute left-0 bottom-full mb-1 rounded-lg overflow-x-hidden overflow-y-auto overscroll-contain z-50 w-full max-h-52" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">关系说明</label>
        <textarea id="relation-desc" rows="2" placeholder="描述该关系的含义..." class="w-full px-3 py-2 text-sm rounded-lg border outline-none resize-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);"></textarea>
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 px-5 py-3" style="border-top:1px solid var(--claude-border);">
      <button @click="closeModal('modal-relation')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="addRelation()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">确认添加</button>
    </div>
  </div>
</div>

<div id="modal-new-arch" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:520px;">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom:1px solid var(--claude-border);">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">新建知识架构</h3>
      <button @click="closeModal('modal-new-arch')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="px-5 py-4 space-y-4">
      <div class="grid grid-cols-2 gap-2 p-1 rounded-xl" style="background:var(--claude-secondary);">
        <button id="create-arch-document-tab" type="button" @click="setCreateArchMode('document')" class="px-3 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-card);border:1px solid var(--claude-border);color:var(--claude-foreground);">基于文档构建</button>
        <button id="create-arch-json-tab" type="button" @click="setCreateArchMode('json')" class="px-3 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:transparent;border:1px solid transparent;color:var(--claude-muted-foreground);">导入 JSON</button>
      </div>
      <div id="create-arch-document-panel" class="space-y-3">
        <div>
          <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">架构名称</label>
          <input id="create-arch-name" type="text" placeholder="输入架构名称" class="w-full h-9 px-3 text-sm rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
        </div>
        <div>
          <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">需求</label>
          <textarea id="create-arch-aim" rows="3" placeholder="描述需要抽取的实体类型、关系和目标" class="w-full px-3 py-2 text-sm rounded-lg border outline-none resize-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);"></textarea>
        </div>
        <button type="button" @click="triggerCreateArchFiles()" class="w-full flex flex-col items-center justify-center gap-1.5 px-3 py-6 rounded-lg cursor-pointer transition-colors hover:opacity-80" style="background:var(--claude-accent);border:1.5px dashed var(--claude-border);color:var(--claude-foreground);">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="1.8"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <span id="create-arch-files-label" class="text-xs">上传 PDF / Word / TXT 文档</span>
          <span class="text-[10px]" style="color:var(--claude-muted-foreground);opacity:0.75;">支持 PDF、DOC、DOCX、TXT，单个文件最大 50 MB</span>
        </button>
      </div>
      <div id="create-arch-json-panel" class="hidden space-y-3">
        <button type="button" @click="triggerImportArchFile()" class="w-full flex flex-col items-center justify-center gap-1.5 px-3 py-6 rounded-lg cursor-pointer transition-colors hover:opacity-80" style="background:var(--claude-accent);border:1.5px dashed var(--claude-border);color:var(--claude-foreground);">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--claude-brand-500)" stroke-width="1.8"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <span id="import-arch-file-label" class="text-xs">选择 JSON 文件</span>
          <span class="text-[10px]" style="color:var(--claude-muted-foreground);opacity:0.75;">仅支持 JSON，单个文件最大 50 MB</span>
        </button>
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 px-5 py-3" style="border-top:1px solid var(--claude-border);">
      <button type="button" @click="closeModal('modal-new-arch')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button type="button" @click="submitCreateArch()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">创建</button>
    </div>
    <input id="create-arch-files" type="file" class="hidden" multiple accept=".pdf,.docx,.txt" @change="handleCreateArchFiles($event.currentTarget)">
    <input id="import-arch-file" type="file" class="hidden" accept=".json" @change="handleImportArchFile($event.currentTarget)">
  </div>
</div>

<div id="modal-update-arch" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:480px;">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom:1px solid var(--claude-border);">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">更新知识架构</h3>
      <button @click="hideElement('modal-update-arch')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="px-5 py-4 space-y-4 max-h-[520px] overflow-y-auto">
      <div class="flex items-center justify-between">
        <label class="text-xs font-medium" style="color:var(--claude-foreground);">架构更新建议</label>
        <div class="flex items-center gap-2">
          <button type="button" @click="saveArchSuggestion()" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium cursor-pointer transition-colors hover:opacity-80" style="background:var(--claude-background);color:var(--claude-foreground);border:1px solid var(--claude-border);">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
            保存
          </button>
          <button type="button" @click="generateSuggestion()" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-medium cursor-pointer transition-colors hover:opacity-80" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
            生成建议
          </button>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">期望实体类型</label>
        <div class="flex flex-wrap gap-1.5 mb-1.5">
          <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px]" style="background:var(--claude-accent);color:var(--claude-foreground);">
            <input type="text" value="111" class="bg-transparent border-none outline-none text-[11px] px-0 py-0 w-auto min-w-[30px]" style="color:inherit;">
            <button type="button" @click="$event.currentTarget.parentElement.remove()" class="cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);padding:0;line-height:0;">
              <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </div>
        <button type="button" @click="addSuggestionTag(0)" class="inline-flex items-center gap-1 text-xs font-medium cursor-pointer" style="color:var(--claude-brand-500);background:none;border:none;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          添加
        </button>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">非期望实体类型</label>
        <div class="flex flex-wrap gap-1.5 mb-1.5">
          <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px]" style="background:var(--claude-accent);color:var(--claude-foreground);">
            <input type="text" value="Validation and Par" class="bg-transparent border-none outline-none text-[11px] px-0 py-0 w-auto min-w-[30px]" style="color:inherit;">
            <button type="button" @click="$event.currentTarget.parentElement.remove()" class="cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);padding:0;line-height:0;">
              <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          <div class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px]" style="background:var(--claude-accent);color:var(--claude-foreground);">
            <input type="text" value="Technology" class="bg-transparent border-none outline-none text-[11px] px-0 py-0 w-auto min-w-[30px]" style="color:inherit;">
            <button type="button" @click="$event.currentTarget.parentElement.remove()" class="cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);padding:0;line-height:0;">
              <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </div>
        <button type="button" @click="addSuggestionTag(1)" class="inline-flex items-center gap-1 text-xs font-medium cursor-pointer" style="color:var(--claude-brand-500);background:none;border:none;">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          添加
        </button>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">需求澄清建议</label>
        <textarea class="w-full h-24 px-3 py-2 text-xs rounded-lg border outline-none transition-colors resize-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);font-family:var(--claude-font-mono);" placeholder="编辑澄清建议...">The user is interested in entities related to cutting-edge technologies and innovations, with a strong emphasis on environmental sustainability and green technology. They are not interested in entities linked to conventional manufacturing industries.</textarea>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">上传文档</label>
        <div class="flex flex-col items-center justify-center gap-1.5 py-6 px-3 rounded-lg cursor-pointer transition-colors" style="border:1.5px dashed var(--claude-border);background:var(--claude-accent);" @click="clickElement('arch-file-input')">
          <input type="file" id="arch-file-input" class="hidden" multiple @change="uploadArchFiles($event.currentTarget.files)" accept=".pdf,.docx,.txt">
          <div id="arch-file-list" class="hidden order-last w-full mt-2 space-y-1.5"></div>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="1.5"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>
          <span class="text-xs" style="color:var(--claude-muted-foreground);">点击上传 PDF / Word / TXT 文档</span>
          <span class="text-[10px]" style="color:var(--claude-muted-foreground);opacity:0.75;">支持 PDF、DOC、DOCX、TXT，单个文件最大 50 MB</span>
        </div>
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 px-5 py-3" style="border-top:1px solid var(--claude-border);">
      <button @click="hideElement('modal-update-arch')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="submitArchUpdate()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">更新架构</button>
    </div>
  </div>
</div>

  </div>
</template>

<script>
import { createGraphDesignViewController } from '@/controllers/GraphDesignView.js';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'GraphDesignView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({ controller: null }),
  mounted() {
    document.title = "知识图谱设计";
    document.body.className = "h-screen overflow-hidden min-h-0";
    this.controller = createGraphDesignViewController();
  },
  methods: {
    clickElement(id) {
      document.getElementById(id)?.click();
    },
    hideElement(id) {
      document.getElementById(id)?.classList.add('hidden');
    },
    showElement(id) {
      document.getElementById(id)?.classList.remove('hidden');
    },
    addAttr(...args) {
      return this.controller?.addAttr(...args);
    },
    addEntity(...args) {
      return this.controller?.addEntity(...args);
    },
    addRelation(...args) {
      return this.controller?.addRelation(...args);
    },
    addSuggestionTag(...args) {
      return this.controller?.addSuggestionTag(...args);
    },
    changeStyle(...args) {
      return this.controller?.changeStyle(...args);
    },
    closeModal(...args) {
      return this.controller?.closeModal(...args);
    },
    deleteArch(...args) {
      return this.controller?.deleteArch(...args);
    },
    deleteCurrentArch(...args) {
      return this.controller?.deleteCurrentArch(...args);
    },
    deleteSelectedElement(...args) {
      return this.controller?.deleteSelectedElement(...args);
    },
    editSelectedElement(...args) {
      return this.controller?.editSelectedElement(...args);
    },
    exportArchitecture(...args) {
      return this.controller?.exportArchitecture(...args);
    },
    filterGraph(...args) {
      return this.controller?.filterGraph(...args);
    },
    generateSuggestion(...args) {
      return this.controller?.generateSuggestion(...args);
    },
    handleCreateArchFiles(...args) {
      return this.controller?.handleCreateArchFiles(...args);
    },
    handleImportArchFile(...args) {
      return this.controller?.handleImportArchFile(...args);
    },
    hideTooltip(...args) {
      return this.controller?.hideTooltip(...args);
    },
    openModal(...args) {
      return this.controller?.openModal(...args);
    },
    removeAttr(...args) {
      return this.controller?.removeAttr(...args);
    },
    resetZoom(...args) {
      return this.controller?.resetZoom(...args);
    },
    saveArchSuggestion(...args) {
      return this.controller?.saveArchSuggestion(...args);
    },
    setCreateArchMode(...args) {
      return this.controller?.setCreateArchMode(...args);
    },
    selectRelationSource(...args) {
      return this.controller?.selectRelationSource(...args);
    },
    selectRelationTarget(...args) {
      return this.controller?.selectRelationTarget(...args);
    },
    filterRelationEntityList(...args) {
      return this.controller?.filterRelationEntityList(...args);
    },
    showRelationEntityList(...args) {
      return this.controller?.showRelationEntityList(...args);
    },
    showTooltip(...args) {
      return this.controller?.showTooltip(...args);
    },
    submitArchUpdate(...args) {
      return this.controller?.submitArchUpdate(...args);
    },
    submitCreateArch(...args) {
      return this.controller?.submitCreateArch(...args);
    },
    toggleArchDropdown(...args) {
      return this.controller?.toggleArchDropdown(...args);
    },
    toggleDropdown(...args) {
      return this.controller?.toggleDropdown(...args);
    },
    triggerCreateArchFiles(...args) {
      return this.controller?.triggerCreateArchFiles(...args);
    },
    triggerImportArchFile(...args) {
      return this.controller?.triggerImportArchFile(...args);
    },
    uploadArchFiles(...args) {
      return this.controller?.uploadArchFiles(...args);
    },
    zoomIn(...args) {
      return this.controller?.zoomIn(...args);
    },
    zoomOut(...args) {
      return this.controller?.zoomOut(...args);
    },
  },
};
</script>

<style>
@import '../../assets/styles/graph-tooltip.css';

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
@keyframes trace-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }

</style>
