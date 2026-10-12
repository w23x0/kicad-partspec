# 交接（HANDOVER）

状态截至 2026-10-12，分支 `next`。本文件是“继续开始”的入口：新会话先读它，再运行 `./scripts/audit.sh`。

## 刚完成的事

附件那套“宪法 + Spec/测试/审计 + 阶段提示词 + 循环驱动”方法论已适配落地，提交 `abc572c` 与 `7bd1def`：

- `AGENTS.md`：宪法（工作循环、红线、Gold 修改仲裁协议、审计分层、架构约定）。
- `spec/rules.json`：27 条规则（`MPN/PIN/STAT/SCH/SRC/DIM/LAND/GEN` 八个模块，MUST/SHOULD），索引 `skills/partspec/reference.md`。
- `tests/test_rules.py`：253 个用例，测试名即 rule-id；SCH/SRC 是穿过真实检查器的夹具测试，其余是对 23 个 gold 的语料测试。措辞守卫仍在 `tests/test_skill_*.py`，不计入审计。
- `scripts/audit.sh`（实现 `scripts/audit.py`）：唯一进度指标。板面 = 规则计数 + `gold-spec` / `gold-quotes` / `gold-build` 三套件；上一板存 `.audit/last.json`（已 gitignore），据此报“退步”。
- `scripts/loop.sh` + `scripts/prompts/`：无人值守循环，每轮独立分支，绿板即停，无进展熔断，每 5 轮跑一次独立审计提示词并存档 `.audit/reports/`。
- `spec/ISSUES.md`：Spec 争议登记处（当前为空）。

## 当前板面（已验证）

```
规则总数: 27   有测试: 25   通过: 25   未通过: []   退步: []
未覆盖:   [DIM-001, DIM-004]
gold-spec: 23/23   gold-quotes: skipped   gold-build: 23/23 (20 mods, 3 skipped)
```

全量：`549 passed, 27 skipped`，ruff/mypy 干净，工作树干净。

## 继续时的三件事（按优先级）

1. **点亮引文层**：PDF 不在仓库。挂上数据表目录后跑
   `./scripts/audit.sh --datasheets DIR`（或设 `PARTSPEC_DATASHEETS`），`gold-quotes` 应从 `skipped` 变为实数。
   预期全绿；若某 case 引文失败，按仲裁协议处理，不得改测试绕开。
2. **首次真独立审计**：循环里的独立审计只用桩agent 验证过路径，从未由真实第二模型跑过。以
   `scripts/prompts/independent_audit.md` 为 prompt 另起一个只读会话，重点看它列出的“uncovered 规则是否真的无法机械验证”。
3. **DIM-001 / DIM-004 的毕业判定**（需人类拍板）：前者（min/max、nom、X±t 的取值形态）缺机械裁判途径，后者
   （括号参考值不得成为封装尺寸）没有独立夹具。两条的候选出路写在 `tests/test_rules.py` 头部注释；决定后要么补测试，
   要么在 `spec/rules.json` 明确标注“不可机械验证”并写进 `spec/ISSUES.md`。

## 无人值守启动方式

```bash
AGENT_CMD="claude -p" MAX_ROUNDS=20 STALL_LIMIT=3 ./scripts/loop.sh
```

`AGENT_CMD` 可换任何无头 agent。循环只认板面；每轮提交信息形如 `[audit] round N: 25/27 passing; 未通过: [...]`。
工作树脏时循环拒绝启动（`ALLOW_DIRTY=1` 可强制）。

## 环境事实

- 虚拟环境 `.venv/`（`python` 不在 PATH，用 `.venv/bin/python`）；`kicad-cli` 与 `pdftotext` 均已安装。
- 数据表 PDF 按 `evals/README.md` 的 revision + SHA-256 获取，不放仓库。
- 分支：`next`（当前），另有 `w/r3writeup`、`w/r4fix`、`w/r5fix`、`main`、`legacy`。
