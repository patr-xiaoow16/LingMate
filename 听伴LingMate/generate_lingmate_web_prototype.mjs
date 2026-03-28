import fs from "node:fs";
import path from "node:path";

let nextId = 0;

const uid = (prefix = "n") => `${prefix}${(++nextId).toString(36)}`;

const defined = (value) => value !== undefined && value !== null;

const clean = (value) => {
  if (Array.isArray(value)) {
    return value.map(clean);
  }
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([, item]) => defined(item))
        .map(([key, item]) => [key, clean(item)]),
    );
  }
  return value;
};

const withChildren = (children) => (children?.length ? { children } : {});

const frame = (props = {}, children = []) =>
  clean({
    type: "frame",
    id: uid("f"),
    ...props,
    ...withChildren(children),
  });

const text = (props = {}) =>
  clean({
    type: "text",
    id: uid("t"),
    ...props,
  });

const rect = (props = {}) =>
  clean({
    type: "rectangle",
    id: uid("r"),
    ...props,
  });

const icon = (props = {}) =>
  clean({
    type: "icon_font",
    id: uid("i"),
    iconFontFamily: "Material Symbols Rounded",
    weight: 300,
    ...props,
  });

const shadow = (opacity = "14", blur = 30, y = 18) => ({
  type: "shadow",
  shadowType: "outer",
  color: `#1b2c24${opacity}`,
  offset: { x: 0, y },
  blur,
});

const hStack = ({
  x,
  y,
  width,
  height,
  gap = 0,
  padding,
  justifyContent,
  alignItems,
  fill,
  stroke,
  cornerRadius,
  effect,
  clip,
  name,
  children = [],
}) =>
  frame(
    {
      x,
      y,
      width,
      height,
      gap,
      padding,
      justifyContent,
      alignItems,
      fill,
      stroke,
      cornerRadius,
      effect,
      clip,
      name,
      layout: "horizontal",
    },
    children,
  );

const vStack = ({
  x,
  y,
  width,
  height,
  gap = 0,
  padding,
  justifyContent,
  alignItems,
  fill,
  stroke,
  cornerRadius,
  effect,
  clip,
  name,
  children = [],
}) =>
  frame(
    {
      x,
      y,
      width,
      height,
      gap,
      padding,
      justifyContent,
      alignItems,
      fill,
      stroke,
      cornerRadius,
      effect,
      clip,
      name,
      layout: "vertical",
    },
    children,
  );

const divider = ({ width, x, y, fill = "$--border" }) =>
  rect({
    x,
    y,
    width,
    height: 1,
    fill,
  });

const dot = ({ size = 10, fill = "$--primary" }) =>
  rect({
    width: size,
    height: size,
    fill,
    cornerRadius: 999,
  });

const counterBubble = ({
  label,
  size = 34,
  fill = "$--secondary",
  textFill = "$--foreground",
}) =>
  vStack({
    width: size,
    height: size,
    justifyContent: "center",
    alignItems: "center",
    fill,
    cornerRadius: 999,
    children: [
      text({
        content: label,
        fill: textFill,
        fontFamily: "$--font-secondary",
        fontSize: 12,
        fontWeight: "600",
        lineHeight: 1,
      }),
    ],
  });

const progressTrack = ({
  width,
  valueWidth,
  background = "$--secondary",
  foreground = "$--primary",
  height = 10,
}) =>
  frame(
    {
      width,
      height,
      layout: "none",
    },
    [
      rect({ x: 0, y: 0, width, height, fill: background, cornerRadius: 999 }),
      rect({ x: 0, y: 0, width: valueWidth, height, fill: foreground, cornerRadius: 999 }),
    ],
  );

const pill = ({
  label,
  fill = "$--secondary",
  textFill = "$--foreground",
  iconName,
  padding = [8, 12],
}) =>
  hStack({
    gap: 8,
    padding,
    fill,
    cornerRadius: "$--radius-pill",
    alignItems: "center",
    children: [
      iconName ? icon({ iconFontName: iconName, width: 16, height: 16, fill: textFill }) : undefined,
      text({
        content: label,
        fill: textFill,
        fontFamily: "$--font-secondary",
        fontSize: 13,
        fontWeight: "500",
        lineHeight: 1.1,
      }),
    ].filter(Boolean),
  });

const button = ({
  label,
  variant = "primary",
  width,
  iconName,
}) => {
  const fills =
    variant === "primary"
      ? { fill: "$--primary", textFill: "$--primary-foreground", stroke: undefined }
      : variant === "outline"
        ? {
            fill: "#00000000",
            textFill: "$--foreground",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
          }
        : {
            fill: "$--secondary",
            textFill: "$--foreground",
            stroke: undefined,
          };

  return hStack({
    width,
    height: 48,
    gap: 8,
    padding: [12, 18],
    fill: fills.fill,
    stroke: fills.stroke,
    cornerRadius: "$--radius-pill",
    alignItems: "center",
    justifyContent: "center",
    children: [
      text({
        content: label,
        fill: fills.textFill,
        fontFamily: "$--font-secondary",
        fontSize: 15,
        fontWeight: "600",
        lineHeight: 1,
      }),
      iconName
        ? icon({
            iconFontName: iconName,
            width: 16,
            height: 16,
            fill: fills.textFill,
          })
        : undefined,
    ].filter(Boolean),
  });
};

const sectionLabel = (content, width = 240) =>
  text({
    width,
    content,
    fill: "$--muted-foreground",
    fontFamily: "$--font-secondary",
    fontSize: 13,
    fontWeight: "600",
    lineHeight: 1.1,
  });

const bodyText = (content, width, size = 16, fill = "$--muted-foreground") =>
  text({
    width,
    content,
    fill,
    textGrowth: "fixed-width",
    fontFamily: "$--font-secondary",
    fontSize: size,
    fontWeight: "normal",
    lineHeight: 1.6,
  });

const titleText = (content, width, size = 42, fill = "$--foreground", weight = "normal") =>
  text({
    width,
    content,
    fill,
    textGrowth: "fixed-width",
    fontFamily: "$--font-primary",
    fontSize: size,
    fontWeight: weight,
    lineHeight: 1.15,
  });

