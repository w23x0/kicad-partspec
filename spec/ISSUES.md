# Spec 议题（ISSUES）

规则矛盾、歧义、不可实现、测试不合理——写在这里，等人类确认。**不要自行拍板。**

格式：

```
## <rule-id 或 "新规则"> 一句话问题
- 现象：
- 两种读法：
- 各自的证据（页码 + 引文）：
- 建议：
- 状态：open | settled（ settled 时写明结论落在哪：reference.md 哪一节 / 哪个 test / 哪个 review.md）
```

历史裁决的去处（不要在这里重新决定）：
- round 4 的争议裁定记录在 `evals/runs/round4_adjudication.md`；
- 每案的 KiCad 分歧与读图裁决在各 case 的 `review.md`；
- 已成文的规则修订在 `skills/partspec/reference.md`。

## DIM-004 三个 gold 把括号参考值记成封装尺寸，与 reference.md 正面冲突（+ round 4 自身也分裂）

- 现象：
  - `skills/partspec/reference.md` 的括号值段（约 132-137 行）："Values in parentheses on a drawing
    are reference dimensions … they may be used for a `land_*` value and must not become a package
    dimension: a parenthesised `(0.15) TYP` across a lead in a package outline is not a
    `lead_thickness`, and if that is the only thickness callout on the sheet, leave `lead_thickness`
    out rather than record it." `spec/rules.json` DIM-004（MUST）同义："A parenthesised reference
    value never becomes a package dimension."
  - 三个 gold 恰好记了这种值：`txs0108e_tssop20` `lead_thickness` nom 0.15，p.28，quote
    `(0.15) TYP`，status `extracted`（review §2.4 明知故记）；`sn74lvc2t45_vssop8` nom 0.13，p.31，
    quote `(0.13) TYP`，`extracted`；`pca9306_vssop8` nom 0.13，p.31，quote `(0.13) TYP`，
    `inferred`（review §2、round-4 adjudication 判 GOLD 保留）。
  - 另两个 gold 按散文把它整个省略：`tca9548a_tssop24`、`uln2003a_tssop16` 均无
    `lead_thickness`（round-4 adjudication 明确裁决 "no `lead_thickness` entry should remain" /
    "parenthesised, so reference-only per Note 1 and not usable for a package dimension"）。
  - 分歧不是遗漏而是同一规则被两个方向执行：round 4 在 pca9306 判 GOLD（"value is still a stated
    one, marked inferred"），在 tca9548a/uln2003a 判必须省略。reference.md 的示例值 `(0.15) TYP`
    就是被记录的 txs0108e 那个标注。
- 两种读法：
  - A（散文立场）：括号 = 该 drawing 自己的 NOTE 1 声明的参考值，参考值不是零件尺寸；若全表只剩
    这一个厚度标注，就整体不记 `lead_thickness`。三个 gold 错，两个省略的 gold 对。
  - B（gold 实际立场）：括号值仍是被印出来的量，含义可由渲染图判定（箭头骑在引脚侧视轮廓上），
    因此可记，用 `status: inferred` 标注判断风险；`land_*` 之外并非禁区。三个 gold 对，
    tca9548a/uln2003a 是否要补字段另说。
- 各自的证据（页码 + 引文）：
  - A：reference.md 括号值段；rules.json DIM-004；round-4 adjudication 的 tca9548a gold
    correction 4 与 uln2003a `lead_thickness` 行。
  - B：txs0108e review §2.4（p.28 `(0.15) TYP`）；pca9306 review §2 与 round-4 pca9306
    `lead_thickness` 行（p.31 `(0.13) TYP`）；sn74lvc2t45 review §2.4（p.31）。
- 建议：
  - 若选 A：删三个 gold 的 `lead_thickness`（走 `[GOLD]` 协议，各 review.md 补证据），DIM-004
    测试写成"括号值只能来自 `land_*`"。
  - 若选 B：改写 reference.md 的示例句（放开含义明确的尺寸标注、维持 `land_*` 一律可用），并一并
    裁定 tca9548a/uln2003a 是否补记；DIM-004 测试改成"非 `land_*` 的括号值必须 `inferred`"。
  - 未裁定前 DIM-004 刻意没有规则测试：写任何断言都等于替本议题拍板，故 audit 板面持续显示
    `未覆盖: DIM-004`。
