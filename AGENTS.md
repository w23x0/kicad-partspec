# 项目宪法

本文件对每个新会话生效。把它当流程读，把红线当禁令读。

# 项目目标

`kicad-partspec`：数据表 PDF → 带页码与引文的 PartSpec JSON → 经验证的 KiCad 符号与封装。**唯一的进度指标是
`./scripts/audit.sh` 的输出**（规则通过数 / 未通过 / 退步 / 未覆盖，加三个 gold 套件）。一个工作会话只推进一轮。

# Spec 与测试在哪

| 层 | 位置 | 说明 |
|---|---|---|
| Spec（权威散文） | `skills/partspec/reference.md` | 抽取规则的唯一正文。**不要另建第二处 spec**；登记表只是索引 |
| 规则登记表 | `spec/rules.json` | 每条规则的 `id`、`level`（MUST/SHOULD）、声明、正文位置；审计据此算"规则总数/未覆盖" |
| 规则测试 | `tests/test_rules.py` | 每个测试函数以 `test_<RULE-ID>_<slug>` 命名，审计按节点名归属规则 |
| 语料（被判题标准） | `evals/cases/*/spec.gold.json` | 23 个金标准 case，`review.md` 记录每案裁决 |
| 措辞守卫 | `tests/test_skill_*.py` | 钉住 reference.md 的**文字**，是历史回归守卫；**不是**规则测试，审计不计数 |
| 检查器单测 | `tests/test_spec_checks.py` 等 | 检查器属性（一次性报错、消息可操作、CLI 退出码） |

rule-id 格式 `<模块>-<三位数字>`，模块：`MPN` `PIN` `STAT` `SCH`（spec 结构） `SRC`（引文校验） `DIM` `LAND` `GEN`（生成/加载）。

# 工作循环（每次会话只做一轮）

1. 运行 `./scripts/audit.sh`，读取 `未通过` / `退步` / `未覆盖` 列表。
2. 选 1 条规则（或同一模块下少数几条）。
3. 读 `skills/partspec/reference.md` 的对应规则和 `tests/test_rules.py` 的对应测试。
4. 实现（或修 gold，或澄清规则文字），直到这些测试通过。
5. 重新运行 `./scripts/audit.sh`，确认：目标规则通过，且没有其他规则退步、三个套件不退步。
6. 提交，message 格式 `[RULE-ID] 简述`。
7. 发现 Spec 矛盾或歧义 → 写入 `spec/ISSUES.md`，**不要自行拍板**。

# 红线（违反任何一条等于任务失败）

- 禁止为了让测试通过而修改、弱化、跳过 `tests/test_rules.py` 中已有的断言——它就是本仓库的 conformance 测试。
- 禁止针对测试输入硬编码、特判、按 case 名或文件名分支。
- 禁止吞掉错误、降低断言强度、把失败降级成警告。
- 禁止删除或跳过测试。`skipif` 仅限环境缺失（无 `pdftotext`、无 `kicad-cli`、无 `PARTSPEC_DATASHEETS`）。
- 实现必须对"同类但不同的输入"也成立。**把散文断言（`assert "..." in REFERENCE`）当行为验证是作弊**——措辞守卫钉文字，规则测试钉行为，两者不可互相顶替。
- 想改测试、改规则等级、改 Spec 正文 → 写 `spec/ISSUES.md` 等人类确认。

# Gold 修改仲裁协议（本仓库特有）

`evals/cases/*/spec.gold.json` 是被判题标准，历史上 `fix_gold_*` 提交确实纠正过 gold（round 4/5 合计 9 处，每次都由引文
或渲染页证据支持）。允许修改，但必须同时满足三条，缺一条即作弊：

1. **证据**：该 case 的 `review.md` 写明改了什么、依据哪一页哪句话；引文必须过 `check_quotes`。
2. **重跑**：改完后重跑受影响 round 的 `python evals/score.py --extracted …`，确认已有运行不被单方面洗分。
3. **提交**：message 以 `[GOLD]` 开头并附证据摘要。

# 审计分层（为什么 audit.sh 不是一锅端）

- **确定性层，每轮跑**：规则测试（`tests/test_rules.py`）、`gold-spec`（`verify_spec`）、`gold-build`（生成 + `kicad-cli` 加载）。
  这三层决定退出码。
- **评估层，隔轮跑**：`gold-quotes`（引文按页校验，需要数据表 PDF：`./scripts/audit.sh --datasheets DIR` 或
  `PARTSPEC_DATASHEETS`；PDF 不在仓库里，缺失时该层打印 `skipped` 且不影响退出码）；`python evals/score.py`（对模型抽取打分，
  非确定性，只在评估轮次跑）。
- 进度判定用"确定性层不退步 + 评估层分数不降"双闸；连续无进展由循环脚本熔断（见 `scripts/loop.sh` 的 `STALL_LIMIT`）。

# 架构约定

- `src/` layout，hatchling 打包；`scripts/` 只放审计与驱动，**不 import `src`**。
- 模块边界：`spec/`（模型+加载） → `sexpr/`（读写） → `gen/`（符号/封装生成） → `verify/`（spec/引文/符号/封装/kicad-cli 五层检查）
  → `api.py`（CLI 与 MCP 共用的操作） → `cli.py` / `mcp_server.py`。检查只追加 `Finding`，不抛异常。
- 测试分层见上表；新规则先进 `spec/rules.json` 和 `tests/test_rules.py`，再动实现。
- 生成的符号面向 KiCad 9 文件格式；可选工具缺失时降级为警告，不是失败。

# 独立审计

每 `AUDIT_EVERY` 轮（默认 5），把 `scripts/prompts/independent_audit.md` 原样交给**另一个**模型实例跑（只读，不改代码），
报告落 `.audit/reports/`。它找四类问题：Spec 矛盾/歧义、测试没覆盖的边界（给具体输入）、疑似针对测试的硬编码（给文件和行号）、
实现与 Spec 不一致。每条标注严重程度和 rule-id。

# 驱动一个无人值守循环

```bash
AGENT_CMD="claude -p" MAX_ROUNDS=20 STALL_LIMIT=3 ./scripts/loop.sh
```

每轮独立分支（`audit/round-N`）、跑一轮工作循环、跑审计、按板面摘要提交，`未通过: []` 且无退步即停。
`AGENT_CMD` 换成任何无头 agent 命令；循环本身不理解 agent，只理解审计板面。
