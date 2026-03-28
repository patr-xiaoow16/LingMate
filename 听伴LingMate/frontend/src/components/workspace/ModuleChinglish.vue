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
      <h4 class="subsection-title">中式表达 vs 地道表达</h4>
      <div class="comparison-list">
        <div v-for="pair in module.payload.pairs" :key="pair.chinglish" class="comparison-row">
          <div class="comparison-bad">
            <p class="mini-label">✖ 中式英文</p>
            <p class="body-copy">{{ pair.chinglish }}</p>
          </div>
          <div class="comparison-good">
            <p class="mini-label">✔ 地道表达</p>
            <p class="body-copy">{{ pair.native }}</p>
          </div>
          <div class="comparison-note">
            <p class="body-copy muted">{{ pair.explanation }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="surface surface-info">
      <h4 class="subsection-title">自我表达体检示例</h4>
      <p class="body-copy"><strong>原句：</strong>{{ module.payload.rewrite_example.original }}</p>
      <p class="body-copy"><strong>改写：</strong>{{ module.payload.rewrite_example.revised }}</p>
      <p class="body-copy muted">{{ module.payload.rewrite_example.note }}</p>
    </section>
  </div>
</template>
