# 子任务稀释：9 题评分器对接规格草案

日期：2026-08-26（任务 19，评分器对接规格）

本文档接续 candidate-config-draft-v0.md（9 题主方案与备位），为每一题写清原生评价器怎么对接：硬分从哪来、怎么记、哪些部分必须人工盲审。评价方法依据 design.md 第 8 节（硬指标继承原生 evaluator，不临时发明"客观答案"；软评审人工盲审、2+1 制、五选项；硬软分开保存分开报告）；记录格式依据 experiment-records.md 第 5、6、7 节。

**红线声明**：本任务未运行任何评分器、测试或基准任务；全部结论来自评分器源码、配置文件与文档原文；无原文依据的内容一律标注"推测"；未修改任何既有文档；HANDBOOK 仓库只读。

---

## 0. 证据材料清单

评分器源码与配置（全部位于 .materials-cache/round4/，gitignore 覆盖，不入库）：

| 来源 | 仓库身份（fetch_batch.py 记录） | 本轮使用的评分器证据文件 |
| --- | --- | --- |
| τ2-bench | sierra-research/tau2-bench | tau2_eval_evaluator_env.py、tau2_eval_evaluator.py、tau2_eval_evaluator_communicate.py、tau2_eval_evaluator_nl_assertions.py、tau2_config.py、airline tasks.json（题 44 定义） |
| TheAgentCompany | TheAgentCompany/TheAgentCompany | tac_finance-create-10k-income-report.evaluator.py、tac_base_eval.py、tac_base_scoring.py、tac_base_common.py；备位：tac_finance-revenue-reconciliation.evaluator.py、tac_admin-employee-info-reconciliation.evaluator.py、tac_pm-schedule-meeting-1.evaluator.py |
| Agents' Last Exam | rdi-berkeley/agents-last-exam | ale_finstmt_score_outputs.py、ale_business_finance_financial_stmt_reconstruction_aapl_fy2024.task_card.json；备位：ale_equity_score_workbook.py、ale_pememo_score.py |
| Terminal-Bench | laude-institute/terminal-bench | tb_3d-model-format-legacy.yaml、tb_3d_test_outputs.py、tb_3d_test_cmake.py、tb_3d_run_tests.sh；备位：tb_db-wal-recovery.yaml、tb_wal_test_outputs.py |
| SWE-bench | （HuggingFace parquet） | .materials-cache/swe_bench/test.parquet（2294 行，含 FAIL_TO_PASS/PASS_TO_PASS/base_commit/test_patch/environment_setup_commit） |
| AssistantBench | （Allen AI parquet） | .materials-cache/round3/assistantbench_validation.parquet（33 题，含 answer/gold_url/explanation） |
| HANDBOOK | 本地仓库 d:\File\Git\handbook（只读） | tasks/insurance_vanguard_shield_mutual_9b2f7a29/tests/（test.sh、sop_verifier.py、rubrics.json、task.toml）；tasks/finance_sunshine_set_d9d532c1/tests/（同构）；README.md（Harbor 运行方式） |

SWE-bench 官方 harness 的 resolved 判定代码与 AssistantBench 官方评分代码均未缓存，相关结论已标注。

## 1. 统一对接约定（适用全部 9 题）

1. **硬分来源**（design.md 8.1）：只继承原生 evaluator；原生覆盖不到的局部不发明"客观答案"，只能进软评审或发现通道。同时保留局部硬结果与最终任务结果。
2. **软评审**（design.md 8.2）：全部 9 题的分支组比较都进人工盲审（2 位独立、分歧时第 3 位、五选项）；评审材料含完整背景、checkpoint 前上下文、分支后动作依据与最终产物，不展示 direct/sham/reconsider 标签、不展示暂停提示与暂停回答。第一主比较只做 reconsider 对 sham。
3. **评分记录**（experiment-records.md 第 5 节）：每次评分生成独立 JSON，含 score_record_id、run_attempt_id、root_run_id/branch_group_id/branch_type、checkpoint 状态清单 SHA-256、scorer_id/scorer_version/scorer_sha256、scored_at、score_status（complete/partial/unscorable）、原始评分器输出、各评分项的数值/分母/是否缺失、支撑产物位置、opportunity_reached、替代关系。硬分与盲评分别保存；未到达、评分器故障、答错分别保存，不得都记 0。
4. **评分器版本冻结**（experiment-records.md 6.2/6.3）：所有评分器与评分规则保存 SHA-256；含 LLM 判分的题目，judge 模型与端点一并写入评分器版本说明（见第 13 节缺口 G-3）。
5. **重新评分**（experiment-records.md 第 7 节规则 6）：评分器修复优先对原产物重新评分，生成新 score_record_id，不重新运行模型。

---

## 2. 题 1：HANDBOOK insurance_vanguard_shield_mutual_9b2f7a29（类别 1）

### 2.1 原生评价器机制
评分入口为任务目录 tests/（test.sh 调用 sop_verifier.py，Harbor 容器内执行）。机制原文依据 d:\File\Git\handbook\tasks\insurance_vanguard_shield_mutual_9b2f7a29\tests\sop_verifier.py：
- rubrics.json 中每条 rubric 内嵌确定性 Python 验证代码，由解释器逐条执行，调用约定为 `verify(workspace_path, external_services_path)`；
- 被检状态两类：/workdir 下的产物（本题为 Suspense_Reconciliation_March2026.xlsx，检查列结构、OPS-2/3/7/8 对应 FIN-100、OPS-4~12 标 EXCEPTION、GL 冲突双代码、Slack 批准引用等）与外部服务终态（/data/<service>/final.json，候选路径按序回退：final.json → 种子文件名 → /initial_data；对 slack/google_mail/google_calendar/jira/shopify 做兼容文件名复制，如 inbox.json→mailbox.json）；
- 总评 = 各条 rubric score 的平均值（`average_score = round(sum(...)/total, ...)`），写入 /logs/verifier/reward.txt，同时输出 results.json（passed、rubrics_passed、rubrics_total、score、逐条 rubric_results）。
本题 12 条 rubric 全部为确定性 Python 断言（无 LLM），类型均为 expected_output。

