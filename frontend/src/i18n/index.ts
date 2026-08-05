import { createI18n } from 'vue-i18n';
import zhCN from './locales/zh-CN';
import enUS from './locales/en-US';

export type AppLocale = 'zh-CN' | 'en-US';

export function savedLocale(): AppLocale {
  return localStorage.getItem('unigraph-language') === 'en' ? 'en-US' : 'zh-CN';
}

export const i18n = createI18n({
  legacy: false,
  locale: savedLocale(),
  fallbackLocale: 'zh-CN',
  missingWarn: false,
  fallbackWarn: false,
  messages: { 'zh-CN': zhCN, 'en-US': enUS },
});

export function setI18nLocale(language: string) {
  i18n.global.locale.value = language === 'en' || language === 'en-US' ? 'en-US' : 'zh-CN';
}
