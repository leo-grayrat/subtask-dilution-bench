# 三条研究线的共用实验记录

更新日期：2026-08-24

这份文件只统一记录方式，不统一研究问题和分数。三条研究线可以使用同一套编号、版本、校验值、运行日志和失效规则，但各自保留自己的条件、评分器和结论。

禁止建立跨研究线的“总分”。子任务稀释、反馈资源分配、上下文整合的分数含义不同，不能相加、平均或据此给模型排一个统一名次。

## 1. 记录层级

记录按下面顺序组织：

1. **实验批次**：某条研究线在一套冻结协议下的全部运行。
2. **母任务**：来自真实来源的一项完整任务，是主要统计单位。
3. **任务内条件**：同一母任务的对照条件。
4. **计划运行**：冻结前写入清单的一次条件重复。
5. **运行尝试**：计划运行实际启动的一次尝试。技术失败后的重跑是新尝试，不覆盖旧尝试。
6. **事件与产物**：可见消息、工具动作、文件变化、最终交付物和环境状态。
7. **评分记录**：评分器或盲评者对一份已冻结产物给出的结果。

三条研究线在第 3 层的结构不同：

| 研究线 | 母任务内层级 |
| --- | --- |
| 子任务稀释 | 根运行 → checkpoint → 同状态分支组 → `direct / sham / reconsider` 分支 |
| 反馈资源分配 | P/C 反馈模块 → 价值高低 × 反馈强弱的四个条件 → 独立重复 |
| 上下文整合 | `Recall / Applicability / Local / Full` → A/B 状态（Recall 不重复 A/B）→ 独立重复 |

checkpoint、分支、A/B、Local/Full、多角度变体和重复运行都不是新的独立样本。统计时先在同一母任务内形成条件差异，再让不同母任务等权进入跨任务汇总。数百次模型调用仍可能只来自少数几个母任务。

## 2. 文件与编号

每个正式实验批次至少保存以下内容：

```text
<experiment_id>/
  private-manifest.jsonl
  manifest-freeze.json
  runs/
    <run_attempt_id>/
      run.json
      events.jsonl
      artifacts/
      artifact-index.json
  scores/
    <score_record_id>.json
  summaries/
    by-mother-task.json
```

真实保存位置可以不同，但这些逻辑文件必须一一对应。私有清单、条件对应关系和评分器不得放进被测 agent 可见的任务目录，也不得装入匿名 ZIP。

编号要求：

- `experiment_id`：研究线与冻结协议的一次正式批次；
- `mother_task_id`：稳定母任务编号，不能随匿名文件名改变；
- `planned_run_id`：冻结清单中的一次计划运行；
- `run_attempt_id`：一次实际启动，格式应能区分第几次尝试；
- `anonymous_package_id`：不含题号、条件或研究含义的随机编号；
- `score_record_id`：一次评分或重新评分的独立编号。

## 3. 私有 manifest

`private-manifest.jsonl` 每行对应一个计划运行。第一次正式运行前生成、检查并冻结；之后只追加修订和状态，不静默改写原记录。

### 3.1 身份与来源

- `experiment_id`
- `research_line`
- `protocol_version`
- `manifest_revision`
- `mother_task_id`
- `source_family`
- `source_item_id`
- `source_version`
- `source_snapshot_sha256`
- `inclusion_reason`

### 3.2 私有条件对应

- `condition_id`
- `condition_fields`：保存该研究线的真实条件；
- `decision_or_checkpoint_id`：不适用时为 `null`；
- `state_variant`：不适用时为 `null`；
- `repeat_id`
- `planned_run_id`
- `anonymous_package_id`
- `anonymous_filename`
- `package_sha256`

`condition_fields` 只能存在于私有记录。例如：子任务稀释保存分支类型；反馈资源分配保存 P/C 模块、价值与反馈强弱；上下文整合保存诊断层、A/B 和 Local/Full。公开目录只能出现不透明编号。

### 3.3 模型与运行配置

- `model_provider`
- `model_name`
- `model_snapshot_or_version`
- `model_config_id`
- `system_prompt_version` 与 `system_prompt_sha256`
- `task_prompt_version` 与 `task_prompt_sha256`
- `toolset_version` 与 `toolset_sha256`
- `environment_version` 与 `environment_sha256`
- `action_budget`、`token_budget`、`time_budget_seconds`
- `timeout_rule_version`
- `seed_requested`
- `seed_effective`：平台不能确认时写 `unknown`，不能假装可控；
- `run_order`

### 3.4 评分、有效性与重跑

- `scorer_id`、`scorer_version`、`scorer_sha256`
- `rubric_version` 与 `rubric_sha256`
- `blind_review_protocol_version`：不需要人工盲评时为 `null`；
- `run_status`
- `validity_status`
- `invalid_reason_code` 与 `invalid_reason_note`
- `supersedes_attempt_id` 与 `superseded_by_attempt_id`
- `rerun_reason_code`
- `rerun_authorized_by_rule`
- `created_at`、`started_at`、`finished_at`、`unblinded_at`

## 4. 每次运行日志

### 4.1 `run.json`

一份运行尝试至少记录：

- 上述所有编号及其 manifest 修订号；
- 实际模型、提示、工具、环境和预算版本；
- 开始、结束、耗时和终止原因；
- 初始可见目录的文件清单与校验值；
- 隔离检查结果和任何越界访问记录；
- 实际消耗的动作数、tokens 和时间；
- 最终消息、最终环境状态和产物索引的校验值；
- 是否到达目标决定机会；
- 日志是否完整，缺失了什么。

