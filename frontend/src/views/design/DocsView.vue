<template>
  <div class="h-screen overflow-hidden min-h-0">
<AppSidebar active="app" />

<AppSearchDialog />

<!-- MAIN CONTENT AREA -->
<div id="app-main" class="flex h-screen min-h-0 transition-all duration-300" style="margin-left:260px;">

  <!-- Zone 1: Doc Navigation Sidebar (220px) -->
  <nav class="w-[220px] shrink-0 border-r flex flex-col h-full overflow-hidden" style="background:var(--claude-card);border-color:var(--claude-border);">
    <!-- Search -->
    <div class="p-3 pb-2">
      <div class="relative">
        <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-muted-foreground);"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" placeholder="搜索文档..." class="w-full pl-8 pr-3 py-[7px] rounded-lg text-[13px] outline-none transition-colors" style="background:var(--claude-background);border:1px solid var(--claude-border);color:var(--claude-foreground);font-family:var(--claude-font-sans);" onfocus="this.style.borderColor='var(--claude-ring)'" onblur="this.style.borderColor='var(--claude-border)'">
      </div>
    </div>

    <!-- Doc categories -->
    <div class="flex-1 overflow-y-auto px-2 py-1" style="scrollbar-width:thin;">
      <!-- 快速开始 -->
      <div class="mb-4">
        <button @click="$event.currentTarget.nextElementSibling.classList.toggle('hidden');$event.currentTarget.querySelector('.chevron').classList.toggle('rotate-90')" class="flex items-center gap-1.5 w-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] cursor-pointer" style="color:var(--claude-muted-foreground);background:none;border:none;font-family:var(--claude-font-sans);">
          <svg class="chevron transition-transform rotate-90" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 6 15 12 9 18"/></svg>
          快速开始
        </button>
        <div class="mt-0.5 space-y-0.5">
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            安装与部署指南
          </a>
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            第一个知识图谱
          </a>
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            API 快速上手
          </a>
        </div>
      </div>

      <!-- API 参考 -->
      <div class="mb-4">
        <button @click="$event.currentTarget.nextElementSibling.classList.toggle('hidden');$event.currentTarget.querySelector('.chevron').classList.toggle('rotate-90')" class="flex items-center gap-1.5 w-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] cursor-pointer" style="color:var(--claude-muted-foreground);background:none;border:none;font-family:var(--claude-font-sans);">
          <svg class="chevron transition-transform rotate-90" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 6 15 12 9 18"/></svg>
          API 参考
        </button>
        <div class="mt-0.5 space-y-0.5">
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer font-medium" style="background:var(--claude-accent);color:var(--claude-foreground);">
            知识架构 API
          </a>
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            知识图谱 API
          </a>
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            问答检索 API
          </a>
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            任务队列 API
          </a>
        </div>
      </div>

      <!-- 使用指南 -->
      <div class="mb-4">
        <button @click="$event.currentTarget.nextElementSibling.classList.toggle('hidden');$event.currentTarget.querySelector('.chevron').classList.toggle('rotate-90')" class="flex items-center gap-1.5 w-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] cursor-pointer" style="color:var(--claude-muted-foreground);background:none;border:none;font-family:var(--claude-font-sans);">
          <svg class="chevron transition-transform rotate-90" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 6 15 12 9 18"/></svg>
          使用指南
        </button>
        <div class="mt-0.5 space-y-0.5">
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            架构设计最佳实践
          </a>
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            知识推理配置指南
          </a>
          <a href="#" @click="selectDocNav($event.currentTarget)" class="doc-nav-item flex items-center gap-2 px-2 py-[5px] rounded-md text-[13px] transition-colors cursor-pointer hover:opacity-80" style="color:var(--claude-muted-foreground);">
            索引优化指南
          </a>
        </div>
      </div>
    </div>
  </nav>

  <!-- Zone 2: Content Area (flex-1) -->
  <main class="flex-1 min-w-0 h-full overflow-y-auto" style="background:var(--claude-background);" data-scroll-region="primary">
    <div class="flex min-h-full">

      <!-- Content + inline TOC wrapper -->
      <div class="flex-1 min-w-0">
        <div class="max-w-[820px] mx-auto px-10 py-8">

          <!-- Breadcrumb -->
          <nav class="flex items-center gap-1.5 text-[13px] mb-6" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-sans);">
            <a href="#" class="hover:underline" style="color:var(--claude-muted-foreground);">技术文档</a>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="opacity:0.5;"><polyline points="9 6 15 12 9 18"/></svg>
            <a href="#" class="hover:underline" style="color:var(--claude-muted-foreground);">API 参考</a>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="opacity:0.5;"><polyline points="9 6 15 12 9 18"/></svg>
            <span style="color:var(--claude-foreground);">知识架构 API</span>
          </nav>

          <!-- Document Title -->
          <h1 class="text-[24px] font-normal leading-tight mb-2" style="font-family:var(--claude-font-display);color:var(--claude-foreground);">知识架构 API</h1>
          <p class="text-sm leading-relaxed mb-8" style="color:var(--claude-muted-foreground);max-width:640px;">管理知识架构的创建、查询、更新和删除。知识架构是知识图谱的骨架定义，描述了图谱的结构和语义模型。</p>

          <!-- 概述 -->
          <section class="mb-10" id="overview">
            <h2 class="text-[18px] font-semibold mb-4" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">概述</h2>
            <p class="text-sm leading-relaxed mb-4" style="color:var(--claude-muted-foreground);">
              知识架构 API 提供了对知识架构的完整 CRUD 操作。每个架构定义了一组实体类型、关系类型及其属性约束，作为知识图谱的数据模型基础。
            </p>
            <div class="rounded-lg p-4 text-sm leading-relaxed" style="background:var(--claude-accent);color:var(--claude-accent-foreground);">
              <strong>Base URL</strong>
              <code class="block mt-1 text-[13px]" style="font-family:var(--claude-font-mono);color:var(--claude-foreground);">https://api.unigraph.ai/v1/schemas</code>
            </div>

            <!-- Auth note -->
            <div class="mt-4 rounded-lg p-4 text-sm leading-relaxed flex items-start gap-3" style="background:var(--claude-card);border:1px solid var(--claude-border);">
              <svg class="shrink-0 mt-0.5" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-primary);"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
              <div>
                <p class="font-medium text-[13px] mb-1" style="color:var(--claude-foreground);">认证方式</p>
                <p class="text-[13px] leading-relaxed" style="color:var(--claude-muted-foreground);">所有 API 请求需要在 Header 中携带 <code style="font-family:var(--claude-font-mono);background:var(--claude-muted);padding:1px 5px;border-radius:4px;font-size:12px;">Authorization: Bearer &lt;API_KEY&gt;</code></p>
              </div>
            </div>
          </section>

          <!-- 创建架构 -->
          <section class="mb-10" id="create">
            <div class="flex items-center gap-3 mb-4">
              <h2 class="text-[18px] font-semibold" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">创建架构</h2>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium" style="background:var(--claude-success-500);color:var(--claude-primary-foreground);">POST</span>
            </div>
            <p class="text-sm leading-relaxed mb-4" style="color:var(--claude-muted-foreground);">创建一个新的知识架构。请求体需包含架构名称、描述和 Schema 定义。</p>

            <!-- Code block -->
            <div class="relative rounded-lg overflow-hidden mb-3" style="background:var(--claude-foreground);">
              <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color:rgba(255,255,255,0.1);">
                <span class="text-[11px] font-medium" style="color:rgba(255,255,255,0.5);font-family:var(--claude-font-mono);">cURL</span>
                <button @click="copyCode($event.currentTarget)" class="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors cursor-pointer hover:opacity-80" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;font-family:var(--claude-font-sans);">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  <span>复制</span>
                </button>
              </div>
              <pre class="px-4 py-3 overflow-x-auto text-[13px] leading-relaxed" style="color:rgba(255,255,255,0.85);font-family:var(--claude-font-mono);margin:0;"><code>curl -X POST https://api.unigraph.ai/v1/schemas \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "enterprise_knowledge",
    "description": "企业知识管理架构",
    "entities": [
      {
        "type": "Department",
        "properties": {
          "name": "string",
          "code": "string",
          "head_count": "integer"
        }
      },
      {
        "type": "Employee",
        "properties": {
          "name": "string",
          "role": "string",
          "department_id": "reference"
        }
      }
    ],
    "relations": [
      {
        "type": "belongs_to",
        "source": "Employee",
        "target": "Department",
        "properties": {
          "since": "date",
          "position": "string"
        }
      }
    ]
  }'</code></pre>
            </div>

            <!-- Response -->
            <p class="text-[13px] font-medium mb-2" style="color:var(--claude-foreground);">响应示例</p>
            <div class="relative rounded-lg overflow-hidden" style="background:var(--claude-foreground);">
              <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color:rgba(255,255,255,0.1);">
                <span class="text-[11px] font-medium" style="color:rgba(255,255,255,0.5);font-family:var(--claude-font-mono);">JSON &middot; 200</span>
                <button @click="copyCode($event.currentTarget)" class="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors cursor-pointer hover:opacity-80" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;font-family:var(--claude-font-sans);">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  <span>复制</span>
                </button>
              </div>
              <pre class="px-4 py-3 overflow-x-auto text-[13px] leading-relaxed" style="color:rgba(255,255,255,0.85);font-family:var(--claude-font-mono);margin:0;"><code>{
  "id": "schema_abc123",
  "name": "enterprise_knowledge",
  "description": "企业知识管理架构",
  "version": 1,
  "status": "active",
  "entity_count": 2,
  "relation_count": 1,
  "created_at": "2025-12-20T08:30:00Z",
  "updated_at": "2025-12-20T08:30:00Z"
}</code></pre>
            </div>
          </section>

          <!-- 获取架构详情 -->
          <section class="mb-10" id="retrieve">
            <div class="flex items-center gap-3 mb-4">
              <h2 class="text-[18px] font-semibold" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">获取架构详情</h2>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium" style="background:var(--claude-brand-300);color:var(--claude-foreground);">GET</span>
            </div>
            <p class="text-sm leading-relaxed mb-4" style="color:var(--claude-muted-foreground);">根据架构 ID 获取完整的架构定义，包括所有实体类型和关系类型的详细配置。</p>

            <div class="relative rounded-lg overflow-hidden mb-3" style="background:var(--claude-foreground);">
              <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color:rgba(255,255,255,0.1);">
                <span class="text-[11px] font-medium" style="color:rgba(255,255,255,0.5);font-family:var(--claude-font-mono);">cURL</span>
                <button @click="copyCode($event.currentTarget)" class="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors cursor-pointer hover:opacity-80" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;font-family:var(--claude-font-sans);">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  <span>复制</span>
                </button>
              </div>
              <pre class="px-4 py-3 overflow-x-auto text-[13px] leading-relaxed" style="color:rgba(255,255,255,0.85);font-family:var(--claude-font-mono);margin:0;"><code>curl -X GET https://api.unigraph.ai/v1/schemas/schema_abc123 \
  -H "Authorization: Bearer ${API_KEY}"</code></pre>
            </div>

            <p class="text-[13px] font-medium mb-2" style="color:var(--claude-foreground);">响应示例</p>
            <div class="relative rounded-lg overflow-hidden" style="background:var(--claude-foreground);">
              <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color:rgba(255,255,255,0.1);">
                <span class="text-[11px] font-medium" style="color:rgba(255,255,255,0.5);font-family:var(--claude-font-mono);">JSON &middot; 200</span>
                <button @click="copyCode($event.currentTarget)" class="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors cursor-pointer hover:opacity-80" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;font-family:var(--claude-font-sans);">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  <span>复制</span>
                </button>
              </div>
              <pre class="px-4 py-3 overflow-x-auto text-[13px] leading-relaxed" style="color:rgba(255,255,255,0.85);font-family:var(--claude-font-mono);margin:0;"><code>{
  "id": "schema_abc123",
  "name": "enterprise_knowledge",
  "description": "企业知识管理架构",
  "version": 1,
  "status": "active",
  "entities": [
    {
      "type": "Department",
      "properties": {
        "name": { "type": "string", "required": true },
        "code": { "type": "string", "required": true },
        "head_count": { "type": "integer", "required": false }
      }
    },
    {
      "type": "Employee",
      "properties": {
        "name": { "type": "string", "required": true },
        "role": { "type": "string", "required": true },
        "department_id": { "type": "reference", "target": "Department" }
      }
    }
  ],
  "relations": [
    {
      "type": "belongs_to",
      "source": "Employee",
      "target": "Department",
      "properties": {
        "since": { "type": "date" },
        "position": { "type": "string" }
      }
    }
  ],
  "created_at": "2025-12-20T08:30:00Z",
  "updated_at": "2025-12-20T08:30:00Z"
}</code></pre>
            </div>
          </section>

          <!-- 更新架构 -->
          <section class="mb-10" id="update">
            <div class="flex items-center gap-3 mb-4">
              <h2 class="text-[18px] font-semibold" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">更新架构</h2>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium" style="background:var(--claude-primary);color:var(--claude-primary-foreground);">PUT</span>
            </div>
            <p class="text-sm leading-relaxed mb-4" style="color:var(--claude-muted-foreground);">更新已有架构的定义。支持增量更新，仅需传递需要变更的字段。架构版本号将自动递增。</p>

            <div class="relative rounded-lg overflow-hidden mb-3" style="background:var(--claude-foreground);">
              <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color:rgba(255,255,255,0.1);">
                <span class="text-[11px] font-medium" style="color:rgba(255,255,255,0.5);font-family:var(--claude-font-mono);">cURL</span>
                <button @click="copyCode($event.currentTarget)" class="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors cursor-pointer hover:opacity-80" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;font-family:var(--claude-font-sans);">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  <span>复制</span>
                </button>
              </div>
              <pre class="px-4 py-3 overflow-x-auto text-[13px] leading-relaxed" style="color:rgba(255,255,255,0.85);font-family:var(--claude-font-mono);margin:0;"><code>curl -X PUT https://api.unigraph.ai/v1/schemas/schema_abc123 \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "企业知识管理架构 v2",
    "entities": [
      {
        "type": "Project",
        "properties": {
          "name": "string",
          "status": "string",
          "owner": "reference"
        }
      }
    ]
  }'</code></pre>
            </div>

            <p class="text-[13px] font-medium mb-2" style="color:var(--claude-foreground);">响应示例</p>
            <div class="relative rounded-lg overflow-hidden" style="background:var(--claude-foreground);">
              <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color:rgba(255,255,255,0.1);">
                <span class="text-[11px] font-medium" style="color:rgba(255,255,255,0.5);font-family:var(--claude-font-mono);">JSON &middot; 200</span>
                <button @click="copyCode($event.currentTarget)" class="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors cursor-pointer hover:opacity-80" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;font-family:var(--claude-font-sans);">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  <span>复制</span>
                </button>
              </div>
              <pre class="px-4 py-3 overflow-x-auto text-[13px] leading-relaxed" style="color:rgba(255,255,255,0.85);font-family:var(--claude-font-mono);margin:0;"><code>{
  "id": "schema_abc123",
  "name": "enterprise_knowledge",
  "description": "企业知识管理架构 v2",
  "version": 2,
  "status": "active",
  "entity_count": 3,
  "relation_count": 1,
  "created_at": "2025-12-20T08:30:00Z",
  "updated_at": "2025-12-20T10:15:00Z"
}</code></pre>
            </div>
          </section>

          <!-- 删除架构 -->
          <section class="mb-16" id="delete">
            <div class="flex items-center gap-3 mb-4">
              <h2 class="text-[18px] font-semibold" style="font-family:var(--claude-font-sans);color:var(--claude-foreground);">删除架构</h2>
              <span class="px-2 py-0.5 rounded text-[11px] font-medium" style="background:var(--claude-destructive);color:var(--claude-destructive-foreground);">DELETE</span>
            </div>
            <p class="text-sm leading-relaxed mb-4" style="color:var(--claude-muted-foreground);">删除指定的知识架构。已关联图谱的架构无法直接删除，需先解除关联。</p>

            <div class="rounded-lg p-4 text-[13px] leading-relaxed flex items-start gap-3 mb-4" style="background:var(--claude-card);border:1px solid var(--claude-destructive);border-left:3px solid var(--claude-destructive);">
              <svg class="shrink-0 mt-0.5" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color:var(--claude-destructive);"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              <div>
                <p class="font-medium mb-0.5" style="color:var(--claude-destructive);">危险操作</p>
                <p style="color:var(--claude-muted-foreground);">此操作不可逆。删除架构后，基于该架构的知识图谱将无法继续使用 Schema 校验功能。</p>
              </div>
            </div>

            <div class="relative rounded-lg overflow-hidden mb-3" style="background:var(--claude-foreground);">
              <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color:rgba(255,255,255,0.1);">
                <span class="text-[11px] font-medium" style="color:rgba(255,255,255,0.5);font-family:var(--claude-font-mono);">cURL</span>
                <button @click="copyCode($event.currentTarget)" class="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors cursor-pointer hover:opacity-80" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;font-family:var(--claude-font-sans);">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  <span>复制</span>
                </button>
              </div>
              <pre class="px-4 py-3 overflow-x-auto text-[13px] leading-relaxed" style="color:rgba(255,255,255,0.85);font-family:var(--claude-font-mono);margin:0;"><code>curl -X DELETE https://api.unigraph.ai/v1/schemas/schema_abc123 \
  -H "Authorization: Bearer ${API_KEY}"</code></pre>
            </div>

            <p class="text-[13px] font-medium mb-2" style="color:var(--claude-foreground);">响应示例</p>
            <div class="relative rounded-lg overflow-hidden" style="background:var(--claude-foreground);">
              <div class="flex items-center justify-between px-4 py-2 border-b" style="border-color:rgba(255,255,255,0.1);">
                <span class="text-[11px] font-medium" style="color:rgba(255,255,255,0.5);font-family:var(--claude-font-mono);">JSON &middot; 204</span>
                <button @click="copyCode($event.currentTarget)" class="flex items-center gap-1.5 px-2 py-1 rounded text-[11px] transition-colors cursor-pointer hover:opacity-80" style="background:rgba(255,255,255,0.1);color:rgba(255,255,255,0.7);border:none;font-family:var(--claude-font-sans);">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  <span>复制</span>
                </button>
              </div>
              <pre class="px-4 py-3 overflow-x-auto text-[13px] leading-relaxed" style="color:rgba(255,255,255,0.85);font-family:var(--claude-font-mono);margin:0;"><code>{
  "success": true,
  "message": "架构已成功删除",
  "deleted_id": "schema_abc123"
}</code></pre>
            </div>
          </section>

        </div>
      </div>

      <!-- Right-side TOC (desktop only, like Anthropic docs) -->
      <div class="hidden xl:block w-[160px] shrink-0">
        <div class="sticky top-8 pl-6 pr-4 py-8">
          <p class="text-[10px] font-semibold uppercase tracking-[0.08em] mb-3" style="color:var(--claude-muted-foreground);font-family:var(--claude-font-sans);">目录</p>
          <nav class="space-y-1.5">
            <a href="#overview" class="toc-link block text-[12px] py-0.5 transition-colors hover:opacity-80" style="color:var(--claude-muted-foreground);text-decoration:none;">概述</a>
            <a href="#create" class="toc-link block text-[12px] py-0.5 transition-colors hover:opacity-80" style="color:var(--claude-muted-foreground);text-decoration:none;">创建架构</a>
            <a href="#retrieve" class="toc-link block text-[12px] py-0.5 transition-colors hover:opacity-80" style="color:var(--claude-muted-foreground);text-decoration:none;">获取架构详情</a>
            <a href="#update" class="toc-link block text-[12px] py-0.5 transition-colors hover:opacity-80" style="color:var(--claude-muted-foreground);text-decoration:none;">更新架构</a>
            <a href="#delete" class="toc-link block text-[12px] py-0.5 transition-colors hover:opacity-80" style="color:var(--claude-muted-foreground);text-decoration:none;">删除架构</a>
          </nav>
        </div>
      </div>

    </div>

    <TaskCenter />


  </main>

