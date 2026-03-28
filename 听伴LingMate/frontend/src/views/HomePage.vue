<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import PanelCard from "../components/shared/PanelCard.vue";
import { api } from "../lib/api";

const router = useRouter();
const loading = ref(true);
const submitting = ref(false);
const error = ref("");
const home = ref(null);

const form = reactive({
  source_type: "link",
  source_value: "",
  goal: "听懂真实口语里的缓冲表达",
});

const placeholder = computed(() => {
  if (!home.value) return "";
  return home.value.composer.placeholders[form.source_type] || "";
});

async function loadHome() {
  loading.value = true;
  error.value = "";
  try {
    home.value = await api.getHome();
  } catch (err) {
    error.value = err.message || "加载首页失败";
  } finally {
    loading.value = false;
  }
}

async function submitImport() {
  submitting.value = true;
  error.value = "";
  try {
    const response = await api.importLesson({ ...form });
    router.push(`/analysis/${response.lesson_id}`);
  } catch (err) {
    error.value = err.message || "导入失败";
  } finally {
    submitting.value = false;
  }
}

onMounted(loadHome);
</script>

<template>
  <section class="page-stack page-screen home-screen">
    <div v-if="loading" class="loading-state">正在准备 LingMate 首页…</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <template v-else>
      <section class="hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">{{ home.hero.eyebrow }}</p>
          <h1 class="display-title">{{ home.hero.title }}</h1>
          <p class="body-copy hero-description">{{ home.hero.description }}</p>
          <div class="pill-row">
            <span v-for="item in home.hero.highlights" :key="item" class="pill pill-neutral">
              {{ item }}
            </span>
          </div>
          <div class="action-row">
            <RouterLink :to="home.hero.primary_action.route" class="btn btn-primary">
              {{ home.hero.primary_action.label }}
            </RouterLink>
            <RouterLink :to="home.hero.secondary_action.route" class="btn btn-secondary">
              {{ home.hero.secondary_action.label }}
            </RouterLink>
          </div>
        </div>

        <PanelCard
          eyebrow="Start here"
          title="把任意英文内容，变成一堂陪你走完的精听课"
          tone="neutral"
        >
          <form class="composer-form" @submit.prevent="submitImport">
            <label class="field-label">
              导入方式
              <select v-model="form.source_type" class="text-input">
                <option
                  v-for="item in home.composer.source_types"
                  :key="item.value"
                  :value="item.value"
                >
                  {{ item.label }}
                </option>
              </select>
            </label>

            <label class="field-label">
              内容
              <input
                v-model="form.source_value"
                class="text-input"
                :placeholder="placeholder"
              />
            </label>

            <label class="field-label">
              你的目标
              <select v-model="form.goal" class="text-input">
                <option v-for="goal in home.composer.goals" :key="goal" :value="goal">
                  {{ goal }}
                </option>
              </select>
            </label>

            <button class="btn btn-primary full-width" :disabled="submitting">
              {{ submitting ? "正在生成…" : "生成精听课" }}
            </button>
          </form>

          <div class="recent-source-list">
            <p class="mini-label">最近材料</p>
            <div v-for="item in home.composer.recent_sources" :key="item.title" class="recent-source-row">
              <span>{{ item.title }}</span>
              <span class="muted">{{ item.meta }}</span>
            </div>
          </div>
        </PanelCard>
      </section>

      <section class="stats-grid">
        <article v-for="stat in home.stats" :key="stat.label" class="surface stat-card">
          <p class="mini-label">{{ stat.label }}</p>
          <p class="stat-value">{{ stat.value }}</p>
          <p class="body-copy muted">{{ stat.note }}</p>
        </article>
      </section>

      <section class="cards-grid cards-grid-3">
        <article v-for="item in home.weekly_picks" :key="item.title" class="surface pick-card">
          <p class="eyebrow">{{ item.tag }}</p>
          <h3 class="panel-title">{{ item.title }}</h3>
          <p class="body-copy muted">{{ item.summary }}</p>
          <RouterLink class="inline-link" :to="item.route">打开这节课</RouterLink>
        </article>
      </section>

      <PanelCard eyebrow="Recent lessons" title="最近生成的精听课">
        <div class="cards-grid cards-grid-auto">
          <article
            v-for="lesson in home.recent_lessons"
            :key="lesson.id"
            class="lesson-summary-card"
          >
            <div>
              <h4 class="subsection-title">{{ lesson.title }}</h4>
              <p class="body-copy muted">{{ lesson.subtitle }}</p>
            </div>
            <div class="lesson-summary-actions">
              <span class="pill pill-neutral">{{ lesson.modules_done }}/8 modules</span>
              <RouterLink class="inline-link" :to="`/analysis/${lesson.id}`">进入分析</RouterLink>
            </div>
          </article>
        </div>
      </PanelCard>
    </template>
  </section>
</template>
