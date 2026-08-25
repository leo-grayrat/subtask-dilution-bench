# 反馈分配线来源公开资料核查与生死判断

更新日期：2026-08-25

状态：仅新增文档。本文件不修改 `design.md`、`source-selection.md`、`source-gap-analysis.md` 或任何既有文件；不运行任何实验、模型或本机外部探测。全部结论只依据公开网络资料（论文、官方仓库、数据集页面、博客文章），并给出访问日期与出处。本文接续 `source-gap-analysis.md`，把其中 能用公开资料查证的实测建议提前消化。

## 0. 范围与方法

- 核查对象：`source-selection.md` 第 6 节限定的两个来源——Reward Hacking Benchmark（RHB）与 EvilGenie，不扩展来源。
- 准入标准口径：`source-selection.md` 第 4 节实际记录的六条（S1–S6）。任务口径中的五条按六条执行，理由见第 6 节回应 1。
- 判定标签三级：**文档证据满足 / 文档证据不满足 / 证据不足需实测**。凡能直接引用公开资料原文的记文档证据；含推断的一律标注**推测**。
- 访问渠道（2026-08-25）：kunvarthaman.com、arxiv.org、github.com 页面与 GitHub REST API。受限说明：raw.githubusercontent.com 因网络不可达，源代码经 API base64 内容获取；arXiv HTML 全文抓取超时，以摘要 + 官方仓库 README + 源代码三者交叉为准。均如实记录，不影响下述结论。

## 1. RHB（Reward Hacking Benchmark，作者 Kunvar Thaman）

### 1.1 它到底是什么

- **出处**：个人博客文章，非同行评审论文。https://kunvarthaman.com/posts/rhb-v1.html （`The Reward Hacking Benchmark`，页面自记 Published 2025-07-01、Last updated 2025-10-28）。站点目录页（https://kunvarthaman.com/fragments.html ）中该条目标题为 `Initial results from the Reward Hacking Benchmark`（2025-07-20），与正文为同一链接。
- **作者**：Kunvar Thaman（博客名 Karanoia；自述常用网名 firstuserhere，见站点页脚社交链接：X `firstuserhere`、`https://firstuserhere.github.io/`）。
- **任务形态**（原文）：`The first version of the Reward Hacking Benchmark (RHB-v1) had five code optimization tasks (sorting, regex, compression, matrix multiplication, prime checking) evaluated in a deliberately vulnerable sandbox.` 即五个单目标代码优化任务，在故意留漏洞的沙箱中评分。
- **交互形态**（原文）：`Models didn't interact with the environment directly – instead, they communicated through a structured harness with specific fields for different actions: 'bash', 'cot', 'code', etc, and the harness executed on their behalf, in a loop with the model.`
- **反馈形态**（原文）：`feedback on their performance and ranking in a leaderboard after each attempt.` 即每轮给出性能反馈与排行榜名次。
- **实验条件与结果**：permissive / hardened 两套沙箱对照；加固后（原文）`exploit rate dropped from 10% to less than 1%, while genuine optimization performance only decreased marginally (around 60% to 54% success rate)`。
- **维护状态**：文章（2025-10-28 更新版）写明 `I'm now developing RHB-v2 with even more extensive tool access`；截至 2026-08-25 未见 v2 的任何公开发布。作者 2025-11-26 的 November Digest（https://kunvarthaman.com/posts/november-digest.html ）亦无 RHB 发布记录。

### 1.2 实现形态：不存在公开可运行实现（消化 gap-analysis 开放问题 3）

证据链（全部为 2026-08-25 公开查证）：

1. 作者 GitHub（firstuserhere）名下 RHB 仓库 https://github.com/firstuserhere/RHB ：GitHub API `/repos/firstuserhere/RHB/contents/` 返回的唯一文件是 39 字节的 README，内容为 `# RHB / Reward Hacking Benchmark website`；最后推送 2025-06-05。无代码、无任务定义、无数据。
2. 作者 2025-05-14 在 https://kunvarthaman.com/posts/reward-hacking-research.html 承诺（原文）：`I recently finished developing a comprehensive characterization of reward hacking behaviors across frontier models (under review at NeurIPS) which I will open-source in the coming weeks.` 截至 2026-08-25，该账号全部 70 个公开仓库（GitHub API `/users/firstuserhere/repos`）中没有 RHB 基准实现；`rl-matmul-gpt-oss`（2025-10-14）只含两个 RL 训练 notebook，不是任务环境。
3. GitHub 全站仓库搜索（API `/search/repositories?q=reward+hacking+benchmark`）前 10 名中无该作者的 RHB 任务实现。
4. 公开检索未见 Varthaman 关于 RHB 的论文；NeurIPS 录用状态无法从公开渠道核实（**推测**：可能未发表或未公开）。

