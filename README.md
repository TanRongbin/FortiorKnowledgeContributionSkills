# Fortior Knowledge Contribution Skills

Open-source Agent Skills for turning solved engineering work into reusable **Engineering Experience** and **Review Point** contributions.

本仓库面向两类读者：

- **普通贡献者**：安装 Skill，在 Claude Code / Codex / Gemini CLI / Copilot 等本地 AI 编程环境中，把已经解决的问题整理并提交到 Fortior 待治理知识库。
- **维护者 / Owner**：维护公网 Gateway、飞书路由、Schema、测试和治理接入。

> 普通贡献者不需要 GitHub 登录、飞书账号、飞书 App Secret、Base Token 或 Table ID。安装器默认使用托管公网 Gateway。

## 普通贡献者：从这里开始

完整的下载安装、更新、调用、成功判据和常见问题请直接看：

**[CONTRIBUTOR_QUICKSTART.md](CONTRIBUTOR_QUICKSTART.md)**

最短安装流程：

```bash
git clone https://github.com/TanRongbin/FortiorKnowledgeContributionSkills.git
cd FortiorKnowledgeContributionSkills
python install.py --target auto
```

如果本机同时使用多个 CLI，推荐：

```bash
python install.py --target all
```

安装完成后彻底关闭并重新启动 AI CLI。

## 这个 Skill 贡献什么

### Engineering Experience（工程经验）

记录一个真实问题当时如何发生、如何定位、根因是什么、怎样修复、如何验证以及从中得到什么经验。

### Review Point（程序评审点）

把已有证据抽象成以后评审其他工程时可复用的检查规则，包括评审问题、检查方法、失败判据、风险、正确实践、验证方式和适用范围。

两者是不同知识实体。一条工程经验可以支持一个或多个评审点，但不会因为提交了一条经验就自动升级成通用评审规则。

## 使用示例

解决完一个真实工程问题后，可以直接对 AI 说：

```text
把刚刚解决的问题总结成工程经验并贡献。
```

或：

```text
把这个问题抽象成一个可复用的程序评审点并贡献。
```

也可以一次要求两种：

```text
把刚才的问题同时总结成工程经验和可复用评审点并分别贡献。
```

支持显式 Skill 调用的 CLI 也可以使用 `fortior-knowledge-contributor` 的显式调用方式。

Skill 会优先利用当前会话、Git diff / commit、源码、日志、测试、波形和用户确认，不要求用户重新描述已经存在于上下文中的信息。

## 提交前的人机确认

远程提交前必须让用户明确确认：

- 贡献者用户名与署名方式；
- 可见范围：公开 / 匿名公开 / 仅治理人员可见；
- 是否允许披露仓库名、Commit、相对文件路径、最小代码片段；
- 是否有权提交，且已排除 Secret、Token、私钥及不必要的客户/个人信息；
- AI 建议标题是否保留或修改。

宿主 CLI 提供结构化单选/多选能力时，Skill 应优先使用选择器，而不是要求用户手工输入整套问卷。

## 当前公共提交链路

```text
AI coding session
   ↓
fortior-knowledge-contributor
   ↓
本地结构化与隐私预检
   ↓
https://fortior-knowledge-contribution-gateway.onrender.com
   ↓
Fortior Contribution Gateway
   ↓
飞书待治理数据
   ├─ Review Point → 现有评审点表
   └─ Engineering Experience → 工程经验贡献表
```

提交成功只表示 **进入待治理数据**，不代表已经成为 FortiorReviewPoints 正式规则。

公网 Gateway 当前提供：

```text
GET /health   进程健康状态
GET /ready    Gateway → 飞书认证与两张目标表可用性检查
POST /v1/contributions
```

Render Free 空闲后可能冷启动，因此首次提交有时会比平时慢几十秒。

## 支持的安装位置

| 平台 | 用户级 Skill 目录 |
|---|---|
| OpenAI Codex | `~/.agents/skills/fortior-knowledge-contributor` |
| GitHub Copilot / Copilot CLI | `~/.agents/skills/fortior-knowledge-contributor` |
| Claude Code | `~/.claude/skills/fortior-knowledge-contributor` |
| Gemini CLI | `~/.gemini/skills/fortior-knowledge-contributor` |
| 其他 Agent Skills 兼容工具 | `install.py --target custom --path ...` |

独立提交 runtime 安装到：

```text
~/.fortior/runtime/fortior-knowledge-contributor
```

普通用户配置保存在：

```text
~/.fortior/knowledge-contributor.env
```

默认模式为 `gateway`，默认公网地址已由安装器配置，不需要普通贡献者手工填写飞书信息。

## 维护者文档

普通贡献者不需要运行 Gateway、mock、飞书建表或 Render 部署命令。维护工作请看：

- [TESTING.md](TESTING.md) — 维护者测试与故障定位
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 知识与提交流程架构
- [docs/SECURITY_AND_ANTI_SPAM.md](docs/SECURITY_AND_ANTI_SPAM.md) — 当前安全边界和后续增强
- [gateway/README.md](gateway/README.md) — Gateway 本地开发与部署说明

仓库根目录中的 `submit.py`、`setup_feishu_base.py`、`bootstrap_feishu.py`、`inspect_feishu.py`、`quick_test.py`、`view_mock.py` 属于维护/测试辅助工具，不是普通贡献者安装 Skill 的必需步骤。

## Repository layout

```text
skills/fortior-knowledge-contributor/  Skill、Schema、运行脚本与参考规则
gateway/                               公网 Contribution Gateway 与测试
docs/                                  架构和安全说明
install.py                             跨 CLI 安装/更新入口
render.yaml                            托管 Gateway 的 Render Blueprint
CONTRIBUTOR_QUICKSTART.md              普通贡献者上手说明
TESTING.md                             维护者测试说明
```

## License

MIT
