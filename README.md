# Fortior Knowledge Contribution Skills

Open-source Agent Skills for capturing engineering experience and contributing structured software review knowledge.

本仓库只存放公开、可复用的知识贡献 Skill。它把真实软件开发过程中的知识拆成两类：

- **Engineering Experience（工程经验）**：问题如何发生、如何定位、根因、修复、验证与经验教训。
- **Review Point（程序评审点）**：以后评审其他项目时应该检查什么、如何检查、什么情况判 Fail、正确实践是什么。

两类知识使用独立 Schema、独立飞书数据表、独立治理状态；Experience 可以作为 Review Point 的来源证据，但不会自动被提升成正式评审点。

## 支持的 AI 编程环境

本项目使用 `SKILL.md` 为核心，按 Agent Skills 开放格式组织。

| 平台 | 用户级安装位置 | 本仓库安装器 |
|---|---|---|
| OpenAI Codex | `~/.agents/skills/` | 支持 |
| GitHub Copilot / Copilot CLI | `~/.agents/skills/` 或 `~/.copilot/skills/` | 支持 |
| Claude Code | `~/.claude/skills/` | 支持 |
| Gemini CLI | `~/.gemini/skills/` | 支持 |
| 其他 Agent Skills 兼容工具 | 自定义目录 | `--target custom --path ...` |

> 同一个 `SKILL.md` 是知识源；安装器只负责复制到不同宿主的发现目录，不为每个平台维护不同逻辑。

## 一键安装

克隆仓库后：

```bash
python install.py --target auto
```

`auto` 会检测本机已安装的 CLI，并安装到对应位置。

安装到所有已支持平台：

```bash
python install.py --target all
```

只安装某个平台：

```bash
python install.py --target agents
python install.py --target claude
python install.py --target gemini
python install.py --target copilot
```

其中 `agents` 是 OpenAI Codex 与 GitHub Copilot 都支持的开放用户级目录。

Gemini CLI 也支持直接从 GitHub 安装 Skill：

```bash
gemini skills install https://github.com/TanRongbin/FortiorKnowledgeContributionSkills
```

## 使用方式

解决完一个真实问题后，可以直接对本地 AI CLI 说：

```text
把刚刚解决的问题贡献为工程经验
```

或：

```text
使用 fortior-knowledge-contributor，把这个问题抽象成程序评审点
```

Skill 会优先复用当前对话和当前 Git 仓库上下文，并按需检查 `git diff`、Commit、相关源码、日志、测试和用户确认，不要求工程师重新描述一次完整问题。

## 提交前必须由用户确认

AI 自动总结完成后，**不得直接上传**。Skill 必须先向用户确认至少这些信息：

1. 贡献者用户名；
2. 本次贡献是工程经验还是评审点（如果此前未明确）；
3. 是否允许公开：`公开` / `匿名公开` / `仅治理人员可见`；
4. 公开时采用什么署名；
5. 是否允许公开仓库名、Commit、文件路径、必要代码摘录；
6. 是否确认自己有权提交这些材料，且已清理密钥、客户隐私和其他敏感信息；
7. AI 生成的标题和关键结论是否需要人工修改。

完整规则见 `skills/fortior-knowledge-contributor/references/pre-submit-questionnaire.md`。

## 公开仓库 ≠ 所有人能写飞书

公开 GitHub 仓库只是让所有人都能**下载 Skill**。它不会自动给任何人飞书 App Secret，也不会自动获得飞书写权限。

生产环境推荐：

```text
公开 Skill
   ↓
用户确认 + 本地 Schema/隐私检查
   ↓
Fortior Contribution Gateway
   ↓
身份验证 / 限流 / 去重 / 垃圾检测 / 风险评分
   ↓
飞书：待治理贡献
   ↓
Owner 治理
   ↓
FortiorReviewPoints
```

普通贡献者**不直接持有飞书密钥**。只有 Owner 内部调试模式才允许 `feishu_direct`。

防垃圾的关键不是客户端 Skill，因为恶意用户可以修改开源代码；真正强制执行的风控必须放在服务端 Gateway。设计见 `docs/SECURITY_AND_ANTI_SPAM.md`。

## 身份

每条贡献至少保存一个 `contributor.username`。生产 Gateway 还应写入服务端验证后的身份字段，例如：

- `verified_identity_provider = github`
- `verified_username`
- `verified_user_id`
- `identity_verified = true`

客户端自己上报的用户名只能作为显示信息，不能当作可信身份。

## 飞书

仓库提供：

- `bootstrap_feishu.py`：在同一个多维表格中建立/补齐 `工程经验贡献` 和 `评审点贡献` 两张表；
- `submit.py`：按贡献类型写入对应表；
- `config.example.env`：本地 Owner 配置模板。

公开用户默认应使用 Gateway，不应获得 `FEISHU_APP_SECRET`。

## 目录

```text
.
├─ install.py
├─ README.md
├─ LICENSE
├─ docs/
│  ├─ ARCHITECTURE.md
│  └─ SECURITY_AND_ANTI_SPAM.md
└─ skills/
   └─ fortior-knowledge-contributor/
      ├─ SKILL.md
      ├─ config.example.env
      ├─ schemas/
      │  ├─ experience-contribution.schema.json
      │  └─ review-point-contribution.schema.json
      ├─ references/
      │  ├─ pre-submit-questionnaire.md
      │  └─ evidence-and-privacy.md
      └─ scripts/
         ├─ submit.py
         └─ bootstrap_feishu.py
```

## License

MIT
