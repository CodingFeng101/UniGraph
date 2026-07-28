<template>
  <div class="">
<div class="flex min-h-screen">
  <div class="relative flex flex-col items-center justify-center" style="width:50vw;min-height:100vh;background:var(--claude-login-dark);overflow:hidden;">
    <div class="absolute inset-0 pointer-events-none" style="background:radial-gradient(ellipse 60% 50% at 50% 50%, rgba(201,100,66,0.06) 0%, transparent 70%);z-index:1;"></div>

    <svg class="kg-bg-login" viewBox="0 0 960 1080" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <defs>
        <filter id="glow-sm" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur"/>
          <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 0.55 0 0 0  0 0 0.35 0 0  0 0 0 0.5 0" result="color"/>
          <feMerge>
            <feMergeNode in="color"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        <filter id="glow-md" x="-150%" y="-150%" width="400%" height="400%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="blur"/>
          <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 0.55 0 0 0  0 0 0.35 0 0  0 0 0 0.6 0" result="color"/>
          <feMerge>
            <feMergeNode in="color"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        <filter id="glow-lg" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur in="SourceGraphic" stdDeviation="14" result="blur"/>
          <feColorMatrix in="blur" type="matrix" values="1 0 0 0 0  0 0.55 0 0 0  0 0 0.35 0 0  0 0 0 0.7 0" result="color"/>
          <feMerge>
            <feMergeNode in="color"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        <radialGradient id="hub-fill" cx="40%" cy="35%">
          <stop offset="0%" stop-color="#E8A88C" stop-opacity="0.5"/>
          <stop offset="100%" stop-color="#C96442" stop-opacity="0.2"/>
        </radialGradient>
        <radialGradient id="sat-fill" cx="40%" cy="35%">
          <stop offset="0%" stop-color="#E8A88C" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="#C96442" stop-opacity="0.12"/>
        </radialGradient>
      </defs>

      <path d="M260,220 Q180,160 120,110" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.14"/>
      <path d="M260,220 Q320,140 380,100" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.12"/>
      <path d="M260,220 Q200,280 140,330" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.16"/>
      <path d="M260,220 Q310,300 360,400" stroke="#E8A88C" stroke-width="1.2" fill="none" opacity="0.10"/>
      <path d="M260,220 Q350,250 460,300" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.13"/>
      <path d="M460,300 Q400,200 380,100" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.11"/>
      <path d="M460,300 Q540,220 600,180" stroke="#E8A88C" stroke-width="1.2" fill="none" opacity="0.15"/>
      <path d="M460,300 Q520,360 560,440" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.14"/>
      <path d="M460,300 Q560,280 700,300" stroke="#E8A88C" stroke-width="1.1" fill="none" opacity="0.12"/>
      <path d="M460,300 Q440,420 420,540" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.10"/>
      <path d="M700,300 Q760,220 820,170" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.13"/>
      <path d="M700,300 Q740,400 720,510" stroke="#E8A88C" stroke-width="1.2" fill="none" opacity="0.16"/>
      <path d="M700,300 Q810,340 860,420" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.11"/>
      <path d="M700,300 Q660,220 600,180" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.10"/>
      <path d="M480,700 Q400,620 360,520" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.13"/>
      <path d="M480,700 Q560,640 620,580" stroke="#E8A88C" stroke-width="1.1" fill="none" opacity="0.14"/>
      <path d="M480,700 Q460,800 380,890" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.12"/>
      <path d="M480,700 Q550,780 620,870" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.10"/>
      <path d="M480,700 Q420,740 300,780" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.11"/>
      <path d="M480,700 Q540,720 720,720" stroke="#E8A88C" stroke-width="1" fill="none" opacity="0.09"/>

      <path d="M120,110 Q200,80 380,100" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>
      <path d="M380,100 Q500,130 600,180" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>
      <path d="M140,330 Q240,400 360,400" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.09"/>
      <path d="M560,440 Q640,510 720,510" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.09"/>
      <path d="M860,420 Q840,520 720,510" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>
      <path d="M300,780 Q340,850 380,890" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.07"/>
      <path d="M620,870 Q680,800 720,720" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>
      <path d="M820,170 Q860,300 860,420" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.07"/>
      <path d="M360,520 Q390,620 420,540" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>
      <path d="M620,580 Q670,650 720,720" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.09"/>
      <path d="M200,920 Q300,960 380,890" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.06"/>
      <path d="M780,900 Q700,890 620,870" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.07"/>
      <path d="M120,110 Q100,220 140,330" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>
      <path d="M560,440 Q490,490 420,540" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.09"/>
      <path d="M420,540 Q390,530 360,520" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>
      <path d="M620,580 Q590,510 560,440" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.09"/>
      <path d="M300,780 Q250,700 200,620" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.07"/>
      <path d="M80,820 Q130,900 180,980" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.07"/>
      <path d="M900,100 Q860,135 820,170" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.09"/>
      <path d="M520,60 Q450,80 380,100" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>
      <path d="M780,900 Q830,750 880,600" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.06"/>
      <path d="M40,200 Q80,155 120,110" stroke="#E8A88C" stroke-width="0.7" fill="none" opacity="0.08"/>

      <circle class="kg-node kg-hub-a" cx="260" cy="220" r="14" fill="url(#hub-fill)" filter="url(#glow-lg)" opacity="0.30"/>
      <circle class="kg-node kg-hub-b" cx="460" cy="300" r="12" fill="url(#hub-fill)" filter="url(#glow-lg)" opacity="0.28"/>
      <circle class="kg-node kg-hub-c" cx="700" cy="300" r="12" fill="url(#hub-fill)" filter="url(#glow-lg)" opacity="0.26"/>
      <circle class="kg-node kg-hub-d" cx="480" cy="700" r="11" fill="url(#hub-fill)" filter="url(#glow-lg)" opacity="0.24"/>

      <circle class="kg-node kg-s01" cx="120" cy="110" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.18"/>
      <circle class="kg-node kg-s02" cx="380" cy="100" r="8" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.20"/>
      <circle class="kg-node kg-s03" cx="140" cy="330" r="6" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.17"/>
      <circle class="kg-node kg-s04" cx="360" cy="400" r="3" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.15"/>
      <circle class="kg-node kg-s05" cx="600" cy="180" r="8" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.22"/>
      <circle class="kg-node kg-s06" cx="560" cy="440" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.16"/>
      <circle class="kg-node kg-s07" cx="420" cy="540" r="3" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.14"/>
      <circle class="kg-node kg-s08" cx="360" cy="520" r="7" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.18"/>
      <circle class="kg-node kg-s09" cx="820" cy="170" r="6" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.20"/>
      <circle class="kg-node kg-s10" cx="720" cy="510" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.16"/>
      <circle class="kg-node kg-s11" cx="860" cy="420" r="8" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.19"/>
      <circle class="kg-node kg-s12" cx="720" cy="720" r="3" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.15"/>
      <circle class="kg-node kg-s13" cx="300" cy="780" r="7" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.17"/>
      <circle class="kg-node kg-s14" cx="620" cy="580" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.15"/>
      <circle class="kg-node kg-s15" cx="380" cy="890" r="8" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.21"/>
      <circle class="kg-node kg-s16" cx="620" cy="870" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.14"/>
      <circle class="kg-node kg-s17" cx="60" cy="540" r="3" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.10"/>
      <circle class="kg-node kg-s18" cx="200" cy="620" r="3" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.08"/>
      <circle class="kg-node kg-s19" cx="880" cy="600" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.09"/>
      <circle class="kg-node kg-s20" cx="80" cy="820" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.11"/>
      <circle class="kg-node kg-s21" cx="180" cy="980" r="3" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.08"/>
      <circle class="kg-node kg-s22" cx="780" cy="900" r="7" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.13"/>
      <circle class="kg-node kg-s23" cx="900" cy="100" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.10"/>
      <circle class="kg-node kg-s24" cx="40" cy="200" r="3" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.07"/>
      <circle class="kg-node kg-s25" cx="520" cy="60" r="4" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.09"/>
      <circle class="kg-node kg-s26" cx="920" cy="780" r="3" fill="url(#sat-fill)" filter="url(#glow-sm)" opacity="0.08"/>

      <text x="260" y="248" text-anchor="middle" fill="#E8A88C" font-size="11" opacity="0.45" font-family="Poppins,sans-serif">数控机床</text>
      <text x="460" y="330" text-anchor="middle" fill="#E8A88C" font-size="11" opacity="0.42" font-family="Poppins,sans-serif">主轴</text>
      <text x="700" y="330" text-anchor="middle" fill="#E8A88C" font-size="11" opacity="0.40" font-family="Poppins,sans-serif">刀具</text>
      <text x="480" y="728" text-anchor="middle" fill="#E8A88C" font-size="11" opacity="0.38" font-family="Poppins,sans-serif">PLC控制器</text>
      <text x="380" y="88" text-anchor="middle" fill="#E8A88C" font-size="10" opacity="0.38" font-family="Poppins,sans-serif">轴承</text>
      <text x="600" y="168" text-anchor="middle" fill="#E8A88C" font-size="10" opacity="0.40" font-family="Poppins,sans-serif">电动机</text>
      <text x="360" y="510" text-anchor="middle" fill="#E8A88C" font-size="10" opacity="0.36" font-family="Poppins,sans-serif">工序</text>
      <text x="300" y="772" text-anchor="middle" fill="#E8A88C" font-size="10" opacity="0.38" font-family="Poppins,sans-serif">操作人员</text>
    </svg>

    <div class="absolute top-0 left-0 right-0 text-center py-5" style="z-index:2;">
      <p style="font-size:13px;color:var(--claude-login-text-faint);margin:0;letter-spacing:1px;font-family:var(--claude-font-sans);">江西师范大学</p>
    </div>

    <div class="relative text-center px-8" style="z-index:2;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);">
      <svg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="margin:0 auto 20px;display:block;box-shadow:0 0 40px rgba(232,168,140,0.3);border-radius:50%;">
        <line x1="30" y1="15" x2="12" y2="45" stroke="#E8A88C" stroke-width="2.5"/>
        <line x1="30" y1="15" x2="48" y2="45" stroke="#E8A88C" stroke-width="2.5"/>
        <line x1="12" y1="45" x2="48" y2="45" stroke="#E8A88C" stroke-width="2.5"/>
        <circle cx="30" cy="15" r="10" fill="none" stroke="#E8A88C" stroke-width="2.5"/>
        <circle cx="12" cy="45" r="7" fill="none" stroke="#E8A88C" stroke-width="2.5"/>
        <circle cx="48" cy="45" r="7" fill="none" stroke="#E8A88C" stroke-width="2.5"/>
      </svg>
      <h1 style="font-family:var(--claude-font-display);font-size:52px;font-weight:bold;color:var(--claude-login-text);line-height:1.2;margin:0 0 16px;letter-spacing:-0.8px;">UniGraph</h1>
      <p style="font-family:var(--claude-font-serif);font-size:19px;color:var(--claude-login-text-dim);line-height:1.6;margin:0;letter-spacing:0.5px;">一站式知识图谱智造平台</p>
    </div>
  </div>

  <div style="width:1px;background:rgba(0,0,0,0.06);flex-shrink:0;"></div>

  <div class="auth-side">
    <div class="auth-panel">
      <h2 class="auth-title">{{ modeInfo.title }}</h2>
      <p class="auth-subtitle">{{ modeInfo.subtitle }}</p>

      <form v-if="mode === 'login'" id="login-form" class="auth-form auth-form--login" autocomplete="off" @submit.prevent="submitLogin">
        <AuthField v-model="loginForm.username" input-id="username" label="用户名" icon="user" placeholder="请输入用户名" autocomplete="username" />
        <AuthField v-model="loginForm.password" input-id="password" label="密码" icon="lock" type="password" placeholder="请输入密码" autocomplete="current-password" />
        <AuthField v-model="loginForm.captcha" input-id="captcha" label="验证码" icon="shield-check" placeholder="请输入验证码" :maxlength="4">
          <template #suffix><img class="captcha-image" :src="captchaSrc" @click="loadCaptcha" title="点击刷新验证码" alt="验证码" /></template>
        </AuthField>

        <p v-if="feedback.message" class="auth-feedback" :class="{ 'auth-feedback--success': feedback.success }">{{ feedback.message }}</p>
        <div class="auth-options">
          <label class="remember-option">
            <input v-model="rememberUsername" type="checkbox" />
            <span>记住密码</span>
          </label>
          <a href="#" class="auth-link auth-link--muted" @click.prevent="switchMode('reset')">忘记密码?</a>
        </div>
        <button type="submit" class="login-btn auth-submit" :disabled="busy">{{ busy ? '登录中...' : '登录' }}</button>
      </form>

      <form v-else-if="mode === 'register'" id="register-form" class="auth-form auth-form--compact" autocomplete="off" @submit.prevent="submitRegister">
        <AuthField v-model="registerForm.username" compact input-id="register-username" label="用户名" icon="user" placeholder="请输入用户名" autocomplete="username" />
        <AuthField v-model="registerForm.nickname" compact input-id="register-nickname" label="昵称" icon="contact-round" placeholder="请输入昵称" />
        <AuthField v-model="registerForm.email" compact input-id="register-email" label="邮箱" icon="mail" type="email" placeholder="请输入邮箱" autocomplete="email" />
        <AuthField v-model="registerForm.password" compact input-id="register-password" label="密码" icon="lock" type="password" placeholder="请输入密码" autocomplete="new-password" />
        <AuthField v-model="registerForm.confirmPassword" compact input-id="register-confirm-password" label="确认密码" icon="lock" type="password" placeholder="请再次输入密码" autocomplete="new-password" />
        <AuthField v-model="registerForm.captcha" compact input-id="register-captcha" label="验证码" icon="shield-check" placeholder="请输入验证码" :maxlength="4">
          <template #suffix><img class="captcha-image" :src="captchaSrc" @click="loadCaptcha" title="点击刷新验证码" alt="验证码" /></template>
        </AuthField>
        <p v-if="feedback.message" class="auth-feedback" :class="{ 'auth-feedback--success': feedback.success }">{{ feedback.message }}</p>
        <button type="submit" class="login-btn auth-submit" :disabled="busy">{{ busy ? '注册中...' : '注册' }}</button>
      </form>

      <form v-else id="reset-form" class="auth-form auth-form--compact" autocomplete="off" @submit.prevent="submitResetPassword">
        <AuthField v-model="resetForm.username" compact input-id="reset-username" label="用户名" icon="user" placeholder="请输入用户名" autocomplete="username" />
        <AuthField v-model="resetForm.email" compact input-id="reset-email" label="注册邮箱" icon="mail" type="email" placeholder="请输入注册邮箱" autocomplete="email" />
        <AuthField v-model="resetForm.password" compact input-id="reset-password" label="新密码" icon="lock" type="password" placeholder="请输入新密码" autocomplete="new-password" />
        <AuthField v-model="resetForm.confirmPassword" compact input-id="reset-confirm-password" label="确认新密码" icon="lock" type="password" placeholder="请再次输入新密码" autocomplete="new-password" />
        <AuthField v-model="resetForm.captcha" compact input-id="reset-captcha" label="验证码" icon="shield-check" placeholder="请输入验证码" :maxlength="4">
          <template #suffix><img class="captcha-image" :src="captchaSrc" @click="loadCaptcha" title="点击刷新验证码" alt="验证码" /></template>
        </AuthField>
        <p v-if="feedback.message" class="auth-feedback" :class="{ 'auth-feedback--success': feedback.success }">{{ feedback.message }}</p>
        <button type="submit" class="login-btn auth-submit" :disabled="busy">{{ busy ? '提交中...' : '重置密码' }}</button>
      </form>

      <p class="auth-switch">
        <template v-if="mode === 'login'">还没有账号？<a href="#" class="auth-link" @click.prevent="switchMode('register')">立即注册</a></template>
        <template v-else>已有账号？<a href="#" class="auth-link" @click.prevent="switchMode('login')">返回登录</a></template>
      </p>
      <p class="auth-copyright">&copy; 2026 UniGraph</p>
    </div>
  </div>
