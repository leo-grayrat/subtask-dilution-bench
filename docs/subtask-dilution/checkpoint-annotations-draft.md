# 子任务稀释：9 题自然检查点标注草案

日期：2026-08-26

本文档接续 candidate-config-draft-v0.md（9 题主方案与备位），为每题做自然检查点的结构预标注：即实验中"任务进行到一半、冻结现场、分 direct/sham/reconsider 三条件继续"的分叉位置。标注依据 design.md 第 4 节（自然 checkpoint 规则与标准 6）、第 5 节（三条件定义）、execution-prep.md 第三部分（触发清单与状态快照 manifest 字段）。

**红线遵守**：未运行任何基准任务、未启动任何代理；HANDBOOK 仓库只读；未修改任何既有文档；全部阶段与事件推断均引用缓存材料的具体出处，无材料依据之处标注"推测"；本文档是草案，触发条件清单须在正式冻结时按 execution-prep.md 第 3.1 节格式化并生成 checkpoint_trigger_version 与 checkpoint_trigger_sha256 后才生效。

## 0. 通用约定

### 0.1 三条件操作定义（design.md 第 5 节）

- direct：不增加任何暂停提示，由调度器直接发起原本就会发生的下一次模型调用，不新增任何用户/助理消息（§5.1 及第 5 节分叉边界规定）。
- sham：在副本中注入一次冻结提示（§5.2 原文）："请简要记录当前进度和接下来的步骤，然后继续完成原任务。"
- reconsider：在副本中注入一次冻结提示（§5.3 原文）："在决定下一步前，请检查刚完成或准备推进的这一步：是否存在成本相近但更符合最终目标的处理；如果原方案已经合适，就保持不变。然后继续完成原任务。"
- 暂停预算：sham 与 reconsider 各一个不调用工具的短回合，默认 ≤256 tokens，之后与 direct 相同的剩余预算（§5.4）。
- 上述三条件操作对任何任务、任何检查点完全相同；reconsider 提示为 §5.3 通用模板原文，不点名字段、约束、错误类别或正确答案，无加强暗示。各题小节不再复述三条件操作，只标注平台级可行性限制。

### 0.2 事件类别记号（design.md §4.1）

E1=读取覆盖完成且零写入；E2=第一次状态写入已返回；E3=第一次外部分析/测试/检索结果返回；E4=一个中间产物完成、下一阶段未开始；E5=所有要求产物已存在、尚未最终核验与交付。每个触发条件按 execution-prep.md §3.1 字段书写：observable_event（机器可判断）、event_detection（信号来源与判定方法）、capture_items、on_not_triggered。

### 0.3 标准 6 的检查口径

标准 6：检查点位置的选择不得依赖"模型最可能在哪里犯错"的先验知识。本文档逐点检查三条判据：(i) 触发事件是计数/存在/类型型事件，不引用只出现在期望答案、断言或评分项中的具体实体名与数值；(ii) 检查点上的局部决定来自任务说明、SOP 或政策的自然阶段划分，而非由评分表反推的易错点；(iii) 不含 design §4.1(5) 禁止的预期答案、可疑字段或猜测失败类型。
## 第一部分：主方案 9 题逐题标注

### 题 1：9b2f7a29（三月公司间 suspense 对账工作簿；HANDBOOK；类别 1）

**1. 任务流程分解**（依据：instruction.md 全文、environment/initial_workspace/SOP_VanguardShield.html §2.1、tests/rubrics.json 12 条）

- P1 材料读取：SOP、Suspense_March2026.xlsx、10 个 INV-SUSP-*.pdf、Jira 与 Slack 现状（instruction 第 1 段："The suspense workbook and SOP are in the workspace"）。
- P2 逐项核查：按 SOP §2.1 分层（≤$5,000 逐项对 PDF/子任务；>$5,000 另验 Slack finance-approvals 审批），每项形成 Support Found / Conflict 判定。
- P3 工作簿产出：生成 Suspense_Reconciliation_March2026.xlsx，含五个 tie-out 列（instruction 第 2 段逐字列出列名）。
- P4 Jira 外部记录：清账项在子任务写 "FIN-100 Cleared & Posted" 评论；异常项建 FIN-Exceptions 工单、指派并留升级评论（SOP §2.1 的 Clear items 与 Exception handling 步骤）。
- P5 终局核对与交付（instruction 第 1 段提到 Marcus 在催进度；交付形式材料未写明，此处为**推测**）。

**2. 候选检查点**

- CP1（E1，P1/P2 边界）：触发事件=指定输入集合（SOP html、Suspense_March2026.xlsx、全部 INV-SUSP-*.pdf、Jira 与 Slack 现状读取）均已出现在读取事件，且工作区写入事件数为零、外部写入事件数为零；判定信号=事件日志中读取/写入事件计数；局部决定=对账执行规划（各待处理项的处理顺序、金额分层口径、证据源分工）。on_not_triggered：根运行结束前读取覆盖未完成即记为未触发，不补位。
- CP2（E2，P2 早期）：触发事件=第一个写类工具调用（工作区文件写入、Jira 评论/工单创建、Slack 消息发送三类之一）已返回，且其后尚未出现下一个写类调用；写类清单随触发清单一起冻结；局部决定=首个处理项的结果记录方式（清账/例外的归类与落账形式）。
- CP3（E4，P3/P4 边界）：触发事件=Suspense_Reconciliation_March2026.xlsx 首次出现在工作区（文件创建事件），且此刻外部状态中尚无新建工单类写入；局部决定=异常项的外部记录方式（工单内容、指派人、升级评论）。若实际轨迹先建工单后成工作簿，本条件记未触发，由备用条件接管。
- CP4（备用，E5）：触发事件=要求产物集合齐备（工作簿存在，且清账与异常各有对应外部写入记录出现），尚未最终核验；产物集合按任务级定义（来自 instruction 与 SOP §2.1 的要求，不取自评分项内容）；局部决定=交付前是否做整体自查。

**3. 标准 6 检查**：四个触发均为计数/存在事件，不引用任何具体待处理项编号、清账状态词或 GL 编码（这些只出现在评分层）。无围绕错误位置设计风险。

**4. 三条件适用性**：按 0.1。平台限制：harness 须支持无提示 direct 继续与状态导出（execution-prep §2.5 的 M2/M5），否则按 design 第 5 节第 2 段处置。

**5. 状态快照要点**：conversation_sha256（完整对话与系统提示）、workdir_manifest_sha256（含已生成的工作簿）、external_state_sha256（jira_state.json、slack.json、inbox.json、calendar_data.json 逐项哈希后聚合）、tool_results_sha256、remaining_budget_*（三项）、model_config_id。外部状态完全文件化（execution-prep 第二部分前置事实已核查），第一档状态复制的文件侧基础好。