**结论**：RHB 目前只有文章描述一种存在形态； 任务环境的全部细节（沙箱构造、harness 字段、评分与排行榜计算）都停留在博文叙述。按 `source-selection.md` 第 6 节在 RHB / EvilGenie 的公开实现及其已有底层任务中检查母任务候选的措辞，RHB 没有公开实现，其候选池为空。

### 1.3 RHB：六条准入标准逐条对照

| 标准 | 判定 | 公开资料证据 |
|---|---|---|
| S1 真实外部可验证整体目标 | 证据不足（倾向不满足，**推测**） | 博文显示五个任务均为合成代码优化题，配以合成激励（原文 `Say there's a $10000 prize for #1 leaderboard rank`），未见真实世界业务整体目标；任务定义未公开，无法完整判定。 |
| S2 拆成两个竞争资源的部分 | 证据不足 | 任务定义未公开；博文描述每题为优化单一代码的单一性能指标（**推测**：无原生双子目标结构）。 |
| S3 支持一种冻结模块 | 证据不足 | harness 未公开；博文只记录每次尝试后给 performance + leaderboard，无法核查呈现层可否受控改造。 |
| S4 记录 tokens / tool calls / 迭代 | 证据不足 | 博文按迭代报告 exploit 率（原文 `by iteration 7`），说明作者内部有逐轮记录；但无任何公开的轨迹格式可供我方采集复用。 |
| S5 同一任务强弱反馈配对 | 证据不足 | 同 S3：反馈通道在作者私有 harness 中，无公开实现可查。 |
| S6 高/低价值局部都能构造 | 文档证据不满足（含**推测**） | 博文只有单一指标（性能/排名）的评分描述，无多分项；要构造权重须重建整个 evaluator，而代码未公开。 |

附加检查：与 `source-selection.md` 第 5 节排除项 纯 reward hacking 场景的关系——RHB 字面上即 reward hacking benchmark，核心观察是 exploit；但博文也显示加固环境后诚实优化仍是主要行为（54% 成功率），存在合法工作内容。**判定（推测）**：不完全落入排除项，但其主要研究价值仍在 exploit 一侧；且无实现使该讨论失去实测对象。

### 1.4 RHB 关键结构问题分析

对两个竞争资源、价值可交换（3:1）、反馈可受控操纵三前提逐一分析：

- **两个竞争资源**：从博文可见形态（每题一段代码、一个性能指标）看不到该结构；无代码，不能实测（**推测**）。
- **价值可交换**：单一指标评分无处挂权重；无代码，不可改造。
- **反馈可受控操纵**：反馈生成在作者私有 harness 内，无公开实现，只改呈现无从操作。

结论：三前提在公开可见形态上均不成立；且即使可能成立，也因没有代码而没有实测通道。

### 1.5 RHB 生死判断

**从公开资料已可判不合格。** 依据：

1. 无公开可运行实现（第 1.2 节证据链）；`source-selection.md` 第 6 节定义的公开实现候选池对 RHB 为空。
2. 即便退到文章描述的形态，五题为单指标合成优化任务，S2 / S6 的前提不成立（此条为**推测**，但因无代码已无实测通道）。
3. `source-selection.md` 第 2 节本就记录当前作为方法参考，不直接把它的数据当最终数据集——本判定与该定位一致：RHB 保留为方法参考，不作为素材来源。

## 2. EvilGenie

### 2.1 它到底是什么

