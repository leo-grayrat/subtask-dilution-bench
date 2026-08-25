# 子任务稀释：候选来源登记与材料获取评估（v0）

日期：2026-08-25

这份文档接续 execution-prep.md：它记录一条用户已拍板的新决策（跨线复用），并报告对两个限定来源（GAIA、SWE-bench）的真实材料获取与候选评估结果。本文档只做记录与评估：不修改任何既有文档与既有决定，不新增来源，不运行任何被测代理，不运行任何模型实验。全部题目信息原样引用自真实数据集，不含任何 AI 编写或改写的任务内容。

## 0. 准入回答（按 research-ledger.md 第 8 节）

1. 属于子任务稀释研究线。
2. 补总账第 6 节该线缺口：母任务抽样框尚未形成（execution-prep.md 第 1.5 节的类别 1/2/3 缺口与硬门槛可行性）。
3. 保留总账第 3 节原则：不从空白编造任务（原则 1）；不把换皮当多样性（原则 2）；候选不是样本量（原则 3）；不预先围绕已知错误挑 checkpoint（原则 8）；不把现成 benchmark 拆成小题拼凑（原则 10）；不因新来源有趣而改变研究问题（原则 11）；工程获取结果不写成模型行为结论（原则 12）。
4. 不修改任何既有决定；记录一条用户新决策（第一部分），它回答 execution-prep.md 开放问题 Q1。研究总账第 9 节决策记录区未来应同步登记该决策（本任务红线为不修改既有文档，故只在此注明）。
5. GAIA 与 SWE-bench 扮演的角色是母任务材料来源；两者均为 source-selection.md 第 5 节已登记来源，不新增来源。
6. 不做这项工作：抽样框缺口无法量化，9 题与结构差异硬门槛是否可达成无法判断，该线无法进入冻结流程。

## 第一部分：决策记录

### 决策 2026-08-25：允许题源跨研究线复用（回答 execution-prep.md 开放问题 Q1）

- **决策内容**：三条研究线由不同的被测模型分别执行，因此不同研究线共用同一批题源（如 HANDBOOK）不构成污染，跨线复用被允许。
- **理由**：污染风险的前提是同一被测模型在一批题上既被训练/暴露又被评测，或同一模型的跨线结果互相串扰。三条线使用不同被测模型时，一个模型在某线上见过或做过 HANDBOOK 任务，不影响另一条线上另一个模型的测量有效性。
- **决策者**：用户（明确拍板）。
- **日期**：2026-08-25。
- **解决的问题**：execution-prep.md 开放问题 Q1（HANDBOOK 任务跨线复用的允许性）。按该文档记录，若排除已被上下文整合线占用的任务，本地可用候选只剩 4dace65e 一题；本决策使本地候选从 1 个恢复为去重后最多 4 个（158b9045、a0895480、4dace65e 三题疑似同模板按规则保留一个，加 d9d532c1、f5947c33、9b2f7a29 中的独立结构项，去重后可保留约 4 个，与 execution-prep.md 第 1.4 节判定一致）。
- **边界说明**：本决策不改变 design.md 第 13 节的禁令——子任务稀释线仍不得用上下文整合线的局部/完整规则题替代本线的 checkpoint-fork 实验。本线使用的仍是 HANDBOOK 原生完整任务本身，不是规则题衍生物。
- **遗留**：execution-prep.md Q1 中提到的隔离办法（匿名包混淆、盲评材料重叠、评分器语义串扰）属于跨线复用的操作性风险，允许复用不等于这些风险消失；隔离办法本身未冻结，列入本文档第六部分开放问题。

## 第二部分：材料获取情况

获取日期：2026-08-25。获取环境：Windows + Python 3.13.5，直连 HuggingFace API 与 parquet 镜像，未使用代理账号。下载约束：只取元数据与题目描述层级数据，单次下载超 200MB 即停止；实际全部下载均远低于该上限。样本数据存放于 .materials-cache/（已补入 .gitignore 第 14 行并验证被忽略），文档只引用题目级信息。

### 2.1 GAIA（优先来源）：获取失败，门控拦截

**尝试的三条路径（全部失败，均为 HTTP 401 Unauthorized）**：

1. parquet 直取（validation 与 test 两个分片）：
   - https://huggingface.co/api/datasets/gaia-benchmark/GAIA/parquet/2023_all/validation/0.parquet → 401
   - https://huggingface.co/api/datasets/gaia-benchmark/GAIA/parquet/2023_all/test/0.parquet → 401