### 4.2 `events.jsonl`

只记录被实验系统实际看见的内容，不要求模型提供隐藏思维过程。每条事件至少包含：

- `event_index` 与 `timestamp`
- `event_type`：消息、工具调用、工具结果、反馈出现、文件变化、checkpoint、最终提交等；
- `actor`
- `tool_name`：不适用时为 `null`；
- 输入和输出的文件引用或 SHA-256；
- 动作前后的剩余预算；
- 新增、修改或删除的产物及其 SHA-256；
- 反馈事件的规范载荷校验值；
- 运行错误、重试和超时信息。

大段内容可以单独保存，日志只放相对路径和校验值。原始消息、工具结果和产物不能因后续清理而被覆盖。

## 5. 分数记录

每次评分生成新的 JSON，至少包含：

- `score_record_id`
- `run_attempt_id`
- `scorer_id`、版本与 SHA-256
- `scored_at`
- `score_status`：`complete / partial / unscorable`
- 原始评分器输出；
- 各评分项的数值、分母和是否缺失；
- 支撑每个评分项的产物或日志位置；
- `opportunity_reached`；
- 人工盲评者编号、顺序随机化记录和逐人结果；
- 对旧评分的替代关系和重新评分原因。

共用格式不等于共用评分项：

| 研究线 | 至少保留的专用评分 |
| --- | --- |
| 子任务稀释 | checkpoint 是否到达、分支有效性、direct 自然基线、局部硬评分、整体硬评分、软性盲评、`reconsider-sham` 与 `reconsider-direct` 的任务内差异 |
| 反馈资源分配 | P/C 模块；焦点目标、竞争目标、背景工作和整体效用；动作、tokens、时间投入；反馈后投入变化；机会成本；边际收益与低收益后持续投入 |
| 上下文整合 | Recall、Applicability、Local、Full 各层评分；A/B；Full 是否到达目标决定；完整任务其他部分得分 |

硬评分和软性盲评分别保存。未到达目标决定、评分器故障和模型答错也分别保存，不能都写成 0 分。重新评分只新增分数记录，不需要重新运行模型。

## 6. 匿名、校验值和版本

### 6.1 匿名

- 匿名文件名不得含 S01、A/B、Local/Full、direct、价值高低、反馈强弱或研究线名称；
- 一个被测实例一次只能看见一个匿名任务目录；
- 条件对应表、评分器、测试、预期答案和实验说明留在私有位置；
- 原始产物冻结并校验后才能解盲，`unblinded_at` 必须记录；
- 匿名不等于隔离。只换目录但继承主对话，运行仍然无效。

### 6.2 SHA-256

至少为以下内容保存 SHA-256：

- 原始来源快照；
- 匿名任务包；
- 系统提示和任务提示；
- 工具与环境配置；
- 评分器和评分规则；
- 原始运行日志；
- 每个最终产物及产物索引；
- 每份分数记录；
- 冻结后的 manifest。

校验值只证明内容是否改变，不证明包内没有泄题。泄漏扫描和人工抽查仍须单独记录。

### 6.3 版本

至少分别维护协议、任务材料、匿名包、提示、工具环境、评分器、盲评规则和记录格式的版本。改变正确答案、条件含义、预算、提示语义或评分方式时必须升版本，并让受影响的旧运行失效或进入单独批次。只修排版也要产生新的文件校验值，但可保留语义版本。

## 7. 失效、未到达和重跑

`run_status` 使用：`planned / materialized / running / completed / aborted`。

`validity_status` 使用：

- `pending`：尚未判定；
- `valid`：按冻结协议完成；
- `invalid_isolation`：继承实验语义、看见私有文件或越界访问；
- `invalid_protocol`：条件、提示、预算、顺序或工具不符合冻结清单；
- `invalid_technical`：平台、进程、网络、文件或工具故障使运行不可解释；
- `invalid_material`：任务包制作错误或反事实不一致；
- `invalid_scoring`：无法恢复所需产物且不能可靠评分；
- `superseded`：由明确的新尝试或新版本替代。

“没有到达目标决定”是单独字段，不自动等于无效，也不能自动算作目标错误。各研究线按冻结规则决定它进入到达率、正确率还是仅作流程结果。

重跑遵守以下规则：

1. 只有冻结前列出的基础设施、隔离或材料故障可以触发重跑；
2. 模型结果不好、没有出现假设现象或评分不理想都不是重跑理由；
3. 同一 `planned_run_id` 的重跑使用新的 `run_attempt_id` 和递增的 `attempt_no`；
4. 原尝试、故障证据和失效判定全部保留；
5. 预先安排的独立重复是新的计划运行，不叫重跑；
6. 评分器修复优先对原产物重新评分，并生成新 `score_record_id`；
7. 每个计划运行允许的最大尝试数必须在实验批次冻结时写明。

## 8. 汇总与报告

正式汇总必须同时给出：

- 母任务数、来源和版本；
- 每个母任务内的条件数、计划重复数、有效运行数和失效数；
- 到达目标决定的次数；
- 各研究线自己的评分与任务内条件差异；
- 按母任务聚合的不确定性和逐母任务结果；
- 所有排除、失效、重跑和重新评分记录。

不能用运行次数替代母任务数，不能把同一母任务的多个分支当作独立证据，也不能把三条研究线压成一个总分。
