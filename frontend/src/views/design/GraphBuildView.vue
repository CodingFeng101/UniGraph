<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="build" />

<AppSearchDialog />

<div id="app-main" class="h-screen min-h-0 flex flex-col transition-all duration-300" style="margin-left:260px;">
  <header class="h-14 flex items-center justify-between px-5 shrink-0 min-w-0" style="background:var(--claude-card);">
    <div class="flex items-center gap-2">
      <div class="relative" id="graph-dropdown-wrapper-top">
        <button id="graph-dropdown-trigger" type="button" disabled @click="toggleElement('graph-dropdown-top')" class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg transition-colors w-[240px] disabled:cursor-not-allowed disabled:opacity-60" style="background:var(--claude-accent);border:1px solid var(--claude-border);">
          <span class="text-xs font-medium truncate flex-1 text-left" style="color:var(--claude-muted-foreground);">暂无知识图谱</span>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2.5" class="shrink-0"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div id="graph-dropdown-top" class="hidden absolute left-0 top-full mt-1 rounded-lg overflow-hidden z-50 w-[240px]" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
      </div>
    </div>
    <div class="flex items-center gap-1.5 shrink-0">
      <button type="button" @click="showElement('modal-new-graph')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增图谱
      </button>
      <button type="button" @click="showElement('modal-update-graph')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
        更新知识图谱
      </button>
      <button type="button" @click="openModal('modal-entity-build')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新增实体
      </button>
      <button type="button" @click="openModal('modal-relation-build')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
        新增关系
      </button>
      <button type="button" @click="openModal('modal-reasoning')" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a8 8 0 0 0-8 8c0 3.4 2.1 6.3 5 7.5V20a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-2.5c2.9-1.2 5-4.1 5-7.5a8 8 0 0 0-8-8Z"/><path d="M9 22h6"/></svg>
                知识迁移
      </button>
      <button type="button" @click="buildGraphIndex()" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>
        建立索引
      </button>
      <button type="button" @click="exportGraphIndex()" class="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors hover:opacity-80 cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>
        导出索引
      </button>
    </div>
  </header>

  <div class="flex-1 min-h-0 flex">
    <div class="flex-1 min-w-0 relative overflow-hidden" style="background:var(--claude-secondary);">
      <div id="graph-canvas" class="w-full h-full" style="background:var(--claude-background);"></div>
      <div class="absolute bottom-4 left-4 z-20 flex items-center gap-1 p-1 rounded-lg" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-sm);">
        <button data-build-graph-style="database" type="button" @click="changeGraphStyle('database')" class="px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">数据库</button>
        <button data-build-graph-style="minimal" type="button" @click="changeGraphStyle('minimal')" class="px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;color:var(--claude-muted-foreground);border:none;">简约</button>
        <button data-build-graph-style="colorful" type="button" @click="changeGraphStyle('colorful')" class="px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;color:var(--claude-muted-foreground);border:none;">多彩</button>
        <button data-build-graph-style="load" type="button" @click="changeGraphStyle('load')" class="px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;color:var(--claude-muted-foreground);border:none;">负载</button>
      </div>
      <svg viewBox="0 0 960 600" width="100%" height="100%" style="font-family:var(--claude-font-sans);background:var(--claude-background);display:none;">
        <defs>
          <marker id="arrow-default" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="var(--claude-muted-foreground)" opacity="0.35"/>
          </marker>
          <marker id="arrow-brand" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="var(--claude-brand-500)" opacity="0.5"/>
          </marker>
          <marker id="arrow-selected" markerWidth="9" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 9 3.5, 0 7" fill="var(--claude-brand-500)" opacity="0.8"/>
          </marker>
          <filter id="node-shadow" x="-15%" y="-15%" width="130%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="rgba(0,0,0,0.06)"/>
          </filter>
          <filter id="node-shadow-active" x="-20%" y="-20%" width="140%" height="150%">
            <feDropShadow dx="0" dy="3" stdDeviation="8" flood-color="rgba(201,100,66,0.18)"/>
          </filter>
        </defs>

        <pattern id="dotgrid" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
          <circle cx="12" cy="12" r="1" fill="var(--claude-muted)" opacity="0.4"/>
        </pattern>
        <rect width="960" height="600" fill="url(#dotgrid)"/>

        <g @mouseenter="showTooltip($event,'操作','关系','张磊 → VM850<br>类型: 操作<br>来源: enterprise_doc.pdf')">
        <line x1="545" y1="108" x2="590" y2="135" stroke="var(--claude-brand-500)" stroke-width="1.8" opacity="0.4" marker-end="url(#arrow-selected)"/>
        <rect x="543" y="105" width="36" height="18" rx="9" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="0.6"/>
        <text x="561" y="118" text-anchor="middle" font-size="10" font-weight="600" fill="var(--claude-brand-500)" opacity="0.85">操作</text>
        </g>

        <g @mouseenter="showTooltip($event,'安装','关系','VM850 → 主轴 T-001<br>类型: 安装<br>来源: enterprise_doc.pdf')">
        <line x1="640" y1="213" x2="585" y2="453" stroke="var(--claude-brand-500)" stroke-width="1.6" opacity="0.35" marker-end="url(#arrow-brand)"/>
        <rect x="593" y="325" width="36" height="18" rx="9" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="0.6"/>
        <text x="611" y="338" text-anchor="middle" font-size="10" font-weight="500" fill="var(--claude-brand-500)" opacity="0.75">安装</text>
        </g>

        <g @mouseenter="showTooltip($event,'使用','关系','VM850 → 立铣刀 A03<br>类型: 使用<br>来源: enterprise_doc.pdf')">
        <line x1="610" y1="213" x2="430" y2="453" stroke="var(--claude-muted-foreground)" stroke-width="1.4" opacity="0.2" marker-end="url(#arrow-default)"/>
        <rect x="496" y="325" width="36" height="18" rx="9" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="0.6"/>
        <text x="514" y="338" text-anchor="middle" font-size="10" font-weight="500" fill="var(--claude-muted-foreground)" opacity="0.6">使用</text>
        </g>

        <g @mouseenter="showTooltip($event,'精通','关系','张磊 → 数控编程<br>类型: 精通<br>来源: 人员档案_2024Q3.docx')">
        <line x1="415" y1="108" x2="365" y2="140" stroke="var(--claude-muted-foreground)" stroke-width="1.2" opacity="0.18" marker-end="url(#arrow-default)" stroke-dasharray="5 3"/>
        <rect x="361" y="105" width="36" height="18" rx="9" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="0.6"/>
        <text x="379" y="118" text-anchor="middle" font-size="10" font-weight="500" fill="var(--claude-muted-foreground)" opacity="0.5">精通</text>
        </g>

        <g @mouseenter="showTooltip($event,'生产','关系','沈阳机床 → VM850<br>类型: 生产<br>来源: enterprise_doc.pdf')">
        <line x1="678" y1="309" x2="660" y2="213" stroke="var(--claude-muted-foreground)" stroke-width="1.2" opacity="0.18" marker-end="url(#arrow-default)" stroke-dasharray="5 3"/>
        <rect x="650" y="252" width="36" height="18" rx="9" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="0.6"/>
        <text x="668" y="265" text-anchor="middle" font-size="10" font-weight="500" fill="var(--claude-muted-foreground)" opacity="0.5">生产</text>
        </g>

        <g @mouseenter="showTooltip($event,'配合','关系','主轴 T-001 → 立铣刀 A03<br>类型: 配合<br>来源: 设备手册_VM850.pdf')">
        <line x1="506" y1="495" x2="455" y2="495" stroke="var(--claude-muted-foreground)" stroke-width="1.2" opacity="0.18" marker-end="url(#arrow-default)" stroke-dasharray="5 3"/>
        <rect x="462" y="478" width="36" height="18" rx="9" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="0.6"/>
        <text x="480" y="491" text-anchor="middle" font-size="10" font-weight="500" fill="var(--claude-muted-foreground)" opacity="0.5">配合</text>
        </g>

        <g @mouseenter="showTooltip($event,'搭载','关系','主轴 T-001 → 轴承 BR-05<br>类型: 搭载<br>来源: 设备手册_VM850.pdf')">
        <line x1="530" y1="453" x2="330" y2="380" stroke="var(--claude-muted-foreground)" stroke-width="1.2" opacity="0.18" marker-end="url(#arrow-default)" stroke-dasharray="5 3"/>
        <rect x="410" y="406" width="36" height="18" rx="9" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="0.6"/>
        <text x="428" y="419" text-anchor="middle" font-size="10" font-weight="500" fill="var(--claude-muted-foreground)" opacity="0.5">搭载</text>
        </g>

        <g filter="url(#node-shadow-active)" @mouseenter="showTooltip($event,'张磊','操作人员 (实体)','工号: EMP-001<br>技能等级: 高级<br>来源: 人员档案_2024Q3.docx<br>关联关系: 4 条')">
          <rect x="410" y="35" width="140" height="90" rx="12" fill="var(--claude-card)" stroke="var(--claude-brand-500)" stroke-width="2.5"/>
          <rect x="422" y="45" width="48" height="16" rx="8" fill="var(--claude-accent)"/>
          <text x="446" y="56.5" text-anchor="middle" font-size="9" font-weight="600" fill="var(--claude-brand-500)">操作人员</text>
          <text x="422" y="80" font-size="15" font-weight="700" fill="var(--claude-foreground)">张磊</text>
          <text x="422" y="98" font-size="9" fill="var(--claude-muted-foreground)">工号=EMP-001</text>
          <text x="422" y="112" font-size="9" fill="var(--claude-muted-foreground)">技能等级=高级</text>
        </g>

        <g filter="url(#node-shadow)" @mouseenter="showTooltip($event,'VM850','数控机床 (实体)','型号: VM850<br>制造商: 沈阳机床<br>来源: enterprise_doc.pdf<br>关联关系: 3 条')">
          <rect x="577" y="113" width="150" height="100" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <rect x="589" y="123" width="56" height="16" rx="8" fill="var(--claude-accent)"/>
          <text x="617" y="134.5" text-anchor="middle" font-size="9" font-weight="600" fill="var(--claude-brand-500)">数控机床</text>
          <text x="589" y="159" font-size="15" font-weight="700" fill="var(--claude-foreground)">VM850</text>
          <text x="589" y="177" font-size="9" fill="var(--claude-muted-foreground)">型号=VM850</text>
          <text x="589" y="191" font-size="9" fill="var(--claude-muted-foreground)">制造商=沈阳机床</text>
          <text x="589" y="205" font-size="9" fill="var(--claude-muted-foreground)">工作台=800x500mm</text>
        </g>

        <g filter="url(#node-shadow)" @mouseenter="showTooltip($event,'沈阳机床','制造商 (实体)','所在地: 辽宁沈阳<br>来源: enterprise_doc.pdf<br>关联关系: 1 条')">
          <rect x="620" y="309" width="150" height="80" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <rect x="632" y="319" width="48" height="16" rx="8" fill="var(--claude-secondary)"/>
          <text x="656" y="330.5" text-anchor="middle" font-size="9" font-weight="600" fill="var(--claude-muted-foreground)">制造商</text>
          <text x="632" y="357" font-size="14" font-weight="600" fill="var(--claude-foreground)">沈阳机床</text>
          <text x="632" y="375" font-size="9" fill="var(--claude-muted-foreground)">所在地=辽宁沈阳</text>
        </g>

        <g filter="url(#node-shadow)" @mouseenter="showTooltip($event,'主轴 T-001','主轴 (实体)','转速: 8000rpm<br>功率: 7.5kW<br>来源: 设备手册_VM850.pdf<br>关联关系: 3 条')">
          <rect x="506" y="453" width="140" height="90" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <rect x="518" y="463" width="36" height="16" rx="8" fill="var(--claude-accent)"/>
          <text x="536" y="474.5" text-anchor="middle" font-size="9" font-weight="600" fill="var(--claude-brand-500)">主轴</text>
          <text x="518" y="499" font-size="14" font-weight="600" fill="var(--claude-foreground)">主轴 T-001</text>
          <text x="518" y="517" font-size="9" fill="var(--claude-muted-foreground)">转速=8000rpm</text>
          <text x="518" y="531" font-size="9" fill="var(--claude-muted-foreground)">功率=7.5kW</text>
        </g>

        <g filter="url(#node-shadow)" @mouseenter="showTooltip($event,'立铣刀 A03','刀具 (实体)','类型: 立铣刀<br>材料: 硬质合金<br>来源: 刀具规格表_A03.txt<br>关联关系: 2 条')">
          <rect x="315" y="453" width="140" height="90" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <rect x="327" y="463" width="36" height="16" rx="8" fill="var(--claude-secondary)"/>
          <text x="345" y="474.5" text-anchor="middle" font-size="9" font-weight="600" fill="var(--claude-muted-foreground)">刀具</text>
          <text x="327" y="499" font-size="14" font-weight="600" fill="var(--claude-foreground)">立铣刀 A03</text>
          <text x="327" y="517" font-size="9" fill="var(--claude-muted-foreground)">类型=立铣刀</text>
          <text x="327" y="531" font-size="9" fill="var(--claude-muted-foreground)">材料=硬质合金</text>
        </g>

        <g filter="url(#node-shadow)" @mouseenter="showTooltip($event,'轴承 BR-05','轴承 (实体)','型号: BR-05<br>精度: P4<br>来源: 设备手册_VM850.pdf<br>关联关系: 1 条')">
          <rect x="196" y="309" width="140" height="80" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <rect x="208" y="319" width="36" height="16" rx="8" fill="var(--claude-secondary)"/>
          <text x="226" y="330.5" text-anchor="middle" font-size="9" font-weight="600" fill="var(--claude-muted-foreground)">轴承</text>
          <text x="208" y="357" font-size="14" font-weight="600" fill="var(--claude-foreground)">轴承 BR-05</text>
          <text x="208" y="375" font-size="9" fill="var(--claude-muted-foreground)">型号=BR-05, 精度=P4</text>
        </g>

        <g filter="url(#node-shadow)" @mouseenter="showTooltip($event,'数控编程','技能 (实体)','等级: 精通<br>来源: 人员档案_2024Q3.docx<br>关联关系: 1 条')">
          <rect x="243" y="128" width="130" height="70" rx="12" fill="var(--claude-card)" stroke="var(--claude-border)" stroke-width="1"/>
          <rect x="255" y="138" width="48" height="16" rx="8" fill="var(--claude-secondary)"/>
          <text x="279" y="149.5" text-anchor="middle" font-size="9" font-weight="600" fill="var(--claude-muted-foreground)">技能</text>
          <text x="255" y="175" font-size="13" font-weight="600" fill="var(--claude-foreground)">数控编程</text>
          <text x="255" y="189" font-size="9" fill="var(--claude-muted-foreground)">等级=精通</text>
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
          <button type="button" @click="hideTooltip();editSelected()" class="graph-hover-card__action">
            <i data-lucide="pencil-line" aria-hidden="true"></i><span>编辑</span>
          </button>
          <button type="button" @click="hideTooltip();deleteSelected()" class="graph-hover-card__action graph-hover-card__action--delete">
            <i data-lucide="trash-2" aria-hidden="true"></i><span>删除</span>
          </button>
        </div>
      </div>

      <div class="absolute top-3 left-3 z-10">
        <div class="flex items-center gap-2 h-9 w-[240px] px-3 rounded-lg" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-md);">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-muted-foreground);flex-shrink:0;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input id="build-graph-search" type="text" @input="filterGraph(false)" @keyup.enter="filterGraph(true)" placeholder="搜索实体或关系..." class="flex-1 min-w-0 bg-transparent border-none outline-none text-xs" style="color:var(--claude-foreground);">
        </div>
      </div>

      <div class="absolute bottom-4 right-4 z-10 flex flex-row gap-0.5 rounded-lg overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-sm);">
        <button @click="zoomIn()" class="w-8 h-8 flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);" aria-label="放大">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
        </button>
        <div style="width:1px;background:var(--claude-border);"></div>
        <button @click="zoomOut()" class="w-8 h-8 flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);" aria-label="缩小">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
        </button>
        <div style="width:1px;background:var(--claude-border);"></div>
        <button @click="fitCanvas()" class="w-8 h-8 flex items-center justify-center transition-colors hover:opacity-70 cursor-pointer" style="background:transparent;border:none;color:var(--claude-foreground);" aria-label="适应画布" title="适应画布">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
        </button>
      </div>
    </div>
  </div>