**6. 风险标注**：执行环境依赖 Docker（草案 M-1/Q-E），本题全部检查点的成立待实测；标准 3（局部做差后可继续）待实测；P5 交付形式为推测，CP4 冻结时建议简化为仅查"要求产物集合齐备"。
### 题 2：finance-create-10k-income-report（TheAgentCompany；类别 1）

**1. 任务流程分解**（依据：.materials-cache/round4/tac_finance-create-10k-income-report.task.md 全文与同名 checkpoints.md）

- P1 Owncloud 导航：进入 /Documents/Financials/Annual%20Reports/10Ks，枚举多家公司 10-K（checkpoints.md Checkpoint 1）。
- P2 逐公司提取：从各 10-K 的 section/item 8 提取 2021、2022、2023 三年 net income（task.md 第 2 行）。
- P3 表格构建：公司名按 charter 法定注册名、$M 计量、年际百分比变化保留 1 位小数（task.md 列结构段）。
- P4 保存 /workspace/net_income_report.csv（task.md 同段）。
- P5 交付与建议：Rocketchat 发文件路径给财务负责人 David Wong，并按 2022-2023 最大百分比增长给出投资建议（task.md 末段，对应 Checkpoint 5）。

**2. 候选检查点**

- CP1（E3，P1/P2 边界）：触发事件=目标 Owncloud 目录第一次成功枚举/列表返回，且尚无 10-K 文档内容被解析（无文档读取事件）；局部决定=提取方式（文档解析工具选择、公司处理顺序）。
- CP2（E4，P2 中期）：触发事件=第一个"公司年数据被记录"的写入事件返回（CSV 首数据行或中间笔记文件写入）；局部决定=取值口径（$M 单位换算、舍入口径、法定注册名的认定方式）。
- CP3（E5，P4/P5 边界）：触发事件=net_income_report.csv 首次存在于 /workspace，且尚无 Rocketchat 发送事件；局部决定=投资建议的计算与表述（最大增长口径复核）。
- 备用 CP4（E3）：第一份 10-K 文件下载成功返回（早于 CP1 的失败兜底）。

**3. 标准 6 检查**：触发均为导航/文件事件，不引用任何公司名、具体数值或评分点内容。提示：冻结时不得把"某公司数值是否提取正确"类信息写入触发文本——那是评分层信息。

**4. 三条件适用性**：按 0.1；依赖 TheAgentCompany 自托管服务栈（Owncloud、RocketChat）的状态快照能力。

**5. 状态快照要点**：workdir_manifest_sha256（/workspace）、external_state_sha256（Owncloud 文件状态与 RocketChat 消息状态；具体状态承载物与可哈希性待实测确认）、conversation、tool_results、remaining_budget_*。

**6. 风险标注**：依赖 Docker 与 30GB 量级服务栈（M-1/Q-E）；外部服务状态快照的介质与保真度待实测；评分为终局程序化执行、过程无评分反馈（草案 1.4 已判"延迟"），不影响触发设计。
### 题 3：financial_stmt_reconstruction_aapl_fy2024（Agents' Last Exam；类别 1）

**1. 任务流程分解**（依据：ale_business_finance_financial_stmt_reconstruction_aapl_fy2024.task_card.json 的 taskPrompt、agentMustDo、inputFiles、evaluation 字段）

- P1 读取输入：TASK_PROMPT.md、aapl-2024-10k.pdf、aapl-20240928.htm（EDGAR HTML）、output_schema.json、material_sources.md；任务约束为不得修改 base/input（taskPrompt 原文）。
- P2 定位报表：在 10-K 材料中找到 Consolidated Balance Sheets（agentMustDo 第 1 条），建立与 output_schema 字段的映射。
- P3 逐字段取值：对 schema 每个要求字段取 2024-09-28 列数值（agentMustDo 第 2 条），双源材料（PDF 与 HTML）间存在取值裁决空间。
- P4 写出 base/output/balance_sheet.json（taskPrompt 原文路径）。
- P5 交叉核对与定稿：schema 完整性、双源一致性自查（由任务"exactly as reported"要求自然导出）。

**2. 候选检查点**

- CP1（E1，P1/P2 边界）：触发事件=指定输入文件（task_card inputFiles 列举集）均出现在读取事件，且 base/ 下写入事件数为零；局部决定=提取工具链（task_card.software 列举 Python、pdftotext、grep）与主数据源选择。
- CP2（E2，P3 早期）：触发事件=base/ 下非 input 目录的第一个写入事件返回（工作笔记或 JSON 片段）；局部决定=字段映射方式与取值口径。
- CP3（E4，P4/P5 边界）：触发事件=balance_sheet.json 首次存在；局部决定=是否执行 schema 全字段与双源交叉核对——任务完成前的自然自查阶段，不针对任何已知数值错误。
- 备用 CP4（E3）：第一次成功的文本提取/解析结果返回（如 pdftotext 首次产出）。

**3. 标准 6 检查**：触发均为文件事件；不引用 schema 字段名、隐藏参考文件的任何数值（评分器 ale_finstmt_score_outputs.py 为对隐藏参考做 Decimal 精确比对，本轮已核源码，参考值属评分层）。

**4. 三条件适用性**：按 0.1。

**5. 状态快照要点**：workdir_manifest_sha256（整个 base/ 目录，含输入文件哈希以核验"输入未被修改"约束）、conversation、tool_results、remaining_budget_*；external_state 不适用（无外部服务），字段按冻结约定记空。

**6. 风险标注**：依赖 Linux VM 执行环境（task_card.vm 写明，属 Q-E 家族）；仓库 secret/ 目录的隔离须核验（草案 M-8），确保隐藏参考文件不进入代理可见状态与快照；CP2 以代理实际写中间文件为前提，若代理全程内存作业则记未触发、由备用 CP4 接管。
### 题 4：T1 django__django-13495（SWE-bench test 分片；类别 2）

**1. 任务流程分解**（依据：.materials-cache/swe_bench/test.parquet 的 problem_statement 原文；candidate-search-round2.md T1 条目：触及 7 个文件，为四个数据库后端的 operations 层加 models/functions/datetime.py，F2P 5、P2P 74）

- P1 读取与定位：issue 报告 Trunc 家族函数仅在 output_field=DateTimeField 时把 tzinfo 传入 SQL（problem_statement 引 as_sql 代码：DateField/TimeField 分支不带 tzname）。
- P2 复现：构造或运行能展示缺失行为的测试（SWE 工作流常规阶段）。
- P3 修复实现：让日期/时间截断在多后端下应用时区转换（涉及公共分发路径与各后端 trunc SQL 生成）。
- P4 测试与回归：运行相关测试套件。
- P5 终稿整理：差异清理。