2. datasets-server 行级 API：
   - https://datasets-server.huggingface.co/rows?dataset=gaia-benchmark%2FGAIA&config=2023_all&split=validation&offset=0&length=1 → 401
3. 数据集 README 原文：
   - https://huggingface.co/datasets/gaia-benchmark/GAIA/raw/main/README.md → 401

**门控状态核实**：HuggingFace 数据集 API 返回 gated=auto、private=False，即该数据集要求登录用户同意使用条款后才放行数据访问。本机无 HF 凭证（HF_TOKEN 未设置，~/.cache/huggingface/token 不存在）。因此 401 不是网络故障，而是授权缺口。

**已获取的部分（仅公开元数据，非题目内容）**：

- 数据集标识：gaia-benchmark/GAIA，lastModified 2025-10-28，tags 含 size_categories:n<1K、format:parquet、modality:audio/document/image/text、arxiv:2311.12983；
- 分片结构：2023_all、2023_level1、2023_level2、2023_level3 四个 config，每个含 test 与 validation 分片；
- 公开论文层面的规模描述（引自 Mialon et al., GAIA: a benchmark for General AI Assistants, arXiv:2311.12983, ICLR 2024，经公开网络来源核对）：共 466 题，其中 166 题开发集带答案、300 题测试集不公开答案；Level 1 为少于 5 步且工具最少的题，Level 2 为 5-10 步、多工具协调的题，Level 3 为长链条、多工具集成的题；评分为对最终短答案的准精确匹配。
- 以上论文数字标注为公开来源信息，不是本次实际拉取的数据；本次没有获取到任何一道 GAIA 题目的内容。

**处置**：按任务红线，不寻找替代来源。GAIA 实例级候选评估无法进行，全部标记为需获取后实测。是否解除门控属于用户级决策（需要 HF 账号并同意数据集条款），列入第六部分开放问题。

### 2.2 SWE-bench：获取成功

**获取方式**：HuggingFace 公开数据集 princeton-nlp/SWE-bench（default config）的 parquet 镜像，直取 dev 与 test 两个分片的完整实例元数据。

**数据量与存放**：

| 分片 | 字节数 | 实例数 | 本地路径 |
| --- | --- | --- | --- |
| dev | 1,382,594（约 1.35MB） | 225 | .materials-cache/swe_bench/dev.parquet |
| test | 12,097,227（约 11.5MB） | 2294 | .materials-cache/swe_bench/test.parquet |

合计约 12.9MB，远低于 200MB 上限。train 分片（约 107MB，同样低于上限）未下载：dev 与 test 已完整覆盖可用作候选评估与练习任务（dev）和正式抽样（test）的实例，train 对本线无用。仓库镜像一律未拉取（遵守只取元数据的约束），因此所有环境相关判断均标记需实测。

**字段结构（逐字段核对）**：每条实例含 12 个字段：repo、instance_id（稳定任务 ID，格式为 组织__仓库-议题号）、base_commit、patch（参考修复补丁）、test_patch（测试补丁）、problem_statement（完整 GitHub issue 原文，含复现步骤）、hints_text、created_at、version、FAIL_TO_PASS（修复后应由失败转通过的测试清单，JSON）、PASS_TO_PASS（不得回归的测试清单，JSON）、environment_setup_commit。

**任务群体统计（实测自所下载元数据）**：

| 指标 | dev（225） | test（2294） |
| --- | --- | --- |
| 覆盖仓库数 | 6 | 12 |
| dev 仓库分布 | pvlib 63、pydicom 56、sqlfluff 50、astroid 31、pyvista 16、marshmallow 9 | — |
| test 仓库分布 | — | django 850、sympy 386、scikit-learn 229、sphinx 187、matplotlib 184、pytest 119、xarray 110、astropy 95、pylint 57、requests 44、seaborn 22、flask 11 |
| patch 行数（中位 / p90 / 最大） | 67 / 359 / 1119 | 34 / 153 / 7008 |
| 触及文件数（中位 / 最大） | 1 / 38 | 1 / 31 |
| 触及 >=2 个文件的实例 | 101 | 569 |
| FAIL_TO_PASS >= 3 的实例 | 96 | 552 |
| patch 只改测试文件的实例 | 0 | 119 |
| FAIL_TO_PASS 数量（均值 / 范围） | 20.9 / 1-890 | 9.0 / 1-1630 |

