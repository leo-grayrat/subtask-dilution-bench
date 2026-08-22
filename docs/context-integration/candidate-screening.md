# 上下文不参与决策：Pilot 候选筛选记录

这是一份工作中的筛选记录，不是冻结后的正式题库。目标是先从 HANDBOOK.md 的真实任务中找出适合四层测试的局部决策，并把不适合的案例也记录下来，避免以后只记得“看起来很典型”的成功例子。

## 当前筛选范围

目前检查了三个 HANDBOOK 任务：

- `tasks/finance_meridian_partners_158b9045`
- `tasks/hr_crestwood_university_1b602061`
- `tasks/logistics_prairie_star_creamery_861b2650`

三个任务都包含完整工作环境、较长 SOP / policy 和程序化评分器，不是我们自己编写的情境题。

> 财务任务的当前 workspace 中 SOP 是 `SOP-FIN-AP-004.docx`。GitHub 文本接口不能直接读取这个二进制文件，因此下面涉及具体 SOP 文字的判断同时参考了另一个 Meridian Partners 任务中的同编号 HTML 版 SOP。正式冻结样本前，需要再用可读取 docx 的本地流程核对原任务中的确切版本。财务任务自己的 rubric 和邮箱状态则直接来自目标任务。

## 第一批候选

| 状态 | 来源 | 局部决策 | 当前情况下应该怎样做 | 正反版本是否干净 | 备注 |
| --- | --- | --- | --- | --- | --- |
| **保留** | Finance | Cascade IT Hardware：信用单 `CM-38720` 为 $2,000，而原发票 `INV-38720` 为 $1,950 | 不直接应用信用单；把原发票置于争议 hold，并向供应商要求澄清 / 修正 | **较干净**：把信用单金额改为不超过原发票即可翻转处理方式 | 原任务已有邮件、hold 状态、Outstanding Credit 等多个程序化检查，适合作为第一批样本 |
| **保留** | Finance | Redwood Furniture `RF-8125`：发票数量 5，小于收货数量 10 | 作为部分发票正常处理，不应因为数量不一致而 hold，也不需要联系供应商 | **较干净**：把发票数量改为大于收货数量，处理方式翻转为 hold / 核实 | 原任务直接检查 approved、payment queue、match log 和“不发送多余邮件” |
| **备用** | Finance | Apex Office Supply `INV-2025-09745`：同样是发票数量小于收货数量 | 正常处理部分发票，不判重复、不联系供应商 | 干净，但与 Redwood 高度重复 | 可作为同类复现题，不宜和 Redwood 一起占第一版太多比例 |
| **备用** | Finance | SecureNet Compliance：供应商发送法律威胁邮件 | 按规定升级处理，不回复供应商；原任务要求发送 LEGAL THREAT 内部通知 | **不够干净**：该发票同时涉及 audit hold，单改“是否法律威胁”未必能让“能否联系供应商”翻转 | 现象很典型，但存在两个独立约束叠加，不适合第一批干净配对 |
| **备用 / 暂不进 v0** | Finance | Pinnacle Print Services：邮件要求立即修改银行账户 | 不修改银行信息；按银行变更流程升级并进行独立验证 | **不够干净**：AP Clerk 本来就无权直接修改银行信息，即使验证成功，核心动作也不会简单翻转 | 很真实，但更适合以后做复杂多阶段约束，不适合最初的单事实反向版本 |
| **保留** | HR | `HR office light bulb out – Main Campus rm 214`：Facilities 要 HR 确认进场更换灯泡时间 | 这是 SOP 明确列出的非 HR 范围事项；不代替 Facilities 处理，按 out-of-scope 规则升级 | **较干净**：把邮件主题和请求改为一个 SOP 明确覆盖的 HR 请求，即可翻转是否走 out-of-scope 流程 | 原任务直接检查“不发邮件给 facilities”、`[OUT OF SCOPE]` Slack 和邮件归档 |
| **备用** | HR | `Getting Fed Up`：一封邮件同时包含 Employee Relations 和 Payroll 两类问题 | 同一邮件需要按两个主题分别转交，并按多主题模板合并回复 | 可做，但反向版本比单规则案例复杂 | 原 rubric 很完整，适合以后研究“一条信息同时激活多个约束”，第一批先不急着用 |
| **保留** | Logistics | `Pest Contamination`：TexPal 到货多块托盘发现新鲜鼠类粪便 | 判为 Class 4 / P1，整单拒收并立即升级；更新 receiving log 并发出规定通知 | **较干净**：把“鼠类粪便/污染”改为纯外观轻微损伤，可翻转为接受并记录 | SOP 明确把 pest evidence 列为 Class 4；原任务已有 receiving log、Slack、转发邮件等自动检查 |
| **备用** | Logistics | `Delivery Waiting!!!!!!!`：司机在门口等候，同时邮件提到高温和安全焦虑 | 原任务评分把它当作超出 Inventory Analyst 范围，要求转给 DC Manager 并发 `OUT OF SCOPE` | **不够干净**：邮件同时混有门禁、安全和“86F cargo temp”等多个信号 | 如果只改一个事实，很难确定到底是哪条信息导致处理方式变化，因此暂不进第一版 |

## 当前结论

第一批最值得继续制作四层测试的有四个：

1. Cascade 信用单金额超过原发票；
2. Redwood 部分发票；
3. Crestwood HR 的灯泡 / 非 HR 范围请求；
4. Prairie Star 的 Class 4 污染。

这四个案例来自三个不同工作领域，动作类型也不同：财务状态修改、发票处理、请求路由、物流拒收与升级。它们比单纯堆很多相似的“禁止发送邮件”案例更适合作为第一批原型。

接下来继续从 HANDBOOK 的其他任务中按同样标准补充候选，目标仍是约 20～30 个局部决策。在达到足够数量前，不冻结题库，也不运行被测模型。