- 状态：open

## MPN-001 六个 gold 记的不是印刷 orderable，MUST 无执行者
- 现象：reference.md:19-21 要求 mpn 是 addendum 列的 orderable，"不是任何页面上都不出现的 package-only 形式"，
  并拿 `ADS1015IDGS` 作反例。实际 gold：`ads1115_vssop10` = `ADS1115IDGS`（正是该反例句的同形状字符串，
  review.md:38 唯一理由是"与 KiCad 符号 Value 同串"）；同族同封装的兄弟 case `ads1015_vssop10` =
  `ADS1015IDGSR`，其 review.md:7-17 恰恰以"该串印在本数据表任何一页上都不存在"为由否掉 `ADS1015IDGS`
  ——两个 gold 不可能同时满足 MPN-001。同类：`ina219_soic8`=`INA219AxD`（review.md:101-106 自述"SOIC 没有裸
  INA219"）、`tlc555_soic8`=`TLC555xD`、`tps54202_sot23`=`TPS54202`（orderable 是 DDCR/DDCT）、
  `txs0108e_tssop20`=`TXS0108EPW`（orderable 是 TXS0108EPWR）。
  执行侧：tests/test_rules.py:191-197 是三 case 硬编码表，通则只断言单 token 无空白（186-188）；
  `scoring.py`/`evals/score.py` 完全不比 mpn。把 ads1115 的 mpn 改成 ADS1115IDGSR，板面仍全绿。
- 两种读法：A 按 MUST 字面（MUST 就是字面）改这 6 个 gold 的 mpn；B 认为"若无 addendum orderable，用印出的
  编号并 say so in the hand-over"的逃生条款覆盖这些 case，则需逐案确认数据表确实没印该 orderable 并补 review 证据。
- 证据：spec/rules.json:4-8（MPN-001）、reference.md:19-21、上列 gold 与 review.md 行号。
- 建议：逐案核对 6 份数据表的 orderable addendum（需要 PDF；本机没有），按 A 或按 B 定；A 走 [GOLD] 协议。
- 状态：open（来源：round 1 独立审计，本条已由主会话复核证据行号）

## PIN-001 散热垫命名 EP 与 gold 的 PAD/DAP 冲突，登记表只写了半条
- 现象：reference.md:37 写"an exposed pad is named `EP` and gets no `alt_names`"；rules.json 的 PIN-001
  声明（:10-16）只保留"描述不是 alt_names"半句。四个带 pad 的 gold 里三个不是 EP：drv8871 是 `PAD`
  （spec.gold.json:222）、tps5430 是 `DAP`（:219）、rp2040 把 pad 折进 `GND` 行；只有 cp2102n:261 与
  tps62130_vqfn16:283 用 EP。tests/test_rules.py:212-217 接受三种写法，靠 EXPOSED_PAD_GOLDS（:36）排除 rp2040
  ——分歧被写进测试而不是被裁决。pin 名参与 names_ok，照正文写 EP 的抽取在 drv8871/tps5430 上会丢 names_ok。
- 两种读法：A 一律 EP（正文当前写法）；B 按印出的主功能命名（reference.md:35），pad 随数据表用词。
- 证据：reference.md:35-37、rules.json PIN-001 声明、上列 gold 行号、tests/test_rules.py:36 与 212-217。
- 建议：人类裁定后，正文/登记表/测试三处同步；gold 是否改动取决于裁定。
- 状态：open（来源：round 1 独立审计，证据行号已复核）

## PIN-004 孤立电源"可选"被语料测试与 evals/README 当成强制
- 现象：reference.md:55-56 明确"grouping it `\"power\"` is optional and leaving `group` off it is equally
  correct"，措辞守卫 tests/test_skill_rules.py:60-67 也钉住这句。但 tests/test_rules.py:281-286
  `test_PIN_004_lone_supplies_may_stay_ungrouped` 断言 NE555 的 VCC/GND 必须没有 group，
  evals/README.md:323-325 写"which `reference.md` says to omit"——把"可选"陈述成"要求省略"。
  后果：任何给孤立电源（NE555 VCC、24LC256 VCC、INA226 VS）分组 power 的 gold/抽取被判错并扣 groups_ok；
  若按 [GOLD] 协议把某 gold 改成 group=\"power\"，该语料测试会失败——测试比规则强。
  另 tests/test_rules.py:289-292 只单向检查 group==\"power\" ⇒ 电源类型，印有 PWR 电源块却把电源留空组的 case 无覆盖。
