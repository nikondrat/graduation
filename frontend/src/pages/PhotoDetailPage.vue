<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Teleport } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import LicenseSelector from '../components/LicenseSelector.vue'
import SimilarPhotos from '../components/SimilarPhotos.vue'
import AuthorAvatar from '../components/common/AuthorAvatar.vue'
import type { Photo } from '../data/photos'
import { getPhoto, getSimilarPhotos } from '../services/photoService'
import { addToCart } from '../services/cartService'
import { auth } from '../utils/auth'
import { Maximize2, ArrowRight } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const photo = ref<Photo | null>(null)
const similarPhotos = ref<Photo[]>([])
const loading = ref(true)
const selectedLicenseId = ref('')
const imageZoomed = ref(false)
const isFavorite = ref(false)

const FAVORITES_KEY = 'ft_favorites'

function checkFavorite() {
  const saved = localStorage.getItem(FAVORITES_KEY)
  if (saved && photo.value) {
    const ids = JSON.parse(saved)
    isFavorite.value = ids.includes(photo.value.id)
  }
}

function toggleFavorite() {
  if (!photo.value) return
  
  const saved = localStorage.getItem(FAVORITES_KEY)
  let ids = saved ? JSON.parse(saved) : []
  
  const idx = ids.indexOf(photo.value.id)
  if (idx === -1) {
    ids.push(photo.value.id)
    isFavorite.value = true
  } else {
    ids.splice(idx, 1)
    isFavorite.value = false
  }
  
  localStorage.setItem(FAVORITES_KEY, JSON.stringify(ids))
}

const nextSimilarPhoto = computed(() => (similarPhotos.value.length > 0 ? similarPhotos.value[0] : null))

// Загрузка данных фотографии
async function loadPhotoData() {
  const photoId = route.params.id as string

  try {
    loading.value = true
    const photoData = await getPhoto(photoId)

    if (!photoData) {
      router.push({ name: 'catalog-photos' })
      return
    }

    photo.value = photoData
    checkFavorite()

    // Выбираем первую лицензию по умолчанию
    if (photoData.licenseTypes && photoData.licenseTypes.length > 0) {
      const firstLicense = photoData.licenseTypes[0]
      if (firstLicense) {
        selectedLicenseId.value = firstLicense.id
      }
    }

    // Загружаем похожие фото
    const similar = await getSimilarPhotos(photoId, photoData.category, 6)
    similarPhotos.value = similar
  } catch (error) {
    console.error('Ошибка загрузки фотографии:', error)
    router.push({ name: 'catalog-photos' })
  } finally {
    loading.value = false
  }
}

const selectedLicense = computed(() => {
  if (!photo.value) return null
  return photo.value.licenseTypes.find((l) => l.id === selectedLicenseId.value)
})

const totalPrice = computed(() => {
  return selectedLicense.value?.price || 0
})

async function handleBuy() {
  if (!auth.isAuthenticated()) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  if (!photo.value || !selectedLicenseId.value) return

  try {
    await addToCart(photo.value.id, selectedLicenseId.value)
    router.push({ name: 'cart' })
  } catch (e: any) {
    console.error('Ошибка добавления в корзину:', e)
  }
}

