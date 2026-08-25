# subtask-dilution-bench

## **我永远不会忘掉多日以后突然发现 GPT 5.6 Sol 悄咪咪地把表格里 description 字段拿去数长度的那一天**

探究问题：
 - 模型单独能够稳定处理的局部问题，在进入更大的完整任务后，会不会因为实际分到的思考资源 / 注意力不足而明显退化？
 - 如果允许复杂任务使用更多推理资源，能否弥补这种退化？

于是进行了心血来潮的 vibe benchmark 设计。

## 主要事实和观点 1

1. 小任务拿出来单独做，天然就会获得更大的精力思考；
2. 不是小任务用花最多的精力做，就一定是最好的方法；
3. 但是你就算不花最多的精力，但我也确实可以说一些处理的方式就是没思考甚至错误的，跟抠细节都没啥关系；
4. 无论如何，确实 AI 难以在一些大任务中正确地思考细枝末节；
5. 我们现有的示例太少， AI 如果自己设计很有可能过拟合，例如字符串问题 AI 多个对话都想按照这个构造。

> 一个模型对某个局部问题本来具有足够的能力。单独问它时，这个问题占据了当前主要注意力，所以它会真正想一下，哪怕最后得到的仍然只是一个很简单的方案。
> 当任务越来越复杂时，模型需要同时规划、记忆、生成、检查很多东西，于是某些局部问题获得的实际认知投入下降了：不是“选择了一个简洁方案”，而是**那一步压根没真正想**。
> 而 AI 与人不完全一样：复杂任务本来就可以允许更长推理、更多 test-time compute、更多子调用。因此我们有理由期待，**随着任务规模增大，总计算也跟着增大，而不是默认把近似固定的一锅注意力越摊越薄**。
>

## 更新：我还tm不会忘掉因为沙盒里面不能测试就想入非非忘记了做好之前不给开发者看 AI 垃圾而开始未经授权 draft PR 然后疯狂测 CI 甚至惊动仓库主人的那二十分钟

探究问题：
- 当一个局部目标拥有非常清晰、连续、可验证的反馈时，模型会不会向它投入超出其全局价值的资源，挤压更重要但反馈模糊的工作？
- 当模型能够回忆此前约束，也理解当前动作的含义时，这些上下文信息为什么仍可能没有进入实际决策？

于是进行了怒火中烧的 vibe benchmark 设计。

## 主要事实和观点 2

1. **显著反馈导致资源失衡**应单独研究：CI 红绿一类指标会持续告诉模型“还没完成”，可能把局部目标变成过强的优化对象；要区分“因为它重要所以多投入”和“只是因为反馈明显所以被吸住”，核心看固定预算下的全局机会成本。
2. **上下文不参与决策**也是独立问题：模型可能能正确复述约束，也知道某个动作会产生什么后果，但在真实执行到该动作时没有把两者结合起来。应把 Recall、Applicability、Execution 分开测，重点观察“知道却没用上”的条件性失败。
3. 这两个方向与前面的子任务稀释有关联，但实验上不耦合：一个研究资源被过强局部反馈吸走，一个研究已有上下文是否真正约束行动。
4. 不自己批量生成大量 AI 味场景，优先借现有 benchmark 的真实任务、环境和 evaluator：第一类参考 reward hacking / optimization-pressure 测试的连续反馈设计；第二类优先参考 HANDBOOK.md、CCTU、τ-bench、ToolSandbox、SABER、AgentIF 等已有 policy / constraint / tool-use 数据。

## 目前任务

- [x] 将三个方向分别整理成独立实验设计，避免为了统一故事而共享指标或强行耦合。
- [ ] 子任务稀释：从候选 benchmark 抽真实复杂任务，按 direct / sham / reconsider 做小规模 checkpoint-fork pilot。
- [ ] 显著反馈导致资源失衡：从有两个真实竞争目标的任务中，分别做“同一信息的呈现显著性”和“连续在线/批量延后反馈”两个 2×2 模块；v0 使用真正进入评分器的受控价值权重，记录局部投入和全局机会成本。
- [ ] 上下文不参与决策：v0 已冻结 S01、S02、S04、S07、S08、S09、S10 共 7 个母任务；Local/Full 的 A/B 生成、评分和匿名打包已经完成，Recall、Applicability、独立隔离验证和正式重复运行尚未完成。当前不再扩题，也还没有真实模型研究结果。
- [ ] 三个方向都先做小规模 pilot；没有稳定信号的方向及时停止，不先扩成大题库。