const metricCard = ({ title, value, note, width = 198 }) =>
  vStack({
    width,
    height: 154,
    gap: 14,
    padding: 22,
    fill: "$--card",
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 20,
    children: [
      sectionLabel(title, width - 44),
      titleText(value, width - 44, 34),
      bodyText(note, width - 44, 14),
    ],
  });

const smallRow = ({ label, meta, width = 486, accent = "$--primary" }) =>
  hStack({
    width,
    gap: 12,
    padding: [14, 16],
    alignItems: "center",
    justifyContent: "space_between",
    stroke: { align: "inside", thickness: { bottom: 1 }, fill: "$--border" },
    children: [
      hStack({
        gap: 12,
        alignItems: "center",
        children: [
          rect({ width: 8, height: 8, fill: accent, cornerRadius: 999 }),
          text({
            content: label,
            fill: "$--foreground",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "500",
            lineHeight: 1.2,
          }),
        ],
      }),
      text({
        content: meta,
        fill: "$--muted-foreground",
        fontFamily: "$--font-secondary",
        fontSize: 13,
        fontWeight: "normal",
        lineHeight: 1.2,
      }),
    ],
  });

const scenarioCard = ({
  title,
  subtitle,
  meta,
  expression,
  accent = "$--primary",
  width = 421,
}) =>
  vStack({
    width,
    height: 240,
    gap: 16,
    padding: 24,
    fill: "$--card",
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 24,
    effect: shadow("0d", 18, 8),
    children: [
      hStack({
        justifyContent: "space_between",
        alignItems: "center",
        children: [
          pill({ label: subtitle, fill: "$--secondary" }),
          dot({ size: 12, fill: accent }),
        ],
      }),
      titleText(title, width - 48, 30),
      bodyText(meta, width - 48, 15),
      rect({
        width: width - 48,
        height: 1,
        fill: "$--border",
      }),
      text({
        width: width - 48,
        content: expression,
        fill: accent,
        textGrowth: "fixed-width",
        fontFamily: "$--font-secondary",
        fontSize: 15,
        fontWeight: "600",
        lineHeight: 1.4,
      }),
    ],
  });

const topLabel = ({ index, name, x, y }) =>
  hStack({
    x,
    y,
    gap: 10,
    alignItems: "center",
    children: [
      pill({ label: index, fill: "$--secondary" }),
      text({
        content: name,
        fill: "$--foreground",
        fontFamily: "$--font-secondary",
        fontSize: 16,
        fontWeight: "600",
        lineHeight: 1.2,
      }),
    ],
  });

const appScreen = ({ name, x, y, width = 1440, height = 1260, children = [] }) =>
  frame(
    {
      name,
      x,
      y,
      width,
      height,
      clip: true,
      fill: "$--background",
      cornerRadius: 28,
      stroke: { align: "inside", thickness: 1, fill: "$--border" },
      effect: shadow("18", 42, 20),
      layout: "none",
    },
    children,
  );

const appHeader = ({ subtitle, primaryAction = "开始学习" }) =>
  hStack({
    x: 0,
    y: 0,
    width: 1440,
    height: 88,
    padding: [24, 32],
    justifyContent: "space_between",
    alignItems: "center",
    stroke: { align: "inside", thickness: { bottom: 1 }, fill: "$--border" },
    children: [
      hStack({
        gap: 14,
        alignItems: "center",
        children: [
          rect({ width: 14, height: 14, fill: "$--primary", cornerRadius: 999 }),
          vStack({
            gap: 4,
            children: [
              text({
                content: "lingmate",
                fill: "$--foreground",
                fontFamily: "$--font-primary",
                fontSize: 24,
                fontWeight: "normal",
                lineHeight: 1,
              }),
              text({
                content: subtitle,
                fill: "$--muted-foreground",
                fontFamily: "$--font-secondary",
                fontSize: 12,
                fontWeight: "500",
                lineHeight: 1.1,
              }),
            ],
          }),
        ],
      }),
      hStack({
        gap: 26,
        alignItems: "center",
        children: [
          text({
            content: "八步方法",
            fill: "$--muted-foreground",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "500",
            lineHeight: 1,
          }),
          text({
            content: "推荐库",
            fill: "$--muted-foreground",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "500",
            lineHeight: 1,
          }),
          text({
            content: "学习报告",
            fill: "$--muted-foreground",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "500",
            lineHeight: 1,
          }),
          button({ label: primaryAction, variant: "primary", iconName: "arrow_outward" }),
        ],
      }),
    ],
  });

