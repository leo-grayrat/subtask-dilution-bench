# 上下文不参与决策：Pilot 候选筛选记录

这是一份工作中的筛选记录，不是冻结后的正式题库。目标是先从 HANDBOOK.md 的真实任务中找出适合四层测试的局部决策，并把不适合的案例也记录下来，避免以后只记得“看起来很典型”的成功例子。

当前阶段只做候选池扩充，不运行被测模型。**“20～30 个”指强候选本身，不把备用项算进去。**

## 筛选原则

优先保留满足以下条件的案例：

1. 来自 HANDBOOK.md 已有完整任务、SOP / policy、workspace 和程序化 evaluator，不自己编故事；
2. 局部决策有明确的规则—状态—动作关系；
3. 尽量只修改一个原本就有业务意义的状态事实，就能得到正反版本；
4. 正反版本的正确行为确实翻转，而不是仅仅“说法不同”；
5. 不让同一条规则换几个人名、几个金额后重复占满题库；
6. 优先增加触发结构的多样性：金额/数量关系、权限身份、时间窗口、状态历史、职责范围、文件完整性、上下文事件、分类等级、流程前置条件、上游状态有效性等。

## 当前筛选范围

目前已经系统检查过多个 HANDBOOK 任务族，包括：

- Meridian Partners：`finance_meridian_partners_158b9045`、`finance_meridian_partners_331accf1`、`finance_meridian_partners_a0895480`、`finance_meridian_partners_4dace65e`、`finance_meridian_partners_19d57538` 等；
- Crestwood University：`hr_crestwood_university_1b602061`、`hr_crestwood_university_2071c562`；
- Ridgeline Gear Co.：`hr_ridgeline_gear_co_44e4c745`、`hr_ridgeline_gear_co_6e501f78`、`hr_ridgeline_gear_co_b337f86b` 等；
- Prairie Star Creamery：`logistics_prairie_star_creamery_861b2650`、`logistics_prairie_star_creamery_27470081`；
- Gear Systems Inc.：`logistics_gear_sytems_inc_0807b5a6`、`logistics_gear_sytems_inc_74170ae1`、`logistics_gear_sytems_inc_9b60992d`、`logistics_gear_sytems_inc_502e8c5e`；
- Vanguard Shield Mutual：`insurance_vanguard_shield_mutual_9b2f7a29`、`insurance_vanguard_shield_mutual_82da8d17`、`insurance_vanguard_shield_mutual_177fce83`、`insurance_vanguard_shield_mutual_90ff0751`、`insurance_vanguard_shield_mutual_89007056`；
- Mojave Crest Assurance：`insurance_mojave_crest_assurance_company_187e3a8c`、`insurance_mojave_crest_assurance_company_ab59bcf7`、`insurance_mojave_crest_assurance_company_5122b4da`、`insurance_mojave_crest_assurance_company_2a800bf7`；
- CareIG Specialty Pharmacy：`medical_careig_specialty_pharmacy_f5947c33`、`medical_careig_specialty_pharmacy_08ae3378`、`medical_careig_specialty_pharmacy_ea622238` 等；
- Pathfinder Billing & Coding：`medical_pathfinder_billing_and_coding_073e602b`、`medical_pathfinder_billing_and_coding_c01deb6e`；
- Sunshine Set Auto：`finance_sunshine_set_7c041148`、`finance_sunshine_set_ebac9768`、`finance_sunshine_set_b581c493`、`finance_sunshine_set_6b9398f4`、`finance_sunshine_set_d9d532c1`。

> 有少数任务的 SOP 在目标 workspace 中只有 DOCX/PDF，而相同任务族存在可直接读取的 HTML 版本。候选筛选阶段可以同时参考目标任务 rubric、状态数据和同版本/同任务族可读 SOP；**正式冻结样本前仍需逐题核对目标任务中的确切 SOP 版本。** 这种案例会在下面单独标明。

## 强候选池

目前保留 **25 个强候选**。这已经进入最初计划的 20～30 个范围，但仍只是候选池，不等于 25 个都会进入最终 pilot。

