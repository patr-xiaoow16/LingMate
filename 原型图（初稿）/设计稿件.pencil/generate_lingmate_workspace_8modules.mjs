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

const shadow = (opacity = "18", blur = 40, y = 20) => ({
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

const sectionLabel = (content, width = 240, fill = "$--muted-foreground") =>
  text({
    width,
    content,
    fill,
    textGrowth: "fixed-width",
    fontFamily: "$--font-secondary",
    fontSize: 13,
    fontWeight: "600",
    lineHeight: 1.15,
  });

const bodyText = (content, width, size = 14, fill = "$--muted-foreground") =>
  text({
    width,
    content,
    fill,
    textGrowth: "fixed-width",
    fontFamily: "$--font-secondary",
    fontSize: size,
    fontWeight: "normal",
    lineHeight: 1.55,
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
  const palette =
    variant === "primary"
      ? { fill: "$--primary", textFill: "$--primary-foreground", stroke: undefined }
      : variant === "soft"
        ? { fill: "$--secondary", textFill: "$--foreground", stroke: undefined }
        : {
            fill: "#00000000",
            textFill: "$--foreground",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
          };

  return hStack({
    width,
    height: 46,
    gap: 8,
    padding: [12, 18],
    fill: palette.fill,
    stroke: palette.stroke,
    cornerRadius: "$--radius-pill",
    justifyContent: "center",
    alignItems: "center",
    children: [
      text({
        content: label,
        fill: palette.textFill,
        fontFamily: "$--font-secondary",
        fontSize: 14,
        fontWeight: "600",
        lineHeight: 1,
      }),
      iconName ? icon({ iconFontName: iconName, width: 16, height: 16, fill: palette.textFill }) : undefined,
    ].filter(Boolean),
  });
};

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

const mainCard = ({ title, subtitle, height = 640, children = [], pills = [] }) =>
  vStack({
    width: 712,
    height,
    gap: 18,
    padding: 28,
    fill: "$--card",
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 28,
    children: [
      hStack({
        width: 656,
        justifyContent: "space_between",
        alignItems: "start",
        children: [
          vStack({
            width: 430,
            gap: 8,
            children: [
              titleText(title, 430, 30),
              subtitle ? bodyText(subtitle, 430, 14) : undefined,
            ].filter(Boolean),
          }),
          pills.length
            ? hStack({
                gap: 8,
                children: pills,
              })
            : undefined,
        ].filter(Boolean),
      }),
      ...children,
    ],
  });

const subCard = ({ title, height = 356, children = [] }) =>
  vStack({
    width: 344,
    height,
    gap: 16,
    padding: 24,
    fill: "$--card",
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 24,
    children: [
      titleText(title, 296, 24),
      ...children,
    ],
  });

const chipRow = (items, fill = "$--secondary") =>
  hStack({
    gap: 8,
    children: items.map((item) => pill({ label: item, fill })),
  });

const listBullet = (content, color = "$--primary", width = 296) =>
  hStack({
    width,
    gap: 12,
    alignItems: "start",
    children: [
      rect({ width: 8, height: 8, fill: color, cornerRadius: 999, y: 6 }),
      text({
        width: width - 20,
        content,
        fill: "$--foreground",
        textGrowth: "fixed-width",
        fontFamily: "$--font-secondary",
        fontSize: 14,
        fontWeight: "500",
        lineHeight: 1.45,
      }),
    ],
  });

const simpleRow = ({ label, meta, tone = "$--secondary", width = 232 }) =>
  hStack({
    width,
    gap: 12,
    padding: [12, 14],
    alignItems: "center",
    fill: tone,
    cornerRadius: 16,
    children: [
      rect({ width: 8, height: 8, fill: "$--primary", cornerRadius: 999 }),
      text({
        width: width - 118,
        content: label,
        fill: "$--foreground",
        textGrowth: "fixed-width",
        fontFamily: "$--font-secondary",
        fontSize: 13,
        fontWeight: "600",
        lineHeight: 1.25,
      }),
      pill({ label: meta, fill: "$--card" }),
    ],
  });

const questionRow = (content, width = 296) =>
  hStack({
    width,
    gap: 10,
    padding: [12, 14],
    fill: "$--secondary",
    cornerRadius: 16,
    alignItems: "center",
    children: [
      counterBubble({ label: "?", size: 28 }),
      text({
        width: width - 52,
        content,
        fill: "$--foreground",
        textGrowth: "fixed-width",
        fontFamily: "$--font-secondary",
        fontSize: 13,
        fontWeight: "500",
        lineHeight: 1.3,
      }),
    ],
  });

const coachCard = ({ title, body, tags = [], accent = "$--primary", height = 220 }) =>
  vStack({
    width: 280,
    height,
    gap: 14,
    padding: 22,
    fill: "$--card",
    stroke: { align: "inside", thickness: 1, fill: "$--border" },
    cornerRadius: 24,
    children: [
      hStack({
        width: 236,
        justifyContent: "space_between",
        alignItems: "center",
        children: [
          titleText(title, 184, 24),
          rect({ width: 10, height: 10, fill: accent, cornerRadius: 999 }),
        ],
      }),
      bodyText(body, 236, 13, "$--foreground"),
      tags.length
        ? hStack({
            width: 236,
            gap: 8,
            children: tags.map((tag) => pill({ label: tag, fill: "$--secondary" })),
          })
        : undefined,
    ].filter(Boolean),
  });

const moduleNames = [
  "沉浸听力",
  "核心词汇",
  "Chinglish 对照",
  "场景映射",
  "听力解码",
  "潜台词与语气",
  "句型拆解",
  "输出练习",
];

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
        label: String(index),
        fill: active ? "#ffffff22" : "$--secondary",
        textFill: active ? "$--primary-foreground" : "$--foreground",
      }),
      vStack({
        width: 164,
        gap: 4,
        children: [
          text({
            width: 164,
            content: title,
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

const appHeader = ({ subtitle, primaryAction = "继续学习" }) =>
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
        gap: 24,
        alignItems: "center",
        children: [
          text({
            content: "工作台",
            fill: "$--muted-foreground",
            fontFamily: "$--font-secondary",
            fontSize: 14,
            fontWeight: "500",
            lineHeight: 1,
          }),
          text({
            content: "词汇本",
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
          button({ label: primaryAction, variant: "primary", iconName: "arrow_forward" }),
        ],
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

const workspaceSidebar = (activeIndex) =>
  vStack({
    x: 64,
    y: 220,
    width: 272,
    height: 1020,
    gap: 18,
    children: [
      vStack({
        width: 272,
        height: 214,
        gap: 12,
        padding: 22,
        fill: "$--card",
        stroke: { align: "inside", thickness: 1, fill: "$--border" },
        cornerRadius: 24,
        children: [
          sectionLabel("Current material", 180),
          titleText("Soft language at work", 228, 24),
          bodyText("本课围绕请假、委婉表达与职场口语展开。", 228, 14),
          chipRow(["B1-B2", "11m 24s"]),
        ],
      }),
      vStack({
        width: 272,
        height: 768,
        gap: 12,
        padding: 18,
        fill: "$--card",
        stroke: { align: "inside", thickness: 1, fill: "$--border" },
        cornerRadius: 24,
        children: moduleNames.map((name, index) =>
          moduleItem({
            index: index + 1,
            title: name,
            subtitle:
              index === 0
                ? "先感受语速与情绪"
                : index === 1
                  ? "抓住高价值表达"
                  : index === 2
                    ? "找到更自然的说法"
                    : index === 3
                      ? "迁移到真实场景"
                      : index === 4
                        ? "把声音拆开看清"
                        : index === 5
                          ? "理解关系与态度"
                          : index === 6
                            ? "抽出句型骨架"
                            : "把所学真正用出来",
            active: activeIndex === index + 1,
          }),
        ),
      }),
    ],
  });

const workspaceHeader = (index, title, desc) =>
  hStack({
    x: 64,
    y: 120,
    width: 1312,
    justifyContent: "space_between",
    alignItems: "end",
    children: [
      vStack({
        gap: 10,
        children: [
          sectionLabel(`Learning Workspace · Module ${index}`, 260),
          titleText(title, 760, 42),
          bodyText(desc, 760, 15),
        ],
      }),
      hStack({
        gap: 8,
        children: [
          pill({ label: `第 ${index} / 8 模块`, fill: "$--secondary" }),
          pill({ label: "AI guided", fill: "$--secondary" }),
        ],
      }),
    ],
  });

const accentPanel = ({ label, content, fill = "$--secondary", width = 656 }) =>
  vStack({
    width,
    gap: 12,
    padding: 22,
    fill,
    cornerRadius: 22,
    children: [
      sectionLabel(label, 160, "$--muted-foreground"),
      bodyText(content, width - 44, 16, "$--foreground"),
    ],
  });

const pairCompareRow = ({ wrong, right, note }) =>
  vStack({
    width: 656,
    gap: 10,
    children: [
      hStack({
        width: 656,
        gap: 12,
        children: [
          vStack({
            width: 300,
            gap: 8,
            padding: 18,
            fill: "$--color-error",
            cornerRadius: 20,
            children: [
              sectionLabel("我可能会这样说", 160, "$--color-error-foreground"),
              bodyText(wrong, 260, 15, "$--foreground"),
            ],
          }),
          vStack({
            width: 344,
            gap: 8,
            padding: 18,
            fill: "$--color-success",
            cornerRadius: 20,
            children: [
              sectionLabel("更自然的表达", 160, "$--color-success-foreground"),
              bodyText(right, 300, 15, "$--foreground"),
            ],
          }),
        ],
      }),
      bodyText(note, 656, 13),
    ],
  });

const expressionRow = ({ phrase, cefr, status }) =>
  hStack({
    width: 236,
    gap: 10,
    padding: [12, 12],
    justifyContent: "space_between",
    alignItems: "center",
    fill: status === "selected" ? "$--primary" : "$--secondary",
    cornerRadius: 16,
    children: [
      text({
        width: 130,
        content: phrase,
        fill: status === "selected" ? "$--primary-foreground" : "$--foreground",
        textGrowth: "fixed-width",
        fontFamily: "$--font-secondary",
        fontSize: 13,
        fontWeight: "600",
        lineHeight: 1.25,
      }),
      pill({
        label: cefr,
        fill: status === "selected" ? "#ffffff22" : "$--card",
        textFill: status === "selected" ? "$--primary-foreground" : "$--foreground",
      }),
    ],
  });

const inputArea = ({ label, content, width, height = 120 }) =>
  vStack({
    width,
    gap: 10,
    children: [
      sectionLabel(label, width),
      vStack({
        width,
        height,
        padding: 18,
        fill: "$--secondary",
        cornerRadius: 18,
        children: [
          bodyText(content, width - 36, 14, "$--foreground"),
        ],
      }),
    ],
  });

const buildImmersiveTop = () =>
  mainCard({
    title: "Module 1 · Immersive Listening",
    subtitle: "先不看文字，只用耳朵建立对内容、语速和情绪的整体感受。",
    pills: [pill({ label: "0.85x", fill: "$--secondary" }), pill({ label: "Listen 1/3", fill: "$--secondary" })],
    children: [
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
            children: [icon({ iconFontName: "play_arrow", width: 20, height: 20, fill: "$--primary-foreground" })],
          }),
          progressTrack({ width: 596, valueWidth: 214 }),
        ],
      }),
      accentPanel({
        label: "现在的学习任务",
        content: "请先纯听两遍，不要急着看答案。试着只抓“谁在说、情绪如何、主要发生了什么”。",
        fill: "$--secondary",
      }),
      hStack({
        width: 656,
        gap: 16,
        children: [
          vStack({
            width: 318,
            height: 236,
            gap: 14,
            padding: 20,
            fill: "$--sage-soft",
            cornerRadius: 22,
            children: [
              sectionLabel("你可能听到的感觉", 180),
              bodyText("语气偏柔和，不像直接请假，更像先铺垫自己的状态，再为后续的请假做准备。", 278, 14, "$--foreground"),
              chipRow(["soft", "hesitant", "workplace"], "$--card"),
            ],
          }),
          vStack({
            width: 322,
            height: 236,
            gap: 12,
            padding: 20,
            fill: "$--card",
            stroke: { align: "inside", thickness: 1, fill: "$--border" },
            cornerRadius: 22,
            children: [
              sectionLabel("听后快速检查", 180),
              questionRow("这段话主要是在解释计划，还是在传达状态？", 282),
              questionRow("说话人听起来更像紧张、抱歉，还是生气？", 282),
              questionRow("你大概听到了哪些高频词块？", 282),
            ],
          }),
        ],
      }),
      hStack({
        width: 656,
        gap: 12,
        children: [
          button({ label: "再听一遍", variant: "outline", width: 144 }),
          button({ label: "进入核心词汇", variant: "primary", width: 184, iconName: "arrow_forward" }),
        ],
      }),
    ],
  });

const buildImmersiveLeft = () =>
  subCard({
    title: "大意理解检查",
    children: [
      bodyText("在不看文本的前提下，只做低负担的“整体理解”。", 296, 14, "$--foreground"),
      questionRow("谁更可能是说话对象？老板 / 同事 / 朋友", 296),
      questionRow("这段内容更接近请假沟通，还是情绪吐槽？", 296),
      questionRow("你听到的是完整请求，还是一种提前铺垫？", 296),
    ],
  });

const buildImmersiveRight = () =>
  subCard({
    title: "听后反思",
    children: [
      bodyText("本模块不追求逐词正确，而是建立整体耳感。", 296, 14, "$--foreground"),
      simpleRow({ label: "已完成纯听", meta: "2 遍", width: 296 }),
      simpleRow({ label: "推荐继续", meta: "核心词汇", tone: "$--color-success", width: 296 }),
      chipRow(["先整体", "后细节", "低压力"]),
      button({ label: "继续下一步", variant: "primary", width: 160, iconName: "arrow_forward" }),
    ],
  });

const buildVocabularyTop = () =>
  mainCard({
    title: "Module 2 · Vocabulary Deep Dive",
    subtitle: "聚焦真正会复用的 5-8 个表达，而不是一张长长的生词表。",
    pills: [pill({ label: "8 expressions", fill: "$--secondary" })],
    children: [
      hStack({
        width: 656,
        gap: 18,
        children: [
          vStack({
            width: 236,
            gap: 10,
            children: [
              expressionRow({ phrase: "call in sick", cefr: "B1", status: "selected" }),
              expressionRow({ phrase: "heads-up", cefr: "B2" }),
              expressionRow({ phrase: "not feeling great", cefr: "B1" }),
              expressionRow({ phrase: "take the afternoon off", cefr: "B2" }),
              expressionRow({ phrase: "might need to", cefr: "A2" }),
            ],
          }),
          vStack({
            width: 402,
            gap: 14,
            padding: 20,
            fill: "$--secondary",
            cornerRadius: 24,
            children: [
              titleText("call in sick", 340, 34),
              bodyText("正式、自然的“打电话请病假”。比直接说 I’m sick 更接近职场真实语境。", 362, 14, "$--foreground"),
              chipRow(["正式一点", "职场高频", "可直接套用"], "$--card"),
              bodyText("例句 1：I need to call in sick today.\n例句 2：She called in sick before the morning stand-up.", 362, 14),
              hStack({
                width: 362,
                gap: 12,
                children: [
                  button({ label: "回听原句", variant: "outline", width: 140 }),
                  button({ label: "加入词汇本", variant: "soft", width: 140 }),
                ],
              }),
            ],
          }),
        ],
      }),
      inputArea({
        label: "试着自己造句",
        content: "I called in sick because I was feeling under the weather this morning.",
        width: 656,
        height: 92,
      }),
      pill({ label: "AI 建议：表达自然，可再试一次更口语的版本", fill: "$--color-success", textFill: "$--color-success-foreground" }),
    ],
  });

const buildVocabularyLeft = () =>
  subCard({
    title: "为什么是这些词",
    children: [
      bodyText("LingMate 优先提取高频、可迁移、且与你当前水平相关的表达。", 296, 14, "$--foreground"),
      listBullet("不是每个生词都值得学，但这些表达会在职场、播客和日常口语里反复出现。"),
      listBullet("系统会结合你过往薄弱点，优先展示你“看过但不会用”的词块。"),
      listBullet("点击回听原句，能把词和语音、语气重新绑在一起。"),
    ],
  });

const buildVocabularyRight = () =>
  subCard({
    title: "掌握状态",
    children: [
      simpleRow({ label: "已掌握", meta: "3", tone: "$--color-success", width: 296 }),
      simpleRow({ label: "需复习", meta: "4", tone: "$--color-warning", width: 296 }),
      simpleRow({ label: "待造句", meta: "1", width: 296 }),
      bodyText("完成造句后，系统会自动同步到个人词汇本，并安排复习时间点。", 296, 14),
      button({ label: "进入 Chinglish 对照", variant: "primary", width: 210, iconName: "arrow_forward" }),
    ],
  });

const buildChinglishTop = () =>
  mainCard({
    title: "Module 3 · Native vs Chinglish",
    subtitle: "把“我会怎么说”与“母语者更自然的说法”放在一起看，差异会立刻变清楚。",
    pills: [pill({ label: "4 pairs", fill: "$--secondary" })],
    children: [
      pairCompareRow({
        wrong: "I have a little sick today.",
        right: "I’m not feeling great today.",
        note: "自然表达往往不是逐词翻译，而是从“身体状态”而不是“疾病名词”切入。",
      }),
      pairCompareRow({
        wrong: "I want to ask for a leave this afternoon.",
        right: "I might need to take the afternoon off.",
        note: "英语里经常用更软的“可能需要”来降低请求的直接度。",
      }),
      pairCompareRow({
        wrong: "I tell you first.",
        right: "I just wanted to give you a heads-up.",
        note: "heads-up 不只是“告诉你”，而是带有“提前打个招呼”的关系温度。",
      }),
    ],
  });

const buildChinglishLeft = () =>
  subCard({
    title: "为什么更自然",
    children: [
      bodyText("更自然的英语通常体现的是语气、关系和使用场景，而不仅是语法正确。", 296, 14, "$--foreground"),
      listBullet("少用中文直译的名词结构，多用状态、动作或语块。"),
      listBullet("真实口语里会主动降低语气强度，让表达更柔和、更可接受。"),
      listBullet("同一句中文，英语里会根据说给谁听而换掉整个句型。"),
    ],
  });

const buildChinglishRight = () =>
  subCard({
    title: "自己试一版",
    children: [
      inputArea({
        label: "你的版本",
        content: "I want to ask for leave because I feel not good.",
        width: 296,
        height: 100,
      }),
      pill({ label: "AI 判断：有明显 Chinglish 痕迹", fill: "$--color-warning", textFill: "$--color-warning-foreground" }),
      bodyText("建议改为：I’m not feeling great, so I might need to take the afternoon off.", 296, 14, "$--foreground"),
    ],
  });

const buildSceneTop = () =>
  mainCard({
    title: "Module 4 · Scene Mapping",
    subtitle: "把本课表达迁移到用户自己的生活、职场或学术语境里，做到“学了就能用”。",
    pills: [
      pill({ label: "职场", fill: "$--primary", textFill: "$--primary-foreground" }),
      pill({ label: "日常", fill: "$--secondary" }),
      pill({ label: "学术", fill: "$--secondary" }),
    ],
    children: [
      hStack({
        width: 656,
        gap: 16,
        children: [
          vStack({
            width: 312,
            height: 248,
            gap: 14,
            padding: 20,
            fill: "$--secondary",
            cornerRadius: 22,
            children: [
              sectionLabel("可直接复用的模板", 160),
              simpleRow({ label: "向老板请半天假", meta: "soft", width: 272 }),
              simpleRow({ label: "会议前先说明状态", meta: "neutral", width: 272 }),
              simpleRow({ label: "向同事提前打招呼", meta: "friendly", width: 272 }),
              chipRow(["何时用", "说给谁听", "语气建议"], "$--card"),
            ],
          }),
          vStack({
            width: 328,
            height: 248,
            gap: 12,
            padding: 20,
            fill: "$--sage-soft",
            cornerRadius: 22,
            children: [
              sectionLabel("为我生成一版", 140),
              bodyText("场景：我想在 stand-up 之前告诉老板自己状态不太好，下午可能需要请假。", 288, 14, "$--foreground"),
              bodyText("脚本：I’m not feeling great today, so I might need to take the afternoon off. I just wanted to give you a heads-up before the stand-up.", 288, 14),
            ],
          }),
        ],
      }),
      inputArea({
        label: "描述你自己的场景",
        content: "我想向老师说明今天状态不好，可能无法参加下午的小组讨论。",
        width: 656,
        height: 120,
      }),
      hStack({
        width: 656,
        gap: 12,
        children: [
          button({ label: "生成我的脚本", variant: "primary", width: 170 }),
          button({ label: "换成更正式语气", variant: "outline", width: 190 }),
        ],
      }),
    ],
  });

const buildSceneLeft = () =>
  subCard({
    title: "使用建议",
    children: [
      listBullet("先选场景，再选说话对象，最后决定语气软硬。"),
      listBullet("不要只背一句话，重点是学会“状态铺垫 + 请求表达 + 提前告知”的结构。"),
      listBullet("同一组表达可以迁移到请假、改期、推迟回复等更多场景。"),
    ],
  });

const buildSceneRight = () =>
  subCard({
    title: "场景迁移结果",
    children: [
      bodyText("系统已生成 3 个变体：对老板、对老师、对同学。", 296, 14, "$--foreground"),
      simpleRow({ label: "老板版本", meta: "正式", tone: "$--color-success", width: 296 }),
      simpleRow({ label: "老师版本", meta: "礼貌", width: 296 }),
      simpleRow({ label: "同学版本", meta: "轻松", width: 296 }),
      button({ label: "进入听力解码", variant: "primary", width: 180, iconName: "arrow_forward" }),
    ],
  });

const buildDecoderTop = () =>
  mainCard({
    title: "Module 5 · Listening Decoder",
    subtitle: "把“视觉上的文字”翻回“耳朵里真正听到的声音”，解决词都认识却听不出来的问题。",
    pills: [pill({ label: "0.85x", fill: "$--secondary" }), pill({ label: "Loop sentence", fill: "$--secondary" })],
    children: [
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
            children: [icon({ iconFontName: "play_arrow", width: 20, height: 20, fill: "$--primary-foreground" })],
          }),
          progressTrack({ width: 596, valueWidth: 214 }),
        ],
      }),
      accentPanel({
        label: "原句",
        content: "I’m not feeling great today, so I might need to take the afternoon off.",
      }),
      accentPanel({
        label: "实际听起来像",
        content: "I’m na feeling great today, so I ma needa take the afternoon off.",
        fill: "$--sage-soft",
      }),
      chipRow(["not → na", "might need to → ma needa", "弱读 / 黏连"], "$--card"),
      hStack({
        width: 656,
        gap: 12,
        children: [
          button({ label: "回放整句", variant: "outline", width: 150 }),
          button({ label: "逐词跟读", variant: "outline", width: 150 }),
          button({ label: "进入潜台词与语气", variant: "primary", width: 210, iconName: "arrow_forward" }),
        ],
      }),
    ],
  });