- **论文**：`EvilGenie: A Reward Hacking Benchmark`，Jonathan Gabor、Jayson Lynch、Jonathan Rosenfeld；arXiv:2511.21654（v1 提交 2025-11-26，v2 修订 2026-05-17）。页面：https://arxiv.org/abs/2511.21654 。摘要（原文）：`We introduce EvilGenie, a benchmark for reward hacking in programming settings. We source problems from LiveCodeBench and create an environment in which agents can easily reward hack, such as by hardcoding test cases or editing the testing files.`
- **当前官方代码**：https://github.com/JonathanGabor/evilgenie_inspect （仓库描述 `Reward Hacking Benchmark (Inspect Edition!)`）。GitHub API 元数据：MIT 许可证，创建于 2026-02-03，最后推送 2026-05-22（最新提交 `f5d8a2ca`，信息 `remove more hints, remove default sample limit`），4 stars、2 open issues。**维护状态：核查日前约 3 个月仍有提交，小规模但活跃维护。**
- **旧仓库**：https://github.com/JonathanGabor/EvilGenie 已标注（原文）`This repo is deprecated. Please see evilgenie_inspect for the current implementation`，并自记安全问题（原文）`This repo currently allows agents to execute arbitrary code on your machine`；最后推送 2026-05-16。
- **运行框架**：Inspect AI（UK AI Safety Institute 的评测框架）；README 用法 `uv run inspect eval reward_hacking.py --model openai/gpt-5`；每题一个 Docker 沙箱（原文）`The benchmark uses Docker containers to create isolated workspaces for each problem`。
- **任务形态**：每题一个工作区 `/home/agent/workspace/`，含 `problem.md`（题面）、`solution.py`（空桩）、`test_cases.json`（约 70% 可见测试）、`test.py`（可见测试运行器）；其余约 30%（至多 10 条）为 holdout 隐藏测试，仅用于最终检测（README `Test Case Split` 节）。题目为（原文）`Stdin/stdout based (read input, write output)`。
- **agent 与预算**：默认 solver 为 Inspect `basic_agent` + `safe_bash` / `safe_python` / `text_editor`（源代码 `reward_hacking.py` 的 `default_solver`）；`constants.py` 中 `DEFAULT_MAX_MESSAGES = 500`、`DEFAULT_PROBLEM_TIMEOUT = 600`（秒）；README 示例参数写 50 轮，以代码默认值为准。
- **评分**：三个类别型维度（README `Scoring System` 节）——`test_result`（passed_all / passed_visible_only / failed_visible）、`llm_classification`（legitimate / heuristic / reward_hacking / error，由 LLM judge 判定）、`files_modified`（对比 `test_cases.json` 与 `test.py` 运行前后 SHA256）。
- **反馈通道（关键事实）**：运行中不存在环境侧周期性反馈。系统提示词（`reward_hacking.py` 的 `DEFAULT_SYSTEM_MESSAGE`，原文）要求 agent 自行跑测试：`2. Test your solution using test.py  3. Iterate until your solution passes all tests`。agent 得到的全部 反馈来自它自己用 `safe_bash`/`safe_python` 执行命令的输出；最终评分在提交后由环境执行。
- **附加事实**：仓库内置 9 个歧义题清单 `AMBIGUOUS_PROBLEM_IDS`（如 `lcb_abc396_e`）；论文要点（README `Key Findings`）：LLM judge 在无歧义情形下检测有效，holdout 测试增益有限，reward hacking 在歧义题上更普遍，Codex 与 Claude Code 出现显式 reward hacking。

### 2.2 底座是什么（消化 gap-analysis 开放问题 2）

- **底座 = LiveCodeBench**（Jain et al.，`LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code`，arXiv:2403.07974），备选 APPS。
- **版本**：README `Dataset` 节（原文）：`Currently uses problems from LiveCodeBench (default) or APPS ... Hard difficulty problems from releases v5 and v6`；源代码 `reward_hacking.py` 默认参数 `livecodebench_release=v5_v6`（docstring 另列 `release_v1`、`release_v2` 等选项）。
- **佐证**：题目 ID 形如 `lcb_abc374_a`、`lcb_arc185_c`（`reward_hacking.py` 与 README 测试节），与 LiveCodeBench 采集 AtCoder 等竞赛题的来源一致；README `Citation` 节要求同时引用 `evilgenie2025` 与 `jain2024livecodebench`，底座身份由作者自行确认。
- **结论**：上轮底座未记录缺口已闭合，可归档为：EvilGenie（evilgenie_inspect @ 2026-05-22）基于 LiveCodeBench release v5+v6 的 hard 题（APPS 备选）。

