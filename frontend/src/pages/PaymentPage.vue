<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getOrder, payOrder } from '../services/orderService'
import type { OrderDetailData } from '../services/orderService'
import { CreditCard, LoaderCircle, CheckCircle } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const order = ref<OrderDetailData | null>(null)
const loading = ref(true)
const paying = ref(false)
const paid = ref(false)
const error = ref('')

async function loadOrder() {
  const id = Number(route.params.id)
  if (!id) {
    router.replace({ name: 'home' })
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

async function handlePay() {
  const id = Number(route.params.id)
  if (!id) return

  paying.value = true
  error.value = ''

  try {
    order.value = await payOrder(id)
    paid.value = true
  } catch (e: any) {
    error.value = e.message || 'Ошибка оплаты'
  } finally {
    paying.value = false
  }
}

function formatPrice(price: number) {
  return `₽${price.toLocaleString()}`
}

onMounted(loadOrder)
</script>

<template>
  <main class="page payment-page">
    <div class="container payment-container">
      <div v-if="loading" class="payment-loading">
        <LoaderCircle :size="32" class="payment-loading__icon" />
        <p>{{ $t('common.loading') }}</p>
      </div>

      <div v-else-if="error && !order" class="payment-error">
        <p>{{ error }}</p>
        <RouterLink :to="{ name: 'order-history' }" class="btn btn--outline">
          {{ $t('order.backToOrders') }}
        </RouterLink>
      </div>

      <template v-else-if="order">
        <div v-if="paid" class="payment-success">
          <div class="payment-success__icon">
            <CheckCircle :size="48" />
          </div>
          <h1 class="payment-success__title">{{ $t('order.paySuccess') }}</h1>
          <p class="payment-success__desc">
            {{ $t('order.orderNumber') }} #{{ order.id }} — {{ formatPrice(order.total) }}
          </p>
          <RouterLink :to="{ name: 'order-detail', params: { id: order.id } }" class="btn btn--primary">
            {{ $t('common.actions') }}
          </RouterLink>
        </div>

        <div v-else class="payment-card">
          <div class="payment-card__header">
            <CreditCard :size="32" class="payment-card__icon" />
            <h1 class="payment-card__title">{{ $t('order.payTitle') }}</h1>
            <p class="payment-card__desc">{{ $t('order.payDescription') }}</p>
          </div>

          <div class="payment-card__order">
            <div class="payment-card__order-row">
              <span>{{ $t('order.orderNumber') }}</span>
              <strong>#{{ order.id }}</strong>
            </div>
            <div class="payment-card__order-row">
              <span>{{ $t('order.status') }}</span>
              <span class="payment-card__status payment-card__status--pending">
                {{ $t('order.statusPending') }}
              </span>
            </div>
            <div class="payment-card__order-row">
              <span>{{ $t('order.date') }}</span>
              <span>{{ new Date(order.createdAt).toLocaleDateString('ru-RU') }}</span>
            </div>
            <div class="payment-card__divider" />
            <div class="payment-card__order-row payment-card__order-row--total">
              <span>{{ $t('order.total') }}</span>
              <strong class="payment-card__total-price">{{ formatPrice(order.total) }}</strong>
            </div>
          </div>

          <div v-if="error" class="payment-card__error">
            {{ error }}
          </div>

          <button
            class="btn btn--primary btn--lg payment-card__btn"
            :disabled="paying"
            @click="handlePay"
          >
            <LoaderCircle v-if="paying" :size="18" class="payment-card__spinner" />
            {{ $t('order.pay') }} — {{ formatPrice(order.total) }}
          </button>
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

.payment-container {
  max-width: 480px;
}

.payment-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6rem 2rem;
  gap: 1rem;
  color: var(--color-text-muted);
}

.payment-loading__icon {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.payment-error {
  text-align: center;
  padding: 4rem 2rem;
  color: #dc2626;
}

.payment-error .btn {
  margin-top: 1rem;
}

.payment-success {
  text-align: center;
  padding: 4rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.payment-success__icon {
  color: var(--color-accent);
  animation: scaleIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes scaleIn {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

.payment-success__title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
}

.payment-success__desc {
  color: var(--color-text-muted);
  margin: 0;
}

/* Card */
.payment-card {
  padding: 2rem;
  border-radius: 24px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: #ffffff;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.08);
  display: grid;
  gap: 1.5rem;
}

.payment-card__header {
  text-align: center;
  display: grid;
  gap: 0.75rem;
  justify-items: center;
}

.payment-card__icon {
  color: var(--color-accent);
  opacity: 0.8;
}

.payment-card__title {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 700;
}

.payment-card__desc {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.payment-card__order {
  padding: 1.25rem;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.03);
  display: grid;
  gap: 0.75rem;
}

.payment-card__order-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
  color: var(--color-text-muted);
}

.payment-card__order-row strong {
  color: var(--color-text);
}

.payment-card__order-row--total {
  font-size: 1.1rem;
  color: var(--color-text);
}

.payment-card__total-price {
  color: var(--color-accent);
  font-size: 1.25rem;
}

.payment-card__status--pending {
  color: #d97706;
  font-weight: 600;
}

.payment-card__divider {
  height: 1px;
  background: rgba(15, 23, 42, 0.08);
}

.payment-card__error {
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
  border-radius: 10px;
  font-size: 0.9rem;
  text-align: center;
}

.payment-card__btn {
  width: 100%;
  justify-content: center;
}

.payment-card__spinner {
  animation: spin 0.8s linear infinite;
}

.btn--lg {
  padding: 0.875rem 2rem;
  font-size: 1.05rem;
}
</style>
