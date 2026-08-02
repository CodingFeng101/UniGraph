# UniGraph 技术架构

UniGraph 把资料接入、知识建模、图谱构建、索引检索和可引用问答串成一个工作台。本文只描述当前代码中的主链路，并把架构图对应到实际模块。

> 阅读顺序：先理解“资料如何变成图”，再看“问题如何命中图中的证据”。图中的外部信源验证属于可扩展路线，不代表系统默认联网。

文中的代码均取自当前仓库，只截取解释机制所需的部分；与主题无关的参数、日志和进度回调会省略，但保留真实调用顺序和异常分支。每个代码块顶部都标明源文件，可直接回到完整实现。

## 1. 一条请求如何穿过系统

浏览器通过 Vue 工作台发起请求；FastAPI 负责认证、资源归属和接口编排；耗时的 Schema、图谱与索引任务进入 Celery；MySQL 保存业务数据，Redis承担会话、限流和任务状态。问答接口使用 NDJSON 持续返回阶段状态和答案增量。

| 层级 | 当前职责 | 代码入口 |
| --- | --- | --- |
| Vue 工作台 | 知识库管理、图谱设计与构建、流式问答 | `frontend/src` |
| FastAPI | 认证、权限、上传、业务 API、流式协议 | `backend/app` |
| GraphRAG 核心 | Schema、抽取、推理、社区索引、混合检索 | `backend/common/core_layer` |
| Celery | 执行 Schema、图谱、索引等长任务 | `backend/app/task` |
| MySQL / Redis | 持久业务数据；保存短期状态与任务队列 | `backend/database`、部署配置 |

系统的核心边界是 `KgBase`。资料、Schema、知识图谱、对话和任务都归属于知识库及其用户；读写接口会再次校验资源归属，不能只依赖前端传入的 UUID。

## 2. 先定义知识结构

Schema 决定允许出现哪些实体、属性和关系。先约束再抽取，可以减少同义类型漂移、关系方向混乱和属性格式不一致。

### 2.1 从资料迭代得到 Schema

![Schema 迭代：资料分块、候选类型提取、合并与收敛](assets/architecture/design-iterative-schema.png)

**输入**是资料分块和用户目标；**处理**是逐轮提取实体类型、关系类型和属性约束，并与上一轮结果合并；**输出**是可继续编辑的 Schema。对应实现位于 `backend/common/core_layer/unigraph/module/schema_construction`。

**关键函数：** `SchemaConstruction.extract_kg_schema()`。它先抽取实例三元组，再分别归类实体和关系；已有 Schema 时通过嵌入相似度合并类型，最后转换为统一 Schema 结构。

```python
# backend/common/core_layer/unigraph/module/schema_construction/schema_construction.py
Triple_source_dict, entity_string, relation_string = extract_triples_and_strings(
    extract_triples_from_text_response
)

temp_entity_type_dict = get_new_entity_types_from_response(entity_classify_response)
self.entity_type_dict = await merge_type_dicts_with_semantic(
    self.entity_type_dict,
    temp_entity_type_dict,
    embedding_api_key=embedding_api_key,
    embedding_base_url=embedding_base_url,
    embedding_model=embedding_model,
)

kg_schema = transform_triplets_to_schema(
    Triple_source_dict,
    self.entity_type_dict,
    self.relation_type_dict,
    entity_type_attribute_dict,
)
```

这里的关键不是让模型一次生成最终 Schema，而是把“实例抽取、类型归并、属性推断、结构转换”拆开，使每一步都能审查和重跑。

### 2.2 人工审查是质量闸门

![人工审查：修正类型、关系方向和属性定义](assets/architecture/design-human-review.png)

自动建议不会直接成为最终规则。用户可以修正实体类型、关系方向和属性，审查结果再进入后续构建，避免错误结构被批量放大。

### 2.3 抽取结果必须回到 Schema

![抽取与分类：实体、属性和关系映射到既有 Schema](assets/architecture/design-extraction-classification.png)

实体和关系先从文本中被识别，再映射到既有类型。无法可靠归类的内容不应静默写入错误类型，而应留给人工检查。

## 3. 资料如何变成知识图谱

### 3.1 构建总流程

![知识图谱构建：结构化路径与语义抽取路径汇合](assets/architecture/construction-overview.png)

构建包含两条路径：结构化数据直接形成节点与边；非结构化文档经过转换、分块和语义抽取。两路结果合并、去重，并在允许时执行关系与属性推理。

### 3.2 文档标准化与分块

![文档处理：格式转换、层级识别与语义分块](assets/architecture/construction-structured-document.png)

PDF、DOCX、TXT 等资料先转换为统一文本表示，再按标题层级与语义边界切分。每个分块保留来源信息，供后续回答引用回原文。

### 3.3 Schema 驱动抽取

![语义抽取：按 Schema 识别实体、属性和有向关系](assets/architecture/construction-semantic-extraction.png)

