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
          <div class="pill pill-neutral">{{ module.payload.listen_round }}</div>
          <p class="body-copy muted">{{ module.payload.focus_prompt }}</p>
        </div>
        <div class="metric-chip">{{ module.payload.audio_progress }}%</div>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: `${module.payload.audio_progress}%` }"></div>
      </div>
      <div class="module-grid-3">
        <div v-for="tile in module.payload.gist_tiles" :key="tile.label" class="mini-card">
          <p class="mini-label">{{ tile.label }}</p>
          <p class="mini-value">{{ tile.value }}</p>
        </div>
      </div>
    </section>

    <section class="module-grid-2">
      <article v-for="card in module.payload.question_cards" :key="card.question" class="surface">
        <h4 class="subsection-title">{{ card.question }}</h4>
        <ul class="choice-list">
          <li v-for="choice in card.choices" :key="choice">{{ choice }}</li>
        </ul>
      </article>
    </section>

    <section class="surface">
      <h4 class="subsection-title">你刚刚捕捉到的关键词</h4>
      <div class="pill-row">
        <span v-for="chip in module.payload.reflection_chips" :key="chip" class="pill pill-success">
          {{ chip }}
        </span>
      </div>
    </section>
  </div>
</template>