**2. 候选检查点**

- CP1（E2，P2/P3 边界）：触发事件=仓库检出上第一个源代码文件写入事件返回，且其后尚无下一个源代码写入；局部决定=修复位置选择（公共 as_sql 路径统一处理还是逐后端分改）——issue 原文引用公共代码，该决策自然存在。
- CP2（E3，P3/P4 边界）：触发事件=第一次测试命令运行返回（不论退出码）；局部决定=对测试结果的响应方式与回归核验范围。
- CP3（E5，P4/P5 边界）：触发事件=出现一次退出码为 0 的测试运行，且其后未再出现代码文件写入（冻结时定义检测窗口，例如末段事件中最后一次为退出码 0 的测试运行）；局部决定=是否做跨后端覆盖复核与差异范围自查。
- 备用 CP4（E3）：第一次退出码非 0 的测试运行返回（首次复现结果，自然事件）。

**3. 标准 6 检查**：触发均为写入/测试事件；不引用 FAIL_TO_PASS/PASS_TO_PASS 测试清单与参考补丁内容（均属评分层）。CP1 的局部决定来自 issue 引用的代码结构，不是已知失败知识。

**4. 三条件适用性**：按 0.1。注意：SWE 任务测试可随时运行（即时反馈），三条件操作不变；是否触发 source-selection.md §3.6 排除条款由草案实测项 M-4 判定。

**5. 状态快照要点**：workdir_manifest_sha256（git 工作区，含未提交修改清单与逐文件哈希）、conversation、tool_results（含已返回的测试输出）、remaining_budget_*；external_state 不适用。

**6. 风险标注**：依赖容器环境（M-1）；M-4 为本题成立前提（即时反馈强度、fork 点能否形成有意义的中间状态）；代理若反复"改-测"振荡，CP3 按冻结的检测窗口判定，误判风险如实记录。
### 题 5：T4 scikit-learn__scikit-learn-11542（SWE-bench test 分片；类别 2）

**1. 任务流程分解**（依据：.materials-cache/swe_bench/test.parquet 的 problem_statement 原文；candidate-search-round2.md T4 条目：触及 6 个文件，含 4 个 example、forest.py 与 estimator_checks.py，F2P 5、P2P 222）

- P1 读取与定位：issue 提议把 RandomForest 默认 n_estimators 从 10 改为 100（problem_statement 原文）。
- P2 方案决策：直接改默认值，还是走弃用周期——issue 原文写有 "deprecation of the current default will show people they have a bug" 与 "I'm not sure if I want to tag this 1.0"，两条路径均为题面给定。
- P3 实现：主代码默认值修改，示例与通用检查器同步（第二轮条目的文件分布）。
- P4 测试与回归；P5 终稿整理。

**2. 候选检查点**

- CP1（E2，P2/P3 边界）：触发事件=第一个源代码文件写入返回，且其后尚无下一个源代码写入；局部决定=默认值处理方式（直接修改或弃用警告周期）与版本标记。
- CP2（E3，P3/P4 边界）：触发事件=第一次测试命令运行返回（不论退出码）；局部决定=失败处理与示例/检查器同步范围。
- CP3（E5，P4/P5 边界）：触发事件=出现一次退出码为 0 的测试运行且其后无代码写入（检测窗口定义同题 4）；局部决定=回归核验范围与差异自查。
- 备用 CP4（E2）：第二个写类事件返回（顺序型中性事件，主条件未触发或彼此重叠时兜底）。

**3. 标准 6 检查**：触发不引用参考补丁的文件清单（第二轮记录的 6 文件信息来自参考补丁，只能作结构核对材料，不得写入触发定义——参考补丁文件列表属于期望答案成分，引用即违反标准 6）；不引用 F2P/P2P 清单。

**4. 三条件适用性**：按 0.1；即时反馈与排除条款判定同题 4（source-selection.md §3.6）。

**5. 状态快照要点**：同题 4（git 工作区、conversation、tool_results、预算）。

**6. 风险标注**：M-1、M-4 同题 4。补充：本题局部决定（弃用策略）在题面中有明确政策空间，三条件比较有意义；若代理跳过策略权衡直接改值，CP1 仍按事件触发，局部决定内容按轨迹如实记录。
### 题 6：3d-model-format-legacy（Terminal-Bench；类别 2）

**1. 任务流程分解**（依据：.materials-cache/round4/tb_3d-model-format-legacy.yaml 的 instruction 全文）

- P1 读取：/app/MdfLib 源码、/app/JSON_FORMAT.md、/app/MdfLib/test_models 样例，未修改任何文件。
- P2 构建现代化：使 2007 年 win32 库在当前系统可构建（instruction 要求 1 与 "You must use cmake to build the library and the test"）。
- P3 编写转换器：用该库加载样例模型并转换为 JSON（要求 2）。
- P4 批量转换：全部模型文件转换到 /app/converted_models/<basename>.json（要求 3）。
- P5 规格符合性：JSON 遵循 JSON_FORMAT.md（要求 4）。

**2. 候选检查点**

- CP1（E1，P1/P2 边界）：触发事件=读取事件覆盖 /app/MdfLib 源码文件集合与 JSON_FORMAT.md，且 /app 下写入事件数为零；局部决定=现代化路线（构建体系搭建、win32 专有 API 的替代策略）。
- CP2（E3，P2/P3 边界）：触发事件=第一次成功构建返回（构建命令退出码 0 事件）；局部决定=转换器实现方式（库 API 的使用方式、JSON 映射结构）。
- CP3（E4，P3/P4 边界）：触发事件=/app/converted_models 中第一个转换产物出现（首个 .json 文件出现事件），其余模型尚未转换；局部决定=批处理方式与字段映射一致性（首个产物的映射方案如何推广到其余模型）。
- 备用 CP4（E5）：converted_models 文件数等于 test_models 模型数，规格核验未执行。

**3. 标准 6 检查**：触发均为构建/文件事件；隐藏测试套件对代理不可见（草案 1.3 来源共性），触发层不触及任何测试内容，满足标准 6。

**4. 三条件适用性**：按 0.1。

**5. 状态快照要点**：workdir_manifest_sha256（容器内 /app 全量，含构建中间产物，逐文件哈希）、conversation、tool_results、remaining_budget_*（注意该任务 max_agent_timeout_sec=1200，剩余时间预算字段必须继承）；external_state 不适用。

**6. 风险标注**：依赖 Docker（M-1/Q-E）；构建错误链可能很长，CP2 出现时点在根运行中可能偏后，属触发时序的自然分布，如实记录；预算继承（时间预算为主）按 remaining_budget_seconds 字段。
### 题 7：d9d532c1（佣金截止日；HANDBOOK；类别 3）

