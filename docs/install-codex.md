# 在 Codex 中使用

本项目当前为预览版，未加入官方市场。下面分别说明本地安装、GitHub 下载与插件预览。Skill、插件和 VSIX 是不同入口，不要重复安装同名能力。

[观看视频使用说明（B 站）](https://www.bilibili.com/video/BV1cz8i67ELD/)。视频版本可能不同，但大致创作流程一致；安装方式和路径以本文为准。

## 本地方式：项目级 Skill

1. 解压 `wuhang-novel-skill-v0.2.0.zip`，取得完整 `wuhang-novel/` 文件夹。
2. 将它复制到小说项目的 `.agents/skills/` 下，得到 `.agents/skills/wuhang-novel/SKILL.md`。保留 references、assets、scripts 等配套目录。
3. 在 Codex 中打开小说项目，查看技能是否出现；未显示时重新打开项目或重启客户端。
4. 说：“使用武行小说创作技能，在当前文件夹初始化新书项目。”然后说明从零开始、导入旧稿或分析参考书。

如果希望多个项目共用，可按当前客户端支持的用户技能位置安装。官方当前列出的用户目录为 `~/.agents/skills/`；不同版本可能仍使用历史目录，以该版本文档和技能列表为准。

无需先安装现有 `.vsix`。本项目只生成安装资源，不自动写入你的用户级技能目录。

## 从 GitHub 安装

用户可复制以下自然语言给 Codex：

> 请使用 skill-installer，从这个 GitHub 仓库安装 skills/wuhang-novel：https://github.com/AIGCwuhang/wuhang-novel-skill。

这是给安装器的请求，不是终端命令。安装完成后确认技能已出现，再指定小说项目并初始化。

## 插件预览

项目根 `plugin.json` 打包统一 Skill，`.agents/plugins/marketplace.json` 提供仓库级本地目录。可以在支持此功能的 Codex/ChatGPT 桌面版本中，将该项目作为本地插件来源，按插件页面完成安装与测试。已安装独立 Skill 时先停用其中一个，避免同名技能重复。

支持市场命令的 CLI 可使用：

```sh
codex plugin marketplace add AIGCwuhang/wuhang-novel-skill
```

此命令添加来源，不等于已安装插件。继续在宿主插件界面安装并检查技能；界面和功能可因版本不同而变化。本地记录文件没有经过真实宿主市场安装验证，见 [验证报告](validation.md)。插件 ZIP 是插件内容包，不承诺客户端提供任意 ZIP 的直接导入入口。

## 安装后验收

- 能找到武行技能，且没有被重复加载。
- 在空文件夹初始化后，能看到 `SOLOENT.md`、五个创作目录与 `.novelkit`。
- 重复初始化不替换作者修改过的内容。
- 从零模式不强制要求样板书。
- 新会话能从控制面板与记忆恢复进度。

来源（2026-11-05 核对）：[OpenAI Skills](https://learn.chatgpt.com/docs/build-skills)、[插件打包与本地市场](https://developers.openai.com/plugins/build/plugins)。
