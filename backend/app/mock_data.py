from __future__ import annotations

from copy import deepcopy


MODULE_ORDER = [
    ("immersive-listening", "沉浸听力", "Immersive Listening"),
    ("vocabulary-deep-dive", "核心词汇", "Vocabulary Deep Dive"),
    ("native-vs-chinglish", "Chinglish 对照", "Native vs Chinglish"),
    ("scene-mapping", "场景映射", "Scene Mapping"),
    ("listening-decoder", "听力解码", "Listening Decoder"),
    ("subtext-and-tone", "潜台词与语气", "Subtext & Tone"),
    ("pattern-extraction", "句型拆解", "Pattern Extraction"),
    ("output-challenge", "输出练习", "Output Challenge"),
]


def _module_panels(title_a: str, items_a: list[str], title_b: str, items_b: list[str], tone_a: str = "info", tone_b: str = "warning") -> list[dict]:
    return [
        {"title": title_a, "tone": tone_a, "items": items_a},
        {"title": title_b, "tone": tone_b, "items": items_b},
    ]


def build_base_lesson() -> dict:
    modules = [
        {
            "key": "immersive-listening",
            "step": 1,
            "title": "沉浸听力：先用耳朵走入语境",
            "english_title": "Module 1 · Immersive Listening",
            "description": "先不看文字，只捕捉语速、情绪和大意。",
            "duration": "8 min",
            "status": "current",
            "progress": 13,
            "primary_action": "进入词汇卡",
            "secondary_action": "再听一遍",
            "quick_prompts": [
                "我听到的核心事件是……",
                "说话人的语气像是在……",
                "我最不确定的一句是……",
            ],
            "prompt_box": {
                "label": "听后总结",
                "placeholder": "用中文或英文写下你理解到的大意、情绪或疑惑点。",
                "button_label": "获取 AI 反馈",
            },
            "payload": {
                "audio_progress": 43,
                "listen_round": "Listen 1 / 3",
                "focus_prompt": "像真实场景那样先“只听不看”，感受说话人是在解释、请求还是抱怨。",
                "gist_tiles": [
                    {"label": "人物关系", "value": "员工对直属经理"},
                    {"label": "场景", "value": "临时请半天病假"},
                    {"label": "语气", "value": "谨慎、礼貌、想先打招呼"},
                ],
                "question_cards": [
                    {
                        "question": "这段内容主要在做什么？",
                        "choices": ["安排团队聚餐", "提前沟通请半天假", "反馈项目延期"],
                        "answer": 1,
                    },
                    {
                        "question": "说话人的整体语气更接近？",
                        "choices": ["命令式", "谨慎但坦诚", "过度兴奋"],
                        "answer": 1,
                    },
                ],
                "reflection_chips": ["workplace", "headache", "afternoon off"],
            },
            "side_panels": [
                {
                    "title": "AI coach note",
                    "tone": "info",
                    "items": [
                        "先别急着看字幕，先记住“谁在对谁说话”。",
                        "这段音频里真正重要的是礼貌地提出需求，而不是抱怨症状。",
                    ],
                },
                {
                    "title": "本轮目标",
                    "tone": "success",
                    "items": [
                        "抓住 3 个关键词：headache / afternoon / manager。",
                        "完成 2 次纯听，记录自己最不确定的一句。",
                    ],
                },
                {
                    "title": "完成标记",
                    "tone": "warning",
                    "items": ["完成 Listening 1/3", "准备进入 Module 2"],
                },
            ],
            "footer_panels": [
                {
                    "title": "大意理解检查",
                    "tone": "neutral",
                    "items": [
                        "她为什么要先给老板发消息？",
                        "请假的时间是整天还是半天？",
                        "她有没有直接说自己非常严重？",
                    ],
                },
                {
                    "title": "听后反思",
                    "tone": "info",
                    "items": [
                        "本次大意捕捉度 82 / 100",
                        "你对礼貌开场的敏感度较高",
                        "下一步适合进入词汇深挖",
                    ],
                },
            ],
        },
        {
            "key": "vocabulary-deep-dive",
            "step": 2,
            "title": "核心词汇：学真正会复用的表达",
            "english_title": "Module 2 · Vocabulary Deep Dive",
            "description": "围绕 5 个关键表达，拆出语义、场景和替换用法。",
            "duration": "7 min",
            "status": "locked",
            "progress": 0,
            "primary_action": "进入 Chinglish 对照",
            "secondary_action": "加入词汇本",
            "quick_prompts": [
                "请帮我用 call in sick 造一个更自然的句子",
                "这个表达更适合发消息还是当面说？",
                "给我一个商务一点的替代说法",
            ],
            "prompt_box": {
                "label": "词汇造句练习",
                "placeholder": "输入一句你自己的例句，AI 会帮你判断是否自然、是否符合场景。",
                "button_label": "检查造句",
            },
            "payload": {
                "vocab_list": [
                    {"term": "call in sick", "cefr": "B1", "mastery": 31},
                    {"term": "head-up", "cefr": "B2", "mastery": 42},
                    {"term": "not feeling great", "cefr": "B1", "mastery": 56},
                    {"term": "take the afternoon off", "cefr": "B1", "mastery": 28},
                    {"term": "arrange cover", "cefr": "B2", "mastery": 18},
                ],
                "focus_term": {
                    "term": "call in sick",
                    "phonetic_hint": "更像“请病假”这一动作，而不是单纯描述生病。",
                    "meaning": "打电话/发消息请病假；适用于临时因身体不适而无法上班。",
                    "scene": "适合和主管、HR、排班经理沟通当天缺勤。",
                    "examples": [
                        "I had to call in sick because I woke up with a fever.",
                        "She rarely calls in sick unless she really needs to rest.",
                    ],
                },
                "why_these_words": [
                    "它们都出现在“礼貌请假”这一真实职场场景里，迁移价值很高。",
                    "不仅能听懂，还能直接复用到邮件、IM、口头说明里。",
                    "这些表达背后都藏着语气强弱和人际距离感。",
                ],
                "mastery_bars": [
                    {"label": "已掌握", "value": 3},
                    {"label": "待复习", "value": 2},
                    {"label": "易混淆", "value": 1},
                ],
            },
            "side_panels": [
                {
                    "title": "今日洞察",
                    "tone": "success",
                    "items": [
                        "call in sick 强调“请病假”动作。",
                        "not feeling great 让语气更软，不会显得太重。",
                    ],
                },
                {
                    "title": "学习策略",
                    "tone": "info",
                    "items": [
                        "先学能复用的表达，再学长尾词。",
                        "每个词至少要会说 1 个自己的句子。",
                    ],
                },
                {
                    "title": "词汇状态",
                    "tone": "warning",
                    "items": ["B1 表达 3 个", "B2 表达 2 个"],
                },
            ],
            "footer_panels": _module_panels(
                "为什么是这些词",
                [
                    "都围绕“请假 + 打招呼 + 解释原因”展开。",
                    "在商务沟通里出现频率高，适合优先掌握。",
                    "和后续 Chinglish 对照、句型提炼会自然衔接。",
                ],
                "掌握状态",
                ["已掌握 3 个", "建议复习 2 个", "下一步：进入中式表达对照"],
                "info",
                "success",
            ),
        },
        {
            "key": "native-vs-chinglish",
            "step": 3,
            "title": "Chinglish 对照：找到更自然的说法",
            "english_title": "Module 3 · Native vs Chinglish",
            "description": "把“我会说”与“母语者会说”并排放在一起看。",
            "duration": "6 min",
            "status": "locked",
            "progress": 0,
            "primary_action": "进入场景映射",
            "secondary_action": "收藏这一版对照",
            "quick_prompts": [
                "这句哪里听起来像中式英文？",
                "帮我把这句话改得更口语一些",
                "解释一下背后的语感差异",
            ],
            "prompt_box": {
                "label": "自我表达体检",
                "placeholder": "输入你平时会说的一句话，AI 帮你判断是否 Chinglish，并给出更地道改写。",
                "button_label": "改写我的表达",
            },
            "payload": {
                "pairs": [
                    {
                        "chinglish": "I have a little sick today.",
                        "native": "I'm not feeling great today.",
                        "explanation": "英文里更常用感受型表达弱化直接度，显得自然也更礼貌。",
                    },
                    {
                        "chinglish": "I want to ask for leave this afternoon.",
                        "native": "I might need to take the afternoon off.",
                        "explanation": "母语者常用 might need to 先留缓冲，不会一上来太硬。",
                    },
                    {
                        "chinglish": "Please allow me to have a rest.",
                        "native": "I just wanted to give you a heads-up.",
                        "explanation": "先打招呼再提出需求，更符合真实职场沟通逻辑。",
                    },
                ],
                "rewrite_example": {
                    "original": "I have a fever so maybe I need rest in home.",
                    "revised": "I've got a fever, so I may need to work from home today.",
                    "note": "把“症状 + 方案”说清楚，并用 may need to 拉低语气强度。",
                },
            },
            "side_panels": [
                {
                    "title": "关键提醒",
                    "tone": "info",
                    "items": [
                        "英语里先表达状态，再提出请求，通常比直说更顺。",
                        "礼貌不是靠复杂词，而是靠缓冲和顺序。",
                    ],
                },
                {
                    "title": "常见问题",
                    "tone": "warning",
                    "items": [
                        "want to ask for leave 太像翻译腔。",
                        "a little sick 并不是最自然的口语表达。",
                    ],
                },
                {
                    "title": "练习建议",
                    "tone": "success",
                    "items": ["用自己的真实场景改写 1 次", "说出更自然的第一句开场"],
                },
            ],
            "footer_panels": _module_panels(
                "为什么更自然",
                [
                    "更像真实职场对话，而不是书面翻译。",
                    "先铺垫状态，再讲需求，更符合英语沟通顺序。",
                    "弱化命令感，给对方留反应空间。",
                ],
                "自己试一版",
                ["先写你原本会说的版本", "再改成更自然的版本", "最后让 AI 给你解释差异"],
            ),
        },
        {
            "key": "scene-mapping",
            "step": 4,
            "title": "场景映射：迁移到真实生活与工作",
            "english_title": "Module 4 · Scene Mapping",
            "description": "把听到的表达迁移到你自己的职场、日常或学术场景里。",
            "duration": "8 min",
            "status": "locked",
            "progress": 0,
            "primary_action": "进入听力解码",
            "secondary_action": "生成定制话术",
            "quick_prompts": [
                "我想跟老板请病假，帮我生成 IM 版本",
                "如果对象换成同事，语气怎么调？",
                "给我一个更正式的邮件版",
            ],
            "prompt_box": {
                "label": "场景迁移",
                "placeholder": "描述你的真实场景，例如：我想向导师解释今天不能参加 meeting。",
                "button_label": "生成我的版本",
            },
            "payload": {
                "filters": ["职场", "日常", "学术"],
                "templates": [
                    {
                        "title": "向老板请半天病假",
                        "channel": "Slack / 微信",
                        "tone": "礼貌、简洁",
                        "script": "Hi, I'm not feeling great today, so I might need to take the afternoon off. I'll keep my phone nearby and make sure nothing urgent is blocked.",
                    },
                    {
                        "title": "和同事协调 cover",
                        "channel": "即时消息",
                        "tone": "合作、直接",
                        "script": "I'm feeling a bit under the weather. Could you help me cover the 3 pm sync if I step away this afternoon?",
                    },
                    {
                        "title": "给导师发邮件",
                        "channel": "Email",
                        "tone": "正式、完整",
                        "script": "I'm not feeling well today and may need to rest this afternoon. I wanted to give you a heads-up in advance and will follow up with the reading notes tonight.",
                    },
                ],
                "transition_map": [
                    {"from": "状态描述", "to": "需求表达", "hint": "先说 not feeling great，再说 might need to..."},
                    {"from": "需求表达", "to": "补偿动作", "hint": "说明你会 keep phone nearby 或 arrange cover。"},
                    {"from": "补偿动作", "to": "结束语", "hint": "最后补一句 thanks for understanding。"},
                ],
            },
            "side_panels": [
                {
                    "title": "推荐先用",
                    "tone": "success",
                    "items": ["状态 + 需求 + 补偿动作", "短句先行，别堆太多理由"],
                },
                {
                    "title": "生成逻辑",
                    "tone": "info",
                    "items": ["识别对象身份", "匹配沟通渠道", "自动调整语气强弱"],
                },
                {
                    "title": "迁移提醒",
                    "tone": "warning",
                    "items": ["不要逐字直译中文理由", "优先复用本课中的核心表达"],
                },
            ],
            "footer_panels": _module_panels(
                "使用建议",
                [
                    "先说明状态，再给出方案，最后做补偿承诺。",
                    "对象越正式，越要避免过度细节化描述身体不适。",
                ],
                "场景迁移结果",
                ["老板版本 3.2 / 5", "导师版本 3.8 / 5", "同事版本 4.2 / 5"],
                "info",
                "success",
            ),
        },
        {
            "key": "listening-decoder",
            "step": 5,
            "title": "听力解码：把真正“听见”的声音还原出来",
            "english_title": "Module 5 · Listening Decoder",
            "description": "逐句还原弱读、连读和音变，解决“词都认识却听不出来”。",
            "duration": "12 min",
            "status": "locked",
            "progress": 0,
            "primary_action": "进入潜台词与语气",
            "secondary_action": "继续循环播放",
            "quick_prompts": [
                "为什么这里听起来像 ma needa？",
                "帮我标一下弱读和连读",
                "我应该怎么跟读这一句？",
            ],
            "prompt_box": {
                "label": "解码提问",
                "placeholder": "输入你听不清的部分，例如：为什么 not feeling 会像 na feeling？",
                "button_label": "解释这一句",
            },
            "payload": {
                "audio_progress": 48,
                "accuracy": 82,
                "loop_mode": "Loop sentence",
                "original": "I'm not feeling great today, so I might need to take the afternoon off.",
                "heard_like": "I'm na feeling great today, so I ma needa take the afternoon off.",
                "tags": ["弱读 so I", "连读 need to", "吞音 not + feeling"],
                "explanations": [
                    "not 在快速语流中会弱化，和后面的 feeling 连在一起，听感更靠近 na feeling。",
                    "might need to 经常被压缩成 ma needa，核心是节奏被整体前移。",
                    "afternoon off 的重音落在 afternoon，off 轻一些，但不能完全吞掉。",
                ],
                "repeat_queue": [
                    "先跟节奏，不急着逐词咬字。",
                    "把 might need to 当成一个音块来模仿。",
                    "最后一遍再把语义和语气一起带上。",
                ],
            },
            "side_panels": [
                {
                    "title": "AI coach note",
                    "tone": "info",
                    "items": ["你已经能抓到主句结构，下一步是把音块和节奏绑在一起。", "最容易漏掉的是 so I 和 need to。"],
                },
                {
                    "title": "核心词",
                    "tone": "success",
                    "items": ["call in sick", "not feeling great", "take the afternoon off"],
                },
                {
                    "title": "本课进度",
                    "tone": "warning",
                    "items": ["已完成 4 / 8 模块", "4.8 minutes spent"],
                },
            ],
            "footer_panels": _module_panels(
                "为什么这里会听不出",
                [
                    "英语口语按音块走，不按单词边界走。",
                    "弱读后信息承重会变化，重音词更突出。",
                    "连读常把语法词缩成“背景音”。",
                ],
                "跟读反馈",
                ["影子跟读分 82 / 100", "节奏稳定，但 need to 还可更轻", "下一步：关注语气层"],
            ),
        },
        {
            "key": "subtext-and-tone",
            "step": 6,
            "title": "潜台词与语气：理解关系与态度",
            "english_title": "Module 6 · Subtext & Tone",
            "description": "不只看字面意思，还要听出说话人为什么这么说。",
            "duration": "9 min",
            "status": "locked",
            "progress": 0,
            "primary_action": "进入句型拆解",
            "secondary_action": "再做一道语气题",
            "quick_prompts": [
                "这里为什么不用 I am sick？",
                "这一句是在试探还是在请求？",
                "如果更急一点，语气会怎么变？",
            ],
            "prompt_box": {
                "label": "语气解读",
                "placeholder": "写下你对一句话的理解，例如：这句是不是在委婉请假？",
                "button_label": "校准我的理解",
            },
            "payload": {
                "cases": [
                    {
                        "quote": "I'm not feeling great today.",
                        "label": "委婉开场",
                        "meaning": "并不是要详细报病情，而是在给请假请求铺垫情绪与合理性。",
                    },
                    {
                        "quote": "I might need to take the afternoon off.",
                        "label": "试探式提出需求",
                        "meaning": "用 might need to 给对方留空间，也让表达显得克制。",
                    },
                    {
                        "quote": "I just wanted to give you a heads-up.",
                        "label": "关系维护",
                        "meaning": "重点是“我提前告诉你”，体现责任感而不是甩手离开。",
                    },
                ],
                "tone_shift": [
                    {"label": "更直接", "text": "I need to take the afternoon off because I'm sick."},
                    {"label": "更柔和", "text": "I may need to step away this afternoon if I don't feel any better."},
                ],
                "signals": [
                    "not feeling great 传达“控制住情绪”的克制感。",
                    "heads-up 是关系型表达，表明自己在替对方着想。",
                    "整段话在寻求理解，而不是单方面宣布。",
                ],
            },
            "side_panels": [
                {"title": "语气标签", "tone": "info", "items": ["真诚", "克制", "礼貌"]},
                {"title": "理解升级", "tone": "success", "items": ["能解释 why 而不只是 what", "开始区分请求与试探"]},
                {"title": "练习建议", "tone": "warning", "items": ["先判断关系，再判断语气强弱"]},
            ],
            "footer_panels": _module_panels(
                "关系与态度信号",
                [
                    "not feeling great 不是抱怨，而是体面地交代原因。",
                    "might need to 体现的是“商量感”。",
                    "heads-up 是典型的合作型沟通标记。",
                ],
                "强弱测验",
                ["更委婉表达 2 个", "更直接表达 2 个", "下一步：提炼可迁移句型"],
                "info",
                "success",
            ),
        },
        {
            "key": "pattern-extraction",
            "step": 7,
            "title": "句型拆解：抽出可反复复用的骨架",
            "english_title": "Module 7 · Pattern Extraction",
            "description": "从原句抽出骨架，再替换槽位，形成你自己的表达模板。",
            "duration": "7 min",
            "status": "locked",
            "progress": 0,
            "primary_action": "进入输出练习",
            "secondary_action": "再练一个变体",
            "quick_prompts": [
                "给我 3 个这个骨架的替换版本",
                "这个句型适合写邮件吗？",
                "我这句替换自然吗？",
            ],
            "prompt_box": {
                "label": "骨架造句",
                "placeholder": "试着套用骨架造一句，例如：I might need to work from home today.",
                "button_label": "检查句型",
            },
            "payload": {
                "patterns": [
                    {
                        "skeleton": "I might need to [do X] today.",
                        "swaps": ["take the afternoon off", "work from home", "join later"],
                    },
                    {
                        "skeleton": "I just wanted to give you a [heads-up] before [event Y].",
                        "swaps": ["quick note", "today's meeting", "the afternoon sync"],
                    },
                ],
                "practice_attempts": [
                    "I might need to work from home today.",
                    "I just wanted to give you a quick note before today's call.",
                ],
                "revision_tip": "如果对象是老板，第二句里 quick note 可以换回 heads-up，语气会更自然。",
            },
            "side_panels": [
                {"title": "本课骨架", "tone": "success", "items": ["I might need to [do X] today.", "I just wanted to give you a [heads-up] before [event Y]."]},
                {"title": "迁移规则", "tone": "info", "items": ["替换内容要和场景保持一个语域", "不要把中文逻辑硬塞进骨架里"]},
                {"title": "做对的标志", "tone": "warning", "items": ["保持语气缓冲", "补充对象和时间线"]},
            ],
            "footer_panels": _module_panels(
                "换词练习",
                ["I might need to work from home today.", "I might need to step out for an hour.", "I just wanted to give you a heads-up before the demo."],
                "AI 句型建议",
                ["保留 might 这一层缓冲", "如果要更正式，可把 wanted 改成 wanted to let you know"],
            ),
        },
        {
            "key": "output-challenge",
            "step": 8,
            "title": "输出练习：把这节课真正用出来",
            "english_title": "Module 8 · Output Challenge",
            "description": "最后用写作或模拟沟通把今天的表达真正输出一遍。",
            "duration": "10 min",
            "status": "locked",
            "progress": 0,
            "primary_action": "完成本课",
            "secondary_action": "换一个任务",
            "quick_prompts": [
                "帮我润色这段请假消息",
                "这句会不会太直接？",
                "给我一个更职场一点的版本",
            ],
            "prompt_box": {
                "label": "输出任务作答",
                "placeholder": "写下你的请假消息、邮件或角色扮演回复。",
                "button_label": "批改我的答案",
            },
            "payload": {
                "tasks": [
                    {"type": "填空复述", "status": "done", "prompt": "I ___ need to take the afternoon off.", "expected": "might"},
                    {"type": "场景写作", "status": "active", "prompt": "给老板发一条 2 句 IM，请求今天下午休息。", "expected": "礼貌、简洁、要有补偿动作"},
                    {"type": "角色扮演", "status": "todo", "prompt": "HR 问你是否有人可 cover，你该怎么回应？", "expected": "说明安排方案"},
                ],
                "draft": "Hi, I'm not feeling well today, so I might need to take the afternoon off. I'll keep an eye on Slack and make sure the client notes are updated before I step away.",
                "scores": [
                    {"label": "核心表达", "value": 89},
                    {"label": "语法准确", "value": 91},
                    {"label": "语感地道", "value": 77},
                    {"label": "人际距离", "value": 85},
                ],
                "feedback": [
                    "你已经自然地用了 might need to，语气控制得不错。",
                    "keep an eye on Slack 是一个很好的补偿动作。",
                    "第一句的 not feeling great 会比 not feeling well 更贴近原场景。",
                ],
            },
            "side_panels": [
                {"title": "今日任务", "tone": "success", "items": ["先完成场景写作", "再挑战角色扮演"]},
                {"title": "评分重点", "tone": "info", "items": ["表达是否自然", "是否体现礼貌和责任感", "有没有复用本课句型"]},
                {"title": "闭环完成", "tone": "warning", "items": ["完成后将自动进入复习队列", "生成精听笔记卡"]},
            ],
            "footer_panels": _module_panels(
                "评分维度",
                ["核心表达 89", "语法准确 91", "语感地道 77", "人际距离 85"],
                "AI 反馈结果",
                ["语气整体自然", "建议把 not feeling well 替换成 not feeling great", "下一轮可练更正式的邮件表达"],
                "success",
                "info",
            ),
        },
    ]

    return {
        "id": "lesson-soft-language",
        "title": "Soft language at work",
        "topic_cn": "请病假状态表达",
        "source_type": "podcast",
        "source_value": "Apple Podcasts",
        "source_label": "Apple Podcasts · 11:24 · B1-B2",
        "level": "B1-B2",
        "length": "11:24",
        "goal": "在不看字幕时听懂职场沟通，并学会礼貌请假的表达方式。",
        "summary": "围绕一次临时请半天病假的播客片段，训练从听懂到会用的完整链路。",
        "status": "analysis_ready",
        "completed_modules": 0,
        "analysis": {
            "headline": "30 秒内，自动拆成一堂完整精听课",
            "summary_cards": [
                {"label": "CEFR", "value": "B1-B2", "note": "词汇难度适中，适合有基础的听力强化。"},
                {"label": "核心表达", "value": "26 条", "note": "包含请假、沟通缓冲、补偿动作等高频表达。"},
                {"label": "语速", "value": "126 WPM", "note": "接近真实播客语速，适合作为进阶材料。"},
            ],
            "processing_steps": [
                {"label": "Whisper 转写", "status": "done"},
                {"label": "难度测级", "status": "done"},
                {"label": "场景识别", "status": "done"},
                {"label": "八步方案生成", "status": "done"},
                {"label": "复习队列预置", "status": "done"},
            ],
            "transcript": {
                "title": "Why saying 'I'm not feeling great' sounds softer",
                "subtitle": "Apple Podcasts · 11:24 · Speaker B",
                "excerpt": "I'm not feeling great today, so I might need to take the afternoon off. I just wanted to give you a heads-up before the meeting starts.",
                "context": "这是一次真实职场请假场景。说话人没有直接说 I am sick，而是先用 softer opening 缓冲，再提出需求并补充 heads-up。",
                "highlights": ["softer opening", "pre-emptive notice", "workplace tone"],
            },
            "voice_signals": [
                "not + feeling 在快速语流里出现明显弱化",
                "might need to 被压缩成 ma needa 的听感",
                "heads-up 是关系维护型词块，语气很重要",
            ],
            "recommendations": [
                "先完成 Module 1-3，确保理解场景和关键表达。",
                "Module 5 建议戴耳机做 2 轮 shadowing。",
                "输出练习优先写 IM，再升级到 email 版本。",
            ],
            "plan": [
                {"step": 1, "key": "immersive-listening", "title": "沉浸听力", "duration": "8 min", "summary": "先抓语境、关系和大意。"},
                {"step": 2, "key": "vocabulary-deep-dive", "title": "核心词汇", "duration": "7 min", "summary": "只学真正能复用的表达。"},
                {"step": 3, "key": "native-vs-chinglish", "title": "Chinglish 对照", "duration": "6 min", "summary": "找到更自然的说法。"},
                {"step": 4, "key": "scene-mapping", "title": "场景映射", "duration": "8 min", "summary": "把表达迁移到你的真实语境。"},
                {"step": 5, "key": "listening-decoder", "title": "听力解码", "duration": "12 min", "summary": "听懂弱读、连读和音变。"},
                {"step": 6, "key": "subtext-and-tone", "title": "潜台词与语气", "duration": "9 min", "summary": "理解话背后的态度与关系。"},
                {"step": 7, "key": "pattern-extraction", "title": "句型拆解", "duration": "7 min", "summary": "抽出可反复迁移的骨架。"},
                {"step": 8, "key": "output-challenge", "title": "输出练习", "duration": "10 min", "summary": "把今天学的内容真正用出来。"},
            ],
        },
        "workspace": {
            "eyebrow": "Learning workspace",
            "heading": "把一次真实材料，走完从听懂到会用的八步精听",
            "subheading": "你的学习工作台会随着模块切换，持续保留当前课文、目标与 AI 教练反馈。",
            "stats": [
                {"label": "本课难度", "value": "B1-B2"},
                {"label": "预计学习", "value": "67 min"},
                {"label": "目标掌握度", "value": "82 / 100"},
            ],
            "lesson_card": {
                "title": "Soft language at work",
                "subtitle": "请病假状态表达",
                "badges": ["11:24", "B1-B2", "AI guided"],
                "objective": "今天先完成 Module 1-5，把“听见”与“说得出”连起来。",
            },
            "modules": modules,
        },
        "report": {
            "hero": {
                "title": "从“听懂一点点”，进入真正会迁移的学习闭环",
                "summary": "你已经把职场请假的表达从“知道字面意思”，推进到了“能在自己的场景里写出来”。",
            },
            "metrics": [
                {"label": "本次用时", "value": "62 min", "note": "比上周快 7%"},
                {"label": "新掌握表达", "value": "26", "note": "其中 12 个已加入复习队列"},
                {"label": "平均完成度", "value": "6.1", "note": "较上次提升 0.8"},
            ],
            "weaknesses": [
                {"label": "状态描述弱化", "value": 76},
                {"label": "补偿动作表达", "value": 43},
                {"label": "句式迁移", "value": 73},
                {"label": "语气把控", "value": 64},
                {"label": "输出稳定性", "value": 69},
            ],
            "weekly_hours": [
                {"day": "Mon", "value": 1.6},
                {"day": "Tue", "value": 1.1},
                {"day": "Wed", "value": 2.3},
                {"day": "Thu", "value": 0.9},
                {"day": "Fri", "value": 2.8},
            ],
            "journal": [
                {"date": "03/24", "title": "完成基础跟听：Soft language at work", "note": "能区分情绪和事件，但 heads-up 听感还不稳定。"},
                {"date": "03/26", "title": "今天试写：give you a heads-up", "note": "开始把补偿动作一起写出来。"},
                {"date": "03/28", "title": "输出练习：请病假 IM", "note": "AI 反馈语感已明显自然，但还可继续练更正式版本。"},
            ],
            "note_card": {
                "title": "精听笔记卡",
                "headline": "每一句，都陪你听懂",
                "summary": "本课最值得带走的，是“状态 + 需求 + 补偿动作”这一套真实可复用的请假表达逻辑。",
                "chips": ["call in sick", "heads-up", "might need to"],
            },
        },
    }