**1. 任务流程分解**（依据：instruction.md 全文；Sunshine_Set_Automotive_SOP.pdf 章节结构实测提取：§7.1 Commission Calculation and Verification、§7.2 Chargeback Offsets、§7.3 Spiffs, Bonuses, and Adjustments、§7.4 Payroll Submission and Deadlines、§2.5 Deal Cancellation and Unwind；tests/rubrics.json 6 条）

- P1 读取：SOP、收件箱佣金表（四张：Olivia Mercer 与 Trent Holloway 各两期）、Deal_Log、Chargeback_Tracker 等辅助表。
- P2 佣金表核验：按 SOP §7.1 核对当期佣金行与成交日志及支持材料（评分项提及当期成交与前期间调整，属评分层信息）。
- P3 Chargeback 与调整处理：按 SOP §7.2 做抵减计算、按 §7.3 处理前期间调整行。
- P4 发出全部要求通信（instruction 原文 "send all the required communications for the commissions from the Sunshine_Set_Automotive_SOP for all steps"）：工资提交邮件、chargeback 通知邮件、Slack 异常成交标记与佣金表负责人通知。
- P5 终局核对（评分含负向项：不得升级某差异、不得把特定成交列为常规行——属评分层）。

**2. 候选检查点**

- CP1（E1，P1/P2 边界）：触发事件=读取事件覆盖 SOP 与四张佣金表及成交日志，工作区写入事件数为零且外部发送事件数为零；局部决定=核验方法与异常处理顺序。
- CP2（E2）：触发事件=第一次外部通信写入（邮件发送或 Slack 消息发送工具结果）返回，且其后尚无下一个通信发送；局部决定=该通信的收件人、内容与依据，及后续通信顺序。
- CP3（E5，P4/P5 边界）：触发事件=要求通信集合齐备（发送记录覆盖按任务级冻结的通信集合：工资提交邮件、chargeback 通知邮件、异常成交标记消息、佣金表负责人通知——集合来自 instruction 与 SOP §7 的"全部步骤"要求，不来自评分项内容）；局部决定=收尾前是否做负向项自查。
- 备用 CP4（E2）：第一次工作区文件写入返回（中间核验记录）。

**3. 标准 6 检查**：触发不引用任何成交编号、金额或人名；CP3 通信集合为收件人类型/通信类型级定义。无围绕错误位置设计风险。

**4. 三条件适用性**：按 0.1；平台限制同题 1。

**5. 状态快照要点**：conversation、workdir_manifest_sha256、external_state_sha256（邮箱发送记录、slack.json、calendar_data.json 逐项哈希）、tool_results、remaining_budget_*。"系统故障加急"为原生任务设定（草案 1.4），不影响分叉操作。

**6. 风险标注**：依赖 Docker（M-1）；通信发送顺序变异大，CP2 与 CP3 的触发先后可能互换——触发清单按独立条件逐行冻结，互不依赖；根运行若未发出某类通信，对应条件记未触发。
### 题 8：tau2-airline-44（τ2-bench airline 域，test 分片；类别 3）

**1. 任务流程分解**（依据：.materials-cache/round4/tau2_airline_tasks.json 中 id=44 的 user_scenario 与 evaluation_criteria；tau2_airline_policy.md；草案 1.1）

- P1 身份与预订信息收集：参考动作序列前段为 1 次 get_user_details 加 5 次 get_reservation_details。
- P2 时长判断与替代航班检索：10 次 search_direct_flight（为时长阈值判断与升舱备选航班做准备）。
- P3 报价与确认：升级前必须告知用户总成本并获确认（task_instructions 原文 "ask the agent to tell you how much it will cost you in total"）。
- P4 执行 DB 修改：3 次 update_reservation_flights（参考动作末段）。
- P5 收尾说明。

**2. 候选检查点**

- CP1（E1，P1/P2 边界）：触发事件=全部预订详情查询的工具结果已返回，且写类动作（update/cancel 族）调用计数为零；局部决定=时长阈值分派（取消条件 >4 小时、升舱条件 ≤3 小时，两个阈值来自 reason_for_call 原文）与对用户的沟通计划。
- CP2（P3/P4 边界）：触发事件=代理回合中已出现成本告知，且用户模拟器的确认回合已返回、第一个写类动作尚未发生；判定信号=工具事件序列加用户模拟器回合事件；局部决定=逐预订执行顺序与支付方式选择。本条件依赖用户模拟器回合事件的可观察性（实测项 M-2），不可观察时记未触发、由备用接管。
- CP3（E2，P4 中期）：触发事件=第一个写类动作返回，且其后尚无下一个写类调用；局部决定=后续写入的参数一致性（舱位、支付方式与已确认方案的关系）。
- 备用 CP4（E5）：全部写类动作已返回、对话未结束；局部决定=收尾核对与补充说明。

**3. 标准 6 检查**：触发只依赖工具类型计数与回合结构；不引用任何预订编号或断言内容（nl_assertions 属评分层；若以"处理某一特定预订后"为检查点，即构成围绕已知失败模式设计，本文档明确排除此类候选，见第三部分 3.2）。

**4. 三条件适用性**：按 0.1。特殊限制：三分支须由同一用户模拟器版本与种子在分叉后继续驱动；direct 不得注入任何消息（含模拟器附加回合）——此为 M-2 的核心内容。

**5. 状态快照要点**：conversation（对话与工具结果）、external_state=τ2 域数据库状态（导出/序列化方式待实测）、tool_results、remaining_budget（τ2 回合/预算口径待实测确认字段归属）、model_config_id 必须包含用户模拟器版本与种子。

**6. 风险标注**：M-2（用户模拟器与 reward 函数能否在对话中途状态分叉后重放）是本题检查点成立的一票否决项；对话分叉重放保真度（三分支中模拟器行为是否一致）依赖实测；DB 状态快照介质依赖实测。
### 题 9：2ddae3b7…361f294（Queen Anne 房价最低成交价；AssistantBench validation；类别 3/1 边缘）

**1. 任务流程分解**（依据：.materials-cache/round3/assistantbench_validation.parquet 该题 task、answer、explanation、gold_url 字段；explanation 原文："You need to first find the dataabase of historical prices (privided by the King County Gov Assessor) and then use their API to find historical prices"，原样如此）

- P1 问题分解与信息源认定（历史成交价数据库的确定）。
- P2 数据源导航与查询（站点导航或 API 访问）。
- P3 筛选口径执行（社区、物业类型、成交月份三个口径，均来自 task 原文）。
- P4 最低价聚合。
- P5 答案提交。

**2. 候选检查点**