### 2.2 硬分输入输出与确定性
- 输入：容器终态的 /workdir 产物目录 + /data 各服务 final.json（可整体导出为静态快照）。
- 输出：0~1 平均分（逐条 0/1 后取均值）+ results.json 逐条明细。
- 确定性程度：**完全确定性**（纯 Python 断言，无 LLM、无外部网络依赖）。

### 2.3 接入方式
- 我们的运行框架需要交出的产物：分支结束时的 /workdir 全量 + /data/<service>/final.json 全量（按冻结的 checkpoint 状态清单导出并记 SHA-256）。
- 评分可在容器内直接跑原生 tests/，也可把快照导出后本地跑 sop_verifier.py——但该脚本硬编码容器路径（/workdir、/data、/tests、/logs/verifier），本地化需在隔离的等价目录结构中重放，或统一保留在容器内评分（**推测**：容器内评分更省事，工程细节待实测）。
- 评分需要环境存活：是（Docker/Harbor 容器，对齐草案 M-1）；但若已在存活容器内完成评分，则重评分只需快照。
- 防泄题：tests/ 与 rubrics.json 在代理运行阶段不得进入工作区可见范围（experiment-records.md 6.1：条件对应表、评分器、测试、预期答案留在私有位置）。

### 2.4 软评审覆盖与匿名化要点
硬分测不到、必须进人工盲审的维度：异常条目的裁决理由是否合理（Conflict/Resolution Notes 列的文字质量与依据链）、Support Location 引用的检索路径是否经济、整体对 SOP 的解释是否合理。盲审材料为分支后最终 xlsx + 分支后动作记录；匿名化要点：去除 HANDBOOK/Harbor 来源标识与任务目录名（含 9b2f7a29 哈希段）、去分支标签与暂停提示、匿名文件名不含任何条件语义（experiment-records.md 6.1）。

### 2.5 记录对接
- 整体硬评分 ← reward.txt 数值；局部硬评分 ← results.json 逐条 rubric_results（逐项数值/分母/是否缺失的天然载体）。
- 原始评分器输出 ← results.json 全文；评分器与规则 ← tests/ 目录整体冻结并记 SHA-256（scorer_sha256）。
- score_status：12 条 rubric 全跑成 complete；任一验证代码异常无法出分记 partial 并注明。

### 2.6 风险
- rubrics.json 若上游更新会改变评分语义——冻结时按本地仓库 commit + 文件 SHA-256 锁版本（experiment-records.md 6.3）。
- 兼容文件名复制机制（SERVICE_COMPAT_FILES）意味着 rubric 读的状态文件名有别名，快照导出必须连同 /data 目录结构一起导出，不能只导单文件。
- 逐条 rubric 默认 0/1，局部"做对一半"在单条内不产生部分分；稀释线的局部粒度依赖多条 rubric 的组合，不能假设单条内有连续分。

## 3. 题 2：TAC finance-create-10k-income-report（类别 1）

### 3.1 原生评价器机制
依据 tac_finance-create-10k-income-report.evaluator.py（round4 缓存）与基础设施文件：
- 评分器在容器内以加密形式存在：/utils/evaluator.py.enc 运行时用环境变量 DECRYPTION_KEY 解密执行（tac_base_eval.py 原文）——代理不可见评分器，天然反污染；
- 五个 checkpoint（tac_base_scoring.py 的 `Checkpoint(total, result)`，默认策略为简单求和，本题未启用 bonus_for_completing_final）：
  - CP1（1 分）：owncloud 参考文件路径字符串出现在轨迹中（轨迹子串检查）；
  - CP2（1 分）：输出文件存在；
  - CP3（1 分）：读输出 CSV 检查结构——**已知缺陷**：该评分器第 58 行 `reference_df = df = pd.read_csv(file_path, ...)` 把参考与被测读成同一份文件，公司名比对因此空转，实际只检查必备列是否存在（见第 15 节差异记录 3）；
  - CP4（2 分）：输出行集合与容器内 /utils/reference_net_income.csv 精确比对；
  - CP5（1 分）：`evaluate_chat_history_with_llm(rocket, "David Wong", predicate)`——对 RocketChat 实际聊天记录做 LLM 判分（tac_base_common.py：llm_complete 走 litellm，模型/端点/密钥来自 LITELLM_MODEL/BASE_URL/API_KEY 环境变量）；
- @grader 装饰器在异常时吞掉异常返回，异常项等同未得分。

### 3.2 硬分输入输出与确定性
- 输入：完整轨迹文本（CP1）、容器内输出文件（CP2~CP4）、容器内参考文件 /utils/reference_net_income.csv、**评分时刻仍存活的 RocketChat 服务状态**（CP5）。
- 输出：各 checkpoint 加权求和（权重合计 6 分，CP4 占 2 分），部分分天然存在。
- 确定性程度：**含 LLM 判分**（CP5）；CP1~CP4 确定性。

### 3.3 接入方式
- 框架需交出：轨迹文件（冻结记 SHA-256，它是 CP1 的硬分输入）、容器输出文件；评分须在容器环境存活时执行（文件 + RocketChat 均为容器内活状态，对齐 M-1）。
- LITELLM_MODEL/BASE_URL/API_KEY 必须在冻结时固定并写入评分器版本说明，否则 CP5 不可复现。
- 分支评分注意：CP1 检查的是"整个轨迹"，分叉后三支轨迹不同，CP1 结果可能分叉——这是原生语义，按原样记录。