const buildDecoderLeft = () =>
  subCard({
    title: "为什么这里会听不出",
    children: [
      bodyText("难点不在词义，而在连续语流下的节奏压缩。", 296, 14, "$--foreground"),
      listBullet("not feeling: /t/ 被吞弱，重心落在 feeling"),
      listBullet("might need to: 三词黏成一块，边界几乎消失"),
      listBullet("afternoon off: 语块贴合，听起来像一个整体"),
    ],
  });

const buildDecoderRight = () =>
  subCard({
    title: "跟读反馈",
    children: [
      hStack({
        width: 296,
        justifyContent: "space_between",
        alignItems: "center",
        children: [
          titleText("82 / 100", 150, 38, "$--primary"),
          pill({ label: "再来一遍", fill: "$--color-warning", textFill: "$--color-warning-foreground" }),
        ],
      }),
      bodyText("节奏基本对，但 might need to 还不够黏连。先模仿气口，再管每个词是否饱满。", 296, 14, "$--foreground"),
      chipRow(["先整体", "后单词"], "$--secondary"),
    ],
  });

const buildSubtextTop = () =>
  mainCard({
    title: "Module 6 · Subtext & Tone",
    subtitle: "理解同一句话背后的关系感、试探感和真实意图，而不只停留在字面意思。",
    pills: [pill({ label: "3 key lines", fill: "$--secondary" })],
    children: [
      hStack({
        width: 656,
        gap: 18,
        children: [
          vStack({
            width: 240,
            gap: 10,
            children: [
              simpleRow({ label: "I’m not feeling great today.", meta: "soft", tone: "$--color-success", width: 240 }),
              simpleRow({ label: "I might need to take the afternoon off.", meta: "tentative", width: 240 }),
              simpleRow({ label: "I just wanted to give you a heads-up.", meta: "considerate", tone: "$--color-info", width: 240 }),
            ],
          }),
          vStack({
            width: 398,
            gap: 14,
            padding: 20,
            fill: "$--secondary",
            cornerRadius: 24,
            children: [
              titleText("这句话真正传递的不是“病情”，而是“我在尽量礼貌地提出请求”。", 358, 28),
              chipRow(["委婉", "关系维护", "提前铺垫"], "$--card"),
              bodyText("如果直接说 I’m sick. I need leave. 信息虽然清楚，但会显得过硬。原句通过状态描述 + 模糊强度 + heads-up，把关系处理得更自然。", 358, 14, "$--foreground"),
            ],
          }),
        ],
      }),
      accentPanel({
        label: "语气对比",
        content: "I’m not feeling great today.  <  I’m really not well at all today.  <  I can’t work today.",
        fill: "$--sage-soft",
      }),
      chipRow(["软一点", "更体面", "更像真实沟通"], "$--card"),
    ],
  });