def build_home_payload(lessons: list[dict]) -> dict:
    latest = lessons[-1]
    completed_full = sum(1 for lesson in lessons if lesson["completed_modules"] >= 5)

    return {
        "hero": {
            "eyebrow": "AI Co-pilot for immersive listening",
            "title": "每一句，都陪你听懂。",
            "description": "把 YouTube、播客、英语会议音频、BBC/TED 片段自动拆成一堂八步精听课。不是冷冰冰的播放器，而是一个陪你听、陪你拆、陪你练的学习伙伴。",
            "primary_action": {"label": "开始一段精听", "route": f"/analysis/{latest['id']}"},
            "secondary_action": {"label": "先看示例课", "route": f"/workspace/{latest['id']}/immersive-listening"},
            "highlights": [
                "导入任意英文内容",
                "30 秒生成八步学习方案",
                "从听懂到会用形成完整闭环",
            ],
        },
        "composer": {
            "title": "把任意英文内容，变成一堂陪你走完的精听课",
            "description": "支持链接、推荐库和本地上传三种入口。",
            "source_types": [
                {"label": "粘贴链接", "value": "link"},
                {"label": "推荐库", "value": "recommended"},
                {"label": "本地上传", "value": "upload"},
            ],
            "placeholders": {
                "link": "例如：https://www.youtube.com/watch?v=...",
                "recommended": "例如：请病假表达 / 商务播客 / TED 教育主题",
                "upload": "例如：meeting-recording.m4a",
            },
            "goals": [
                "听懂真实口语里的缓冲表达",
                "提升会议或播客的精听稳定度",
                "把本课表达迁移到自己场景里",
            ],
            "recent_sources": [
                {"title": lesson["title"], "meta": lesson["source_label"]}
                for lesson in lessons[-3:]
            ],
        },
        "stats": [
            {"label": "完整课程", "value": f"{completed_full}", "note": "本周完成 5 个模块以上的课程数"},
            {"label": "表达入库", "value": "26 条", "note": "本周新增可复用表达"},
            {"label": "平均评分", "value": "B1-B2", "note": "当前推荐的最合适难度"},
        ],
        "weekly_picks": [
            {
                "tag": "请假 / 职场",
                "title": "请假状态表达",
                "summary": "适合练习 softer opening 与 give a heads-up。",
                "route": f"/analysis/{latest['id']}",
            },
            {
                "tag": "播客 / 商务",
                "title": "播客里的商场口语",
                "summary": "练习快速口语中的语气与补偿动作表达。",
                "route": f"/workspace/{latest['id']}/listening-decoder",
            },
            {
                "tag": "学术 / 听力",
                "title": "雅思课堂听力",
                "summary": "适合训练先抓大意，再进句型迁移。",
                "route": f"/review/{latest['id']}",
            },
        ],
        "recent_lessons": [
            {
                "id": lesson["id"],
                "title": lesson["title"],
                "subtitle": lesson["topic_cn"],
                "status": lesson["status"],
                "modules_done": lesson["completed_modules"],
            }
            for lesson in reversed(lessons[-4:])
        ],
    }