**版本与出处**：数据集 princeton-nlp/SWE-bench，来源论文 Jimenez et al., SWE-bench: Can Language Models Resolve Real-World GitHub Issues?, arXiv:2310.06770（与 source-selection.md 第 5 节登记一致）。许可证信息未能从本次获取中核实（未下载仓库文件），列入需实测/需核查项。

## 第三部分：候选评估

### 3.1 来源级评估（按 source-selection.md 第 2 节六条准入标准）

**SWE-bench**：

| 标准 | 判定 | 依据 |
| --- | --- | --- |
| 1 完整持续工作 | 结构上满足 | 每实例是真实仓库上的完整 issue 修复工作：读代码、定位、修改、过测试；非单次问答 |
| 2 自然产生多个局部判断 | 多数实例满足，逐实例需核查 | 多文件实例（dev 101 个、test 569 个）含定位文件、选修改方案、防回归等自然局部决定；单文件小实例（中位 34 行）可能不足 |
| 3 局部做差后整体仍可能继续 | 需实测 | 测试可随时运行（即时反馈），局部错误可能被测试迭代洗掉，也可能静默存活到最终；正是 source-selection.md 第 5 节记录的该来源核心风险 |
| 4 部分结果外部可检查 | 满足 | FAIL_TO_PASS / PASS_TO_PASS 提供原生测试判据 |
| 5 可做 checkpoint fork 的结构 | 结构上可行，实测未验证 | 工作载体是 git 工作目录，完全文件化、可复制、可哈希；会话侧可行性仍依赖 execution-prep.md 第二部分实测清单 |
| 6 无需先知道模型在哪里犯错 | 满足 | issue 与参考补丁来自真实开源项目，本评估未使用任何目标模型轨迹信息 |

**GAIA**：未获取任何题目内容，六条标准全部无法实例级判定。仅按公开论文描述作方向性记录：多步多工具任务形态方向上接近类别 3；最终短答案准精确匹配意味着评分反馈落在最终答案（延迟/终局型），中间过程无原生硬判据（与 source-selection.md 第 5 节"有些实例的局部过程并没有天然 evaluator"的记录一致）。一切以获取数据后实测为准。

### 3.2 SWE-bench 具体候选题目（实例级）

初筛规则（冻结于本文档，未使用任何模型信息）：dev 分片中，参考补丁 30-300 行、触及 >=2 个文件、FAIL_TO_PASS >=3 个测试，共 39 个实例进入候选短名单。以下 5 题为其中结构差异较大的代表，内容摘要均为 problem_statement 字段原文节选（原样引用，未改写）。

**候选 S1：pydicom__pydicom-1048**（dev 分片；repo pydicom/pydicom；base_commit 00c248441ffb8b7d46c6d855b723e696a8f5aada）
- 原文节选："dcmread cannot handle pathlib.Path objects ... The dcmread() currently fails when passed an instance of pathlib.Path. ... dcmread() should open and read the file to which the pathlib.Path object points."
- 规模：触及 6 个文件，258 个 FAIL_TO_PASS 测试（dev 分片最大）。
- 建议类别：类别 2（软件仓库与多文件产物）。
- 潜在局部决定：统一入口判定与多处读取路径的兼容方式、是否修改公共 API 行为、回归面控制。
- 潜在自然 checkpoint（事件型，运行前仍需按 design.md 第 4.2 节冻结）：issue 与相关源码读取完毕且未发生写入；第一次测试命令返回；第一个源文件修改完成。
- 反馈时延：即时（测试命令可随时运行并立即返回通过/失败）。
- evaluator 类型：文件/测试（FAIL_TO_PASS 258 条 + PASS_TO_PASS 0 条）。

**候选 S2：pvlib__pvlib-python-1518**（dev 分片；repo pvlib/pvlib-python；base_commit 6a94e35ffae279468d59577a1d2fbefdcbf768d9）
- 原文节选："Altitude lookup table ... altitude for pvlib.location based algorithms defaults to zero, but if we include a low-resolution altitude lookup, we can provide better results ... We can make this altitude lookup the same format as LinkeTurbidities.h5 ... we do need to do is add this attribution somewhere in the documentation."
- 规模：触及 3 个文件，81 个 FAIL_TO_PASS 测试。
- 建议类别：类别 2。
- 潜在局部决定：数据文件格式选择（沿用既有 h5 格式还是新格式）、接口设计、数据归属声明放置位置。
- 反馈时延：即时。
- evaluator 类型：文件/测试。
- 注意：参考实现含新增数据文件；任务工作目录中该数据文件的供给方式需在环境准备时核实（需实测）。