function toggleZoom() {
  if (!photo.value) return
  imageZoomed.value = !imageZoomed.value
  
  if (imageZoomed.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

function formatDate(dateString: string) {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// Отслеживание изменения ID в роуте
watch(
  () => route.params.id,
  () => {
    if (route.params.id) {
      loadPhotoData()
    }
  },
  { immediate: true }
)

onMounted(() => {
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<template>
  <main class="page photo-detail-page">
    <div v-if="loading" class="photo-detail-loading">
      <div class="container">
        <div class="photo-detail-loading__skeleton">
          <div class="photo-detail-loading__skeleton-image"></div>
          <div class="photo-detail-loading__skeleton-info">
            <div class="photo-detail-loading__skeleton-line"></div>
            <div class="photo-detail-loading__skeleton-line photo-detail-loading__skeleton-line--short"></div>
            <div class="photo-detail-loading__skeleton-line"></div>
          </div>
        </div>
      </div>
    </div>

    <template v-else-if="photo">
      <!-- Breadcrumbs -->
      <section class="photo-detail-breadcrumbs">
        <div class="container">
          <nav :aria-label="$t('common.back')">
            <ol class="breadcrumbs">
              <li class="breadcrumbs__item">
                <router-link to="/">{{ $t('home.title') }}</router-link>
              </li>
              <li class="breadcrumbs__item">
                <router-link to="/catalog">{{ $t('nav.catalog') }}</router-link>
              </li>
              <li class="breadcrumbs__item">
                <RouterLink :to="`/catalog/photos?category=${photo.category_slug || photo.category}`">
                  {{ photo.category }}
                </RouterLink>
              </li>
              <li class="breadcrumbs__item breadcrumbs__item--current" aria-current="page">
                {{ photo.title }}
              </li>
            </ol>
          </nav>
        </div>
      </section>

      <!-- Hero секция с изображением -->
      <section class="photo-detail-hero">
        <div class="container photo-detail-hero__container">
          <div class="photo-detail-hero__image">
            <div class="photo-detail-hero__image-wrapper">
              <img
                :src="photo.imageUrl"
                :alt="photo.title"
                @click="toggleZoom"
                class="photo-detail-hero__img"
              />
              <button
                class="photo-detail-hero__zoom-btn"
                @click="toggleZoom"
                :aria-label="$t('common.search')"
              >
                <Maximize2 :size="20" />
              </button>
            </div>
          </div>

          <div class="photo-detail-hero__info">
            <div class="photo-detail-hero__meta">
              <span class="photo-detail-hero__category">{{ photo.category }}</span>
              <time v-if="photo.uploadedAt" class="photo-detail-hero__date">
                {{ formatDate(photo.uploadedAt) }}
              </time>
            </div>

            <h1 class="photo-detail-hero__title">{{ photo.title }}</h1>

            <div v-if="photo.description" class="photo-detail-hero__description">
              <p>{{ photo.description }}</p>
            </div>

            <!-- Автор -->
            <RouterLink :to="`/author/@${photo.author.username}`" class="photo-detail-hero__author">
              <AuthorAvatar 
                :src="photo.author.avatarUrl" 
                :name="photo.author.name" 
                size="md" 
              />
            <div class="photo-detail-hero__author-info">
              <span class="photo-detail-hero__author-label">{{ $t('photo.author') }}</span>
              <strong class="photo-detail-hero__author-name">{{ photo.author.name }}</strong>
            </div>
              <ArrowRight class="ml-auto text-muted opacity-50" :size="18" />
            </RouterLink>

            <!-- Теги -->
            <div v-if="photo.tags && photo.tags.length > 0" class="photo-detail-hero__tags">
              <span v-for="tag in photo.tags" :key="tag" class="tag">#{{ tag }}</span>
            </div>

            <!-- Статистика -->
            <div v-if="photo.views || photo.downloads" class="photo-detail-hero__stats">
              <div v-if="photo.views" class="photo-detail-hero__stat">
                <span class="photo-detail-hero__stat-label">{{ $t('photo.views') }}:</span>
                <span class="photo-detail-hero__stat-value">{{ photo.views }}</span>
              </div>
              <div v-if="photo.downloads" class="photo-detail-hero__stat">
                <span class="photo-detail-hero__stat-label">{{ $t('photo.downloads') }}:</span>
                <span class="photo-detail-hero__stat-value">{{ photo.downloads }}</span>
              </div>
            </div>

            <!-- Размеры -->
            <div v-if="photo.dimensions" class="photo-detail-hero__dimensions">
              <span class="photo-detail-hero__dimensions-label">{{ $t('photo.dimensions') }}:</span>
              <span class="photo-detail-hero__dimensions-value">
                {{ photo.dimensions.width }} × {{ photo.dimensions.height }} px
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Лицензии и покупка -->
      <section class="photo-detail-licenses">
        <div class="container photo-detail-licenses__container">
          <div class="photo-detail-licenses__content">
            <LicenseSelector
              v-model="selectedLicenseId"
              :licenses="photo.licenseTypes"
            />

            <div class="photo-detail-licenses__actions">
              <button class="btn btn--primary photo-detail-licenses__buy" @click="handleBuy" :disabled="!selectedLicenseId">
                {{ $t('photo.buy') }} ₽{{ totalPrice.toLocaleString() }}
              </button>
              <button
                class="btn btn--outline photo-detail-licenses__cart"
                :class="{ 'btn--active': isFavorite }"
                @click="toggleFavorite"
              >
                <span v-if="isFavorite" class="mr-1">♥</span>
                {{ isFavorite ? $t('common.reset') : $t('common.save') }}
              </button>
            </div>

            <div class="photo-detail-licenses__nav" v-if="nextSimilarPhoto">
              <RouterLink :to="`/photo/${nextSimilarPhoto.id}`" class="nav-link">
                {{ $t('common.actions') }} → {{ nextSimilarPhoto.title }}
              </RouterLink>
              <RouterLink :to="`/catalog/photos?category=${photo.category_slug}`" class="nav-link nav-link--muted">
                {{ $t('common.back') }} «{{ photo.category }}»
              </RouterLink>
            </div>
          </div>
        </div>
      </section>

      <!-- Похожие фото -->
      <SimilarPhotos v-if="similarPhotos.length > 0" :photos="similarPhotos" />
    </template>
  </main>

    <Teleport to="body">
      <transition name="fade">
        <div
          v-if="imageZoomed && photo"
          class="photo-zoom-modal"
          @click="toggleZoom"
        >
          <div class="photo-zoom-modal__content">
            <img
              :src="photo.imageUrl"
              :alt="photo.title"
              class="photo-zoom-modal__img"
            />
            <button
              class="photo-zoom-modal__close"
              @click.stop="toggleZoom"
              :aria-label="$t('common.cancel')"
            >
              <Maximize2 :size="24" />
            </button>
          </div>
        </div>
      </transition>
    </Teleport>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  flex: 1;
}

/* Loading skeleton */
.photo-detail-loading {
  padding-top: calc(var(--header-height) + 3rem);
  padding-bottom: 4rem;
}

.photo-detail-loading__skeleton {
  display: grid;
  gap: 3rem;
  grid-template-columns: 1fr 1fr;
}

.photo-detail-loading__skeleton-image {
  aspect-ratio: 4 / 3;
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.05) 0%,
    rgba(15, 23, 42, 0.1) 50%,
    rgba(15, 23, 42, 0.05) 100%
  );
  background-size: 200% 100%;
  border-radius: 24px;
  animation: shimmer 1.5s infinite;
}

.photo-detail-loading__skeleton-info {
  display: grid;
  gap: 1rem;
  padding: 1rem;
}

.photo-detail-loading__skeleton-line {
  height: 24px;
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0.05) 0%,
    rgba(15, 23, 42, 0.1) 50%,
    rgba(15, 23, 42, 0.05) 100%
  );
  background-size: 200% 100%;
  border-radius: 4px;
  animation: shimmer 1.5s infinite;
}