- 两种读法：A 规则保留"可选"，测试改成两种读法都通过（如断言孤立电源的 group 只能是 absent 或 \"power\"）；
  B 规则改为必须省略，同步 README。
- 证据：reference.md:55-56、tests/test_skill_rules.py:60-67、tests/test_rules.py:281-292、evals/README.md:323-325。
- 建议：改测试需人类确认（涉及既有断言）；注意 round 1/2 的评分历史上按 B 罚过 run（evals/README.md:323-325）。
- 状态：open（来源：round 1 独立审计，证据行号与正文均已复核）

## SCH-007 整数引脚号被 load 层强制转字符串，MUST 无检查器
- 现象：reference.md:31 与 SCH-007（MUST）要求 pin number 是字符串，但 src/kicad_partspec/spec/load.py:86-91
  对 JSON 整数 `str()` 转换，错误文案也写"non-empty string or integer"。实测（.venv/bin/python -B，取自
  tests/test_spec_checks.BASE 的合法文档，pins[0].number 改为整数 77）：`verify_spec` 零失败，
  模型随后以 "77" 生成符号。SCH-007 的测试（tests/test_rules.py:139-143）只遍历 gold 文件，不探检查器。
- 两种读法：A 严守 MUST：loader 对整数报 schema 失败；B 允许整数（宽容加载），则 reference.md/rules.json
  改口径，文案保持现状。
- 证据：reference.md:31、spec/rules.json:88-92、src/kicad_partspec/spec/load.py:86-91、上述实测输出。
- 建议：A 会改变 loader 行为（原先通过的 JSON 输入开始失败），需人类拍板；无论哪种都要给检查器补测试。
- 状态：open（来源：round 1 独立审计，已由主会话实测复现）

## DIM-003 "labelled GAGE PLANE" 两种读法，两个 gold 各占一边
- 现象：reference.md:122-123："A boxed basic dimension, or one labelled `GAGE PLANE`, is a reference plane
  or a datum, not a size: never record it as `standoff`, `lead_length`, `lead_thickness` or anything else"；
  同文 spans 表（:140-142）却把 standoff 定义为"body underside and the seating (gage) plane"。语料侧：
  txs0108e_tssop20/spec.gold.json:60 的 standoff 引文含 "GAGE PLANE 0.15 0.05"，tps54202_sot23/spec.gold.json:114
  的 lead_thickness 引文含 "0.20 TYP GAGE PLANE 0.12"——按读法(b)（带该字样即不得记）两条 gold 违反 DIM-003。
  evals/README.md:460 显示正文想禁的是把框住的 `0.25 GAGE PLANE` 当尺寸。
- 两种读法：(a) 只有"框住的 GAGE PLANE 数值本身"不得当尺寸，引文顺带出现该字样无妨；(b) 任何位于 datum/GD&T
  语境、带该标注的数值都不得当尺寸。
- 证据：reference.md:122-123 与 140-142、两条 gold 的 source.quote、evals/README.md:460。
- 建议：正文改写为读法(a)（并把 `0.25 GAGE PLANE` 写成正例）或 (b)；DIM-003 的测试目前只断言 ne555/drv8871，
  无 quote 级检查，两种读法都能一路绿。
- 状态：open（来源：round 1 独立审计，证据行号已复核）

## LAND-001 "三者同时记或全不记"只存在于登记表，正文与 src 都没有
- 现象：spec/rules.json:157-159 的 LAND-001 声明尾句"land_pad_length, land_pad_width and land_span are
  recorded together or not at all"，但声明指向的 reference.md:127-130 只讲 metal vs SOLDER MASK OPENING，
  从无该要求。src 里这三个名字只出现在 gen/footprint.py:46 的 REQUIRED 与 87-92 的 skip_reason，
  即只在生成封装时以"跳过"体现。输入：任取不受支持家族（如 SOT-223）只记 land_pad_length——
  verify_spec 全绿、封装 skip，LAND-001 从未触发；唯一执行者是 tests/test_rules.py:411-417。