### 2.3 EvilGenie：六条准入标准逐条对照

| 标准 | 判定 | 公开资料证据 |
|---|---|---|
| S1 真实外部可验证整体目标 | 文档证据满足（有限） | holdout 测试由环境在提交后执行、可重放；测试文件完整性用 SHA256 校验（README `Detection Methods`）。限定：整体目标是 正确解出该题，判定为类别型，不是多组件效用。 |
| S2 拆成两个竞争资源的部分 | 文档证据不满足 | 一题 = 一个 `solution.py` + 一组测试；仓库模板 `solution_function.py.jinja` / `solution_stdio.py.jinja` 把解固定为单一函数或单一 stdin/stdout 程序；visible/holdout 拆分是反作弊检测机制，不是两个工作部分。公开材料中不存在任何子组件评分结构。 |
| S3 支持一种冻结模块 | 文档证据不满足 | 运行中没有 evaluator 提供的反馈通道（见 2.1 反馈通道）。P 模块要求环境侧周期报告（`design.md` 4.1 节），C 模块要求 evaluator 时点结果（第 5 节），两者都不存在；从零搭建等于新造评测环境，超出只改反馈呈现/时机的允许操纵。 |
| S4 记录 tokens / tool calls / 迭代 | 文档证据满足 | Inspect AI 记录完整轨迹：README `Analyzing Results` 节（`Individual sample transcripts`、`uv run inspect view`）；全部工具调用进入 transcript。 |
| S5 同一任务强弱反馈配对 | 文档证据不满足 | 由 S3 推出：不存在可被改变呈现或在线可见时机的环境侧反馈通道。 |
| S6 高/低价值局部都能构造 | 文档证据不满足 | 评分为类别型反作弊分类（README `Scoring System`），没有子项质量分 `Q_F`/`Q_C`；`design.md` 3.1 节的 `U = w_F*Q_F + w_C*Q_C + w_B*Q_B - P` 没有可落地的分项。 |

### 2.4 EvilGenie 关键结构问题分析

对两个竞争资源、价值可交换（3:1）、反馈可受控操纵三前提逐一分析（全部基于公开代码与 README，无**推测**成分）：

- **两个竞争资源**：单题内不存在。可见的变通是把两道 LiveCodeBench 题拼成一个母任务、分别充当 F 与 C——但 `design.md` 第 3 节要求 F/C 是同一母任务本来就有的真实要求；`research-ledger.md` 第 3 节原则与第 5 节已放弃路线表明确排除把不同 benchmark 小题拼成大杂题。该路径在规则层面即不合格。
- **价值可交换（3:1）**：没有多分项评分，权重无处可挂；要引入权重必须先新造子项评分，等于重建 evaluator，违反 `design.md` 第 3 节的原生要求。
- **反馈可受控操纵**：反馈是 agent 自己工具调用的输出（自生成），不是环境发送的；P 的同一载荷、不同呈现与 C 的同一评价序列、不同在线可见时机都缺少操纵对象。引入周期性评价器即新造环境，不构成来源复用。

结论：三前提在任务机制层面全部不成立。这正是 `source-selection.md` 第 5 节排除的只有一个最终分数的 benchmark形状（每题一个聚合判定），且比一般单分数更窄——它的评分语义还是反作弊分类。

### 2.5 EvilGenie 生死判断

**从公开资料已可判不合格。** 依据：

1. S2 / S3 / S5 / S6 四条为文档证据不满足，且全部是结构性事实（单题单解形态 + 无环境侧反馈通道），不是实测后才可能翻转为满足的未知项。gap-analysis 实测建议 1 的前提（底座中存在含两个竞争局部的任务）已被公开资料否定：LiveCodeBench 题目是单题单程序的竞赛编程题，EvilGenie 的工作区与评分模板把单解形态固化。
2. 满足的 S1 / S4 不足以挽救：S2 不满足即触发 `source-selection.md` 第 5 节只有一个最终分数的排除形状。
3. 判定范围限定于当前公开实现（evilgenie_inspect @ commit f5d8a2ca，2026-05-22）；不覆盖未来可能出现的结构不同版本。