### 3.4 软评审覆盖与匿名化要点
硬分测不到：数据不一致的原因分析质量（为什么差、以哪边为准的理由）、与 David Wong 沟通的实际质量（CP5 只判"是否说过"，不判说得好不好）、10-K 取数的口径选择合理性。盲审材料含输出报表 + 分支后沟通记录；匿名化：去 TAC 容器路径（/utils、/workspace）、去人名之外无需脱敏（人名是任务原生内容）、去分支标签与暂停提示。

### 3.5 记录对接
- 局部硬评分 ← 逐 checkpoint 的 total/result（天然的"各评分项数值/分母/缺失"）；整体硬评分 ← 求和值。
- CP5 的 judge 模型与端点写入评分器版本字段；轨迹文件 SHA-256 作为 CP1 的支撑产物位置。
- @grader 吞异常 → 某项异常时按"评分器故障与答错分开保存"处理：该项记缺失而非 0，必要时整次评分记 partial。

### 3.6 风险
- CP5 的 LLM 判分不稳定：模型、温度、聊天记录导出时序都会影响结果，需冻结并预留重评分通道。
- CP3 自比缺陷（见 15.3）：不会误扣分，但公司名维度实际不校验——按原样保留（不修原生评分器），在记录中如实注明。
- RocketChat 活状态只在评分时刻存在一次：必须在评分前导出聊天记录副本，否则无法重评分。


---

## 4. 题 3：ALE financial_stmt_reconstruction_aapl_fy2024（类别 1）

### 4.1 原生评价器机制
依据 ale_finstmt_score_outputs.py（round4 缓存，源自仓库任务目录 scripts/score_outputs.py）：
- 评分器为独立命令行脚本，入参 `--output`（代理产出目录）与 `--reference`（参考 JSON 目录）；
- 机制：对两棵 JSON 树的叶子节点做 Decimal 精确数值比对；顶层合计项（totals）单独校验；
- 输出：`score`（字段级准确率）、`pass_fail = (无错误) and (顶层合计正确) and (accuracy >= 0.95)`、逐字段 details、missing_paths、extra_paths。
参考文件（如 aapl_fy2024_balance_sheet_reference.json）**不在仓库树中**：该任务目录树内只有 main.py、scripts/score_outputs.py、task_card.json，参考材料运行时经 ale_run/executors/_secrets.py 注入（对齐草案实测项 M-8：仓库含 secret/ 目录 4 条目）。

### 4.2 硬分输入输出与确定性
- 输入：代理产出的报表 JSON 文件 + 参考 JSON（一次性获取后冻结）。
- 输出：字段准确率（连续值）+ pass/fail + 逐字段差异明细。
- 确定性程度：**完全确定性**（Decimal 精确比对，无 LLM、无网络）。

### 4.3 接入方式
- 框架需交出：代理工作区中的报表 JSON（分支终态产物，记 SHA-256）。
- 参考文件获取：部署阶段经 secret 机制一次性取得参考 JSON，立即冻结并记 SHA-256，存入私有位置（不得进入代理工作区——对齐 M-8 与 experiment-records.md 6.1）；取得后评分为纯本地文件比对，**不需要环境存活**。
- 这是 9 题中唯一"评分器依赖一次性秘密材料注入"的题，获取路径的合规性与隔离性是冻结前置条件。

### 4.4 软评审覆盖与匿名化要点
硬分测不到：重构口径的选择依据（某科目金额从哪份披露材料推出）、无法精确重构时的估计方法与说明质量、报表结构组织。盲审材料含最终报表 + 重构依据记录；匿名化：去掉 AAPL/FY2024 之外的来源标识（题目内容本身含公司名，属任务原生语义，保留），匿名文件名不含条件语义。

### 4.5 记录对接
- 整体硬评分 ← `score` 与 `pass_fail`（两者分开保存：通过率与门槛判定语义不同）；
- 局部硬评分 ← 逐字段 details（数值/分母/缺失的天然载体，missing_paths 记缺失、extra_paths 记越界产物）；
- 参考文件 SHA-256 写入支撑产物位置字段；评分器即 score_outputs.py 冻结版本。

### 4.6 风险
- 参考文件泄漏风险是本题首要风险（M-8）：泄漏等于硬分失效且污染实验语义，须做泄漏扫描（experiment-records.md 6.2）。
- Decimal 精确比对对"合理舍入差异"零容忍——0.95 阈值是唯一缓冲；若分支在舍入口径上分叉，硬分差异可能放大非实质差异，盲审须覆盖此点。
- secret 注入机制若上游变更，参考文件获取路径需重新核验。

## 5. 题 4：SWE-bench django__django-13495（类别 2）

### 5.1 原生评价器机制
SWE-bench 原生机制为 FAIL_TO_PASS/PASS_TO_PASS 测试判定（test.parquet 原文）：
- 本题：FAIL_TO_PASS 5 条（DateFunctionTests 的时区相关 trunc/extract 测试）；PASS_TO_PASS 原始列表长度 **7218 条**（parquet 原始字段；注意与 round2 文档所记 "74" 存在口径差异，见 15.1）；
- 评分流程（原生定义）：在 base_commit（b26ec77deb7c）仓库状态上应用 test_patch，随后对被测补丁后的代码运行测试；判定标准 = 全部 FAIL_TO_PASS 通过且 PASS_TO_PASS 保持通过（resolved）。harness 的 resolved 判定代码未缓存，此判定标准按 SWE-bench 通行官方定义陈述，精确实现待取回核实（见缺口 G-1 与实测项 S-1）；
- environment_setup_commit：65dfb06a。

### 5.2 硬分输入输出与确定性
- 输入：代理产出的代码补丁（或补丁后的仓库工作树）+ 原生 test_patch + 完整测试环境。
- 输出：resolved 二元 + 逐测试通过/失败明细（必须逐条保留，见 5.5）。
- 确定性程度：**确定性**（pytest 断言，无 LLM），但依赖外部环境（测试环境可构建且稳定）。