const buildSubtextLeft = () =>
  subCard({
    title: "关系与态度信号",
    children: [
      listBullet("not feeling great: 降低强度，让表达更容易被接受"),
      listBullet("might need to: 保留余地，不把请求说得太硬"),
      listBullet("heads-up: 表现出你在顾及对方节奏和安排"),
    ],
  });

const buildSubtextRight = () =>
  subCard({
    title: "理解测验",
    children: [
      questionRow("说话人是在命令式通知，还是在关系维护式沟通？", 296),
      questionRow("如果改成 I’m sick today. 会显得更强硬还是更柔和？", 296),
      questionRow("heads-up 在这里表达的是提醒、抱怨还是照顾？", 296),
    ],
  });

const buildPatternTop = () =>
  mainCard({
    title: "Module 7 · Pattern Extraction",
    subtitle: "把原句抽成骨架，掌握之后就能迁移到更多场景和表达任务里。",
    pills: [pill({ label: "3 high-value patterns", fill: "$--secondary" })],
    children: [
      vStack({
        width: 656,
        gap: 12,
        padding: 22,
        fill: "$--secondary",
        cornerRadius: 24,
        children: [
          sectionLabel("骨架句", 120),
          titleText("I might need to [do X] today.", 612, 34),
          chipRow(["take the afternoon off", "work from home", "leave a little early"], "$--card"),
        ],
      }),
      vStack({
        width: 656,
        gap: 12,
        padding: 22,
        fill: "$--sage-soft",
        cornerRadius: 24,
        children: [
          sectionLabel("再抽一层", 120),
          titleText("I just wanted to [give you X] before [event Y].", 612, 30),
          chipRow(["give you a heads-up", "let you know"], "$--card"),
        ],
      }),
      hStack({
        width: 656,
        gap: 12,
        children: [
          button({ label: "换词练习", variant: "outline", width: 150 }),
          button({ label: "生成更复杂句型", variant: "soft", width: 180 }),
        ],
      }),
    ],
  });