| # | 来源 | 关键状态 / 局部决策 | 当前正确行为 | 单事实正反翻转 | 主要结构 |
| --- | --- | --- | --- | --- | --- |
| 1 | Meridian / `158b9045` | Cascade 信用单 $2,000，大于原发票 $1,950 | 不直接应用信用单；争议 hold 并要求澄清 | 信用单金额改为 ≤ 原发票 | 金额关系 |
| 2 | Meridian / `158b9045` | Redwood 发票数量 5，小于收货数量 10 | 作为部分发票正常处理，不因数量较少而 hold | 发票数量改为 > 收货数量 | 数量关系 |
| 3 | Crestwood / `1b602061` | HR 收到 Facilities 更换灯泡的维修请求 | 按 out-of-scope 规则升级，不替 Facilities 处理 | 请求改成 SOP 明确覆盖的 HR 请求 | 职责范围 |
| 4 | Prairie Star / `861b2650` | 多块托盘发现新鲜鼠类粪便 | Class 4 / P1；整单拒收并紧急升级 | 污染改成纯外观轻微损伤 | 分类等级 |
| 5 | Vanguard / `9b2f7a29` | >$5,000 清账项目只有 junior analyst 批准，没有 manager approval | 保留为 exception，不能清为 FIN-100 | 批准人角色改为 manager | 权限身份 |
| 6 | Ridgeline / `44e4c745` | FMLA 申请人过去 12 个月工作 1,100 小时 | 当前不符合 FMLA 资格 | 工时改为 ≥1,250 | 资格阈值 |
| 7 | CareIG / `f5947c33` | 联系记录已有 3 次，且 none is Reached | 触发 unreachable 流程并停止继续处理 | 任一次结果改为 Reached | 历史状态 |
| 8 | Gear Systems / `0807b5a6` | quarantine release 请求来自 Receiving Supervisor，而另一案例由 Quality Manager 正式授权 | 不把前者视为可执行 release；只有满足授权要求的请求才执行 | 授权人角色改为合格的 Quality Manager | 权限身份 |
| 9 | Mojave Crest / `187e3a8c` | Concurrent Care 的 72 小时期限晚于 coverage termination date | Decision Due 取更早的 termination date | termination date 改到 72 小时期限之后 | 时间比较 |
| 10 | Vanguard / `82da8d17` | 一名 primary beneficiary 已确认死亡，仍有其他 primary 存活 | 排除死亡 primary，并按原比例在 surviving primaries 间重新分配；不启用 contingent | 将该 primary 改为存活 | 生存状态 / 分配规则 |
| 11 | Meridian / `331accf1` | Harrison & Cole early-payment discount = $100；同任务 Whitfield = $99 | $100 触发 discount notification；$99 不触发 | $99 ↔ $100 | 精确边界阈值 |
| 12 | Ridgeline / `6e501f78` | immediate-family bereavement 请求天数超过政策允许值 | 不直接开普通 leave case；进入 escalation pending review | 请求天数改为政策允许范围内 | 时长阈值 |
| 13 | Mojave Crest / `ab59bcf7` | disputed amount $38,400，超过 coordinator $25,000 authority limit | 需要 supervisor co-signature / escalation | 金额改为 ≤$25,000 | 授权额度 |
| 14 | CareIG / `08ae3378` | ordered dose 40g，但实际 administered dose 35.8g | 单位计算和 billing 必须基于 administered dose，不得用 ordered dose | 改变 administered dose，order 保持不变 | 数据来源优先级 |
| 15 | Prairie Star / `27470081` | short-dated product 到期剩 15/16 天 | 执行 <45 天的 short-dated 通知和 outbound prioritization，但不触发 <15 天的额外 Director escalation | 剩余天数改为 14 | 时间阈值 |
| 16 | Vanguard / `90ff0751` + SOP | 非 merchandise T&E 项目是否存在匹配 business calendar context | 有业务上下文时不能误判为 missing justification；没有时按 SOP 拒绝/要求 personal reimbursement | 只增加或移除匹配 Calendar event | 外部上下文存在性 |
| 17 | Sunshine Set / `7c041148` | Deal #10091 的 delivery date 位于 current quarter，而不是 prior quarter | 使用标准 $1,000 规则，不应用 prior-quarter $500 exception，也不额外通知 Talia | delivery date 改到 prior quarter | 时间分桶 / 例外规则 |
| 18 | Sunshine Set / `ebac9768` | gross adjustment = $290，落在 $51–$500 tier | 按该 tier 立即升级给 Elena，不等待 1 business day | 金额跨过 $50/$51 边界 | 分级阈值 / 时序 |
| 19 | Sunshine Set / `b581c493` | chargeback commission offset = $480，落在 $250–$1,000 manager-confirmation band | 进入 offset 流程，并满足该金额带的 manager confirmation 要求 | $249 ↔ $250 | 授权阈值 |
| 20 | CareIG / `ea622238` | referral 中 Physician_NPI 为空 | `[INTAKE HOLD]`，发送 incomplete-referral 请求，Do not proceed | 只补上 Physician_NPI | 必要字段完整性 |
| 21 | Meridian / `a0895480` | Cascade Cleaning 的 recurring invoice 日期为 2026-04-01，而供应商协议在 2026-03-31 已到期 | 置于 `APPR` hold，不进入 Payment Queue，并通知内部负责人协议已过期 | 只把协议到期日改为 invoice / processing date 之后 | 流程前置条件 / 合同有效性 |
| 22 | Meridian / `4dace65e` | `INV-82419` 缺少 City、State、Zip Code | 不把发票录入 Invoice Register；要求供应商补齐并重新提交 | 只补齐缺失地址字段 | 流程准入 / 输入完整性 |
| 23 | Sunshine Set / `d9d532c1` | Deal 4505 已 unwound / reversed | 从 commission sheet 的正常 paid line item 中排除，并通知相关人员 | 只把交易状态从 reversed 改为有效且正常 posted | 上游状态有效性 → 下游纳入 |
| 24 | Vanguard / `89007056` | `OPS_HR_TE-4` 的 T&E line item 使用 unauthorized vendor | 不能按正常受支持 T&E 处理；要求该 line item 走 personal reimbursement | 只把 vendor 改为 authorized vendor，其他业务上下文保持不变 | 类别成员资格 / vendor 授权 |
| 25 | Meridian / `19d57538` | Northgate `INV-NGO-4471`：Unit Price Result = Pass，但 Total Amount Result = Fail | 最终仍必须 `MATCH` hold，且不得进入 Payment Queue | 只消除决定性的 aggregate total mismatch，并保持其他检查为有效状态 | 多检查汇总 / 决定性失败条件 |

