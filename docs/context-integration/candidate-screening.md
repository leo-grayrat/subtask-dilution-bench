# 上下文不参与决策：Pilot 候选筛选记录

这是一份工作中的筛选记录，不是冻结后的正式题库。目标是先从 HANDBOOK.md 的真实任务中找出适合四层测试的局部决策，并把不适合的案例也记录下来，避免以后只记得“看起来很典型”的成功例子。

## 当前筛选范围

目前检查了六个 HANDBOOK 任务：

- `tasks/finance_meridian_partners_158b9045`
- `tasks/hr_crestwood_university_1b602061`
- `tasks/logistics_prairie_star_creamery_861b2650`
- `tasks/insurance_vanguard_shield_mutual_9b2f7a29`
- `tasks/medical_careig_specialty_pharmacy_f5947c33`
- `tasks/hr_ridgeline_gear_co_44e4c745`

这些任务都包含完整工作环境、较长 SOP / policy 和程序化评分器，不是我们自己编写的情境题。

> 财务任务的当前 workspace 中 SOP 是 `SOP-FIN-AP-004.docx`。GitHub 文本接口不能直接读取这个二进制文件，因此下面涉及具体 SOP 文字的判断同时参考了另一个 Meridian Partners 任务中的同编号 HTML 版 SOP。正式冻结样本前，需要再用可读取 docx 的本地流程核对原任务中的确切版本。财务任务自己的 rubric 和邮箱状态则直接来自目标任务。

## 候选记录