const makeHomeScreen = (x, y) => {
  const importCard = vStack({
    x: 826,
    y: 132,
    width: 550,
    height: 650,
    gap: 24,
    padding: 32,
    fill: "$--card",
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 28,
    effect: shadow("10", 22, 10),
    children: [
      sectionLabel("Start with any material", 240),
      titleText("把任意英文内容，变成一堂会陪你走完的精听课", 486, 34),
      hStack({
        width: 486,
        gap: 10,
        children: [
          pill({ label: "链接粘贴", fill: "$--primary", textFill: "$--primary-foreground" }),
          pill({ label: "推荐库", fill: "$--secondary" }),
          pill({ label: "本地上传", fill: "$--secondary" }),
        ],
      }),
      vStack({
        width: 486,
        height: 160,
        gap: 14,
        padding: 20,
        fill: "$--secondary",
        cornerRadius: 22,
        children: [
          text({
            content: "YouTube / Spotify / Apple Podcast / TED / BBC",
            fill: "$--muted-foreground",
            fontFamily: "$--font-secondary",
            fontSize: 13,
            fontWeight: "500",
            lineHeight: 1.2,
          }),
          hStack({
            width: 446,
            height: 54,
            gap: 12,
            padding: [16, 18],
            alignItems: "center",
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 18,
            children: [
              icon({ iconFontName: "link", width: 18, height: 18, fill: "$--muted-foreground" }),
              text({
                content: "粘贴一段你最近总是听不清的英文链接",
                fill: "$--muted-foreground",
                fontFamily: "$--font-secondary",
                fontSize: 15,
                fontWeight: "normal",
                lineHeight: 1.2,
              }),
            ],
          }),
          hStack({
            width: 446,
            justifyContent: "space_between",
            alignItems: "center",
            children: [
              pill({ label: "预计 30 秒完成分析", fill: "$--color-success", textFill: "$--color-success-foreground" }),
              text({
                content: "Whisper + AI lesson planner",
                fill: "$--muted-foreground",
                fontFamily: "$--font-secondary",
                fontSize: 13,
                fontWeight: "500",
                lineHeight: 1.2,
              }),
            ],
          }),
        ],
      }),
      button({ label: "生成精听课", variant: "primary", width: 486, iconName: "north_east" }),
      vStack({
        width: 486,
        gap: 0,
        fill: "#00000000",
        children: [
          smallRow({ label: "The Daily: Why Office English Still Feels Hard", meta: "B2 · 11 min", accent: "$--primary" }),
          smallRow({ label: "TED: Tiny Habits That Actually Stick", meta: "B1 · 08 min", accent: "$--color-warning-foreground" }),
          smallRow({ label: "Modern Family Clip: I’m not feeling great", meta: "A2 · 03 min", accent: "$--color-error-foreground" }),
        ],
      }),
    ],
  });

  return appScreen({
    name: "LingMate / Home",
    x,
    y,
    children: [
      appHeader({ subtitle: "Nordic editorial web prototype", primaryAction: "导入材料" }),
      rect({
        x: 1006,
        y: 110,
        width: 290,
        height: 290,
        fill: "$--sage-soft",
        cornerRadius: 999,
        opacity: 0.7,
      }),
      rect({
        x: 948,
        y: 416,
        width: 342,
        height: 154,
        fill: "$--sand-soft",
        cornerRadius: 32,
        opacity: 0.8,
      }),
      vStack({
        x: 64,
        y: 132,
        width: 626,
        gap: 18,
        children: [
          sectionLabel("AI Co-pilot for immersive listening", 320),
          titleText("每一句，都陪你听懂。", 600, 78),
          bodyText(
            "将 YouTube、播客或本地音频，拆成覆盖“听懂、拆解、迁移、会用”的八步沉浸式精听课。网页端强调安静、连续、低负担的学习体验，不像题库，更像一位审美在线的听力教练。",
            590,
            19,
          ),
          hStack({
            gap: 14,
            children: [
              button({ label: "开始一段新材料", variant: "primary", iconName: "arrow_outward" }),
              button({ label: "先看示例课", variant: "outline" }),
            ],
          }),
          hStack({
            gap: 12,
            children: [
              pill({ label: "支持 YouTube / Podcast / MP3", fill: "$--secondary" }),
              pill({ label: "AI 30s 预处理", fill: "$--secondary" }),
            ],
          }),
        ],
      }),
      hStack({
        x: 64,
        y: 510,
        gap: 18,
        children: [
          metricCard({
            title: "本周完整精听",
            value: "4 次",
            note: "平均完成 6.3 / 8 模块，已超过目标节奏。",
          }),
          metricCard({
            title: "最近新增表达",
            value: "26 条",
            note: "高频集中在商务请假、播客口语与态度表达。",
          }),
          metricCard({
            title: "适配材料难度",
            value: "B1-B2",
            note: "推荐先从 8-12 分钟材料开始，体验更顺滑。",
          }),
        ],
      }),
      importCard,
      vStack({
        x: 64,
        y: 848,
        width: 1312,
        gap: 18,
        children: [
          hStack({
            width: 1312,
            justifyContent: "space_between",
            alignItems: "center",
            children: [
              titleText("从真实场景开始，而不是从题目开始", 680, 34),
              text({
                content: "Most chosen this week",
                fill: "$--muted-foreground",
                fontFamily: "$--font-secondary",
                fontSize: 14,
                fontWeight: "500",
                lineHeight: 1.1,
              }),
            ],
          }),
          hStack({
            gap: 24,
            children: [
              scenarioCard({
                title: "请假与状态表达",
                subtitle: "日常 / 职场",
                meta: "从 “I’m not feeling great” 到 “calling in sick”，顺手学会委婉与正式语气的差异。",
                expression: "I’m calling in sick today.",
                accent: "$--primary",
              }),
              scenarioCard({
                title: "播客里的高频口语",
                subtitle: "通勤 / 自学",
                meta: "针对连读、吞音和语速跳跃的段落，给你逐句拆出“实际听起来像什么”。",
                expression: "kind of / sort of / gonna",
                accent: "$--color-warning-foreground",
              }),
              scenarioCard({
                title: "雅思与课堂听力",
                subtitle: "学术 / 备考",
                meta: "保留材料的原始语速，但把关键词、语义转折与潜台词先替你点亮。",
                expression: "What the speaker is really implying",
                accent: "$--color-error-foreground",
              }),
            ],
          }),
        ],
      }),
    ],
  });
};

const stepRow = ({ index, title, note, status = "done", width = 232 }) => {
  const tone =
    status === "active"
      ? { fill: "$--primary", textFill: "$--primary-foreground", dot: "$--primary" }
      : status === "todo"
        ? { fill: "$--secondary", textFill: "$--muted-foreground", dot: "$--border" }
        : { fill: "$--color-success", textFill: "$--color-success-foreground", dot: "$--color-success-foreground" };

  return hStack({
    width,
    gap: 14,
    padding: [14, 16],
    alignItems: "center",
    fill: tone.fill,
    cornerRadius: 18,
    children: [
      counterBubble({
        label: status === "done" ? "OK" : index,
        fill: status === "todo" ? "$--card" : "#ffffff22",
        textFill: tone.textFill,
      }),
      vStack({
        width: width - 96,
        gap: 4,
        children: [
          text({
            content: `${index}. ${title}`,
            fill: tone.textFill,
            width: width - 96,
            textGrowth: "fixed-width",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "600",
            lineHeight: 1.25,
          }),
          text({
            content: note,
            fill: status === "active" ? "$--primary-foreground" : "$--muted-foreground",
            width: width - 96,
            textGrowth: "fixed-width",
            fontFamily: "$--font-secondary",
            fontSize: 12,
            fontWeight: "normal",
            lineHeight: 1.3,
            opacity: status === "active" ? 0.86 : 1,
          }),
        ],
      }),
    ],
  });
};

