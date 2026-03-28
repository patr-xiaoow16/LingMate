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
      <h4 class="subsection-title">输出任务</h4>
      <div class="stack-list">
        <div v-for="task in module.payload.tasks" :key="task.prompt" class="task-row">
          <div>
            <div class="stack-title">{{ task.type }}</div>
            <div class="body-copy muted">{{ task.prompt }}</div>
          </div>
          <span class="pill" :class="task.status === 'active' ? 'pill-success' : 'pill-neutral'">
            {{ task.status }}
          </span>
        </div>
      </div>
    </section>

    <section class="module-grid-2">
      <article class="surface surface-info">
        <h4 class="subsection-title">你的作答草稿</h4>
        <p class="body-copy">{{ module.payload.draft }}</p>
      </article>
      <article class="surface">
        <h4 class="subsection-title">评分维度</h4>
        <div class="score-list">
          <div v-for="score in module.payload.scores" :key="score.label" class="score-row">
            <span>{{ score.label }}</span>
            <strong>{{ score.value }}</strong>
          </div>
        </div>
      </article>
    </section>

    <section class="surface">
      <h4 class="subsection-title">AI 点评</h4>
      <ul class="bullet-list">
        <li v-for="item in module.payload.feedback" :key="item">{{ item }}</li>
      </ul>
    </section>
  </div>
</template>
