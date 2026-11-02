<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

const { t, currentCurrency } = useI18n()

const BUDGET_STEP = 100
const MAX_ROUNDING = 1000
const TREND_RANK = { increasing: 0, stable: 1, decreasing: 2 }

const loading = ref(true)
const error = ref(null)
const forecasts = ref([])
const inventoryItems = ref([])
const budget = ref(0)

const submitting = ref(false)
const submitError = ref(null)
const placedOrder = ref(null)

// Stock by SKU; SKUs missing from inventory count as 0
const stockBySku = computed(() => {
  const map = {}
  for (const item of inventoryItems.value) {
    map[item.sku] = (map[item.sku] || 0) + (item.quantity_on_hand || 0)
  }
  return map
})

// Forecasts with unmet need (forecast minus stock), carrying growth for ranking
const needLines = computed(() => {
  return forecasts.value
    .map(f => {
      const stock = stockBySku.value[f.item_sku] || 0
      const need = Math.max(f.forecasted_demand - stock, 0)
      const growth = f.current_demand > 0
        ? (f.forecasted_demand - f.current_demand) / f.current_demand
        : 0
      return {
        id: f.id,
        sku: f.item_sku,
        name: f.item_name,
        trend: f.trend,
        forecastedDemand: f.forecasted_demand,
        stock,
        need,
        growth,
        unitCost: f.unit_cost,
        leadTime: f.lead_time_days
      }
    })
    .filter(line => line.need > 0)
})

// Slider max: total cost of all unmet need, rounded up to the next 1000
const maxBudget = computed(() => {
  const total = needLines.value.reduce((sum, l) => sum + l.need * l.unitCost, 0)
  return Math.max(Math.ceil(total / MAX_ROUNDING) * MAX_ROUNDING, MAX_ROUNDING)
})

// Rank by trend, then growth descending; greedy fill, skipping lines that do not fit
const recommended = computed(() => {
  const ranked = [...needLines.value].sort((a, b) => {
    const byTrend = (TREND_RANK[a.trend] ?? 3) - (TREND_RANK[b.trend] ?? 3)
    return byTrend !== 0 ? byTrend : b.growth - a.growth
  })

  let remaining = budget.value
  const picked = []
  for (const line of ranked) {
    const cost = line.need * line.unitCost
    if (cost <= remaining) {
      picked.push({ ...line, quantity: line.need, cost })
      remaining -= cost
    }
  }
  return picked
})

const allocated = computed(() => recommended.value.reduce((sum, l) => sum + l.cost, 0))
const remainingBudget = computed(() => Math.max(budget.value - allocated.value, 0))
const notFittingCount = computed(() => forecasts.value.length - recommended.value.length)

const money = (amount) => formatCurrency(amount, currentCurrency.value)
const moneyDetailed = (amount) => formatCurrencyWithDecimals(amount, currentCurrency.value, 2)

const loadData = async () => {
  try {
    loading.value = true
    error.value = null
    const [forecastData, inventoryData] = await Promise.all([
      api.getDemandForecasts(),
      api.getInventory()
    ])
    forecasts.value = forecastData
    inventoryItems.value = inventoryData
    // Default budget: half of max (max is a multiple of 1000, so this stays on the step grid)
    budget.value = Math.round(maxBudget.value / 2 / BUDGET_STEP) * BUDGET_STEP
  } catch (err) {
    error.value = t('restocking.loadError') + ': ' + err.message
  } finally {
    loading.value = false
  }
}

const placeOrder = async () => {
  if (submitting.value || recommended.value.length === 0) return
  submitting.value = true
  submitError.value = null
  placedOrder.value = null
  try {
    placedOrder.value = await api.createRestockingOrder({
      items: recommended.value.map(({ sku, quantity }) => ({ sku, quantity }))
    })
  } catch (err) {
    submitError.value = err.response?.data?.detail || t('restocking.errorFallback')
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.budget') }}</div>
          <div class="stat-value">{{ money(budget) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.allocated') }}</div>
          <div class="stat-value">{{ money(allocated) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.remaining') }}</div>
          <div class="stat-value">{{ money(remainingBudget) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="slider-header">
          <label for="budget-slider" class="card-title">{{ t('restocking.budgetSlider') }}</label>
          <span class="slider-value">{{ money(budget) }}</span>
        </div>
        <input
          id="budget-slider"
          v-model.number="budget"
          type="range"
          class="budget-slider"
          min="0"
          :max="maxBudget"
          :step="BUDGET_STEP"
        />
        <div class="slider-scale">
          <span>{{ money(0) }}</span>
          <span>{{ money(maxBudget) }}</span>
        </div>
        <p class="muted">{{ t('restocking.budgetHint') }}</p>
      </div>

      <div v-if="placedOrder" class="banner banner-success" role="status">
        <div>
          <strong>{{ t('restocking.successTitle') }}</strong>
          {{ t('restocking.successMessage', {
            orderNumber: placedOrder.order_number,
            total: money(placedOrder.total_value),
            days: placedOrder.lead_time_days
          }) }}
        </div>
        <router-link to="/orders" class="banner-link">{{ t('restocking.viewOrder') }}</router-link>
      </div>
      <div v-if="submitError" class="banner banner-error" role="alert">{{ submitError }}</div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">
            {{ t('restocking.recommendation') }} ({{ t('restocking.itemsCount', { count: recommended.length }) }})
          </h3>
          <button
            type="button"
            class="btn-primary"
            :disabled="recommended.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="recommended.length === 0" class="empty-state">{{ t('restocking.empty') }}</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.item') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.forecastedDemand') }}</th>
                <th class="num">{{ t('restocking.table.inStock') }}</th>
                <th class="num">{{ t('restocking.table.orderQty') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="line in recommended" :key="line.sku">
                <td><strong>{{ line.sku }}</strong></td>
                <td>{{ line.name }}</td>
                <td>
                  <span :class="['badge', line.trend]">{{ t(`trends.${line.trend}`) }}</span>
                </td>
                <td class="num">{{ line.forecastedDemand }}</td>
                <td class="num">{{ line.stock }}</td>
                <td class="num"><strong>{{ line.quantity }}</strong></td>
                <td class="num">{{ moneyDetailed(line.unitCost) }}</td>
                <td class="num"><strong>{{ money(line.cost) }}</strong></td>
                <td class="num">{{ t('orders.leadTimeDays', { count: line.leadTime }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-if="notFittingCount > 0" class="muted note">
          {{ t('restocking.notFitting', { count: notFittingCount }) }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.75rem;
}

.slider-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
}

.budget-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
  cursor: pointer;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #2563eb;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.3);
}

.budget-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #2563eb;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.3);
}

.budget-slider:focus-visible {
  box-shadow: 0 0 0 3px #dbeafe;
}

.slider-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
}

.muted {
  color: #64748b;
  font-size: 0.813rem;
}

.card > .muted {
  margin-top: 0.75rem;
}

.note {
  margin-top: 1rem;
}

.num {
  text-align: right;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
  font-size: 0.938rem;
}

.btn-primary {
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.938rem;
}

.banner-success {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
}

.banner-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.banner-link {
  color: #065f46;
  font-weight: 600;
  text-decoration: underline;
  white-space: nowrap;
}
</style>