</div>

  </div>
</template>

<script>
import { createDocsViewController } from '@/controllers/DocsView.js';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppSearchDialog from '@/components/layout/AppSearchDialog.vue';
import TaskCenter from '@/components/task/TaskCenter.vue';

export default {
  name: 'DocsView',
  components: { AppSidebar, AppSearchDialog, TaskCenter },
  data: () => ({ controller: null }),
  mounted() {
    document.title = "文档";
    document.body.className = "h-screen overflow-hidden min-h-0";
    this.controller = createDocsViewController();
  },
  methods: {
    copyCode(...args) {
      return this.controller?.copyCode(...args);
    },
    selectDocNav(...args) {
      return this.controller?.selectDocNav(...args);
    },
  },
};
</script>

<style>

@layer base { body { background: var(--claude-background); color: var(--claude-foreground); font-family: var(--claude-font-sans); -webkit-font-smoothing: antialiased; } *, *::before, *::after { box-sizing: border-box; } }



:root {
  --claude-background: #FDFBF7;--claude-foreground: #1C1917;--claude-card: #FFFFFF;--claude-card-foreground: #1C1917;
  --claude-popover: #FFFFFF;--claude-popover-foreground: #1C1917;--claude-primary: #C96442;--claude-primary-foreground: #FFFFFF;
  --claude-secondary: #F0EAE0;--claude-secondary-foreground: #3D3530;--claude-muted: #E8E0D4;--claude-muted-foreground: #78716C;
  --claude-accent: #FAF0E4;--claude-accent-foreground: #5C3A1E;--claude-destructive: #B91C1C;--claude-destructive-foreground: #FFFFFF;
  --claude-border: #D6CEC4;--claude-ring: #C96442;--claude-input: #D6CEC4;
  --claude-brand-500: #C96442;--claude-brand-300: #E8A88C;--claude-brand-700: #A0502F;--claude-success-500: #22C55E;
  --claude-shadow-xs: 0 1px 2px rgba(0,0,0,0.05);--claude-shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  --claude-shadow-md: 0 4px 6px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);--claude-shadow-lg: 0 10px 15px rgba(0,0,0,0.06), 0 4px 6px rgba(0,0,0,0.03);
  --claude-radius-sm: 8px;--claude-radius-md: 12px;--claude-radius: 16px;--claude-radius-xl: 20px;--claude-radius-2xl: 24px;
  --claude-radius-full: 9999px;--claude-radius-lg: 16px;--claude-spacing: 0.25rem;
  --claude-font-display: Newsreader, Georgia, ui-serif, serif;--claude-font-sans: Poppins, ui-sans-serif, system-ui, sans-serif;
  --claude-font-serif: Lora, Georgia, ui-serif, serif;--claude-font-mono: Geist Mono, ui-monospace, monospace;
}



