<!--
  Reference sidebar. Adapt to the project: replace `navItems` with the real routes,
  swap hard-coded labels for the project's i18n, and match its component API style
  (this sample uses the setup() form with an options wrapper).
-->
<template>
  <!-- Backdrop only exists for the mobile drawer; clicking it closes the drawer. -->
  <div v-if="mobileOpen" class="sidebar-backdrop" @click="closeMobile"></div>

  <aside
    class="sidebar"
    :class="{ collapsed, 'mobile-open': mobileOpen }"
    :aria-label="'Primary'"
  >
    <div class="sidebar-brand">
      <span class="brand-mark" aria-hidden="true">{{ brandInitial }}</span>
      <span class="brand-text">{{ brandName }}</span>
    </div>

    <nav class="sidebar-nav" aria-label="Main navigation">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :title="collapsed ? item.label : null"
        active-class="active"
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
          <path :d="item.icon" />
        </svg>
        <span class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <!-- Put the profile menu / language switcher here (moved from the old top bar). -->
      <slot name="footer"></slot>
      <button
        type="button"
        class="collapse-toggle"
        :aria-expanded="String(!collapsed)"
        :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        @click="toggleCollapsed"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"
             stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M15 18l-6-6 6-6" :style="{ transform: collapsed ? 'rotate(180deg)' : 'none', transformOrigin: 'center' }" />
        </svg>
        <span class="nav-label">Collapse</span>
      </button>
    </div>
  </aside>
</template>

<script>
import { onMounted, onBeforeUnmount } from 'vue'
import { useSidebar } from '../composables/useSidebar'

export default {
  name: 'AppSidebar',
  props: {
    brandName: { type: String, default: 'App' },
    // Items: { to, label, icon } where icon is an SVG path `d` string (24x24 stroke icons).
    navItems: { type: Array, required: true }
  },
  setup(props) {
    const { collapsed, mobileOpen, toggleCollapsed, closeMobile } = useSidebar()

    const brandInitial = props.brandName.charAt(0).toUpperCase()

    // Escape closes the drawer so keyboard users are never trapped behind the backdrop.
    const onKeydown = (event) => {
      if (event.key === 'Escape' && mobileOpen.value) closeMobile()
    }
    onMounted(() => window.addEventListener('keydown', onKeydown))
    onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))

    return { collapsed, mobileOpen, toggleCollapsed, closeMobile, brandInitial }
  }
}
</script>

<style scoped>
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

.sidebar.collapsed {
  width: var(--sidebar-width-collapsed);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-height);
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
  color: #fff;
  font-weight: 700;
}

.brand-text {
  font-size: var(--text-md);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
  white-space: nowrap;
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

.nav-icon {
  flex: none;
}

.nav-label {
  white-space: nowrap;
}

.sidebar-footer {
  padding: var(--space-3);
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

/* Collapsed rail: hide labels, center icons. */
.sidebar.collapsed .nav-label,
.sidebar.collapsed .brand-text {
  display: none;
}
.sidebar.collapsed .nav-item,
.sidebar.collapsed .collapse-toggle {
  justify-content: center;
  padding: 0;
}
.sidebar.collapsed .sidebar-brand {
  justify-content: center;
  padding: 0;
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  z-index: var(--z-backdrop);
}

/* Below the tablet breakpoint the sidebar is an off-canvas drawer and the
   collapse control is meaningless, so it is hidden and the width is forced to full. */
@media (max-width: 1023px) {
  .sidebar,
  .sidebar.collapsed {
    width: var(--sidebar-width);
    transform: translateX(-100%);
    box-shadow: var(--shadow-raised);
  }
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  .sidebar.collapsed .nav-label,
  .sidebar.collapsed .brand-text {
    display: inline;
  }
  .collapse-toggle {
    display: none;
  }
}
</style>
