<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrder } from '../services/orderService'
import type { OrderDetailData } from '../services/orderService'
import { ArrowLeft, LoaderCircle, CreditCard, CheckCircle } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const order = ref<OrderDetailData | null>(null)
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

async function loadOrder() {
  const id = Number(route.params.id)
  if (!id) {
    router.replace({ name: 'order-history' })
    return
  }

  try {
    loading.value = true
    order.value = await getOrder(id)
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки заказа'
  } finally {
    loading.value = false
  }
}

onMounted(loadOrder)
</script>

<template>
  <main class="page order-detail-page">
    <div class="container">
      <div v-if="loading" class="detail-loading">
        <LoaderCircle :size="32" class="detail-loading__icon" />
        <p>{{ $t('common.loading') }}</p>
      </div>

      <div v-else-if="error" class="detail-error">
        <p>{{ error }}</p>
        <RouterLink :to="{ name: 'order-history' }" class="btn btn--outline">
          {{ $t('order.backToOrders') }}
        </RouterLink>
      </div>

      <template v-else-if="order">
        <div class="detail-header">
          <RouterLink :to="{ name: 'order-history' }" class="detail-back">
            <ArrowLeft :size="20" />
            {{ $t('order.backToOrders') }}
          </RouterLink>
          <h1 class="detail-title">{{ $t('order.orderNumber') }} #{{ order.id }}</h1>
        </div>

        <div class="detail-content">
          <div class="detail-info">
            <div class="detail-info__row">
              <span>{{ $t('order.status') }}</span>
              <span :class="['order-status', statusClass(order.status)]">
                {{ $t(`order.${statusLabels[order.status]}`) }}
              </span>
            </div>
            <div class="detail-info__row">
              <span>{{ $t('order.date') }}</span>
              <span>{{ new Date(order.createdAt).toLocaleDateString('ru-RU') }}</span>
            </div>
            <div v-if="order.paidAt" class="detail-info__row">
              <span>{{ $t('order.paidAt') }}</span>
              <span>{{ new Date(order.paidAt).toLocaleDateString('ru-RU') }}</span>
            </div>
          </div>

          <div class="detail-items">
            <h2 class="detail-section-title">
              {{ $t('cart.title') }} ({{ order.items.length }})
            </h2>
            <div v-for="item in order.items" :key="item.id" class="detail-item">
              <div class="detail-item__image">
                <img :src="item.photo.imageUrl" :alt="item.photo.title" />
              </div>
              <div class="detail-item__info">
                <p class="detail-item__title">{{ item.photo.title }}</p>
                <span class="detail-item__license">
                  {{ item.licenseType === 'personal' ? 'Персональная' : 'Коммерческая' }}
                </span>
              </div>
              <div class="detail-item__price">{{ formatPrice(item.price) }}</div>
            </div>
          </div>

          <div class="detail-total">
            <span>{{ $t('cart.total') }}:</span>
            <strong class="detail-total__price">{{ formatPrice(order.total) }}</strong>
          </div>

          <div v-if="order.status === 'pending'" class="detail-pay">
            <RouterLink
              :to="{ name: 'payment', params: { id: order.id } }"
              class="btn btn--primary btn--lg"
            >
              <CreditCard :size="18" />
              {{ $t('order.pay') }}
            </RouterLink>
          </div>

          <div v-if="order.status === 'paid'" class="detail-paid">
            <CheckCircle :size="20" />
            {{ $t('order.paySuccess') }}
          </div>
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

.detail-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6rem 2rem;
  gap: 1rem;
  color: var(--color-text-muted);
}

.detail-loading__icon {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.detail-error {
  text-align: center;
  padding: 4rem 2rem;
  color: #dc2626;
}

.detail-error .btn {
  margin-top: 1rem;
}

.detail-header {
  margin-bottom: 2rem;
}

.detail-back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin-bottom: 1rem;
  text-decoration: none;
  transition: color 0.2s ease;
}

.detail-back:hover {
  color: var(--color-accent);
}

.detail-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
}

.detail-content {
  display: grid;
  gap: 1.5rem;
  max-width: 640px;
}

.detail-section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 1rem;
}

.detail-info {
  display: grid;
  gap: 0.75rem;
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.1);
}

.detail-info__row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
  color: var(--color-text-muted);
}

.detail-info__row span:last-child {
  color: var(--color-text);
  font-weight: 500;
}

.detail-items {
  display: grid;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem;
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.detail-item__image {
  width: 64px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.05);
}

.detail-item__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-item__info {
  flex: 1;
  min-width: 0;
}

.detail-item__title {
  margin: 0 0 0.25rem;
  font-size: 0.95rem;
  font-weight: 500;
}

.detail-item__license {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.detail-item__price {
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
}

.detail-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.5), rgba(236, 253, 245, 0.2));
  font-size: 1.1rem;
  font-weight: 600;
}

.detail-total__price {
  font-size: 1.25rem;
  color: var(--color-accent);
}

.detail-pay {
  display: flex;
  justify-content: center;
}

.detail-pay .btn {
  gap: 0.5rem;
}

.detail-paid {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(236, 253, 245, 0.5);
  color: var(--color-accent);
  font-weight: 600;
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
</style>
