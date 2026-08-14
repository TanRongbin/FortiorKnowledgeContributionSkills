# Submission Security & Anti-Spam

## 目标

Fortior 的贡献入口首先要做到“任何安装 Skill 的人都能用”。因此 **GitHub、飞书或其他账号登录不是 V1 前置条件**。

公开 GitHub 仓库只让用户获得 Skill 源码，不会让用户得到飞书 App Secret。飞书凭据只放在 Contribution Gateway 服务端。

## V1：Open Contribution

默认模式：

```text
FORTIOR_GATEWAY_MODE=open
```

任何人都可提交，只要求：

- 一个稳定的 `contributor.username`；
- 完成公开/隐私必答项；
- 通过本地与服务端字段检查。

用户名只是贡献记录中的声明身份，不代表实名或已验证身份。

## V1 仍然可以做的防垃圾

这些控制不需要账号：

### 请求大小限制

限制总 payload 大小、单字段长度、数组元素数量和代码摘录长度。

### 精确去重

规范化 payload 后计算 SHA-256 `content_hash`，对短期重复请求直接返回已有结果或拒绝重复写入。

### 轻量限流

组合以下弱信号：

- 来源 IP（服务端短期使用，不需要写入飞书明文）；
- `contributor.username`；
- `client_instance_id`。

`client_instance_id` 是安装时生成的随机 UUID，可被用户重置，所以不能作为真实身份，只适合做软限流。

### 基础内容拦截

阻止：

- 明显私钥；
- 高置信 API Secret/Token；
- 超大无意义内容；
- 高频完全重复提交。

### 治理隔离

所有贡献先写 `待治理`，不会直接进入 FortiorReviewPoints 正式知识。

## V2：不登录的“编辑能力”限制

如果开放入口垃圾变多，可以把 Gateway 改成：

```text
FORTIOR_GATEWAY_MODE=edit_code
```

贡献者仍然不需要 GitHub/飞书账号，但必须提供一个贡献编辑码：

```text
X-Fortior-Edit-Code: ...
```

可以：

- 一个团队共用一个码；
- 每个合作团队一个码；
- 每个人一个码；
- 随时吊销或轮换。

这比强制 GitHub 登录更符合“任何工具用户都能贡献”的目标。

## V3：可选身份验证

未来可以增加 GitHub、飞书、企业 SSO 等验证，但只能作为：

- 提高额度；
- 提升信誉；
- 获得快速治理；
- 提供可信署名。

不应成为公共贡献的唯一入口。

## 建议飞书治理字段

两张贡献表都保存：

- 提交ID
- 贡献者用户名
- 显示名
- 可选第三方用户名
- 客户端实例ID
- 身份验证状态
- 公开范围
- 公开署名方式
- 是否允许公开仓库/Commit/路径/代码摘录
- 权利确认
- 内容哈希
- 风控状态
- 风控分
- 客户端版本
- 治理状态

## 重要边界

客户端 Skill 是开源代码，恶意用户可以修改本地检查。因此：

- 本地检查主要防误操作；
- 真正不可绕过的大小限制、去重和限流必须在 Gateway；
- 飞书 Secret 永远不进入普通贡献者客户端。
