# 上下文不参与决策：实验设计

## 1. 研究问题

我们关心一种比“模型忘了上下文”更窄的失败：

> **模型能够正确回忆此前约束，也能够正确理解当前动作会产生什么后果，但在真实复杂任务执行到这个动作时，却没有把两者结合起来。**

典型状态不是 `忘记规则`，而是：

- Recall 正确；
- Applicability / action semantics 正确；
- Execution 仍然错误。

这可以把“它做的时候根本没想起前面的东西”从感性描述变成机器可判定的行为模式。

## 2. 三联测试

对现有 benchmark 中有明确 constraint-action 关系的单元，建立三个**相互独立**的 run，避免前一个 probe 提醒后一个。

### Recall

给完整 policy / handbook 上下文，问与目标约束直接相关的结构化问题，例如：允许 / 禁止 / 条件允许。

目的：确认模型仍能取回规则。

### Applicability

给当前 world state 和候选 action，不运行完整任务，问这个动作在当前事实下是否满足那条规则。

目的：确认模型理解 action semantics 和约束的适用关系。

### Execution

运行原 benchmark 的完整复杂任务，不提醒目标约束，也不问它“有没有记住”。由原有 deterministic validator / final state evaluator 判断模型最终是否真的做对。

## 3. 核心指标

最重要的是条件性失败：

`R = 1, A = 1, E = 0`

即“记得、也懂，但执行没用上”。

主指标可写成：

`CIFR = P(E = 0 | R = 1, A = 1)`

CIFR 只统计已经证明不是纯遗忘、也不是纯工具知识缺失的样本。

同时保留 Recall、Applicability、Execution 各自原始正确率，避免一个条件指标掩盖前两层本身的退化。

## 4. 反事实对照

不能让“永远拒绝行动”成为高分策略。

每类 constraint-action 最好构造配对：

- **constraint-active**：关键事实使动作确实不允许；
- **constraint-inactive**：只改变一个决定适用性的事实，动作变为允许 / 必须执行。

反事实优先修改结构化 world state、权限位、审批状态、资源状态等真实变量，不重新让 GPT 编一套故事。

## 5. Minimal vs Full context

对同一 constraint-action pair 再做上下文控制：

- **Minimal**：只保留完成判断真正需要的 policy + state；
- **Full**：保留真实完整任务上下文和 trajectory。

如果 minimal decision 正确、full-context Recall 也正确，但 full execution 错误，就更接近我们真正关心的“信息存在，却没有进入在线决策”。

## 6. Decisive action 分析

不需要对 trajectory 的每一步都做 probe。

优先定位第一个真正改变环境、并使成功轨迹开始不可恢复的 mutating action，再围绕这个 action 建 Recall / Applicability 诊断。

这一点参考 SABER 的 decisive deviation / mutating action 分析思路。

## 7. 评价原则

- 尽量使用原 benchmark 的程序化 rubric、数据库最终状态、tool-call validator；
- 不用 LLM judge 判断“它有没有认真思考”；
- 三个 run 独立，不能先提醒规则再让同一 trajectory 继续；
- required action 和 prohibited action 都要有；
- 最保守、什么都不做的 agent 不能通过反事实配对拿满分。

## 8. 与普通长上下文 benchmark 的区别

普通测试常问“模型还能不能找到前面那句话”。

这里进一步问：

> **即使已经证明它能找到，而且知道这句话与当前动作有关，这条信息在复杂执行时是否真的具有行为效力？**

这才是本方向的核心。