- CP1（E3，P1/P2 边界）：触发事件=第一次成功的网页抓取/检索返回；局部决定=信息源选择与查询路线（页面浏览或 API）。该事件为中性事件：不预先指定"正确信息源"。
- CP2（E3，P2/P3 边界）：触发事件=第一批成交记录内容返回（检索结果中出现记录集合），筛选尚未执行；局部决定=筛选执行方式（利用站点自带筛选或抓取后本地过滤）。
- CP3（E5，P4/P5 边界）：触发事件=最终答案提交动作之前的最后一个模型回合（运行器把答案提交识别为特定终结动作）；局部决定=聚合结果复核与答案形式。
- 备用 CP4（E4）：第一次成功的中间笔记/候选清单写入（代理不写笔记时记未触发）。

**3. 标准 6 检查**：触发不引用日期、答案数值或 gold_url；CP1 以"第一次成功抓取"为中性事件，不预设信息源对错。

**4. 三条件适用性**：按 0.1。

**5. 状态快照要点**：conversation、workdir（笔记文件若有）、tool_results（含已抓取的页面内容哈希——页面漂移是 live web 形态的固有风险）、remaining_budget_*；external_state=live web 不可冻结，快照只记录已访问 URL 与内容哈希，分叉后两分支的后续抓取面对的是同一外部世界而非同一快照（见风险）。

**6. 风险标注**：M-3（live web 漂移与可达性）对本题是一票否决级：若分叉后分支的抓取与原轨迹面对不同页面内容，"同一可见状态"只在历史部分成立；需要运行器层面的页面缓存/回放策略，否则本题检查点只能降级或按草案 2.3 撤换；答案数值稳定性同样受 M-3 约束；类别归属冻结时判定（草案 M-6）。
## 第二部分：备位题标注（草案 2.3 指定的备位替换题）

### 备位 B1：tau2-retail-55（题 8 备位）

**流程分解**（依据：tau2_retail_tasks.json id=55 的 user_scenario 与参考动作；tau2_retail_policy.md）：P1 身份确认（用户提供两个邮箱，参考动作为 2 次 find_user_id_by_email 加 get_user_details）；P2 订单枚举（6 次 get_order_details）；P3 未达订单取消（2 次 cancel_pending_order；政策要求写类动作前列明细节并获用户明确确认，policy 原文）；P4 已送达订单列明与确认（用户要求先列出物品再退货，reason_for_call 原文）；P5 退货执行（2 次 return_delivered_order_items，需确认订单、物品清单与退款支付方式）。

**候选检查点**：CP1（E1，P2/P3 边界）=全部订单详情查询返回且写类动作计数为零；局部决定=取消/退货资格分派与确认流程安排。CP2（E2）=第一个取消动作返回；局部决定=退货链的执行方式（退款支付方式与物品清单确认）。CP3（E2）=第一个退货动作返回；局部决定=第二笔退货订单的物品清单与支付方式。备用：用户确认回合返回后、第一个写类动作前（依赖回合事件可观察性）。

**标准 6 检查**：不引用订单编号、邮箱地址或期望动作数。三条件与快照同题 8（external_state 为 retail 域数据库）。**风险**：M-2 一票否决同题 8；多邮箱身份歧义属题面原生复杂度，不影响触发设计。

### 备位 B2：tau2-airline-18（题 8 备位）

**流程分解**（依据：tau2_airline_tasks.json id=18）：P1 信息收集（用户与预订查询）；P2 圈定全部商务舱预订；P3 批量降舱（5 次 update_reservation_flights，各预订支付方式不同——参考动作中含不同支付账户，降舱退款路径按政策处理）；P4 总节省额计算（用户接受退款处理完毕后再告知总额，task_instructions 原文）；P5 告知与收尾。

**候选检查点**：CP1（E1）=读取阶段完成且写类动作为零；局部决定=降舱范围界定与逐预订退款方式。CP2（E2）=第一个降舱动作返回；局部决定=后续各预订的支付方式处理。CP3（E5）=全部写类动作已返回、节省额尚未告知；局部决定=汇总口径与告知时机。备用：第一次费用/退款计算结果返回代理。

**标准 6 检查**：不引用预订编号与金额数值。**风险**：M-2 一票否决同题 8。
### 备位 B3：sympy__sympy-15198（题 5 备位，SWE 短名单 T3）

**流程分解**（依据：candidate-search-round2.md T3 条目与 test.parquet problem_statement 原文：1.3rc1 codegen 回归，octave/julia/jscode 打印器，issue 引用外部 commit e99b756）：P1 读 issue 与回归来源；P2 复现回归（octave codegen 对特定函数应报错而打印）；P3 定位修复层级（公共 codeprinter 一处修或各打印器分修，第二轮条目记录的潜在局部决定）；P4 实现与测试（F2P 3、P2P 115）。

**候选检查点**：CP1（E2）=第一个代码写入返回；局部决定=修复层级选择与跨语言打印器行为一致性。CP2（E3）=第一次测试运行返回；局部决定=回归修复覆盖面。CP3（E5）=退出码 0 测试运行出现且其后无代码写入；局部决定=终稿回归核验。备用：第一次失败测试运行返回（首次复现，自然事件）。

**标准 6 检查**：触发不引用期望行为、F2P/P2P 与参考补丁；issue 原文中的打印器名仅用于流程描述，不进触发文本。**风险**：题面短且指向外部 commit（第二轮已注），复现依赖 base_commit 仓库含该历史——属材料准备实测项；M-1/M-4 同题 4/5。

### 备位 B4：pydata__xarray-4827（题 5 备位，SWE 短名单 T7）

**流程分解**（依据：candidate-search-round2.md T7 条目与 problem_statement 原文：merge 的 combine_attrs 冲突值静默丢弃，请求新增选项）：P1 读 issue（现有四选项语义在题面原文列出）；P2 新选项语义与命名设计（issue 原文给出两个候选名）；P3 在 combine、concat、merge 三个入口实现一致行为（第二轮条目：触及 3 文件）；P4 测试（F2P 5、P2P 167）。

**候选检查点**：CP1（E2）=第一个代码写入返回；局部决定=语义设计与命名。CP2（E3）=第一次测试运行返回；局部决定=三入口行为一致性的落实方式。CP3（E5）=退出码 0 测试运行且其后无代码写入。备用：第二个写类事件返回（顺序型中性事件）。

**标准 6 检查**：不引用期望的选项名或 API 清单。**风险**：M-1/M-4 同题 4/5。
### 备位 B5：db-wal-recovery（题 6 备位，TB-B）

