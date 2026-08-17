# Fortior Knowledge Contributor — 普通贡献者安装与使用

这份文档只面向 **使用 Skill 贡献知识的人**。如果你只是安装并提交工程经验/评审点，不需要配置飞书、不需要启动 Gateway，也不需要知道任何 Table ID。

公网 Gateway：

```text
https://fortior-knowledge-contribution-gateway.onrender.com
```

普通贡献者不需要：

- GitHub 登录；
- 飞书账号；
- 飞书 App ID / App Secret；
- Base Token；
- Table ID；
- 自己运行 FastAPI / Uvicorn。

## 1. 前置条件

本机需要：

- Python 3；
- Git（或手工下载仓库 ZIP）；
- 至少一个支持本地 Agent Skill 的 AI 编程环境，例如 Claude Code、OpenAI Codex、Gemini CLI 或 GitHub Copilot。

先确认 Python：

```bash
python --version
```

## 2. 下载或更新仓库

### 第一次下载

```bash
git clone https://github.com/TanRongbin/FortiorKnowledgeContributionSkills.git
cd FortiorKnowledgeContributionSkills
```

### 如果 `git clone` 提示目录已经存在

例如：

```text
fatal: destination path 'FortiorKnowledgeContributionSkills' already exists and is not an empty directory.
```

**不要直接继续运行旧目录里的 `install.py`。** 先进入已有目录并同步最新 `main`：

```bash
cd FortiorKnowledgeContributionSkills
git status
git remote -v
git switch main
git pull --ff-only origin main
```

如果 `git pull --ff-only` 因本地改动失败，而这些本地改动又不需要保留，最安全的做法是先退出目录，把旧目录改名备份，再重新 clone；不要直接删除未知内容。

当前目录应当确实是本仓库，并且 `git remote -v` 应指向：

```text
https://github.com/TanRongbin/FortiorKnowledgeContributionSkills.git
```

## 3. 安装 Skill

### 自动检测当前 CLI

```bash
python install.py --target auto
```

### 本机同时使用多个 CLI

推荐直接：

```bash
python install.py --target all
```

### 只安装到指定 CLI

```bash
python install.py --target claude
python install.py --target codex
python install.py --target gemini
python install.py --target copilot
```

当前安装器成功执行后会打印类似：

```text
Installed Fortior skill:
  - ...\fortior-knowledge-contributor
Stable runtime: ...\.fortior\runtime\fortior-knowledge-contributor
Submit runtime: ...\scripts\submit.py
Local config: ...\.fortior\knowledge-contributor.env
Hosted Gateway: https://fortior-knowledge-contribution-gateway.onrender.com
```

**如果 `python install.py ...` 什么都不输出就直接返回命令行，优先怀疑当前目录不是最新版仓库。** 先回到第 2 节执行 `git status`、`git remote -v`、`git pull --ff-only origin main`，再重新安装。

安装器会同时安装一个独立提交 runtime：

```text
~/.fortior/runtime/fortior-knowledge-contributor
```

并创建/更新普通用户配置：

```text
~/.fortior/knowledge-contributor.env
```

默认配置应包含：

```text
FORTIOR_SUBMIT_MODE=gateway
FORTIOR_CONTRIBUTION_ENDPOINT=https://fortior-knowledge-contribution-gateway.onrender.com
```

普通贡献者不要填写任何 `FEISHU_*` Secret。

## 4. Windows 安装后立即验证

Windows PowerShell 建议使用真实用户目录，而不是依赖可能被某些 CLI 沙箱改写的 `$HOME`：

```powershell
$u = [Environment]::GetFolderPath('UserProfile')

$paths = @(
  "$u\.agents\skills\fortior-knowledge-contributor\SKILL.md",
  "$u\.claude\skills\fortior-knowledge-contributor\SKILL.md",
  "$u\.gemini\skills\fortior-knowledge-contributor\SKILL.md",
  "$u\.fortior\runtime\fortior-knowledge-contributor\SKILL.md"
)

$paths | ForEach-Object {
    if (Test-Path $_) { "OK   $_" } else { "MISS $_" }
}
```

使用 `--target all` 时，前三个 Skill 路径和公共 runtime 正常应显示 `OK`。

同时确认 Python 认为的用户目录：

