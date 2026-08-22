# subtask-dilution-bench

## **我永远不会忘掉多日以后突然发现 GPT 5.6 Sol 悄咪咪地把表格里 description 字段拿去数长度的那一天**

这个仓库用于研究一个很具体的问题：模型单独能够稳定处理的局部问题，在进入更大的完整任务后，会不会因为实际分到的 thinking / attention 不足而明显退化；如果允许复杂任务使用更多推理资源，这种退化能否被补回来。

当前阶段先做 benchmark 设计，不急着写评测框架。重点是两件事：

1. 找到适合的题目结构，而不是针对已经见过的错误出题。
2. 检查现有 benchmark 的真实样例，判断哪些材料能自然构造“局部问题不变、整体任务逐渐变大”的对照。

目前文档：

- [`docs/design.md`](docs/design.md)：当前 benchmark 设计骨架。
- [`docs/source-selection.md`](docs/source-selection.md)：现有 benchmark 素材应该怎么筛。
- [`archive/failed-design/`](archive/failed-design/)：此前失败设计对话的原始存档。