**候选 S3：sqlfluff__sqlfluff-891**（dev 分片；repo sqlfluff/sqlfluff；base_commit bcc986e7d217f017130385b89cbda837f3e650ac）
- 原文节选："Add enable and disable syntax to noqa to allow rules disabling across multiple lines. See the pylint docs for an example"（problem_statement 全文仅 224 字符，指向外部文档）。
- 规模：触及 2 个文件，49 个 FAIL_TO_PASS 测试。
- 建议类别：类别 2。
- 潜在局部决定：语法形态设计（对齐 pylint 还是另立）、解析器与规则引擎两处改动的一致性。
- 反馈时延：即时。
- evaluator 类型：文件/测试。
- 注意：题面极短、细节依赖外部链接；作为母任务是否提供外部文档内容属材料准备决定，需实测确定。

**候选 S4：pyvista__pyvista-4648**（dev 分片；repo pyvista/pyvista；base_commit d804a93a3bcae250c74a9f0f7c37fbc8bf002011）
- 原文节选："Clean up and clarify sampling-like filters ... One issue is that it is hard to figure out when to use which filter. The other issue is that probe has the opposite behavior of sample and interpolate in regards to order of operation"（附 5 行复现代码与输出对照）。
- 规模：触及 3 个文件，9 个 FAIL_TO_PASS、203 个 PASS_TO_PASS 测试。
- 建议类别：类别 2。
- 潜在局部决定：是统一三个过滤器的参数语义还是保持向后兼容、弃用策略、文档与行为改动的取舍——属于范围/优先级与表示/建模混合型决定，与其它候选题结构不同。
- 反馈时延：即时。
- evaluator 类型：文件/测试。

**候选 S5：pvlib__pvlib-python-1480**（dev 分片；repo pvlib/pvlib-python；base_commit 35af84e9a7bede8dfe86d6d6c73002393544ab5a）
- 原文节选："Consider extracting the surface orientation calculation in pvlib.tracking.singleaxis() to its own function ... Sometimes a user might have their own tracker rotations but not have the corresponding surface_tilt and surface_azimuth values ... A function pvlib.tracking.rotation_to_orient..."
- 规模：触及 2 个文件，3 个 FAIL_TO_PASS、20 个 PASS_TO_PASS 测试；problem_statement 2680 字符，含多个动机场景。
- 建议类别：类别 2。
- 潜在局部决定：函数提取边界（重构范围）、原调用路径的行为保持、数学分支覆盖。
- 反馈时延：即时。
- evaluator 类型：文件/测试。

**候选短名单其余 34 题**：同一初筛规则的其余实例保留在 .materials-cache/swe_bench/dev.parquet 中，逐题登记留到冻结前的抽样程序完成（本文档只给出代表样本，不把短名单当成已入选样本）。

**实例级排除条款检查（source-selection.md 第 3.6 节）**：
- test 分片中 119 个只改测试文件的实例排除（无生产代码工作，不构成多文件产物任务）；
- 两个分片中单文件、参考补丁过短（中位 34 行）的大量实例初判不满足准入标准 1（持续工作），逐实例结论留待抽样时判定；
- 未发现需要"设计者新加规则才出现局部判断"的实例形态（均为原生 issue）。

**群体级风险记录**：
- 即时反馈洗掉局部错误的风险是 SWE-bench 进入本线的核心待验证项（source-selection.md 第 5 节、第 6 节均已登记）；它同时是填补"即时反馈至少 2 题"硬门槛的唯一现实来源。两件事必须实测分开：反馈是否即时足够强到强制修正局部错误。
- 训练污染：12 个仓库均为 2023 年前公开开源项目，大概率出现在主流模型训练语料中。按 source-selection.md 第 7 节只作记录，不在看过模型成绩后选择性排除。
- 环境：SWE-bench 官方运行依赖 Docker 镜像构建仓库环境；本机无 Docker/WSL（与 HANDBOOK 同一阻塞，execution-prep.md Q5）。

### 3.3 GAIA 具体候选题目

