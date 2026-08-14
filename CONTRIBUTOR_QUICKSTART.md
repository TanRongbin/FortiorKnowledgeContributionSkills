# Fortior Knowledge Contributor — 快速测试

公网 Gateway：

```text
https://fortior-knowledge-contribution-gateway.onrender.com
```

普通贡献者不需要 GitHub 登录、飞书账号、飞书 App Secret、Base Token 或 Table ID。飞书凭据仅保存在 Gateway 服务端。

## 1. 安装

需要本机已有 Python 3 和正在使用的 AI 编程 CLI（Claude Code / Codex / Gemini CLI / Copilot）。

```bash
git clone https://github.com/TanRongbin/FortiorKnowledgeContributionSkills.git
cd FortiorKnowledgeContributionSkills
python install.py --target auto
```

也可以指定平台：

```bash
python install.py --target claude
python install.py --target codex
python install.py --target gemini
python install.py --target copilot
```

安装完成后彻底关闭并重新启动 AI CLI。

## 2. 贡献工程经验

在一个已经通过 AI 完成分析/修复的真实工程会话里说：

```text
$fortior-knowledge-contributor
把刚刚解决的问题总结成工程经验并贡献。
```

## 3. 贡献程序评审点

```text
$fortior-knowledge-contributor
把刚刚这个问题抽象成一个可复用的程序评审点并贡献。
```

也可以一次要求两种：

```text
$fortior-knowledge-contributor
把刚才的问题同时总结成工程经验和可复用评审点并贡献。
```

Skill 会优先利用当前对话、Git diff/commit、源码、日志、测试和用户确认。提交前会要求确认贡献者用户名、可见范围、署名方式、源码/仓库披露边界和权利/隐私声明。

## 4. 成功判据

只有看到真实提交结果时才算成功：

```text
Submission: PASS
sink: feishu
record_id: rec...
```

`Submission: PASS` 表示贡献已经进入待治理数据，不代表已经被批准为正式 FortiorReviewPoints 规则。

## 5. 免费 Gateway 冷启动

当前公网 Gateway 使用 Render Free。长时间没有访问时服务会休眠，第一次提交可能比平时慢几十秒；客户端已经为免费冷启动预留更长等待时间。

## 6. 更新

以后更新 Skill：

```bash
cd FortiorKnowledgeContributionSkills
git pull
python install.py --target auto
```

安装器会更新 Skill/runtime，并保留用户自己的身份与隐私配置。默认公网 Gateway 为：

```text
https://fortior-knowledge-contribution-gateway.onrender.com
```
