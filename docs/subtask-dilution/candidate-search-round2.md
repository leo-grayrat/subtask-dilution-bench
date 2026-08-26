# 子任务稀释：候选第二轮搜索（SWE-bench test 分片全量过筛与限定来源任务级复核）

日期：2026-08-25（第二轮）

这份文档接续 candidate-sources-v0.md（第一轮）。用户本轮指示：HuggingFace 门控的 GAIA 暂时搁置（账号问题晚点决定），先把**不需要凭证**的已登记限定来源搜透；搜不到的缺口如实报告。本轮另收到两条追加输入：(a) 新登记来源 MiniSWE-bench（登记表称"234 题、剔除测试文件、出自 SWE-bench 论文"，HF 数据集 ID princeton-nlp/SWE-bench_MiniSWE）；(b) 硬门槛缺口 2 的容量口径问题（"能出几题"按来源集中度上限算）。本文档不修改任何既有文档与既有决定，不新增来源（MiniSWE-bench 由上级登记，本文只作核验），不运行任何被测代理。全部题目信息原样引用自本地已下载数据集，公开资料结论均给出出处；核验失败的来源如实写"未核验"，不用推测补写。

> **更正（2026-08-26 溯源）**：本段所述"追加输入"中的 MiniSWE-bench 登记，经溯源核查仓库中不存在任何书面登记实体，"上级登记"表述不可证实；用户已明确否认登记过该来源，主对话领导代理也从未登记。该条目按 AI 流程内产生的、出处不明的内容对待，维持"未核验、不能用、不计入任何核算"结论。原核验内容不改写。

## 0. 准入回答（按 research-ledger.md 第 8 节）

1. 属于子任务稀释研究线。
2. 补总账第 6 节该线缺口：母任务抽样框候选扩充（SWE-bench 由 dev 扩到 test 分片）、其余限定来源排除结论的任务级证据、硬门槛逐格可行性重算。
3. 保留总账第 3 节原则：不从空白编造任务（原则 1）；不把换皮当多样性（原则 2）；候选不是样本量（原则 3）；不预先围绕已知错误挑 checkpoint（原则 8）；不把现成 benchmark 拆成小题拼凑（原则 10）；不因新来源有趣而改变研究问题（原则 11）；工程获取结果不写成模型行为结论（原则 12）。
4. 不修改任何既有决定；复核结论只回答"上一轮的来源级排除是否过粗"，维持或推翻均给出任务级证据。
5. 角色：母任务材料来源核验。涉及来源全部为 source-selection.md 第 5 节已登记来源加用户新登记的 MiniSWE-bench，未引入其它来源。
6. 不做这项工作：第二轮无新候补进入总账，"不等 GAIA 最多能配出什么"无法向用户交付决策依据。

## 第一部分：SWE-bench test 分片全量过筛

### 1.1 方法与规则

数据：本地 .materials-cache/swe_bench/test.parquet（12,097,227 字节，2294 实例，第一轮已下载，本轮未重新下载）。初筛规则沿用 candidate-sources-v0.md 第 3.2 节冻结口径，未改动：参考补丁 30–300 行（按补丁文本行数计）、触及 >=2 个文件（按补丁内 "+++ b/" 计）、FAIL_TO_PASS >=3 个测试；再按第一轮实例级排除条款剔除"补丁只改测试文件"的实例。同一脚本在 dev 分片上复现第一轮的 39 题短名单，确认规则实现一致。分析脚本与中间产物在 .materials-cache/（.gitignore 第 14 行覆盖，不入库）。

### 1.2 数量结果

| 步骤 | 数量 |
| --- | --- |
| test 分片总实例 | 2294 |
| 冻结三条件（30–300 行、>=2 文件、FTP>=3）命中 | 191 |
| 其中补丁只改测试文件（按排除条款剔除） | 8 |
| **最终短名单** | **183** |

对照：dev 分片同规则 39 题。短名单群体统计：触及文件数中位 2、最大 13；补丁行数中位 117、p90 247；FAIL_TO_PASS 中位 5。

### 1.3 仓库分布与扎堆情况

