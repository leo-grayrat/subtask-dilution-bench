# 上下文不参与决策：第二轮候选质量审计

这份文档记录第一轮 25 个候选进入正式样本制作前的质量审计，并随着实际制作继续修正。`candidate-screening.md` 保留“为什么当时选中”，这里记录“现在是否适合进入 v0”。

一个候选要进入 v0，至少要满足：原任务能客观评分；正反版本尽量只改一个自然业务事实；改动后正确动作真的翻转；没有第二个独立条件同时决定同一动作；局部执行也能客观评分。

状态分为：**可直接制作 / 需补核 / 应降级**。

## 当前结果

制作第一批样本后，25 个候选更新为：

- **可直接制作：14 个**
- **需补核：7 个**
- **应降级：4 个**

| # | 来源 | 状态 | 结论 |
| --- | --- | --- | --- |
| 1 | Meridian / `158b9045` 信用单金额 | 可直接制作 | `$2,000 > $1,950` 直接触发信用单争议；金额关系可单独翻转 |
| 2 | Meridian / `158b9045` 部分发票 | 可直接制作 | partial invoice 与 over-invoice 可由数量关系翻转 |
| 3 | Crestwood / `1b602061` Facilities 灯泡邮件 | 需补核 | evaluator 只直接证明“不要回复 Facilities、邮件留在 General”；需核 SOP scope 后再做 in-scope 对照 |
| 4 | Prairie Star / `861b2650` 鼠类污染 | 可直接制作 | Class 4、拒收和紧急通知均可客观检查 |
| 5 | Vanguard / `9b2f7a29` manager approval | 可直接制作 | `$7,500` 项目的批准人角色是自然触发事实；junior 与 Finance Manager 可干净对照 |
| 6 | Ridgeline / `44e4c745` FMLA 1,250 小时 | 可直接制作 | SOP 与 evaluator 都明确使用 1,250 小时门槛 |
| 7 | CareIG / `f5947c33` 3 次未联系成功 | 可直接制作 | “三次且 none reached”与“其中一次 reached”直接翻转 unreachable / continue 路径 |
| 8 | Gear Systems / `0807b5a6` quarantine release | **应降级** | 授权人身份与货物质量状态纠缠，无法做纯单事实权限题 |
| 9 | Mojave Crest / `187e3a8c` coverage termination vs 72h | 可直接制作 | 更早日期决定 deadline，反事实非常干净 |
| 10 | Vanguard / `82da8d17` beneficiary 生存状态 | 可直接制作 | SOP 和 evaluator 支持“死亡 primary 排除、surviving primaries 重分配”；但首批 fixture 暂缓，先读清决定 Linda 已故的具体二进制附件 |
| 11 | Meridian / `331accf1` $99 / $100 discount | 可直接制作 | SOP 明确 `$100` 为边界，原任务本身已有边界两侧评分逻辑 |
| 12 | Ridgeline / `6e501f78` bereavement 天数 | 可直接制作 | 请求时长跨政策范围后动作翻转 |
| 13 | Mojave Crest / `ab59bcf7` $25k authority | 可直接制作 | 金额跨授权额度后需要 co-sign / escalation |
| 14 | CareIG / `08ae3378` administered dose | **应降级** | 只是数值来源选择，规则始终生效，不是当前要测的条件性动作翻转 |
| 15 | Prairie Star / `27470081` short-dated 15 天边界 | **应降级** | 制作时发现上游 SOP 与 evaluator 冲突：SOP 写 `<15 days` 才额外通知 Director，而目标 evaluator 对 15/16 天也要求该动作 |
| 16 | Vanguard / `90ff0751` T&E calendar context | 需补核 | 需证明 Calendar event 本身足以决定是否 flag，排除 employee notes 等第二条件 |
| 17 | Sunshine Set / `7c041148` prior/current quarter | 可直接制作 | delivery date 的季度归属决定例外规则 |
| 18 | Sunshine Set / `ebac9768` $50/$51 tier | 可直接制作 | 跨层级后通知对象和时序改变 |
| 19 | Sunshine Set / `b581c493` $249/$250 offset | 可直接制作 | 授权带边界清晰 |
| 20 | CareIG / `ea622238` Physician_NPI | **需补核** | 制作时发现原始邮件写的是 `NPI: NPI` 占位值，而 SOP 明确条件是 Physician_NPI blank；不能自行把二者当成同一状态 |
| 21 | Meridian / `a0895480` expired agreement | 需补核 | 当前侧评分很强，但还需证明协议有效时没有另一独立 hold |
| 22 | Meridian / `4dace65e` 缺 City/State/Zip | 需补核 | 需证明补齐地址后三字段之外没有第二 blocker |
| 23 | Sunshine Set / `d9d532c1` Deal 4505 reversed | 需补核 | 原 evaluator 把 4505 与 4507 合并检查，需单独抽 scorer |
| 24 | Vanguard / `89007056` unauthorized vendor | 需补核 | 需证明换成 authorized vendor 后不会仍被 business justification 等规则挡住 |
| 25 | Meridian / `19d57538` aggregate total mismatch | **应降级** | 总额、单价、数量数学耦合，难以只改一个自然事实同时维持数据一致 |

## 制作阶段发现的四个关键问题

### 1. evaluator 清楚不代表反事实干净

#8 和 #25 都有明确答案，但一个有多个同时生效的条件，另一个的数据字段互相数学约束。两者都不适合作为 v0 的单事实 paired case。

### 2. 不能从 evaluator 倒推不存在的流程

#3 的 evaluator 能证明“不回复 Facilities”，但不能因此自行补出某种 out-of-scope escalation。样本只能写到原规则和评分器真实支持的程度。

### 3. 数值变化不等于规则是否参与决策

#14 很适合研究“模型选对哪个事实源了吗”，但它没有规则 active/inactive 或动作路径翻转，因此不放进当前方向。

### 4. 上游 benchmark 自己矛盾时必须停

#15 在候选阶段看起来很干净，真正摘 SOP 时却发现 `<15` 与目标 evaluator 对 15/16 天的要求冲突。这种题不能靠我们改提示词或选一个“更顺眼的答案”修补，直接降级。

#20 则是另一类问题：SOP 要求字段 blank，而原始资料是 `NPI: NPI`。除非后续找到上游对 placeholder 的明确解释，否则不能把它当成严格的 blank case。

## 第一批实际制作样本

第一批 runnable 规格改为：

1. **#1** 信用单金额是否超过原发票；
2. **#5** 大额项目的批准人是否为 manager；
3. **#6** FMLA 是否达到 1,250 小时；
4. **#7** 三次联系中是否存在一次 `Reached`；
5. **#9** coverage termination 与 72 小时期限谁更早；
6. **#11** early-payment discount 是 `$99` 还是 `$100`。

这 6 个的具体正反状态、局部任务和评分依据写在 `pilot-samples-v0.md`。

#10 仍保留为可直接制作候选，只是没有塞进第一批：其规则和目标输出已经明确，但正式修改 fixture 前还需要把决定 Linda 已故的具体附件读清楚，避免猜测二进制材料内容。

## 当前停止点

现在不再继续扩题，也不再继续写方法说明。下一步是把这 6 个规格真正变成可运行 fixture / scorer，并先跑一个很小的四层测试，检查整个实验链路是否工作。