</div>
  </div>
</template>

<script>
import AuthField from '@/components/auth/AuthField.vue';
import { KgBaseAPI } from '@/api';
import { Auth } from '@/api/runtime/auth';

export default {
  name: 'LoginView',
  components: { AuthField },
  data: () => ({
    mode: 'login',
    busy: false,
    captchaSrc: '',
    rememberUsername: false,
    feedback: { message: '', success: false },
    loginForm: { username: '', password: '', captcha: '' },
    registerForm: { username: '', nickname: '', email: '', password: '', confirmPassword: '', captcha: '' },
    resetForm: { username: '', email: '', password: '', confirmPassword: '', captcha: '' },
  }),
  computed: {
    loginRedirect() {
      const redirect = this.$route.query.redirect;
      if (typeof redirect !== 'string') return { name: 'workspace' };

      const base = import.meta.env.BASE_URL.replace(/\/$/, '');
      const normalized = redirect.startsWith(`${base}/`) ? redirect.slice(base.length) : redirect;
      return normalized.startsWith('/') && !normalized.startsWith('//') ? normalized : { name: 'workspace' };
    },
    modeInfo() {
      return {
        login: { title: '登录', subtitle: '欢迎使用 UniGraph 知识图谱平台' },
        register: { title: '注册', subtitle: '创建您的 UniGraph 平台账号' },
        reset: { title: '重置密码', subtitle: '验证账号信息并设置新密码' },
      }[this.mode];
    },
  },
  mounted() {
    document.title = '登录';
    document.body.className = '';
    if (Auth.isLogin()) {
      this.$router.replace(this.loginRedirect);
      return;
    }
    const rememberedUsername = window.localStorage.getItem('unigraph-remembered-username');
    if (rememberedUsername) {
      this.loginForm.username = rememberedUsername;
      this.rememberUsername = true;
    }
    this.loadCaptcha();
  },
  methods: {
    switchMode(mode) {
      this.mode = mode;
      this.feedback = { message: '', success: false };
      document.title = this.modeInfo.title;
      this.$nextTick(() => window.lucide?.createIcons());
    },
    validateRequired(form, fields) {
      if (fields.some((field) => !form[field]?.trim())) {
        this.feedback = { message: '请填写完整信息', success: false };
        return false;
      }
      if ('confirmPassword' in form && form.password !== form.confirmPassword) {
        this.feedback = { message: '两次输入的密码不一致', success: false };
        return false;
      }
      return true;
    },
    async loadCaptcha() {
      try {
        const response = await KgBaseAPI.auth.getCaptcha();
        if (response.code === 200 && response.data) {
          const imageType = response.data.image_type === 'base64' ? 'image/jpeg' : response.data.image_type;
          this.captchaSrc = `data:${imageType};base64,${response.data.image}`;
        }
      } catch (error) {
        console.error('获取验证码失败', error);
        this.feedback = { message: '验证码加载失败，请点击重试', success: false };
      }
    },
    async submitLogin() {
      if (!this.validateRequired(this.loginForm, ['username', 'password', 'captcha'])) return;
      this.busy = true;
      this.feedback = { message: '', success: false };
      try {
        const response = await KgBaseAPI.auth.login(this.loginForm.username, this.loginForm.password, this.loginForm.captcha);
        if (response.code !== 200 || !response.data?.access_token) {
          throw new Error(response.msg || '登录失败');
        }
        Auth.setToken(response.data.access_token);
        if (this.rememberUsername) {
          window.localStorage.setItem('unigraph-remembered-username', this.loginForm.username);
        } else {
          window.localStorage.removeItem('unigraph-remembered-username');
        }
        try {
          const userResponse = await KgBaseAPI.auth.getUserInfo();
          if (userResponse.code === 200 && userResponse.data) Auth.setUserInfo(userResponse.data);
        } catch {
          // 用户信息失败不阻断已经成功的登录。
        }
        await this.$router.replace(this.loginRedirect);
      } catch (error) {
        this.feedback = { message: error.msg || error.message || '网络错误，请重试', success: false };
        this.loginForm.captcha = '';
        await this.loadCaptcha();
      } finally {
        this.busy = false;
      }
    },
    async submitRegister() {
      const fields = ['username', 'nickname', 'email', 'password', 'confirmPassword', 'captcha'];
      if (!this.validateRequired(this.registerForm, fields)) return;
      this.busy = true;
      this.feedback = { message: '', success: false };
      try {
        const response = await KgBaseAPI.auth.register(this.registerForm);
        if (response.code !== 200) throw new Error(response.msg || '注册失败');
        this.loginForm.username = this.registerForm.username;
        this.switchMode('login');
        this.feedback = { message: '注册成功，请使用新账号登录', success: true };
      } catch (error) {
        this.feedback = { message: error.msg || error.message || '注册失败，请重试', success: false };
      } finally {
        this.registerForm.captcha = '';
        await this.loadCaptcha();
        this.busy = false;
      }
    },
    async submitResetPassword() {
      const fields = ['username', 'email', 'password', 'confirmPassword', 'captcha'];
      if (!this.validateRequired(this.resetForm, fields)) return;
      this.busy = true;
      this.feedback = { message: '', success: false };
      try {
        const response = await KgBaseAPI.auth.resetPassword(this.resetForm);
        if (response.code !== 200) throw new Error(response.msg || '密码重置失败');
        this.loginForm.username = this.resetForm.username;
        this.switchMode('login');
        this.feedback = { message: '密码重置成功，请使用新密码登录', success: true };
      } catch (error) {
        this.feedback = { message: error.msg || error.message || '密码重置失败，请重试', success: false };
      } finally {
        this.resetForm.captcha = '';
        await this.loadCaptcha();
        this.busy = false;
      }
    },
  },
};
</script>

