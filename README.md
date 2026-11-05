# 许老师聊健康

134****2834 / 小红书号 **2689093300** 的健康内容工作区。手机资料已于 2026-11-05 改名并读回确认。

定位、操作授权和发布要求见 [AGENTS.md](AGENTS.md)，受众假设和实验见 [ACCOUNT_DNA.md](ACCOUNT_DNA.md)。

迁移到新电脑请先读 [HANDOFF.md](HANDOFF.md)。本分支为健康项目的独立私有备份。

## 当前生产入口（v4）

Python 3.9+。ReAct 是编辑动作与工具观察循环。生产路径已参考邻近工程
`/Users/mac/work/ai/redbook_ai/apps/editor-agent/` 的模型适配器与独立编辑设计。
复用 **Codex CLI 已有登录**，固定 `gpt-6.1-sol`、`medium`；不导出登录令牌，不复制另一个项目的 API Key。
模型在隔离临时目录运行，read-only sandbox，禁用 shell、联网、MCP、插件等执行工具；
它只能提出结构化动作，宿主决定读取哪些已采来源、补什么公开证据。

以下 NEW_TASK 是占位路径，须先准备新任务和当轮核实的权威来源；旧 v3 packet 仅供历史查阅。

```bash
python3 -m health_agent produce \
  --task research/NEW_TASK/task.json \
  --packet research/NEW_TASK/packet.json \
  --run research/NEW_TASK/new-run --max-calls 44
# 已有运行需要追加公开证据时，保持原任务/原来源不变，再加 --resume
python3 -m unittest discover -s tests -v
```

实际流程：读取50篇参考中的相关正文与当轮权威依据 → 两篇选题独立审读 →
逐篇首屏审读 → 制作正文与按信息需要决定张数的图片方案 →
独立盲读者、内容编辑、事实编辑分别重新调用。
`REVISE` 的具体理由返回写作者；公开文字不变不能反复重抽 GO。
缺证据会输出 `evidence-request.json`，暂停交给宿主检索后续跑。
任何必审项失败、假引用、未读取来源都不能被顶层 GO 绕过。

`run/calls/` 留存每次公开输入、结构化输出、模型、推理档位、耗时和 token 用量；
`trace.jsonl`、`state.json` 保留动作、版本、修改理由与标准快照。
不记录密钥或内部思维。`READY_FOR_ASSETS` 仅是文字阶段通过；
实际成图还要另行读图与事实审核，图片 hash、审核与发布证据分别保存。
模型审读是编辑辅助，不构成医学认证或流量效果保证。

以下为保留的原始 Responses API 路径，需自行配置环境变量；与 v3 CLI 实际调用分开记账。

## 启动

在本机私有环境设置 `OPENAI_API_KEY`。可参考 `.env.example`，但程序**不自动加载 .env**，应由终端或密钥管理器注入。不要在聊天、截图和版本库里放密钥。

```bash
python3 -m health_agent check
python3 -m health_agent run --brief '为工作忙的普通成年人选一个减少久坐的图文选题'
python3 -m unittest discover -s tests -v
```

`OPENAI_BASE_URL` 可选，默认 `https://api.openai.com/v1`，仅允许 HTTPS；自定义地址需确认为可信服务。缺 Key、联网原文打不开、模型不可用、响应截断或 API 出错会明确失败并保留已完成阶段，不用模拟数据冒充成功。

## 产物

`data/<时间-随机ID>/`：

- `state.json`：当前状态、账号配置、来源、当前稿件、摘要、审核与 token 用量。
- `events.jsonl`：工具动作与结果记录，不保存请求密钥或内部思维。
- `draft-vN.json`、`review-vN.json`：各版本文本稿和审核；改稿必须重新审核。
- 仅 GO 后导出 `content.md`、`mobile-handoff.json`，明确 `published=false`。

程序检查每条来源是否来自当轮工具返回的真实引用，并要求对应原文已由工具打开；审核需完整覆盖全部登记论断。语义证据充分性依然依赖模型审核，不能把结构验证当成专业医学认证。最终图片中的论断、图示、字与正文也必须审核。

测试全部使用明确标识的虚构夹具，不调用真实 API、不操作手机、不发布；它们验证流程和异常分支，不能证明模型输出质量或账户 API 可用性。

## 手机执行交接

这个本地 Python CLI 不会继承 Codex 的 Mobile MCP 连接；它生成供 Codex 接续的文字发布包。现有手机已能被 Codex 实际读屏和操作，后续由 Codex 按 AGENTS.md 接续：

