<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { auth } from '../utils/auth'
import { getCart, removeFromCart, updateCartItem, addToCart } from '../services/cartService'
import type { CartData, CartItemData } from '../services/cartService'
import { Trash2, ShoppingCart } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const cart = ref<CartData | null>(null)
const loading = ref(true)
const error = ref('')

const isAuthenticated = computed(() => auth.isAuthenticated())

const items = computed(() => cart.value?.items || [])
const total = computed(() => cart.value?.total || 0)

async function loadCart() {
  if (!isAuthenticated.value) {
    loading.value = false
    return
  }

  try {
    loading.value = true
    error.value = ''
    cart.value = await getCart()
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки корзины'
  } finally {
    loading.value = false
  }
}

async function handleAddFromQuery() {
  const addId = route.query.add as string
  const license = (route.query.license as string) || 'personal'
  if (!addId || !isAuthenticated.value) return

  try {
    await addToCart(addId, license)
    await loadCart()
    // clean query params
    router.replace({ query: {} })
  } catch (e: any) {
    error.value = e.message || 'Ошибка при добавлении в корзину'
  }
}

async function handleRemove(itemId: number) {
  try {
    await removeFromCart(itemId)
    await loadCart()
  } catch (e: any) {
    error.value = e.message || 'Ошибка удаления'
  }
}

async function handleChangeLicense(item: CartItemData) {
  const newLicense = item.licenseType === 'personal' ? 'commercial' : 'personal'
  try {
    await updateCartItem(item.id, newLicense)
    await loadCart()
  } catch (e: any) {
    error.value = e.message || 'Ошибка обновления'
  }
}

function handleGoToCheckout() {
  router.push({ name: 'checkout' })
}

function formatPrice(price: number) {
  return `₽${price.toLocaleString()}`
}

onMounted(async () => {
  await loadCart()
  await handleAddFromQuery()
})
</script>

<template>
  <main class="page cart-page">
    <div class="container">
      <div v-if="loading" class="cart-loading">
        <div class="cart-loading__spinner" />
        <p>{{ $t('common.loading') }}</p>
      </div>

      <div v-else-if="!isAuthenticated" class="cart-empty">
        <ShoppingCart :size="48" class="cart-empty__icon" />
        <h1 class="cart-empty__title">{{ $t('cart.title') }}</h1>
        <p class="cart-empty__desc">{{ $t('auth.loginTitle') }}</p>
        <RouterLink :to="{ name: 'login', query: { redirect: route.fullPath } }" class="btn btn--primary">
          {{ $t('nav.login') }}
        </RouterLink>
      </div>

      <div v-else-if="items.length === 0" class="cart-empty">
        <ShoppingCart :size="48" class="cart-empty__icon" />
        <h1 class="cart-empty__title">{{ $t('cart.empty') }}</h1>
        <p class="cart-empty__desc">{{ $t('cart.emptyDesc') }}</p>
        <RouterLink :to="{ name: 'catalog-photos' }" class="btn btn--primary">
          {{ $t('cart.goToCatalog') }}
        </RouterLink>
      </div>

      <template v-else>
        <div class="cart-header">
          <h1 class="cart-header__title">{{ $t('cart.title') }}</h1>
          <span class="cart-header__count">{{ items.length }} {{ $t('cart.items') }}</span>
        </div>

        <div v-if="error" class="cart-error">
          {{ error }}
        </div>

        <div class="cart-items">
          <div v-for="item in items" :key="item.id" class="cart-item">
            <div class="cart-item__image">
              <img :src="item.photo.imageUrl" :alt="item.photo.title" />
            </div>
            <div class="cart-item__info">
              <h3 class="cart-item__title">{{ item.photo.title }}</h3>
              <p class="cart-item__category">{{ item.photo.category }}</p>
              <button
                class="cart-item__license"
                @click="handleChangeLicense(item)"
                :title="$t('common.actions')"
              >
                {{ item.licenseType === 'personal' ? 'Персональная' : 'Коммерческая' }}
              </button>
            </div>
            <div class="cart-item__price">
              {{ formatPrice(item.price) }}
            </div>
            <button
              class="cart-item__remove"
              @click="handleRemove(item.id)"
              :aria-label="$t('cart.remove')"
            >
              <Trash2 :size="18" />
            </button>
          </div>
        </div>

        <div class="cart-footer">
          <div class="cart-footer__total">
            <span class="cart-footer__total-label">{{ $t('cart.total') }}:</span>
            <span class="cart-footer__total-price">{{ formatPrice(total) }}</span>
          </div>
          <button class="btn btn--primary btn--lg" @click="handleGoToCheckout">
            {{ $t('cart.checkout') }}
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

/* Loading */
.cart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6rem 2rem;
  gap: 1rem;
  color: var(--color-text-muted);
}

.cart-loading__spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(15, 23, 42, 0.1);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Empty */
.cart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6rem 2rem;
  text-align: center;
  gap: 1rem;
}

.cart-empty__icon {
  color: var(--color-text-muted);
  opacity: 0.4;
  margin-bottom: 0.5rem;
}

.cart-empty__title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.cart-empty__desc {
  color: var(--color-text-muted);
  margin: 0;
  max-width: 400px;
}

/* Header */
.cart-header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 2rem;
}

.cart-header__title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
}

.cart-header__count {
  color: var(--color-text-muted);
  font-size: 1rem;
}

/* Error */
.cart-error {
  padding: 1rem;
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

/* Items */
.cart-items {
  display: grid;
  gap: 1rem;
  margin-bottom: 2rem;
}

.cart-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: #ffffff;
  transition: box-shadow 0.2s ease;
}

.cart-item:hover {
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.08);
}

.cart-item__image {
  width: 80px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(15, 23, 42, 0.05);
}

.cart-item__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cart-item__info {
  flex: 1;
  min-width: 0;
}

.cart-item__title {
  margin: 0 0 0.25rem;
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cart-item__category {
  margin: 0 0 0.5rem;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.cart-item__license {
  font-size: 0.8rem;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(16, 185, 129, 0.3);
  background: rgba(236, 253, 245, 0.5);
  color: var(--color-accent);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.cart-item__license:hover {
  background: rgba(236, 253, 245, 0.8);
  border-color: var(--color-accent);
}

.cart-item__price {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-text);
  white-space: nowrap;
}

.cart-item__remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.cart-item__remove:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

/* Footer */
.cart-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.5), rgba(236, 253, 245, 0.2));
  border: 1px solid rgba(16, 185, 129, 0.15);
}

.cart-footer__total {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.cart-footer__total-label {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
}

.cart-footer__total-price {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-accent);
}

.btn--lg {
  padding: 0.875rem 2rem;
  font-size: 1.05rem;
}

@media (max-width: 640px) {
  .cart-item {
    flex-wrap: wrap;
  }

  .cart-item__price {
    margin-left: auto;
  }

  .cart-footer {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }

  .cart-footer .btn {
    width: 100%;
  }
}
</style>
