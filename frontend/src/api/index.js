/**
 * kgbase 业务 API 模块
 * 对接旧系统后端全部 kgbase 端点
 * API 前缀: /v1/kg/...
 */
import { Auth } from './runtime/auth';
import { API } from './runtime/client';

export const KgBaseAPI = window.KgBaseAPI = {

  // ==================== 认证 ====================
  auth: {
    /** 获取验证码 */
    getCaptcha() {
      return API.get('/v1/auth/captcha');
    },
    /** 登录（需加密 username/password/captcha） */
    login(username, password, captcha) {
      const u = Auth.encryptData(username);
      const p = Auth.encryptData(password);
      const c = Auth.encryptData(captcha);
      return API.post('/v1/auth/login', {
        username: u.ciphertext,
        password: p.ciphertext,
        captcha: c.ciphertext,
        username_iv: u.iv,
        password_iv: p.iv,
        captcha_iv: c.iv,
      });
    },
    /** 注册 */
    register({ username, password, email, captcha }) {
      const values = {
        username: Auth.encryptData(username),
        password: Auth.encryptData(password),
        nickname: Auth.encryptData(username),
        email: Auth.encryptData(email),
        captcha: Auth.encryptData(captcha),
      };
      return API.post('/v1/auth/register', {
        username: values.username.ciphertext,
        password: values.password.ciphertext,
        nickname: values.nickname.ciphertext,
        email: values.email.ciphertext,
        captcha: values.captcha.ciphertext,
        username_iv: values.username.iv,
        password_iv: values.password.iv,
        nickname_iv: values.nickname.iv,
        email_iv: values.email.iv,
        captcha_iv: values.captcha.iv,
      });
    },
    /** 重置密码 */
    resetPassword({ username, email, password, captcha }) {
      const values = {
        username: Auth.encryptData(username),
        email: Auth.encryptData(email),
        password: Auth.encryptData(password),
        captcha: Auth.encryptData(captcha),
      };
      return API.put('/v1/auth/password/reset', {
        username: values.username.ciphertext,
        email: values.email.ciphertext,
        password: values.password.ciphertext,
        captcha: values.captcha.ciphertext,
        username_iv: values.username.iv,
        email_iv: values.email.iv,
        password_iv: values.password.iv,
        captcha_iv: values.captcha.iv,
      });
    },
    /** 退出登录 */
    logout() {
      return API.post('/v1/auth/logout');
    },
    /** 获取当前用户信息 */
    getUserInfo() {
      return API.get('/v1/sys/users/me');
    },
    updateUser(username, data) {
      return API.put(`/v1/sys/users/${encodeURIComponent(username)}`, data);
    },
    updateAvatar(username, url) {
      return API.put(`/v1/sys/users/${encodeURIComponent(username)}/avatar`, { url });
    },
  },

  // ==================== 图谱库 KgBase ====================
  kgBase: {
    /** 获取当前用户所有图谱库 */
    getAll() {
      return API.get('/v1/kg/base/all/');
    },
    /** 获取图谱库详情（含 knowledge_graphs + schema_graphs） */
    getDetail(uuid) {
      return API.get(`/v1/kg/base/${uuid}`);
    },
    /** 创建图谱库 */
    create(data) {
      return API.post('/v1/kg/base', data);
    },
    /** 更新图谱库 */
    update(uuid, data) {
      return API.put(`/v1/kg/base/${uuid}`, data);
    },
    /** 删除图谱库 */
    delete(uuid) {
      return API.delete(`/v1/kg/base/${uuid}`);
    },
  },

  // ==================== 架构图谱 SchemaGraph ====================
  schemaGraph: {
    /** 获取 kgbase 下所有架构图谱 */
    getAll(kgBaseUuid) {
      return API.get(`/v1/kg/schema/all/${kgBaseUuid}`);
    },
    /** 获取架构图谱详情（含 entities + relationships） */
    getDetail(uuid) {
      return API.get(`/v1/kg/schema/${uuid}`);
    },
    /** 导出架构（返回 name/aim/kg_schema/definition/modify_info/modify_suggestion） */
    export(uuid) {
      return API.get(`/v1/kg/schema/export/${uuid}`);
    },
    /** 导入知识架构 */
    import(data) {
      return API.post('/v1/kg/schema/import', data);
    },
    /** 删除架构图谱 */
    delete(uuid) {
      return API.delete(`/v1/kg/schema/${uuid}`);
    },
    /** 更新架构详情 */
    updateDetail(uuid, data) {
      const body = { ...data };
      if (body.modify_info && typeof body.modify_info === 'object') {
        body.modify_info = JSON.stringify(body.modify_info);
      }
      return API.put(`/v1/kg/schema/update/${uuid}`, body);
    },
  },

  // ==================== 实体类型 SchemaEntity ====================
  schemaEntity: {
    /** 获取架构下所有实体类型 */
    getAll(schemaGraphUuid) {
      return API.get(`/v1/kg/schema_entity/all/${schemaGraphUuid}`);
    },
    /** 获取实体类型详情 */
    getDetail(uuid) {
      return API.get(`/v1/kg/schema_entity/${uuid}`);
    },
    /** 创建实体类型 */
    create(data) {
      return API.post('/v1/kg/schema_entity', data);
    },
    /** 更新实体类型 */
    update(uuid, data) {
      return API.put(`/v1/kg/schema_entity/${uuid}`, data);
    },
    /** 删除实体类型 */
    delete(uuid) {
      return API.delete(`/v1/kg/schema_entity/${uuid}`);
    },
  },

  // ==================== 关系类型 SchemaRelationship ====================
  schemaRelationship: {
    /** 获取架构下所有关系类型 */
    getAll(schemaGraphUuid) {
      return API.get(`/v1/kg/schema_relationship/all/${schemaGraphUuid}`);
    },
    /** 获取关系类型详情 */
    getDetail(uuid) {
      return API.get(`/v1/kg/schema_relationship/${uuid}`);
    },
    /** 创建关系类型 */
    create(data) {
      return API.post('/v1/kg/schema_relationship', data);
    },
    /** 更新关系类型 */
    update(uuid, data) {
      return API.put(`/v1/kg/schema_relationship/${uuid}`, data);
    },
    /** 删除关系类型 */
    delete(uuid) {
      return API.delete(`/v1/kg/schema_relationship/${uuid}`);
    },
  },

  // ==================== 知识图谱 KnowledgeGraph ====================
  knowledgeGraph: {
    /** 获取 kgbase 下所有实例图谱 */
    getAll(kgBaseUuid) {
      return API.get(`/v1/kg/knowledge/all/${kgBaseUuid}`);
    },
    /** 获取实例图谱详情（含 entities + relationships + communities + schema_graph） */
    getDetail(uuid) {
      return API.get(`/v1/kg/knowledge/${uuid}`);
    },
    getExplorationOverview(uuid) {
      return API.get(`/v1/kg/knowledge/explore/${uuid}/overview`);
    },
    getExplorationType(uuid, entityType, limit = 200) {
      return API.get(`/v1/kg/knowledge/explore/${uuid}/type?entity_type=${encodeURIComponent(entityType)}&limit=${limit}`);
    },
    getExplorationNeighbors(uuid, entityUuid, depth = 1, limit = 300) {
      return API.get(`/v1/kg/knowledge/explore/${uuid}/neighbors/${encodeURIComponent(entityUuid)}?depth=${depth}&limit=${limit}`);
    },
    /** 获取最大索引深度 */
    getDepth(uuid) {
      return API.get(`/v1/kg/knowledge/depth/${uuid}`);
    },
    /** 索引导出为文件 */
    exportIndexFile(uuid) {
      return API.post(`/v1/kg/knowledge/export-index-file/${uuid}`);
    },
    /** 索引导出为 URL */
    exportIndexUrl(uuid) {
      return API.post(`/v1/kg/knowledge/export-index-url/${uuid}`);
    },
    /** 导入索引（multipart） */
    importIndex(knowledgeGraphUuid, file) {
      const formData = new FormData();
      formData.append('knowledge_graph_uuid', knowledgeGraphUuid);
      formData.append('file', file);
      return API.post('/v1/kg/knowledge/import-index', formData);
    },
    /** 删除实例图谱 */
    delete(uuid) {
      return API.delete(`/v1/kg/knowledge/${uuid}`);
    },
    /**
     * 基于索引的问答（NDJSON 流式响应）
     * @param {string} uuid - 知识图谱 UUID
     * @param {object} params - { message, infer, depth, chat_library_uuid, current_message_uuid, llm_model_uuid }
     * @param {function} onEvent - 事件回调
     */
    ask(uuid, params, onEvent) {
      return API.stream(`/v1/kg/knowledge/ask/${uuid}`, params, onEvent);
    },
  },

  // ==================== 实体 KnowledgeEntity ====================
  knowledgeEntity: {
    /** 获取图谱下所有实体 */
    getAll(knowledgeGraphUuid) {
      return API.get(`/v1/kg/knowledge_entity/all/${knowledgeGraphUuid}`);
    },
    /** 获取实体详情 */
    getDetail(uuid) {
      return API.get(`/v1/kg/knowledge_entity/${uuid}`);
    },
    /** 创建实体 */
    create(data) {
      return API.post('/v1/kg/knowledge_entity', data);
    },
    /** 更新实体（name, attributes, type） */
    update(uuid, data) {
      return API.put(`/v1/kg/knowledge_entity/${uuid}`, data);
    },
    /** 删除实体 */
    delete(uuid) {
      return API.delete(`/v1/kg/knowledge_entity/${uuid}`);
    },
  },

  // ==================== 关系 KnowledgeRelationship ====================
  knowledgeRelationship: {
    /** 获取图谱下所有关系 */
    getAll(knowledgeGraphUuid) {
      return API.get(`/v1/kg/knowledge_relationship/all/${knowledgeGraphUuid}`);
    },
    /** 获取关系详情 */
    getDetail(uuid) {
      return API.get(`/v1/kg/knowledge_relationship/${uuid}`);
    },
    /** 创建关系 */
    create(data) {
      return API.post('/v1/kg/knowledge_relationship', data);
    },
    /** 更新关系 */
    update(uuid, data) {
      return API.put(`/v1/kg/knowledge_relationship/${uuid}`, data);
    },
    /** 删除关系 */
    delete(uuid) {
      return API.delete(`/v1/kg/knowledge_relationship/${uuid}`);
    },
  },

  // ==================== 聊天库 ChatLibrary ====================
  chatLibrary: {
    /** 获取所有聊天库 */
    getAll(kgBaseUuid) {
      return API.get(`/v1/kg/chat_library/all/${kgBaseUuid}`);
    },
    /** 获取当前用户的所有聊天，包括已解除知识库绑定的历史聊天 */
    getAllForUser() {
      return API.get('/v1/kg/chat_library/all');
    },
    /** 获取聊天库详情 */
    getDetail(chatLibraryUuid) {
      return API.get(`/v1/kg/chat_library/${chatLibraryUuid}`);
    },
    /** 创建聊天库 */
    create(data) {
      return API.post('/v1/kg/chat_library', data);
    },
    /** 更新聊天库 */
    update(chatLibraryUuid, data) {
      return API.put(`/v1/kg/chat_library/${chatLibraryUuid}`, data);
    },
    appendTurn(chatLibraryUuid, data) {
      return API.post(`/v1/kg/chat_library/${chatLibraryUuid}/turn`, data);
    },
    appendMessage(chatLibraryUuid, data) {
      return API.post(`/v1/kg/chat_library/${chatLibraryUuid}/message`, data);
    },
    updateMessage(chatLibraryUuid, messageUuid, content) {
      return API.patch(`/v1/kg/chat_library/${chatLibraryUuid}/message/${messageUuid}`, { content });
    },
    generateTitle(chatLibraryUuid, content) {
      return API.post(`/v1/kg/chat_library/${chatLibraryUuid}/title`, { content });
    },
    setFavorite(chatLibraryUuid, isFavorite) {
      return API.patch(`/v1/kg/chat_library/${chatLibraryUuid}/favorite`, {
        is_favorite: isFavorite,
      });
    },
    getShare(chatLibraryUuid) {
      return API.get(`/v1/kg/chat_library/${chatLibraryUuid}/share`);
    },
    createShare(chatLibraryUuid) {
      return API.post(`/v1/kg/chat_library/${chatLibraryUuid}/share`, {});
    },
    updateShare(chatLibraryUuid) {
      return API.put(`/v1/kg/chat_library/${chatLibraryUuid}/share`, {});
    },
    rotateShare(chatLibraryUuid) {
      return API.post(`/v1/kg/chat_library/${chatLibraryUuid}/share/rotate`, {});
    },
    revokeShare(chatLibraryUuid) {
      return API.delete(`/v1/kg/chat_library/${chatLibraryUuid}/share`);
    },
    getPublicShare(publicId) {
      return API.get(`/v1/kg/chat_library/public/${encodeURIComponent(publicId)}`);
    },
    /** 删除聊天库 */
    delete(chatLibraryUuid) {
      return API.delete(`/v1/kg/chat_library/${chatLibraryUuid}`);
    },
  },

  // ==================== 模型配置 LLM ====================
  llm: {
    getProviders() {
      return API.get('/v1/llm/provider/all');
    },
    getProviderDetail(uuid) {
      return API.get(`/v1/llm/provider/${uuid}/detail`);
    },
    getModels(providerUuid) {
      const query = providerUuid ? `?llm_provider_uuid=${encodeURIComponent(providerUuid)}` : '';
      return API.get(`/v1/llm/model/all${query}`);
    },
    testModel(data) {
      return API.post('/v1/llm/model/test', data);
    },
    createProvider(name, config = {}) {
      const user = Auth.getUserInfo() || {};
      return API.post('/v1/llm/provider', {
        name,
        user_uuid: user.uuid || user.user_uuid,
        api_key: config.api_key || '',
        api_url: config.api_url || '',
        document_url: '',
        llm_model_url: '',
      });
    },
    updateProvider(uuid, data) {
      return API.put(`/v1/llm/provider/${uuid}`, data);
    },
    reorderProviders(providerUuids) {
      return API.put('/v1/llm/provider/order', { provider_uuids: providerUuids });
    },
    deleteProvider(uuid) {
      return API.delete(`/v1/llm/provider?llm_provider_uuid=${encodeURIComponent(uuid)}`);
    },
    createModel(data) {
      return API.post('/v1/llm/model', data);
    },
    updateModel(uuid, data) {
      return API.put(`/v1/llm/model/${uuid}`, data);
    },
    deleteModel(uuid) {
      return API.delete(`/v1/llm/model?llm_model_uuid=${encodeURIComponent(uuid)}`);
    },
  },

  // ==================== 异步任务 Task ====================
  task: {
    /** 提交任务 */
    submit(taskName, params) {
      return API.post(`/v1/tasks/${encodeURIComponent(taskName)}`, {
        args: [],
        kwargs: params || {},
      });
    },
    /** 获取可执行任务 */
    getAll() {
      return API.get('/v1/tasks');
    },
    /** 获取当前任务 */
    getCurrent() {
      return API.get('/v1/tasks/current');
    },
    /** 查询任务状态 */
    getStatus(taskId) {
      return API.get(`/v1/tasks/${encodeURIComponent(taskId)}/status`);
    },
    /** 获取任务结果 */
    getResult(taskId) {
      return API.get(`/v1/tasks/${encodeURIComponent(taskId)}`);
    },
    /** 撤销任务 */
    revoke(taskId) {
      return API.post(`/v1/tasks/${encodeURIComponent(taskId)}/revoke`, {});
    },
  },
};
