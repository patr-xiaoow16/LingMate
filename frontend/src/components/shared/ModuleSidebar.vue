<script setup>
import { RouterLink } from "vue-router";

defineProps({
  lessonId: {
    type: String,
    required: true,
  },
  lessonCard: {
    type: Object,
    required: true,
  },
  modules: {
    type: Array,
    required: true,
  },
  activeKey: {
    type: String,
    required: true,
  },
});
</script>

<template>
  <aside class="workspace-sidebar">
    <section class="surface sidebar-lesson-card">
      <p class="eyebrow">Current material</p>
      <h3 class="panel-title">{{ lessonCard.title }}</h3>
      <p class="body-copy muted">{{ lessonCard.subtitle }}</p>
      <div class="pill-row">
        <span v-for="badge in lessonCard.badges" :key="badge" class="pill pill-neutral">
          {{ badge }}
        </span>
      </div>
      <p class="sidebar-objective">{{ lessonCard.objective }}</p>
    </section>

    <section class="surface sidebar-module-list">
      <p class="eyebrow">8-step flow</p>
      <div class="module-nav-list">
        <RouterLink
          v-for="module in modules"
          :key="module.key"
          :to="`/workspace/${lessonId}/${module.key}`"
          class="module-nav-link"
          :class="{
            active: module.key === activeKey,
            done: module.status === 'completed',
          }"
        >
          <div class="module-order">{{ module.step }}</div>
          <div class="module-copy">
            <div class="module-name">{{ module.title }}</div>
            <div class="module-meta">{{ module.duration }}</div>
          </div>
        </RouterLink>
      </div>
    </section>
  </aside>
</template>