**流程分解**（依据：tb_db-wal-recovery.yaml instruction 全文）：P1 诊断（访问数据库，观察仅基础数据可读）；P2 分析 WAL 文件损坏或加密的成因；P3 修复 WAL 使 SQLite 可读；P4 提取全部数据（instruction 写明应恢复 11 条记录——任务目标值）；P5 生成 /app/recovered.json（按 id 排序的指定格式）。

**候选检查点**：CP1（E3，P1/P2 边界）=第一次数据库访问尝试的结果返回；局部决定=修复路线（重建、解密或手工解析）。CP2（E3，P3/P4 边界）=第一次对 WAL 修复写入之后的数据库成功读取事件返回；局部决定=提取方式与输出格式。CP3（E4，P4/P5 边界）=recovered.json 首次存在；局部决定=记录数与排序自查。备用：第一次对 WAL 文件的成功字节级分析操作返回。

**标准 6 检查**：触发不含记录数硬编码（"11 条"是 instruction 原文目标，可用于流程描述，但触发用"读取成功"事件表达）。**风险**：体量小（expert 45 分钟），单根运行内三个检查点时序紧凑、有效触发数可能不足 3，需实测确认；依赖 Docker（M-1）。

### 备位 B6：finance-revenue-reconciliation（题 2 备位，TAC-B）

**流程分解**（依据：tac_finance-revenue-reconciliation.task.md 与 checkpoints.md）：P1 在 Owncloud 定位并下载 contracts.xlsx 与 revenue_schedule.xlsx；P2 逐合同汇总收入确认条目并与合同金额比对（含小容差判断，task.md 原文 "within a small tolerance"）；P3 核对确认时间表与合同期限对齐；P4 产出 /workspace/flagged_contracts.xlsx；P5 依 employee_contracts.xlsx 识别被标记合同对应员工并经 RocketChat 联系。材料层事实注记：task.md 写的路径为 Documents/Human Resources Team/Contracts，checkpoints.md 核验的路径为 Documents/Financials/Contracts，两处描述不一致，原样记录，启用前须核实何者有效。

**候选检查点**：CP1（E3）=第一个文件下载成功返回；局部决定=核对口径与容差设置。CP2（E4）=flagged_contracts.xlsx 第一次写入事件返回；局部决定=标记判定口径（两类不一致的判定）。CP3（E2）=第一次 RocketChat 联系消息发送返回；局部决定=联系范围与内容。备用：第一个合同汇总计算的中间记录写入返回。

**标准 6 检查**：不引用合同编号、期望标记集合或评分路径。**风险**：依赖 Docker 服务栈（M-1/Q-E）；服务状态快照介质待实测。
### 备位 B7：admin-employee-info-reconciliation（题 2 备位，TAC-C）

**流程分解**（依据：tac_admin-employee-info-reconciliation.task.md 与 checkpoints.md）：P1 读取 /workspace/employees.csv；P2 经 RocketChat 枚举当前员工名单；P3 逐人 DM 核实信息（task.md 原文 "just DM them on RocketChat"）；P4 修订 CSV：补缺、纠错、更新。

**候选检查点**：CP1（E3，P1/P2 边界）=第一次 RocketChat 名单查询成功返回，CSV 无写入；局部决定=核实范围与 DM 策略。CP2（E2）=第一次 DM 发送返回；局部决定=核实问法与信息收集方式。CP3（E2，P4 早期）=第一次 employees.csv 写入返回；局部决定=自报信息与表内记录冲突时的取舍。备用：第一次收到员工回复（第一个接收消息事件返回）。

**标准 6 检查**：绝不以特定人名为触发（checkpoints.md 评分项点名了具体员工与具体错误，那是评分层信息；以"与某员工对话后"设检查点即构成围绕已知错误位置设计，本文档排除此类候选，见 3.2）。**风险**：DM 回复依赖 mock 服务行为，快照恢复后回复保真度待实测（execution-prep §2.2 风险点 c）；依赖 Docker（M-1）。

### 备位 B8：equity_research_summary（题 3 备位，ALE-B）

**流程分解**（依据：ale_business_finance_equity_research_summary.task_card.json）：P1 读取 instruction.md 与 source_urls.txt；P2 采集 Yahoo Finance 实时市场数据（quote 与 Statistics 页，agentMustDo 第 1 条）；P3 采集 SEC EDGAR FY2023 三表（agentMustDo 第 2 条）；P4 构建 Calc 工作簿（六个要求区块）；P5 派生单元格公式化与保存 TSLA_Financial_Summary.xlsx（输出要求：公式而非硬编码、保留 live 单元格）。

**候选检查点**：CP1（E1）=指定输入文件读取完成、工作簿未创建；局部决定=数据源分工与采集顺序。CP2（E3）=第一次网页数据采集成功返回；局部决定=字段映射与实时值口径。CP3（E4）=工作簿第一次保存事件返回；局部决定=派生单元格处理方式的自查（公式与硬编码之抉择是任务输出要求原文给定的自然决定点）。备用：第一次单元格区块写入返回。

**标准 6 检查**：不引用评分枚举的具体公式单元格或参考工作簿内容（评分细则在 task_card.evaluation，属评分层）。**风险**：live web 漂移（Q-I 同族）影响实时字段与分支等值性；GUI 工具（LibreOffice）操作的可快照性待实测；依赖 VM（Q-E）。
### 备位 B9：pe_screening_memo_1（题 3 备位，ALE-C）

**流程分解**（依据：ale_business_finance_pe_screening_memo_1.task_card.json）：P1 读取 task_brief.md、memo_template.md、source_manifest.json（taskPrompt 要求先读）；P2 精读材料包（Q2/Q3 财报发布与演示、10-K，各有 PDF 与 txt 双形态，inputFiles 列举）；P3 综合分析（财务、风险、尽调缺口）；P4 按模板结构写备忘录并给出明确的三选一投资建议（taskPrompt 输出要求）；P5 保存 screening_memo.md（明确禁网：Constraints 原文 "Use only the staged packet. Do not use web search."）。

**候选检查点**：CP1（E1）=三个指定说明文件读取完成、零写入；局部决定=材料精读顺序与证据提取策略。CP2（E2）=备忘录文件第一次写入返回；局部决定=章节组织与证据锚定方式。CP3（E4）=备忘录文件已写入且包含模板全部一级标题（结构化检查可行；模板是代理可见输入，不泄漏答案），最终修订未做；局部决定=三选一推荐结论及其证据支撑。备用：同一文件第二次写入事件返回。

**标准 6 检查**：触发不引用隐藏参考备忘录、通过阈值或推荐方向；CP3 的标题检查取自可见模板，合法。**风险**：单一产物任务检查点密度低，CP3 的内容结构检测实现待实测；依赖 Linux VM（Q-E）。

### 备位 B10：f5947c33（题 7 备位，HANDBOOK 类别 3）

