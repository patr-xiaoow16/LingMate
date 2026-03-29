from copy import deepcopy


HOME_DATA = {
    "hero": {
        "eyebrow": "AI Co-pilot for immersive listening",
        "title": "每一句，都陪你听懂。",
        "description": "将 YouTube、播客或本地音频，拆成覆盖“听懂、拆解、迁移、会用”的八步沉浸式精听课。LingMate 更像一位有陪伴感、有审美的精听教练，而不是一套冷冰冰的题库。",
        "actions": [
            {"label": "开始一段新材料", "kind": "primary"},
            {"label": "先看示例课", "kind": "secondary"},
        ],
        "tags": ["支持 YouTube / Podcast / MP3", "AI 30s 预处理"],
    },
    "metrics": [
        {"title": "本周完整精听", "value": "4 次", "note": "平均完成 6.3 / 8 模块，已超过目标节奏。"},
        {"title": "最近新增表达", "value": "26 条", "note": "高频集中在商务请假、播客口语与态度表达。"},
        {"title": "适配材料难度", "value": "B1-B2", "note": "推荐先从 8-12 分钟材料开始，体验更顺滑。"},
    ],
    "importCard": {
        "title": "把任意英文内容，变成一堂会陪你走完的精听课",
        "tabs": ["链接粘贴"],
        "platforms": "YouTube / Spotify / Apple Podcast / TED / BBC",
        "placeholder": "粘贴一段你最近总是听不清的英文链接",
        "eta": "预计 30 秒完成分析",
        "engine": "FastAPI skeleton · DeepSeek ready",
        "button": "生成精听课",
        "examples": [
            {"label": "The Daily: Why Office English Still Feels Hard", "meta": "B2 · 11 min"},
            {"label": "TED: Tiny Habits That Actually Stick", "meta": "B1 · 08 min"},
            {"label": "Modern Family Clip: I’m not feeling great", "meta": "A2 · 03 min"},
        ],
    },
    "scenarios": [
        {
            "title": "请假与状态表达",
            "subtitle": "日常 / 职场",
            "meta": "从 “I’m not feeling great” 到 “calling in sick”，顺手学会委婉与正式语气的差异。",
            "expression": "I’m calling in sick today.",
        },
        {
            "title": "播客里的高频口语",
            "subtitle": "通勤 / 自学",
            "meta": "针对连读、吞音和语速跳跃的段落，给你逐句拆出“实际听起来像什么”。",
            "expression": "kind of / sort of / gonna",
        },
        {
            "title": "雅思与课堂听力",
            "subtitle": "学术 / 备考",
            "meta": "保留材料的原始语速，但把关键词、语义转折与潜台词先替你点亮。",
            "expression": "What the speaker is really implying",
        },
    ],
}

ANALYSIS_DATA = {
    "summary": {
        "eyebrow": "Import complete in 00:28",
        "title": "30 秒内，自动拆成一堂完整精听课",
        "description": "系统先替你完成转写、难度分级、关键表达抽取、场景识别和语音现象标注，再把结果排成可浏览、可解释、可开始学习的八步精听路径。",
        "pills": ["CEFR B2", "147 WPM", "Business podcast", "11m 24s"],
    },
    "pipeline": {
        "title": "AI 预处理流水线",
        "description": "已完成 6 / 6 个关键步骤，正在生成八步学习结构。",
        "progress": 92,
        "steps": [
            {"index": "01", "title": "Whisper 转写", "note": "句级时间戳已对齐", "status": "done"},
            {"index": "02", "title": "难度分级", "note": "词汇 B2 / 语速偏快", "status": "done"},
            {"index": "03", "title": "关键表达", "note": "已提取 8 条高价值表达", "status": "done"},
            {"index": "04", "title": "场景识别", "note": "职场沟通 / 请假语境", "status": "done"},
            {"index": "05", "title": "语音现象", "note": "连读 / 弱读 / T 音变化", "status": "done"},
            {"index": "06", "title": "课程编排", "note": "正在把内容映射到 8 个模块", "status": "done"},
        ],
    },
    "lesson": {
        "title": "Why Saying “I’m not feeling great” Sounds Softer",
        "meta": "Apple Podcast · 11 分 24 秒 · 对话体材料",
        "badge": "Recommended",
        "transcript": "I’m not feeling great today, so I might need to take the afternoon off. I just wanted to give you a heads-up before the meeting starts.",
        "chips": ["heads-up", "take the afternoon off", "委婉语气"],
    },
    "modulePlan": [
        {"label": "1 沉浸听力", "desc": "先纯听 2-3 遍，建立整体语义与情绪印象。", "tone": "success"},
        {"label": "2 核心词汇", "desc": "提取 8 个关键表达，聚焦真正会复用的口语。", "tone": "default"},
        {"label": "3 Chinglish 对照", "desc": "把“我会说”的表达，改写成更自然的英语。", "tone": "default"},
        {"label": "4 场景映射", "desc": "生成为老板请假、会议说明等可直接复用脚本。", "tone": "default"},
        {"label": "5 听力解码", "desc": "逐句标出连读 / 弱读 / T 音变化，解决听不清。", "tone": "warning"},
        {"label": "6 潜台词与语气", "desc": "理解为什么这句话更软，以及它真正传递的关系感。", "tone": "default"},
        {"label": "7 句型拆解", "desc": "抽出骨架句，支持快速换词迁移。", "tone": "default"},
    ],
}