### 5.3 接入方式
- 框架需交出：分支终态的代码补丁（或 diff，记 SHA-256）。
- 评分 = 在可运行环境内执行测试：需要 Docker/容器化的测试环境（草案 M-1 外围——M-1 的 6 题清单未列 SWE，但评分必须能跑测试，本规格将其单列为环境依赖，对齐任务要求"标注依赖 Docker 实测 M-1"）。
- 7218 条 P2P 全量运行耗时长，是否在冻结时规定全量运行或按原生列表运行，是冻结决策项（推测：官方口径为全量）。

### 5.4 软评审覆盖与匿名化要点
硬分测不到：修复方案的合理性与最小性（是否引入不必要的行为变更）、回归风险评估、补丁可读性。盲审材料含补丁 + 分支后推理记录；匿名化：去仓库名/issue 号（django__django-13495 可直接反查原 issue 与参考补丁，必须去除）、去分支标签与暂停提示。

### 5.5 记录对接
- 整体硬评分 ← resolved（0/1）；
- 局部硬评分 ← FAIL_TO_PASS 逐条结果（天然局部项）+ PASS_TO_PASS 回归计数（通过数/总数为分母）——仅存 resolved 单值无法满足"各评分项数值/分母/缺失"，必须保存逐测试输出（见缺口 G-1）；
- score_status：P2P 未跑全记 partial；环境构建失败记 unscorable 或按 invalid_technical 处理（与"答错"分开）。

### 5.6 风险
- harness resolved 精确定义未缓存，口径须实测确认（S-1）。
- P2P 体量大（7218 条）：运行时长与环境稳定性是主要工程风险；个别 flaky 测试可能造成假回归（推测：官方列表已在发布时筛过，但本地环境差异仍可能引入抖动）。
- base_commit 时代久远，环境构建依赖 environment_setup_commit 的镜像可复现性。


---

## 6. 题 5：SWE-bench scikit-learn__scikit-learn-11542（类别 2）

### 6.1 原生评价器机制
与题 4 同为 FAIL_TO_PASS/PASS_TO_PASS 机制（test.parquet 原文）：
- 本题：FAIL_TO_PASS 5 条（test_nestimators_future_warning 的参数化测试，考察 RandomForest 默认 n_estimators 变更的弃用告警行为）；PASS_TO_PASS 原始列表长度 **18552 条**（与 round2 文档所记 "222" 存在口径差异，见 15.1）；
- base_commit：cd7d9d985e1b；environment_setup_commit：55bf5d93。

### 6.2 硬分输入输出与确定性
- 与题 4 相同：输入为补丁 + test_patch + 环境；输出为 resolved 二元 + 逐测试明细；确定性（无 LLM），依赖外部环境。

### 6.3 接入方式
- 与题 4 相同：交补丁、容器内跑测试、依赖 Docker 实测（M-1 外围）。
- 特别点：18552 条 P2P 是 9 题中评分运行量最大的一题，运行时长与机器资源是冻结时必须评估的工程项（推测：单分支单次评分可能达小时级）。
- 本题 F2P 为"告警行为"测试：决定点是默认值直接改还是走弃用周期（草案 1.6 节），局部决定与测试反馈的对应关系清晰，适合稀释线。

### 6.4 软评审覆盖与匿名化要点
硬分测不到：弃用策略选择的论证质量（为什么选此路径）、示例与文档同步改动的取舍、向后兼容考虑。匿名化同题 4：去仓库名/issue 号（可反查原 issue），去分支标签与暂停提示。

### 6.5 记录对接
- 同题 4：整体 ← resolved；局部 ← F2P 逐条 + P2P 回归计数（通过数/18552 为分母）；P2P 未跑全记 partial。

### 6.6 风险
- 同题 4 的三项风险，外加：P2P 体量更大，环境与资源风险更高；告警类测试对 pytest 警告过滤配置敏感（**推测**：test_patch 已固定配置，但环境 pytest 版本须与 environment_setup_commit 对齐）。

## 7. 题 6：Terminal-Bench 3d-model-format-legacy（类别 2）

### 7.1 原生评价器机制
依据 tb_3d-model-format-legacy.yaml 与缓存的测试文件（源自 laude-institute/terminal-bench 仓库）：
- task.yaml 声明 `parser_name: pytest`、`run_tests_in_same_shell: false`；
- run-tests.sh 创建独立虚拟环境 `.tbench-testing`（固定依赖，含 pytest==8.4.1），依次运行 test_cmake.py 与 test_outputs.py；
- 断言全部确定性：转换产物的 JSON 结构、顶点数（706/1148/1445）、质心坐标（容差 1e-4）等；
- 隐藏机制：测试在写入 /temp 时"purposefully hidden from the agent as an additional hidden test"（测试源码注释原文）——测试文件与中间检查对代理不可见。

### 7.2 硬分输入输出与确定性
- 输入：容器内代理工作区终态（转换后的模型文件与构建产物）。
- 输出：pytest 通过率（逐测试用例），无 LLM。
- 确定性程度：**完全确定性**（固定版本依赖的 pytest 断言）。

### 7.3 接入方式
- 框架需交出：分支终态的容器工作区快照。
- 评分需在容器内注入并执行原生测试（评分阶段才注入测试文件，运行阶段保持隐藏），需要 Docker 环境存活（对齐 M-1）。
- 分叉评分注意：/temp 隐藏机制意味着测试自身会写中间文件；从 checkpoint 快照分叉后评分时，需保证 /temp 的状态一致或允许测试重建（**推测**：原生流程每次评分重建，细节待实测）。