| 仓库 | 短名单题数 | 短名单题数（占比） |
| --- | --- | --- |
| django/django | 67 | 36.6% |
| sympy/sympy | 21 | 11.5% |
| pydata/xarray | 18 | 9.8% |
| scikit-learn/scikit-learn | 17 | 9.3% |
| astropy/astropy | 16 | 8.7% |
| sphinx-doc/sphinx | 14 | 7.7% |
| pylint-dev/pylint | 11 | 6.0% |
| matplotlib/matplotlib | 10 | 5.5% |
| psf/requests | 7 | 3.8% |
| mwaskom/seaborn | 2 | 1.1% |

扎堆判断：

- 约束"同一类别同一来源最多 2 个"（source-selection.md 第 3.4 节）是**来源级**上限：SWE-bench 作为类别 2 的一个来源集合，无论短名单多大，正式最多出 **2 题**。这是本轮对上级追问（硬门槛缺口 2 的容量口径）的直接回答：容量口径是来源集中度上限 2，不是短名单规模。
- 仓库级无明文上限，但 django 单仓占 36.6%。正式抽样的 2 题应从不同仓库选取，以免主要工作载体同质化（第 3.4 节"共享同一父模板只保留一个"对同仓库同结构题同样适用）。
- 抽样框容量口径（第 3.4 节每类目标 6、最低 5 个合格候选）：test 短名单 183 题全部属类别 2 候选池，远超目标 6；dev 短名单 39 题也已过最低 5。**正式抽样框应按 candidate-sources-v0.md 开放问题 Q-D 的预设立场建在 test 分片上**，dev 分片留作练习任务（该分工仍是待用户确认的决策项，本文不代决）。

### 1.4 代表候选（9 题，跨 8 仓库，内容均为 problem_statement 字段原文节选，未改写）

以下 9 题为短名单中结构差异较大的代表，全部为类别 2、即时反馈（测试命令可随时运行并立即返回）、文件/测试型原生 evaluator（FAIL_TO_PASS / PASS_TO_PASS）。决定类型与 checkpoint 位置为结构预标注，正式冻结前按 design.md 第 4.2 节逐题确认。

**T1：django__django-13495**（repo django/django；base_commit b26ec77deb7c5052163ef8514ec7db70c0a5ea2a；触及 7 个文件，全部为四个数据库后端的 operations 层加 models/functions/datetime.py；F2P 5、P2P 74）
- 原文节选："Trunc() function take tzinfo param into account only when DateTimeField() are used as output_field ... So timezone convertation like AT TIME ZONE 'Europe/Kiev' was totally missed from sql."
- 潜在局部决定：跨四个后端的时区处理一致性方案（表示/建模选择）；改公共路径还是逐后端分改（范围）。
- 与 dev 候补的差异：多后端一致性型决定，短名单（dev）中未出现同构题。

**T2：django__django-12771**（repo django/django；base_commit 0f2885e3f6e0c73c9f455dcbc0326ac11ba4b84c；触及 5 个文件，均在 migrations 子系统；F2P 18、P2P 190）
- 原文节选："Store ModeState.fields into a dict. ... Given storing fields this way results in awkward and inefficient lookup by name for no apparent benefits and that dict now preserves insertion ordering I suggest we switch ModelState.fields to Dict[str, models.Field]. I suggest we do the same for ModelState.indexes and .constraints..."
- 潜在局部决定：数据结构迁移范围（fields 单改还是 indexes、constraints 同改）、autodetector 与 operations 多处联动改动的顺序与回归面。

**T3：sympy__sympy-15198**（repo sympy/sympy；base_commit 115dd821a4b9ec94ca1bd339a8c0d63f31a12167；触及 11 个文件，全部为打印器（ccode、fcode、glsl、jscode、julia、mathematica、octave 等）加 lambdify；F2P 3、P2P 115）
- 原文节选："1.3rc1 codegen regression in octave/julia/jscode ... I have a (minor?) regression in codeprinting from e99b756df3291a666ee2d2288daec4253014df40 ... Octave codegen prints `laguerre` but is supposed to error on `assoc_laguerre` (untested, apparently). The above commit breaks that."
- 潜在局部决定：回归根因定位后的修复层级（公共 codeprinter 一处修还是各打印器分修）、跨七个语言后端的行为一致性。注意题面短且指向外部 commit，材料准备方式需实测确定（与第一轮候选 S3 同类注意事项）。