MODULES = [
    {
        "index": 1,
        "slug": "immersive-listening",
        "name": "沉浸听力",
        "sidebar": "先感受语速与情绪",
        "headerTitle": "沉浸听力：先只用耳朵进入语境",
        "headerDesc": "网页端第一步不让用户立刻陷进文字，而是先通过更安静的播放器建立整体耳感与情绪判断。",
        "topCard": {
            "title": "Module 1 · Immersive Listening",
            "subtitle": "先不看文字，只用耳朵建立对内容、语速和情绪的整体感受。",
            "pills": ["0.85x", "Listen 1/3"],
            "sections": [
                {"type": "player", "progress": 36},
                {"type": "panel", "label": "现在的学习任务", "tone": "secondary", "content": "请先纯听两遍，不要急着看答案。试着只抓“谁在说、情绪如何、主要发生了什么”。"},
                {
                    "type": "dual-panels",
                    "left": {"label": "你可能听到的感觉", "content": "语气偏柔和，不像直接请假，更像先铺垫自己的状态，再为后续的请假做准备。", "chips": ["soft", "hesitant", "workplace"], "tone": "sage"},
                    "right": {"label": "听后快速检查", "questions": ["这段话主要是在解释计划，还是在传达状态？", "说话人听起来更像紧张、抱歉，还是生气？", "你大概听到了哪些高频词块？"]},
                },
            ],
            "actions": [{"label": "再听一遍", "kind": "secondary"}, {"label": "进入核心词汇", "kind": "primary"}],
        },
        "leftCard": {"title": "大意理解检查", "body": "在不看文本的前提下，只做低负担的“整体理解”。", "items": ["谁更可能是说话对象？老板 / 同事 / 朋友", "这段内容更接近请假沟通，还是情绪吐槽？", "你听到的是完整请求，还是一种提前铺垫？"]},
        "rightCard": {"title": "听后反思", "rows": [{"label": "已完成纯听", "meta": "2 遍", "tone": "default"}, {"label": "推荐继续", "meta": "核心词汇", "tone": "success"}], "chips": ["先整体", "后细节", "低压力"], "button": "继续下一步"},
        "coachCards": [{"title": "AI coach note", "body": "先别急着求证每个词。你现在最重要的是抓住语速、情绪和主要事件。", "tags": ["先整体", "后文本"]}],
    },
    {
        "index": 2,
        "slug": "vocabulary-deep-dive",
        "name": "核心词汇",
        "sidebar": "抓住高价值表达",
        "headerTitle": "核心词汇：学真正会复用的表达",
        "headerDesc": "不是列满屏生词，而是只抓 5-8 个会在未来反复用到的词块和表达。",
        "topCard": {
            "title": "Module 2 · Vocabulary Deep Dive",
            "subtitle": "聚焦真正会复用的 5-8 个表达，而不是一张长长的生词表。",
            "pills": ["8 expressions"],
            "sections": [
                {
                    "type": "expression-browser",
                    "expressions": [{"phrase": "call in sick", "cefr": "B1", "selected": True}, {"phrase": "heads-up", "cefr": "B2"}, {"phrase": "not feeling great", "cefr": "B1"}],
                    "detail": {"title": "call in sick", "body": "正式、自然的“打电话请病假”。比直接说 I’m sick 更接近职场真实语境。", "chips": ["正式一点", "职场高频", "可直接套用"], "examples": ["I need to call in sick today.", "She called in sick before the morning stand-up."]},
                },
                {"type": "input", "label": "试着自己造句", "content": "I called in sick because I was feeling under the weather this morning."},
                {"type": "banner", "tone": "success", "content": "AI 建议：表达自然，可再试一次更口语的版本"},
            ],
            "actions": [{"label": "回听原句", "kind": "secondary"}, {"label": "加入词汇本", "kind": "soft"}],
        },
        "leftCard": {"title": "为什么是这些词", "body": "LingMate 优先提取高频、可迁移、且与你当前水平相关的表达。", "items": ["不是每个生词都值得学，但这些表达会在职场、播客和日常口语里反复出现。", "系统会结合你过往薄弱点，优先展示你“看过但不会用”的词块。", "点击回听原句，能把词和语音、语气重新绑在一起。"]},
        "rightCard": {"title": "掌握状态", "rows": [{"label": "已掌握", "meta": "3", "tone": "success"}, {"label": "需复习", "meta": "4", "tone": "warning"}, {"label": "待造句", "meta": "1", "tone": "default"}], "body": "完成造句后，系统会自动同步到个人词汇本，并安排复习时间点。", "button": "进入 Chinglish 对照"},
        "coachCards": [{"title": "今日高频", "body": "call in sick / heads-up / not feeling great 是本课最值得优先掌握的三组表达。", "tags": ["B1-B2", "职场高频"]}],
    },
    {
        "index": 3,
        "slug": "native-vs-chinglish",
        "name": "Chinglish 对照",
        "sidebar": "找到更自然的说法",
        "headerTitle": "Chinglish 对照：找到更自然的说法",
        "headerDesc": "通过左右并置的方式，把“中文思路下的英语”与“母语者真实会说的表达”做出对照。",
        "topCard": {
            "title": "Module 3 · Native vs Chinglish",
            "subtitle": "把“我会怎么说”与“母语者更自然的说法”放在一起看，差异会立刻变清楚。",
            "pills": ["4 pairs"],
            "sections": [{"type": "compare-list", "pairs": [{"wrong": "I have a little sick today.", "right": "I’m not feeling great today.", "note": "自然表达往往不是逐词翻译，而是从“身体状态”而不是“疾病名词”切入。"}]}],
        },
        "leftCard": {"title": "为什么更自然", "body": "更自然的英语通常体现的是语气、关系和使用场景，而不仅是语法正确。", "items": ["少用中文直译的名词结构，多用状态、动作或语块。"]},
        "rightCard": {"title": "自己试一版", "inputLabel": "你的版本", "inputContent": "I want to ask for leave because I feel not good.", "banner": "AI 判断：有明显 Chinglish 痕迹", "body": "建议改为：I’m not feeling great, so I might need to take the afternoon off。"},
        "coachCards": [{"title": "关键提醒", "body": "自然表达不只是“词更高级”，而是更符合真实语气和关系距离。", "tags": ["语气", "场景"]}],
    },
    {
        "index": 4,
        "slug": "scene-mapping",
        "name": "场景映射",
        "sidebar": "迁移到真实场景",
        "headerTitle": "场景映射：迁移到真实生活与工作",
        "headerDesc": "把学到的表达套回用户自己的场景里，让每节精听课都带着明确的落地价值。",
        "topCard": {
            "title": "Module 4 · Scene Mapping",
            "subtitle": "把本课表达迁移到用户自己的生活、职场或学术语境里，做到“学了就能用”。",
            "pills": ["职场", "日常", "学术"],
            "sections": [
                {
                    "type": "scene-grid",
                    "left": {"label": "可直接复用的模板", "rows": [{"label": "向老板请半天假", "meta": "soft"}, {"label": "会议前先说明状态", "meta": "neutral"}], "chips": ["何时用", "说给谁听", "语气建议"]},
                    "right": {"label": "为我生成一版", "content": "场景：我想在 stand-up 之前告诉老板自己状态不太好，下午可能需要请假。\n\n脚本：I’m not feeling great today, so I might need to take the afternoon off. I just wanted to give you a heads-up before the stand-up."},
                },
                {"type": "input", "label": "描述你自己的场景", "content": "我想向老师说明今天状态不好，可能无法参加下午的小组讨论。"},
            ],
            "actions": [{"label": "生成我的脚本", "kind": "primary"}, {"label": "换成更正式语气", "kind": "secondary"}],
        },
        "leftCard": {"title": "使用建议", "items": ["先选场景，再选说话对象，最后决定语气软硬。"]},
        "rightCard": {"title": "场景迁移结果", "body": "系统已生成 3 个变体：对老板、对老师、对同学。", "rows": [{"label": "老板版本", "meta": "正式", "tone": "success"}, {"label": "老师版本", "meta": "礼貌", "tone": "default"}], "button": "进入听力解码"},
        "coachCards": [{"title": "推荐先用", "body": "优先把本课表达迁移到“向老板说明状态”“提前告知安排”这类高频场景。", "tags": ["高复用"]}],
    },
    {
        "index": 5,
        "slug": "listening-decoder",
        "name": "听力解码",
        "sidebar": "把声音拆开看清",
        "headerTitle": "听力解码：把真正“听见”的声音还原出来",
        "headerDesc": "这一页专门解决“词都认识，但连起来就听不懂”的核心痛点。",
        "topCard": {
            "title": "Module 5 · Listening Decoder",
            "subtitle": "把“视觉上的文字”翻回“耳朵里真正听到的声音”，解决词都认识却听不出来的问题。",
            "pills": ["0.85x", "Loop sentence"],
            "sections": [{"type": "player", "progress": 36}, {"type": "panel", "label": "原句", "tone": "secondary", "content": "I’m not feeling great today, so I might need to take the afternoon off."}, {"type": "panel", "label": "实际听起来像", "tone": "sage", "content": "I’m na feeling great today, so I ma needa take the afternoon off."}, {"type": "chips", "items": ["not → na", "might need to → ma needa", "弱读 / 黏连"]}],
            "actions": [{"label": "回放整句", "kind": "secondary"}, {"label": "逐词跟读", "kind": "secondary"}, {"label": "进入潜台词与语气", "kind": "primary"}],
        },
        "leftCard": {"title": "为什么这里会听不出", "body": "难点不在词义，而在连续语流下的节奏压缩。", "items": ["not feeling: /t/ 被吞弱，重心落在 feeling"]},
        "rightCard": {"title": "跟读反馈", "score": "82 / 100", "banner": "再来一遍", "body": "节奏基本对，但 might need to 还不够黏连。先模仿气口，再管每个词是否饱满。", "chips": ["先整体", "后单词"]},
        "coachCards": [{"title": "AI coach note", "body": "你不是词不认识，而是语块还没形成。先把一整句稳定听成三个块。", "tags": ["语块感", "先整体后细节"]}],
    },
    {
        "index": 6,
        "slug": "subtext-tone",
        "name": "潜台词与语气",
        "sidebar": "理解关系与态度",
        "headerTitle": "潜台词与语气：理解关系与态度",
        "headerDesc": "这一页帮助用户超越字面意义，开始感知说话者真正想表达的关系处理和态度强度。",
        "topCard": {
            "title": "Module 6 · Subtext & Tone",
            "subtitle": "理解同一句话背后的关系感、试探感和真实意图，而不只停留在字面意思。",
            "pills": ["3 key lines"],
            "sections": [{"type": "tone-insight", "rows": [{"label": "I’m not feeling great today.", "meta": "soft", "tone": "success"}, {"label": "I might need to take the afternoon off.", "meta": "tentative", "tone": "default"}], "insightTitle": "这句话真正传递的不是“病情”，而是“我在尽量礼貌地提出请求”。", "insightBody": "如果直接说 I’m sick. I need leave. 信息虽然清楚，但会显得过硬。", "chips": ["委婉", "关系维护", "提前铺垫"]}],
        },
        "leftCard": {"title": "关系与态度信号", "items": ["not feeling great: 降低强度，让表达更容易被接受"]},
        "rightCard": {"title": "理解测验", "items": ["说话人是在命令式通知，还是在关系维护式沟通？"]},
        "coachCards": [{"title": "语气标签", "body": "soft / tentative / considerate 是这段材料的主导气质。", "tags": ["tone tags"]}],
    },
    {
        "index": 7,
        "slug": "pattern-extraction",
        "name": "句型拆解",
        "sidebar": "抽出句型骨架",
        "headerTitle": "句型拆解：抽出可反复套用的骨架",
        "headerDesc": "这一页把具体语句抽象成骨架句型，帮助用户从“听懂”走向“会自己搭建表达”。",
        "topCard": {
            "title": "Module 7 · Pattern Extraction",
            "subtitle": "把原句抽成骨架，掌握之后就能迁移到更多场景和表达任务里。",
            "pills": ["3 high-value patterns"],
            "sections": [{"type": "pattern-panel", "label": "骨架句", "title": "I might need to [do X] today.", "chips": ["take the afternoon off", "work from home", "leave a little early"]}],
            "actions": [{"label": "换词练习", "kind": "secondary"}, {"label": "生成更复杂句型", "kind": "soft"}],
        },
        "leftCard": {"title": "换词练习", "rows": [{"label": "I might need to work from home today.", "meta": "easy", "tone": "default"}], "body": "先做简单替换，再让 AI 帮你合并两个句型。"},
        "rightCard": {"title": "AI 句型建议", "body": "你已经会用 I might need to ...，下一步建议学会把它和原因表达串起来。", "panel": "I’m not feeling great, so I might need to work from home this afternoon."},
        "coachCards": [{"title": "本课骨架", "body": "I might need to [do X] today.\nI just wanted to [do X] before [Y].", "tags": ["高价值句型"]}],
    },
    {
        "index": 8,
        "slug": "output-challenge",
        "name": "输出练习",
        "sidebar": "把所学真正用出来",
        "headerTitle": "输出练习：把这节课真正用出来",
        "headerDesc": "最后一页让学习闭环真正发生，用户要把今天学到的表达写进自己的输出里，并获得 AI 反馈。",
        "topCard": {
            "title": "Module 8 · Output Challenge",
            "subtitle": "学习的终点不是“我懂了”，而是“我能自己写、自己说”。",
            "pills": ["3 tasks"],
            "sections": [{"type": "output-layout", "tasks": [{"label": "填空复述", "meta": "easy", "tone": "default"}, {"label": "请假邮件", "meta": "medium", "tone": "primary"}], "inputLabel": "任务：向老板写一段请假说明", "inputContent": "Hi, I’m not feeling great today, so I might need to take the afternoon off. I just wanted to give you a heads-up before the stand-up."}, {"type": "chips", "items": ["词汇是否准确", "语气是否自然", "是否符合场景"]}],
            "actions": [{"label": "提交给 AI", "kind": "primary"}, {"label": "换一个任务", "kind": "secondary"}],
        },
        "leftCard": {"title": "评分维度", "rows": [{"label": "词汇准确", "meta": "86", "tone": "success"}, {"label": "语法正确", "meta": "82", "tone": "default"}, {"label": "表达地道", "meta": "78", "tone": "warning"}, {"label": "场景适配", "meta": "89", "tone": "success"}]},
        "rightCard": {"title": "AI 反馈结果", "body": "整体表达自然，已经正确用上了 not feeling great / take the afternoon off / heads-up。", "extra": "如果想更正式一点，可以把 just wanted to 改成 wanted to let you know。", "button": "完成本课"},
        "coachCards": [{"title": "今日任务", "body": "建议先完成请假邮件，再尝试对话模拟。这样更容易看出表达是否真的内化。", "tags": ["写作优先"]}],
    },
]