<style>

    @layer base {
      body {
        background: var(--claude-background);
        color: var(--claude-foreground);
        font-family: var(--claude-font-sans);
        -webkit-font-smoothing: antialiased;
      }
      *, *::before, *::after { box-sizing: border-box; }
    }
  


    :root {
      --claude-background: #FDFBF7;
      --claude-foreground: #1C1917;
      --claude-card: #FFFFFF;
      --claude-card-foreground: #1C1917;
      --claude-popover: #FFFFFF;
      --claude-popover-foreground: #1C1917;
      --claude-primary: #C96442;
      --claude-primary-foreground: #FFFFFF;
      --claude-secondary: #F0EAE0;
      --claude-secondary-foreground: #3D3530;
      --claude-muted: #E8E0D4;
      --claude-muted-foreground: #78716C;
      --claude-accent: #FAF0E4;
      --claude-accent-foreground: #5C3A1E;
      --claude-destructive: #B91C1C;
      --claude-destructive-foreground: #FFFFFF;
      --claude-border: #D6CEC4;
      --claude-ring: #C96442;
      --claude-input: #D6CEC4;
      --claude-brand-500: #C96442;
      --claude-brand-300: #E8A88C;
      --claude-brand-700: #A0502F;
      --claude-success-500: #22C55E;
      --claude-shadow-sm: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
      --claude-shadow-lg: 0 10px 15px rgba(0,0,0,0.06), 0 4px 6px rgba(0,0,0,0.03);
      --claude-radius-md: 12px;
      --claude-radius-xl: 20px;
      --claude-radius-2xl: 24px;
      --claude-radius-full: 9999px;
      --claude-font-display: Newsreader, Georgia, ui-serif, serif;
      --claude-font-sans: Poppins, ui-sans-serif, system-ui, sans-serif;
      --claude-font-serif: Lora, Georgia, ui-serif, serif;
      --claude-font-mono: Geist Mono, ui-monospace, monospace;
      --claude-login-dark: #2C2A27;
      --claude-login-text: #FFFFFF;
      --claude-login-text-dim: rgba(255,255,255,0.55);
      --claude-login-text-faint: rgba(255,255,255,0.30);
    }
  


  .kg-bg-login {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    pointer-events: none;
  }

  .auth-side {
    display: flex;
    width: 50vw;
    min-height: 100vh;
    align-items: center;
    justify-content: center;
    background: var(--claude-background);
  }

  .auth-panel {
    width: 100%;
    max-width: 400px;
    padding: 24px;
  }

  .auth-title {
    margin: 0 0 8px;
    color: var(--claude-foreground);
    font-family: var(--claude-font-display);
    font-size: 32px;
    font-weight: bold;
    letter-spacing: -0.3px;
    line-height: 1.3;
  }

  .auth-subtitle {
    margin: 0;
    color: var(--claude-muted-foreground);
    font-family: var(--claude-font-sans);
    font-size: 14px;
  }

  .auth-form {
    margin-top: 40px;
  }

  .auth-form--compact {
    margin-top: 24px;
  }

  .captcha-image {
    height: 36px;
    border-radius: 8px;
    cursor: pointer;
    user-select: none;
  }

  .auth-feedback {
    margin: -8px 0 14px;
    color: var(--claude-destructive);
    font-family: var(--claude-font-sans);
    font-size: 13px;
    line-height: 1.5;
  }

  .auth-feedback--success {
    color: #16803a;
  }

  .auth-options {
    display: flex;
    margin-bottom: 32px;
    align-items: center;
    justify-content: space-between;
  }

  .remember-option {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--claude-foreground);
    cursor: pointer;
    font-family: var(--claude-font-sans);
    font-size: 14px;
  }

  .remember-option input {
    width: 16px;
    height: 16px;
    accent-color: var(--claude-brand-500);
    cursor: pointer;
  }

  .auth-submit {
    width: 100%;
    height: 48px;
    border: none;
    border-radius: 14px;
    background: var(--claude-brand-500);
    color: var(--claude-primary-foreground);
    cursor: pointer;
    font-family: var(--claude-font-sans);
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.2px;
  }

  .auth-switch {
    margin: 40px 0 0;
    color: var(--claude-muted-foreground);
    font-family: var(--claude-font-sans);
    font-size: 14px;
    text-align: center;
  }

  .auth-form--compact + .auth-switch {
    margin-top: 24px;
  }

  .auth-link {
    color: var(--claude-primary);
    font-weight: 500;
    text-decoration: none;
    transition: opacity 0.2s, color 0.2s;
  }

  .auth-link:hover {
    opacity: 0.8;
  }

  .auth-link--muted {
    color: var(--claude-muted-foreground);
    font-weight: 400;
  }

  .auth-link--muted:hover {
    color: var(--claude-brand-500);
  }

  .auth-copyright {
    margin: 16px 0 0;
    color: var(--claude-muted-foreground);
    font-family: var(--claude-font-sans);
    font-size: 12px;
    text-align: center;
  }

  @keyframes float-a { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-20px); } }
  @keyframes float-b { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-14px); } }
  @keyframes float-c { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-25px); } }
  @keyframes float-d { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-11px); } }
  @keyframes float-e { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-18px); } }
  @keyframes float-f { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-16px); } }
  @keyframes glow-breathe { 0%,100% { opacity: 0.3; } 50% { opacity: 0.5; } }

  .kg-hub-a { animation: float-a 10s ease-in-out infinite, glow-breathe 6s ease-in-out infinite; transform-origin: 260px 220px; }
  .kg-hub-b { animation: float-c 14s ease-in-out 1.5s infinite, glow-breathe 8s ease-in-out 1s infinite; transform-origin: 460px 300px; }
  .kg-hub-c { animation: float-e 12s ease-in-out 0.8s infinite, glow-breathe 7s ease-in-out 2s infinite; transform-origin: 700px 300px; }
  .kg-hub-d { animation: float-b 16s ease-in-out 2s infinite, glow-breathe 9s ease-in-out 3s infinite; transform-origin: 480px 700px; }

  .kg-s01 { animation: float-b 11s ease-in-out 0.5s infinite; transform-origin: 120px 110px; }
  .kg-s02 { animation: float-d 9s ease-in-out 1.2s infinite; transform-origin: 380px 100px; }
  .kg-s03 { animation: float-f 13s ease-in-out 2.5s infinite; transform-origin: 140px 330px; }
  .kg-s04 { animation: float-a 15s ease-in-out 0.3s infinite; transform-origin: 360px 400px; }
  .kg-s05 { animation: float-e 8s ease-in-out 1.8s infinite; transform-origin: 600px 180px; }
  .kg-s06 { animation: float-c 12s ease-in-out 3.2s infinite; transform-origin: 560px 440px; }
  .kg-s07 { animation: float-b 17s ease-in-out 0.7s infinite; transform-origin: 420px 540px; }
  .kg-s08 { animation: float-d 10s ease-in-out 2.1s infinite; transform-origin: 360px 520px; }
  .kg-s09 { animation: float-f 9s ease-in-out 1.4s infinite; transform-origin: 820px 170px; }
  .kg-s10 { animation: float-a 14s ease-in-out 0.9s infinite; transform-origin: 720px 510px; }
  .kg-s11 { animation: float-e 11s ease-in-out 3.5s infinite; transform-origin: 860px 420px; }
  .kg-s12 { animation: float-c 16s ease-in-out 0.4s infinite; transform-origin: 720px 720px; }
  .kg-s13 { animation: float-b 13s ease-in-out 2.8s infinite; transform-origin: 300px 780px; }
  .kg-s14 { animation: float-d 10s ease-in-out 1.6s infinite; transform-origin: 620px 580px; }
  .kg-s15 { animation: float-a 15s ease-in-out 0.6s infinite; transform-origin: 380px 890px; }
  .kg-s16 { animation: float-f 12s ease-in-out 2.3s infinite; transform-origin: 620px 870px; }
  .kg-s17 { animation: float-b 18s ease-in-out 1.1s infinite; transform-origin: 60px 540px; }
  .kg-s18 { animation: float-d 14s ease-in-out 3.0s infinite; transform-origin: 200px 620px; }
  .kg-s19 { animation: float-e 10s ease-in-out 0.2s infinite; transform-origin: 880px 600px; }
  .kg-s20 { animation: float-a 16s ease-in-out 1.7s infinite; transform-origin: 80px 820px; }
  .kg-s21 { animation: float-c 13s ease-in-out 2.6s infinite; transform-origin: 180px 980px; }
  .kg-s22 { animation: float-f 11s ease-in-out 0.8s infinite; transform-origin: 780px 900px; }
  .kg-s23 { animation: float-b 17s ease-in-out 3.3s infinite; transform-origin: 900px 100px; }
  .kg-s24 { animation: float-d 15s ease-in-out 1.0s infinite; transform-origin: 40px 200px; }
  .kg-s25 { animation: float-a 9s ease-in-out 2.4s infinite; transform-origin: 520px 60px; }
  .kg-s26 { animation: float-e 18s ease-in-out 0.1s infinite; transform-origin: 920px 780px; }

  .login-btn:hover {
    opacity: 0.92;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(201,100,66,0.30);
  }
  .login-btn:active {
    transform: translateY(0);
    box-shadow: none;
    opacity: 0.95;
  }
  .login-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @media (prefers-reduced-motion: reduce) {
    .kg-node { animation: none !important; }
    .login-btn { transition: none !important; }
  }

</style>