</div>

<TaskCenter />



<div id="modal-new-graph" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:420px;">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom:1px solid var(--claude-border);">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">新增图谱</h3>
      <button @click="hideElement('modal-new-graph')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="px-5 py-4 space-y-4">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">图谱名称</label>
        <input id="new-graph-name" type="text" placeholder="输入知识图谱名称" class="w-full h-9 px-3 text-sm rounded-lg border outline-none transition-colors" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">选择知识架构</label>
        <div class="relative">
          <button id="arch-modal-trigger" type="button" disabled @click="toggleDropdown('arch-dropdown-modal')" class="w-full h-9 px-3 text-sm rounded-lg border flex items-center justify-between outline-none transition-colors disabled:cursor-not-allowed disabled:opacity-60" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-muted-foreground);">
            <span id="arch-modal-value">暂无知识架构</span>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2" class="shrink-0"><polyline points="6 9 12 15 18 9"/></svg>
          </button>
          <div id="arch-dropdown-modal" class="hidden absolute left-0 top-full mt-1 rounded-lg overflow-hidden z-50 w-full" style="background:#fff;border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">上传文档</label>
        <input id="new-graph-files" type="file" class="hidden" multiple accept=".pdf,.docx,.txt" @change="onNewGraphFilesSelected($event.currentTarget)">
        <div class="flex flex-col items-center justify-center gap-1.5 py-6 px-3 rounded-lg cursor-pointer" style="border:1.5px dashed var(--claude-border);background:var(--claude-accent);" @click="clickElement('new-graph-files')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="1.8"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>
          <span id="new-graph-files-label" class="text-xs" style="color:var(--claude-muted-foreground);">上传 PDF/Word/TXT 文档</span>
          <span class="text-[10px]" style="color:var(--claude-muted-foreground);opacity:0.75;">支持 PDF、DOC、DOCX、TXT，单个文件最大 50 MB</span>
        </div>
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 px-5 py-3" style="border-top:1px solid var(--claude-border);">
      <button @click="hideElement('modal-new-graph')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="submitNewGraph()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">创建</button>
    </div>
  </div>
