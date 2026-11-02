import { ref, computed, watch, getCurrentInstance, onMounted, onBeforeUnmount } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'

// Breakpoints (CSS vars cannot be used in media queries, so they live here and in
// the matching @media rules): desktop >= 1024px, tablet 640-1023px, phone < 640px.
const DESKTOP_QUERY = '(min-width: 1024px)'
const TABLET_QUERY = '(min-width: 640px)'

function getMql(query) {
  // matchMedia may be missing (tests, very old browsers); callers fall back to desktop.
  try {
    return typeof window !== 'undefined' && window.matchMedia ? window.matchMedia(query) : null
  } catch {
    return null
  }
}

function readViewport() {
  const desktop = getMql(DESKTOP_QUERY)
  const tablet = getMql(TABLET_QUERY)
  if (!desktop || !tablet) return 'desktop'
  if (desktop.matches) return 'desktop'
  return tablet.matches ? 'tablet' : 'phone'
}

function readStored() {
  // localStorage can throw (private mode, blocked storage); fall back to expanded.
  try {
    return localStorage.getItem(STORAGE_KEY) === 'true'
  } catch {
    return false
  }
}

// Module-level refs so the shell and the sidebar share one state without prop drilling.
// `collapsed` is ONLY the desktop preference and is the only thing persisted; the
// tablet rail is derived from the viewport so it can never overwrite that preference.
const collapsed = ref(readStored())
// Temporary expansion: the off-canvas drawer on phones, the overlay on tablets.
const mobileOpen = ref(false)
const viewport = ref(readViewport())

watch(collapsed, (value) => {
  try {
    localStorage.setItem(STORAGE_KEY, String(value))
  } catch {
    // Persistence is a convenience only; ignore failures.
  }
})

// Reset the temporary state whenever a breakpoint is crossed so a stale overlay or
// drawer never lingers (e.g. the backdrop staying up after a rotate/resize).
watch(viewport, () => {
  mobileOpen.value = false
})

// Listeners are attached once per mounted consumer and removed when the last unmounts.
let consumers = 0
let desktopMql = null
let tabletMql = null
const onViewportChange = () => {
  viewport.value = readViewport()
}

function attach() {
  if (consumers++ > 0) return
  desktopMql = getMql(DESKTOP_QUERY)
  tabletMql = getMql(TABLET_QUERY)
  desktopMql?.addEventListener?.('change', onViewportChange)
  tabletMql?.addEventListener?.('change', onViewportChange)
  onViewportChange() // sync in case the size changed before mount
}

function detach() {
  if (--consumers > 0) return
  desktopMql?.removeEventListener?.('change', onViewportChange)
  tabletMql?.removeEventListener?.('change', onViewportChange)
  desktopMql = null
  tabletMql = null
}

export function useSidebar() {
  if (getCurrentInstance()) {
    onMounted(attach)
    onBeforeUnmount(detach)
  }

  // True when the sidebar renders as the 72px icon rail.
  const isRail = computed(() => {
    if (viewport.value === 'desktop') return collapsed.value
    if (viewport.value === 'tablet') return !mobileOpen.value
    return false // phone: drawer is always full width
  })

  // True when the main column should be offset by the rail width. On tablet the
  // offset stays 72px even while expanded, because the expanded sidebar overlays.
  const railLayout = computed(() =>
    viewport.value === 'tablet' || (viewport.value === 'desktop' && collapsed.value)
  )

  const toggleCollapsed = () => {
    if (viewport.value === 'desktop') {
      collapsed.value = !collapsed.value
    } else {
      mobileOpen.value = !mobileOpen.value
    }
  }
  const openMobile = () => {
    mobileOpen.value = true
  }
  const closeMobile = () => {
    mobileOpen.value = false
  }

  return { collapsed, mobileOpen, viewport, isRail, railLayout, toggleCollapsed, openMobile, closeMobile }
}
