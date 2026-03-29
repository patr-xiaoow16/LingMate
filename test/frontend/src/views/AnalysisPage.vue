<template>
  <div class="view-stack" v-if="data">
    <section class="page-intro">
      <div>
        <p class="eyebrow">{{ data.summary.eyebrow }}</p>
        <h1 class="page-title">{{ data.summary.title }}</h1>
        <p class="page-description">{{ data.summary.description }}</p>
      </div>
      <div class="chip-row">
        <span v-for="pill in data.summary.pills" :key="pill" class="chip">{{ pill }}</span>
      </div>
    </section>

    <section class="analysis-grid">
      <article class="surface-card pipeline-card">
        <h2 class="section-title pipeline-title">{{ data.pipeline.title }}</h2>
        <p class="metric-note">{{ data.pipeline.description }}</p>
        <div class="pipeline-runtime">
          <span class="chip chip-soft">当前步骤：{{ data.pipeline.activeStepTitle || "启动中" }}</span>
          <span class="subtle-label">{{ data.mockMeta?.provider || "mock" }} · {{ data.mockMeta?.elapsedSeconds ?? 0 }}s / {{ data.mockMeta?.totalDurationSeconds ?? 0 }}s</span>
        </div>
        <div v-if="data.status === 'failed'" class="banner banner-warning">
          {{ data.summary.description }}
        </div>
        <div v-if="data.status === 'failed' && data.recoveryAction" class="button-row">
          <button class="btn btn-secondary" @click="handleRecoveryAction">
            {{ data.recoveryAction.label }}
          </button>
        </div>
        <div class="split-row">
          <span class="subtle-label">生成进度</span>
          <span class="progress-value">{{ data.pipeline.progress }}%</span>
        </div>
        <div class="progress-track">
          <span :style="{ width: `${data.pipeline.progress}%` }"></span>
        </div>
        <div class="pipeline-steps">
          <div
            v-for="step in data.pipeline.steps"
            :key="step.index"
            class="pipeline-step"
            :class="`step-${step.status}`"
          >
            <div class="counter">{{ step.status === 'done' ? 'OK' : step.index }}</div>
            <div class="pipeline-step-content">
              <p class="step-title">{{ step.title }}</p>
              <p class="step-note">{{ step.note }}</p>
              <div v-if="step.status === 'active'" class="mini-progress-track">
                <span :style="{ width: `${step.stepProgress}%` }"></span>
              </div>
            </div>
          </div>
        </div>
      </article>

      <article class="surface-card lesson-card">
        <div class="split-row align-start">
          <div>
            <h2 class="section-title">{{ data.lesson.title }}</h2>
            <p class="metric-note">{{ data.lesson.meta }}</p>
          </div>
          <span class="chip" :class="data.analysisReady ? 'chip-success' : 'chip-soft'">{{ data.lesson.badge }}</span>
        </div>

        <div class="soft-panel">
          <p class="eyebrow">Transcript preview</p>
          <p class="lesson-transcript">{{ data.lesson.transcript }}</p>
          <div class="chip-row">
            <span v-for="chip in data.lesson.chips" :key="chip" class="chip chip-soft">
              {{ chip }}
            </span>
          </div>
          <p class="subtle-label analysis-source">
            来源链接：{{ data.mockMeta?.source?.url || "https://podcasts.apple.com/example" }}
          </p>
        </div>

        <div class="module-plan">
          <h3 class="subsection-title">八步学习方案</h3>
          <div
            v-for="module in data.modulePlan"
            :key="module.label"
            class="module-plan-row"
            :class="`tone-${module.tone}`"
          >
            <strong>{{ module.label }}</strong>
            <span>{{ module.desc }}</span>
          </div>
        </div>

        <button class="btn btn-primary analysis-start-btn" :class="{ ready: data.analysisReady }" :disabled="!data.analysisReady" @click="startLesson">
          {{ data.analysisReady ? "开始本课" : data.status === "failed" ? "分析失败" : "AI 正在处理中..." }}
        </button>
      </article>
    </section>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";

import { api } from "../lib/api";

const props = defineProps({
  lessonId: {
    type: String,
    required: true,
  },
});

const data = ref(null);
const router = useRouter();
let pollTimer = null;

onMounted(async () => {
  await fetchAnalysis();
  startPolling();
});

async function startLesson() {
  if (!data.value?.analysisReady) return;
  const result = await api.startLesson(props.lessonId);
  router.push({
    name: "workspace",
    params: { lessonId: props.lessonId },
    query: { module: "1", entry: "analysis", status: result.status || "started" },
  });
}

onUnmounted(() => {
  if (pollTimer) {
    window.clearInterval(pollTimer);
  }
});

async function fetchAnalysis() {
  data.value = await api.getAnalysis(props.lessonId);
  if ((data.value?.analysisReady || data.value?.status === "failed") && pollTimer) {
    window.clearInterval(pollTimer);
    pollTimer = null;
  }
}

function handleRecoveryAction() {
  const action = data.value?.recoveryAction;
  if (!action || action.type !== "open_url" || !action.url || typeof window === "undefined") return;
  window.open(action.url, "lingmate-youtube-login", "popup=yes,width=960,height=760");
}

function startPolling() {
  if (pollTimer) {
    window.clearInterval(pollTimer);
  }
  pollTimer = window.setInterval(fetchAnalysis, 1000);
}
</script>
