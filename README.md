# 武行·网文创作 Skill

把作者、编辑与编剧的创作经验整理为 AI 可以跟随的长篇网文工作流：从新书立项，到设定、大纲、逐章写作、编辑审稿与连载记忆。

**作者：武行 · 当前版本：0.2.0 预览版 · 许可范围待作者明确。**

🎬 **[视频使用说明（B 站）](https://www.bilibili.com/video/BV1cz8i67ELD/)**

视频演示的版本可能与当前版本不同，但大致创作流程一致，可配合本项目说明观看。安装方式、文件路径和界面如有差异，以当前版本文档为准。

## 选择你的使用方式

| 你使用的工具 | 安装说明 | 下载预览版 |
| --- | --- | --- |
| Codex | [安装 Skill 或预览插件](docs/install-codex.md) | [Skill ZIP](https://github.com/AIGCwuhang/wuhang-novel-skill/releases/download/v0.2.0/wuhang-novel-skill-v0.2.0.zip) · [插件 ZIP](https://github.com/AIGCwuhang/wuhang-novel-skill/releases/download/v0.2.0/wuhang-novel-codex-plugin-v0.2.0.zip) |
| WorkBuddy | [导入技能包](docs/install-workbuddy.md) | [WorkBuddy ZIP](https://github.com/AIGCwuhang/wuhang-novel-skill/releases/download/v0.2.0/wuhang-novel-workbuddy-v0.2.0.zip) |
| 支持 VSIX 的编辑器 | [安装编辑器扩展](docs/install-vscode.md) | [VSIX](https://github.com/AIGCwuhang/wuhang-novel-skill/releases/download/v0.2.0/wuhang-novel-skill-0.2.0.vsix) |
| 希望阅读或改造方法 | [Skill 入口](skills/wuhang-novel/SKILL.md) · [流程全览](docs/workflow.md) | 本仓库源码 |

安装包见 [v0.2.0 Releases](https://github.com/AIGCwuhang/wuhang-novel-skill/releases/tag/v0.2.0)；本地构建产物位于 `dist/`。GitHub 自动生成的 Source code ZIP 是完整源码，不是 WorkBuddy 的专用导入包。

**验证范围：**已做的检查与未验证部分分别记录在 [验证报告](docs/validation.md)。WorkBuddy ZIP 是待实际宿主导入验证的候选包；不代表进入官方市场。基础创作不要求另配 API Key，全书批量梗概是可选增强。

## 这套方法帮助你做什么

- **先定边界。** 把题材、目标读者、核心梗、情感承诺和不想写的内容说清楚。
- **把创意变成可写的方案。** 讨论世界、主线、人物利益与关系博弈，以及适用题材中的金手指代价和成长路线。
- **逐层细化。** 总纲 → 卷纲 → 章纲 → 场景，让开写前有明确的章节任务。
- **持续校准。** 写前核对设定和前章，写后核对范围、文风、接续、字数和机制。
- **管理连载记忆。** 用文件保存角色状态、伏笔、近期情节和下一章任务，新会话从项目状态恢复。
- **允许改线。** 新剧情出现时回溯设定和大纲，并同步相关文件。

适合希望与 AI 逐步共创、愿意决定方向并审阅产出的作者。默认模板偏向商业网文连载，字数、节奏和文风禁忌可以按题材调整。每章完成后暂停，由作者决定是否继续。

## 三分钟开始

1. 按上表安装完整技能包。
2. 新建一个用于这本书的文件夹，在工具中打开或指定它。
3. 输入：

> 使用武行小说创作技能，在我指定的小说文件夹中初始化项目。我想从零开始，请先和我讨论题材边界、核心梗与预期。

也可以从已有素材开始：

> 我已有大纲和三章正文。请先读取并建立索引，确认现有进度，再建议下一步。保留原稿位置。

或者只做一个环节：

> 使用武行小说创作技能，审查当前卷纲的人物动机、情绪节奏和伏笔，不重走新书立项。

## 一本书的文件夹

```text
我的小说/
├── SOLOENT.md                 # 项目总控，保留旧名称，不要求 SoloEnt 软件
├── .novelkit/
│   ├── config.json            # 字数和题材偏好
│   ├── constitution/MASTER.md # 本书的创作宪法
│   └── memory/                # 角色状态、伏笔与线索
├── 1-边界/                    # 作者预期、文风、可选参考分析
├── 2-设定/
├── 3-大纲/
├── 4-正文/
└── 5-审查/
```

技能安装资源与小说项目分开保存。升级技能不会替换作者已经修改的项目规则或稿件。重复初始化只补缺文件。

## 看一个实际例子

[《渡口账册》微型原创示例](examples/demo-novel/README.md) 展示了设定 → 章纲 → 正文 → 自检 → 角色与伏笔回写。为了便于阅读，示例使用 300–900 字的演示范围；普通新项目默认 2300–4000 字。示例由 AI 为本项目编写，供查看流程，不是作者既有作品或商业成效证明。

## 文档与开发

- [流程全览](docs/workflow.md) · [常见问题](docs/faq.md) · [从 0.1.5 迁移](docs/migration.md)
- [方法与工程变更说明](docs/provenance.md) · [发布前清单](docs/release-checklist.md)
- [更新记录](CHANGELOG.md) · [当前授权状态](LICENSE)
- [预览版发布说明](docs/release-notes.md)

Python 工具只需 Python 3.9+ 标准库。查看命令帮助可加 `--help`。可选梗概工具需要支持 Chat Completions 的服务商和用户自己的配置；不会在安装或初始化时调用接口。

在仓库根目录验证、构建：

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_project.py
python3 tools/build_release.py
```

## 关于作者

武行，依据自身网文作者、编辑与编剧经验整理本流程。原说明书中的公开渠道：公众号、抖音、小红书「武行」；B 站「责编武行」「悟饭呐你可长点心吧」。

作品的创作判断、最终审阅与取舍由作者完成。审稿模块中仍保留原版对部分 AI 辅助规则尚在优化的说明。
