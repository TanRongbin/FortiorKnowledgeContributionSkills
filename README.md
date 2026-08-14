# Fortior Knowledge Contribution Skills

Open-source Agent Skills for capturing engineering experience and contributing structured software review knowledge.

本仓库只存放公开、可复用的知识贡献 Skill。任何人都可以下载安装，不要求 GitHub、飞书或其他平台账号。

知识分成两类：

- **Engineering Experience（工程经验）**：问题如何发生、如何定位、根因、修复、验证与经验教训。
- **Review Point（程序评审点）**：以后评审其他项目时应该检查什么、如何检查、什么情况判 Fail、正确实践是什么。

Experience 与 Review Point 使用独立 Schema、独立飞书数据表和独立治理流程。

## 设计原则：开放贡献，不绑定账号

第一版采用 **Open Contribution**：

```text
任何安装 Skill 的用户
   ↓
AI 自动总结
   ↓
用户填写用户名 + 公开范围等必答项
   ↓
本地检查
   ↓
Fortior Contribution Gateway（无需登录）
   ↓
基础限流 / 去重 / 大小检查
   ↓
飞书待治理
```

**不要求 GitHub 登录。** GitHub、飞书账号或其他身份验证以后只能作为可选增强，不能成为所有用户贡献的前置条件。

## 支持的 AI 编程环境

| 平台 | 用户级安装位置 | 支持 |
|---|---|---|
| OpenAI Codex | `~/.agents/skills/` | ✅ |
| GitHub Copilot / Copilot CLI | `~/.agents/skills/` | ✅ |
| Claude Code | `~/.claude/skills/` | ✅ |
| Gemini CLI | `~/.gemini/skills/` | ✅ |
| 其他 Agent Skills 兼容工具 | 自定义目录 | ✅ |

## 一键安装

```bash
python install.py --target auto
```

安装到所有支持位置：

```bash
python install.py --target all
```

或指定平台：

```bash
python install.py --target codex
python install.py --target copilot
python install.py --target claude
python install.py --target gemini
```

每次首次安装会生成一个随机 `FORTIOR_CLIENT_INSTANCE_ID`。它**不是账号，也不是身份认证**，只作为未来重复提交和滥用分析的弱信号。

## 使用

解决完一个真实问题后，对本地 AI CLI 说：

```text
把刚刚解决的问题贡献为工程经验
```

或：

```text
把这个问题抽象成程序评审点并贡献
```

Skill 会优先利用当前对话、`git diff`、Commit、相关源码、日志、测试与用户确认，不要求重新描述一次完整问题。

## 提交前必须人工选择

AI 生成内容后不能立即上传。至少要确认：

1. **贡献者用户名**（不要求是真名，也不要求任何第三方账号）；
2. 工程经验 / 程序评审点；
3. 公开范围：`公开` / `匿名公开` / `仅治理人员可见`；
4. 公开署名：用户名 / 显示名 / 匿名；
5. 是否允许未来公开仓库名、Commit、文件路径、必要代码摘录；
6. 是否有权提交且已排除密钥、客户隐私等敏感内容；
7. AI 建议标题是否保留或修改。

详见 `skills/fortior-knowledge-contributor/references/pre-submit-questionnaire.md`。

## 防垃圾：第一版先轻量，后续可逐步收紧

开放贡献不等于飞书密钥公开。普通用户只知道 Gateway 地址，飞书 App Secret 只保存在服务端。

V1 Gateway 不登录，但至少做：

- 请求大小限制；
- 必填字段校验；
- `content_hash` 精确去重；
- 按 IP / 用户名 / client_instance_id 的轻量限流；
- 所有记录默认 `待治理`。

未来如果垃圾量变大，可以**不改 Skill 主流程**，只把 Gateway 模式从：

```env
FORTIOR_GATEWAY_MODE=open
```

改为：

```env
FORTIOR_GATEWAY_MODE=edit_code
```

然后只向允许贡献的人发一个“贡献编辑码”。它不要求 GitHub/飞书账号，也比账号体系更符合当前目标。

## Gateway 参考实现

仓库包含无需登录的参考 Gateway：

```text
gateway/app.py
```

它支持两种后端：

```text
mock    本地测试，不访问飞书
afeishu 真实写入飞书（环境变量值实际使用 feishu）
```

推荐第一次先用 `mock`。

### 5 分钟本地测试

```bash
python -m pip install -r gateway/requirements.txt
python gateway/test_gateway.py
```

预期：

```text
Gateway mock tests: PASS
```

完整的 **Skill → Gateway mock → 飞书直写 → Gateway → 飞书 → 真实 AI Skill** 测试步骤见：

```text
TESTING.md
```

## 飞书

`bootstrap_feishu.py` 会非破坏性创建/补齐：

- `工程经验贡献`
- `评审点贡献`

两张表都会保存贡献者用户名、公开权限、client instance、内容哈希、风控状态和治理状态。

## License

MIT
