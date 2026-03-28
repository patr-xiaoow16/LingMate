<script setup>
import { computed } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";

const route = useRoute();

const activeLessonId = computed(() => route.params.lessonId || "lesson-soft-language");
const routeShellClass = computed(() => `page-shell--${route.name || "home"}`);

const navLinks = computed(() => [
  { label: "入门页", to: "/" },
  { label: "分析", to: `/analysis/${activeLessonId.value}` },
  { label: "学习台", to: `/workspace/${activeLessonId.value}/immersive-listening` },
  { label: "复习报告", to: `/review/${activeLessonId.value}` },
]);
</script>

<template>
  <div class="app-backdrop">
    <div class="ambient ambient-a"></div>
    <div class="ambient ambient-b"></div>
    <div class="app-frame">
      <header class="topbar">
        <RouterLink class="brand" to="/">
          <div class="brand-mark"></div>
          <div>
            <div class="brand-title">lingmate</div>
            <div class="brand-subtitle">AI co-pilot for immersive listening</div>
          </div>
        </RouterLink>

        <nav class="nav-links">
          <RouterLink
            v-for="link in navLinks"
            :key="link.label"
            :to="link.to"
            class="nav-link"
          >
            {{ link.label }}
          </RouterLink>
        </nav>

        <RouterLink
          class="btn btn-primary topbar-cta"
          :to="`/workspace/${activeLessonId}/immersive-listening`"
        >
          开始本课
        </RouterLink>
      </header>

      <main class="page-shell" :class="routeShellClass">
        <RouterView />
      </main>
    </div>
  </div>
</template>
