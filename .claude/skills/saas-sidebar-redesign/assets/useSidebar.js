import { ref, watch } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'

// Module-level refs so the shell, sidebar and top bar share one state
// without prop drilling.
const collapsed = ref(readStored())
const mobileOpen = ref(false)

function readStored() {
  // localStorage can throw (private mode, blocked storage); fall back to expanded.
  try {
    return localStorage.getItem(STORAGE_KEY) === 'true'
  } catch {
    return false
  }
}

watch(collapsed, (value) => {
  try {
    localStorage.setItem(STORAGE_KEY, String(value))
  } catch {
    // Persistence is a convenience only; ignore failures.
  }
})

export function useSidebar() {
  const toggleCollapsed = () => {
    collapsed.value = !collapsed.value
  }
  const openMobile = () => {
    mobileOpen.value = true
  }
  const closeMobile = () => {
    mobileOpen.value = false
  }

  return { collapsed, mobileOpen, toggleCollapsed, openMobile, closeMobile }
}
