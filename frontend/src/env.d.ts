/// <reference types="vite/client" />

interface Window {
  API: Record<string, (...args: any[]) => any>;
  AppConfig: Record<string, any>;
  Auth: Record<string, any>;
  ChatSidebar: Record<string, any>;
  cytoscape: any;
  FRONTEND_CONFIG?: Record<string, string>;
  getUniGraphSearchParams: () => URLSearchParams;
  GraphRenderer: Record<string, any>;
  KgBaseAPI: Record<string, (...args: any[]) => any>;
  lucide: { createIcons: () => void };
  TaskManager: Record<string, any>;
}

declare module 'cytoscape-cose-bilkent';
declare module 'cytoscape-dagre';
declare module 'cytoscape-fcose';
