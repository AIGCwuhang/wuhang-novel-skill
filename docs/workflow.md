# 工作流与模块

## 三种起点

```text
从零开始 → Define ──┐
带着旧稿 → Guide ───┼→ Ideation → Outline → Write ↔ Review
有参考书 → Analyze ─┘                ↑          │
                                    └─ 动态修订 ┘
```

Guide 可根据现有资产直接接入某个环节；Review 可在设定、大纲和正文阶段独立使用。每完成一章暂停，不自动写到下一章。

## 七个模块

| 模块 | 方法重点 | 主要产物 |
| --- | --- | --- |
| [Define](../skills/wuhang-novel/references/define.md) | 核心梗、金手指、世界、人物、主线、爽点、事件、受众、类型边界；文风逐项确定 | 创意方向、文风 |
| [Guide](../skills/wuhang-novel/references/guide.md) | 资产扫描、属性识别、索引注册、进度定锚 | 已有稿件索引与下一步 |
| [Analyze](../skills/wuhang-novel/references/analyze.md) | 九维套路、起承转合、黄金三章、场景调度、微观节奏与自定义拆解 | 已读范围内的参考分析 |
| [Ideation](../skills/wuhang-novel/references/ideation.md) | 共创设定、机制代价、人物利益、关系博弈、地图和事件 | 设定案、角色与机制档案 |
| [Outline](../skills/wuhang-novel/references/outline.md) | 总纲→卷纲→章纲，情绪与事件规划，设定回溯、双向动态修订 | 总纲、卷纲、章纲、书名简介 |
| [Write](../skills/wuhang-novel/references/write.md) | 写前检查、分场景、完稿自检、状态回写 | 单章草稿、自检与记忆更新 |
| [Review](../skills/wuhang-novel/references/review.md) | 编辑视角检查逻辑、人物、期待感、节奏与文字 | 修改建议或审稿报告 |

## 项目参数

`.novelkit/config.json` 中的 `chapter_words.min`、`max` 控制默认章节范围。普通项目默认 2300–4000；原创微型示例为 300–900。题材、节奏和是否需要金手指由作者确认，模板仅为起点。

模板宪法中的具体禁词与节奏要求可以修改。方法强调作者掌控方向、逐项讨论，初始化不代表设定已完成。

## 记忆如何连续

静态设定保存在 `2-设定/`，当前状态保存在 `.novelkit/memory/`，总控保存索引、近期三章和下一步任务。新会话先读控制面板，再读取本次相关资料。技能升级不替换这一本书的状态文件。

统一约定详见 [project-contract.md](../skills/wuhang-novel/references/project-contract.md)。