**T4：scikit-learn__scikit-learn-11542**（repo scikit-learn/scikit-learn；base_commit cd7d9d985e1bbe2dbbbae17da0e9fbbba7e8c8c6；触及 6 个文件，含 4 个 example、forest.py 与 estimator_checks.py；F2P 5、P2P 222）
- 原文节选："Change default n_estimators in RandomForest (to 100?) ... I suggest 100. ... I'm not sure if I want to tag this 1.0 because really no-one should ever run a random forest with 10 trees imho and therefore deprecation of the current default will show people they have a bug."
- 潜在局部决定：默认值直接改还是走弃用周期（范围/优先级加验证安排混合）；示例与通用检查器同步改动的取舍。决定类型与 T1/T2/T3 明显不同。

**T5：sphinx-doc__sphinx-10207**（repo sphinx-doc/sphinx；base_commit 8b23f6db12d9fcdb6e1ca2015ea32e3e2e1fbdb6；触及 7 个文件；F2P 7、P2P 702）
- 原文节选（该实例 problem_statement 为多 issue 合并原文，含两段独立描述）："Allow keyboard shortcut `/` to focus on search ... napoleon prefixes instance attributes documented in class docstring with class name ... The `~` tilde being included is also a bug."
- 潜在局部决定：两个独立问题的处理顺序与范围边界、autodoc 与 napoleon 两处渲染路径的一致性。注意该实例是 SWE-bench 中已知的多 issue 合并形态，是否按一题使用需在冻结时判定并记录（材料原样使用，不拆不并）。

**T6：matplotlib__matplotlib-23198**（repo matplotlib/matplotlib；base_commit 3407cbc42f0e70595813e2b1816d432591558921；触及 2 个文件；F2P 9、P2P 1091）
- 原文节选："Inconsistency in keyword-arguments ncol/ncols, nrow/nrows ... plt.subplots(ncols=2) ... while axis.legend(ncol=2) ..."
- 潜在局部决定：API 命名统一方向（新名兼容旧名还是反向）、弃用策略——表示/建模选择加向后兼容，与 dev 候选 S4（pyvista 过滤器语义统一）同属"接口语义一致性"家族但仓库、API 面与回归面不同，四元组核对时逐题判定是否构成换皮。

**T7：pydata__xarray-4827**（repo pydata/xarray；base_commit f98d6f065db2ad1f8911cb22aa04b4e0210ecee4；触及 3 个文件：combine、concat、merge；F2P 5、P2P 167）
- 原文节选："Option for combine_attrs with conflicting values silently dropped ... It would be nice to have an option to combine attrs from all objects like "no_conflicts", but that drops attributes with conflicting values rather than raising an error. We might call this `combine_attrs="drop_conflicts"` or `combine_attrs="matching"`."
- 潜在局部决定：冲突策略语义设计、命名、三个合并入口的行为一致性（表示/建模选择）。

**T8：astropy__astropy-13075**（repo astropy/astropy；base_commit c660b079b6472920662ca4a0c731751a0342448c；触及 2 个文件；F2P 750、P2P 0）
- 原文节选："Register format ``html`` to ``Cosmology.write`` with nice mathjax ... the ``write_html(...)`` method would call ``cosmology.io.table.to_table()``, format the table to nice MathJax or something and then call the `QTable.write(..., format='html')`."
- 潜在局部决定：IO 插件注册结构遵循、MathJax 表示方案选择。注意 F2P 高达 750 且 P2P 为 0，测试面极宽，预算内完成机会需练习运行核实（入选条件之一）。

**T9：pylint-dev__pylint-8929**（repo pylint-dev/pylint；base_commit f40e9ffd766bb434a0181dd9db3886115d2dfb2f；触及 5 个文件，含 reporter 层与 options 层；F2P 156、P2P 0）
- 原文节选："Exporting to JSON does not honor score option ... The score is not outputted when exporting to JSON, not even when `--score=y` is activated. ... Expected behavior: The score is added to the JSON, at least when `--score=y` is activated."
- 潜在局部决定：score 输出口径（仅 --score=y 还是默认输出）、reporter 接口改动范围。

其余 174 题保留在 .materials-cache/swe_bench/test_shortlist_full.txt（不入库），逐题登记留到冻结前抽样程序完成；短名单不是已入选样本（总账原则 3）。