const buildPatternLeft = () =>
  subCard({
    title: "换词练习",
    children: [
      simpleRow({ label: "I might need to work from home today.", meta: "easy", width: 296 }),
      simpleRow({ label: "I might need to leave a little early.", meta: "easy", width: 296 }),
      simpleRow({ label: "I just wanted to let you know before class.", meta: "medium", width: 296 }),
      bodyText("先做简单替换，再让 AI 帮你合并两个句型。", 296, 14, "$--foreground"),
    ],
  });

const buildPatternRight = () =>
  subCard({
    title: "AI 句型建议",
    children: [
      bodyText("你已经会用 I might need to ...，下一步建议学会把它和原因表达串起来。", 296, 14, "$--foreground"),
      accentPanel({
        label: "推荐升级版",
        content: "I’m not feeling great, so I might need to work from home this afternoon.",
        fill: "$--secondary",
        width: 296,
      }),
    ],
  });

const buildOutputTop = () =>
  mainCard({
    title: "Module 8 · Output Challenge",
    subtitle: "学习的终点不是“我懂了”，而是“我能自己写、自己说”。",
    pills: [pill({ label: "3 tasks", fill: "$--secondary" })],
    children: [
      hStack({
        width: 656,
        gap: 18,
        children: [
          vStack({
            width: 196,
            gap: 10,
            children: [
              simpleRow({ label: "填空复述", meta: "easy", width: 196 }),
              simpleRow({ label: "请假邮件", meta: "medium", tone: "$--primary", width: 196 }),
              simpleRow({ label: "对话模拟", meta: "hard", width: 196 }),
            ],
          }),
          vStack({
            width: 442,
            gap: 14,
            children: [
              inputArea({
                label: "任务：向老板写一段请假说明",
                content: "Hi, I’m not feeling great today, so I might need to take the afternoon off. I just wanted to give you a heads-up before the stand-up.",
                width: 442,
                height: 188,
              }),
              hStack({
                width: 442,
                gap: 12,
                children: [
                  button({ label: "提交给 AI", variant: "primary", width: 150 }),
                  button({ label: "换一个任务", variant: "outline", width: 150 }),
                ],
              }),
            ],
          }),
        ],
      }),
      chipRow(["词汇是否准确", "语气是否自然", "是否符合场景"], "$--card"),
    ],
  });