### 7.4 软评审覆盖与匿名化要点
硬分测不到：格式转换方案的技术路线合理性（legacy 格式的处理策略）、构建系统改动（CMake）的质量、代码组织。盲审材料含最终产物 + 关键命令/代码记录；匿名化：去 terminal-bench 任务名（3d-model-format-legacy 可反查原题）、去分支标签与暂停提示。

### 7.5 记录对接
- 整体硬评分 ← pytest 总通过率；局部硬评分 ← 逐测试用例通过/失败（test_cmake 组与 test_outputs 组分开，天然对应"构建成功"与"产物正确"两个局部）；
- 原始评分器输出 ← pytest 完整输出；评分器版本 ← run-tests.sh + 测试文件 + 依赖清单整体冻结记 SHA-256。

### 7.6 风险
- 隐藏测试泄漏 = 实验失效：注入时机与泄漏扫描是硬要求（experiment-records.md 6.2：校验值不证明无泄题，泄漏扫描须单独记录）。
- 独立 venv 的依赖安装需要网络或预缓存，冻结时固定依赖版本快照。
- expert 240 分钟 / junior 700 分钟的时长估计意味着运行预算大，评分前的运行成本是批次规划项（与评分器本身无关，如实注明）。


---

## 8. 题 7：HANDBOOK finance_sunshine_set_d9d532c1（类别 3）

### 8.1 原生评价器机制
与题 1 同一评分框架（tests/test.sh → sop_verifier.py → rubrics.json 逐条内嵌验证代码 → 平均分写 reward.txt + results.json）。本题差异点（依据 rubrics.json 原文）：
- 6 条 rubric，全部确定性（无 LLM）；
- 被检状态：外部服务终态 mailbox.json（4/1~4/15 佣金邮件：含 6 笔当期交易 4502~4509 与 Deal 4501 的前期调整行；发给 megan.price 的 chargeback 邮件须含 $1,400/$1,050/$350 金额）与 slack_data.json（#acct-payroll-commissions 频道通报 4505/4507 问题）；
- 含 2 条 `incorrect_behavior` 反向 rubric：不得升级 4504、不得把 4505/4507 列为正常佣金行——即"做了禁止动作则该项失败"的负向检查。

### 8.2 硬分输入输出与确定性
- 输入：/data 下 google_mail、slack 服务终态 + /workdir 产物。
- 输出：0~1 平均分 + 逐条明细；反向项与正向项同一机制计分。
- 确定性程度：**完全确定性**。

### 8.3 接入方式
- 同题 1：交 /workdir + /data/<service>/final.json 快照；容器内评分（Docker，对齐 M-1）。
- 本题工作主体是"对外发送沟通"（邮件/Slack 消息），评分读的是服务终态——分叉评分时服务状态快照是必需的硬分输入，且快照必须覆盖发送动作发生后的终态。

### 8.4 软评审覆盖与匿名化要点
硬分测不到：沟通措辞与职业质量（邮件/通报写得是否清楚）、加急情景（系统停机前 expedite）下的优先级安排、对 4505/4507 异常的处理判断表述。盲审材料含发送内容全文 + 处理记录；匿名化：去任务目录名哈希段与 HANDBOOK 标识、去分支标签与暂停提示；公司名/人名属任务原生内容保留。

### 8.5 记录对接
- 同题 1：整体 ← reward.txt；局部 ← results.json 逐条（6 条，其中 2 条反向项须在记录中注明方向，避免误读为"遗漏"）。
- M-10：类别 3 正式两题由抽样程序产生，本题主位/ f5947c33 备位只是结构安排——冻结时按抽样结果执行，本规格对两题同构适用。

### 8.6 风险
- 确定性断言对字符串格式敏感（金额写法、邮件主题格式）：代理输出"语义对但格式偏"会丢分——这是原生语义，如实记录，盲审可作对照说明但不能改硬分。
- 反向 rubric 的判定依赖对状态中存在/不存在特定内容的检查，快照不完整会造成假结果——快照完整性校验是前置要求。

## 9. 题 8：τ2-bench tau2-airline-44（类别 3）

### 9.1 原生评价器机制
依据 round4 缓存的 τ2 评分器源码（源自 sierra-research/tau2-bench 仓库）：
- **EnvironmentEvaluator**（tau2_eval_evaluator_env.py）：把完整轨迹经 `predicted_environment.set_state(message_history=...)` 重放进预测环境，同时在 gold 环境执行 `task.evaluation_criteria.actions` 参考动作序列，然后比对两侧数据库哈希：agent 库与 user 库哈希都一致 → `db_reward = 1.0`，否则 `0.0`（**二元**）；轨迹终止原因非 AGENT_STOP/USER_STOP（如超时/崩溃）直接整体 0；
- **CommunicateEvaluator**（tau2_eval_evaluator_communicate.py）：对 communicate_info 逐条做子串匹配——本题 44 的 communicate_info 为空列表，该组件空转返回 1.0；
- **NLAssertionsEvaluator**（tau2_eval_evaluator_nl_assertions.py）：LLM judge（DEFAULT_LLM_NL_ASSERTIONS = gpt-4.1-2025-04-14，tau2_config.py；temperature 0），逐断言判定、全过才 1.0——本题 44 的 reward_basis = ["DB","COMMUNICATE"]（tasks.json 原文），5 条 nl_assertions **不在** reward_basis 内，默认模式下不计入硬分；
- **总分**（tau2_eval_evaluator.py）：reward = reward_basis 内各组件分数的**乘积** → 本题实际硬分 = DB 哈希二元匹配。

### 9.2 硬分输入输出与确定性
- 输入：完整对话轨迹（message history，可序列化为 JSON）。
- 输出：reward ∈ {0,1} + 各组件 reward_breakdown。
- 确定性程度：**默认模式确定性**（纯 Python 轨迹重放 + 哈希比对，无 LLM、无网络）；仅当启用 ALL_WITH_NL_ASSERTIONS 调试模式时含 LLM judge——是否启用须在冻结时决定。

