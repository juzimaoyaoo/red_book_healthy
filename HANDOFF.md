# 换电脑交接 · 2026-11-06

此分支完整保存「许老师聊健康」工程、两批各50篇参考、原始截图和拆解、模型调用回执、两篇成品及公开发布证据。先读本文件，再读 AGENTS.md、ACCOUNT_DNA.md、LEARNINGS.md。

## 获取工程

目标仓库：`https://github.com/juzimaoyaoo/red_book_healthy`，分支 `main`。2026-11-06 核验仓库为 public；用户在获知当前可见性后明确要求先上传，因此按最新授权执行公开上传。这不是 private 备份。此前误推到 redbook_ai 的远程分支已经删除。

```bash
git clone https://github.com/juzimaoyaoo/red_book_healthy.git
cd red_book_healthy
python3 -m unittest discover -s tests -v
python3 tools/verify_handoff.py
```

工程不包含 SSH 私钥、Codex 登录凭证或 API Key。后续推送仅使用本健康工程专属仓库。

## 运行条件

- Python 3.9+，核心 agent 仅使用标准库。执行离线检查不会调用模型或发布。
- 真实生产使用已经安装并正常登录的 Codex CLI，固定 `gpt-6.1-sol`、`reasoning.effort=medium`。新电脑自行完成正常登录，不复制另一台机器的认证文件；模型不可用时不要静默换型号。
- `python3 -m health_agent produce --task TASK --packet PACKET --run NEW_RUN`。先创建新任务与当轮核实的权威来源 packet；历史 v3 文件不是新稿任务。协议已更新，必须新建运行，不续用历史 GO。
- 旧 `run` / `backtest --mode live` 为另一路 HTTP API，需要环境变量 `OPENAI_API_KEY`；与 Codex CLI 回执分开记账。不要把密钥写进仓库。
- 重新排版图片时安装 Pillow；macOS 默认使用 PingFang。其他系统可通过 `HEALTH_CJK_FONT` 指定已安装中文字体路径。改字体会改变换行，必须重新审实际成图。已有成品 PNG 无需重绘。
- Mobile MCP 由新电脑的 Codex 环境连接；Python 工程不会自动获得手机工具。重新列设备并完成正常 USB/系统授权。历史设备 ID 不能当作当前连接状态。

## 已发布，禁止重复提交

账号：小红书号 **2689093300**，绑定 **134****2834**，昵称「许老师聊健康」。历史使用 Redmi K40S 桌面第三屏的小红书分身；普通小红书为另一账号。每次发布前核小红书号，不能只核昵称/包名。

- 带饭稿：<https://xhslink.cn/o/1Xg3yqwAlDb>，3张图。
- 睡眠稿：<https://xhslink.cn/o/AFhRDMIxElj>，2张图。

两篇2026-11-05提交并从目标账号独立打开读回，均为 PUBLISHED。证据入口 `reports/publication-20261105.json`、`data/publication-20261105/`；最终成品 `content/2026-11-05/agent-v3/`。旧 walk/vegetables 包是退回历史稿，不能当待发合格稿。任何旧压缩包/历史快照状态与发布事实冲突时，以最新发布记录为准。

## 参考记忆与真实调用

旧50：`data/backtest-50.json`、`benchmarks/manifest.json`。两轮规则回归不是模型准确率，未做50篇 live 医学回测。

新50：`research/reference-new50-20261105/manifest.json` 冻结，原文/截图/拆解在 `data/reference-new50-20261105/`。60候选中50入库、8排除、2备用；24正向表达、26反例；260张已读截图；41篇采齐标示图片，9篇仅完整正文和已读首图。不能声称50套轮播全图医学审核。

`config/reference-playbook.json` 有10条样本支撑的规则；`reference_memory.py` 自动校验并载入50个正文来源和50个视觉来源。选题、成稿必须实际读取相关正向样本并说明迁移，不能只挂编号。参考内容绝不成为权威医学事实。

历史生产43次完整模型调用，另4次中断用量未知；新参考拆解12次、接入探针1次。分别查 `reports/agent-v3-live-receipt.json`、`reports/reference-new50-live-receipt.json`、`reports/reference-new50-integration.json`。探针不是新稿，也不是医学盲测。

历史回执保留旧电脑绝对路径以维护证据原貌。当前参考库通过 `config/reference-library.json` 的 `capture_root` 精确映射原采集路径，仍校验原文件与图片 hash；不要全局替换历史记录路径或重新冻结已有证据。历史采集脚本是当时批次工具，直接重跑前须检查其路径和输出目标。

## 接续工作

1. 先运行离线交接校验，确认两批资料和成品齐全。
2. 如继续生产，按 AGENTS.md 核最新健康事实和平台规则，建立新任务、新运行，执行选题、写作、独立编辑、最终成图审读。
3. 已有用户授权发布合格内容，无需逐稿再问；仅真人验证等交给用户。核账号、预览、AI标识后记录 SUBMITTING，点击一次，公开读回后才记 PUBLISHED。
4. 尚未安排后台调度或运行频率，没有离线持续运营任务。迁移本身不追加发布内容。
