<template>
  <div class="app" :class="{ 'sidebar-collapsed': railLayout }">
    <AppSidebar
      :brand-name="t('nav.companyName')"
      :brand-subtitle="t('nav.subtitle')"
      :nav-items="navItems"
    >
      <template #footer>
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
      </template>
    </AppSidebar>

    <div class="app-main">
      <!-- Slim top bar is only the phone (< 640px) drawer trigger; tablet/desktop use the persistent rail. -->
      <header class="topbar">
        <button
          type="button"
          class="menu-button"
          :aria-label="t('nav.openMenu')"
          aria-controls="app-sidebar"
          :aria-expanded="String(mobileOpen)"
          @click="openMobile"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor"
               stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 6h16" />
            <path d="M4 12h16" />
            <path d="M4 18h16" />
          </svg>
        </button>
        <span class="topbar-title">{{ currentTitle }}</span>
      </header>

      <main class="main-content">
        <FilterBar v-if="$route.path !== '/restocking'" />
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import AppSidebar from './components/AppSidebar.vue'
import { useRoute } from 'vue-router'
import { useSidebar } from './composables/useSidebar'

export default {
  name: 'App',
  components: {
    AppSidebar,
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    const { railLayout, mobileOpen, openMobile } = useSidebar()
    const route = useRoute()

    // Icons are arrays of 24x24 stroke path strings (rendered inline, no icon library).
    const navItems = computed(() => [
      { to: '/', label: t('nav.overview'), icon: ['M4 4h7v7H4z', 'M13 4h7v7h-7z', 'M4 13h7v7H4z', 'M13 13h7v7h-7z'] },
      { to: '/inventory', label: t('nav.inventory'), icon: ['M21 8l-9-5-9 5v8l9 5 9-5z', 'M3 8l9 5 9-5', 'M12 13v8'] },
      { to: '/orders', label: t('nav.orders'), icon: ['M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2', 'M9 2h6v4H9z', 'M8 12h8', 'M8 16h5'] },
      { to: '/spending', label: t('nav.finance'), icon: ['M12 2v20', 'M17 6H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'] },
      { to: '/demand', label: t('nav.demandForecast'), icon: ['M3 17l6-6 4 4 8-8', 'M15 7h6v6'] },
      { to: '/reports', label: t('nav.reports'), icon: ['M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z', 'M14 2v6h6', 'M8 13h8', 'M8 17h5'] },
      { to: '/restocking', label: t('nav.restocking'), icon: ['M3 12a9 9 0 0 1 15-6.7L21 8', 'M21 3v5h-5', 'M21 12a9 9 0 0 1-15 6.7L3 16', 'M3 21v-5h5'] }
    ])

    // Shown in the mobile top bar; falls back to the company name on unknown routes.
    const currentTitle = computed(() => {
      const match = navItems.value.find(item => item.to === route.path)
      return match ? match.label : t('nav.companyName')
    })

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      railLayout,
      mobileOpen,
      openMobile,
      navItems,
      currentTitle,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<!-- Shell layout (scoped). Shared, cross-view styles live in the unscoped block below. -->
<style scoped>
.app {
  min-height: 100vh;
}

/* Main column is offset by the fixed sidebar width and animates with collapse. */
.app-main {
  margin-left: var(--sidebar-width);
  min-width: 0;
  min-height: 100vh;
  transition: margin-left var(--transition-base);
}

.app.sidebar-collapsed .app-main {
  margin-left: var(--sidebar-width-collapsed);
}

.topbar {
  display: none;
}

.main-content {
  max-width: var(--content-max-width);
  width: 100%;
  margin: 0 auto;
  padding: var(--space-6) var(--space-8);
}

/* Phone (< 640px): the sidebar is an off-canvas drawer, so no column offset and a top bar.
   Tablet keeps the 72px rail offset via the sidebar-collapsed class (railLayout). */
@media (max-width: 639px) {
  .app-main,
  .app.sidebar-collapsed .app-main {
    margin-left: 0;
  }

  .topbar {
    position: sticky;
    top: 0;
    z-index: var(--z-topbar);
    display: flex;
    align-items: center;
    gap: var(--space-3);
    height: var(--topbar-height);
    padding: 0 var(--space-4);
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
  }

  .menu-button {
    display: grid;
    place-items: center;
    width: 40px;
    height: 40px;
    border: 0;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--color-text-muted);
    cursor: pointer;
    transition: background var(--transition-fast), color var(--transition-fast);
  }

  .menu-button:hover {
    background: var(--color-surface-muted);
    color: var(--color-text);
  }

  .topbar-title {
    font-size: var(--text-md);
    font-weight: 700;
    color: var(--color-text);
    letter-spacing: -0.025em;
  }
}

@media (max-width: 639px) {
  .main-content {
    padding: var(--space-4);
  }
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  background: var(--color-bg);
  color: var(--color-text-secondary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Visible keyboard focus everywhere; mouse clicks do not trigger it. */
:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.page-header {
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-1);
  letter-spacing: -0.025em;
}

.page-header p {
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-surface);
  padding: var(--space-5);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
}

.stat-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-hover);
}

.stat-label {
  color: var(--color-text-muted);
  font-size: var(--text-base);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-3);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.stat-card.warning .stat-value {
  color: var(--color-warning);
}

.stat-card.success .stat-value {
  color: var(--color-success);
}

.stat-card.danger .stat-value {
  color: var(--color-danger);
}

.stat-card.info .stat-value {
  color: var(--color-info);
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-5);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-card);
  margin-bottom: var(--space-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap; /* title + actions/legend stack instead of overflowing on phones */
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

/* Wide tables scroll inside their container, never the page. */
.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}

th {
  text-align: left;
  padding: var(--space-2) var(--space-3);
  font-weight: 600;
  color: var(--color-text-label);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

td {
  padding: var(--space-2) var(--space-3);
  border-top: 1px solid var(--color-surface-muted);
  color: var(--color-text-secondary);
  font-size: var(--text-base);
}

tbody tr {
  transition: background-color var(--transition-fast);
}

tbody tr:hover {
  background: var(--color-bg);
}

.badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.badge.success,
.badge.increasing {
  background: var(--color-success-soft);
  color: var(--color-success-text);
}

.badge.warning,
.badge.medium {
  background: var(--color-warning-soft);
  color: var(--color-warning-text);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--color-danger-soft);
  color: var(--color-danger-text);
}

.badge.info,
.badge.low {
  background: var(--color-info-soft);
  color: var(--color-info-text);
}

.badge.stable {
  background: var(--color-stable-soft);
  color: var(--color-stable-text);
}

.loading {
  text-align: center;
  padding: var(--space-10);
  color: var(--color-text-muted);
  font-size: var(--text-base);
}

.error {
  background: var(--color-danger-bg);
  border: 1px solid var(--color-danger-soft);
  color: var(--color-danger-text);
  padding: var(--space-4);
  border-radius: var(--radius-sm);
  margin: var(--space-4) 0;
  font-size: var(--text-base);
}
</style>