</div>

<div id="modal-update-graph" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl overflow-hidden" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-xl);width:420px;">
    <div class="flex items-center justify-between px-5 py-4" style="border-bottom:1px solid var(--claude-border);">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">更新知识图谱</h3>
      <button @click="hideElement('modal-update-graph')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="px-5 py-4 space-y-4">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">上传文档</label>
        <input type="file" id="update-graph-file" class="hidden" @change="onUpdateFileSelected($event.currentTarget)" accept=".pdf,.docx,.txt">
        <div class="flex flex-col items-center justify-center gap-1.5 py-6 px-3 rounded-lg cursor-pointer" style="border:1.5px dashed var(--claude-border);background:var(--claude-accent);" @click="triggerUpdateFile()">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--claude-muted-foreground)" stroke-width="1.8"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>
          <span id="update-graph-file-label" class="text-xs" style="color:var(--claude-muted-foreground);">上传 PDF/Word/TXT 文档</span>
          <span class="text-[10px]" style="color:var(--claude-muted-foreground);opacity:0.75;">支持 PDF、DOC、DOCX、TXT，单个文件最大 50 MB</span>
        </div>
      </div>
    </div>
    <div class="flex items-center justify-end gap-2 px-5 py-3" style="border-top:1px solid var(--claude-border);">
      <button @click="hideElement('modal-update-graph')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="submitUpdateGraph()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer inline-flex items-center gap-1.5" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">
        提交更新任务
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
    </div>
  </div>