def build_review_payload(lessons: list[dict], active_lesson_id: str) -> dict:
    active = next(lesson for lesson in lessons if lesson["id"] == active_lesson_id)
    queue = [
        {"term": "call in sick", "prompt": "请写一句向主管请病假的消息", "due": "今天", "lesson_id": active_lesson_id},
        {"term": "give you a heads-up", "prompt": "什么时候适合用 heads-up？", "due": "2 天后", "lesson_id": active_lesson_id},
        {"term": "under the weather", "prompt": "把它放进一个日常聊天句子", "due": "3 天后", "lesson_id": active_lesson_id},
        {"term": "might need to", "prompt": "给出一个更委婉的请求例句", "due": "7 天后", "lesson_id": active_lesson_id},
    ]

    return {
        "active_lesson_id": active_lesson_id,
        "summary": {
            "today_target": "完成 3 张复习卡",
            "weekly_goal": "本周至少完成 3 次 ≥5 模块的精听",
            "recovered_words": "本周回收 12 个旧表达",
        },
        "queue": queue,
        "review_cards": [
            {
                "title": active["report"]["note_card"]["headline"],
                "summary": active["report"]["note_card"]["summary"],
                "chips": active["report"]["note_card"]["chips"],
                "lesson_id": active_lesson_id,
            }
        ],
    }