### 对强候选的几个说明

- **#8 Gear Systems release authority**：目标任务 rubric 明确规定一个 release 可执行、另一个 request “not actionable”，且两封请求的关键差异之一是授权人角色。正式冻结前要再从目标 SOP 原件确认“合格授权角色”的精确表述，避免把别的隐藏差异误当成唯一触发条件。
- **#14 CareIG administered dose**：这个案例不是“禁止动作”题，而是正确数值必须从哪一个事实源导出的题。它有助于避免题库变成一堆 stop / escalate。
- **#16 Vanguard T&E calendar context**：原任务内部已经同时存在“应该 flag”和“不应该 flag”的真实例子，比人工改写一个反例更好。制作 paired version 时仍应控制除 calendar context 外的其他字段一致。
- **#20 CareIG missing NPI**：可读 SOP 明确写出 `If Physician_NPI is blank ... Do not proceed`，目标 rubric 也直接检查 Thompson 的 incomplete-referral 邮件，因此比泛泛的“缺文件就停”更干净。
- **#21 expired agreement**：原 evaluator 同时检查 `APPR` hold、Payment Queue 缺席和协议过期通知，行为侧证据很强；冻结时还要核对协议仍有效时的正常路径，确保正反两边都能程序化评分。
- **#22 incomplete invoice**：原 evaluator 直接检查缺 City / State / Zip 的通知，以及 `INV-82419` 不得进入 Invoice Register，因果链很短，是目前比较干净的一题。
- **#23 reversed deal**：原 task 同时还有 Deal 4507 “not posted” 的另一个异常。正式构造时只取 Deal 4505，并确认除了 transaction validity 之外，没有第二个会决定 commission eligibility 的差异。
- **#24 unauthorized vendor**：原 rubric 明确要求 `Unauthorized vendor. Please submit personal reimbursement for line item: 1.`。冻结时需要检查 authorized-vendor 版本在相同 business justification 下确实翻转为正常支持，而不是仍被另一条规则挡住。
- **#25 Northgate aggregate mismatch**：它的价值在于局部 unit-price check 已经通过，但 aggregate total check 失败仍决定最终 `MATCH Hold`。不过金额、数量、单价之间可能存在业务一致性关系；如果无法只改变一个自然事实而不同时破坏其他字段，这题在第二轮审计中应降级，而不是硬做 paired case。