.photo-detail-loading__skeleton-line--short {
  width: 60%;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* Breadcrumbs */
.photo-detail-breadcrumbs {
  padding-top: calc(var(--header-height) + 1.5rem);
  padding-bottom: 1rem;
  background: radial-gradient(circle at top right, #ecfdf5 0%, #ffffff 55%);
}

.breadcrumbs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
  font-size: 0.9rem;
}

.breadcrumbs__item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.breadcrumbs__item:not(:last-child)::after {
  content: '→';
  color: var(--color-text-muted);
  margin-left: 0.5rem;
}

.breadcrumbs__item a {
  color: var(--color-text-muted);
  transition: color 0.2s ease;
}

.breadcrumbs__item a:hover {
  color: var(--color-accent);
}

.breadcrumbs__item--current {
  color: var(--color-text);
  font-weight: 600;
}

/* Hero section */
.photo-detail-hero {
  padding: 3rem 0 4rem;
}

.photo-detail-hero__container {
  display: grid;
  gap: 3rem;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  align-items: start;
}

.photo-detail-hero__image {
  position: sticky;
  top: calc(var(--header-height) + 2rem);
}

.photo-detail-hero__image-wrapper {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.12);
  background: rgba(15, 23, 42, 0.05);
  cursor: zoom-in;
  transition: transform 0.3s ease;
  max-height: 80vh;
}

.photo-detail-hero__img {
  width: 100%;
  height: auto;
  max-height: 80vh;
  object-fit: contain;
  display: block;
  transition: transform 0.3s ease;
}

.photo-detail-hero__zoom-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease, background 0.2s ease;
}

.photo-detail-hero__zoom-btn:hover {
  transform: scale(1.1);
  background: #ffffff;
}

.photo-detail-hero__info {
  display: grid;
  gap: 1.5rem;
}