def build_imported_lesson(lesson_id: str, source_type: str, source_value: str, goal: str | None = None) -> dict:
    lesson = deepcopy(build_base_lesson())
    lesson["id"] = lesson_id
    lesson["source_type"] = source_type
    lesson["source_value"] = source_value or "User imported lesson"
    lesson["title"] = (source_value or "Imported lesson").strip()[:42] or "Imported lesson"
    lesson["topic_cn"] = "用户导入内容"
    lesson["summary"] = "这是基于你刚刚导入的材料生成的示例精听课，结构与真实产品一致。"
    lesson["goal"] = goal or lesson["goal"]
    lesson["source_label"] = {
        "link": "链接导入 · 09:48 · B1",
        "recommended": "推荐内容 · 12:05 · B1-B2",
        "upload": "本地上传 · 08:36 · B2",
    }.get(source_type, "导入内容 · 10:20 · B1-B2")
    lesson["analysis"]["transcript"]["title"] = lesson["title"]
    lesson["analysis"]["transcript"]["subtitle"] = lesson["source_label"]
    lesson["analysis"]["transcript"]["context"] = f"这是一段通过 {source_type} 导入的示例材料，系统已经自动完成转写、场景识别和八步方案编排。"
    lesson["workspace"]["lesson_card"]["title"] = lesson["title"]
    lesson["workspace"]["lesson_card"]["subtitle"] = lesson["topic_cn"]
    lesson["report"]["hero"]["summary"] = "你刚导入的新材料已经被拆解成完整八步学习路径，后续可继续累积复习队列。"
    return lesson
