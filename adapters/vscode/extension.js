'use strict';
const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function assertSafe(root, target) {
  const relative = path.relative(root, target);
  if (relative.startsWith('..') || path.isAbsolute(relative)) throw new Error('目标超出项目目录');
  let current = root;
  for (const part of relative.split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    try {
      if (fs.lstatSync(current).isSymbolicLink()) throw new Error(`目标含符号链接：${current}`);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
    }
  }
}

function copyMissing(source, target, root, result) {
  assertSafe(root, target);
  if (fs.statSync(source).isDirectory()) {
    fs.mkdirSync(target, { recursive: true });
    for (const name of fs.readdirSync(source).sort()) {
      copyMissing(path.join(source, name), path.join(target, name), root, result);
    }
  } else {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    try {
      fs.copyFileSync(source, target, fs.constants.COPYFILE_EXCL);
      result.created.push(path.relative(root, target));
    } catch (error) {
      if (error.code !== 'EEXIST') throw error;
      result.preserved.push(path.relative(root, target));
    }
  }
}

function initialize(context, folder) {
  const root = fs.realpathSync(folder);
  const source = path.join(context.extensionPath, 'assets', 'wuhang-novel');
  const targetSkill = path.join(root, '.agents', 'skills', 'wuhang-novel');
  const result = { created: [], preserved: [] };
  assertSafe(root, targetSkill);
  if (!fs.existsSync(targetSkill)) copyMissing(source, targetSkill, root, result);
  else {
    if (!fs.existsSync(path.join(targetSkill, 'SKILL.md'))) {
      throw new Error('目标技能目录已存在但缺少 SKILL.md；请先备份并移开不完整的技能目录');
    }
    result.preserved.push('.agents/skills/wuhang-novel（已有技能，未混合更新）');
  }
  copyMissing(path.join(source, 'assets', 'project'), root, root, result);
  for (const name of ['2-设定', '3-大纲', '4-正文', '5-审查']) {
    const target = path.join(root, name);
    assertSafe(root, target);
    fs.mkdirSync(target, { recursive: true });
  }
  return { root, ...result };
}

function activate(context) {
  context.subscriptions.push(vscode.commands.registerCommand('soloent.initNovelKit', async () => {
    const folders = vscode.workspace.workspaceFolders || [];
    if (!folders.length) {
      vscode.window.showErrorMessage('请先打开一个小说文件夹。');
      return;
    }
    const selected = folders.length === 1 ? folders[0] : await vscode.window.showQuickPick(
      folders.map(folder => ({ label: folder.name, folder })), { placeHolder: '选择本书的项目目录' });
    if (!selected) return;
    const folder = selected.folder || selected;
    if (folder.uri.scheme !== 'file') {
      vscode.window.showErrorMessage('此初始化器仅支持本地文件系统工作区。');
      return;
    }
    try {
      const result = initialize(context, folder.uri.fsPath);
      const preserved = result.preserved.length;
      vscode.window.showInformationMessage(`武行小说项目已就绪：新建 ${result.created.length} 个文件，保留 ${preserved} 个已有项。`);
      if (result.preserved.includes('.gitignore')) {
        vscode.window.showWarningMessage('已保留原 .gitignore；请合并技能模板中的密钥与缓存忽略项。');
      }
      const doc = await vscode.workspace.openTextDocument(path.join(result.root, 'SOLOENT.md'));
      await vscode.window.showTextDocument(doc);
    } catch (error) {
      vscode.window.showErrorMessage(`初始化未完成：${error.message}。已有文件未被替换。`);
    }
  }));
}

module.exports = { activate, deactivate() {}, initialize };
