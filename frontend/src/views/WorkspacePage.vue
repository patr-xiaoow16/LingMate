<script setup>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import PanelCard from "../components/shared/PanelCard.vue";
import ModuleSidebar from "../components/shared/ModuleSidebar.vue";
import ModuleRenderer from "../components/workspace/ModuleRenderer.vue";
import { api } from "../lib/api";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const error = ref("");
const workspace = ref(null);
const coachInput = ref("");
const coachResponse = ref(null);
const coaching = ref(false);
const completing = ref(false);

const activeModule = computed(() => workspace.value?.active_module || null);

async function loadWorkspace() {
  loading.value = true;
  error.value = "";
  coachResponse.value = null;
  try {
    workspace.value = await api.getWorkspace(route.params.lessonId, route.params.moduleKey);
    coachInput.value = "";
  } catch (err) {
    error.value = err.message || "加载学习工作台失败";
  } finally {
    loading.value = false;
  }
}

async function submitCoach() {
  if (!activeModule.value) return;
  coaching.value = true;
  try {
    const result = await api.coachModule(
      route.params.lessonId,
      activeModule.value.key,
      coachInput.value
    );
    coachResponse.value = result.response;
  } catch (err) {
    error.value = err.message || "AI 教练反馈失败";
  } finally {
    coaching.value = false;
  }
}

async function completeModule() {
  if (!activeModule.value) return;
  completing.value = true;
  try {
    const result = await api.completeModule(route.params.lessonId, activeModule.value.key);
    if (result.next_module) {
      router.push(`/workspace/${route.params.lessonId}/${result.next_module}`);
    } else {
      router.push(`/review/${route.params.lessonId}`);
    }
  } catch (err) {
    error.value = err.message || "保存模块进度失败";
  } finally {
    completing.value = false;
  }
}

watch(
  () => [route.params.lessonId, route.params.moduleKey],
  loadWorkspace,
  { immediate: true }
);
</script>

<template>
  <section class="page-stack page-screen workspace-screen">
    <div v-if="loading" class="loading-state">正在打开学习工作台…</div>
    <div v-else-if="error" class="error-state">{{ error }}</div>
    <template v-else-if="workspace && activeModule">
      <header class="page-header">
        <div>
          <p class="eyebrow">{{ workspace.shell.eyebrow }}</p>
          <h1 class="headline">{{ activeModule.title }}</h1>
          <p class="body-copy muted">{{ workspace.lesson.goal }}</p>
        </div>
        <div class="header-metrics">
          <div class="metric-chip">
            {{ workspace.shell.completion.completed }}/{{ workspace.shell.completion.total }}
          </div>
          <button class="btn btn-primary" :disabled="completing" @click="completeModule">
            {{ completing ? "保存中…" : activeModule.primary_action }}
          </button>
        </div>
      </header>

      <section class="workspace-grid">
        <ModuleSidebar
          :lesson-id="workspace.lesson.id"
          :lesson-card="workspace.sidebar.lesson_card"
          :modules="workspace.sidebar.modules"
          :active-key="activeModule.key"
        />

        <div class="workspace-main">
          <PanelCard
            :eyebrow="activeModule.english_title"
            :title="activeModule.description"
            tone="neutral"
          >
            <div class="pill-row">
              <span class="pill pill-neutral">{{ workspace.lesson.source_label }}</span>
              <span class="pill pill-success">{{ activeModule.duration }}</span>
              <span class="pill pill-warning">{{ activeModule.progress }}% progress</span>
            </div>
          </PanelCard>

          <ModuleRenderer :module="activeModule" />

          <section class="module-grid-2">
            <PanelCard
              v-for="panel in activeModule.footer_panels"
              :key="panel.title"
              :title="panel.title"
              :tone="panel.tone"
            >
              <ul class="bullet-list">
                <li v-for="item in panel.items" :key="item">{{ item }}</li>
              </ul>
            </PanelCard>
          </section>

          <PanelCard
            :eyebrow="activeModule.prompt_box.label"
            title="让 AI 教练继续往前推一小步"
            tone="info"
          >
            <div class="pill-row">
              <button
                v-for="prompt in activeModule.quick_prompts"
                :key="prompt"
                class="pill-button"
                @click="coachInput = prompt"
              >
                {{ prompt }}
              </button>
            </div>
            <textarea
              v-model="coachInput"
              class="text-area"
              :placeholder="activeModule.prompt_box.placeholder"
            ></textarea>
            <div class="action-row">
              <button class="btn btn-secondary" @click="coachInput = ''">清空</button>
              <button class="btn btn-primary" :disabled="coaching" @click="submitCoach">
                {{ coaching ? "思考中…" : activeModule.prompt_box.button_label }}
              </button>
            </div>
          </PanelCard>

          <PanelCard
            v-if="coachResponse"
            eyebrow="AI coach"
            :title="coachResponse.headline"
            tone="success"
          >
            <div class="score-banner">
              <span class="score-number">{{ coachResponse.score }}</span>
              <span class="body-copy muted">当前版本综合分</span>
            </div>
            <p class="body-copy">{{ coachResponse.summary }}</p>
            <ul class="bullet-list">
              <li v-for="item in coachResponse.bullets" :key="item">{{ item }}</li>
            </ul>
            <div class="pill-row">
              <span class="pill pill-success">下一步：{{ coachResponse.next_step }}</span>
            </div>
          </PanelCard>
        </div>

        <aside class="workspace-rail">
          <PanelCard
            v-for="panel in activeModule.side_panels"
            :key="panel.title"
            :title="panel.title"
            :tone="panel.tone"
          >
            <ul class="bullet-list">
              <li v-for="item in panel.items" :key="item">{{ item }}</li>
            </ul>
          </PanelCard>

          <PanelCard eyebrow="Lesson focus" title="本课状态">
            <div class="stack-list">
              <div v-for="metric in workspace.shell.stats" :key="metric.label" class="stack-row">
                <span>{{ metric.label }}</span>
                <strong>{{ metric.value }}</strong>
              </div>
            </div>
          </PanelCard>
        </aside>
      </section>
    </template>
  </section>
</template>
