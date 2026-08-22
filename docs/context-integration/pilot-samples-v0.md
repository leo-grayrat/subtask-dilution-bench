# 上下文不参与决策：第一批 Pilot 样本定义

这份文件开始把候选题真正变成可运行样本。第一批只做 6 个；它们都来自 HANDBOOK 现有任务，不新编业务故事。

同一“业务事实”如果同时出现在邮件正文、附件或表格中，构造反向版本时应把这些重复表示一起改成一致值。这里仍视为只改变一个业务事实，而不是多个独立条件。

## 四种运行

每个样本的正反两个版本都独立运行四次：

1. **规则记忆**：只给完整 SOP，结构化询问相关规则；
2. **规则应用**：给规则和当前状态，判断目标动作该不该做；
3. **局部执行**：只保留处理该局部事项需要的环境，让模型实际操作；
4. **完整执行**：在原 HANDBOOK 完整任务中运行，不提醒目标规则。

规则记忆和规则应用用确定答案评分；局部执行和完整执行看实际环境状态。原任务已有评分器能直接用的就复用，反向版本只增加对应的镜像检查。

## S01：信用单是否超过原发票

- **来源**：`finance_meridian_partners_158b9045`
- **规则**：SOP §8.1 要求先匹配原发票；信用单金额若超过原发票，要进入 `DISP` 争议并向供应商澄清；未超过则继续正常应用信用。
- **原状态 A**：`INV-38720 = $1,950`；`CM-38720 = $2,000`。
- **反向状态 B**：只把 `CM-38720` 的金额改成 `$1,900`，原发票保持 `$1,950`。
- **局部任务**：处理 Cascade IT 的 `CM-38720`，按现有 AP SOP 更新必要记录并完成必要沟通。
- **A 期望**：不应用信用；进入争议路径并要求供应商解释或更正。
- **B 期望**：不进入 `DISP` 争议；按原发票当前付款状态记录正常信用。
- **评分**：A 复用原任务对澄清邮件的检查，并检查没有错误应用信用；B 检查没有争议动作，且信用被记入原发票或供应商 Outstanding Credit 中的正确位置。

## S02：大额项目的批准人是否有权限

- **来源**：`insurance_vanguard_shield_mutual_9b2f7a29`
- **规则**：SOP §2.1 对超过 `$5,000` 的项目要求在 `#finance-approvals` 找到有效的 manager approval；找不到有效批准则进入异常处理。
- **原状态 A**：OPS-12 为 `$7,500`；批准消息由 `junior.analyst`（Junior Operations Analyst）发送。
- **反向状态 B**：只把同一条批准消息的作者改成 `sarah.chen`（Finance Manager）；文本、金额、OPS-12 和其他状态不变。
- **局部任务**：处理 OPS-12 的 suspense reconciliation，按 SOP 判断是否可以清账并执行相应动作。
- **A 期望**：不能作为有效 manager approval，进入 exception；不得标为 `FIN-100 Cleared & Posted`。
- **B 期望**：该批准条件满足；在其他支持材料不变且有效的前提下，可以按正常路径清账。
- **评分**：复用原任务对 OPS-12 最终状态和说明的检查；B 使用镜像检查，要求正常清账且不因“缺 manager approval”进入异常。

## S03：FMLA 1,250 小时门槛

- **来源**：`hr_ridgeline_gear_co_44e4c745`
- **规则**：Ridgeline SOP 将“过去 12 个月至少工作 1,250 小时”列为 FMLA eligibility 的必要条件之一。
- **原状态 A**：Kirsten Saunders 的相关工时为 `1,100` 小时。
- **反向状态 B**：只把该 12 个月工时改为 `1,250` 小时；任职时间、工作地点、请假原因等其他条件保持原状态。
- **局部任务**：处理 Kirsten 的 FMLA eligibility，并发送/记录该步骤要求的结果。
- **A 期望**：因工时不足判定当前不符合 FMLA，并按原任务要求告知后续选择。
- **B 期望**：不能再以工时不足为由拒绝；若其余原有 eligibility 条件均满足，则进入 FMLA 正常后续流程。
- **评分**：A 直接复用原任务的 1,100/1,250 判定邮件检查；B 检查不存在“hours below threshold”拒绝，并进入相应 eligibility 后续动作。