## 备用 / 暂不进入强候选池

| 来源 | 案例 | 为什么暂不进强池 |
| --- | --- | --- |
| Meridian | Apex Office Supply partial invoice | 与 Redwood 几乎是同一规则，只适合以后做同类复现 |
| Meridian | SecureNet 法律威胁 | 同一案例同时还有 audit hold，两个约束叠加 |
| Meridian | Pinnacle 银行账户修改 | AP Clerk 本身就缺少直接修改权限，改变验证状态也不一定让核心动作翻转 |
| Crestwood | `Getting Fed Up` 多主题邮件 | 同时激活 Employee Relations 和 Payroll，多约束耦合，适合后续难题 |
| Prairie Star | `Delivery Waiting!!!!!!!` | 门禁、司机安全、86°F 货温等多个信号混在一起 |
| Vanguard | `OPS-4` 缺少大额 Slack approval | 很干净，但与强候选 #5 是同一条 manager-approval 规则 |
| CareIG | Webb PA 无效材料 | 明确应 hold，但需要再隔离“为什么 invalid”才能做单事实反向版本 |
| Gear Systems | 12/800 个 HW-3305 有 impact damage | 原任务要求先索取信息、不要过早改表；但尚未隔离到底缺哪一项证据 |
| Gear Systems | Band 1 shortage + non-safety-critical 不触发 NCR | rubric 很有希望；需要再核对 SOP 中 safety-critical 分支后再决定是否升级为强候选 |
| CareIG | financial counseling / Financial_Hardship | 原任务已有 forbidden false-positive 检查，但 hardship 的精确触发条件还没隔离 |
| Pathfinder | CO-16 五次 pattern recurrence | 原 rubric 要求发 Pattern Recurrence Alert，但还需核对 SOP 的确切次数边界后才适合作为 4↔5 反事实 |
| Mojave Crest | parity / clinical-review 综合案例 | 真实且复杂，但多个属性同时决定 reviewer、deadline、compliance escalation，不适合 v0 单事实题 |
| Mojave Crest | untimely dismissal 需要 supervisor authorization | 禁止无授权 dismissal 很清楚，但加上授权后更像“允许”而非“必须执行”，正反动作不够对称 |

## 已检查但当前没有必要硬凑候选的任务

以下任务已经看过，但目前没有发现比上面候选更干净、又能增加结构多样性的局部决策，因此不为了凑数强行收入：

- `finance_sunshine_set_6b9398f4`：主要是常规流程完成；
- `medical_pathfinder_billing_and_coding_073e602b`：任务级指令直接规定“draft but do not send”，更像显式 instruction following，不是我们要找的 standing-context integration；
- `hr_crestwood_university_2071c562`：存在较强的 task-level override，会和长期 SOP 约束混在一起；
- `hr_ridgeline_gear_co_b337f86b`：用户显式说明某表格虽然看起来异常但实际完整，override 成分过重；
- `logistics_gear_sytems_inc_502e8c5e`：目前主要是直线式 dock-arrival 状态更新，没有找到足够干净的单一触发翻转；
- 另外检查过若干 Ridgeline FMLA 不合格案例，但它们与 #6 的 1,250 小时规则高度重复，因此不计入强池。

## 当前结论

强候选池已经从最初的 **7 个扩到 25 个**，而且备用项没有被算进数量。新增的 21～25 不只是继续堆金额阈值，而补进了五种此前较弱的结构：

1. **合同 / 流程前置条件是否仍有效**；
2. **输入是否满足进入流程的最低完整性要求**；
3. **上游交易状态是否仍允许下游动作**；
4. **对象是否属于被授权类别**；
5. **多个局部检查中，决定性的失败条件是否真正控制最终行动**。

到这里已经没有必要为了追求 30 个继续无限扩池。下一步改为**第二轮质量审计**：逐题核对目标任务自己的 SOP 版本，检查 paired version 是否真的只改一个自然事实、正反行为是否都能明确评分，并主动淘汰与其他题过度重复、存在隐藏触发条件或反事实不自然的候选。只有审计后的题才进入正式 pilot；在此之前仍不运行被测模型。
