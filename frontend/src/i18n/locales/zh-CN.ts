export default {
  common: {
    create: '创建', update: '更新', delete: '删除', edit: '编辑', save: '保存', cancel: '取消',
    close: '关闭', copy: '复制', copied: '已复制', send: '发送', search: '搜索', refresh: '刷新',
    loading: '加载中', retry: '重试', success: '成功', failed: '失败', inProgress: '进行中', completed: '已完成',
  },
  nav: {
    knowledgeBases: '图知识库列表', info: '信息', design: '设计', build: '构建', newChat: '新建对话',
    profile: '个人中心', docs: '技术文档', tutorials: '视频教程', tasks: '后台任务', settings: '设置', logout: '退出登录',
  },
  auth: {
    login: '登录', register: '注册', username: '用户名', email: '邮箱', password: '密码',
    sessionExpired: '认证已失效，请重新登录',
  },
  chat: {
    empty: '有什么可以帮你的？', historyEmpty: '暂无历史对话', newConversation: '新对话',
    selectIndex: '选择知识图谱索引', noIndex: '暂无可用索引', regenerate: '重新生成', share: '分享对话',
  },
  task: {
    title: '后台任务', empty: '暂无后台任务', pending: '等待中', running: '执行中', retrying: '重试中',
    succeeded: '已完成', failed: '失败', revoked: '已撤销', runningCount: '{count} 进行中',
  },
  profile: {
    title: '个人中心', changeAvatar: '更换头像', editProfile: '编辑资料', modelConfig: '模型配置',
    profileUpdated: '个人资料已更新，下次请使用新用户名登录',
  },
  settings: {
    language: '语言', theme: '主题', light: '亮色', dark: '暗色', system: '跟随系统',
    chinese: '中文', english: '英文', user: '用户', administrator: '管理员', emailUnset: '未设置邮箱',
  },
  errors: {
    page: '页面发生异常，请重试；若问题持续请刷新页面', network: '网络请求失败', request: '请求失败',
    load: '加载失败', operation: '操作失败',
  },
} as const;