const insightsCard = ({ title, items, fill = "$--card", height = 250 }) =>
  vStack({
    width: 264,
    height,
    gap: 16,
    padding: 22,
    fill,
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 24,
    children: [
      titleText(title, 220, 26),
      ...items.map((item, index) =>
        hStack({
          width: 220,
          gap: 12,
          alignItems: "center",
          children: [
            rect({
              width: 8,
              height: 8,
              fill: index === 0 ? "$--primary" : index === 1 ? "$--color-warning-foreground" : "$--color-error-foreground",
              cornerRadius: 999,
            }),
            text({
              width: 200,
              content: item,
              fill: "$--foreground",
              textGrowth: "fixed-width",
              fontFamily: "$--font-secondary",
              fontSize: 14,
              fontWeight: "500",
              lineHeight: 1.45,
            }),
          ],
        }),
      ),
    ],
  });

const lessonModuleRow = ({ label, desc, toneFill = "$--secondary" }) =>
  hStack({
    width: 640,
    gap: 14,
    padding: [14, 16],
    alignItems: "center",
    fill: toneFill,
    cornerRadius: 16,
    children: [
      rect({ width: 10, height: 10, fill: "$--primary", cornerRadius: 999 }),
      text({
        content: label,
        fill: "$--foreground",
        fontFamily: "$--font-secondary",
        fontSize: 14,
        fontWeight: "600",
        lineHeight: 1.2,
      }),
      text({
        width: 420,
        content: desc,
        fill: "$--muted-foreground",
        textGrowth: "fixed-width",
        fontFamily: "$--font-secondary",
        fontSize: 13,
        fontWeight: "normal",
        lineHeight: 1.35,
      }),
    ],
  });

const makeAnalysisScreen = (x, y) =>
  appScreen({
    name: "LingMate / AI Analysis",
    x,
    y,
    children: [
      appHeader({ subtitle: "Pre-processing and lesson planning", primaryAction: "开始本课" }),
      vStack({
        x: 64,
        y: 128,
        width: 720,
        gap: 14,
        children: [
          sectionLabel("Import complete in 00:28", 240),
          titleText("30 秒内，自动拆成一堂完整精听课", 700, 52),
          bodyText("系统先替你完成转写、难度分级、关键表达抽取、场景识别和语音现象标注。网页端把这些分析做成可浏览、可解释、可开始学习的结构，而不是一串黑箱结果。", 680, 18),
        ],
      }),
      hStack({
        x: 64,
        y: 286,
        gap: 12,
        children: [
          pill({ label: "CEFR B2", fill: "$--secondary" }),
          pill({ label: "147 WPM", fill: "$--secondary" }),
          pill({ label: "Business podcast", fill: "$--secondary" }),
          pill({ label: "11m 24s", fill: "$--secondary" }),
        ],
      }),
      vStack({
        x: 64,
        y: 348,
        width: 280,
        height: 848,
        gap: 20,
        padding: 24,
        fill: "$--card",
        stroke: { align: "inside", thickness: 1, fill: "$--border" },
        cornerRadius: 26,
        children: [
          titleText("AI 预处理流水线", 232, 28),
          bodyText("已完成 6 / 6 个关键步骤，正在生成八步学习结构。", 232, 14),
          hStack({
            width: 232,
            justifyContent: "space_between",
            children: [
              text({
                content: "生成进度",
                fill: "$--muted-foreground",
                fontFamily: "$--font-secondary",
                fontSize: 13,
                fontWeight: "500",
                lineHeight: 1.2,
              }),
              text({
                content: "92%",
                fill: "$--primary",
                fontFamily: "$--font-secondary",
                fontSize: 13,
                fontWeight: "600",
                lineHeight: 1.2,
              }),
            ],
          }),
          progressTrack({ width: 232, valueWidth: 184 }),
          stepRow({ index: "01", title: "Whisper 转写", note: "句级时间戳已对齐", status: "done" }),
          stepRow({ index: "02", title: "难度分级", note: "词汇 B2 / 语速偏快", status: "done" }),
          stepRow({ index: "03", title: "关键表达", note: "已提取 8 条高价值表达", status: "done" }),
          stepRow({ index: "04", title: "场景识别", note: "职场沟通 / 请假语境", status: "done" }),
          stepRow({ index: "05", title: "语音现象", note: "连读 / 弱读 / T 音变化", status: "done" }),
          stepRow({ index: "06", title: "课程编排", note: "正在把内容映射到 8 个模块", status: "active" }),
        ],
      }),
      vStack({
        x: 368,
        y: 348,
        width: 696,
        height: 848,
        gap: 22,
        padding: 28,
        fill: "$--card",
        stroke: { align: "inside", thickness: 1, fill: "$--border" },
        cornerRadius: 28,
        children: [
          hStack({
            width: 640,
            justifyContent: "space_between",
            alignItems: "center",
            children: [
              vStack({
                gap: 8,
                children: [
                  titleText("Why Saying “I’m not feeling great” Sounds Softer", 540, 34),
                  bodyText("Apple Podcast · 11 分 24 秒 · 对话体材料", 520, 14),
                ],
              }),
              pill({ label: "Recommended", fill: "$--color-success", textFill: "$--color-success-foreground" }),
            ],
          }),
          vStack({
            width: 640,
            gap: 16,
            padding: 22,
            fill: "$--secondary",
            cornerRadius: 22,
            children: [
              sectionLabel("Transcript preview", 180),
              bodyText("I’m not feeling great today, so I might need to take the afternoon off. I just wanted to give you a heads-up before the meeting starts.", 596, 17, "$--foreground"),
              hStack({
                gap: 10,
                children: [
                  pill({ label: "heads-up", fill: "$--card" }),
                  pill({ label: "take the afternoon off", fill: "$--card" }),
                  pill({ label: "委婉语气", fill: "$--card" }),
                ],
              }),
            ],
          }),
          vStack({
            width: 640,
            gap: 16,
            children: [
              titleText("八步学习方案", 280, 28),
              lessonModuleRow({ label: "1 沉浸听力", desc: "先纯听 2-3 遍，建立整体语义与情绪印象。", toneFill: "$--color-success" }),
              lessonModuleRow({ label: "2 核心词汇", desc: "提取 8 个关键表达，聚焦真正会复用的口语。 " }),
              lessonModuleRow({ label: "3 Chinglish 对照", desc: "把“我会说”的表达，改写成更自然的英语。 " }),
              lessonModuleRow({ label: "4 场景映射", desc: "自动生成为老板请假、会议说明等可直接复用脚本。 " }),
              lessonModuleRow({ label: "5 听力解码", desc: "逐句标出连读 / 弱读 / T 音变化，解决听不清。", toneFill: "$--color-warning" }),
              lessonModuleRow({ label: "6 潜台词与语气", desc: "理解为什么这句话“软”，以及它实际传递的关系感。 " }),
              lessonModuleRow({ label: "7 句型拆解", desc: "抽出骨架句，支持快速换词迁移。 " }),
              lessonModuleRow({ label: "8 输出练习", desc: "最后用写作或对话把这节课真正学会。", toneFill: "$--color-info" }),
            ],
          }),
        ],
      }),
      vStack({
        x: 1088,
        y: 348,
        width: 288,
        height: 848,
        gap: 18,
        children: [
          insightsCard({
            title: "关键表达",
            items: [
              "call in sick: 正式且自然的“请病假”说法",
              "give you a heads-up: 提前打个招呼",
              "not feeling great: 比 “I’m sick” 更委婉",
            ],
            height: 244,
          }),
          insightsCard({
            title: "语音现象",
            items: [
              "not feeling → /na fiːlɪŋ/",
              "might need to → /mai niːdə/",
              "heads-up → 连读后更像一个词块",
            ],
            height: 244,
            fill: "$--secondary",
          }),
          insightsCard({
            title: "建议先学",
            items: [
              "先看第 5 模块，解决“明明认识却没听出来”的核心障碍。",
              "完成后进入第 4 模块，把请假表达迁移到自己的工作语境。",
              "最后做一封请假邮件输出，形成完整闭环。",
            ],
            height: 324,
          }),
        ],
      }),
    ],
  });

