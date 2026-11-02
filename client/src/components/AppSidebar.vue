<template>
  <!-- Backdrop only exists for the mobile drawer; clicking it closes the drawer. -->
  <div v-if="mobileOpen" class="sidebar-backdrop" @click="closeMobile"></div>

  <aside
    id="app-sidebar"
    class="sidebar"
    :class="{ rail: isRail, 'mobile-open': mobileOpen }"
  >
    <div class="sidebar-brand">
      <span class="brand-mark" aria-hidden="true">{{ brandInitial }}</span>
      <div class="brand-text">
        <span class="brand-name">{{ brandName }}</span>
        <span v-if="brandSubtitle" class="brand-subtitle">{{ brandSubtitle }}</span>
      </div>
    </div>

    <nav class="sidebar-nav" :aria-label="t('nav.mainNavigation')">
      <!--
        Only exact-active-class is styled: router-link-active is a prefix match,
        so '/' would otherwise look active on every page.
      -->
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :title="isRail ? item.label : null"
        :aria-label="isRail ? item.label : null"
        exact-active-class="active"
        @click="closeMobile"
      >
        <svg
          class="nav-icon"
          viewBox="0 0 24 24"
          width="20"
          height="20"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path v-for="d in item.icon" :key="d" :d="d" />
        </svg>
        <span class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <!-- Profile menu and language switcher (moved from the old top bar). -->
      <slot name="footer"></slot>
      <button
        type="button"
        class="collapse-toggle"
        :aria-expanded="String(!isRail)"
        :aria-label="isRail ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        :title="isRail ? t('nav.expandSidebar') : null"
        @click="toggleCollapsed"
      >
        <svg
          class="collapse-icon"
          viewBox="0 0 24 24"
          width="20"
          height="20"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M15 18l-6-6 6-6" />
        </svg>
        <span class="nav-label">{{ t('nav.collapseSidebar') }}</span>
      </button>
    </div>
  </aside>
</template>

<script>
import { computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useSidebar } from '../composables/useSidebar'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'AppSidebar',
  props: {
    brandName: { type: String, default: '' },
    brandSubtitle: { type: String, default: '' },
    // Items: { to, label, icon } where icon is an array of SVG path `d` strings (24x24 stroke icons).
    navItems: { type: Array, required: true }
  },
  setup(props) {
    const { isRail, mobileOpen, toggleCollapsed, closeMobile } = useSidebar()
    const { t } = useI18n()
    const route = useRoute()

    const brandInitial = computed(() => props.brandName.charAt(0).toUpperCase())

    // Close the drawer/overlay on any navigation (including programmatic ones), not just link clicks.
    watch(() => route.path, closeMobile)

    // Escape closes the drawer/overlay so keyboard users are never trapped behind the backdrop.
    const onKeydown = (event) => {
      if (event.key === 'Escape' && mobileOpen.value) closeMobile()
    }

    // Breakpoint crossings are handled in useSidebar (it resets the temporary state).
    onMounted(() => window.addEventListener('keydown', onKeydown))
    onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))

    return { t, isRail, mobileOpen, toggleCollapsed, closeMobile, brandInitial }
  }
}
</script>

<style scoped>
/*
 * No overflow on .sidebar itself: the profile/language dropdowns in the footer
 * open upward/sideways and would be clipped. Only the nav list scrolls.
 */
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  z-index: var(--z-sidebar);
  transition: width var(--transition-base), transform var(--transition-base);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-height);
  flex: none;
  padding: 0 var(--space-5);
  border-bottom: 1px solid var(--color-border);
  overflow: hidden;
}

.brand-mark {
  flex: none;
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: var(--color-surface);
  font-weight: 700;
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-size: var(--text-md);
  font-weight: 700;
  line-height: 1.2;
  color: var(--color-text);
  letter-spacing: -0.025em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-4) var(--space-3);
  overflow-y: auto;
}

.nav-item,
.collapse-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 40px;
  padding: 0 var(--space-3);
  border: 0;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--color-text-muted);
  font: inherit;
  font-size: var(--text-base);
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.nav-item:hover,
.collapse-toggle:hover {
  background: var(--color-surface-muted);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.nav-item:focus-visible,
.collapse-toggle:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.nav-icon,
.collapse-icon {
  flex: none;
}

.collapse-icon {
  transition: transform var(--transition-base);
}

.nav-label {
  white-space: nowrap;
}

.sidebar-footer {
  flex: none;
  padding: var(--space-3);
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Footer controls fill the sidebar width; the components own their own look. */
.sidebar-footer :deep(.profile-menu),
.sidebar-footer :deep(.language-switcher) {
  width: 100%;
}

.sidebar-footer :deep(.profile-button),
.sidebar-footer :deep(.language-button) {
  width: 100%;
}

.sidebar-footer :deep(.profile-name) {
  flex: 1;
  min-width: 0;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-footer :deep(.language-label) {
  flex: 1;
  text-align: left;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  z-index: var(--z-backdrop);
}

/*
 * The rail class is computed in JS (useSidebar.isRail): the user's preference on
 * desktop, the default on tablet. Phones never get it, so the drawer is always full width.
 */
.sidebar.rail {
  width: var(--sidebar-width-collapsed);
}

.sidebar.rail .nav-label,
.sidebar.rail .brand-text,
.sidebar.rail .sidebar-footer :deep(.profile-name),
.sidebar.rail .sidebar-footer :deep(.language-label),
.sidebar.rail .sidebar-footer :deep(.chevron) {
  display: none;
}

.sidebar.rail .nav-item,
.sidebar.rail .collapse-toggle {
  justify-content: center;
  padding: 0;
}

.sidebar.rail .sidebar-brand {
  justify-content: center;
  padding: 0;
}

.sidebar.rail .sidebar-footer :deep(.profile-button),
.sidebar.rail .sidebar-footer :deep(.language-button) {
  justify-content: center;
  padding: var(--space-1);
}

.sidebar.rail .collapse-icon {
  transform: rotate(180deg);
}

/* Tablet: expanded sidebar overlays the content (the main column keeps its 72px offset). */
@media (min-width: 640px) and (max-width: 1023px) {
  .sidebar.mobile-open {
    box-shadow: var(--shadow-raised);
  }
}

/* Phone (< 640px): off-canvas drawer. */
@media (max-width: 639px) {
  .sidebar {
    transform: translateX(-100%);
    box-shadow: var(--shadow-raised);
    /* Keep the closed drawer out of the tab order and away from assistive tech. */
    visibility: hidden;
    transition: transform var(--transition-base), visibility 0s linear var(--transition-base);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
    visibility: visible;
    transition: transform var(--transition-base), visibility 0s;
  }

  /* Collapse control is meaningless for the drawer. */
  .collapse-toggle {
    display: none;
  }
}
</style>