### 1.5 test 分片是否比 dev 更优：是

- **容量**：183 对 39，抽样框从"刚过最低 5"变为"远超目标 6"，备用题空间充足（第 3.4 节要求正式 3 题外加至少 2 备用）。
- **仓库多样性**：10 个仓库对 6 个；且 test 的 10 仓与 dev 的 6 仓完全不重叠，两个分片候补可以无冲突合并进同一类别 2 候选池。
- **结构多样性**：test 短名单出现了 dev 没有的决定类型组合——跨后端一致性（T1、T3）、数据结构重构（T2）、默认值与弃用策略（T4）、多 issue 合并（T5）、冲突策略语义设计（T7）；dev 的 5 个代表偏"单点行为修复加接口扩展"。
- **规模分布**：中位补丁 117 行（dev 67 行）、中位文件数更高，更接近"多文件持续工作"的准入标准 1 形态；小碎题比例更低。
- **质量注意项**：test 是官方冻结评测集（不可在调试后转正式样本的规则天然适用），且 django 扎堆需在抽样时显式控仓；这些是使用注意，不是质量减分。

结论：**test 分片在候选质量与多样性上均优于 dev，正式抽样框建在 test 分片**（待用户在 Q-D 上确认后冻结）。

## 第二部分：其余限定来源任务级复核

上一轮（candidate-sources-v0.md 沿用 execution-prep.md 1.2）在**来源级**排除了 LongBench v2、LiveBench、BIG-bench/lm-evaluation-harness。本轮按用户要求做**任务级**复核：用公开资料核对真实任务形态，确认排除是否过粗。结论先行：三个来源全部**维持排除**，且本轮给出的证据比上一轮更细；没有发现任何"需要持续工作的完整多步任务"子集。

### 2.1 LongBench v2：维持排除

公开资料（arXiv:2412.15204；THUDM/LongBench 官方仓库说明，均为免凭证公开来源）任务形态证据：

- 全基准为 **503 道四选一选择题**，6 大类 20 个子任务：单文档问答、多文档问答、长上下文语境学习、长对话历史理解、代码仓库理解、长结构化数据理解；上下文长度 8k 到 2M 词（引自论文公开摘要与官方介绍：原文表述为 "503 challenging multiple-choice questions ... six main task categories ... single-document QA, multi-document QA, long-context in-context learning, long dialogue history understanding, code repository understanding, and long structured data understanding"）。
- 可靠性机制即选择题形式（论文公开中译资料原文："为了保证评估的可靠性，LongBench v2 的所有问题都采用多项选择题的形式"）。人类专家基线是"15 分钟限时下作答一道题"的准确率（53.7%），说明任务单位就是单题作答。
- 逐类核查有无"持续工作"子集：**代码仓库理解**类虽以整个代码仓库为材料，但任务仍是对该仓库提出一个理解性问题并四选一作答——材料长不等于工作持续，没有修改、交付、外部状态或中间产物；**长结构化数据理解**类同样是"读大表答一问"。

对照六条准入标准：标准 1（本身是需要持续工作的完整任务）不满足——每题只有一个最终选择；落入 source-selection.md 第 3.6 节排除条款第一条（"只有一次回答、一个选择或一个最终数字的题"）。维持排除结论与上一轮一致；它仍可作材料池（总账原则不变，本文不改）。

### 2.2 LiveBench：维持排除

公开资料（livebench.ai；White et al., LiveBench: A Challenging, Contamination-Free LLM Benchmark, ICLR 2025；LiveBench/LiveBench 官方仓库说明）任务形态证据：

- 18 个任务、6 个类别（数学、编码、推理、语言理解、指令遵循、数据分析），每题有可验证的客观答案、自动评分不用 LLM 判官；官方说明原文要点："each question has a verifiable objective ground-truth answer ... no LLM judge"。
- 逐类任务形态（引自官方任务清单公开描述）：
  - 编码：经 LiveCodeBench 来自 Leetcode/AtCoder 的算法题加一个代码补全任务——单函数单答，评测为一次性提交；
  - 数据分析：表格格式转换（JSON/CSV/HTML 等之间）、预测两表可连接列、预测列类型标注——单轮输入、单输出、按内容精确匹配或 F1；
  - 指令遵循：按一到多条指令改写新闻文章——单轮生成加逐条遵守率检查；
  - 数学/推理/语言：竞赛题、逻辑谜题、拼写纠错等——均为单题。
