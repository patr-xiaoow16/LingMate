<template>
  <div class="page-shell">
    <header class="app-header">
      <div class="brand-lockup">
        <span class="brand-dot"></span>
        <div>
          <p class="brand-name">lingmate</p>
          <p class="brand-subtitle">Immersive listening workspace</p>
        </div>
      </div>
      <nav class="top-nav">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink :to="analysisPath">AI 分析</RouterLink>
        <RouterLink :to="workspacePath">工作台</RouterLink>
        <RouterLink :to="reviewPath">学习报告</RouterLink>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed, watch } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const FALLBACK_LESSON_ID = "demo-lesson";
const STORAGE_KEY = "lingmate-active-lesson-id";

const routeLessonId = computed(() => {
  const raw = route.params.lessonId;
  return typeof raw === "string" && raw.trim() ? raw.trim() : "";
});

const storedLessonId = computed(() => {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(STORAGE_KEY) || "";
});

const activeLessonId = computed(() => routeLessonId.value || storedLessonId.value || FALLBACK_LESSON_ID);

watch(
  routeLessonId,
  (lessonId) => {
    if (!lessonId || typeof window === "undefined") return;
    window.localStorage.setItem(STORAGE_KEY, lessonId);
  },
  { immediate: true },
);

const analysisPath = computed(() => `/analysis/${activeLessonId.value}`);
const workspacePath = computed(() => `/workspace/${activeLessonId.value}`);
const reviewPath = computed(() => `/review/${activeLessonId.value}`);
</script>