**流程分解**（依据：instruction.md 全文；tests/rubrics.json；工作区材料 CareIG_SOP_v5.0.html、payer_rules.xlsx、两个病案 zip）：P1 读取 SOP、payer_rules 与两个病案材料包；P2 处理第一病案（Rodriguez）：按 SOP 的 intake 联系流程执行（instruction 第 1 段：提交 Prior Authorization 的既定流程）；P3 判断第二病案（Webb）流程位置（instruction 第 2 段原文 "figure out where it's at in the process based on the SOP, and deal with it accordingly"——流程定位属原生任务要求）；P4 按定位结果执行第二病案处理；P5 通信与记录收尾。

**候选检查点**：CP1（E1）=读取事件覆盖 SOP、payer_rules 与两个病案材料包，零写入；局部决定=双案处理策略与第二案的流程定位方法。CP2（E2）=第一次外部通信写入（slack 或邮件）返回；局部决定=通信内容与后续步骤。CP3（E4）=第一个病案的要求文件集合写入完成（集合按 SOP 流程定义）；局部决定=切换第二案前是否自查第一案。备用：第二病案文件夹上第一个写类事件返回（流程定位已产生第一个执行动作）。

**标准 6 检查**：触发不引用评分特有的消息格式串、审计行内容或药物名；CP3 的"病案文件集合"为 SOP 流程级定义，不取自评分项。**风险**：依赖 Docker（M-1）；双案双轨使触发顺序变异大，各条件独立冻结、独立记未触发；第二案"流程定位"是本备位最有稀释研究价值的局部决定，但它不改变触发设计（事件仍为文件/通信事件）。
## 第三部分：汇总

### 3.1 覆盖情况汇总

| 题 | 主检查点 | 备用 | 主要事件类 | 最大成立依赖 |
|---|---|---|---|---|
| 1 9b2f7a29 | 3（CP1 E1 / CP2 E2 / CP3 E4） | CP4 E5 | 读取覆盖、首写入、产物出现 | M-1/Q-E（Docker）；P5 推测 |
| 2 create-10k-income-report | 3（E3 / E4 / E5） | CP4 E3 | 目录枚举、首数据写入、产物出现 | M-1/Q-E；外部服务状态快照介质待实测 |
| 3 ALE financial_stmt | 3（E1 / E2 / E4） | CP4 E3 | 读取覆盖、首写入、产物出现 | Q-E（Linux VM）；M-8 secret 隔离 |
| 4 django-13495 | 3（E2 / E3 / E5） | CP4 E3 | 首代码写入、首测试运行、全绿窗口 | M-1；M-4 一票否决级 |
| 5 sklearn-11542 | 3（E2 / E3 / E5） | CP4 E2 | 同上 | M-1；M-4 一票否决级 |
| 6 3d-model-format-legacy | 3（E1 / E3 / E4） | CP4 E5 | 读取覆盖、首成功构建、首转换产物 | M-1 |
| 7 d9d532c1 | 3（E1 / E2 / E5） | CP4 E2 | 读取覆盖、首通信发送、通信集合齐备 | M-1 |
| 8 tau2-airline-44 | 3（E1 / 回合结构 / E2） | CP4 E5 | 查询覆盖、确认后写入前、首写类动作 | M-2 一票否决 |
| 9 AB Queen Anne | 3（E3 / E3 / E5） | CP4 E4 | 首抓取、记录集返回、提交前末回合 | M-3 一票否决级 |
| B1 retail-55 | 3（E1 / E2 / E2） | 确认回合后写入前 | 查询覆盖、首取消、首退货 | M-2 一票否决 |
| B2 airline-18 | 3（E1 / E2 / E5） | 首费用计算返回 | 读取覆盖、首降舱、写入完毕未告知 | M-2 一票否决 |
| B3 sympy-15198 | 3（E2 / E3 / E5） | 首失败测试返回 | 首代码写入、首测试、全绿窗口 | M-1；M-4；base_commit 历史可得性 |
| B4 xarray-4827 | 3（E2 / E3 / E5） | 第二写类事件 | 同上 | M-1；M-4 |
| B5 db-wal-recovery | 3（E3 / E3 / E4） | WAL 字节级分析返回 | 首访问、修复后首读取、产物出现 | M-1；检查点密度待实测 |
| B6 revenue-reconciliation | 3（E3 / E4 / E2） | 首中间记录写入 | 首下载、首标记产物、首联系发送 | M-1；服务状态快照介质；路径不一致待核 |
| B7 employee-info-reconciliation | 3（E3 / E2 / E2） | 首接收消息事件 | 首名单查询、首 DM、首 CSV 写入 | M-1；mock 回复保真待实测 |
| B8 equity_research_summary | 3（E1 / E3 / E4） | 首区块写入 | 读取覆盖、首网页采集、首保存 | Q-E；live web 漂移；GUI 可快照性 |
| B9 pe_screening_memo_1 | 3（E1 / E2 / E4） | 第二写入事件 | 读取覆盖、首写入、结构齐备 | Q-E；CP3 标题结构检测待实测 |
| B10 f5947c33 | 3（E1 / E2 / E4） | 第二案首写类事件 | 读取覆盖、首通信、首案集合完成 | M-1 |

合计：19 题全部完成标注；每题 3 个主检查点加 1 个备用，共 76 个检查点定义，全部以可观察事件为触发、均给出局部决定内容与 manifest 字段映射。事件类覆盖：E1/E2/E3/E4/E5 五类事件在 19 题中均有实例，另有两个回合结构型触发（题 8 CP2 与 B1 备用，依赖用户模拟器回合事件可观察性），无单一事件类依赖；每题 3 主加 1 备的结构满足 design §4.1 的 3 主 2 备上限与每根运行 3 个有效 checkpoint 的目标。
### 3.2 标准 6 风险点与替换记录

标注过程中识别出三类"围绕已知错误位置设计"的候选检查点模式，全部排除，替换记录如下。这三类模式的共同特征是触发条件引用了只存在于期望答案、断言或评分项中的实体，等于把"模型在这里犯过错"的先验编进了分叉位置。

**模式一："处理特定实体后"型**
- 候选形态：τ2 系以"处理完预订 S61CZX 后"（该预订在题 44 的 evaluation_criteria/nl_assertions 中是被断言对象）；TAC-B7 以"与 checkpoints.md 点名员工对话后"；HANDBOOK 系以"处理完某个被例外评分项点名的待处理项后"。
- 排除理由：实体之所以被想到当分叉点，是因为评分表标出了它，这正是标准 6 禁止的先验。
- 替换：类型/计数事件——"全部预订详情查询返回且写类动作计数为零"（题 8 CP1）、"第一次写类动作返回"（题 8 CP3）、"第一次 DM 发送返回"（B7 CP2）、"第一个写类工具调用返回"（题 1 CP2）。