无法产生：未获取到任何题目内容。公开论文信息显示其 Level 2-3 多步多工具题方向上对应类别 3，但题目级标识、内容、checkpoint 位置、反馈时延、类别归属全部无法填写。待门控解除获取数据后补入本节，全部标记需实测。

## 第四部分：总账结论

### 4.1 当前全部候选资产盘点

| 来源 | 状态 | 类别 1 | 类别 2 | 类别 3 | 反馈时延 | 原生 evaluator 类型 |
| --- | --- | --- | --- | --- | --- | --- |
| HANDBOOK（本地 8 题，跨线复用决策后去重约 4 个） | 结构已判定，运行项需实测 | 1（9b2f7a29） | 0 | 3 | 全部延迟 | 外部世界状态 |
| SWE-bench（dev 短名单 39，正式抽样框应自 test 分片建） | 元数据已获取，群体与代表实例已评估 | 0 | 39 短名单（正式受"同类别同来源最多 2 个"约束） | 0 | 即时 | 文件/测试 |
| GAIA（优先） | 获取失败（门控 401） | 未知 | 未知 | 未知（方向上对应类别 3） | 未知（论文层面为终局答案型） | 未知（论文层面为答案/数值型） |
| LongBench v2 / LiveBench / BIG-bench | 来源级已判定不入主抽样框（execution-prep.md 1.2） | — | — | — | — | — |

### 4.2 9 题凑不凑得齐：不够

按 design.md 9 题（3 类各 3）与 source-selection.md 第 3.4 节来源集中度约束（同一来源总数最多 4、同一类别同一来源最多 2）逐类核算：

- **类别 1**：仅 9b2f7a29 一个。抽样框最低需 5 个合格候选，缺口 >=4。限定来源中只有 GAIA 可能补此类（是否存在类别 1 形态的题，未获取数据，不能猜）。按第 3.4 节，该类别当前应记为尚未准备好。
- **类别 2**：只有 SWE-bench 一个来源（其余限定来源已在来源级排除）。受"同一类别同一来源最多 2 个"约束，SWE-bench 最多贡献 2 个正式母任务，第 3 个在限定来源内没有已登记的现实出处（GAIA 以 assistant 问答/工具任务为主，是否含类别 2 形态需获取后实测，不能预设）。结论：类别 2 最多凑 2/3，或按第 3.4 节记为尚未准备好。
- **类别 3**：HANDBOOK 最多贡献 2（同类别来源上限），第 3 个原由 GAIA Level 2-3 补——GAIA 当前门控被拦。结论：2/3，缺口 1。

### 4.3 结构差异硬门槛过不过：当前过不了，缺口集中在三处

| 门槛 | 现状 | 判定 |
| --- | --- | --- |
| 即时反馈至少 2 题 | SWE-bench 是限定来源中唯一即时反馈来源，可出 2 题；但须实测确认局部错误不被测试迭代强制洗掉（否则落入 3.6 排除条款） | 有条件可达，需实测 |
| 延迟反馈至少 2 题 | HANDBOOK 4 个候选全部延迟反馈 | 满足 |
| 静默或仅终局评分反馈至少 2 题 | 当前候选 0 个；限定来源中只有 GAIA 的终局答案形态可能覆盖 | 缺口，取决于 GAIA 解除门控 |
| >=3 种原生 evaluator 且每种 >=2 题 | 外部世界状态（HANDBOOK）、文件/测试（SWE-bench）已各可凑 >=2；第 3 种"答案或数值"只有 GAIA 能提供 | 缺口，取决于 GAIA |
| 至少覆盖 4 种局部决定 | HANDBOOK 提供证据冲突处理、外部状态修改（及表示/验证混合）；SWE-bench 提供表示/建模选择、范围/优先级 | 有望满足，需逐题冻结标注后核实 |
| >=3 题后果经两步以上才显现 | HANDBOOK 多单元批处理结构上满足；SWE-bench 多文件实例需逐题标注回归依赖 | 有望满足，需实测标注 |
| 任意两题四元组不同 | HANDBOOK（外部状态+证据冲突+延迟+外部状态 evaluator）与 SWE-bench（代码文件+表示选择+即时+测试 evaluator）四元组天然不同；GAIA 题若进入，其答案/数值 evaluator 与终局反馈也自成一格 | 当前候选间无冲突，扩入新题时逐题核对 |

### 4.4 一句话结论