1. 读取 GO 的精确版本，生成最终图片并查看每张成图；核对来源与全文，不凭逐页文案推定图片合格。
2. 核当轮平台规则、健康内容所需资质与 AI 标识。来源/平台证据不足时保留待处理状态。
3. 重新列设备，打开正确应用分身，确认小红书号 2689093300；编辑预览与已审核包逐字对应。
4. 用户已授权合格内容发布，无需逐篇再确认。只在系统验证码、必须真人验证等确实依赖用户时暂停。
5. 记录 hash、目标账号与 SUBMITTING，单次点击发布；结果不明记 UNKNOWN，先查证，不重复提交。
6. 读回目标账号下对应笔记和公开状态、保存证据，才记 PUBLISHED；平台处理中记 PLATFORM_REVIEW。

未部署定时器、未设发布频率；两篇已发布，详见下方发布记录。生产与修改状态以实际日志为准，发布状态只以目标账号公开读回为准。

## 接口依据

- [GPT-6.1 Sol：支持 medium，工具调用使用 Responses API](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
- [Function calling：传递 function_call_output 与完整输出项](https://developers.openai.com/api/docs/guides/function-calling)
- [Web search：域名过滤、原文打开和 URL 引用](https://developers.openai.com/api/docs/guides/tools-web-search)

## 已完成的50篇参考正文回测

本轮通过 Mobile MCP 采集62条，剔除12条后，保留50篇真实正文。4位作者：摸鱼养生专业户30、养生搭子小满6、丁香医生13、茶茶1。关注已从本账号关注列表读回确认，数据与覆盖范围见 `benchmarks/manifest.json`。

```bash
# 本地规则回归：读取真实原文及冻结标注，要求至少50篇，校验hash、短正文和重复
python3 -m health_agent backtest
# 真实模型核源+审核：需要OPENAI_API_KEY；逐篇独立检索，再审核；可断点续跑
python3 -m health_agent backtest --mode live
```

回归结果见 [50篇逐篇报告](reports/backtest50.md)。第一轮最低哨兵覆盖40/42，修订后42/42；这是对已读样本的规则回归，不能当模型准确率。8篇未预设哨兵也不等于医学合格。没有独立盲测数据；图片未逐张核查；尚未完成真实API回测。

50篇的正文在 `data/backtest-50.json`。按用户换电脑要求，原始资料已纳入本次私有迁移备份，不得将本仓库公开或对外全文转载。完整数据、标注、规则和结果都有hash，禁止用另一个样本覆盖后仍沿用旧结论。

`config/reference-playbook.json` 已接入选题、制作、审核的输入；`health_agent/editorial.py` 会预检标题、封面、正文与逐页文案。必须改写项不能被模型GO绕过；待核源项交给独立审核，不能直接判真或判假。

真实API模式会对每篇做权威原文检索和一次独立模型审核（通常每篇至少2次请求，50篇约100次请求，另有联网成本）；不调用写作、手机发布或互动工具。未配置Key时立即失败，不产生成功回测结果。

## 本轮真实成品

2026-11-05：参考学习后由agent实际产出两篇、5张原创操作示意；完成文字三审与最终全图两审；两篇已于2026-11-05发布并在2689093300账号下读回，见reports/publication-20261105.json。

- [带饭：分装、保冷和复热](content/2026-11-05/agent-v3/p01/article.md)
- [睡眠：三个时间怎样安排](content/2026-11-05/agent-v3/p02/article.md)
- [调用与审核回执](reports/agent-v3-live-receipt.json) / [迭代记录](reports/agent-v3-iteration.md)

本批43次完整模型回执、4次中断用量未知；不是50篇live回测。图片为宿主依agent方案执行的确定性排版，工具在tools/，使用本机Pillow与中文字体。当前renderer针对这两篇的操作示意设计，其他题需按自己的方案制作，不能机械套图。

已有run目录禁止静默重置；后续标准/协议变化请新建run，追加证据续跑才使用--resume。

## 新增50篇记忆已接入

两篇发布后采集60条新候选，排除8条、备用2条，冻结与旧库不重复的50篇。24篇正向表达样本、26篇反例，均为真实模型拆解；不等于医学核验或流量效果回测。逐篇观察范围、10条可迁移规则见[学习报告](reports/reference-new50.md)，实际调用见[回执](reports/reference-new50-live-receipt.json)。

`ProductionAgent`自动读取`config/reference-library.json`，校验原文、图片、拆解及旧库身份后加入来源索引。选题和成稿须先实际读源，并分别说明标题与内容迁移；缺引用或迁移字段会被拒绝。参考帖不允许充当`official_fact`。库及协议更新后请新建run。

一次真实`gpt-6.1-sol / medium`接入探针已从生产入口读取4篇正向样本，通过连续引文和迁移检查，见[接入证据](reports/reference-new50-integration.json)。这次探针没有制作、审核放行或发布额外稿件。