## 目前文档

- [`HANDOFF-2026-08-25.md`](HANDOFF-2026-08-25.md)：给下一位模型的完整交接入口，包含本轮完成内容、失败边界、当前代码停点、必读顺序和接手复述检查。
- [`docs/research-ledger.md`](docs/research-ledger.md)：跨版本研究总账，固定三条研究线、不得静默推翻的原则、现有成果位置和证据边界。任何新搜索、扩题或实现先对照这里。
- [`docs/superpowers/specs/2026-08-24-integrated-benchmark-program-design.md`](docs/superpowers/specs/2026-08-24-integrated-benchmark-program-design.md)：三条实验线的综合结构、推进顺序和共同测试前门槛。
- [`docs/experiment-records.md`](docs/experiment-records.md)：三条线共用的批次、母任务、运行、产物、评分、匿名、版本和重跑记录格式；只统一记录，不建立共同总分。
- [`docs/pre-test-readiness.md`](docs/pre-test-readiness.md)：逐项说明三条线目前已经完成什么、正式模型实验前还缺什么。
- [`docs/subtask-dilution/design.md`](docs/subtask-dilution/design.md)：子任务稀释的当前实验设计。
- [`docs/subtask-dilution/source-selection.md`](docs/subtask-dilution/source-selection.md)：子任务稀释的素材筛选与参考 benchmark。
- [`docs/feedback-allocation/design.md`](docs/feedback-allocation/design.md)：显著反馈导致资源失衡的实验设计。
- [`docs/feedback-allocation/source-selection.md`](docs/feedback-allocation/source-selection.md)：显著反馈方向的参考资料与素材筛选。
- [`docs/context-integration/design.md`](docs/context-integration/design.md)：上下文不参与决策的实验设计。
- [`docs/context-integration/pilot-spec.md`](docs/context-integration/pilot-spec.md)：上下文不参与决策的第一轮 pilot 规格。
- [`docs/context-integration/status-v0.md`](docs/context-integration/status-v0.md)：七个已实现母任务、现有工程资产、缺失诊断层和当前结论边界。
- [`docs/context-integration/candidate-screening.md`](docs/context-integration/candidate-screening.md)：HANDBOOK 真实任务的 pilot 候选筛选记录。
- [`docs/context-integration/source-selection.md`](docs/context-integration/source-selection.md)：上下文整合方向的参考 benchmark 与筛选标准。
- [`docs/context-integration/next-samples-v1.md`](docs/context-integration/next-samples-v1.md)：第二批六个已实现母任务的历史选择依据；当前冻结状态以 `status-v0.md` 和 `pilot-spec.md` 为准。
- [`experiments/next-samples-progress.md`](experiments/next-samples-progress.md)：第二批六道题的实际制作和验证结果。
- [`experiments/design-progress-2026-08-24.md`](experiments/design-progress-2026-08-24.md)：面向审阅的简明进度说明，汇总今天保留、完成和仍未完成的工作。
- [`archive/failed-design/`](archive/failed-design/)：此前失败设计对话的原始存档。我说白了， AI 根本无法处理这么复杂多角度的事情……

## 生成第二批匿名任务包

本机已有 HANDBOOK 仓库时，可一次生成六道题共 24 个匿名 ZIP：

```powershell
python -m benchmarks.context_integration.make_release `
  --handbook D:\File\Git\handbook `
  --release-output experiments\next-samples-release\release `
  --private-manifest experiments\next-samples-release\private\mapping.json
```

`release` 目录只含匿名 ZIP 和校验值；条件对应表单独写入 `private/mapping.json`，不能交给被测模型。