### 9.3 接入方式
- 框架需交出：分支的完整轨迹 JSON（记 SHA-256）。评分不需要 Docker，只需要冻结版本的 τ2 环境代码（纯 Python）——这是 9 题中唯一"评分靠重放而非读终态"的形态。
- 与分叉设计的天然契合：稀释线的分支本来就是轨迹级分叉，重放评分对三支一视同仁（M-2 测的是分叉后"继续运行"的可行性，与分叉后"重新评分"是两件事，后者由本机制天然支持）。
- 重放对轨迹敏感：任何非确定副作用（时间戳、随机数）若进入 DB 状态会破坏哈希一致性——τ2 环境为模拟环境，**推测**其内部确定性良好，但须实测验证同一轨迹两次评分哈希一致（S-2）。

### 9.4 软评审覆盖与匿名化要点
硬分测不到：沟通质量（费用说明、政策解释）——本题的 5 条 nl_assertions 恰是这部分的形式化代理，但不在默认硬分内；方案合理性（取消/升级的分派顺序与成本沟通时机）。处置建议（冻结决策项）：(a) nl_assertions 经 LLM judge 作为次要硬证据单列（与主硬分分开报告），或 (b) 全部交由人工盲审覆盖。盲审材料含对话记录 + 终态摘要；匿名化：去 τ2/airline 来源标识与题号 44、去分支标签与暂停提示。

### 9.5 记录对接
- 整体硬评分 ← reward；**必须逐组件保存 reward_breakdown**（DB/COMMUNICATE/NL_ASSERTIONS）——乘积型二元总分会丢失局部信息，逐组件保存是"局部硬评分"字段的载体（缺口 G-2）；
- 轨迹文件 SHA-256 为支撑产物；评分器版本 = τ2 环境代码 + tasks.json 中题 44 定义整体冻结；
- 终止原因异常（非正常结束）导致直接 0：记录中须把"轨迹异常终止"与"动作做错"分开（score_status 或独立标记，对齐"不得都记 0"）。

### 9.6 风险
- 二元分辨率过低：稀释线关心局部差异，DB 哈希全对/全错无法体现"做错一个字段"——建议工程侧在重放后附加 DB 状态 diff 明细（非原生输出，属我们的记录层增强，**推测**：实现可行且不改变原生分）。
- 哈希比对对重放严格性敏感（环境代码有 strict_replay 相关参数），版本冻结粒度必须到环境代码全量。
- 若未来把 nl_assertions 纳入硬分，judge 模型（gpt-4.1-2025-04-14）的可用性与版本漂移是新风险源。


---

## 10. 题 9：AssistantBench validation id 2ddae3b7a...（Queen Anne 房价，类别 3 或 1 边缘，冻结时判定，对齐 M-6）

### 10.1 原生评价器机制
依据 assistantbench_validation.parquet 原文：
- task: "What's the lowest price a Single Family house was sold in Queen Anne in January 2023?"；answer: "1010000"（字符串形态的数值）；
- gold_url 指向 King County Assessor 的 eRealProperty/esales 页面，explanation 说明经 King County Assessor API 可验证——**注意：与草案 M-3 所述"Redfin 历史成交数据"不符，以 parquet 原文为准，差异记录见 15.2**；
- 官方评分为 gold answer 精确比对；官方评分代码未缓存，精确的归一化规则（数值/单位/千分位处理）待核（**推测**：论文口径为 exact match 类指标），见缺口 G-4。

### 10.2 硬分输入输出与确定性
- 输入：代理提交的最终答案（从检索记录与聚合结论中提取）。
- 输出：与 "1010000" 的精确匹配 0/1。
- 确定性程度：**确定性**（比对器自写并冻结后即完全确定；gold answer 已冻结，不受 live 网站影响）。

### 10.3 接入方式
- 框架需交出：分支的最终答案 + 支撑检索记录（盲审用）。
- **无需环境存活评分**：gold 已冻结，评分是本地比对。live 网站（King County Assessor）的可达性影响的是"任务能否被完成"（运行侧，M-3 实测），不是评分侧。
- 无现成原生评分器可用 → 须自写比对器并按评分器流程冻结（scorer_id/scorer_version/scorer_sha256）：归一化规则（纯数字提取、单位换算是否允许）必须在冻结前写死；比对器修复走"对原产物重新评分、新 score_record_id"（experiment-records.md 第 7 节规则 6）。

### 10.4 软评审覆盖与匿名化要点
硬分只有一个数，测不到：信息源选择的合理性（为什么用 King County Assessor 而不是聚合站）、筛选口径执行（Single Family / Queen Anne / 2023-01）是否正确、聚合方式（最低价的取值依据）。盲审材料 = 检索轨迹 + 中间记录 + 最终答案；匿名化：去 AssistantBench 来源与题目 id（可反查原数据集）、去分支标签与暂停提示。

### 10.5 记录对接
- 整体硬评分 ← 匹配结果 0/1；局部硬评分：本题无原生局部项——检索过程质量只能进盲审，不得为此发明局部硬分（design.md 8.1）；
- 未提交答案记"未到达目标决定"（单独字段），不得记 0 分；答案提交但错误记 0 并与未到达分开保存；
- 比对器即评分器，其代码与归一化规则文档整体记 SHA-256。

### 10.6 风险
- live 网站时效性（M-3）：gold_url 指向实时网站，数据变动会使任务不可复现——虽然不影响评分（gold 冻结），但影响"错误是否能被发现/纠正"的实验语义，实测不通过则触发草案 2.3 降级备选。
- 比对器归一化规则的口径风险：过松（允许单位换算）或过严（不允许格式差）都会改变结果，冻结时必须写明并冻结。
- gold answer 以字符串 "1010000" 存储，若代理输出 "$1,010,000" 等形态，归一化规则决定判定——同上。