| 状态 | 来源 | 局部决策 | 当前情况下应该怎样做 | 正反版本是否干净 | 备注 |
| --- | --- | --- | --- | --- | --- |
| **保留** | Finance | Cascade IT Hardware：信用单 `CM-38720` 为 $2,000，而原发票 `INV-38720` 为 $1,950 | 不直接应用信用单；把原发票置于争议 hold，并向供应商要求澄清 / 修正 | **较干净**：把信用单金额改为不超过原发票即可翻转处理方式 | 原任务已有邮件、hold 状态、Outstanding Credit 等多个程序化检查 |
| **保留** | Finance | Redwood Furniture `RF-8125`：发票数量 5，小于收货数量 10 | 作为部分发票正常处理，不应因为数量不一致而 hold，也不需要联系供应商 | **较干净**：把发票数量改为大于收货数量，处理方式翻转为 hold / 核实 | 原任务直接检查 approved、payment queue、match log 和“不发送多余邮件” |
| **备用** | Finance | Apex Office Supply `INV-2025-09745`：同样是发票数量小于收货数量 | 正常处理部分发票，不判重复、不联系供应商 | 干净，但与 Redwood 高度重复 | 可作为同类复现题，不宜和 Redwood 一起占第一版太多比例 |
| **备用** | Finance | SecureNet Compliance：供应商发送法律威胁邮件 | 按规定升级处理，不回复供应商；原任务要求发送 LEGAL THREAT 内部通知 | **不够干净**：该发票同时涉及 audit hold | 现象很典型，但两个独立约束叠加，不适合第一批干净配对 |
| **备用 / 暂不进 v0** | Finance | Pinnacle Print Services：邮件要求立即修改银行账户 | 不修改银行信息；按银行变更流程升级并进行独立验证 | **不够干净**：AP Clerk 本来就无权直接修改银行信息 | 更适合以后做复杂多阶段约束 |
| **保留** | HR / Crestwood | `HR office light bulb out – Main Campus rm 214`：Facilities 要 HR 确认进场更换灯泡时间 | 这是 SOP 明确列出的非 HR 范围事项；不代替 Facilities 处理，按 out-of-scope 规则升级 | **较干净**：把请求改为一个 SOP 明确覆盖的 HR 请求即可翻转 | 原任务直接检查“不发邮件给 facilities”、`[OUT OF SCOPE]` Slack 和邮件归档 |
| **备用** | HR / Crestwood | `Getting Fed Up`：一封邮件同时包含 Employee Relations 和 Payroll 两类问题 | 按两个主题分别转交，并按多主题模板合并回复 | 可做，但反向版本比单规则案例复杂 | 适合以后研究“一条信息同时激活多个约束” |
| **保留** | Logistics | `Pest Contamination`：TexPal 到货多块托盘发现新鲜鼠类粪便 | 判为 Class 4 / P1，整单拒收并立即升级；更新 receiving log 并发出规定通知 | **较干净**：把污染改为纯外观轻微损伤，可翻转为接受并记录 | SOP 明确把 pest evidence 列为 Class 4；原任务有多项自动检查 |
| **备用** | Logistics | `Delivery Waiting!!!!!!!`：司机在门口等候，同时邮件提到高温和安全焦虑 | 原任务评分要求转给 DC Manager 并按超范围事项升级 | **不够干净**：门禁、安全和高货温多个信号混在一起 | 单事实修改很难隔离真正触发条件 |
| **保留** | Insurance | Intercompany suspense `OPS-12`：存在审批信息，但审批人是 junior analyst，不是 manager | 对 >$5,000 项目不能把该信息当作有效经理批准；保留为 exception，不能清为 FIN-100 | **很干净**：只把审批人的角色改成 manager，即可翻转为可清账 | SOP 明确要求 >$5,000 项目在 `finance-approvals` 中找到 manager approval；原 rubric 明确检查“junior analyst 不够” |
| **备用** | Insurance | `OPS-4`：支持材料存在，但找不到 >$5,000 项目的 Slack 批准 | 保留为 exception，不能清为 FIN-100 | 干净，但与 OPS-12 属于同一规则 | 可留作同类复现，不急着和 OPS-12 同时进入首批 |
| **保留** | HR / Ridgeline | Kirsten Saunders：FMLA 申请人过去 12 个月只工作 1,100 小时 | 判定当前不满足 FMLA 资格，并告知可能适用 Colorado FAMLI | **很干净**：只把 hours worked 从 1,100 改到 ≥1,250，FMLA 这一资格条件翻转 | SOP 明确要求至少 1,250 小时；原 rubric 直接检查基于 1,100 小时作出的不合格通知 |
| **保留** | Medical | Rodriguez：联系记录已有 3 次尝试且均未联系到患者 | 触发 unreachable 流程：发送规定通知、记录并停止继续处理 | **很干净**：把其中一次联系结果改为 Reached，即不再满足“三次均失败”的停止条件 | SOP 明确规定 3 entries 且 none is Reached 时必须停止；原 rubric 检查 Slack、邮件和日志 |
| **备用** | Medical | Webb：PA 所需材料中存在无效文件，原 rubric 要求不得提交 PA | 触发 PA hold 和 Stop Protocol，不得继续提交 | 原理上可通过把无效文件换成有效文件翻转，但还需进一步确认具体无效原因 | 先不进入第一批，避免把“文件是否有效”的多个潜在条件混在一起 |

## 当前结论

目前有 **7 个较强的保留候选**：

1. Cascade：信用单金额超过原发票；
2. Redwood：部分发票数量小于收货数量；
3. Crestwood：HR 收到明确超出职责范围的维修请求；
4. Prairie Star：Class 4 污染导致拒收与升级；
5. Vanguard Shield：大额清账的批准人身份不合格；
6. Ridgeline：FMLA 的 1,250 小时资格门槛；
7. CareIG：三次联系失败后必须停止流程。

这 7 个案例来自六个完整任务，触发条件分别涉及金额比较、数量关系、职责范围、污染等级、审批人身份、资格阈值和历史尝试状态。它们已经开始体现我们希望的多样性，而不是把同一种“禁止动作”换皮多次。

接下来继续从 HANDBOOK 的其他任务中按同样标准补充候选，目标仍是约 20～30 个局部决策。在达到足够数量前，不冻结题库，也不运行被测模型。