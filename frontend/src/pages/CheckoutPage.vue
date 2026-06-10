<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCart, checkout } from '../services/cartService'
import type { CartData } from '../services/cartService'
import { ArrowLeft, LoaderCircle } from 'lucide-vue-next'

const router = useRouter()

const cart = ref<CartData | null>(null)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

const items = computed(() => cart.value?.items || [])
const total = computed(() => cart.value?.total || 0)

async function loadCart() {
  try {
    loading.value = true
    cart.value = await getCart()
    if (!cart.value || cart.value.items.length === 0) {
      router.replace({ name: 'cart' })
    }
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки корзины'
  } finally {
    loading.value = false
  }
}

async function handlePlaceOrder() {
  submitting.value = true
  error.value = ''

  try {
    const order = await checkout()
    router.push({ name: 'payment', params: { id: order.id } })
  } catch (e: any) {
    error.value = e.message || 'Ошибка оформления заказа'
  } finally {
    submitting.value = false
  }
}

function formatPrice(price: number) {
  return `₽${price.toLocaleString()}`
}

onMounted(loadCart)
</script>

<template>
  <main class="page checkout-page">
    <div class="container">
      <div v-if="loading" class="checkout-loading">
        <LoaderCircle :size="32" class="checkout-loading__icon" />
        <p>{{ $t('common.loading') }}</p>
      </div>

      <template v-else-if="cart">
        <div class="checkout-header">
          <RouterLink :to="{ name: 'cart' }" class="checkout-back">
            <ArrowLeft :size="20" />
            {{ $t('common.back') }}
          </RouterLink>
          <h1 class="checkout-title">{{ $t('cart.checkout') }}</h1>
        </div>

        <div v-if="error" class="checkout-error">
          {{ error }}
        </div>

        <div class="checkout-content">
          <div class="checkout-items">
            <h2 class="checkout-section-title">{{ $t('cart.title') }} ({{ items.length }})</h2>
            <div v-for="item in items" :key="item.id" class="checkout-item">
              <div class="checkout-item__image">
                <img :src="item.photo.imageUrl" :alt="item.photo.title" />
              </div>
              <div class="checkout-item__info">
                <p class="checkout-item__title">{{ item.photo.title }}</p>
                <span class="checkout-item__license">
                  {{ item.licenseType === 'personal' ? 'Персональная' : 'Коммерческая' }}
                </span>
              </div>
              <div class="checkout-item__price">
                {{ formatPrice(item.price) }}
              </div>
            </div>
          </div>

          <div class="checkout-summary">
            <h2 class="checkout-section-title">{{ $t('cart.total') }}</h2>
            <div class="checkout-summary__row">
              <span>{{ $t('cart.sum') }} ({{ items.length }} {{ $t('cart.items') }})</span>
              <span>{{ formatPrice(total) }}</span>
            </div>
            <div class="checkout-summary__divider" />
            <div class="checkout-summary__row checkout-summary__row--total">
              <span>{{ $t('cart.total') }}</span>
              <span class="checkout-summary__total-price">{{ formatPrice(total) }}</span>
            </div>
            <button
              class="btn btn--primary btn--lg checkout-submit"
              :disabled="submitting"
              @click="handlePlaceOrder"
            >
              <LoaderCircle v-if="submitting" :size="18" class="checkout-submit__spinner" />
              {{ $t('cart.checkout') }}
            </button>
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

.checkout-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 6rem 2rem;
  gap: 1rem;
  color: var(--color-text-muted);
}

.checkout-loading__icon {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.checkout-header {
  margin-bottom: 2rem;
}

.checkout-back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
  margin-bottom: 1rem;
  text-decoration: none;
  transition: color 0.2s ease;
}

.checkout-back:hover {
  color: var(--color-accent);
}

.checkout-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
}

.checkout-error {
  padding: 1rem;
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.checkout-content {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 2rem;
  align-items: start;
}

.checkout-section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 1rem;
}

.checkout-items {
  display: grid;
  gap: 0.75rem;
}

.checkout-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem;
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.08);
}

.checkout-item__image {
  width: 64px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.05);
}

.checkout-item__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.checkout-item__info {
  flex: 1;
  min-width: 0;
}

.checkout-item__title {
  margin: 0 0 0.25rem;
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.checkout-item__license {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.checkout-item__price {
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
}

.checkout-summary {
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.4), rgba(236, 253, 245, 0.1));
  position: sticky;
  top: calc(var(--header-height) + 2rem);
}

.checkout-summary__row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  font-size: 0.95rem;
  color: var(--color-text-muted);
}

.checkout-summary__row--total {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text);
  padding-top: 0.75rem;
}

.checkout-summary__divider {
  height: 1px;
  background: rgba(15, 23, 42, 0.1);
  margin: 0.25rem 0;
}

.checkout-summary__total-price {
  color: var(--color-accent);
  font-size: 1.25rem;
}

.checkout-submit {
  width: 100%;
  margin-top: 1.5rem;
  justify-content: center;
}

.checkout-submit__spinner {
  animation: spin 0.8s linear infinite;
}

.btn--lg {
  padding: 0.875rem 2rem;
  font-size: 1.05rem;
}

@media (max-width: 900px) {
  .checkout-content {
    grid-template-columns: 1fr;
  }

  .checkout-summary {
    position: static;
  }
}
</style>