</div>

<div id="modal-entity-build" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl p-5 w-[420px] max-w-[calc(100vw-32px)] max-h-[calc(100dvh-32px)] overflow-y-auto" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">新增实体</h3>
      <button @click="closeModal('modal-entity-build')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="space-y-3">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">实体类型</label>
        <div class="relative">
          <input id="entity-type-input" type="text" autocomplete="off" disabled data-value="" @focus="showEntityTypeList()" @input="filterEntityTypeList()" placeholder="搜索或选择实体类型" class="w-full h-9 px-3 text-sm rounded-lg border outline-none disabled:cursor-not-allowed disabled:opacity-60" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
          <div id="entity-type-dropdown" class="hidden absolute left-0 top-full mt-1 rounded-lg overflow-x-hidden overflow-y-auto overscroll-contain z-50 w-full max-h-40" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">实体名称</label>
        <input type="text" id="entity-name-input" class="w-full h-9 px-3 text-sm rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="输入实体名称">
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">实体属性</label>
        <div id="entity-attributes" class="space-y-2">
          <div class="flex items-center gap-1.5">
            <input type="text" class="flex-1 min-w-0 h-8 px-2 text-xs rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="属性名">
            <span class="shrink-0 text-xs" style="color:var(--claude-muted-foreground);">=</span>
            <input type="text" class="flex-1 min-w-0 h-8 px-2 text-xs rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="属性值">
            <button type="button" @click="$event.currentTarget.parentElement.remove()" class="w-7 h-7 shrink-0 flex items-center justify-center rounded cursor-pointer transition-colors hover:opacity-80" style="background:var(--claude-primary);border:none;color:var(--claude-primary-foreground);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg></button>
          </div>
        </div>
        <button type="button" @click="addEntityAttribute()" class="mt-2 text-xs font-medium cursor-pointer transition-colors hover:opacity-70" style="background:none;border:none;color:var(--claude-primary);">+ 添加属性</button>
      </div>
    </div>
    <div class="flex justify-end gap-2 mt-4">
      <button @click="closeModal('modal-entity-build')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="submitEntity()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">创建</button>
    </div>
  </div>
