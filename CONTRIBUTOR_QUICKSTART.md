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

## 2. 下载仓库

```bash
git clone https://github.com/TanRongbin/FortiorKnowledgeContributionSkills.git
cd FortiorKnowledgeContributionSkills
```

如果已经下载过仓库，直接进入目录即可。

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

## 4. 重启 AI CLI

安装或更新后，**彻底退出当前 Claude Code / Codex / Gemini / Copilot 进程，再重新启动**。

只新建一个聊天会话可能仍然使用旧 Skill 缓存。

## 5. 贡献工程经验

在一个已经通过 AI 完成分析、定位或修复的真实工程会话里直接说：

```text
把刚刚解决的问题总结成工程经验并贡献。
```

如果当前 CLI 支持显式 Skill 调用，也可以显式调用 `fortior-knowledge-contributor` 后再给出同样指令。

## 6. 贡献程序评审点

```text
把刚刚这个问题抽象成一个可复用的程序评审点并贡献。
```

## 7. 同时贡献两种知识

```text
把刚才的问题同时总结成工程经验和可复用评审点并分别贡献。
```

Skill 会优先使用当前对话、Git diff / commit、源码、日志、测试、波形和已有用户确认，不要求重新描述已经在上下文中的信息。

## 8. 提交前会让你确认什么

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

## 9. 成功判据

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

## 10. 更新 Skill

以后仓库更新后：

```bash
cd FortiorKnowledgeContributionSkills
git pull --ff-only
python install.py --target auto
```

如果本机同时使用多个 CLI，推荐：

```bash
python install.py --target all
```

然后彻底重启对应 AI CLI。

## 11. 检查安装位置

常见位置：

```text
Codex / Copilot:
~/.agents/skills/fortior-knowledge-contributor

Claude Code:
~/.claude/skills/fortior-knowledge-contributor

Gemini CLI:
~/.gemini/skills/fortior-knowledge-contributor

公共 runtime:
~/.fortior/runtime/fortior-knowledge-contributor
```

Windows PowerShell 可以检查：

```powershell
$paths = @(
  "$HOME\.agents\skills\fortior-knowledge-contributor\SKILL.md",
  "$HOME\.claude\skills\fortior-knowledge-contributor\SKILL.md",
  "$HOME\.gemini\skills\fortior-knowledge-contributor\SKILL.md",
  "$HOME\.fortior\runtime\fortior-knowledge-contributor\SKILL.md"
)

$paths | ForEach-Object {
    if (Test-Path $_) { "OK   $_" } else { "MISS $_" }
}
```

## 12. 常见问题

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