**不够。** 9 题凑不齐，硬门槛过不了。缺口排序：(1) GAIA 门控是最大单一阻塞——同时卡住类别 3 补位、类别 1 补位、第三种 evaluator 与静默/终局反馈门槛；(2) 类别 2 第 3 题在限定来源内无出处，只能接受 2 题或记该类别尚未准备好（需用户决策）；(3) 即时反馈门槛唯一出处是 SWE-bench，其可用性本身还需练习任务实测确认。若不解除 GAIA 门控，第一轮现实可行的上限是"类别 2 两题 + 类别 3 两题 + 类别 1 一题"共 5 个母任务，且不满 3 类各 3 的设计规模——这属于设计分支决策，不在本文档权限内。

## 第五部分：需实测项清单

1. **GAIA 获取**（前置：用户提供 HF 凭证并同意数据集条款）：重新拉取元数据后，对 Level 2-3 题逐题做六条标准与类别归属评估，补 3.3 节。
2. **SWE-bench 即时反馈强度**：用不进入正式样本的练习实例跑一次（由未来的运行协议执行，非本任务），观察局部错误是被测试迭代强制修正还是可静默存活；结果决定 SWE-bench 候选是否落入 3.6 排除条款。
3. **SWE-bench 环境可启动**：Docker/镜像/仓库检出能力（与 HANDBOOK 同一阻塞 execution-prep.md Q5）；候选 S2 的新增数据文件供给方式一并核实。
4. **checkpoint 分叉可行性**：SWE-bench 工作目录为 git 仓库、文件侧快照/哈希/复制无障碍（结构判断），会话侧仍按 execution-prep.md 第 2.5 节 M1-M7 实测，本任务未新增证据。
5. **HANDBOOK 4 个候选的逐题标注**：反馈时延的动作层/评分层区分、局部决定类型标注（execution-prep.md 1.4 已留此待办）。
6. **统一预算可行性**：SWE-bench 实例在冻结预算内的完成机会（参考补丁中位 34 行、候选短名单 30-300 行只是必要条件），需练习运行。
7. **许可证核查**：SWE-bench 数据集与 12 个仓库的许可证条款、GAIA 的使用条款（获取时一并确认）。

## 第六部分：开放问题

- **Q-A（新）**：GAIA 门控访问是否解除。需要用户级动作：注册/使用 HuggingFace 账号并同意 gaia-benchmark/GAIA 数据集条款，再提供凭证供获取。在解除前，按红线不找替代来源，GAIA 相关评估维持空白。
- **Q-B（延续 execution-prep Q1 的遗留部分）**：跨线复用已被允许，但匿名包混淆、盲评材料重叠、评分器语义串扰的具体隔离办法未冻结。
- **Q-C（延续 execution-prep Q2）**：类别 2 第 3 题无来源——接受 2 题规模、把类别 2 记为尚未准备好、或等待 GAIA 实测后看是否含类别 2 形态题，三选一，需用户决策。
- **Q-D（新）**：SWE-bench 正式抽样框用 test 分片（官方冻结评测集，2294 题）还是 dev 分片（225 题、可直接调试）；练习任务用哪个分片。涉及冻结清单，需决策。
- **Q-E（延续）**：运行环境（Docker/WSL）与被测隔离仍是三条线共同阻塞（execution-prep Q5/Q6），本文档不重复展开。

## 附录：证据与存放位置

- SWE-bench 元数据：.materials-cache/swe_bench/dev.parquet（1,382,594 字节）、.materials-cache/swe_bench/test.parquet（12,097,227 字节）；获取脚本 .materials-cache/fetch_meta.py；统计脚本 .materials-cache/analyze_swebench.py、analyze2.py、analyze3.py；候选原文细节 .materials-cache/swe_candidates_detail.txt。均被 .gitignore 第 14 行覆盖，不进版本库。
- 数据来源 URL：
  - https://huggingface.co/datasets/princeton-nlp/SWE-bench （parquet 镜像 /api/datasets/princeton-nlp/SWE-bench/parquet/default/{dev,test}/0.parquet）
  - https://huggingface.co/datasets/gaia-benchmark/GAIA （gated=auto，401 未获取）
- 论文：GAIA arXiv:2311.12983（ICLR 2024）；SWE-bench arXiv:2310.06770。
- 本仓库文档：docs/subtask-dilution/design.md、source-selection.md、execution-prep.md、docs/research-ledger.md。
- 本次未运行任何被测代理，未产生任何模型行为数据；所有"需实测"条目均未写成结论。