WORKSPACE_DATA = {
    "material": {"title": "Soft language at work", "description": "本课围绕请假、委婉表达与职场口语展开。", "chips": ["B1-B2", "11m 24s"]},
    "progress": {"current": 1, "total": 8, "duration": "37 分钟", "completed": 0},
    "modules": MODULES,
}

REPORT_DATA = {
    "hero": {"eyebrow": "This week", "title": "从“听懂一点点”，进入真正会迁移的学习闭环", "description": "报告页不只展示学习时长，而是把本周新掌握表达、薄弱点变化和下一轮复习节奏串成一个更安心的网页端学习节奏。", "actions": ["开始今日复习", "导出精听笔记"]},
    "metrics": [{"title": "本周精听时长", "value": "6.2h", "note": "较上周 +18%，学习节奏更稳定。"}, {"title": "新增表达", "value": "26", "note": "其中 12 条已进入复习队列。"}, {"title": "平均完成模块", "value": "6.1", "note": "最常完成到输出练习。"}],
    "radar": [{"label": "词汇掌握", "value": "78%", "tone": "primary"}, {"label": "连读弱读识别", "value": "64%", "tone": "warning"}, {"label": "句式理解", "value": "73%", "tone": "primary"}, {"label": "语用感知", "value": "58%", "tone": "error"}, {"label": "输出能力", "value": "61%", "tone": "primary"}],
    "weeklyHours": [{"day": "Mon", "value": 96, "tone": "secondary"}, {"day": "Tue", "value": 122, "tone": "secondary"}, {"day": "Wed", "value": 148, "tone": "primary"}, {"day": "Thu", "value": 110, "tone": "secondary"}, {"day": "Fri", "value": 172, "tone": "primary"}],
    "records": [{"date": "03/24", "title": "完成播客材料《Soft language at work》", "note": "关键突破：委婉语气 + 连读识别"}, {"date": "03/26", "title": "复习表达 give you a heads-up", "note": "已在新材料中再次遇到并正确理解"}, {"date": "03/28", "title": "输出练习：请假邮件", "note": "用上了 call in sick / not feeling great / heads-up"}],
    "queue": [{"title": "call in sick", "meta": "第 3 天 · 需要在新场景中再用一次", "active": True}, {"title": "give you a heads-up", "meta": "第 7 天 · 适合做口语复述"}],
    "shareCard": {"title": "每一句，都陪你听懂", "body": "本次材料：Soft language at work\n掌握表达：call in sick / give you a heads-up / not feeling great\n完成模块：6 / 8", "chips": ["委婉语气", "商务场景", "连读解码"]},
}