</div>

<div id="modal-relation-build" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl p-5 w-[460px] max-w-[calc(100vw-32px)] max-h-[calc(100dvh-32px)] overflow-y-auto" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">新增关系</h3>
      <button @click="closeModal('modal-relation-build')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="space-y-3">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">关系类型</label>
        <div class="relative">
          <input id="relation-type-input" type="text" autocomplete="off" disabled data-value="" @focus="showRelationTypeList()" @input="filterRelationTypeList()" placeholder="搜索或选择关系类型" class="w-full h-9 px-3 text-sm rounded-lg border outline-none disabled:cursor-not-allowed disabled:opacity-60" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
          <div id="relation-type-dropdown" class="hidden absolute left-0 top-full mt-1 rounded-lg overflow-x-hidden overflow-y-auto overscroll-contain z-50 w-full max-h-36" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">关系名称</label>
        <input id="relation-name-input" type="text" placeholder="输入关系名称" class="w-full h-9 px-3 text-sm rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">关系描述</label>
        <textarea id="relation-description-input" rows="2" placeholder="描述该关系的含义" class="w-full px-3 py-2 text-sm rounded-lg border outline-none resize-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);"></textarea>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">头实体</label>
        <div class="relative">
          <input type="text" id="head-entity-input" @input="filterEntityList('head-entity')" @focus="showEntityList('head-entity')" class="w-full h-9 px-3 text-sm rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="搜索或选择头实体">
          <div id="head-entity-list" class="hidden absolute left-0 top-full mt-1 rounded-lg overflow-x-hidden z-50 w-full max-h-32 overflow-y-auto overscroll-contain" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
        </div>
      </div>
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">尾实体</label>
        <div class="relative">
          <input type="text" id="tail-entity-input" @input="filterEntityList('tail-entity')" @focus="showEntityList('tail-entity')" class="w-full h-9 px-3 text-sm rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);" placeholder="搜索或选择尾实体">
          <div id="tail-entity-list" class="hidden absolute left-0 bottom-full mb-1 rounded-lg overflow-x-hidden z-50 w-full max-h-32 overflow-y-auto overscroll-contain" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);"></div>
        </div>
      </div>
    </div>
    <div class="flex justify-end gap-2 mt-4">
      <button @click="closeModal('modal-relation-build')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="submitRelation()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">创建</button>
    </div>
  </div>