const buildOutputLeft = () =>
  subCard({
    title: "评分维度",
    children: [
      simpleRow({ label: "词汇准确", meta: "86", tone: "$--color-success", width: 296 }),
      simpleRow({ label: "语法正确", meta: "82", width: 296 }),
      simpleRow({ label: "表达地道", meta: "78", tone: "$--color-warning", width: 296 }),
      simpleRow({ label: "场景适配", meta: "89", tone: "$--color-success", width: 296 }),
    ],
  });

const buildOutputRight = () =>
  subCard({
    title: "AI 反馈结果",
    children: [
      bodyText("整体表达自然，已经正确用上了 not feeling great / take the afternoon off / heads-up。", 296, 14, "$--foreground"),
      bodyText("如果想更正式一点，可以把 just wanted to 改成 wanted to let you know。", 296, 14),
      button({ label: "完成本课", variant: "primary", width: 150, iconName: "check" }),
    ],
  });

const rightColumn = (cards) =>
  vStack({
    x: 1096,
    y: 220,
    width: 280,
    height: 1020,
    gap: 16,
    children: cards,
  });

const moduleScreen = ({
  x,
  y,
  index,
  title,
  desc,
  topCard,
  leftCard,
  rightCard,
  rightCards,
}) =>
  appScreen({
    name: `Learning Workspace / ${index}`,
    x,
    y,
    children: [
      appHeader({ subtitle: `Learning workspace · module ${index}`, primaryAction: index === 8 ? "完成整课" : "继续下一步" }),
      workspaceHeader(index, title, desc),
      workspaceSidebar(index),
      vStack({
        x: 360,
        y: 220,
        width: 712,
        height: 1020,
        gap: 24,
        children: [
          topCard,
          hStack({
            width: 712,
            gap: 24,
            children: [leftCard, rightCard],
          }),
        ],
      }),
      rightColumn(rightCards),
    ],
  });

