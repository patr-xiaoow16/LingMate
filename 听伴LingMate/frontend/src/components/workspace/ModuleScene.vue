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
      <div class="pill-row">
        <span v-for="filter in module.payload.filters" :key="filter" class="pill pill-neutral">
          {{ filter }}
        </span>
      </div>
      <div class="template-list">
        <article v-for="template in module.payload.templates" :key="template.title" class="template-card">
          <div class="template-head">
            <h4 class="subsection-title">{{ template.title }}</h4>
            <span class="pill pill-success">{{ template.channel }}</span>
          </div>
          <p class="body-copy muted">{{ template.tone }}</p>
          <p class="body-copy">{{ template.script }}</p>
        </article>
      </div>
    </section>

    <section class="surface">
      <h4 class="subsection-title">迁移逻辑</h4>
      <div class="transition-map">
        <div v-for="step in module.payload.transition_map" :key="step.from" class="transition-row">
          <div>
            <div class="mini-label">{{ step.from }}</div>
            <div class="mini-value">{{ step.to }}</div>
          </div>
          <p class="body-copy muted">{{ step.hint }}</p>
        </div>
      </div>
    </section>
  </div>
</template>
