<template>
  <div class="view-stack" v-if="data">
    <section class="hero-layout">
      <div class="hero-copy cardless">
        <p class="eyebrow">{{ data.hero.eyebrow }}</p>
        <h1 class="hero-title">{{ data.hero.title }}</h1>
        <p class="hero-description">{{ data.hero.description }}</p>
      </div>

      <aside class="surface-card import-card">
        <p class="eyebrow">Start with any material</p>
        <h2 class="section-title import-card-title">{{ data.importCard.title }}</h2>
        <div class="chip-row import-tabs">
          <span class="chip chip-primary">链接粘贴</span>
        </div>
        <div class="soft-panel import-panel">
          <p class="subtle-label">{{ data.importCard.platforms }}</p>
          <div class="input-shell">
            <span class="input-icon">↗</span>
            <input
              v-model="link"
              type="text"
              :placeholder="data.importCard.placeholder"
            />
          </div>
          <div class="split-row import-meta-row">
            <span class="chip chip-success">{{ data.importCard.eta }}</span>
            <span class="subtle-label">{{ data.importCard.engine }}</span>
          </div>
        </div>
        <button class="btn btn-primary btn-block" @click="handleImport">
          {{ data.importCard.button }}
        </button>
      </aside>
    </section>

    <section class="metric-grid">
      <article v-for="metric in data.metrics" :key="metric.title" class="surface-card metric-card">
        <p class="metric-title">{{ metric.title }}</p>
        <p class="metric-value">{{ metric.value }}</p>
        <p class="metric-note">{{ metric.note }}</p>
      </article>
    </section>

    <section class="section-header">
      <div>
        <h2 class="section-title">从真实场景开始，而不是从题目开始</h2>
      </div>
      <p class="subtle-label">Most chosen this week</p>
    </section>

    <section class="scenario-grid">
      <article v-for="scenario in data.scenarios" :key="scenario.title" class="surface-card scenario-card">
        <p class="eyebrow">{{ scenario.subtitle }}</p>
        <h3>{{ scenario.title }}</h3>
        <p class="scenario-meta">{{ scenario.meta }}</p>
        <div class="quote-card">{{ scenario.expression }}</div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { api } from "../lib/api";

const router = useRouter();
const data = ref(null);
const link = ref("https://podcasts.apple.com/example");
const STORAGE_KEY = "lingmate-active-lesson-id";

onMounted(async () => {
  data.value = await api.getHome();
});

async function handleImport() {
  if (!/^https?:\/\//.test(link.value.trim())) {
    return;
  }

  const result = await api.importMaterial({
    mode: "mock_url_import",
    source: {
      type: "url",
      url: link.value.trim(),
    },
  });
  if (!result.lessonId) return;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, result.lessonId);
  }
  router.push({ name: "analysis", params: { lessonId: result.lessonId } });
}
</script>
