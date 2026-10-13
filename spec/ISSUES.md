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
