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
          <button class="chip" :class="activeTab === 'link' ? 'chip-primary' : 'chip-soft'" @click="activeTab = 'link'">链接粘贴</button>
          <button class="chip" :class="activeTab === 'upload' ? 'chip-primary' : 'chip-soft'" @click="activeTab = 'upload'">本地音频</button>
        </div>
        <div v-if="activeTab === 'link'" class="soft-panel import-panel">
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
        <div v-else class="soft-panel import-panel">
          <p class="subtle-label">支持 MP3 / WAV / M4A / AAC / MP4</p>
          <input
            ref="fileInput"
            class="hidden-file-input"
            type="file"
            accept="audio/*,.mp3,.wav,.m4a,.aac,.mp4"
            @change="handleFileChange"
          />
          <div class="upload-picker">
            <button class="btn btn-secondary upload-picker-btn" @click="openFilePicker">
              选择音频文件
            </button>
            <div class="upload-picker-copy">
              <strong>{{ selectedFile ? selectedFile.name : "还没有选择文件" }}</strong>
              <span>{{ selectedFile ? formatFileSize(selectedFile.size) : "建议 3-15 分钟、清晰英文音频" }}</span>
            </div>
          </div>
          <p v-if="selectedFile" class="subtle-label">已选择：{{ selectedFile.name }}</p>
          <div class="split-row import-meta-row">
            <span class="chip chip-success">上传后进入分析队列</span>
            <span class="subtle-label">当前转写为开发态种子流程，已保留文件以便接 ASR</span>
          </div>
        </div>
        <p v-if="errorMessage" class="metric-note">{{ errorMessage }}</p>
        <button class="btn btn-primary btn-block" :disabled="isSubmitting" @click="handleImport">
          {{
            isSubmitting
              ? "正在提交..."
              : activeTab === 'link'
                ? data.importCard.button
                : '上传并生成精听课'
          }}
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
const activeTab = ref("link");
const link = ref("https://podcasts.apple.com/example");
const selectedFile = ref(null);
const errorMessage = ref("");
const isSubmitting = ref(false);
const fileInput = ref(null);
const STORAGE_KEY = "lingmate-active-lesson-id";

onMounted(async () => {
  data.value = await api.getHome();
});

async function handleImport() {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  errorMessage.value = "";

  try {
    if (activeTab.value === "link") {
      if (!/^https?:\/\//.test(link.value.trim())) {
        errorMessage.value = "请输入有效的链接。";
        return;
      }

      const result = await api.importMaterial({
        mode: "mock_url_import",
        source: {
          type: "url",
          url: link.value.trim(),
        },
      });
      return routeToAnalysis(result);
    }

    if (!selectedFile.value) {
      errorMessage.value = "请先选择一个本地音频文件。";
      return;
    }

    const result = await api.importAudio(selectedFile.value);
    return routeToAnalysis(result);
  } catch (error) {
    console.error(error);
    errorMessage.value = "上传失败，请检查后端是否启动，或稍后重试。";
  } finally {
    isSubmitting.value = false;
  }
}

function handleFileChange(event) {
  selectedFile.value = event.target.files?.[0] || null;
}

function openFilePicker() {
  fileInput.value?.click();
}

function formatFileSize(size) {
  if (!Number.isFinite(size)) return "";
  if (size < 1024 * 1024) {
    return `${Math.round(size / 1024)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function routeToAnalysis(result) {
  if (!result.lessonId) return;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, result.lessonId);
  }
  router.push({ name: "analysis", params: { lessonId: result.lessonId } });
}
</script>