const moduleItem = ({ index, title, subtitle, active = false }) =>
  hStack({
    width: 224,
    gap: 12,
    padding: [14, 14],
    alignItems: "center",
    fill: active ? "$--primary" : "#00000000",
    stroke: active ? undefined : { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 18,
    children: [
      counterBubble({
        label: index,
        fill: active ? "#ffffff22" : "$--secondary",
        textFill: active ? "$--primary-foreground" : "$--foreground",
      }),
      vStack({
        width: 164,
        gap: 4,
        children: [
          text({
            width: 164,
            content: `${index}. ${title}`,
            fill: active ? "$--primary-foreground" : "$--foreground",
            textGrowth: "fixed-width",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "600",
            lineHeight: 1.2,
          }),
          text({
            width: 164,
            content: subtitle,
            fill: active ? "$--primary-foreground" : "$--muted-foreground",
            textGrowth: "fixed-width",
            fontFamily: "$--font-secondary",
            fontSize: 12,
            fontWeight: "normal",
            lineHeight: 1.25,
            opacity: active ? 0.82 : 1,
          }),
        ],
      }),
    ],
  });

const coachCard = ({ title, body, tags = [], height = 220 }) =>
  vStack({
    width: 280,
    height,
    gap: 16,
    padding: 22,
    fill: "$--card",
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 24,
    children: [
      titleText(title, 236, 26),
      bodyText(body, 236, 14, "$--foreground"),
      tags.length
        ? hStack({
            width: 236,
            gap: 8,
            children: tags.map((tag) => pill({ label: tag, fill: "$--secondary" })),
          })
        : undefined,
    ].filter(Boolean),
  });

const makeWorkspaceScreen = (x, y) =>
  appScreen({
    name: "LingMate / Workspace",
    x,
    y,
    height: 1280,
    children: [
      appHeader({ subtitle: "Eight-step listening workspace", primaryAction: "完成本课" }),
      hStack({
        x: 64,
        y: 120,
        width: 1312,
        justifyContent: "space_between",
        alignItems: "end",
        children: [
          vStack({
            gap: 12,
            children: [
              sectionLabel("Lesson 12 · Listening Decoder", 240),
              titleText("听力解码：把真正“听见”的声音还原出来", 760, 46),
            ],
          }),
          hStack({
            gap: 10,
            children: [
              pill({ label: "第 5 / 8 模块", fill: "$--secondary" }),
              pill({ label: "11m 24s material", fill: "$--secondary" }),
            ],
          }),
        ],
      }),
      vStack({
        x: 64,
        y: 220,
        width: 272,
        height: 1000,
        gap: 18,
        children: [
          vStack({
            width: 272,
            height: 154,
            gap: 12,
            padding: 22,
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 24,
            children: [
              sectionLabel("Current material", 180),
              titleText("Soft language at work", 228, 26),
              bodyText("你将会学会：委婉请假、语气减压、真实连读。", 228, 14),
            ],
          }),
          vStack({
            width: 272,
            height: 828,
            gap: 12,
            padding: 18,
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 24,
            children: [
              ...[
                ["1", "沉浸听力", "先只用耳朵感受语速"],
                ["2", "核心词汇", "抓住真正重要的表达"],
                ["3", "Chinglish 对照", "找到更自然的说法"],
                ["4", "场景映射", "迁移到自己的生活语境"],
                ["5", "听力解码", "看到声音如何变化", true],
                ["6", "潜台词与语气", "理解关系与态度"],
                ["7", "句型拆解", "抽出骨架句型"],
                ["8", "输出练习", "最后真正开口或动笔"],
              ].map(([index, title, subtitle, active]) =>
                moduleItem({ index, title, subtitle, active }),
              ),
            ],
          }),
        ],
      }),
      vStack({
        x: 360,
        y: 220,
        width: 712,
        height: 1000,
        gap: 24,
        children: [
          vStack({
            width: 712,
            height: 620,
            gap: 22,
            padding: 28,
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 28,
            children: [
              hStack({
                width: 656,
                justifyContent: "space_between",
                alignItems: "center",
                children: [
                  titleText("Module 5 · Listening Decoder", 380, 30),
                  hStack({
                    gap: 8,
                    children: [
                      pill({ label: "0.85x", fill: "$--secondary" }),
                      pill({ label: "Loop sentence", fill: "$--secondary" }),
                    ],
                  }),
                ],
              }),
              hStack({
                width: 656,
                gap: 14,
                alignItems: "center",
                children: [
                  hStack({
                    width: 46,
                    height: 46,
                    justifyContent: "center",
                    alignItems: "center",
                    fill: "$--primary",
                    cornerRadius: 999,
                    children: [
                      icon({
                        iconFontName: "play_arrow",
                        width: 20,
                        height: 20,
                        fill: "$--primary-foreground",
                      }),
                    ],
                  }),
                  progressTrack({ width: 596, valueWidth: 214 }),
                ],
              }),
              vStack({
                width: 656,
                gap: 12,
                padding: 22,
                fill: "$--secondary",
                cornerRadius: 22,
                children: [
                  sectionLabel("原句", 80),
                  titleText("I’m not feeling great today, so I might need to take the afternoon off.", 612, 34),
                ],
              }),
              vStack({
                width: 656,
                gap: 14,
                padding: 22,
                fill: "$--sage-soft",
                cornerRadius: 22,
                children: [
                  sectionLabel("实际听起来像", 120),
                  titleText("I’m na feeling great today, so I ma needa take the afternoon off.", 612, 30, "$--foreground"),
                  hStack({
                    width: 612,
                    gap: 10,
                    children: [
                      pill({ label: "not → na", fill: "$--card" }),
                      pill({ label: "might need to → ma needa", fill: "$--card" }),
                      pill({ label: "弱读", fill: "$--card" }),
                    ],
                  }),
                ],
              }),
              hStack({
                width: 656,
                gap: 12,
                children: [
                  button({ label: "回放整句", variant: "outline", width: 152 }),
                  button({ label: "逐词跟读", variant: "outline", width: 152 }),
                  button({ label: "进入场景迁移", variant: "primary", width: 212, iconName: "arrow_forward" }),
                ],
              }),
            ],
          }),
          hStack({
            width: 712,
            gap: 24,
            children: [
              vStack({
                width: 344,
                height: 356,
                gap: 16,
                padding: 24,
                fill: "$--card",
                stroke: { align: "inside", thickness: 1, fill: "$--border" },
                cornerRadius: 24,
                children: [
                  titleText("为什么这里会听不出", 296, 26),
                  bodyText("这句的难点不在单词，而在连续语流下的弱读和黏连。LingMate 会把“视觉上的文字”重新翻译成“耳朵里的声音”。", 296, 14, "$--foreground"),
                  ...[
                    "not feeling: /t/ 被吞弱，重心落在 feeling",
                    "might need to: 三词连成一块，实际节奏被压缩",
                    "afternoon off: 语块边界模糊，更像一个整体",
                  ].map((item) =>
                    hStack({
                      width: 296,
                      gap: 12,
                      alignItems: "start",
                      children: [
                        rect({ width: 8, height: 8, fill: "$--primary", cornerRadius: 999, y: 6 }),
                        text({
                          width: 276,
                          content: item,
                          fill: "$--foreground",
                          textGrowth: "fixed-width",
                          fontFamily: "$--font-secondary",
                          fontSize: 14,
                          fontWeight: "500",
                          lineHeight: 1.45,
                        }),
                      ],
                    }),
                  ),
                ],
              }),
              vStack({
                width: 344,
                height: 356,
                gap: 16,
                padding: 24,
                fill: "$--card",
                stroke: { align: "inside", thickness: 1, fill: "$--border" },
                cornerRadius: 24,
                children: [
                  titleText("跟读反馈", 296, 26),
                  hStack({
                    width: 296,
                    justifyContent: "space_between",
                    alignItems: "center",
                    children: [
                      titleText("82 / 100", 170, 40, "$--primary"),
                      pill({ label: "再来一遍", fill: "$--color-warning", textFill: "$--color-warning-foreground" }),
                    ],
                  }),
                  bodyText("节奏基本对，但 “might need to” 还不够黏连。先模仿气口，再管每个字的饱满度。", 296, 14, "$--foreground"),
                  rect({ width: 296, height: 1, fill: "$--border" }),
                  bodyText("教练提示：先读成 “ma needa”，再慢慢回到标准形式，你会更容易记住真实语流。", 296, 14),
                ],
              }),
            ],
          }),
        ],
      }),
      vStack({
        x: 1096,
        y: 220,
        width: 280,
        height: 1000,
        gap: 16,
        children: [
          coachCard({
            title: "AI coach note",
            body: "你不是词不认识，而是语块还没形成。今天先把一整句听成三个稳定块，再去做输出。",
            tags: ["语块感", "先整体后细节"],
            height: 220,
          }),
          coachCard({
            title: "核心词",
            body: "call in sick / heads-up / take the afternoon off / not feeling great",
            tags: ["B1-B2", "职场高频"],
            height: 260,
          }),
          coachCard({
            title: "今日目标",
            body: "完成 5-6 模块，确保不仅听懂字面，也听懂语气轻重。",
            tags: ["25 分钟", "完成后自动生成报告"],
            height: 220,
          }),
          coachCard({
            title: "本课进度",
            body: "已学习 37 分钟，4 个模块完成。接下来建议：潜台词与语气。",
            tags: ["4 / 8 modules", "继续保持"],
            height: 252,
          }),
        ],
      }),
    ],
  });

const chartBar = ({ label, value, color = "$--primary", width = 320 }) =>
  vStack({
    width,
    gap: 8,
    children: [
      hStack({
        width,
        justifyContent: "space_between",
        children: [
          text({
            content: label,
            fill: "$--foreground",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "500",
            lineHeight: 1.2,
          }),
          text({
            content: value,
            fill: "$--muted-foreground",
            fontFamily: "$--font-secondary",
            fontSize: 13,
            fontWeight: "500",
            lineHeight: 1.2,
          }),
        ],
      }),
      progressTrack({
        width,
        valueWidth: Math.round(width * Number(value.replace("%", "")) / 100),
        foreground: color,
      }),
    ],
  });

const weeklyBar = ({ day, height, fill }) =>
  vStack({
    width: 72,
    height: 220,
    justifyContent: "end",
    alignItems: "center",
    gap: 10,
    children: [
      rect({ width: 40, height, fill, cornerRadius: 14 }),
      text({
        content: day,
        fill: "$--muted-foreground",
        fontFamily: "$--font-secondary",
        fontSize: 12,
        fontWeight: "500",
        lineHeight: 1,
      }),
    ],
  });

const queueRow = ({ title, meta, fill = "$--card" }) =>
  hStack({
    width: 436,
    gap: 14,
    padding: [16, 16],
    alignItems: "center",
    fill,
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 18,
    children: [
      counterBubble({ label: "R", size: 40 }),
      vStack({
        width: 260,
        gap: 4,
        children: [
          text({
            width: 260,
            content: title,
            fill: "$--foreground",
            textGrowth: "fixed-width",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "600",
            lineHeight: 1.25,
          }),
          text({
            width: 260,
            content: meta,
            fill: "$--muted-foreground",
            textGrowth: "fixed-width",
            fontFamily: "$--font-secondary",
            fontSize: 12,
            fontWeight: "normal",
            lineHeight: 1.25,
          }),
        ],
      }),
      pill({ label: "复习", fill: "$--secondary" }),
    ],
  });

const makeReviewScreen = (x, y) =>
  appScreen({
    name: "LingMate / Review",
    x,
    y,
    height: 1340,
    children: [
      appHeader({ subtitle: "Report and spaced review", primaryAction: "查看周报" }),
      hStack({
        x: 64,
        y: 124,
        width: 1312,
        height: 280,
        gap: 24,
        padding: 28,
        fill: "$--card",
        stroke: { align: "inside", thickness: 1, fill: "$--border" },
        cornerRadius: 28,
        children: [
          vStack({
            width: 724,
            gap: 14,
            justifyContent: "center",
            children: [
              sectionLabel("This week", 140),
              titleText("从“听懂一点点”，进入真正会迁移的学习闭环", 700, 46),
              bodyText("报告页不只展示学习时长，而是把本周新掌握表达、薄弱点变化和下一轮复习节奏串成一个更安心的网页端学习节奏。", 680, 17),
              hStack({
                gap: 12,
                children: [
                  button({ label: "开始今日复习", variant: "primary", iconName: "arrow_forward" }),
                  button({ label: "导出精听笔记", variant: "outline" }),
                ],
              }),
            ],
          }),
          hStack({
            width: 508,
            gap: 14,
            children: [
              metricCard({ title: "本周精听时长", value: "6.2h", note: "较上周 +18%，学习节奏更稳定。", width: 160 }),
              metricCard({ title: "新增表达", value: "26", note: "其中 12 条已进入复习队列。", width: 160 }),
              metricCard({ title: "平均完成模块", value: "6.1", note: "最常完成到输出练习。", width: 160 }),
            ],
          }),
        ],
      }),
      vStack({
        x: 64,
        y: 428,
        width: 804,
        height: 828,
        gap: 24,
        children: [
          vStack({
            width: 804,
            height: 460,
            gap: 18,
            padding: 24,
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 26,
            children: [
              hStack({
                width: 756,
                justifyContent: "space_between",
                alignItems: "center",
                children: [
                  titleText("薄弱点正在往上走", 320, 30),
                  pill({ label: "vs. 上周", fill: "$--secondary" }),
                ],
              }),
              hStack({
                width: 756,
                gap: 28,
                children: [
                  vStack({
                    width: 356,
                    gap: 18,
                    children: [
                      chartBar({ label: "词汇掌握", value: "78%" }),
                      chartBar({ label: "连读弱读识别", value: "64%", color: "$--color-warning-foreground" }),
                      chartBar({ label: "句式理解", value: "73%" }),
                      chartBar({ label: "语用感知", value: "58%", color: "$--color-error-foreground" }),
                      chartBar({ label: "输出能力", value: "61%", color: "$--primary" }),
                    ],
                  }),
                  vStack({
                    width: 372,
                    gap: 14,
                    children: [
                      sectionLabel("Weekly listening hours", 200),
                      hStack({
                        width: 372,
                        height: 240,
                        justifyContent: "space_between",
                        alignItems: "end",
                        children: [
                          weeklyBar({ day: "Mon", height: 96, fill: "$--secondary" }),
                          weeklyBar({ day: "Tue", height: 122, fill: "$--secondary" }),
                          weeklyBar({ day: "Wed", height: 148, fill: "$--primary" }),
                          weeklyBar({ day: "Thu", height: 110, fill: "$--secondary" }),
                          weeklyBar({ day: "Fri", height: 172, fill: "$--primary" }),
                        ],
                      }),
                      bodyText("周三和周五进入了更深的专注状态，完成了 5-8 模块。下周继续保持 20-30 分钟的完整精听块。", 372, 14),
                    ],
                  }),
                ],
              }),
            ],
          }),
          vStack({
            width: 804,
            height: 344,
            gap: 16,
            padding: 24,
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 26,
            children: [
              titleText("学习闭环记录", 240, 28),
              ...[
                ["03/24", "完成播客材料《Soft language at work》", "关键突破：委婉语气 + 连读识别"],
                ["03/26", "复习表达 give you a heads-up", "已在新材料中再次遇到并正确理解"],
                ["03/28", "输出练习：请假邮件", "用上了 call in sick / not feeling great / heads-up"],
              ].map(([date, title, note], index) =>
                hStack({
                  width: 756,
                  gap: 18,
                  padding: [12, 0],
                  alignItems: "start",
                  stroke: index < 2 ? { align: "inside", thickness: { bottom: 1 }, fill: "$--border" } : undefined,
                  children: [
                    text({
                      width: 86,
                      content: date,
                      fill: "$--muted-foreground",
                      fontFamily: "$--font-secondary",
                      fontSize: 13,
                      fontWeight: "600",
                      lineHeight: 1.4,
                    }),
                    vStack({
                      width: 650,
                      gap: 4,
                      children: [
                        text({
                          width: 650,
                          content: title,
                          fill: "$--foreground",
                          textGrowth: "fixed-width",
                          fontFamily: "$--font-secondary",
                          fontSize: 15,
                          fontWeight: "600",
                          lineHeight: 1.4,
                        }),
                        text({
                          width: 650,
                          content: note,
                          fill: "$--muted-foreground",
                          textGrowth: "fixed-width",
                          fontFamily: "$--font-secondary",
                          fontSize: 14,
                          fontWeight: "normal",
                          lineHeight: 1.4,
                        }),
                      ],
                    }),
                  ],
                }),
              ),
            ],
          }),
        ],
      }),
      vStack({
        x: 892,
        y: 428,
        width: 484,
        height: 890,
        gap: 24,
        children: [
          vStack({
            width: 484,
            height: 396,
            gap: 16,
            padding: 24,
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 26,
            children: [
              hStack({
                width: 436,
                justifyContent: "space_between",
                alignItems: "center",
                children: [
                  titleText("今日复习队列", 220, 28),
                  pill({ label: "Ebbinghaus", fill: "$--secondary" }),
                ],
              }),
              ...[
                ["call in sick", "第 3 天 · 需要在新场景中再用一次"],
                ["give you a heads-up", "第 7 天 · 适合做口语复述"],
                ["under the weather", "第 14 天 · 已掌握，但建议继续复现"],
                ["sort of / kind of", "第 1 天 · 连读识别还不稳定"],
              ].map(([title, meta], index) =>
                queueRow({
                  title,
                  meta,
                  fill: index === 0 ? "$--secondary" : "$--card",
                }),
              ),
            ],
          }),
          vStack({
            width: 484,
            height: 470,
            gap: 18,
            padding: 24,
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 26,
            children: [
              titleText("精听笔记卡", 220, 28),
              vStack({
                width: 436,
                gap: 14,
                padding: 22,
                fill: "$--secondary",
                cornerRadius: 22,
                children: [
                  sectionLabel("Shareable note", 140),
                  titleText("每一句，都陪你听懂", 392, 34),
                  bodyText("本次材料：Soft language at work\n掌握表达：call in sick / give you a heads-up / not feeling great\n完成模块：6 / 8", 392, 14, "$--foreground"),
                  hStack({
                    gap: 10,
                    children: [
                      pill({ label: "委婉语气", fill: "$--card" }),
                      pill({ label: "商务场景", fill: "$--card" }),
                      pill({ label: "连读解码", fill: "$--card" }),
                    ],
                  }),
                ],
              }),
              bodyText("这张卡可以作为社交裂变素材，也能成为用户自己愿意保存的学习记忆点。", 436, 14),
              hStack({
                gap: 12,
                children: [
                  button({ label: "分享学习卡", variant: "primary", width: 170 }),
                  button({ label: "查看月报", variant: "outline", width: 140 }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  });

const document = {
  version: "2.9",
  children: [
    frame(
      {
        id: uid("canvas"),
        x: 0,
        y: 0,
        name: "LingMate Web Prototype Canvas",
        clip: true,
        width: 3240,
        height: 2920,
        fill: "$--canvas",
        layout: "none",
      },
      [
        topLabel({ index: "01", name: "Home / Import", x: 120, y: 68 }),
        topLabel({ index: "02", name: "AI Analysis", x: 1680, y: 68 }),
        topLabel({ index: "03", name: "Learning Workspace", x: 120, y: 1448 }),
        topLabel({ index: "04", name: "Report / Review", x: 1680, y: 1448 }),
        makeHomeScreen(120, 120),
        makeAnalysisScreen(1680, 120),
        makeWorkspaceScreen(120, 1500),
        makeReviewScreen(1680, 1500),
      ],
    ),
  ],
  variables: {
    "--canvas": { type: "color", value: "#ECE7DD" },
    "--background": { type: "color", value: "#F7F3EA" },
    "--card": { type: "color", value: "#FBF8F2" },
    "--secondary": { type: "color", value: "#ECE5D9" },
    "--secondary-foreground": { type: "color", value: "#21352D" },
    "--foreground": { type: "color", value: "#21352D" },
    "--muted-foreground": { type: "color", value: "#6E776E" },
    "--primary": { type: "color", value: "#315F4C" },
    "--primary-foreground": { type: "color", value: "#F8F5EE" },
    "--border": { type: "color", value: "#D9D1C4" },
    "--input": { type: "color", value: "#D9D1C4" },
    "--sage-soft": { type: "color", value: "#DFE7DD" },
    "--sand-soft": { type: "color", value: "#E7DDCC" },
    "--color-success": { type: "color", value: "#DEE8DE" },
    "--color-success-foreground": { type: "color", value: "#2F5C49" },
    "--color-warning": { type: "color", value: "#EADFCB" },
    "--color-warning-foreground": { type: "color", value: "#8A6520" },
    "--color-error": { type: "color", value: "#E7DDD7" },
    "--color-error-foreground": { type: "color", value: "#8F432A" },
    "--color-info": { type: "color", value: "#E5EAE4" },
    "--color-info-foreground": { type: "color", value: "#315F4C" },
    "--white": { type: "color", value: "#FFFFFF" },
    "--font-primary": { type: "string", value: "Songti SC" },
    "--font-secondary": { type: "string", value: "PingFang SC" },
    "--radius-none": { type: "number", value: 0 },
    "--radius-m": { type: "number", value: 18 },
    "--radius-pill": { type: "number", value: 999 },
  },
};

const outputPath = path.join(process.cwd(), "LingMate_web_prototype.pen");
fs.writeFileSync(outputPath, `${JSON.stringify(clean(document), null, 2)}\n`);
console.log(`Wrote ${outputPath}`);
