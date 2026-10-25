# 手动更新贡献Skill

用户更新本地仓库后，由CLI核对HEAD、未提交修改与实际宿主skills目录，不需要自动更新服务。

```text
python -B install.py --target custom --path "<宿主实际skills父目录>"
python -B install.py --target custom --path "<同一父目录>" --replace
python -B install.py --verify "<同一父目录>/fortior-knowledge-contributor"
```

首次安装省略replace。原有target/auto/all入口继续保留，但推荐明确实际目录；不能只根据CLI名称猜宿主已加载。安装同时更新所选Skill和`~/.fortior/runtime/fortior-knowledge-contributor`，保留备份；任一复制失败回滚本轮其它目标。只读核验不会提交任何内容。

已有`~/.fortior/knowledge-contributor.env`的模式、端点、凭据、实例ID保持；只在首次安装复制默认配置，更新版本字段不切换local_only为gateway。不要上传本机配置和凭据。旧包备份确认后由用户自行清理；重载宿主后再提交新案例。

用户只负责描述踩坑案例、证据、条件、修复与验证，并明确署名、隐私和提交权利；提交前仍须确认。knowledge_extension记录新增价值与边界，推荐关系只供治理参考，不宣称已成为正式规则。提交成功只证明网关接收/飞书入池（按实际回执），不等于站点引入、语义整合、审批和发布成功。

来源对象与原始JSON保留结构，不把对象转换成字符串。不为了填字段编造芯片、反例或测试。正式层级与合并由Owner治理，用户无需维护规则ID、Hub或MotorGo，也不应得到Owner GitHub/飞书凭据。

package-identity.json记录当前软件节点与整包摘要；ZIP缺Git时为unknown，不假冒最新。此安装器不校验托管网关今天是否在线，真实提交链另由Owner账号验证，不用测试样例污染正式池。
