import { nextTick, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { gsap } from 'gsap';

const HEAVY_ROUTES = new Set(['graph-design', 'graph-build', 'graph-application']);

const MOTION_ITEM_SELECTOR = [
  '[data-motion-item]',
  '.kb-card',
  '.video-item',
  '.settings-section',
  '.shared-chat-message',
  '.doc-nav-item',
  '.task-card',
  '.ai-thinking-log__item',
  '#chat-container > div > .group',
].join(',');

const OVERLAY_SELECTOR = [
  '[id*="modal"]',
  '[id$="-dropdown"]',
  '[id*="-dropdown-"]',
  '.depth-menu',
  '.task-panel',
  '.claude-menu',
  '.profile-menu',
].join(',');

function isVisible(element: HTMLElement): boolean {
  const style = window.getComputedStyle(element);
  return !element.classList.contains('hidden')
    && style.display !== 'none'
    && style.visibility !== 'hidden'
    && element.getClientRects().length > 0;
}

function overlaySurface(element: HTMLElement): HTMLElement {
  if (element.classList.contains('task-panel')) {
    return element.querySelector<HTMLElement>('.task-panel-surface') || element;
  }
  if (element.id.includes('modal')) {
    return element.querySelector<HTMLElement>('[role="dialog"], .modal-content, :scope > div') || element;
  }
  return element;
}

export function useAppMotion(): void {
  const route = useRoute();
  const overlayVisibility = new WeakMap<HTMLElement, boolean>();
  const animatedItems = new WeakSet<HTMLElement>();
  const animatingOverlays = new WeakSet<HTMLElement>();

  let appObserver: MutationObserver | null = null;
  let bodyObserver: MutationObserver | null = null;
  let routeContext: gsap.Context | null = null;
  let media: gsap.MatchMedia | null = null;
  let routeFrame = 0;
  let reducedMotion = false;
  let pressedElement: HTMLElement | null = null;

  function motionItems(scope: ParentNode): HTMLElement[] {
    return Array.from(scope.querySelectorAll<HTMLElement>(MOTION_ITEM_SELECTOR))
      .filter((element) => isVisible(element))
      .slice(0, 14);
  }

  function animateRoute(): void {
    routeContext?.revert();
    const appRoot = document.getElementById('app');
    const page = appRoot?.firstElementChild as HTMLElement | null;
    if (!page) return;

    const content = page.querySelector<HTMLElement>('#app-main, main')
      || page.firstElementChild as HTMLElement | null
      || page;
    const isHeavy = HEAVY_ROUTES.has(String(route.name || ''));

    routeContext = gsap.context(() => {
      if (reducedMotion) {
        gsap.set(content, { clearProps: 'opacity,visibility,transform,will-change' });
        return;
      }

      gsap.fromTo(
        content,
        { autoAlpha: 0, y: isHeavy ? 0 : 10, scale: isHeavy ? 1 : 0.998 },
        {
          autoAlpha: 1,
          y: 0,
          scale: 1,
          duration: isHeavy ? 0.24 : 0.38,
          ease: 'power2.out',
          overwrite: 'auto',
          willChange: 'transform,opacity',
          onComplete: () => {
            gsap.set(content, { clearProps: 'opacity,visibility,transform,will-change' });
          },
        },
      );

      const items = motionItems(content).filter((element) => element !== content);
      if (items.length) {
        items.forEach((element) => animatedItems.add(element));
        gsap.fromTo(
          items,
          { autoAlpha: 0, y: 8 },
          {
            autoAlpha: 1,
            y: 0,
            duration: 0.32,
            stagger: 0.035,
            ease: 'power2.out',
            overwrite: 'auto',
            onComplete: () => {
              gsap.set(items, { clearProps: 'opacity,visibility,transform' });
            },
          },
        );
      }
    }, page);
  }

  function scheduleRouteMotion(): void {
    window.cancelAnimationFrame(routeFrame);
    void nextTick().then(() => {
      routeFrame = window.requestAnimationFrame(animateRoute);
    });
  }

  function animateItems(elements: HTMLElement[]): void {
    const freshItems = elements
      .filter((element) => !animatedItems.has(element) && isVisible(element))
      .slice(0, 14);
    if (!freshItems.length) return;
    freshItems.forEach((element) => animatedItems.add(element));
    if (reducedMotion) return;

    gsap.fromTo(
      freshItems,
      { autoAlpha: 0, y: 8 },
      {
        autoAlpha: 1,
        y: 0,
        duration: 0.3,
        stagger: 0.03,
        ease: 'power2.out',
        overwrite: 'auto',
        onComplete: () => {
          gsap.set(freshItems, { clearProps: 'opacity,visibility,transform' });
        },
      },
    );
  }

  function animateOverlay(element: HTMLElement): void {
    if (reducedMotion || animatingOverlays.has(element)) return;
    animatingOverlays.add(element);
    overlayVisibility.set(element, true);

    const surface = overlaySurface(element);
    const isBackdrop = surface !== element;
    if (isBackdrop) {
      gsap.fromTo(
        element,
        { autoAlpha: 0 },
        {
          autoAlpha: 1,
          duration: 0.16,
          ease: 'power1.out',
          overwrite: 'auto',
          onComplete: () => {
            gsap.set(element, { clearProps: 'opacity,visibility' });
          },
        },
      );
    }

    gsap.fromTo(
      surface,
      { autoAlpha: 0, y: isBackdrop ? 10 : -6, scale: 0.985 },
      {
        autoAlpha: 1,
        y: 0,
        scale: 1,
        duration: 0.24,
        ease: 'power2.out',
        overwrite: 'auto',
        transformOrigin: isBackdrop ? 'center center' : 'top center',
        onComplete: () => {
          gsap.set(surface, { clearProps: 'opacity,visibility,transform,transform-origin' });
          animatingOverlays.delete(element);
          overlayVisibility.set(element, true);
        },
      },
    );
  }

  function registerOverlay(element: HTMLElement): void {
    const visible = isVisible(element);
    const wasVisible = overlayVisibility.get(element) || false;
    if (!animatingOverlays.has(element)) overlayVisibility.set(element, visible);
    if (visible && !wasVisible) animateOverlay(element);
  }

  function processAddedNode(node: Node): void {
    if (!(node instanceof HTMLElement)) return;
    if (node.parentElement?.id === 'app') return;

    const items = node.matches(MOTION_ITEM_SELECTOR) ? [node] : [];
    items.push(...Array.from(node.querySelectorAll<HTMLElement>(MOTION_ITEM_SELECTOR)));
    animateItems(items);

    const overlays = node.matches(OVERLAY_SELECTOR) ? [node] : [];
    overlays.push(...Array.from(node.querySelectorAll<HTMLElement>(OVERLAY_SELECTOR)));
    overlays.forEach(registerOverlay);
  }

  function onAppMutation(records: MutationRecord[]): void {
    records.forEach((record) => {
      if (record.type === 'childList') {
        record.addedNodes.forEach(processAddedNode);
        return;
      }
      if (record.target instanceof HTMLElement && record.target.matches(OVERLAY_SELECTOR)) {
        registerOverlay(record.target);
      }
    });
  }

  function onBodyMutation(records: MutationRecord[]): void {
    records.forEach((record) => record.addedNodes.forEach(processAddedNode));
  }

  function releasePressedElement(): void {
    if (!pressedElement) return;
    const target = pressedElement;
    pressedElement = null;
    gsap.to(target, {
      scale: 1,
      duration: reducedMotion ? 0 : 0.18,
      ease: 'power2.out',
      overwrite: 'auto',
      onComplete: () => {
        gsap.set(target, { clearProps: 'transform' });
      },
    });
  }

  function onPointerDown(event: PointerEvent): void {
    const target = (event.target as Element | null)?.closest<HTMLElement>('button, [role="button"]');
    if (!target || target.matches(':disabled, [aria-disabled="true"]') || reducedMotion) return;
    releasePressedElement();
    pressedElement = target;
    gsap.to(target, { scale: 0.97, duration: 0.1, ease: 'power1.out', overwrite: 'auto' });
  }

  onMounted(() => {
    const appRoot = document.getElementById('app');
    if (!appRoot) return;

    media = gsap.matchMedia();
    media.add(
      {
        reduceMotion: '(prefers-reduced-motion: reduce)',
        allowMotion: '(prefers-reduced-motion: no-preference)',
      },
      (context) => {
        reducedMotion = Boolean(context.conditions?.reduceMotion);
        scheduleRouteMotion();
      },
    );

    appRoot.querySelectorAll<HTMLElement>(OVERLAY_SELECTOR).forEach((element) => {
      overlayVisibility.set(element, isVisible(element));
    });

    appObserver = new MutationObserver(onAppMutation);
    appObserver.observe(appRoot, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['class', 'style'],
    });

    bodyObserver = new MutationObserver(onBodyMutation);
    bodyObserver.observe(document.body, { childList: true });

    document.addEventListener('pointerdown', onPointerDown, true);
    document.addEventListener('pointerup', releasePressedElement, true);
    document.addEventListener('pointercancel', releasePressedElement, true);
    window.addEventListener('blur', releasePressedElement);
  });

  watch(() => route.fullPath, scheduleRouteMotion, { flush: 'post' });

  onUnmounted(() => {
    window.cancelAnimationFrame(routeFrame);
    appObserver?.disconnect();
    bodyObserver?.disconnect();
    routeContext?.revert();
    media?.revert();
    releasePressedElement();
    document.removeEventListener('pointerdown', onPointerDown, true);
    document.removeEventListener('pointerup', releasePressedElement, true);
    document.removeEventListener('pointercancel', releasePressedElement, true);
    window.removeEventListener('blur', releasePressedElement);
  });
}
