<script setup lang="ts">
/**
 * Только для локальных скриншотов: все варианты PhotoCard в один ряд.
 * Маршрут регистрируется в router только при import.meta.env.DEV.
 */
import PhotoCard from '../../components/PhotoCard.vue'
import demoImage from '../../assets/images/alpine-lake.jpg'

const base = {
  id: 'demo-1',
  title: 'Рассвет над озером',
  category: 'Пейзаж',
  imageUrl: demoImage,
  tags: ['утро', 'вода'],
  views: 1200,
  downloads: 48,
  earnings: 3500,
  uploadedAt: '12 мая 2026',
}
</script>

<template>
  <div class="playground">
    <p class="playground__hint">
      Dev: откройте /__dev/photo-card-states и сделайте скриншот области ниже (viewport по ширине или фрагмент).
    </p>
    <div class="playground__row">
      <figure class="playground__col">
        <figcaption>default</figcaption>
        <PhotoCard :photo="{ ...base, status: 'published' }" />
      </figure>
      <figure class="playground__col">
        <figcaption>compact + статус</figcaption>
        <PhotoCard
          :photo="{ ...base, id: '2', status: 'pending' }"
          variant="compact"
          show-status
        />
      </figure>
      <figure class="playground__col">
        <figcaption>favorite on</figcaption>
        <PhotoCard :photo="{ ...base, id: '3' }" show-favorite is-favorite />
      </figure>
      <figure class="playground__col playground__col--overlay">
        <figcaption>actions (оверлей)</figcaption>
        <PhotoCard :photo="{ ...base, id: '4', status: 'draft' }" show-actions show-status />
      </figure>
      <figure class="playground__col">
        <figcaption>stats</figcaption>
        <PhotoCard :photo="{ ...base, id: '5' }" show-stats />
      </figure>
      <figure class="playground__col">
        <figcaption>category</figcaption>
        <PhotoCard :photo="{ ...base, id: '6' }" variant="category" />
      </figure>
      <figure class="playground__col">
        <figcaption>collection</figcaption>
        <PhotoCard :photo="{ ...base, id: '7' }" variant="collection" />
      </figure>
    </div>
  </div>
</template>

<style scoped>
.playground {
  min-height: 100vh;
  padding: 1.5rem;
  background: #f1f5f9;
}

.playground__hint {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: #64748b;
}

.playground__row {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 1rem;
  align-items: flex-start;
  overflow-x: auto;
  padding-bottom: 0.5rem;
}

.playground__col {
  margin: 0;
  flex: 0 0 220px;
  min-width: 200px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.playground__col figcaption {
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  text-align: center;
}

/* Оверлей с кнопками по умолчанию скрыт до hover — для скрина держим видимым */
.playground__col--overlay :deep(.photo-card__overlay) {
  opacity: 1;
}
</style>
