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
    <section class="module-grid-2">
      <article v-for="pattern in module.payload.patterns" :key="pattern.skeleton" class="surface surface-success">
        <div class="pill pill-neutral">Pattern</div>
        <h4 class="decoder-line">{{ pattern.skeleton }}</h4>
        <div class="pill-row">
          <span v-for="swap in pattern.swaps" :key="swap" class="pill pill-warning">
            {{ swap }}
          </span>
        </div>
      </article>
    </section>

    <section class="module-grid-2">
      <article class="surface">
        <h4 class="subsection-title">换词练习</h4>
        <ul class="bullet-list">
          <li v-for="item in module.payload.practice_attempts" :key="item">{{ item }}</li>
        </ul>
      </article>
      <article class="surface">
        <h4 class="subsection-title">AI 提醒</h4>
        <p class="body-copy">{{ module.payload.revision_tip }}</p>
      </article>
    </section>
  </div>
</template>