</div>

<div id="modal-reasoning" class="hidden fixed inset-0 z-[100] flex items-center justify-center" style="background:rgba(0,0,0,0.3);">
  <div class="rounded-xl p-4 w-[400px]" style="background:var(--claude-card);border:1px solid var(--claude-border);box-shadow:var(--claude-shadow-lg);">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-sm font-semibold" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">知识迁移</h3>
      <button @click="closeModal('modal-reasoning')" class="p-1 transition-opacity hover:opacity-70 cursor-pointer" style="background:none;border:none;color:var(--claude-muted-foreground);"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
    </div>
    <div class="space-y-3">
      <div>
        <label class="block text-xs font-medium mb-1.5" style="color:var(--claude-foreground);">迁移深度</label>
        <div class="flex items-center gap-2">
          <input id="reasoning-depth" type="number" min="1" max="10" value="2" class="w-24 h-9 px-3 text-sm rounded-lg border outline-none" style="background:var(--claude-background);border-color:var(--claude-border);color:var(--claude-foreground);">
          <span class="text-xs" style="color:var(--claude-muted-foreground);">跳（建议从较小深度开始）</span>
        </div>
      </div>
      <div class="p-3 rounded-lg" style="background:var(--claude-background);border:1px solid var(--claude-border);">
        <p class="text-xs font-medium mb-1" style="color:var(--claude-foreground);">关于迁移深度</p>
        <p class="text-xs leading-relaxed" style="color:var(--claude-muted-foreground);">迁移深度表示会探索多少层知识迁移关系。较小深度（1-2）更快，适合简单迁移任务。较大深度（3-5）可发现更复杂的关系网络，但耗时更长。建议先从较小深度开始，再根据结果逐步增加。</p>
      </div>
    </div>
    <div class="flex justify-end gap-2 mt-4">
      <button @click="closeModal('modal-reasoning')" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-secondary);color:var(--claude-secondary-foreground);border:none;">取消</button>
      <button @click="startKnowledgeInference()" class="px-4 py-2 rounded-lg text-xs font-medium cursor-pointer" style="background:var(--claude-primary);color:var(--claude-primary-foreground);border:none;">开始迁移</button>
    </div>
  </div>
