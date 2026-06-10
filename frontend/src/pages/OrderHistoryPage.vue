<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getOrders } from '../services/orderService'
import type { OrderListData } from '../services/orderService'
import { Package, LoaderCircle } from 'lucide-vue-next'

const orders = ref<OrderListData[]>([])
const loading = ref(true)
const error = ref('')

const statusLabels: Record<string, string> = {
  pending: 'statusPending',
  paid: 'statusPaid',
  cancelled: 'statusCancelled',
}

function statusClass(status: string) {
  return `order-status--${status}`
}

function formatPrice(price: number) {
  return `₽${price.toLocaleString()}`
}

async function loadOrders() {
  try {
    loading.value = true
    orders.value = await getOrders()
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки заказов'
  } finally {
    loading.value = false
  }
}

onMounted(loadOrders)
</script>

<template>
  <main class="page orders-page">
    <div class="container">
      <div v-if="loading" class="orders-loading">
        <LoaderCircle :size="32" class="orders-loading__icon" />
        <p>{{ $t('common.loading') }}</p>
      </div>

      <div v-else-if="orders.length === 0" class="orders-empty">
        <Package :size="48" class="orders-empty__icon" />
        <h1 class="orders-empty__title">{{ $t('order.noOrders') }}</h1>
        <p class="orders-empty__desc">{{ $t('order.noOrdersDesc') }}</p>
        <RouterLink :to="{ name: 'catalog-photos' }" class="btn btn--primary">
          {{ $t('cart.goToCatalog') }}
        </RouterLink>
      </div>

      <template v-else>
        <div class="orders-header">
          <h1 class="orders-header__title">{{ $t('order.orders') }}</h1>
        </div>

        <div v-if="error" class="orders-error">{{ error }}</div>

        <div class="orders-list">
          <RouterLink
            v-for="order in orders"
            :key="order.id"
            :to="{ name: 'order-detail', params: { id: order.id } }"
            class="order-card"
          >
            <div class="order-card__main">
              <div class="order-card__id">
                {{ $t('order.orderNumber') }} #{{ order.id }}
              </div>
              <div class="order-card__meta">
                <span class="order-card__date">
                  {{ new Date(order.createdAt).toLocaleDateString('ru-RU') }}
                </span>
                <span class="order-card__items">
                  {{ order.itemsCount }} {{ $t('cart.items') }}
                </span>
              </div>
            </div>
            <div class="order-card__side">
              <span :class="['order-status', statusClass(order.status)]">
                {{ $t(`order.${statusLabels[order.status]}`) }}
              </span>
              <span class="order-card__price">{{ formatPrice(order.total) }}</span>
            </div>
          </RouterLink>
        </div>
      </template>
    </div>
  </main>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding-top: calc(var(--header-height) + 2rem);
  padding-bottom: 4rem;
}

.orders-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6rem 2rem;
  gap: 1rem;
  color: var(--color-text-muted);
}

.orders-loading__icon {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.orders-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6rem 2rem;
  text-align: center;
  gap: 1rem;
}

.orders-empty__icon {
  color: var(--color-text-muted);
  opacity: 0.4;
}

.orders-empty__title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.orders-empty__desc {
  color: var(--color-text-muted);
  margin: 0;
}

.orders-header {
  margin-bottom: 2rem;
}

.orders-header__title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
}

.orders-error {
  padding: 1rem;
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.orders-list {
  display: grid;
  gap: 0.75rem;
}

.order-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: #ffffff;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
  cursor: pointer;
}

.order-card:hover {
  border-color: rgba(16, 185, 129, 0.3);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.08);
  transform: translateY(-2px);
}

.order-card__main {
  display: grid;
  gap: 0.35rem;
}

.order-card__id {
  font-weight: 600;
  font-size: 1.05rem;
}

.order-card__meta {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.order-card__side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
}

.order-card__price {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--color-text);
}

.order-status {
  font-size: 0.8rem;
  padding: 0.2rem 0.75rem;
  border-radius: 999px;
  font-weight: 500;
}

.order-status--pending {
  background: rgba(217, 119, 6, 0.1);
  color: #d97706;
}

.order-status--paid {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-accent);
}

.order-status--cancelled {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

@media (max-width: 640px) {
  .order-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .order-card__side {
    flex-direction: row;
    align-items: center;
    width: 100%;
    justify-content: space-between;
  }
}
</style>