ANALYSIS_STEP_BLUEPRINT = [
    {"index": "01", "title": "Whisper 转写", "duration": 1.8, "pending": "正在拆句并对齐时间戳", "done": "句级时间戳已对齐"},
    {"index": "02", "title": "难度分级", "duration": 1.3, "pending": "正在计算 CEFR / 语速 / 句式复杂度", "done": "词汇 B2 / 语速偏快"},
    {"index": "03", "title": "关键表达", "duration": 1.5, "pending": "正在抽取高价值表达与词块", "done": "已提取 8 条高价值表达"},
    {"index": "04", "title": "场景识别", "duration": 1.2, "pending": "正在识别材料语境与使用场景", "done": "职场沟通 / 请假语境"},
    {"index": "05", "title": "语音现象", "duration": 1.6, "pending": "正在标注连读 / 弱读 / T 音变化", "done": "连读 / 弱读 / T 音变化"},
    {"index": "06", "title": "课程编排", "duration": 1.9, "pending": "正在把内容映射到 8 个模块", "done": "已完成 8 模块映射与页面编排"},
]


def home_fixture() -> dict:
    return deepcopy(HOME_DATA)


def analysis_fixture() -> dict:
    return deepcopy(ANALYSIS_DATA)


def workspace_fixture() -> dict:
    return deepcopy(WORKSPACE_DATA)


def report_fixture() -> dict:
    return deepcopy(REPORT_DATA)


def modules_fixture() -> list[dict]:
    return deepcopy(MODULES)


def analysis_steps_fixture() -> list[dict]:
    return deepcopy(ANALYSIS_STEP_BLUEPRINT)