- 两种读法：A 这是真 MUST，正文补写并在 verify 层加检查；B 登记表删掉尾句，只保留语料测试这一层执行。
- 证据：spec/rules.json:157-159、reference.md:127-130、src/kicad_partspec/gen/footprint.py:46/87-92。
- 建议：人类裁定登记表与正文的对齐方向。
- 状态：open（来源：round 1 独立审计，证据行号已复核）

## DIM-001 登记表声明漏掉"两个叠印数字"形态
- 现象：reference.md:25 的 bullet 列了五种形态，其中"或两个叠印在图上（1.0 压 0.8）→ min 与 max"；
  spec/rules.json 的 DIM-001 声明只写 printed range / TYP、BSC / MAX / X±t 四种，丢掉叠印形态。
  另外新增的 DIM-001 测试用 RANGE_QUOTE（tests/test_rules.py:57）只认小数端点区间，`0.9 - 1`、`2-3`、
  `1.0 0.8` 都不匹配（主会话实测）；输入：quote 写 "0.9 - 1" 只记 {max: 1.0}，板面全绿而规则要求 min/max。
- 两种读法：A 声明补上叠印形态（与正文对齐）；B 认为叠印属于"range"的一种表现，声明措辞合并。
- 证据：reference.md:25、spec/rules.json DIM-001 声明、tests/test_rules.py:57 与 372-375（及其实测）。
- 建议：与 DIM-004 同属 DIM 模块的措辞对齐，人类确认后同步措辞守卫 tests/test_skill_dimension_rules.py。
- 状态：open（来源：round 1 独立审计，RANGE_QUOTE 边界由主会话实测确认）

## 候选新规则：没有任何一层校验"引文支撑所记数值"（SRC-001/SCH-001 的边界）
- 现象：check_provenance（src/kicad_partspec/verify/spec_checks.py:26-41）只查 source 存在、page>=1、quote 非空；
  check_quotes（src/kicad_partspec/verify/quotes.py:103-141）只做归一化子串匹配；全仓没有代码把 min/nom/max
  与 quote 内数字对照。审计员实测输入：dimensions 写 land_pad_length={nom:1.55, source:{page:1,
  quote:"SEATING PLANE"}}，只要该串在页面上存在，verify_spec 零失败、check_quotes 零 finding，
  DIM-001 语料测试因 quote 无区间而 continue——一个与引文无关的数值会一路绿到生成焊盘几何。
- 两种读法：A 新规则"记录的数值必须以同单位出现在引文中"（强，但会误杀双单位引文：如 ina219/lm358/ne555/tlc555
  的 lead_width 引文 `8X .012-.020` 只有英寸，gold 记公制 0.31/0.51——新测试必须先处理该例外）；
  B 只要求"引文中至少出现一个与记录值同单位的数字"或仅对单 token 引文（如 `TYP`）加约束。
- 证据：src/kicad_partspec/verify/{spec_checks,quotes}.py 上列行号；tests/test_rules.py:164-166（SRC-003 只覆盖
  "改写后子串消失"一种篡改）；DIM-001 测试 374-375 的 continue。
- 建议：作为候选新规则待人类评估；若立规则，必须先立"双单位引文"的例外口径再写测试。
- 状态：open（来源：round 1 独立审计，边界由主会话在 DIM-001 测试工作中独立发现并确认）

## PIN-005 语料测试的电源名白名单漏掉 AVDD/VBUS/VDDIO 一类
- 现象：tests/test_rules.py:301-305 只认 11 个硬写名（VCC VDD VSS GND V+ V- VM PGND VIO VBAT USB）。
  输入（审计员实测 verify_spec 零失败）：{"number": 3, "name": "AVDD", "electrical_type": "output"}（未分组）
  全板面绿；VDDIO/VDDA/VBUS/VREF+/VCCIO 同理。reference.md:70 的规则是语义的"a supply pin or a ground pin,
  even when the I/O column says I → power_in"，没有名单，白名单只是测试的代理。
- 两种读法：A 扩充白名单（把常见电源名补齐）；B 承认名单不可能穷尽，转而按 electrical_type × 命名启发式断言，
  或明确该测试只覆盖所见语料。
- 证据：tests/test_rules.py:301-305、reference.md:70、spec/rules.json:56-61。
- 建议：属"测试覆盖边界"而非规则矛盾，可与下轮工作循环一并处理；若选 B 涉及改既有断言，需人类确认。
- 状态：open（来源：round 1 独立审计，证据行号已复核）
