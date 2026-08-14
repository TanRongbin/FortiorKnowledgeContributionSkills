# Submission Security & Anti-Spam

## 先明确一个边界

**公开 GitHub 仓库不会让所有人获得飞书写权限。**

公开意味着所有人能读取、fork 和安装 Skill。只要飞书密钥没有进入仓库，普通用户就不能直接调用你的飞书应用身份。

真正出现“任何人都能提交”的时刻，是未来你公开一个 Contribution Gateway endpoint。因此风控必须设计在 Gateway。

## Production Gateway 必须执行的控制

### 1. 身份验证

推荐要求 GitHub 登录或其他可验证身份。服务端生成：

- `verified_identity_provider`
- `verified_username`
- `verified_user_id`
- `identity_verified`

不得信任客户端自己填写的 `github_username` 作为已验证身份。

未验证身份可以选择：

- 拒绝生产提交；或
- 只进入隔离队列，绝不进入正常治理列表。

### 2. 限流

至少按以下维度组合限流：

- verified user id
- IP / network fingerprint（只保存必要的不可逆摘要）
- submission token

建议初始策略：

- 新用户：每小时 5 条、每天 20 条；
- 已建立信誉用户：提高额度；
- 短时间突发重复内容：直接节流。

具体阈值应该配置化，不硬编码进 Skill。

### 3. Schema 与大小限制

服务端重新验证，绝不能因为客户端已经验证过就跳过。

必须限制：

- 总 JSON 字节数；
- 单字段长度；
- 数组元素数量；
- URL 数量；
- evidence 数量；
- 代码摘录长度。

### 4. 去重和幂等

服务端规范化内容并生成 `content_hash`。

至少检查：

- 相同 user + content_hash；
- 近似标题 + 高相似正文；
- 同一 repo/commit/problem 的重复提交；
- 同一个 `submission_id` 的重试。

### 5. 垃圾/恶意内容评分

建议形成 `risk_score`，信号包括但不限于：

- 大量重复字符或无意义文本；
- 广告链接密度；
- 与软件/嵌入式工程完全无关；
- 极低信息量却大量提交；
- 相同账号短时批量变体；
- 敏感凭据模式；
- 被历史治理标记为垃圾的用户。

输出：

- `clean`
- `suspected_spam`
- `blocked`

任何自动模型评分都只用于路由，Owner 仍可纠正误判。

### 6. 信任等级

推荐：

- `new`：新贡献者，全部人工治理；
- `normal`：正常贡献者；
- `trusted`：稳定高质量贡献者，可减少人工前置检查；
- `restricted`：只进入隔离队列；
- `blocked`：拒绝提交。

### 7. 飞书只接收 Gateway 的服务端写入

生产环境不要把：

- `FEISHU_APP_SECRET`
- `tenant_access_token`
- 可长期写入的其他 token

放到公开仓库、Skill、安装脚本或客户端配置模板中。

Owner 本地 `feishu_direct` 只用于管理和调试。

## 建议写入飞书的治理元数据

两张贡献表都建议拥有：

- 提交ID
- 贡献者用户名
- GitHub用户名（客户端声明）
- 已验证用户名（Gateway 写入）
- 身份验证状态
- 公开范围
- 公开署名方式
- 是否允许公开仓库名
- 是否允许公开 Commit
- 是否允许公开文件路径
- 是否允许公开代码摘录
- 权利确认
- 内容哈希
- 风控状态
- 风控分
- 客户端版本
- 提交时间
- 治理状态

这样垃圾记录即使进入飞书，也可以被过滤视图隔离，而不参与 Sites / FortiorReviewPoints 后续同步。
