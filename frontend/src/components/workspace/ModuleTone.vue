<script setup>
defineProps({
  module: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <div class="module-stack">
    <section class="surface">
      <div v-for="item in module.payload.cases" :key="item.quote" class="tone-case">
        <div class="pill pill-neutral">{{ item.label }}</div>
        <p class="decoder-line">{{ item.quote }}</p>
        <p class="body-copy muted">{{ item.meaning }}</p>
      </div>
    </section>

    <section class="module-grid-2">
      <article class="surface">
        <h4 class="subsection-title">语气强弱对比</h4>
        <div v-for="item in module.payload.tone_shift" :key="item.label" class="shift-row">
          <span class="mini-label">{{ item.label }}</span>
          <p class="body-copy">{{ item.text }}</p>
        </div>
      </article>
      <article class="surface">
        <h4 class="subsection-title">关系与态度信号</h4>
        <ul class="bullet-list">
          <li v-for="signal in module.payload.signals" :key="signal">{{ signal }}</li>
        </ul>
      </article>
    </section>
  </div>
</template>