</div>

  </div>
</template>

<script>
import { createGraphBuildViewController } from '@/controllers/GraphBuildView.js';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'GraphBuildView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({ controller: null }),
  mounted() {
    document.title = "知识图谱构建";
    document.body.className = "h-screen overflow-hidden min-h-0";
    this.controller = createGraphBuildViewController();
  },
  beforeUnmount() {
    this.controller?.destroy?.();
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
    toggleElement(id) {
      document.getElementById(id)?.classList.toggle('hidden');
    },
    addEntityAttribute(...args) {
      return this.controller?.addEntityAttribute(...args);
    },
    buildGraphIndex(...args) {
      return this.controller?.buildGraphIndex(...args);
    },
    closeModal(...args) {
      return this.controller?.closeModal(...args);
    },
    deleteSelected(...args) {
      return this.controller?.deleteSelected(...args);
    },
    deleteCurrentKnowledgeGraph(...args) {
      return this.controller?.deleteCurrentKnowledgeGraph(...args);
    },
    editSelected(...args) {
      return this.controller?.editSelected(...args);
    },
    exportGraphIndex(...args) {
      return this.controller?.exportGraphIndex(...args);
    },
    filterGraph(...args) {
      return this.controller?.filterGraph(...args);
    },
    filterEntityList(...args) {
      return this.controller?.filterEntityList(...args);
    },
    fitCanvas(...args) {
      return this.controller?.fitCanvas(...args);
    },
    hideTooltip(...args) {
      return this.controller?.hideTooltip(...args);
    },
    onNewGraphFilesSelected(...args) {
      return this.controller?.onNewGraphFilesSelected(...args);
    },
    onUpdateFileSelected(...args) {
      return this.controller?.onUpdateFileSelected(...args);
    },
    openModal(...args) {
      return this.controller?.openModal(...args);
    },
    selectArch(...args) {
      return this.controller?.selectArch(...args);
    },
    selectEntity(...args) {
      return this.controller?.selectEntity(...args);
    },
    selectEntityType(...args) {
      return this.controller?.selectEntityType(...args);
    },
    filterEntityTypeList(...args) {
      return this.controller?.filterEntityTypeList(...args);
    },
    showEntityTypeList(...args) {
      return this.controller?.showEntityTypeList(...args);
    },
    filterRelationTypeList(...args) {
      return this.controller?.filterRelationTypeList(...args);
    },
    showRelationTypeList(...args) {
      return this.controller?.showRelationTypeList(...args);
    },
    changeGraphStyle(...args) {
      return this.controller?.changeGraphStyle(...args);
    },
    selectRelationType(...args) {
      return this.controller?.selectRelationType(...args);
    },
    showToast(...args) {
      return this.controller?.showToast(...args);
    },
    showEntityList(...args) {
      return this.controller?.showEntityList(...args);
    },
    showTooltip(...args) {
      return this.controller?.showTooltip(...args);
    },
    startKnowledgeInference(...args) {
      return this.controller?.startKnowledgeInference(...args);
    },
    submitEntity(...args) {
      return this.controller?.submitEntity(...args);
    },
    submitNewGraph(...args) {
      return this.controller?.submitNewGraph(...args);
    },
    submitRelation(...args) {
      return this.controller?.submitRelation(...args);
    },
    submitUpdateGraph(...args) {
      return this.controller?.submitUpdateGraph(...args);
    },
    toggleDropdown(...args) {
      return this.controller?.toggleDropdown(...args);
    },
    triggerUpdateFile(...args) {
      return this.controller?.triggerUpdateFile(...args);
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