.photo-detail-hero__meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.photo-detail-hero__category {
  padding: 0.4rem 1rem;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.12);
  color: var(--color-accent);
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.photo-detail-hero__date {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.photo-detail-hero__title {
  margin: 0;
  font-family: 'Playfair Display', 'Inter', serif;
  font-size: clamp(2rem, 3vw, 2.75rem);
  line-height: 1.2;
}

.photo-detail-hero__description {
  color: var(--color-text-muted);
  line-height: 1.7;
}

.photo-detail-hero__description p {
  margin: 0;
}

.photo-detail-hero__author {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.6), rgba(236, 253, 245, 0.3));
  border: 1px solid rgba(16, 185, 129, 0.15);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  text-decoration: none;
}

.photo-detail-hero__author:hover {
  transform: translateY(-4px);
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.8), rgba(236, 253, 245, 0.5));
  border-color: var(--color-accent);
  box-shadow: 0 12px 24px rgba(16, 185, 129, 0.12);
}

.photo-detail-hero__author-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(16, 185, 129, 0.2);
}

.photo-detail-hero__author-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-detail-hero__author-info {
  display: grid;
  gap: 0.2rem;
}

.photo-detail-hero__author-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.photo-detail-hero__author-name {
  font-size: 1rem;
  color: var(--color-text);
}

.photo-detail-hero__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.photo-detail-hero__stats {
  display: flex;
  gap: 2rem;
  padding: 1rem 0;
  border-top: 1px solid rgba(15, 23, 42, 0.08);
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.photo-detail-hero__stat {
  display: grid;
  gap: 0.25rem;
}

.photo-detail-hero__stat-label {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.photo-detail-hero__stat-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
}

.photo-detail-hero__dimensions {
  display: flex;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.photo-detail-hero__dimensions-value {
  font-weight: 600;
  color: var(--color-text);
}

/* Licenses section */
.photo-detail-licenses {
  padding: 4rem 0;
  background: radial-gradient(circle at top left, #f5fdf9, #ffffff 55%);
}

.photo-detail-licenses__container {
  max-width: 800px;
}

.photo-detail-licenses__content {
  display: grid;
  gap: 2rem;
}

.photo-detail-licenses__actions {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr auto;
}

.photo-detail-licenses__nav {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.nav-link {
  color: var(--color-accent);
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.nav-link:hover {
  text-decoration: underline;
}

.nav-link--muted {
  color: var(--color-text-muted);
  font-weight: 500;
}

.photo-detail-licenses__buy {
  min-width: 200px;
}

.photo-detail-licenses__cart {
  white-space: nowrap;
}

@media (max-width: 1023px) {
  .photo-detail-hero__container {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }

  .photo-detail-hero__image {
    position: static;
  }

  .photo-detail-licenses__actions {
    grid-template-columns: 1fr;
  }

  .photo-detail-licenses__buy,
  .photo-detail-licenses__cart {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .photo-detail-hero {
    padding: 2rem 0 3rem;
  }

  .photo-detail-breadcrumbs {
    padding-top: calc(var(--header-height) + 1rem);
  }

  .photo-detail-licenses {
    padding: 3rem 0;
  }

  .photo-detail-hero__stats {
    flex-direction: column;
    gap: 1rem;
  }
}

/* Модальное окно для zoom */
.photo-zoom-modal {
  position: fixed;
  inset: 0;
  z-index: 100000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.98);
  backdrop-filter: blur(20px);
  cursor: zoom-out;
}

.photo-zoom-modal__content {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.photo-zoom-modal__img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  box-shadow: 0 40px 100px rgba(0, 0, 0, 0.8);
  border-radius: 12px;
}

.photo-zoom-modal__close {
  position: absolute;
  top: 2rem;
  right: 2rem;
  background: #ffffff;
  color: #0f172a;
  border: none;
  border-radius: 50%;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.photo-zoom-modal__close:hover {
  transform: scale(1.1) rotate(90deg);
  background: var(--color-accent);
  color: #ffffff;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active .photo-zoom-modal__img {
  animation: zoomIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes zoomIn {
  from {
    transform: scale(0.85);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .photo-zoom-modal {
    padding: 1rem;
  }

  .photo-zoom-modal__close {
    top: 1rem;
    right: 1rem;
    width: 40px;
    height: 40px;
  }
}
</style>