- 逐类核查：数据分析类虽有真实数据集材料，但每题仍是一次性单输出（不存在"修改-再查-再改"的持续工作环，也没有外部状态可被中间决定影响）；编码类单函数题无多文件产物。

对照：同样落入第 3.6 节排除条款第一条。维持排除；作硬评分外部对照的既有定位不变。

### 2.3 BIG-bench / lm-evaluation-harness：维持排除

公开资料（google/BIG-bench 官方仓库 README 与 docs；BIG-bench 论文 arXiv:2206.04615 公开介绍）任务形态证据：

- 200+ 任务中约 **80% 为 JSON 任务**：任务数据就是一张 examples 表，每条是 `{"input": ..., "target": ...}` 或多选 `target_scores`，评测为把模型输出与目标做精确匹配或概率比较（官方 README 原文要点："JSON tasks are defined by a JSON file containing a list of examples consisting of inputs and targets"）。这是逐实例原子题的标准定义。
- 约 **20% 为程序化任务**：用 Python 编写、可与模型多轮交互、用自定义度量。本轮专门核查这一子集是否构成漏网候选：程序化任务的评测单位仍是**单个 task 实例的一次会话得分**，没有工作目录、交付物、外部状态或跨阶段产物；多轮交互只改变提问方式，不产生"需要持续工作的完整任务"结构。官方对基准的定位原文即为探测原子能力（"a collaborative benchmark intended to probe large language models"）。
- lm-evaluation-harness：任务均为单 prompt 评测配置，无多步工作形态。

对照：落入第 3.6 节排除条款第一条；且把多个原子题拼成项目违反总账原则 10。维持排除；作基础能力校准的既有定位不变。

### 2.4 复核小结

| 来源 | 上一轮（来源级） | 本轮（任务级） | 依据 |
| --- | --- | --- | --- |
| LongBench v2 | 排除 | **维持排除** | 503 题全部四选一单答；代码仓库理解类仅材料长、任务仍是单问单答 |
| LiveBench | 不入主抽样框 | **维持排除** | 18 任务全部单轮客观单答；数据分析/编码类无持续工作环 |
| BIG-bench / lm-eval | 不入主抽样框 | **维持排除** | 80% JSON 原子题；20% 程序化任务评测单位仍是单实例单会话 |

三个来源中不存在能补任何缺口的候选题；"搜透"的结论就是**限定来源内这三个来源确实无解**，不是上一轮筛得太粗。

## 第三部分：新登记来源 MiniSWE-bench 的核验（本轮追加工作）

登记表信息（上级登记，本文原样转述）：MiniSWE-bench，234 题，剔除测试文件，出自 SWE-bench 论文，HF 数据集 ID princeton-nlp/SWE-bench_MiniSWE，角色为候补补充。

> **更正（2026-08-26 溯源）**：所谓"上级登记"经溯源核查无任何书面登记实体支撑，表述不可证实；用户已否认登记，主对话领导代理也从未登记。该条目按 AI 流程内产生的、出处不明的内容对待，维持"不能用"结论；以下原核验记录保留不改写。

### 3.1 获取核验：失败，与 GAIA 同类阻塞

- 直取该 HF 数据集 ID 的元数据 API 与 parquet 镜像，均返回 **HTTP 401 Unauthorized**（2026-08-25 实测，无凭证环境，与第一轮 GAIA 的失败形态一致）。
- HF 站内搜索（MiniSWE、mini-swe-bench 等关键词）未命中任何 princeton-nlp 名下的对应数据集；princeton-nlp 名下全部 SWE 系数据集已逐一列出核对：SWE-bench、SWE-bench_Lite、SWE-bench_Verified、SWE-bench_Multimodal 及各检索增强变体，**没有 MiniSWE 条目**。
- swebench.com 官方子集清单实测核对：Full 2294、Verified 500、Bash Only（Verified 视图）、Lite 300、Multilingual 300、Multimodal 517——**不含 234 题的 MiniSWE-bench**。

### 3.2 出处核验："出自 SWE-bench 论文"未获证实

