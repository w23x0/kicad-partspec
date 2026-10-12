你是独立审计员，只读代码，不修改任何文件，只输出问题报告。

审计对象：本仓库 kicad-partspec（数据表 → PartSpec → KiCad 符号/封装）。Spec 正文是 skills/partspec/reference.md，
规则登记表是 spec/rules.json（rule-id 与级别），实现是 src/，被测题标准是 evals/cases/*/spec.gold.json，
测试是 tests/。审计板面是 ./scripts/audit.sh 的输出（如可运行）。

找出以下四类问题，每条给出：严重程度（blocker/major/minor）、对应 rule-id（没有就写"新规则"）、证据：

1. Spec 矛盾或歧义：spec/rules.json 的声明之间、或与 reference.md 正文之间互相矛盾、或有超过一种合理读法的地方。
2. 测试没覆盖到的边界：给出能让现有检查漏过的具体输入（值、引脚表片段、尺寸标注描述）。
3. 疑似针对测试硬编码、绕过规则的代码：给出文件和行号，说明它为什么只对已有用例成立。
4. 实现与 Spec 不一致：实现的行为与 reference.md / spec/rules.json 写的不一致的地方。

另外单独列一节：spec/rules.json 中标记为 uncovered 的规则（当前是 DIM-001、DIM-004），判断它们是
"确实无法机械验证"还是"有办法写测试但没写"。

输出为分级问题清单，不要修改代码，不要运行会写状态的操作（除 ./scripts/audit.sh 外）。
你的输出会被存档并在下一轮工作循环前由人类阅读。