每个文本块在 Schema 约束下抽取实体、实体属性和有向关系。多块结果按实体标识、类型与关系方向合并，来源片段始终随记录保留。

### 3.4 推理只负责补候选

![知识推理：生成候选事实并与抽取图谱合并](assets/architecture/construction-inference.png)

推理用于补全候选实体、关系或属性，不替代原始证据。推理结果需要和直接抽取结果区分，方便审查、解释与回溯。主要编排入口位于 `backend/common/core_layer/interface/kg_services.py`。

### 3.5 验证边界

![验证路线：内部一致性判断与可选外部信源检查](assets/architecture/construction-validation.png)

当前实现侧重内部结构与多结果一致性检查。图中的外部信源验证是扩展方向；若启用，必须额外处理域名白名单、超时、可信度、版权、SSRF 和审计日志。

## 4. 图谱如何建立可检索索引

### 4.1 索引总览

![检索总览：图分析、社区报告、向量索引和混合召回](assets/architecture/retrieval-overview.png)

图谱会被转换为分析图，使用 Leiden 算法形成分层社区；系统同时生成社区报告和实体向量。问答时不只做向量相似度，还会组合实体、关系、原文和社区上下文。

### 4.2 四类索引材料

![索引结构：实体向量、关系来源、社区层级和社区报告](assets/architecture/retrieval-indexing.png)

索引保留四类材料：实体属性向量、实例关系、原始来源、社区报告。语言模型和嵌入模型独立配置；向量生成失败时任务应明确失败，不能留下“索引成功但不可查询”的状态。

**关键函数：** `GraphIndexer.build_index()`。社区划分、报告生成和实体嵌入是三个连续阶段，分别使用图算法、语言模型和嵌入模型。

```python
# backend/common/core_layer/unigraph/module/sapperrag/index/graph/cli.py
detector = CommunityDetection(max_comm_size=20, max_level=level, seed=5)
vertices, edges = detector.load_data(entities, relationships)
graph = detector.create_graph(vertices, edges)
communities = detector.detect_communities(graph, relationships)

generator = CommunityReportGenerator(input_data=communities)
reports_list = await generator.generate_reports(
    api_key=api_key, base_url=base_url, model=model
)
entities_list = await AttributeEmbedder().add_attribute_vectors(
    entities,
    api_key=embedding_api_key,
    base_url=embedding_base_url,
    model=embedding_model,
)
```

### 4.3 社区层级控制视野

![社区层级：从局部实体邻域逐步扩展到全局主题](assets/architecture/retrieval-community-hierarchy.png)

浅层社区适合精确的实体关系问题，深层社区提供更广的主题背景。界面上的检索深度最终影响上下文扩展范围，而不是简单改变回答长度。

### 4.4 当前问题驱动上下文

![上下文构建：当前问题命中实体后组织四类证据](assets/architecture/retrieval-context.png)

系统先从当前问题提取关键实体并执行向量匹配，再围绕命中结果组织四类信息。历史对话只作为辅助上下文，不能替代当前问题的图谱检索。

**关键函数：** `LocalSearch.search()`。调用顺序明确保证“当前问题检索在前，历史上下文注入在后”。历史摘要只能帮助理解对话指代，不能改变图谱证据本身。

```python
# backend/common/core_layer/unigraph/module/sapperrag/retriver/structured_search/local_search/search.py
extracted_entities = await extract_entities_from_query(query, llm, api_key, base_url, model)
context_text, context_data = await self.context_builder.build_context(
    extracted_entities,
    level,
    infer,
    kwargs.get('embedding_api_key', ''),
    kwargs.get('embedding_base_url', ''),
    **kwargs,
)
self.context_data = {key: value.to_dict() for key, value in context_data.items()}

conversation_context = await context_provider(context_text) if context_provider else None
answer_context = conversation_context.get('knowledge_context', context_text) \
    if conversation_context else context_text
search_prompt = self.system_prompt.format(
    context_data=answer_context, query=query, response_type='plain'
)
```

| 数据集 | 界面语义 | 回答中的作用 |
| --- | --- | --- |
| `Entities` | 重点知识细节 | 展示命中实体及其属性细节 |
| `Relationships` | 相关知识关联 | 展示实体之间的关系路径 |
| `Sources` | 具体信息来源 | 回到原文或资料片段核对事实 |
| `Reports` | 整体知识概览 | 提供社区主题与全局背景 |

`context_data` 不只是拼给模型的文本，也会随最终结果返回前端。正文中的记录 ID 因而可以再次定位到本轮实际使用的实体、关系、来源或报告，而不是跳到一个泛化的资料列表。

## 5. 可引用的流式问答

问答接口按行返回 NDJSON，前端边接收边展示。它展示的是可审计的处理阶段，而不是模型隐藏思维链。

| 事件 | 前端行为 |
| --- | --- |
| `processing` | 更新可折叠的检索阶段摘要 |
| `answer_delta` | 平滑追加答案文本 |
| `final_result` | 收口完整答案并绑定四类引用数据 |
| `error` | 展示脱敏后的错误和可操作提示 |

