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
    <section class="module-grid-vocabulary">
      <article class="surface">
        <h4 class="subsection-title">关键词卡</h4>
        <div class="stack-list">
          <div v-for="word in module.payload.vocab_list" :key="word.term" class="stack-row">
            <div>
              <div class="stack-title">{{ word.term }}</div>
              <div class="stack-meta">{{ word.cefr }}</div>
            </div>
            <div class="stack-score">{{ word.mastery }}</div>
          </div>
        </div>
      </article>

      <article class="surface surface-success">
        <div class="pill pill-neutral">Focus term</div>
        <h4 class="feature-term">{{ module.payload.focus_term.term }}</h4>
        <p class="body-copy">{{ module.payload.focus_term.meaning }}</p>
        <p class="body-copy muted">{{ module.payload.focus_term.phonetic_hint }}</p>
        <p class="body-copy"><strong>适用场景：</strong>{{ module.payload.focus_term.scene }}</p>
        <ul class="bullet-list">
          <li v-for="example in module.payload.focus_term.examples" :key="example">
            {{ example }}
          </li>
        </ul>
      </article>
    </section>

    <section class="module-grid-2">
      <article class="surface">
        <h4 class="subsection-title">为什么是这些词</h4>
        <ul class="bullet-list">
          <li v-for="item in module.payload.why_these_words" :key="item">{{ item }}</li>
        </ul>
      </article>
      <article class="surface">
        <h4 class="subsection-title">掌握状态</h4>
        <div class="bar-stack">
          <div v-for="bar in module.payload.mastery_bars" :key="bar.label" class="bar-row">
            <span>{{ bar.label }}</span>
            <strong>{{ bar.value }}</strong>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>