- SWE-bench 论文 arXiv:2310.06770 的 v1、v2、v3 三个版本全文（arXiv HTML 原文下载后全文检索）：**"MiniSWE" 0 处命中，"234" 0 处命中**。论文明文记载的开发集是 225 题 6 仓库（原文："225 development task instances (slightly more than 10% of the main evaluation set) collected from 6 open source repositories"），与本地 dev.parquet 的 225 条一致。
- SWE-agent 论文 arXiv:2405.15793 全文同样 0 处命中。
- 公开网络检索（多关键词组合）未发现任何对 "MiniSWE-bench" 数据集的记载。

### 3.3 结论与处置

1. **未核验，不能用**：本轮没有获取到该来源的任何一道题目或任何一份公开规格文档，六条准入标准全部无法实例级判定。按红线"搜不到就如实说搜不到"，该来源在本轮状态为：登记在册、获取失败（401，与 GAIA 同类门控/缺失）、出处声明未获证实。
2. **登记表需核对**：登记表中"234 题、出自 SWE-bench 论文"两条与可核验的公开事实不符（论文三个版本均无此名、此数）。提请用户核对登记依据；在出处澄清前，本文不把它当作可用来源计入任何核算。
3. **即便登记描述属实也不补缺口**（以下按登记表描述作方向性推演，明确标注非实测）：剔除测试文件的 SWE-bench 子集与 SWE-bench 同源同仓库同 issue，属同一来源集合——按第 3.4 节，它与 SWE-bench 合并计类别 2 上限 2，不新增正式名额；同一 instance_id 在两个数据集中只能保留一个（同一父模板条款）。剔除测试文件改变的是调试面，不是四元组：主要工作载体仍是代码文件、决定类型仍落在既有家族、反馈仍即时（仓库自身测试仍可运行）、evaluator 仍是文件/测试。因此它**补不了**静默/终局反馈格、答案/数值型 evaluator 格、类别 1 与类别 3 的缺口。

## 第四部分：总账更新（HANDBOOK 4 候选 + SWE-bench 新短名单 + 复核结论）

### 4.1 全部候选资产盘点（本轮后）

| 来源 | 状态 | 类别 1 | 类别 2 | 类别 3 | 反馈时延 | 原生 evaluator 类型 |
| --- | --- | --- | --- | --- | --- | --- |
| HANDBOOK（去重后独立结构候选约 4 个，沿用 execution-prep 1.4） | 结构已判定，运行项需实测 | 1（9b2f7a29） | 0 | 3（财务模板保留 1 + 保险疑似同模板保留 1 + d9d532c1 + f5947c33） | 全部延迟（评分层） | 外部世界状态 |
| SWE-bench（test 短名单 183 + dev 短名单 39，正式抽样框建在 test） | 元数据已获取，代表实例已评估 | 0 | 候选池充足（正式受类别 2 来源上限 2 约束） | 0 | 即时 | 文件/测试 |
| GAIA（优先） | 门控搁置（用户晚点决定账号） | 未知 | 未知 | 未知 | 未知（论文层面终局答案型） | 未知（论文层面答案/数值型） |
| MiniSWE-bench（新登记） | 获取失败（401）且出处未证实 | — | — | — | — | — |
| LongBench v2 / LiveBench / BIG-bench | 任务级复核后维持排除 | — | — | — | — | — |

### 4.2 9 题可行性重算：仍不够，上限 5 题

按第 3.4 节（同一来源集合最多 4、同一类别同一来源最多 2、每类最低 5 个合格候选）：

- **类别 1**：仅 9b2f7a29 一个。抽样框最低 5，缺口 >=4。限定来源内无任何来源能补（三个复核来源已任务级排除；MiniSWE 同源不补；GAIA 未知且已搁置）。
- **类别 2**：只有 SWE-bench 一个来源。正式最多 2/3。抽样框容量本轮后不再是问题（183 题）。
- **类别 3**：HANDBOOK 去重后约 4 个独立结构候选，受类别内来源上限 2 约束，正式最多 2/3。
- **合计**：不等 GAIA 时第一轮现实上限 = 类别 1 一题 + 类别 2 两题 + 类别 3 两题 = **5 个母任务**（与第一轮结论一致；本轮扩充了候选池但没有改变上限，因为卡上限的是来源集中度约束，不是候选数量）。

