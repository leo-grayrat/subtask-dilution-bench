# 上下文不参与决策：参考 benchmark 与素材选择

## 1. 主数据源：HANDBOOK.md

当前最接近我们目标的现成 benchmark。

它的价值不只是“长上下文”，而是：

- agent 面对长期有效的 SOP / policy；
- 在较长工作流中持续做真实操作；
- evaluator 能检查 required / prohibited actions；
- 适合研究 standing instruction 是否真的持续约束行为。

我们计划在其原有 execution grading 之外增加 Recall 和 Applicability 两层诊断。

参考：
- https://github.com/surge-ai/handbook
- https://arxiv.org/abs/2607.25398

## 2. CCTU

用途：补充复杂 tool-use constraint 的类型和 step-level 自动检查。

适合借：

- 多类 resource / behavior / tool / response constraint；
- 可执行 validator；
- 大量“知道规则以后仍需在 tool call 时满足”的场景。

我们更关注其中能够明确抽出 `constraint + current state + action` 的样本。

参考：
- https://github.com/Junjie-Ye/CCTU

## 3. τ-bench

用途：提供 policy + 用户交互 + API world state 的真实 agent 环境。

适合借：

- 最终数据库状态评价；
- required / prohibited state change；
- 同一 policy 在多轮交互中持续生效。

它适合作为 execution 层和反事实 state 修改的候选环境。

参考：
- https://github.com/sierra-research/tau-bench

## 4. ToolSandbox

用途：补充 action 是否适用取决于当前 world state、信息是否充分的 tool-use 场景。

特别适合 Applicability 层：模型不仅要记住规则，还要理解“当前事实下这个动作是否真的可用”。

参考：
- https://github.com/apple/ToolSandbox

## 5. AgentIF

用途：作为 constraint 类型和 evaluator 设计的素材库。

适合借：

- 来自真实 agent application 的多约束 instruction；
- 对单个 constraint 的拆分标注；
- code / hybrid evaluator 的组织方式。

它不一定是第一主环境，但可以帮助我们避免只围绕“不要公开 / 不要写入”一种规则造题。

参考：
- https://github.com/THU-KEG/AgentIF

## 6. SABER

用途：主要借**轨迹分析方法**，不是拿它直接当题库。

我们关注：

- mutating action 与 non-mutating action 的区别；
- decisive deviation：哪个最早的有后果动作真正把成功轨迹推向失败；
- 只在高后果 action 周围做 targeted diagnosis，而不是每一步都复盘全部上下文。

参考：
- https://arxiv.org/abs/2512.07850

## 7. 选样标准

优先保留同时满足以下条件的 constraint-action 单元：

1. constraint 在上下文里明确存在；
2. action 后果可由环境 / 文档确定，不依赖主观解释；
3. execution 有 deterministic 或近似 deterministic evaluator；
4. 能单独构造 Recall probe；
5. 能单独构造 Applicability probe；
6. 可以做 active / inactive 反事实配对；
7. 完整任务足够复杂，确实存在“规则知道但在线执行没用上”的空间。

## 8. 不优先的材料

### 纯 needle-in-a-haystack

它只能说明检索或记忆，不足以证明信息有没有进入行动。

### 只有禁止动作的 safety 场景

模型永远拒绝就可能得高分，必须同时有 required actions 和反事实允许版本。

### 需要 LLM judge 猜动作是否合规的场景

第一版尽量回避，优先使用结构化状态和程序化 validator。

## 9. 下一步

先从 HANDBOOK.md 和 CCTU 抽一小批有清晰 validator 的 constraint-action 单元，建立 Recall–Applicability–Execution 三联表；再用 τ-bench / ToolSandbox 扩展 world-state 和反事实类型。