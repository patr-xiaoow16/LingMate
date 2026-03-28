<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import PanelCard from "../components/shared/PanelCard.vue";
import { api } from "../lib/api";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const starting = ref(false);
const error = ref("");
const analysis = ref(null);

async function loadAnalysis() {
  loading.value = true;
  error.value = "";
  try {
    analysis.value = await api.getAnalysis(route.params.lessonId);
  } catch (err) {
    error.value = err.message || "加载分析页失败";
  } finally {
    loading.value = false;
  }
}

async function startLesson() {
  starting.value = true;
  try {
    await api.startLesson(route.params.lessonId);
    router.push(`/workspace/${route.params.lessonId}/immersive-listening`);
  } catch (err) {
    error.value = err.message || "启动学习失败";
  } finally {
    starting.value = false;
  }
}

watch(() => route.params.lessonId, loadAnalysis, { immediate: true });
</script>

<template>
  <section class="page-stack page-screen analysis-screen">
    <div v-if="loading" class="loading-state">正在分析材料…</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <template v-else>
      <header class="page-header">
        <div>
          <p class="eyebrow">Import complete</p>
          <h1 class="headline">{{ analysis.headline }}</h1>
          <p class="body-copy muted">{{ analysis.lesson.goal }}</p>
        </div>
        <button class="btn btn-primary" :disabled="starting" @click="startLesson">
          {{ starting ? "正在进入…" : "开始学习" }}
        </button>
      </header>

      <section class="stats-grid">
        <article v-for="stat in analysis.summary_cards" :key="stat.label" class="surface stat-card">
          <p class="mini-label">{{ stat.label }}</p>
          <p class="stat-value">{{ stat.value }}</p>
          <p class="body-copy muted">{{ stat.note }}</p>
        </article>
      </section>

      <section class="analysis-grid">
        <PanelCard eyebrow="AI pre-processing" title="处理流水线" tone="neutral">
          <div class="stack-list">
            <div v-for="step in analysis.processing_steps" :key="step.label" class="stack-row">
              <span>{{ step.label }}</span>
              <span class="pill pill-success">{{ step.status }}</span>
            </div>
          </div>
        </PanelCard>

        <div class="analysis-main">
          <PanelCard eyebrow="Transcript" :title="analysis.transcript.title" tone="info">
            <p class="body-copy muted">{{ analysis.transcript.subtitle }}</p>
            <p class="transcript-excerpt">{{ analysis.transcript.excerpt }}</p>
            <p class="body-copy">{{ analysis.transcript.context }}</p>
            <div class="pill-row">
              <span v-for="item in analysis.transcript.highlights" :key="item" class="pill pill-warning">
                {{ item }}
              </span>
            </div>
          </PanelCard>

          <PanelCard eyebrow="8-step plan" title="八步学习方案">
            <div class="plan-list">
              <article v-for="item in analysis.plan" :key="item.key" class="plan-row">
                <div class="plan-index">{{ item.step }}</div>
                <div class="plan-copy">
                  <div class="plan-title">{{ item.title }}</div>
                  <div class="body-copy muted">{{ item.summary }}</div>
                </div>
                <span class="pill pill-neutral">{{ item.duration }}</span>
              </article>
            </div>
          </PanelCard>
        </div>

        <div class="analysis-rail">
          <PanelCard eyebrow="Voice signals" title="语音现象">
            <ul class="bullet-list">
              <li v-for="item in analysis.voice_signals" :key="item">{{ item }}</li>
            </ul>
          </PanelCard>
          <PanelCard eyebrow="建议先学" title="推荐策略" tone="success">
            <ul class="bullet-list">
              <li v-for="item in analysis.recommendations" :key="item">{{ item }}</li>
            </ul>
          </PanelCard>
        </div>
      </section>
    </template>
  </section>
</template>