### 4.3 结构差异硬门槛逐格重算

| 门槛 | 现状 | 判定 |
| --- | --- | --- |
| 即时反馈至少 2 题 | SWE-bench 可出 2（仍须练习运行实测局部错误不被测试迭代强制洗掉，否则落 3.6 排除条款） | 有条件可达 |
| 延迟反馈至少 2 题 | HANDBOOK 3 题全部延迟 | **满足** |
| 静默或仅终局评分反馈至少 2 题 | 当前 0；限定来源内只有 GAIA 的终局答案形态可能覆盖；MiniSWE 若属实仍是即时 | **缺口：静默/终局反馈类 × 2 题，只能等 GAIA** |
| >=3 种原生 evaluator 且每种 >=2 题 | 外部世界状态（HANDBOOK 3）、文件/测试（SWE-bench 2）两种已满足；第三种"答案或数值"只有 GAIA 能提供 | **缺口：答案/数值型 evaluator × 2 题，只能等 GAIA** |
| 至少覆盖 4 种局部决定 | HANDBOOK：证据冲突处理、外部状态修改（含表示/验证混合）；SWE-bench：表示/建模选择（T1、T6、T7）、范围/优先级（T4）、验证/恢复安排（T3、T4 混合） | 五类决定全覆盖，逐题冻结标注后核实 |
| >=3 题后果经两步以上才显现 | HANDBOOK 多单元批处理结构上满足（>=2 题）；SWE-bench 多文件回归依赖（T1、T2、T3）需逐题标注 | 有望满足，需标注 |
| 任意两题四元组不同 | HANDBOOK 四元组（外部状态载体 + 证据冲突/外部状态修改 + 延迟 + 外部状态 evaluator）与 SWE-bench 四元组（代码文件 + 表示/范围 + 即时 + 文件/测试）天然不同；同类内两题靠载体差异（如 django ORM 后端 vs sympy 打印器）与决定类型差异区分，冻结时逐对核对 | 当前无冲突 |

### 4.4 哪些格只能等 GAIA、哪些格限定来源内无解

- **只能等 GAIA**（解锁后可核验填补）：静默/终局反馈 × 2 题；答案/数值型 evaluator × 2 题；类别 3 第 3 题（GAIA Level 2-3 多步多工具形态方向上对应，需获取后实测）；类别 1 补位（是否存在类别 1 形态，未获取数据不能预设）。
- **限定来源内无解**（即使 GAIA 解锁也不自动解决，需单独决策）：类别 1 抽样框凑 5 的缺口——限定来源中没有任何已核实来源以结构化记录产物为主，GAIA 是否含此类需实测；若不含，类别 1 按第 3.4 节记为尚未准备好。
- **已解决**：类别 2 抽样框容量（test 分片 183 题）；候选结构多样性（跨 10 仓库、五类决定都有实例支撑）。

### 4.5 最终判断（两种情形如实并列，供用户决策）

- **情形 A（不等 GAIA，先行）**：第一轮最多拿出 **5 题先行**配置——类别 1 一题（9b2f7a29）+ 类别 2 两题（SWE-bench test 分片抽，不同仓库）+ 类别 3 两题（HANDBOOK 去重后候选抽）。代价：不满设计规模（3 类各 3）；硬门槛中静默/终局反馈格与第三种 evaluator 格空缺；类别 1、类别 2 的抽样框均不足 5（类别 1 缺 4、类别 2 虽池大但全部同源，是否算"合格候选充足"由用户裁量）。这实质是一个缩小版 pilot，不能按原设计口径报告。
- **情形 B（结构门槛优先，等待）**：硬门槛的静默/终局反馈格与答案/数值型 evaluator 格在限定来源内确定无解，只能由 GAIA 补；若不解锁 GAIA，9 题设计规模与结构门槛**都无法满足，只能等**。本轮对三个复核来源的任务级复核与对 MiniSWE 的核验，已经把"限定来源内还有没有别的路"这个问题搜尽，结论是没有。

两种情形的共同前置（无论选哪种都先要做）：隔离问题解决（三条线共同阻塞，execution-prep Q5/Q6）、SWE-bench 即时反馈强度练习实测、HANDBOOK 环境可启动。

## 第五部分：需实测项清单（对第一轮的增量）

