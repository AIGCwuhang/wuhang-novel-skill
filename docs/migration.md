# 从 0.1.5 迁移

先备份小说项目，保留原 `.vsix`、`.soloent/skills/wuhangnovellong/` 和所有现有稿件。本版不自动搬迁旧项目。

1. 按目标工具安装新技能 `wuhang-novel`，停用旧技能入口以避免重复路由。
2. 在原小说项目运行新初始化器。它补缺模板，不替换已有 `SOLOENT.md`、创作宪法和记忆。
3. 检查原总控开头的 `.soloent/skills/wuhangnovellong/` 固定路径。将固定安装路径说明改为“使用当前安装的武行小说创作技能”，保留这一本书的索引和进度。
4. 将各处 `docs/MASTER.md`、`state.json`、`状态追踪表.md` 旧约定合并到 `.novelkit/constitution/MASTER.md` 和 `.novelkit/memory/`。先比较内容，不直接删除旧文件。
5. 在 `.novelkit/config.json` 填写本书实际章节字数范围。宪法中的作者自定义规则保持有效。
6. 用“检查进度”核对现有设定、最后完成章、待收伏笔和下一步，确认没有把模板空值替换到真实状态上。

旧的中文目录名与文件名称保持支持。技能命名变为 `wuhang-novel`，旧模块名称作为统一技能内的流程继续存在。

本版没有从旁边的真实小说目录导入任何素材，公共示例独立编写。
