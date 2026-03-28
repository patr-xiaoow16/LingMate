<script setup>
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import PanelCard from "../components/shared/PanelCard.vue";
import { api } from "../lib/api";

const route = useRoute();

const loading = ref(true);
const error = ref("");
const review = ref(null);
const report = ref(null);

async function loadReview() {
  loading.value = true;
  error.value = "";
  try {
    const reviewData = await api.getReview(route.params.lessonId);
    review.value = reviewData;
    report.value = await api.getReport(route.params.lessonId || reviewData.active_lesson_id);
  } catch (err) {
    error.value = err.message || "加载复习页失败";
  } finally {
    loading.value = false;
  }
}

watch(() => route.params.lessonId, loadReview, { immediate: true });
</script>

<template>
  <section class="page-stack page-screen review-screen">
    <div v-if="loading" class="loading-state">正在生成学习报告…</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <template v-else-if="review && report">
      <header class="page-header">
        <div>
          <p class="eyebrow">This week</p>
          <h1 class="headline">{{ report.hero.title }}</h1>
          <p class="body-copy muted">{{ report.hero.summary }}</p>
        </div>
        <div class="pill-row">
          <span class="pill pill-success">{{ review.summary.today_target }}</span>
          <span class="pill pill-neutral">{{ review.summary.recovered_words }}</span>
        </div>
      </header>

      <section class="stats-grid">
        <article v-for="metric in report.metrics" :key="metric.label" class="surface stat-card">
          <p class="mini-label">{{ metric.label }}</p>
          <p class="stat-value">{{ metric.value }}</p>
          <p class="body-copy muted">{{ metric.note }}</p>
        </article>
      </section>

      <section class="review-grid">
        <PanelCard eyebrow="Weakness radar" title="薄弱点正在往上走">
          <div class="chart-list">
            <div v-for="item in report.weaknesses" :key="item.label" class="chart-row">
              <span>{{ item.label }}</span>
              <div class="chart-track">
                <div class="chart-fill" :style="{ width: `${item.value}%` }"></div>
              </div>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
        </PanelCard>

        <PanelCard eyebrow="Weekly listening hours" title="本周投入">
          <div class="chart-bars">
            <div v-for="item in report.weekly_hours" :key="item.day" class="chart-bar-col">
              <div class="chart-bar" :style="{ height: `${item.value * 42}px` }"></div>
              <span>{{ item.day }}</span>
            </div>
          </div>
        </PanelCard>

        <PanelCard eyebrow="Today review queue" title="今日复习队列" tone="success">
          <div class="queue-list">
            <article v-for="item in review.queue" :key="item.term" class="queue-row">
              <div>
                <h4 class="subsection-title">{{ item.term }}</h4>
                <p class="body-copy muted">{{ item.prompt }}</p>
              </div>
              <span class="pill pill-warning">{{ item.due }}</span>
            </article>
          </div>
        </PanelCard>

        <PanelCard eyebrow="Study journal" title="学习闭环记录">
          <div class="journal-list">
            <article v-for="item in report.journal" :key="item.date + item.title" class="journal-row">
              <div class="journal-date">{{ item.date }}</div>
              <div>
                <h4 class="subsection-title">{{ item.title }}</h4>
                <p class="body-copy muted">{{ item.note }}</p>
              </div>
            </article>
          </div>
        </PanelCard>

        <PanelCard eyebrow="Featured note" :title="report.note_card.headline" tone="info">
          <p class="body-copy">{{ report.note_card.summary }}</p>
          <div class="pill-row">
            <span v-for="chip in report.note_card.chips" :key="chip" class="pill pill-success">
              {{ chip }}
            </span>
          </div>
          <RouterLink class="btn btn-primary full-width" :to="`/workspace/${report.lesson.id}/immersive-listening`">
            继续学习本课
          </RouterLink>
        </PanelCard>
      </section>
    </template>
  </section>
</template>