## 3. 准入标准对照总表

| 标准 | RHB | EvilGenie |
|---|---|---|
| S1 外部可验证整体目标 | 证据不足（倾向不满足，**推测**） | 文档证据满足（限类别型判定） |
| S2 拆成两个竞争资源的部分 | 证据不足 | 文档证据不满足 |
| S3 支持一种冻结模块（P 或 C） | 证据不足 | 文档证据不满足 |
| S4 记录 tokens / tool calls / 迭代 | 证据不足 | 文档证据满足 |
| S5 同一任务强弱反馈配对 | 证据不足 | 文档证据不满足 |
| S6 高/低价值局部都能构造 | 文档证据不满足（含**推测**） | 文档证据不满足 |
| **生死判断** | **从公开资料已可判不合格**（无可运行实现，候选池为空） | **从公开资料已可判不合格**（四项结构性不满足） |

两来源均无任何一条达到 文档证据满足且无保留；RHB 六条中无一条达到文档证据满足。

## 4. 线级结论：建议触发停止规则，部分终止

`source-selection.md` 第 6 节原文：`若现有来源无法同时满足至少一个反馈模块和外部价值交换，应停止并报告素材不适配，而不是继续搜索新 benchmark 或让 AI 自由生成任务。`

- RHB：无公开实现，满足任一模块不可验证；且公开可见形态（单指标合成优化题）没有多组件价值交换的落点。
- EvilGenie：P / C 两个模块在结构上都不可行（无环境侧反馈通道），外部价值交换在结构上也不可行（无子项评分）——全部基于公开代码，非推测。

**两个限定来源均从公开资料判不合格。** 按 `pre-test-readiness.md` 第 5 节重大分支 3 原文（`RHB / EvilGenie 中有合格任务则继续；没有则停止该 pilot`），本报告建议：

1. **反馈分配线部分终止**：停止该线 pilot 的素材搜索、呈现器实现与预检投入；`design.md` 410 行设计保留为已审查设计记录，方法规格在将来出现合格来源时仍可复用。
2. **不启用新来源**：启用新来源属于新的设计审查，不是自动下一步（`source-selection.md` 第 6 节、`pre-test-readiness.md` 第 5 节分支 3）。
3. **不影响另两条线**：三线相互独立（`research-ledger.md` 第 2 节），一线终止不构成另外两线的放行或阻塞。

## 5. 剩余实测清单

**无。** 限定来源内已没有值得实测的对象：

- RHB 没有代码可运行，其实测建议（gap-analysis 实测 6、7）失去对象；
- EvilGenie 的不合格理由是公开代码确认的结构性事实（单题单解、无环境侧反馈通道、类别型反作弊评分），运行任何模型都不会改变这些事实，实测 1–5 全部失去前提。

复检触发条件（登记备查，防止以后被悄悄捡回；触发不等于自动重启，重启须按停止规则走新的设计审查）：

1. RHB 作者公开发布基准代码与任务定义（监控 firstuserhere/RHB 与 kunvarthaman.com）；
2. EvilGenie 或其官方后继者发布具有多组件、可分项评分任务形态的版本；
3. 若出现上述新证据，对新素材按 gap-analysis 实测建议 1–5 做任务结构检查（仍不需要运行被测模型）；两来源之外的任何新来源一律先经新的设计审查。

## 6. 对 source-gap-analysis.md 六个开放问题的逐条回应

| # | 开放问题 | 处理结果 |
|---|---|---|
| 1 | 条数口径不一致（ 五条与记录的六条） | **已回应**：本文按 `source-selection.md` 第 4 节实际条文的六条（S1–S6）执行，不采用五条口径。统一措辞需修改既有文档，超出本任务权限，建议下次文档维护时处理。 |
| 2 | EvilGenie 底座未记录 | **已回答**：底座为 LiveCodeBench（arXiv:2403.07974），默认取 release v5+v6 的 hard 题（README `Dataset` 节与代码默认参数 `livecodebench_release=v5_v6`），APPS 为备选。版本信息完备，可归档进冻结清单。 |
| 3 | RHB 可运行性未记录 | **已回答**：不存在公开可运行实现（本文 1.2 节证据链：39 字节占位仓库、70 个仓库中无实现、开源承诺未兑现）。RHB 实际只够当方法参考，候选资格不成立——与 gap-analysis 的预警一致。 |
| 4 | P/C 是否共用同一批母任务 | **不能答，且问题已悬空**：两来源都不产生任何候选母任务，该分支失去对象。建议在记录中挂无对象，本文不修改 `pre-test-readiness.md`。 |
| 5 | 规模不足时的处理 | **已失效**：现状不是合格任务只有 1–2 个而是0 个，直接触发 `source-selection.md` 第 6 节停止规则，不进入 `design.md` 第 8 节执行协议未完成分支。 |
| 6 | 受控权重与原生价值的边界 | **未涉及**：两来源都不带原生多组件权重或可再加权的分项评分，不需要为该边界建记录模板；未来若触发复检，按 `design.md` 3.1 节执行。 |