.bg-background{background-color:var(--claude-background)}.bg-foreground{background-color:var(--claude-foreground)}
.bg-card{background-color:var(--claude-card)}.bg-card-foreground{background-color:var(--claude-card-foreground)}
.bg-popover{background-color:var(--claude-popover)}.bg-popover-foreground{background-color:var(--claude-popover-foreground)}
.bg-primary{background-color:var(--claude-primary)}.bg-primary-foreground{background-color:var(--claude-primary-foreground)}
.bg-secondary{background-color:var(--claude-secondary)}.bg-secondary-foreground{background-color:var(--claude-secondary-foreground)}
.bg-muted{background-color:var(--claude-muted)}.bg-muted-foreground{background-color:var(--claude-muted-foreground)}
.bg-accent{background-color:var(--claude-accent)}.bg-accent-foreground{background-color:var(--claude-accent-foreground)}
.bg-destructive{background-color:var(--claude-destructive)}.bg-destructive-foreground{background-color:var(--claude-destructive-foreground)}
.bg-border{background-color:var(--claude-border)}.bg-ring{background-color:var(--claude-ring)}.bg-input{background-color:var(--claude-input)}
.text-background{color:var(--claude-background)}.text-foreground{color:var(--claude-foreground)}
.text-card{color:var(--claude-card)}.text-card-foreground{color:var(--claude-card-foreground)}
.text-popover{color:var(--claude-popover)}.text-popover-foreground{color:var(--claude-popover-foreground)}
.text-primary{color:var(--claude-primary)}.text-primary-foreground{color:var(--claude-primary-foreground)}
.text-secondary{color:var(--claude-secondary)}.text-secondary-foreground{color:var(--claude-secondary-foreground)}
.text-muted{color:var(--claude-muted)}.text-muted-foreground{color:var(--claude-muted-foreground)}
.text-accent{color:var(--claude-accent)}.text-accent-foreground{color:var(--claude-accent-foreground)}
.text-destructive{color:var(--claude-destructive)}.text-destructive-foreground{color:var(--claude-destructive-foreground)}
.text-border{color:var(--claude-border)}.text-ring{color:var(--claude-ring)}.text-input{color:var(--claude-input)}
.border-border{border-color:var(--claude-border)}



/* Copy button feedback */
.copy-done span { color: rgba(34,197,94,1) !important; }
.copy-done span::after { content: ' 已复制'; }

/* Active doc nav item hover effect */
.doc-nav-item:hover {
  background: var(--claude-secondary);
}

/* Custom scrollbar for doc nav */
nav::-webkit-scrollbar { width: 4px; }
nav::-webkit-scrollbar-track { background: transparent; }
nav::-webkit-scrollbar-thumb { background: var(--claude-border); border-radius: 4px; }

/* Smooth scroll */
html { scroll-behavior: smooth; }



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