```powershell
python -c "from pathlib import Path; print(Path.home())"
$env:USERPROFILE
```

两者通常应指向同一个 Windows 用户目录。如果不是同一个目录，Skill 可能被安装到了另一个用户配置下。

## 5. 重启 AI CLI

安装或更新后，**彻底退出当前 Claude Code / Codex / Gemini / Copilot 进程，再重新启动**。

只新建一个聊天会话可能仍然使用旧 Skill 缓存。

如果第 4 节已经确认对应 `SKILL.md` 存在，但 CLI 仍然看不到 Skill，再检查这个 CLI 实际使用的 Skill 目录和版本；不要重复 clone 或反复运行安装器掩盖问题。

## 6. 贡献工程经验

在一个已经通过 AI 完成分析、定位或修复的真实工程会话里直接说：

```text
把刚刚解决的问题总结成工程经验并贡献。
```

如果当前 CLI 支持显式 Skill 调用，也可以显式调用 `fortior-knowledge-contributor` 后再给出同样指令。

## 7. 贡献程序评审点

```text
把刚刚这个问题抽象成一个可复用的程序评审点并贡献。
```

## 8. 同时贡献两种知识

```text
把刚才的问题同时总结成工程经验和可复用评审点并分别贡献。
```

Skill 会优先使用当前对话、Git diff / commit、源码、日志、测试、波形和已有用户确认，不要求重新描述已经在上下文中的信息。

## 9. 提交前会让你确认什么

远程提交前，Skill 会要求确认：

- 稳定贡献用户名；
- 署名方式：用户名 / 显示名 / 匿名；
- 可见范围：公开 / 匿名公开 / 仅治理人员可见；
- 是否允许披露仓库名称；
- 是否允许披露 Commit；
- 是否允许披露相对文件路径；
- 是否允许披露必要的最小代码片段；
- AI 建议标题是否保留或修改；
- 是否有权提交，并确认未包含 Secret、Token、私钥及不必要的客户/个人信息。

如果 CLI 支持结构化问答，正常情况下这些项目会以单选/多选界面出现。

## 10. 成功判据

只有看到真实远程提交结果才算成功，例如：

```text
Validation: PASS
Submission: PASS
sink: feishu
record_id: rec...
```

`Submission: PASS` 只表示这条贡献已经进入 **待治理数据**，不表示已经成为正式 FortiorReviewPoints 规则。

如果只看到：

```text
Validation: PASS
```

但没有 `Submission: PASS`，说明内容只通过了本地校验，远程提交并未完成。

## 11. 更新 Skill

以后仓库更新后：

```bash
cd FortiorKnowledgeContributionSkills
git switch main
git pull --ff-only origin main
python install.py --target auto
```

如果本机同时使用多个 CLI，推荐：

```bash
python install.py --target all
```

然后重新执行第 4 节的安装路径检查，并彻底重启对应 AI CLI。

## 12. 常见问题

### `git clone` 说目录已经存在

说明本机已经有同名目录。这不是安装成功提示。进入已有仓库后先 `git pull --ff-only origin main`；如果它不是正确仓库或本地状态不可安全快进，先改名备份，再重新 clone。

### `python install.py` 没有任何输出

当前正式安装器成功时一定会打印安装结果。无输出通常意味着你运行了旧版/错误目录里的脚本。检查：

```bash
git status
git remote -v
git log -1 --oneline
```

然后更新 `main` 再安装。

### 第一次提交比较慢

公网 Gateway 当前运行在 Render Free。长时间无访问时会休眠，首次请求可能需要等待几十秒。客户端已经为免费冷启动预留较长超时。

### `HTTP 429`

表示当前 Gateway 触发了轻量限流。不要连续重复点击提交；稍后再试，并避免在短时间内重复发送同一贡献。

### `HTTP 502 / 503`

通常表示公网 Gateway 或 Gateway → 飞书链路暂时不可用。不要把飞书 Secret 发给任何人；保留 CLI 返回的错误文本并交给维护者排查。

### AI 只整理了内容但没有真正上传

成功必须看到 `Submission: PASS`。如果没有，请确认本地 Skill 已更新，并彻底重启 CLI 后重试。

### 我需要飞书账号吗？

不需要。普通贡献者的请求统一通过公网 Gateway 写入待治理数据。