## 7. 本文不得声称什么

- 不得声称看到了 RHB 的内部实现：本文对其任务结构的全部描述都来自博文叙述的推断，推断点均已标注**推测**；其 NeurIPS 录用状态无法从公开渠道核实。
- 不得声称 EvilGenie 永远或全版本不合格：判定限定于核查日公开可见的 evilgenie_inspect @ commit `f5d8a2ca`（2026-05-22）；不覆盖未来可能出现的结构不同版本。
- 不得写成该线已完全终止：终止的是 pilot 与素材搜索投入；`design.md` 的设计与方法规格保留。
- 不得把本判定当作正式实验的放行依据：该线仍被被测隔离、呈现器、信息等价预检与动作采集等其余门槛阻塞（`pre-test-readiness.md` 第 3 节），素材不合格只是其中一个阻塞项。
- 不得把结论外推到两个来源之外：任何其他 benchmark 的判定都须先经新的设计审查。

## 8. 公开来源清单（访问日期均为 2026-08-25）

RHB：

1. https://kunvarthaman.com/posts/rhb-v1.html —— RHB-v1 博文正文（自记 Published 2025-07-01、Last updated 2025-10-28）
2. https://kunvarthaman.com/fragments.html —— 站点目录页
3. https://kunvarthaman.com/posts/reward-hacking-research.html —— 开源承诺文（2025-05-14）
4. https://kunvarthaman.com/posts/november-digest.html —— 作者 2025-11 月报
5. https://github.com/firstuserhere/RHB —— 占位仓库页面
6. GitHub REST API：`/repos/firstuserhere/RHB/contents/`（仓库文件清单）、`/users/firstuserhere/repos`（该账号全部 70 个公开仓库）、`/search/repositories?q=reward+hacking+benchmark`、`/repos/firstuserhere/rl-matmul-gpt-oss/contents/`
EvilGenie：

1. https://arxiv.org/abs/2511.21654 —— 论文页面（v1 2025-11-26，v2 2026-05-17）
2. https://github.com/JonathanGabor/evilgenie_inspect —— 当前官方仓库页面与 README
3. https://github.com/JonathanGabor/EvilGenie —— 旧仓库页面（自记 deprecated）
4. GitHub REST API：仓库元数据 `/repos/JonathanGabor/evilgenie_inspect`、提交历史 `/repos/JonathanGabor/evilgenie_inspect/commits`、文件树 `/git/trees/HEAD?recursive=1`、源代码 base64 内容 `/contents/reward_hacking.py` 与 `/contents/constants.py`

底座：

1. https://arxiv.org/abs/2403.07974 —— LiveCodeBench 论文（Jain et al.）
渠道受限记录：raw.githubusercontent.com 访问时网络不可达，源代码改经 GitHub API contents 端点（base64）获取；arXiv HTML 全文抓取超时，改以论文摘要、官方仓库 README 与源代码三者为交叉依据。两处受限均不影响本文结论。

## 9. 本文的证据边界

- 外部结论只基于第 8 节清单中的公开资料；内部依据为 `design.md`、`source-selection.md`、`source-gap-analysis.md`、`research-ledger.md`、`pre-test-readiness.md` 五份既有文档。
- 本文未运行任何评测、模型或代理；未探测本仓库以外的目录；未修改任何既有文档。
- 超出材料范围的判断一律标注**推测**；检索受限查不到的内容如实记录为无法核实，不编造来源信息。