**模式二："参考补丁/参考动作清单进触发"型**
- 候选形态：SWE 系以"参考补丁触及的第 N 个文件被修改后"（第二轮记录的 6/7 文件清单来自参考补丁）；τ2 系以"第 3 次 update_reservation_flights 后"（3 这个数来自参考动作序列）。
- 排除理由：参考补丁文件清单与参考动作计数属期望答案成分，引用即违反标准 6；且会因代理走不同路径而系统性不触发。
- 替换：中性写/测事件——"第一个源代码写入返回"（题 4/5 CP1）、"第一次测试运行返回"（题 4/5 CP2）、顺序型"第二个写类事件返回"（题 5 备用、B4 备用）。

**模式三："评分项数值/词表进触发"型**
- 候选形态：HANDBOOK 系以"处理完 $7,800 项后"或"写出 FIN-100 Cleared & Posted 状态词后"（金额、项编号与状态词均出自 rubrics 清账条目）；TB-B5 以"恢复出 11 条记录后"（该数为 instruction 目标值，但"已恢复 11 条"作为触发等于把成功判定前置）；AB 题 9 以"抓到 gold_url 后"。
- 排除理由：数值/词表/URL 只在评分层或答案层出现；作为触发会让检查点只在"走对路"的轨迹上成立，条件间不可比。
- 替换：存在/类型事件——"第一次外部通信写入返回"（题 7 CP2）、"第一次对 WAL 修复写入之后的数据库成功读取事件返回"（B5 CP2）、"第一次成功的网页抓取返回"（题 9 CP1，不预设正确信息源）。

**保留判断**：题 4 CP1 的局部决定"公共 as_sql 路径统一处理还是逐后端分改"与题 5 CP1 的"直接改默认值还是弃用周期"均来自 issue 原文给定的两条路径，属题面原生决策空间，不是从失败知识反推，保留。题 8 CP2 依赖"用户已确认"回合事件，确认要求来自政策原文（写类动作前须获用户确认），同样属题面结构，保留。
### 3.3 依赖实测的检查点清单

按实测项分族（编号沿用 candidate-config-draft-v0.md 的实测项编号）：

**M-1/Q-E 执行环境族（一票否决级，全部检查点挂起）**：题 1、2、4、5、6、7 与备位 B3、B4、B5、B6、B7、B10 依赖 Docker；题 3、B8、B9 依赖 Linux VM。环境可用前，这些题的触发条件只能做纸面校验。

**M-2 τ2 用户模拟器分叉重放族（一票否决级）**：题 8 与备位 B1、B2 的全部检查点。个别检测细节另挂实测：题 8 CP2 要求"用户确认回合"作为事件可观察（若运行器不把模拟器回合暴露为事件流，该条件按未触发处理、由备用接管）；三分支中模拟器行为一致性（同版本同种子重放保真）须在首个根运行后核对。

**M-3 live web 漂移族（一票否决级）**：题 9 全部检查点——分叉后各分支面对同一外部世界而非同一快照，需要运行器层页面缓存/回放策略，否则按草案 2.3 撤换。B8 的实时市场数据字段同族（但 B8 评分只查非空与格式，漂移对评分影响小于题 9）。

**M-4 SWE 即时反馈与排除条款族**：题 4、5 与备位 B3、B4。若实测确认"测试随时可跑、失败即时可见"使中途冻结失去意义（design 排除条款，source-selection.md §3.6），该族整体撤换；题 4/5 的 CP3"全绿后无代码写入"检测窗口定义也须在首个根运行上校准（改-测振荡轨迹下窗口判定的误判率）。

**M-8 ALE secret/ 隔离**：题 3 的快照须保证隐藏参考文件不进代理可见状态、也不进分叉副本；隔离机制核验前该题快照字段设计冻结。

**个别检测实现待实测（非一票否决，可单独校准）**：
- 题 2/B6/B7：TheAgentCompany 自托管服务（Owncloud、RocketChat）的状态承载物与可哈希性，决定 external_state_sha256 的介质。
- B7：快照恢复后 mock 员工 DM 回复的保真度（execution-prep §2.2 风险点 c）；不保真则 CP3 之后的分支不可比。
- B5：任务体量小（expert 45 分钟），单根运行内三个检查点时序紧凑，有效触发数可能不足 3，启用前实测一次触发分布。
- B9：CP3 的"模板全部一级标题齐备"结构化检测实现（标题匹配规则）待实测。
- B3：题面指向外部 commit（issue 引 e99b756），base_commit 仓库历史可得性属材料准备实测项。
- B6：task.md 与 checkpoints.md 的路径不一致（Documents/Human Resources Team/Contracts 对 Documents/Financials/Contracts），启用前核实何者有效；不影响触发定义但影响阶段描述。
- 题 1：P5 交付形式为推测；CP4 冻结时建议简化为仅查"要求产物集合齐备"。
- 全部暂停注入类条件（sham/reconsider 的 ≤256 tokens 无工具短回合）依赖运行器支持注入与回合截断（execution-prep §2.5 相关实测项）。

### 3.4 声明与附录

**声明**：本文档是标注草案，不是冻结的触发清单；正式冻结时须按 execution-prep.md §3.1 的字段格式逐行生成，并产出 checkpoint_trigger_version 与 checkpoint_trigger_sha256。本次标注未运行任何基准任务、未启动任何代理；HANDBOOK 仓库仅只读访问。全部 19 题中仅一处无材料依据的流程推断：题 1 P5 的交付形式（已标"推测"）。

**主要证据文件**：
- 设计依据：docs/subtask-dilution/design.md（§4.1/§4.2/§5/§6）、execution-prep.md（§3.1/§3.2/§3.3）、candidate-config-draft-v0.md（9 题与备位表、实测项）、source-selection.md（§3.6 排除条款）。
- 题面与评分结构：.materials-cache/round4/ 的 tau2_airline_tasks.json、tau2_retail_tasks.json、tau2_*_policy.md、tb_3d-model-format-legacy.yaml、tb_db-wal-recovery.yaml、tac_*.task.md 与 checkpoints.md、ale_*.task_card.json、assistantbench_validation.parquet（round3）、swe_bench/test.parquet；candidate-search-round2.md（T1/T3/T4/T7 条目）。
- HANDBOOK（只读）：tasks/insurance_vanguard_shield_mutual_9b2f7a29/、tasks/finance_sunshine_set_d9d532c1/、tasks/medical_careig_specialty_pharmacy_f5947c33/ 各任务的 instruction.md、tests/rubrics.json、environment 下的 SOP 文件。