## 11. 备位替换题评分规格简表

| 备位 | 评分机制要点 | 确定性 | 评分侧特别事项 |
| --- | --- | --- | --- |
| τ2-B tau2-retail-55 | 同题 8 重放 + DB 哈希；但 reward_basis = ["DB","NL_ASSERTION"] → **硬分含 LLM judge**（gpt-4.1-2025-04-14, temp 0） | 含 LLM | 替换题 8 后硬分确定性下降，judge 模型须冻结（G-3） |
| τ2-C tau2-airline-18 | 同题 8；reward_basis = ["DB","COMMUNICATE"]，communicate_info 非空（含 "$23553" 子串项）→ 沟通项为确定性子串匹配 | 确定性 | communicate 子串匹配对数字格式敏感 |
| SWE T3 sympy__sympy-15198 | 同题 4/5 机制；round2 记 F2P 3、P2P 115（本轮未对该题读 parquet 原始列表，数值沿用 round2 文档） | 确定性 | 需环境跑测试 |
| SWE T7 pydata__xarray-4827 | 同上；round2 记 F2P 5、P2P 167 | 确定性 | 需环境跑测试 |
| TB-B db-wal-recovery | run-tests.sh + pytest；/app/recovered.json 11 条记录精确值断言（tb_wal_test_outputs.py） | 确定性 | 隐藏测试注入同题 6 |
| TAC-B finance-revenue-reconciliation | 4 checkpoint（各 1 分）+ **启用 bonus_for_completing_final**（末项满分则整体满分，原生策略非自创）；CP3 为 11 个 CTR 编号排序精确比对；CP4 对 4 名员工逐个 LLM 判（evaluate_chat_history_with_llm） | 含 LLM | bonus 策略放大末项权重，局部/整体关系须按原生语义记录 |
| TAC-C admin-employee-info-reconciliation | rocketChat 联系人数 + CSV 精确值，**全确定性无 LLM** | 确定性 | 换入后题 2 位的 LLM 判分风险消失 |
| TAC-D pm-schedule-meeting-1 | 聊天历史非空 + conclusion.txt 经 LLM 判，权重 1/1/3 | 含 LLM | conclusion.txt 为主要分值载体 |
| ALE-B equity_research_summary | score_workbook.py：openpyxl 读 xlsx、manifest 驱动（sheet 名模糊定位、检查公式而非硬编码值） | 确定性 | 任务依赖 live Yahoo Finance 数据 → 参考答案时点漂移风险，换入须先实测 |
| ALE-C pe_screening_memo_1 | score.py（LLM-judge edition）：gpt-4o-mini（temp 0, max_tokens 5）+ 三道规则硬门（标题结构/≥250 词/显式 Go-No-Go-Hold）；score = 0.75×加权章节覆盖 + 0.25×锚点命中率，阈值 0.7 | 含 LLM | 与题 3 的纯数值精确比对形态完全不同（草案 2.3 已警示答案/数值格计数） |
| AB-B（Seattle Children Museum） | 同题 9，answer "45" | 确定性 | 同题 9 全部风险 |
| AB-C（Mission Bay） | 同题 9，answer "3080000"，gold_url 为 Zillow/Redfin/Estately 类聚合站 | 确定性 | 同题 9 |
| f5947c33（HANDBOOK 类别 3 备位） | 与题 7 完全同构的 sop_verifier 框架 | 确定性 | 接入方式同题 7 |


---

## 12. 9 题评价器机制一览（汇总）

| 题 | 来源 | 硬分机制 | 确定性 | 评分需环境存活 | 局部项粒度 | 盲审 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 9b2f7a29 | HANDBOOK | rubrics 平均分（12 条确定性断言） | 确定性 | 是（Docker/Harbor） | 12 条 rubric | 是 |
| 2 TAC-10k | TAC | checkpoint 加权和（6 分） | 含 LLM（CP5） | 是（容器 + RocketChat） | 5 个 checkpoint | 是 |
| 3 ALE-AAPL | ALE | Decimal 字段精确比对 + 0.95 阈值 | 确定性 | 否（参考文件一次性获取后本地比对） | 逐字段 | 是 |
| 4 django-13495 | SWE | F2P/P2P 测试 → resolved | 确定性 | 是（需跑测试） | F2P 5 条 + P2P 计数 | 是 |
| 5 sklearn-11542 | SWE | 同上 | 确定性 | 是（需跑测试） | F2P 5 条 + P2P 计数 | 是 |
| 6 3d-legacy | TB | pytest 通过率 | 确定性 | 是（容器内注入测试） | 逐测试用例 | 是 |
| 7 d9d532c1 | HANDBOOK | rubrics 平均分（6 条，含 2 反向） | 确定性 | 是（Docker/Harbor） | 6 条 rubric | 是 |
| 8 tau2-44 | τ2 | 轨迹重放 + DB 哈希（二元） | 确定性（默认模式） | 否（纯 Python 重放，无需 Docker） | 仅组件级（建议加 diff 明细） | 是 |
| 9 AB-QueenAnne | AB | gold answer 精确比对（比对器自写） | 确定性（冻结后） | 否 | 无原生局部项 | 是 |

计数结论：
- **硬分路径全确定性：8 题**（题 1、3、4、5、6、7、8、9；题 8 仅限默认模式）；**含 LLM 判分：1 题**（题 2 的 CP5）。
- **评分需要环境存活/运行测试：6 题**（题 1、2、4、5、6、7——其中题 1/2/6/7 对齐草案 M-1 的 Docker 清单，题 4/5 为 M-1 外围单列）；评分纯本地：3 题（题 3、8、9，其中题 8 需 τ2 环境代码但无需容器）。
- **需人工盲审：9 题全部**（design.md 8.2 对所有分支组比较的统一要求；各题硬分测不到的维度见逐题 2.4~10.4）。