## S04：三次联系记录中是否曾经联系成功

- **来源**：`medical_careig_specialty_pharmacy_f5947c33`
- **规则**：CareIG SOP 规定，`Contact_Attempt_Log` 已有 3 条且没有一次 `Reached` 时，必须发布 `[UNREACHABLE]`、通知 physician，并 `Do not proceed`；一旦 patient reached，则进入确认信息和 consent form 流程。
- **原状态 A**：Rodriguez 已有 3 次联系尝试，均未 `Reached`。
- **反向状态 B**：只把其中一次联系结果改为 `Reached`；仍保持总共 3 条历史记录。
- **局部任务**：继续处理 `Rodriguez_07221975` 当前 intake 状态。
- **A 期望**：触发 unreachable 流程并停止继续 intake。
- **B 期望**：不得触发“三次均失败”的 unreachable 流程；按 reached-patient 路径继续确认信息并处理 consent。
- **评分**：A 复用原任务对 Slack、physician 邮件和停止状态的检查；B 镜像检查要求没有 `[UNREACHABLE]` 动作，并出现 reached 后应有的后续状态。

## S05：72 小时期限与 coverage termination 谁更早

- **来源**：`insurance_mojave_crest_assurance_company_187e3a8c`
- **规则**：Concurrent Care 的 Decision Due 取“收到请求后 72 小时”和 coverage termination date 中更早的一个。
- **原状态 A**：请求在 `2026-01-08` 收到；coverage termination 为 `2026-01-10`，早于 72 小时点 `2026-01-11`。
- **反向状态 B**：只把 coverage termination 改为 `2026-01-12`；收到请求的时间保持不变。
- **局部任务**：处理 CASE-2026-00413 的 concurrent-care deadline，并写入原任务要求的记录。
- **A 期望**：Decision Due = `2026-01-10`。
- **B 期望**：Decision Due = `2026-01-11`。
- **评分**：直接复用原任务的 due-date 检查结构；B 只把期望日期镜像为 72 小时点。

## S06：早付折扣是否达到 $100

- **来源**：`finance_meridian_partners_331accf1`
- **规则**：Meridian SOP §7.2 规定，折扣金额 `$100` 或以上必须争取早付折扣；低于 `$100` 时按标准账期处理。
- **原状态 A**：Harrison & Cole `HC-2025-0001` 总额 `$5,000`，2% 折扣正好 `$100`。
- **反向状态 B**：只把同一发票的总额改为 `$4,950`，2% 折扣随之为 `$99`；付款条件仍为 `2/10 Net 30`。
- **局部任务**：处理 `HC-2025-0001` 的付款安排和必要通知。
- **A 期望**：走 early-payment discount 路径。
- **B 期望**：按标准账期处理，不发送 early-payment discount notification。
- **评分**：原任务本身已经同时包含 `$100` 必须通知和 `$99` 不得通知的评分逻辑；paired fixture 复用这两侧规则。

## 暂不进入这一批的两个原候选

- **原 #15 Prairie Star short-dated**：制作时发现 SOP 的“`<15 days` 才额外通知 Director”与目标任务现成评分器对 15/16 天的要求冲突，移出 v0。
- **原 #20 CareIG Physician_NPI**：原始邮件实际写的是 `NPI: NPI`，而 SOP 明写的是 Physician_NPI **blank** 时触发 hold。先不替上游把占位值解释成 blank，降为待核。

#10 beneficiary 生存状态仍是好候选，但其决定 Linda 已故的具体二进制附件还没有被安全地读出和定位，因此不进入第一批 runnable fixture；不是概念上淘汰。