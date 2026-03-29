<template>
  <div class="view-stack" v-if="data && activeModule">
    <section class="workspace-header">
      <div>
        <p class="eyebrow">Learning Workspace · Module {{ activeModule.index }}</p>
        <h1 class="page-title">{{ activeModule.headerTitle }}</h1>
        <p class="page-description">{{ activeModule.headerDesc }}</p>
      </div>
      <div class="chip-row">
        <span class="chip">第 {{ activeModule.index }} / {{ data.progress.total }} 模块</span>
        <span class="chip">AI guided</span>
      </div>
    </section>

    <section class="workspace-grid">
      <aside class="workspace-sidebar">
        <article class="surface-card material-card">
          <p class="eyebrow">Current material</p>
          <h2 class="subsection-title">{{ data.material.title }}</h2>
          <p class="metric-note">{{ data.material.description }}</p>
          <div class="chip-row">
            <span v-for="chip in data.material.chips" :key="chip" class="chip">{{ chip }}</span>
          </div>
        </article>

        <article class="surface-card module-list">
          <button
            v-for="module in data.modules"
            :key="module.index"
            class="module-nav-item"
            :class="{ active: module.index === currentIndex }"
            :disabled="isSubmitting"
            @click="handleModuleSelect(module.index)"
          >
            <span class="counter">{{ module.index }}</span>
            <span>
              <strong>{{ module.name }}</strong>
              <small>{{ module.sidebar }}</small>
            </span>
          </button>
        </article>
      </aside>

      <main class="workspace-main">
        <div v-if="interactionMessage" class="workspace-feedback">
          {{ interactionMessage }}
        </div>
        <article class="surface-card top-module-card">
          <div class="split-row align-start">
            <div>
              <h2 class="section-title">{{ activeModule.topCard.title }}</h2>
              <p class="metric-note">{{ activeModule.topCard.subtitle }}</p>
            </div>
            <div class="chip-row">
              <span v-for="pill in activeModule.topCard.pills" :key="pill" class="chip">{{ pill }}</span>
            </div>
          </div>

          <div class="module-content">
            <template v-for="section in activeModule.topCard.sections" :key="JSON.stringify(section)">
              <div v-if="section.type === 'player'" class="player-row">
                <button class="play-button" :disabled="isSubmitting" @click="handleMockAction('play', '开始播放')">▶</button>
                <div class="progress-track">
                  <span :style="{ width: `${section.progress}%` }"></span>
                </div>
              </div>

              <div
                v-else-if="section.type === 'panel'"
                class="soft-panel"
                :class="`panel-${section.tone || 'secondary'}`"
              >
                <p class="eyebrow">{{ section.label }}</p>
                <p class="panel-text">{{ section.content }}</p>
              </div>

              <div v-else-if="section.type === 'chips'" class="chip-row">
                <span v-for="chip in section.items" :key="chip" class="chip chip-soft">
                  {{ chip }}
                </span>
              </div>

              <div v-else-if="section.type === 'dual-panels'" class="dual-grid">
                <div class="soft-panel panel-sage">
                  <p class="eyebrow">{{ section.left.label }}</p>
                  <p class="panel-text">{{ section.left.content }}</p>
                  <div class="chip-row">
                    <span v-for="chip in section.left.chips" :key="chip" class="chip chip-soft">
                      {{ chip }}
                    </span>
                  </div>
                </div>
                <div class="surface-card inner-card">
                  <p class="eyebrow">{{ section.right.label }}</p>
                  <div class="question-list">
                    <div v-for="question in section.right.questions" :key="question" class="question-row">
                      {{ question }}
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="section.type === 'expression-browser'" class="expression-layout">
                <div class="expression-list">
                  <div
                    v-for="expression in section.expressions"
                    :key="expression.phrase"
                    class="expression-row"
                    :class="{ selected: expression.selected }"
                  >
                    <span>{{ expression.phrase }}</span>
                    <span class="chip">{{ expression.cefr }}</span>
                  </div>
                </div>
                <div class="soft-panel">
                  <h3 class="feature-title">{{ section.detail.title }}</h3>
                  <p class="panel-text">{{ section.detail.body }}</p>
                  <div class="chip-row">
                    <span v-for="chip in section.detail.chips" :key="chip" class="chip chip-soft">
                      {{ chip }}
                    </span>
                  </div>
                  <div class="bullet-list">
                    <div v-for="item in section.detail.examples" :key="item" class="bullet-item">
                      <span class="bullet-dot"></span>
                      <span>{{ item }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="section.type === 'input'" class="input-module">
                <p class="eyebrow">{{ section.label }}</p>
                <textarea :value="section.content" rows="4" readonly />
              </div>

              <div v-else-if="section.type === 'banner'" class="banner" :class="`banner-${section.tone}`">
                {{ section.content }}
              </div>

              <div v-else-if="section.type === 'compare-list'" class="compare-list">
                <div v-for="pair in section.pairs" :key="pair.wrong" class="compare-item">
                  <div class="compare-columns">
                    <div class="compare-box compare-wrong">
                      <p class="eyebrow">我可能会这样说</p>
                      <p>{{ pair.wrong }}</p>
                    </div>
                    <div class="compare-box compare-right">
                      <p class="eyebrow">更自然的表达</p>
                      <p>{{ pair.right }}</p>
                    </div>
                  </div>
                  <p class="metric-note">{{ pair.note }}</p>
                </div>
              </div>

              <div v-else-if="section.type === 'scene-grid'" class="dual-grid">
                <div class="soft-panel">
                  <p class="eyebrow">{{ section.left.label }}</p>
                  <div class="simple-list">
                    <div v-for="row in section.left.rows" :key="row.label" class="simple-row">
                      <span>{{ row.label }}</span>
                      <span>{{ row.meta }}</span>
                    </div>
                  </div>
                  <div class="chip-row">
                    <span v-for="chip in section.left.chips" :key="chip" class="chip chip-soft">
                      {{ chip }}
                    </span>
                  </div>
                </div>
                <div class="soft-panel panel-sage">
                  <p class="eyebrow">{{ section.right.label }}</p>
                  <p class="panel-text whitespace">{{ section.right.content }}</p>
                </div>
              </div>

              <div v-else-if="section.type === 'tone-insight'" class="tone-layout">
                <div class="simple-list">
                  <div v-for="row in section.rows" :key="row.label" class="simple-row" :class="`tone-${row.tone}`">
                    <span>{{ row.label }}</span>
                    <span>{{ row.meta }}</span>
                  </div>
                </div>
                <div class="soft-panel">
                  <h3 class="feature-title">{{ section.insightTitle }}</h3>
                  <div class="chip-row">
                    <span v-for="chip in section.chips" :key="chip" class="chip chip-soft">
                      {{ chip }}
                    </span>
                  </div>
                  <p class="panel-text">{{ section.insightBody }}</p>
                </div>
              </div>

              <div v-else-if="section.type === 'pattern-panel'" class="soft-panel" :class="`panel-${section.tone || 'secondary'}`">
                <p class="eyebrow">{{ section.label }}</p>
                <h3 class="feature-title">{{ section.title }}</h3>
                <div class="chip-row">
                  <span v-for="chip in section.chips" :key="chip" class="chip chip-soft">
                    {{ chip }}
                  </span>
                </div>
              </div>

              <div v-else-if="section.type === 'output-layout'" class="output-layout">
                <div class="simple-list">
                  <div v-for="task in section.tasks" :key="task.label" class="simple-row" :class="`tone-${task.tone}`">
                    <span>{{ task.label }}</span>
                    <span>{{ task.meta }}</span>
                  </div>
                </div>
                <div class="input-module">
                  <p class="eyebrow">{{ section.inputLabel }}</p>
                  <textarea :value="section.inputContent" rows="8" readonly />
                </div>
              </div>
            </template>
          </div>

          <div v-if="activeModule.topCard.actions" class="button-row">
            <button
              v-for="action in activeModule.topCard.actions"
              :key="action.label"
              class="btn"
              :class="buttonClass(action.kind)"
              :disabled="isSubmitting"
              @click="handleAction(action)"
            >
              {{ action.label }}
            </button>
          </div>
        </article>

        <section class="bottom-cards">
          <article class="surface-card side-detail-card">
            <h3 class="subsection-title">{{ activeModule.leftCard.title }}</h3>
            <p v-if="activeModule.leftCard.body" class="metric-note">{{ activeModule.leftCard.body }}</p>
            <div v-if="activeModule.leftCard.items" class="bullet-list">
              <div v-for="item in activeModule.leftCard.items" :key="item" class="bullet-item">
                <span class="bullet-dot"></span>
                <span>{{ item }}</span>
              </div>
            </div>
            <div v-if="activeModule.leftCard.rows" class="simple-list">
              <div v-for="row in activeModule.leftCard.rows" :key="row.label" class="simple-row" :class="`tone-${row.tone}`">
                <span>{{ row.label }}</span>
                <span>{{ row.meta }}</span>
              </div>
            </div>
          </article>

          <article class="surface-card side-detail-card">
            <h3 class="subsection-title">{{ activeModule.rightCard.title }}</h3>
            <div v-if="activeModule.rightCard.score" class="split-row">
              <strong class="score">{{ activeModule.rightCard.score }}</strong>
              <span class="chip chip-warning">{{ activeModule.rightCard.banner }}</span>
            </div>
            <div v-if="activeModule.rightCard.rows" class="simple-list">
              <div v-for="row in activeModule.rightCard.rows" :key="row.label" class="simple-row" :class="`tone-${row.tone}`">
                <span>{{ row.label }}</span>
                <span>{{ row.meta }}</span>
              </div>
            </div>
            <div v-if="activeModule.rightCard.items" class="question-list">
              <div v-for="item in activeModule.rightCard.items" :key="item" class="question-row">
                {{ item }}
              </div>
            </div>
            <div v-if="activeModule.rightCard.inputLabel" class="input-module compact-input">
              <p class="eyebrow">{{ activeModule.rightCard.inputLabel }}</p>
              <textarea :value="activeModule.rightCard.inputContent" rows="4" readonly />
            </div>
            <div v-if="activeModule.rightCard.banner && !activeModule.rightCard.score" class="banner banner-warning">
              {{ activeModule.rightCard.banner }}
            </div>
            <p v-if="activeModule.rightCard.body" class="metric-note">{{ activeModule.rightCard.body }}</p>
            <div v-if="activeModule.rightCard.chips" class="chip-row">
              <span v-for="chip in activeModule.rightCard.chips" :key="chip" class="chip chip-soft">
                {{ chip }}
              </span>
            </div>
            <div v-if="activeModule.rightCard.panel" class="soft-panel">
              <p class="panel-text">{{ activeModule.rightCard.panel }}</p>
            </div>
            <p v-if="activeModule.rightCard.extra" class="metric-note">{{ activeModule.rightCard.extra }}</p>
            <button
              v-if="activeModule.rightCard.button"
              class="btn btn-primary"
              :disabled="isSubmitting"
              @click="handlePrimaryAdvance"
            >
              {{ activeModule.rightCard.button }}
            </button>
          </article>
        </section>
      </main>

      <aside class="coach-column">
        <article v-for="card in activeModule.coachCards" :key="card.title" class="surface-card coach-card">
          <h3 class="subsection-title">{{ card.title }}</h3>
          <p class="metric-note whitespace">{{ card.body }}</p>
          <div class="chip-row">
            <span v-for="tag in card.tags" :key="tag" class="chip">{{ tag }}</span>
          </div>
        </article>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { api } from "../lib/api";

const props = defineProps({
  lessonId: {
    type: String,
    required: true,
  },
});

const route = useRoute();
const router = useRouter();
const data = ref(null);
const currentIndex = ref(1);
const interactionMessage = ref("");
const isSubmitting = ref(false);

const activeModule = computed(() =>
  data.value?.modules.find((module) => module.index === currentIndex.value),
);

onMounted(async () => {
  await loadWorkspace();
});

watch(
  () => route.query.module,
  async (moduleValue, previousValue) => {
    if (moduleValue === previousValue) return;
    await loadWorkspace();
  },
);

function buttonClass(kind) {
  if (kind === "primary") return "btn-primary";
  if (kind === "soft") return "btn-soft";
  return "btn-secondary";
}

async function handlePrimaryAdvance() {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  try {
    if (currentIndex.value >= 8) {
      router.push({ name: "review", params: { lessonId: props.lessonId } });
      return;
    }
    const result = await api.completeModule(props.lessonId, String(currentIndex.value));
    interactionMessage.value = result.message;
    currentIndex.value = result.nextModule;
    await router.replace({
      name: "workspace",
      params: { lessonId: props.lessonId },
      query: { ...route.query, module: String(result.nextModule) },
    });
    await loadWorkspace();
  } catch (error) {
    interactionMessage.value = "工作台 mock 服务暂时没有响应，请再点一次试试。";
    console.error(error);
  } finally {
    isSubmitting.value = false;
  }
}

function handleAction(action) {
  if (action.kind === "primary") return handlePrimaryAdvance();
  return handleMockAction(action.kind || "interact", action.label);
}

async function handleModuleSelect(index) {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  try {
    const result = await api.moduleAction(props.lessonId, String(index), {
      action: "module_select",
      label: `切换到模块 ${index}`,
    });
    interactionMessage.value = result.message;
    currentIndex.value = result.currentModule;
    await router.replace({
      name: "workspace",
      params: { lessonId: props.lessonId },
      query: { ...route.query, module: String(result.currentModule) },
    });
    await loadWorkspace();
  } catch (error) {
    interactionMessage.value = "模块切换失败，请稍后重试。";
    console.error(error);
  } finally {
    isSubmitting.value = false;
  }
}

async function handleMockAction(action, label) {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  try {
    const result = await api.moduleAction(props.lessonId, String(currentIndex.value), {
      action,
      label,
    });
    interactionMessage.value = result.message;
    currentIndex.value = result.currentModule;
    await router.replace({
      name: "workspace",
      params: { lessonId: props.lessonId },
      query: { ...route.query, module: String(result.currentModule) },
    });
    await loadWorkspace();
  } catch (error) {
    interactionMessage.value = "当前操作没有成功提交到 mock 后端，请重试。";
    console.error(error);
  } finally {
    isSubmitting.value = false;
  }
}

async function loadWorkspace() {
  try {
    const requestedModule = Number.parseInt(String(route.query.module || ""), 10);
    const moduleIndex = Number.isFinite(requestedModule) ? requestedModule : null;
    data.value = await api.getWorkspace(props.lessonId, moduleIndex);
    currentIndex.value = data.value.progress.current || currentIndex.value;
    interactionMessage.value = data.value.interaction?.lastAction || interactionMessage.value;
  } catch (error) {
    interactionMessage.value = "工作台内容加载失败，请检查后端是否正在运行。";
    console.error(error);
  }
}
</script>