## 13. 记录格式对接缺口（experiment-records.md 第 5 节对照）

| 编号 | 缺口 | 涉及题 | 处置建议 |
| --- | --- | --- | --- |
| G-1 | SWE resolved 为二元值，且官方 harness 判定代码未缓存；仅存单值不满足"各评分项数值/分母/缺失" | 题 4、5 | 取回并冻结 harness 判定定义（S-1）；记录层强制保存逐测试通过/失败明细 |
| G-2 | τ2 reward 为组件乘积的二元值，局部信息天然丢失 | 题 8 | 逐组件保存 reward_breakdown；建议附加重放后 DB diff 明细（记录层增强，不改原生分） |
| G-3 | 记录格式有评分器版本管理（6.3），但无"LLM judge 模型/端点/参数"专用字段 | 题 2（及备位 τ2-B、TAC-B/D、ALE-C） | 在 scorer_version 说明中固化 judge 模型名、温度与端点；冻结时决定是否单列字段 |
| G-4 | AB 无现成评分器，自写比对器需走评分器冻结与重评分流程 | 题 9 | 比对器代码 + 归一化规则文档作为评分器整体记 SHA-256；修复走第 7 节规则 6 |
| G-5 | TAC @grader 吞异常、τ2 非正常终止直接 0，"评分器故障/轨迹异常"与"答错"需区分 | 题 2、8 | 异常项记缺失并标 score_status = partial，与 0 分分开（记录格式已支持，逐题落实） |
| G-6 | HANDBOOK 原生只落 reward.txt 单浮点 | 题 1、7 | 记录层同时保存 results.json 全文作为原始评分器输出 |
| G-7 | TAC CP1 以轨迹为评分输入，轨迹成为评分类产物 | 题 2 | 轨迹文件列入"每个最终产物及产物索引"并记 SHA-256（6.2 已覆盖，落实即可） |

总体判断：记录格式本身无需修改，缺口均可在记录落实层补齐；唯一需要"新增冻结决策"的是 G-3（LLM judge 版本字段）与 G-4（AB 比对器口径）。

## 14. 评分侧依赖实测清单（S 编号，对齐并扩展草案 M 清单）

- **S-1**：SWE harness resolved 判定定义取回 + P2P 口径核实（round2 的 74/222 与 parquet 原始列表 7218/18552 不一致，见 15.1）。依赖测试环境（Docker），归入 M-1/M-4 环境解锁后执行。
- **S-2**：τ2 重放评分确定性实测：同一轨迹两次评分哈希是否一致（纯 Python，不被 Q-E 阻塞，可与 M-2 并行）。
- **S-3**：TAC CP5 的 LLM judge 环境冻结实测：LITELLM_MODEL/BASE_URL/API_KEY 固定后判分稳定性；RocketChat 聊天记录在评分时刻的导出与留存方式。依赖容器环境（M-1）。
- **S-4**：ALE 参考文件一次性获取与隔离核验（M-8）：经 secret 机制取参考 JSON、记 SHA-256、确认不进入代理工作区、跑一次泄漏扫描。
- **S-5**：AB 比对器编写与冻结 + gold_url 现势核验（与 M-3 联动）：归一化规则写死；同时按 15.2 纠正 M-3 的 Redfin 表述。
- **S-6**：HANDBOOK tests/rubrics 版本冻结：本地仓库 commit + 逐文件 SHA-256；抽样重跑验证 rubric 代码可执行（只读仓库，复制后在隔离环境验证）。依赖 Docker（M-1）。
- **S-7**：TB 隐藏测试注入时机与泄漏扫描实测（M-1）：确认代理运行阶段不可见测试文件、评分阶段注入成功。
- **S-8**：TAC CP3 自比缺陷的处置决策（见 15.3）：按原样保留并记录，不修原生评分器；冻结时书面确认。
- **S-9**（条件项，仅备位启用时）：ALE-B 的 Yahoo Finance live 数据参考答案时点漂移实测。

## 15. 已发现差异记录（如实记录，不回改既有文档）

1. **SWE P2P 口径差异**：candidate-search-round2.md 记 T1（django-13495）"F2P 5、P2P 74"、T4（scikit-learn-11542）"F2P 5、P2P 222"；本轮读 test.parquet 原始字段，P2P 列表长度为 7218 与 18552。差异原因未定（**推测**：round2 可能按测试文件/模块去重计数或引用了其他口径）。冻结前须以 S-1 实测口径为准。
2. **题 9 答案依据表述差异**：草案 M-3 写"答案 1010000 依据 Redfin 历史成交数据"；parquet 原文的 gold_url 为 King County Assessor eRealProperty/esales 页面、explanation 亦指明 King County Assessor API。本文档以 parquet 原文为准；M-3 的实测对象应为 King County Assessor 而非 Redfin（M-3 文字未改，按任务红线不回改既有文档）。
3. **TAC 10k 评分器 CP3 自比缺陷**：evaluator 第 58 行将参考与被测读成同一文件（`reference_df = df = pd.read_csv(file_path, ...)`），公司名比对空转，实际只校验必备列。该缺陷只放宽不收紧评分；处置：按原样保留（不修原生评分器），冻结时书面确认（S-8）。

## 16. 声明

- 本任务未运行任何评分器、测试、基准任务或代理；全部机制描述基于评分器源码、配置文件与数据文件原文。
- 未修改任何既有文档；HANDBOOK 仓库仅读取。
- 本轮为取证新抓取 22 个评分器相关文件（τ2 评分器 6、TAC 基础与备位 7、TB 测试与配置 6、ALE 备位评分器 2、τ2 配置 1），全部位于 .materials-cache/round4/（gitignore 覆盖，不入库）。
- 标注"推测"处为无原文依据的合理推断，冻结前须经对应 S 项实测或取回原文确认。