**后端流式编排：** `ask_knowledge_graph()` 将模型增量写入队列，并与处理阶段一起输出。最终事件携带完整答案和 `context_data`。

```python
# backend/app/kgbase/api/v1/kgbase/knowledge_graph.py
async def report_answer_delta(delta: str) -> None:
    await context_progress.put({'type': 'answer_delta', 'delta': delta})

query_task = asyncio.create_task(
    knowledge_graph_service.query(
        knowledge_graph=data,
        query=obj.message,
        depth=obj.depth,
        token_callback=report_answer_delta,
    )
)
while not query_task.done() or not context_progress.empty():
    try:
        progress = await asyncio.wait_for(context_progress.get(), timeout=0.1)
    except asyncio.TimeoutError:
        continue
    yield json.dumps(progress, ensure_ascii=False) + '\n'
```

这个接口同时发送心跳，避免模型处理时间较长时连接被代理或浏览器误判为中断。异常会转为脱敏后的 `error` 事件，而不是把上游模型凭据或请求细节直接返回页面。

模型在答案中输出 `[Data: Entities(...)]`、`[Data: Relationships(...)]` 等索引。前端解析索引后，将它替换为带语义类型的行内引用；悬停或聚焦引用，即可在小窗中查看对应记录片段。这样正文、索引和检索上下文形成闭环。

**前端引用解析：** `renderAnswerWithCitations()` 只接受四种数据集名称，逐个解析记录 ID，再从本轮 `context_data` 找到对应行并生成引用小窗。

```javascript
// frontend/src/controllers/GraphApplicationView.js
const sourceLabels = {
  Reports: '整体知识概览',
  Sources: '具体信息来源',
  Relationships: '相关知识关联',
  Entities: '重点知识细节',
};

const prepared = text.replace(/\[Data:\s*([^\]]+)\]/gi, function(_, citationBody) {
  const badges = [];
  citationBody.split(';').forEach(function(group) {
    const match = group.trim().match(
      /^(Reports|Sources|Relationships|Entities)\s*\(([^)]+)\)$/i
    );
    if (!match) return;
    match[2].split(',').forEach(function(recordId) {
      badges.push(renderCitationBadge(match[1], recordId.trim(), sources));
    });
  });
  return badges.length ? badges.join('') : _;
});
```

实际实现还支持一个标记中包含多个数据集和多个 ID，并先用占位符保护引用 HTML，再执行 Markdown 渲染，避免引用小窗被 Markdown 转义。

问答 API 位于 `backend/app/kgbase/api/v1/kgbase/knowledge_graph.py`，上下文检索位于 `backend/common/core_layer/unigraph/module/sapperrag/retriver`，前端引用解析位于 `frontend/src/controllers/GraphApplicationView.js`。

## 6. 任务、权限与部署

- Schema、图谱和索引构建进入 Celery，任务中心展示阶段、错误和重试状态。
- API Key 使用 `LLM_API_KEY_ENCRYPTION_KEY` 加密，读取接口不回传明文。
- 上传文件在后端校验扩展名、大小、最终落盘路径和资源归属。
- 模型地址执行 SSRF 防护；内网模型只能在隔离网络中显式允许。
- 生产入口应由 HTTPS 反向代理统一暴露；流式接口需要关闭代理缓冲。

长任务统一通过 `TaskService.run()` 发送到 Celery，并在 Redis 中登记任务所有者。查询进度或撤销任务时仍需校验用户归属。

```python
# backend/app/task/service/task_service.py
def run(*, name: str, user_uuid: str, args=None, kwargs=None):
    task = celery_app.send_task(name=name, args=args, kwargs=kwargs)
    TaskService.register_owner(task.id, user_uuid)
    return {
        'task_id': task.id,
        'status': 'started',
        'name': name,
    }
```

单机部署从根目录 `compose.yaml` 开始，生产叠加配置位于 `deploy/compose.prod.yaml`。更完整的安全边界见 `SECURITY.md`，部署步骤见 `DEPLOYMENT.md`。

## 7. 从哪里开始读代码

| 目标 | 建议入口 |
| --- | --- |
| 应用启动和中间件 | `backend/main.py`、`backend/core/registrar.py` |
| Schema 构建 | `backend/common/core_layer/unigraph/module/schema_construction` |
| 图谱构建与推理 | `backend/common/core_layer/interface/kg_services.py` |
| Leiden 社区和实体嵌入 | `backend/common/core_layer/unigraph/module/sapperrag/index/graph` |
| 混合上下文检索 | `backend/common/core_layer/unigraph/module/sapperrag/retriver` |
| 流式问答 API | `backend/app/kgbase/api/v1/kgbase/knowledge_graph.py` |
| 前端问答与引用 | `frontend/src/controllers/GraphApplicationView.js` |
| 图谱渲染 | `frontend/src/graph` |