const screens = [
  {
    index: 1,
    title: "沉浸听力：先只用耳朵进入语境",
    desc: "网页端第一步不让用户立刻陷进文字，而是先通过更安静的播放器建立整体耳感与情绪判断。",
    topCard: buildImmersiveTop(),
    leftCard: buildImmersiveLeft(),
    rightCard: buildImmersiveRight(),
    rightCards: [
      coachCard({ title: "AI coach note", body: "先别急着求证每个词。你现在最重要的是抓住语速、情绪和主要事件。", tags: ["先整体", "后文本"] }),
      coachCard({ title: "本轮目标", body: "完成 2-3 遍纯听，并能回答“主要发生了什么”。", tags: ["低负担", "2-3 遍"], accent: "$--color-success-foreground" }),
      coachCard({ title: "完成标记", body: "系统会记录你的遍数与大意判断，不需要一开始就听得很全。", tags: ["Listening 1/3"] }),
      coachCard({ title: "下一步", body: "进入核心词汇，把你刚才模糊听到的高频表达一点点拉清楚。", tags: ["进入 Module 2"], accent: "$--color-warning-foreground" }),
    ],
  },
  {
    index: 2,
    title: "核心词汇：学真正会复用的表达",
    desc: "不是列满屏生词，而是只抓 5-8 个会在未来反复用到的词块和表达。",
    topCard: buildVocabularyTop(),
    leftCard: buildVocabularyLeft(),
    rightCard: buildVocabularyRight(),
    rightCards: [
      coachCard({ title: "今日高频", body: "call in sick / heads-up / not feeling great 是本课最值得优先掌握的三组表达。", tags: ["B1-B2", "职场高频"] }),
      coachCard({ title: "学习策略", body: "每学一个表达，都要同时看它的语境、语气和原音频位置。", tags: ["听回原句", "自己造句"], accent: "$--color-success-foreground" }),
      coachCard({ title: "词汇本状态", body: "本课表达会自动同步到个人词汇本，并按记忆强度进入复习队列。", tags: ["spaced review"] }),
      coachCard({ title: "下一步", body: "进入 Chinglish 对照，看看这些表达为什么比直译更自然。", tags: ["进入 Module 3"], accent: "$--color-warning-foreground" }),
    ],
  },
  {
    index: 3,
    title: "Chinglish 对照：找到更自然的说法",
    desc: "通过左右并置的方式，把“中文思路下的英语”与“母语者真实会说的表达”做出对照。",
    topCard: buildChinglishTop(),
    leftCard: buildChinglishLeft(),
    rightCard: buildChinglishRight(),
    rightCards: [
      coachCard({ title: "关键提醒", body: "自然表达不只是“词更高级”，而是更符合真实语气和关系距离。", tags: ["语气", "场景"] }),
      coachCard({ title: "常见问题", body: "很多用户会把请假说成 ask for leave，但真实口语更常说 take the afternoon off。", tags: ["直译警惕"], accent: "$--color-error-foreground" }),
      coachCard({ title: "练习建议", body: "先输入你自己的版本，再看 AI 如何改写成更自然的说法。", tags: ["先自己写"] }),
      coachCard({ title: "下一步", body: "进入场景映射，让这些说法开始进入你自己的生活或工作里。", tags: ["进入 Module 4"], accent: "$--color-warning-foreground" }),
    ],
  },
  {
    index: 4,
    title: "场景映射：迁移到真实生活与工作",
    desc: "把学到的表达套回用户自己的场景里，让每节精听课都带着明确的落地价值。",
    topCard: buildSceneTop(),
    leftCard: buildSceneLeft(),
    rightCard: buildSceneRight(),
    rightCards: [
      coachCard({ title: "推荐先用", body: "优先把本课表达迁移到“向老板说明状态”“提前告知安排”这类高频场景。", tags: ["高复用"] }),
      coachCard({ title: "生成逻辑", body: "系统会根据“谁对谁说”“正式度”“是否需要缓和语气”生成不同脚本。", tags: ["对象", "语气"], accent: "$--color-success-foreground" }),
      coachCard({ title: "迁移提醒", body: "不要背整段稿子，重点是学会结构：状态 + 请求 + 提前告知。", tags: ["结构优先"] }),
      coachCard({ title: "下一步", body: "进入听力解码，把这些表达的真实声音拆开学会。", tags: ["进入 Module 5"], accent: "$--color-warning-foreground" }),
    ],
  },
  {
    index: 5,
    title: "听力解码：把真正“听见”的声音还原出来",
    desc: "这一页专门解决“词都认识，但连起来就听不懂”的核心痛点。",
    topCard: buildDecoderTop(),
    leftCard: buildDecoderLeft(),
    rightCard: buildDecoderRight(),
    rightCards: [
      coachCard({ title: "AI coach note", body: "你不是词不认识，而是语块还没形成。先把一整句稳定听成三个块。", tags: ["语块感", "先整体后细节"] }),
      coachCard({ title: "核心词", body: "call in sick / heads-up / not feeling great / take the afternoon off", tags: ["B1-B2", "职场高频"] }),
      coachCard({ title: "今日目标", body: "完成逐句回放和一轮跟读，确认自己能听出 ma needa 这类真实语流。", tags: ["25 分钟"], accent: "$--color-success-foreground" }),
      coachCard({ title: "下一步", body: "进入潜台词与语气，理解这句话为什么“软”、为什么体面。", tags: ["进入 Module 6"], accent: "$--color-warning-foreground" }),
    ],
  },
  {
    index: 6,
    title: "潜台词与语气：理解关系与态度",
    desc: "这一页帮助用户超越字面意义，开始感知说话者真正想表达的关系处理和态度强度。",
    topCard: buildSubtextTop(),
    leftCard: buildSubtextLeft(),
    rightCard: buildSubtextRight(),
    rightCards: [
      coachCard({ title: "语气标签", body: "soft / tentative / considerate 是这段材料的主导气质。", tags: ["tone tags"], accent: "$--color-success-foreground" }),
      coachCard({ title: "理解升级", body: "当你能分辨“试探性请求”和“直接通知”，真实沟通理解会明显上台阶。", tags: ["pragmatics"] }),
      coachCard({ title: "练习建议", body: "多比较不同强度版本的说法，感受它们对关系的影响。", tags: ["语气梯度"] }),
      coachCard({ title: "下一步", body: "进入句型拆解，把本课里最值得复用的骨架句抽出来。", tags: ["进入 Module 7"], accent: "$--color-warning-foreground" }),
    ],
  },
  {
    index: 7,
    title: "句型拆解：抽出可反复套用的骨架",
    desc: "这一页把具体语句抽象成骨架句型，帮助用户从“听懂”走向“会自己搭建表达”。",
    topCard: buildPatternTop(),
    leftCard: buildPatternLeft(),
    rightCard: buildPatternRight(),
    rightCards: [
      coachCard({ title: "本课骨架", body: "I might need to [do X] today.\nI just wanted to [do X] before [Y].", tags: ["高价值句型"] }),
      coachCard({ title: "迁移原则", body: "先替换动作，再替换场景，最后再尝试合并多个句型。", tags: ["简单到复杂"], accent: "$--color-success-foreground" }),
      coachCard({ title: "做对的标志", body: "你能不用原句，也能说出工作、上课、请假等不同版本。", tags: ["迁移成功"] }),
      coachCard({ title: "下一步", body: "进入输出练习，让 AI 检查你能否把这些表达真正写出来。", tags: ["进入 Module 8"], accent: "$--color-warning-foreground" }),
    ],
  },
  {
    index: 8,
    title: "输出练习：把这节课真正用出来",
    desc: "最后一页让学习闭环真正发生，用户要把今天学到的表达写进自己的输出里，并获得 AI 反馈。",
    topCard: buildOutputTop(),
    leftCard: buildOutputLeft(),
    rightCard: buildOutputRight(),
    rightCards: [
      coachCard({ title: "今日任务", body: "建议先完成请假邮件，再尝试对话模拟。这样更容易看出表达是否真的内化。", tags: ["写作优先"] }),
      coachCard({ title: "评分重点", body: "系统最关注是否用对语气、是否符合场景、是否把本课表达真正用进去。", tags: ["地道", "适配"], accent: "$--color-success-foreground" }),
      coachCard({ title: "闭环完成", body: "完成这一页后，本课表达会同步进词汇本并进入复习计划。", tags: ["report ready"] }),
      coachCard({ title: "课程结束", body: "你已经走完一整轮从输入到输出的完整精听闭环。", tags: ["Done"], accent: "$--primary" }),
    ],
  },
];

const positions = [
  [120, 120],
  [1680, 120],
  [3240, 120],
  [4800, 120],
  [120, 1500],
  [1680, 1500],
  [3240, 1500],
  [4800, 1500],
];

const canvasChildren = [];

screens.forEach((screen, idx) => {
  const [x, y] = positions[idx];
  canvasChildren.push(
    topLabel({
      index: String(screen.index).padStart(2, "0"),
      name: `${screen.index}. ${moduleNames[screen.index - 1]}`,
      x,
      y: y - 52,
    }),
  );
  canvasChildren.push(
    moduleScreen({
      ...screen,
      x,
      y,
    }),
  );
});

const document = {
  version: "2.9",
  children: [
    frame(
      {
        id: uid("canvas"),
        x: 0,
        y: 0,
        name: "LingMate Learning Workspace 8 Modules",
        clip: true,
        width: 6360,
        height: 2900,
        fill: "$--canvas",
        layout: "none",
      },
      canvasChildren,
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

const outputPath = path.join(process.cwd(), "LingMate_learning_workspace_8modules.pen");
fs.writeFileSync(outputPath, `${JSON.stringify(clean(document), null, 2)}\n`);
console.log(`Wrote ${outputPath}`);
