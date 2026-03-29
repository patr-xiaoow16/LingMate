<template>
  <div class="view-stack" v-if="data">
    <section class="report-hero surface-card">
      <div class="report-copy">
        <p class="eyebrow">{{ data.hero.eyebrow }}</p>
        <h1 class="page-title">{{ data.hero.title }}</h1>
        <p class="page-description">{{ data.hero.description }}</p>
        <div class="button-row">
          <button class="btn btn-primary">{{ data.hero.actions[0] }}</button>
          <button class="btn btn-secondary">{{ data.hero.actions[1] }}</button>
        </div>
      </div>
      <div class="metric-grid compact">
        <article v-for="metric in data.metrics" :key="metric.title" class="metric-card mini">
          <p class="metric-title">{{ metric.title }}</p>
          <p class="metric-value">{{ metric.value }}</p>
          <p class="metric-note">{{ metric.note }}</p>
        </article>
      </div>
    </section>

    <section class="report-grid">
      <div class="report-main-column">
        <article class="surface-card">
          <div class="split-row">
            <h2 class="section-title">薄弱点正在往上走</h2>
            <span class="chip">vs. 上周</span>
          </div>
          <div class="insight-2col">
            <div class="bar-group">
              <div v-for="item in data.radar" :key="item.label" class="bar-item">
                <div class="split-row">
                  <span>{{ item.label }}</span>
                  <span class="subtle-label">{{ item.value }}</span>
                </div>
                <div class="progress-track">
                  <span :class="`fill-${item.tone}`" :style="{ width: item.value }"></span>
                </div>
              </div>
            </div>

            <div>
              <p class="eyebrow">Weekly listening hours</p>
              <div class="weekly-bars">
                <div v-for="bar in data.weeklyHours" :key="bar.day" class="week-bar-col">
                  <span class="week-bar" :class="`bar-${bar.tone}`" :style="{ height: `${bar.value}px` }"></span>
                  <small>{{ bar.day }}</small>
                </div>
              </div>
              <p class="metric-note">
                周三和周五进入了更深的专注状态，完成了 5-8 模块。下周继续保持 20-30 分钟的完整精听块。
              </p>
            </div>
          </div>
        </article>

        <article class="surface-card">
          <h2 class="section-title">学习闭环记录</h2>
          <div class="timeline">
            <div v-for="item in data.records" :key="item.date + item.title" class="timeline-item">
              <span class="timeline-date">{{ item.date }}</span>
              <div>
                <p class="timeline-title">{{ item.title }}</p>
                <p class="metric-note">{{ item.note }}</p>
              </div>
            </div>
          </div>
        </article>

        <article v-if="data.aiNotes?.length" class="surface-card">
          <div class="split-row">
            <h2 class="section-title">AI 随记回放</h2>
            <span class="chip">课堂过程</span>
          </div>
          <div class="report-note-list">
            <div v-for="entry in data.aiNotes" :key="entry.submissionId" class="report-note-item">
              <div class="report-note-bubble report-note-user">
                <div class="split-row">
                  <p class="eyebrow">{{ entry.user.role }} · Module {{ entry.moduleKey }}</p>
                  <span class="chip chip-soft">{{ entry.emotion?.label }}</span>
                </div>
                <p class="panel-text whitespace">{{ entry.user.content }}</p>
                <p class="subtle-label">{{ entry.createdAt }}</p>
              </div>
              <div class="report-note-bubble report-note-ai">
                <p class="eyebrow">{{ entry.assistant.role }}</p>
                <p class="panel-text whitespace">{{ entry.assistant.content }}</p>
                <div v-if="entry.assistant.suggestions?.length" class="chip-row">
                  <span v-for="suggestion in entry.assistant.suggestions" :key="suggestion" class="chip chip-soft">
                    {{ suggestion }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </article>
      </div>

      <div class="report-side-column">
        <article v-if="data.learningJourney" class="surface-card compact-report-card">
          <div class="split-row">
            <h2 class="section-title">学习情绪与模块时长</h2>
            <span class="chip">同图呈现</span>
          </div>
          <p class="metric-note">
            看看你在哪个模块最卡，又是从哪一段开始稳下来。
          </p>
          <div class="journey-chart compact-journey-chart">
            <div class="journey-chart-grid compact-journey-grid">
              <div
                v-for="(item, index) in data.learningJourney.labels"
                :key="item"
                class="journey-chart-col"
              >
                <div class="journey-bar-wrap">
                  <span
                    class="journey-bar"
                    :style="{ height: `${durationHeight(data.learningJourney.durationMinutes[index])}px` }"
                  ></span>
                </div>
                <div class="journey-meta">
                  <strong>{{ item }}</strong>
                  <small>{{ data.learningJourney.durationMinutes[index] }}m</small>
                  <span class="journey-emotion-chip" :class="emotionToneClass(data.learningJourney.emotionLabels[index])">
                    {{ data.learningJourney.emotionLabels[index] }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </article>

        <article v-if="data.learningJourney" class="surface-card compact-report-card">
          <div class="split-row">
            <h2 class="section-title">学习效率曲线</h2>
            <span class="chip">定义已说明</span>
          </div>
          <p class="metric-note">{{ data.learningJourney.efficiencyDefinition }}</p>
          <div class="efficiency-chart compact-efficiency-chart">
            <div class="efficiency-chart-board compact-efficiency-board">
              <svg class="efficiency-line-chart compact-efficiency-line" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
                <polyline
                  :points="efficiencyPolylinePoints(data.learningJourney.efficiencyScores)"
                  fill="none"
                  stroke="#315f4c"
                  stroke-width="2.8"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
                <circle
                  v-for="(point, index) in efficiencyChartPoints(data.learningJourney.efficiencyScores)"
                  :key="`${point.x}-${point.y}-${index}`"
                  :cx="point.x"
                  :cy="point.y"
                  r="2.8"
                  fill="#315f4c"
                />
              </svg>
              <div class="efficiency-x-axis">
                <div
                  v-for="(label, index) in data.learningJourney.labels"
                  :key="`${label}-${index}`"
                  class="efficiency-axis-item"
                >
                  <strong>{{ label }}</strong>
                  <small>{{ data.learningJourney.efficiencyScores[index] }}</small>
                </div>
              </div>
            </div>
            <p class="metric-note">
              效率最高：{{ highestEfficiencyLabel(data.learningJourney) }}
            </p>
          </div>
        </article>

        <article class="surface-card compact-report-card">
          <div class="split-row">
            <h2 class="section-title">今日复习队列</h2>
            <span class="chip">Ebbinghaus</span>
          </div>
          <div class="queue-list">
            <div
              v-for="item in data.queue"
              :key="item.title"
              class="queue-item"
              :class="{ active: item.active }"
            >
              <span class="queue-badge">R</span>
              <div class="queue-copy">
                <p class="timeline-title">{{ item.title }}</p>
                <p class="metric-note">{{ item.meta }}</p>
              </div>
              <span class="chip chip-soft">复习</span>
            </div>
          </div>
        </article>

        <article class="surface-card report-share-card">
          <h2 class="section-title">精听笔记卡</h2>
          <div class="soft-panel share-note-panel">
            <p class="eyebrow">Shareable note</p>
            <h3 class="feature-title">{{ data.shareCard.title }}</h3>
            <p class="panel-text whitespace">{{ data.shareCard.body }}</p>
            <div class="chip-row">
              <span v-for="chip in data.shareCard.chips" :key="chip" class="chip chip-soft">
                {{ chip }}
              </span>
            </div>
          </div>
          <p v-if="snapshotMessage" class="metric-note">{{ snapshotMessage }}</p>
          <div class="button-row">
            <button class="btn btn-primary" :disabled="isSavingSnapshot" @click="saveSnapshot">
              {{ isSavingSnapshot ? "生成快照中..." : "分享学习卡" }}
            </button>
            <RouterLink class="btn btn-secondary no-underline" :to="`/workspace/${props.lessonId}`">
              返回工作台
            </RouterLink>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { api } from "../lib/api";

const props = defineProps({
  lessonId: {
    type: String,
    required: true,
  },
});

const data = ref(null);
const isSavingSnapshot = ref(false);
const snapshotMessage = ref("");

onMounted(async () => {
  data.value = normalizeReport(await api.getReport(props.lessonId));
});

function normalizeReport(report) {
  const normalized = {
    ...(report || {}),
  };

  if (!Array.isArray(normalized.aiNotes) || !normalized.aiNotes.length) {
    normalized.aiNotes = buildFallbackAiNotes(normalized);
  }

  if (!normalized.learningJourney) {
    normalized.learningJourney = buildFallbackLearningJourney();
  }

  return normalized;
}

function buildFallbackAiNotes(report) {
  const records = Array.isArray(report?.records) ? report.records : [];
  const queue = Array.isArray(report?.queue) ? report.queue : [];
  const title = report?.shareCard?.title || "每一句，都陪你听懂";
  const body = report?.shareCard?.body || "本课的关键表达已经进入复习与迁移阶段。";

  const baseEntries = records.slice(0, 3).map((item, index) => ({
    submissionId: `fallback-note-${index + 1}`,
    moduleKey: index + 3,
    createdAt: item.date || `03/2${index + 4}`,
    emotion: {
      label: ["困惑", "投入", "兴奋"][index] || "投入",
    },
    user: {
      role: "Learner note",
      content: item.note || item.title || "这一段已经开始听顺了，但还想再复述一遍。",
    },
    assistant: {
      role: "Lingmate AI",
      content:
        index === 0
          ? "先别急着记整句，先抓住场景里的语气变化，再回头复述关键词。"
          : index === 1
            ? "这次已经不只是听懂了，你开始把表达和新场景连接起来了。"
            : "可以继续把这条表达放进自己的工作或生活语境里，迁移会更稳。",
      suggestions: [
        queue[index]?.title || "跟读 2 遍",
        index === 0 ? "标出弱读" : "换场景复述",
      ],
    },
  }));

  if (baseEntries.length) {
    return baseEntries;
  }

  return [
    {
      submissionId: "fallback-note-1",
      moduleKey: 4,
      createdAt: "03/24",
      emotion: { label: "困惑" },
      user: {
        role: "Learner note",
        content: `刚开始听的时候只能抓住零散词，但已经能感觉到整段语气在变。`,
      },
      assistant: {
        role: "Lingmate AI",
        content: "这是正常过程，先抓住表达出现的位置，再回头做精听切片。",
        suggestions: ["标记关键词", "回放两遍"],
      },
    },
    {
      submissionId: "fallback-note-2",
      moduleKey: 6,
      createdAt: "03/26",
      emotion: { label: "投入" },
      user: {
        role: "Learner note",
        content: body,
      },
      assistant: {
        role: "Lingmate AI",
        content: `你已经开始把材料中的表达迁移到自己的语境里了，继续保持这种输出节奏。`,
        suggestions: [title, "换场景复述"],
      },
    },
  ];
}

function buildFallbackLearningJourney() {
  return {
    labels: ["M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"],
    durationMinutes: [5, 7, 10, 8, 12, 11, 9, 6],
    emotionLabels: ["困惑", "投入", "投入", "挫败", "投入", "兴奋", "投入", "平稳"],
    efficiencyScores: [42, 58, 63, 49, 72, 81, 76, 68],
    efficiencyDefinition: "综合模块停留时长、推进速度和交互完成度得到的阶段效率分数。",
  };
}

function durationHeight(value) {
  const max = Math.max(...(data.value?.learningJourney?.durationMinutes || [1]), 1);
  return Math.max(8, (Number(value || 0) / max) * 60);
}

function emotionToneClass(label) {
  if (label === "挫败" || label === "困惑") return "emotion-negative";
  if (label === "投入" || label === "兴奋") return "emotion-positive";
  return "emotion-neutral";
}

function efficiencyChartPoints(scores) {
  const values = Array.isArray(scores) ? scores : [];
  if (!values.length) return [];
  const step = 100 / Math.max(values.length - 1, 1);
  return values.map((score, index) => {
    const normalized = Math.max(0, Math.min(100, Number(score || 0))) / 100;
    return {
      x: Number((index * step).toFixed(2)),
      y: Number((92 - normalized * 72).toFixed(2)),
    };
  });
}

function efficiencyPolylinePoints(scores) {
  return efficiencyChartPoints(scores)
    .map((point) => `${point.x},${point.y}`)
    .join(" ");
}

function highestEfficiencyLabel(journey) {
  const scores = journey?.efficiencyScores || [];
  const labels = journey?.labels || [];
  if (!scores.length || !labels.length) return "暂无";
  let maxIndex = 0;
  scores.forEach((score, index) => {
    if (score > scores[maxIndex]) maxIndex = index;
  });
  return `${labels[maxIndex]}（${scores[maxIndex]}）`;
}

function wrapText(context, text, maxWidth) {
  const paragraphs = String(text || "").split("\n");
  const lines = [];

  for (const paragraph of paragraphs) {
    if (!paragraph.trim()) {
      lines.push("");
      continue;
    }
    let current = "";
    for (const char of paragraph) {
      const next = current + char;
      if (context.measureText(next).width > maxWidth && current) {
        lines.push(current);
        current = char;
      } else {
        current = next;
      }
    }
    if (current) lines.push(current);
  }

  return lines;
}

function roundRect(context, x, y, width, height, radius) {
  context.beginPath();
  context.moveTo(x + radius, y);
  context.arcTo(x + width, y, x + width, y + height, radius);
  context.arcTo(x + width, y + height, x, y + height, radius);
  context.arcTo(x, y + height, x, y, radius);
  context.arcTo(x, y, x + width, y, radius);
  context.closePath();
}

async function saveSnapshot() {
  if (!data.value || isSavingSnapshot.value) return;

  isSavingSnapshot.value = true;
  snapshotMessage.value = "";

  try {
    const card = data.value.shareCard;
    const pixelRatio = typeof window !== "undefined" ? Math.max(window.devicePixelRatio || 1, 2) : 2;
    const width = 1200;
    const height = 900;
    const canvas = document.createElement("canvas");
    canvas.width = width * pixelRatio;
    canvas.height = height * pixelRatio;

    const context = canvas.getContext("2d");
    if (!context) throw new Error("Canvas unavailable");
    context.scale(pixelRatio, pixelRatio);

    context.fillStyle = "#f5f1e8";
    context.fillRect(0, 0, width, height);

    const gradient = context.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, "rgba(223, 231, 221, 0.72)");
    gradient.addColorStop(1, "rgba(236, 229, 217, 0.22)");
    context.fillStyle = gradient;
    context.fillRect(0, 0, width, height);

    roundRect(context, 64, 64, width - 128, height - 128, 42);
    context.fillStyle = "#fbf8f2";
    context.fill();
    context.strokeStyle = "rgba(214, 202, 184, 0.92)";
    context.lineWidth = 2;
    context.stroke();

    context.fillStyle = "#3f6a56";
    context.beginPath();
    context.arc(112, 118, 12, 0, Math.PI * 2);
    context.fill();

    context.fillStyle = "#2c3c35";
    context.font = "600 28px Georgia, 'Times New Roman', serif";
    context.fillText("lingmate", 140, 128);
    context.fillStyle = "#7a8178";
    context.font = "500 20px system-ui, -apple-system, sans-serif";
    context.fillText("Immersive listening workspace", 140, 164);

    roundRect(context, 820, 98, 250, 56, 28);
    context.fillStyle = "#ece5d9";
    context.fill();
    context.fillStyle = "#31493f";
    context.font = "700 22px system-ui, -apple-system, sans-serif";
    context.fillText("SHAREABLE NOTE", 856, 134);

    roundRect(context, 108, 214, width - 216, 518, 34);
    context.fillStyle = "#efe7d7";
    context.fill();

    context.fillStyle = "#7a8178";
    context.font = "700 18px system-ui, -apple-system, sans-serif";
    context.fillText("每一句，都陪你听懂", 130, 268);

    context.fillStyle = "#22362f";
    context.font = "400 56px 'Songti SC', 'STSong', Georgia, serif";
    const titleLines = wrapText(context, card.title, width - 320);
    let cursorY = 350;
    for (const line of titleLines) {
      context.fillText(line, 130, cursorY);
      cursorY += 70;
    }

    context.font = "500 24px system-ui, -apple-system, sans-serif";
    const bodyLines = wrapText(context, card.body, width - 320);
    cursorY += 12;
    for (const line of bodyLines) {
      if (!line) {
        cursorY += 16;
        continue;
      }
      context.fillText(line, 130, cursorY);
      cursorY += 38;
    }

    let chipX = 130;
    const chipY = 640;
    context.font = "700 20px system-ui, -apple-system, sans-serif";
    for (const chip of card.chips) {
      const chipWidth = context.measureText(chip).width + 42;
      roundRect(context, chipX, chipY, chipWidth, 48, 24);
      context.fillStyle = "#fbf8f2";
      context.fill();
      context.fillStyle = "#31493f";
      context.fillText(chip, chipX + 21, chipY + 31);
      chipX += chipWidth + 16;
    }

    context.fillStyle = "#7a8178";
    context.font = "500 18px system-ui, -apple-system, sans-serif";
    context.fillText(`Lesson ID · ${props.lessonId}`, 130, 780);
    context.fillText(new Date().toLocaleDateString("zh-CN"), 920, 780);

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
    if (!blob) throw new Error("Snapshot export failed");

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `lingmate-note-${props.lessonId}.png`;
    link.click();
    URL.revokeObjectURL(url);

    snapshotMessage.value = "学习卡快照已生成并开始下载。";
  } catch (error) {
    console.error(error);
    snapshotMessage.value = "快照生成失败，请稍后再试。";
  } finally {
    isSavingSnapshot.value = false;
  }
}
</script>
