# 上下文不参与决策：第二轮候选质量审计

这份文档记录第一轮 25 个强候选进入正式样本制作前的第二轮审计。它不覆盖 `candidate-screening.md`：前者保留“为什么当时把它选进候选池”，这里记录“现在是否适合进入第一版 pilot”。

本轮仍不运行被测模型。审计依据是第一轮已经检查过的原始任务、规则和 evaluator，并对容易存在隐藏条件的案例重新核对任务状态和 rubric。**这里的“可直接制作”也不等于样本已经冻结；正式制作时仍要逐题摘出目标 SOP 的确切规则，并验证正反两个版本都能独立评分。**

## 审计标准

一个候选要进入第一版样本制作，至少应满足：

1. 原任务 evaluator 能直接或经过很小改造判断目标动作 / 最终状态；
2. 反事实最好只改一个自然存在的业务事实，而不是为了翻答案硬改多个互相依赖的字段；
3. 改完这个事实后，正确动作或正确结果确实翻转；
4. 没有已知的第二个条件也足以独立决定同一动作；
5. 能搭出一个局部执行版本，并且局部执行也能客观评分。

状态分三类：

- **可直接制作**：没有发现明显结构性阻碍，可以进入样本制作；
- **需补核**：候选仍有价值，但必须先解决一个明确的问题，不能直接开跑；
- **应降级**：不适合第一版单事实 pilot，保留作以后更复杂或相邻问题的材料。

## 审计结果

目前 25 个候选分为：

- **可直接制作：16 个**
- **需补核：6 个**
- **应降级：3 个**

| # | 来源 | 状态 | 第二轮结论 | 下一步 |
| --- | --- | --- | --- | --- |
| 1 | Meridian / `158b9045` 信用单金额 | 可直接制作 | 金额关系直接决定 dispute hold；反向版本自然 | 摘出规则，制作 `>$invoice` / `≤$invoice` pair |
| 2 | Meridian / `158b9045` 部分发票 | 可直接制作 | `invoice qty < received qty` 与 over-invoice 可做清楚翻转 | 制作 partial / over-invoice pair |
| 3 | Crestwood / `1b602061` Facilities 灯泡邮件 | **需补核** | 第一轮把它概括成“out-of-scope 升级”过强。原 evaluator 直接要求的是**不要回复 Facilities**，并把邮件保留在 `General` | 核对 SOP 的 scope 规则，并找一个只改请求类别就变成应处理的 in-scope 对照 |
| 4 | Prairie Star / `861b2650` 鼠类污染 | 可直接制作 | 原 evaluator 直接检查 Class 4、拒收和紧急通知；动作结果很明确 | 用污染观察事实构造低等级损伤对照，避免同时改变其他安全信号 |
| 5 | Vanguard / `9b2f7a29` manager approval | 可直接制作 | 审批角色是自然、可程序化的触发事实 | 制作 junior / manager approval pair |
| 6 | Ridgeline / `44e4c745` FMLA 1,250 小时 | 可直接制作 | 资格阈值清晰 | 制作 1,100 / ≥1,250 pair |
| 7 | CareIG / `f5947c33` 3 次未联系成功 | 可直接制作 | 历史状态是否出现 `Reached` 可直接翻转 unreachable 流程 | 制作 none reached / one reached pair |
| 8 | Gear Systems / `0807b5a6` quarantine release | **应降级** | `REC-002` 不可执行不只是授权人角色不同：此前质量检查还记录 3 件功能完整性受损，而后续 Receiving/Warehouse Supervisor 又把它们说成纯 cosmetic。角色和实体状态两个条件纠缠 | 移出 v0；可留作以后“冲突证据 + 权限”复合约束题 |
| 9 | Mojave Crest / `187e3a8c` coverage termination vs 72h | 可直接制作 | 两个时间点取更早者，反事实自然 | 制作 termination before / after 72h pair |
| 10 | Vanguard / `82da8d17` primary beneficiary 生存状态 | 可直接制作 | 单一生存状态改变分配路径 | 制作 deceased / alive pair，并保持其他 beneficiary 不变 |
| 11 | Meridian / `331accf1` $99 / $100 discount | 可直接制作 | 原任务本身已有边界两侧实例 | 直接利用边界 pair |
| 12 | Ridgeline / `6e501f78` bereavement 天数 | 可直接制作 | 超政策范围与范围内动作不同 | 制作 within / exceed pair |
| 13 | Mojave Crest / `ab59bcf7` $25k authority | 可直接制作 | 金额跨授权额度后需要 co-sign / escalation | 制作 ≤25k / >25k pair |
| 14 | CareIG / `08ae3378` administered dose | **应降级** | evaluator 很客观，但“改 administered dose”只改变数值输出，`必须按 administered dose 计费`这条规则始终生效；不是我们当前要的规则 active/inactive 或动作翻转 | 留作以后“事实源选择 / 数据来源优先级”扩展，不放 v0 |
| 15 | Prairie Star / `27470081` short-dated 15 天边界 | 可直接制作 | 14 天与 15/16 天对应不同 escalation 层级 | 制作 14 / 15–16 day pair |
| 16 | Vanguard / `90ff0751` T&E calendar context | **需补核** | 原 evaluator 明确区分应 flag 的 water bottle 与不应 flag 的 Capital Grille / Marriott / Hartwell；Calendar 也确有对应会议。但还需确认 SOP 是否把 calendar context 本身作为决定条件，避免 employee notes 等第二条件混入 | 摘出目标 SOP，证明只增删匹配 Calendar event 就足以翻转 |
| 17 | Sunshine Set / `7c041148` prior/current quarter | 可直接制作 | delivery date 的季度归属决定例外规则 | 制作 current / prior-quarter pair |
| 18 | Sunshine Set / `ebac9768` $50/$51 tier | 可直接制作 | 跨层级后通知对象 / 时序改变 | 制作 $50 / $51 pair |
| 19 | Sunshine Set / `b581c493` $249/$250 offset | 可直接制作 | 授权带边界清晰 | 制作 $249 / $250 pair |
| 20 | CareIG / `ea622238` Physician_NPI 缺失 | 可直接制作 | 原规则明确 blank → hold / do not proceed | 制作 blank / valid NPI pair |
| 21 | Meridian / `a0895480` expired agreement | **需补核** | 当前侧证据很强：原 evaluator 同时检查 `APPR` hold、Payment Queue 缺席和协议过期通知。但尚未证明把 agreement date 改到有效期内后不存在其他独立 hold | 验证“协议有效”的正常路径和评分器，再冻结 pair |
| 22 | Meridian / `4dace65e` 缺 City/State/Zip | **需补核** | 当前侧因果链很短：缺字段 → 不录 Invoice Register + 要求补齐重交。仍需确认这三个字段是该发票的唯一 blocker | 补齐三字段后走一次正常路径检查；若无第二 blocker 即升级为可制作 |
| 23 | Sunshine Set / `d9d532c1` Deal 4505 reversed | **需补核** | 原 evaluator 把 4505 reversed 与 4507 not-posted 一起检查，不能直接把现有 full-task rubric 当成 4505 单独评分器 | 单独抽 4505 scorer，并证明 valid + posted 时应正常纳入 commission |
| 24 | Vanguard / `89007056` unauthorized vendor | **需补核** | 原 rubric 对 `OPS_HR_TE-4` 直接要求 `Unauthorized vendor... personal reimbursement`，但授权 vendor 后是否仍被 business-justification 等规则拦住尚未验证 | 固定其他上下文，仅替换 vendor membership，确认正向路径 |
| 25 | Meridian / `19d57538` aggregate total mismatch | **应降级** | 当前 evaluator 很强，但 97.50×20=1950、101.50×20=2030；总额 mismatch 与 unit price / quantity / invoice amount 数学耦合。很难只改一个自然事实又保持记录内部一致 | 移出 v0；留作以后“多个局部检查如何汇总到最终动作”题 |