1. SWE-bench 正式抽样框冻结在 test 分片后，练习任务取 dev 分片（Q-D 待用户确认）。
2. test 分片代表候选的环境可启动与预算内核验（T8 的 750 条 F2P、T9 的 156 条 F2P 尤其需要）。
3. T5（多 issue 合并实例）按一题使用还是整条排除，冻结时判定并记录。
4. MiniSWE-bench 的出处澄清与获取路径（若用户确认该来源存在且能给凭证/数据，则补实例级核验；否则建议从登记表移除或标注"未证实"）。
5. 第一轮遗留的全部实测项（GAIA 获取、即时反馈强度、分叉可行性等）不变，见 candidate-sources-v0.md 第五部分。

## 第六部分：开放问题

- **Q-D（延续，本轮给出证据）**：正式抽样框建在 test 分片（183 题候选池）、练习任务用 dev 分片。证据已备，待用户拍板。
- **Q-F（新）**：MiniSWE-bench 登记出处存疑（论文无记载、HF 无数据集、官方子集无此项）——请用户核对登记依据；澄清前该来源不计入任何核算。**更正（2026-08-26 溯源）**：仓库内无任何书面登记实体，"上级登记"不可证实；用户已否认登记；该条目按 AI 流程内产生的出处不明内容对待，维持"不能用"结论，本问题按已澄清关闭。
- **Q-G（新）**：先行还是等待（第 4.5 节情形 A 与情形 B），需用户决策。本文档只提供证据，不代选。
- **Q-A、Q-B、Q-C、Q-E**：延续 candidate-sources-v0.md 第六部分，无变化（Q-A 即 GAIA 门控，用户已表示晚点决定）。

## 附录：证据与存放位置

- 本地数据与脚本（.materials-cache/，.gitignore 第 14 行覆盖，不入库）：
  - SWE-bench：swe_bench/dev.parquet、swe_bench/test.parquet（第一轮下载，本轮复用，未重新下载）；
  - 本轮脚本：analyze_test_round2.py（test 全量过筛，dev 复现 39 题作一致性检查）、round2_representatives.py（9 个代表候选原文导出）、fetch_miniswe.py / find_miniswe.py / find_miniswe2.py（MiniSWE HF 核验）、check_miniswe_paper.py / check_paper_v1.py / grep_234.py（SWE-bench 论文三版本全文检索）、check_miniswe_agent.py（SWE-agent 论文检索）；
  - 中间产物：swe_bench/test_shortlist_full.txt（183 题全清单）、swe_bench/round2_representatives.txt（代表候选原文）、swebench_paper_v3.html（论文原文存档备查）、mini_matches.txt、miniswe_agent_matches.txt。
- 公开资料（均免凭证获取）：
  - SWE-bench 论文 arXiv:2310.06770 v1/v2/v3（全文检索 "MiniSWE"/"234" 均 0 命中；开发集 225 题记载原文见正文）；
  - SWE-agent 论文 arXiv:2405.15793（全文检索 "MiniSWE" 0 命中）；
  - swebench.com 官方子集清单（Full 2294 / Verified 500 / Lite 300 / Multilingual 300 / Multimodal 517，无 MiniSWE）；
  - HF API 实测：princeton-nlp/SWE-bench_MiniSWE 元数据与 parquet 均 401；princeton-nlp 名下 SWE 系数据集全清单无 MiniSWE；
  - LongBench v2：arXiv:2412.15204 公开摘要与官方仓库介绍（503 道四选一、6 类 20 子任务、全选择题可靠性设计）；
  - LiveBench：livebench.ai 与 ICLR 2025 论文公开信息（18 任务 6 类、每题客观单答、不用 LLM 判官、任务清单逐类形态）；
  - BIG-bench：google/BIG-bench 官方 README（约 80% JSON 任务 input/target 原子格式、约 20% 程序化任务单实例评测）与 arXiv:2206.04615 公开介绍。
- 本仓库文档：docs/subtask-dilution/design.md、source-selection.md、execution-prep.md、candidate-sources-v0.md、docs/research-ledger.md。
- 本轮未运行任何被测代理，未产生任何模型行为数据；全部"需实测"条目均未写成结论；全部题目内容原样引用自真实数据集，无 AI 编写或改写。
