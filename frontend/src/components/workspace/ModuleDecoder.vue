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
    <section class="surface surface-info">
      <div class="module-player-head">
        <div>
          <div class="pill pill-neutral">{{ module.payload.loop_mode }}</div>
          <p class="body-copy muted">逐句听清楚“真正听起来像什么”。</p>
        </div>
        <div class="metric-chip">{{ module.payload.accuracy }}%</div>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: `${module.payload.audio_progress}%` }"></div>
      </div>
      <div class="decoder-card">
        <p class="mini-label">原句 transcript</p>
        <p class="decoder-line">{{ module.payload.original }}</p>
        <p class="mini-label">实际听感</p>
        <p class="decoder-line decoder-alt">{{ module.payload.heard_like }}</p>
      </div>
      <div class="pill-row">
        <span v-for="tag in module.payload.tags" :key="tag" class="pill pill-warning">
          {{ tag }}
        </span>
      </div>
    </section>

    <section class="module-grid-2">
      <article class="surface">
        <h4 class="subsection-title">为什么会听不出来</h4>
        <ul class="bullet-list">
          <li v-for="item in module.payload.explanations" :key="item">{{ item }}</li>
        </ul>
      </article>
      <article class="surface">
        <h4 class="subsection-title">循环练习建议</h4>
        <ul class="bullet-list">
          <li v-for="item in module.payload.repeat_queue" :key="item">{{ item }}</li>
        </ul>
      </article>
    </section>
  </div>
</template>