## 本轮发现的三个重要修正

### 1. “原 evaluator 有明确答案”还不够

#8 和 #25 都有非常明确的原始 evaluator，但仍不适合 v0。

- #8 的问题是**多个事实同时支持不执行**，所以改一个角色并不能证明正确动作应该翻转；
- #25 的问题是**反事实在数据结构里并不独立**，改一个总额会破坏单价、数量和金额之间的一致性。

因此第一版不能只筛“评分器清楚”的题，还必须筛“反事实干净”的题。

### 2. 不能把 evaluator 的结果倒推成我们想要的规则

#3 是一次实际纠正。原任务能直接证明的是：不应向 Facilities 发送回复，并把该邮件保留在 `General`。它并不能单凭 evaluator 证明“应该执行某种 out-of-scope escalation”。

后续制作样本时，`target action` 必须按原规则和原 evaluator 能支持到的程度写，不能为了让故事更完整自行补一段流程。

### 3. 数值会变化不等于“上下文有没有进入决策”

#14 的 administered dose 很适合测试模型是否选对事实源，但它不是当前设计最关心的 `Recall / Applicability / Local Execution / Full Execution` 中的条件性动作翻转。把它硬塞进来会让这个方向慢慢变成泛化的“复杂任务里会不会犯错”。

所以它应当保留，但从第一版移出。

## 第一批正式制作建议

先不要一次把 16 个全部做完。第一批取 6 个结构差异最大的：

1. **#1 金额关系**：信用单金额是否超过原发票；
2. **#5 权限身份**：junior approval vs manager approval；
3. **#9 时间比较**：coverage termination 与 72 小时期限谁更早；
4. **#10 状态 → 分配路径**：primary beneficiary 生存状态；
5. **#15 时间阈值**：14 天 vs 15/16 天的 escalation；
6. **#20 必要字段 gate**：Physician_NPI blank vs present。

这 6 个先分别制作：规则摘录、关键事实、正反状态、局部任务、局部 scorer、完整任务 scorer。制作过程中如果发现任何一个必须再增加第二个修改才能让答案翻转，立即降级，不靠补充提示词把它“修成”一道题。

## 当前停止点

第二轮之后，第一版可制作池从名义上的 25 个收缩为 16 个；另外 6 个待补核，3 个明确降级。

下一步不再继续筛题，而是从上面 6 个开始真正制作样本。完成第一小批后先试跑四层测试，确认整个实验结构能工作，再决定是否继续制作剩余候选。