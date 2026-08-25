# 子任务稀释：候选第三轮搜索（全网扩展搜索与缺口补齐评估）

日期：2026-08-25（第三轮）

这份文档接续 candidate-search-round2.md（第二轮）。用户本轮以明确指示批准：突破 source-selection.md 第 5 节已登记限定来源的限制，在互联网上广泛搜索新的候选任务来源（'不要放弃'是用户原话）。研究诚信要求不变：找到的都是候选，过不过准入标准照六条标准判定；搜不到的缺口如实记'未找到'，不硬凑。本轮全部来源均为人类设计的真实基准，不接受 AI 生成的合成场景；未运行任何基准任务、未启动任何代理；下载只取题目描述级元数据（AssistantBench 两个 parquet 合计约 60KB、Terminal-Bench 2.1 任务级元数据，均远低于 200MB 单项上限），存放于 .materials-cache/（已 .gitignore）。所有结论附出处；获取失败的来源如实记录失败。

## 0. 准入回答（按 research-ledger.md 第 8 节）

1. 属于子任务稀释研究线。
2. 补总账第 6 节该线缺口：母任务抽样框构成。第二轮已确认'静默/终局反馈 ×2 题'与'答案/数值型 evaluator ×2 题'两格在限定来源内无解（只有 GAIA 能补而 GAIA 门控被拦），类别 3 第 3 题与类别 1 补位同样无出处；本轮在限定来源之外搜索新来源填这些缺口。
3. 保留总账第 3 节原则：不从空白编造任务（原则 1，本轮全部新来源均为真实基准）；不把换皮当多样性（原则 2）；候选不是样本量（原则 3）；不预先围绕已知错误挑 checkpoint（原则 8）；不把现成 benchmark 拆成小题拼凑（原则 10）；不因新来源有趣而改变研究问题（原则 11，本轮只填已写明的四个缺口）；工程获取结果不写成模型行为结论（原则 12）。
4. 修改既有决定：是。替代第一、二轮'仅搜索已登记限定来源'的约束，按总账格式记录于第一部分；其余决定均不修改。
5. 新来源角色：母任务材料来源（其中 τ 系 DB 状态比对、AssistantBench 精确答案比对、TheAgentCompany checkpoint 部分得分、Agents' Last Exam 确定性评分器同时构成原生评价器来源）。
6. 不做这项工作：按第二轮情形 B 结论，两个硬门槛格只能无限期等 GAIA，9 题设计规模无法达成；用户已明确指示另寻路径。

## 第一部分：决策记录

### 决策 2026-08-25：候选来源搜索范围扩大（替代'仅限登记来源'）

- **决策内容**：批准在 source-selection.md 第 5 节已登记限定来源（GAIA、LongBench v2、LiveBench、SWE-bench、BIG-bench）之外，于互联网广泛搜索新的候选任务来源。
- **被替代的决定**：第一、二轮'仅搜索已登记限定来源'的约束。未被替代：六条准入标准、三类任务、结构差异硬门槛、来源集中度约束（第 3.4 节）、排除条款（第 3.6 节）与全部红线（真实基准、不运行、轻量下载、如实报告）。
- **理由**：第二轮证明静默/终局反馈 ×2 与答案/数值型 evaluator ×2 两格在限定来源内无解，唯一潜在来源 GAIA 被门控拦截；用户明确表示'不要放弃'。
- **决策者**：用户（明确批准）。**日期**：2026-08-25。
- **边界说明**：本决策只扩大候选来源范围，不放宽任何准入标准；新来源一律按同一六条标准判定，总账原则 11（搜索结果只填补已写明的缺口）继续生效。

## 第二部分：搜索覆盖说明

- **时间**：2026-08-25，单日连续搜索与核验。
- **手段**：(a) 四轮公开网络搜索，共 16 组关键词；(b) GitHub 公开 API 逐仓核验许可证、维护状态（pushed_at / archived / stars）与目录结构；(c) HuggingFace 公开 API 核验数据集门控、许可证与 lastModified；(d) HF parquet 镜像直取题目级元数据（AssistantBench）；(e) 论文公开摘要与官方仓库文档交叉核对任务形态与评价方式。
- **方向与关键词**（任务书提示方向全覆盖，另自行扩展）：

| 方向 | 关键词示例 |
| --- | --- |
| Agentic 基准综述 | agentic benchmark survey 2024/2025；long-horizon agent tasks benchmark |
| Web agent 基准 | web agent benchmark；browsing agent benchmark；tau-bench / tau2-bench；AssistantBench；BrowseComp |
| 办公/企业工作流 | TheAgentCompany；WorkArena；enterprise agent benchmark |
| 长程编程/科研 | Terminal-Bench；MLE-bench；PaperBench；SWE-Lancer |
| 终局答案评分型问答/文档 | Frames benchmark；Humanity's Last Exam；Mind2Web 2；Online-Mind2Web；OSWorld |

- **覆盖自查**：四个缺口中，静默/终局反馈与答案/数值型 evaluator 两格对所有'最终答案精确匹配'评分形态的来源逐一对照；类别 1（结构化记录与分析产物）专门搜索了'办公文档/专业工作流产出'方向——该方向在限定来源内零覆盖，本轮首次找到 TheAgentCompany 与 Agents' Last Exam 两个真实来源。

## 第三部分：逐来源评估

### 3.1 总览表

| 来源 | 结论 | 补缺口 | 获取路径 | 许可证 | 最近更新 |
| --- | --- | --- | --- | --- | --- |
| τ-bench / τ2-bench | **推荐进入候选池** | 类别 3 第 3 题 + 静默/终局 1 题 | GitHub 公开 | MIT | 2026-03-18 / 2026-08-18 |
| AssistantBench | **推荐进入候选池** | 静默/终局 1 题 + 答案/数值 evaluator 1 题 | HF 公开（已下载） | Apache-2.0 | 2024-07-26 |
| Terminal-Bench | **推荐进入候选池** | 类别 2 第 3 题出处 + 静默/终局备位 | GitHub + HF 公开 | Apache-2.0 | 2026-07-11 / 2026-08-21 |
| TheAgentCompany | **推荐进入候选池** | 类别 1 候选 + 类别 3 候选 | GitHub 公开 | MIT | 2025-11-17 |
| Agents' Last Exam | **推荐（有条件）** | 类别 1 候选 + 答案型评分 | GitHub 公开（全集路径待核） | Apache-2.0 + LICENSE-DATA | 2026-08-21 |
| WebArena | 备查 | 类别 3 备选 | GitHub 公开 | Apache-2.0 | 2025-11-26 |
| MLE-bench | 备查（凭证门） | 数值 evaluator 备选 | GitHub + Kaggle 凭证 | NOASSERTION | 2026-04-24 |
| BrowseComp | 备查（门控） | 答案型 evaluator 备选 | HF 门控（本轮 401） | 未知 | — |
| WorkArena | 备查（申请门） | 类别 3 备选 | GitHub + ServiceNow 实例申请 | NOASSERTION | 2026-04-25 |
| OSWorld | 备查 | 类别 3 备选（重环境） | GitHub 公开 | Apache-2.0 | 2026-08-21 |
| Mind2Web 2 / Online-Mind2Web | 备查（不入主抽样框） | — | GitHub 公开 | MIT | 2026-05-17 / 2026-06-25 |
| Humanity's Last Exam | 不合格 | — | HF 门控（本轮 401） | 未知 | — |
| Frames | 不合格（材料池） | — | HF 公开 | Apache-2.0 | 2024-10-15 |
| PaperBench | 不合格（获取失败） | — | 仓库 404 | 未知 | — |
| SWE-Lancer | 不合格 | — | GitHub 公开但已 archived | 无许可证 | 2025-07-18 |

本轮共考察 15 个具名来源集合（τ 系两仓、Mind2Web 系两仓各按同一来源集合计）：**5 个来源集合推荐进入候选池，6 个备查，4 个不合格，另有 MiniSWE-bench 维持第二轮'未证实'结论不重复核验**。

### 3.2 推荐来源详情

#### 3.2.1 τ-bench / τ2-bench（Sierra）

**出处与证据**：github.com/sierra-research/tau-bench（GitHub API 本轮实测：MIT，pushed 2026-03-18，未 archived，1403 stars）；github.com/sierra-research/tau2-bench（MIT，pushed 2026-08-18，未 archived，1866 stars；仓库根目录实测含 data/ 目录，内分 tau2/、voice/ 子目录）。任务形态：LLM 用户模拟器与代理的双角色对话任务，代理须按领域政策调用工具并修改后端 DB 状态完成用户请求（零售/航空等领域）；评价为 pass^k：仅当 k 次独立运行全部满足'终局 DB 状态与参考状态一致且输出通过比对'才算通过。

**六条准入标准**：

| 标准 | 判定 | 依据 |
| --- | --- | --- |
| 1 完整持续工作 | 结构上满足 | 每题是需要多轮对话 + 工具调用 + 状态修改的完整服务任务，非单轮问答 |
| 2 自然产生多个局部判断 | 满足 | 领域政策遵循、操作顺序、信息核验与澄清、约束冲突处理等局部判断自然产生（政策驱动是该基准核心设计） |
| 3 局部做差整体仍可继续 | 需实测 | 终局评分为 DB 状态比对，局部错误很可能静默存活到终局——恰是本线目标形态；分叉后能否继续需实测 |
| 4 部分结果外部可检查 | 满足 | 参考 DB 状态比对为原生评价器，任意中间状态可 diff 检查 |
| 5 可做 checkpoint fork | 结构上可行，需实测 | 状态为 Python 进程内对象与 DB，可序列化复制；用户模拟器对话历史的分叉（种子/版本冻结）需实测 |
| 6 无需先知道模型错在哪 | 满足 | 任务人类设计、参考状态预先冻结，本评估未用任何模型轨迹 |

**补缺口**：类别 3 第 3 题（外部状态与多工具工作流）；静默/终局反馈门槛第 1 题（过程无评分反馈、仅终局状态比对）。
**获取路径**：GitHub 公开直链，MIT，无需凭证。
**风险**：LLM 用户模拟器引入对话不确定性，与 fork 协议的适配需实测（见 Q-H）；部分任务对话链较短，选题应取长链条实例。
**结论**：**推荐进入候选池**。

#### 3.2.2 AssistantBench（Allen AI）

**出处与证据**：HF 数据集 AssistantBench/AssistantBench（本轮 API 实测：gated=False，许可证 apache-2.0，lastModified 2024-07-26，config default，split test 与 validation）；论文为 AssistantBench: Can Web Agents Solve Realistic and Time-Consuming Tasks?（公开资料）。**本轮已下载并实测分析**：test.parquet 33,155 字节、181 题（答案不公开，answer 字段为 null）；validation.parquet 28,095 字节、33 题（含 answer、explanation、gold_url）；字段为 id、set、task、answer、gold_url、explanation、metadata、difficulty；validation 答案类型实测：字符串 17、数字 7、列表 9；难度 Medium 14、Hard 19。样例题（原文原样引用，未改写）：'Which gyms near Tompkins Square Park (<200m) have fitness classes before 7am?'、'What's the lowest price a Single Family house was sold in Queen Anne in January 2023?'——均为需要多网页交叉查证与数值聚合的多约束真实任务。

**六条准入标准**：

| 标准 | 判定 | 依据 |
| --- | --- | --- |
| 1 完整持续工作 | 满足 | 公开资料记载人类单题完成耗时以十分钟以上计，需多步浏览、筛选、计算；本轮实测题面均为多约束研究任务 |
| 2 自然产生多个局部判断 | 满足 | 信息源选择、筛选口径转换、数值聚合方式、结果交叉验证等局部判断自然产生 |
| 3 局部做差整体仍可继续 | 需实测 | 过程无反馈，局部错误大概率静默存活至终局答案；分叉后能否继续需实测 |
| 4 部分结果外部可检查 | 满足 | validation 分片有精确答案（含 7 个数值型），可精确匹配/数值核对 |
| 5 可做 checkpoint fork | 需实测 | 工作载体为浏览会话与笔记，非文件仓库；状态复制方式按 design.md 第 6 节需实测 |
| 6 无需先知道模型错在哪 | 满足 | 真实人类出题、答案预先冻结 |

**补缺口**：静默/终局反馈门槛第 1 题；答案/数值型 evaluator 门槛第 1 题（validation 分片含 7 个数值答案与字符串/列表精确匹配）。类别归属：主形态属类别 3（web 浏览工具），若强调'研究笔记 + 聚合结论'的产物形态可作类别 1 边缘候选——归属在冻结时判定，不预先指派。
**获取路径**：HF 公开直链，无门控；本轮已下载（合计约 60KB，题目描述级）。
**风险**：test 分片答案不公开，选题限于 validation 33 题或向作者申请；任务依赖 live web，页面随时间漂移，漂移归属与可复现性需实测（见 Q-I）。
**结论**：**推荐进入候选池**。

#### 3.2.3 Terminal-Bench（Laude Institute / Harbor）

**出处与证据**：github.com/laude-institute/terminal-bench（GitHub API 实测：Apache-2.0，pushed 2026-07-11，未 archived，2552 stars；original-tasks/ 目录实测 241 个任务目录）；HF 数据集 harborframework/terminal-bench-2.1（API 实测：gated=False，apache-2.0，lastModified 2026-08-21；本轮获取任务级元数据）。任务形态：代理在 Docker 容器终端内完成编程/系统操作/数据处理/验证类任务；**测试对代理隐藏，只在任务结束时运行并评分**——反馈时延天然静默/终局。

**六条准入标准**：

| 标准 | 判定 | 依据 |
| --- | --- | --- |
| 1 完整持续工作 | 满足 | 每题为终端环境中的完整工作任务（构建、调试、配置、数据处理等），非单轮问答 |
| 2 自然产生多个局部判断 | 多数任务满足，逐题待核 | 241 题跨难度带，多步任务含方案选择、错误定位、验证安排等局部判断 |
| 3 局部做差整体仍可继续 | 需实测 | 测试隐藏至终局，局部错误天然静默存活；分叉后能否继续需实测 |
| 4 部分结果外部可检查 | 满足 | 隐藏测试套件为原生评价器，可对外部单独运行作部分核验 |
| 5 可做 checkpoint fork | 结构上可行，依赖 Docker | 容器文件系统即状态，快照/复制结构上可行；本机无 Docker（Q-E），实测受阻 |
| 6 无需先知道模型错在哪 | 满足 | 任务人类设计、测试预先冻结 |

**补缺口**：类别 2 第 3 题出处（打破第二轮'类别 2 只有 SWE-bench 一个来源'的死局）；静默/终局反馈门槛备位题。
**获取路径**：GitHub 与 HF 均公开，Apache-2.0，无需凭证。
**风险**：依赖 Docker，与 HANDBOOK/SWE-bench 同一阻塞（Q-E）；241 题的任务级六条标准过筛本轮未展开（仅来源级判定）。
**结论**：**推荐进入候选池**。

#### 3.2.4 TheAgentCompany

**出处与证据**：github.com/TheAgentCompany/TheAgentCompany（GitHub API 实测：MIT，pushed 2025-11-17，未 archived，770 stars；workspaces/tasks 目录实测恰有 175 个任务目录）。任务形态：模拟真实公司的 175 个部分工作（part-time work）任务（软件开发、文档撰写、财务、人事、运营等），环境为自托管服务栈（GitLab、项目管理、即时通讯、云盘等）；评价为**程序化 checkpoint 部分得分**（中间检查点程序化评分，部分完成得部分分）。

**六条准入标准**：

| 标准 | 判定 | 依据 |
| --- | --- | --- |
| 1 完整持续工作 | 满足 | 每题是一段完整工作任务，非单轮问答 |
| 2 自然产生多个局部判断 | 满足 | 多系统协同、信息整合、优先级安排等判断自然产生（跨服务是核心设计） |
| 3 局部做差整体仍可继续 | 需实测 | checkpoint 部分得分机制表明局部错误不必中断任务；分叉后能否继续需实测 |
| 4 部分结果外部可检查 | 满足 | 程序化 checkpoint 评分为原生评价器，部分结果可逐项得分——与本线部分可检查要求天然对齐 |
| 5 可做 checkpoint fork | 依赖环境，需实测 | 状态分布在自托管服务栈，Docker 环境 30GB 量级；本机无 Docker（Q-E） |
| 6 无需先知道模型错在哪 | 满足 | 任务人类设计、checkpoint 预先冻结 |

**补缺口**：**类别 1 候选**（175 题中含档案整理、表格与文档产出类任务（按官方任务目录的方向性判断，任务级过筛未开始），填类别 1 在限定来源内零出处的问题）；类别 3 候选（多工具网页工作流）。
**获取路径**：GitHub 公开直链，MIT，无需凭证。
**风险**：重环境（Docker 服务栈 30GB 量级）；类别 1 归属需任务级过筛（见 Q-K）。
**结论**：**推荐进入候选池**。

#### 3.2.5 Agents' Last Exam（UC Berkeley RDI）

**出处与证据**：github.com/rdi-berkeley/agents-last-exam（GitHub API 本轮实测：Apache-2.0，pushed 2026-08-21，未 archived，969 stars，默认分支 main；根目录实测含 tasks/（21 条目）、LICENSE-DATA、secret/、selected_tasks/、.gitmodules）；论文 arXiv:2606.05405（公开资料）。规模与形态（引自公开资料）：960 个专家编写的专业工作流、1490 个任务实例，覆盖 55 个子领域、13 个行业集群；公开版约 150 任务；**93.2% 任务由确定性程序评分器自动判分**；任务在真实操作系统沙箱中执行；难度分档 Near-Term（59）、Full-Spectrum（55）、Last-Exam（36）。

**六条准入标准**：

| 标准 | 判定 | 依据 |
| --- | --- | --- |
| 1 完整持续工作 | 满足 | 专家设计的完整专业工作流，非原子小题 |
| 2 自然产生多个局部判断 | 满足 | 专业领域判断自然产生（领域专业知识即该基准的难度来源） |
| 3 局部做差整体仍可继续 | 需实测 | 分叉后能否继续需实测 |
| 4 部分结果外部可检查 | 满足 | 93.2% 任务有确定性程序评分器 |
| 5 可做 checkpoint fork | 依赖沙箱，需实测 | 操作系统沙箱的状态复制方式需实测 |
| 6 无需先知道模型错在哪 | 满足 | 专家出题、评分预先冻结，非合成场景 |

**补缺口**：类别 1 候选（专业工作流产出报告/文档/表格类任务）；其终局评分形态同时覆盖静默/终局反馈与答案型评分。
**获取路径**：GitHub 仓库公开；**全集数据获取路径本轮未核实到底**（.gitmodules 指向的子模块内容与是否需申请未确认）；LICENSE-DATA 条款内容级核销受限（raw 直读失败，改用目录 API 确认存在，如实记录）。
**风险**：上述两项获取侧未决（见 Q-L）；任务级六条标准核验在获取后展开。
**结论**：**推荐进入候选池**（有条件：冻结前须完成获取路径与数据许可核验）。

### 3.3 备查

- **WebArena**（web-arena-x/webarena，Apache-2.0，pushed 2025-11-26）：自托管站点套件 + 程序化状态判定，类别 3 备选；环境较重（多个自托管站点 Docker），任务级对本线的适配性需实测。备查。
- **MLE-bench**（openai/mle-bench，NOASSERTION，pushed 2026-04-24）：Kaggle 竞赛式 ML 工程任务，评价器为数值指标比对（天然答案/数值型）；获取竞赛数据需 Kaggle 账号。备查（凭证门，见 Q-J）。
- **BrowseComp**（OpenAI，公开资料见 openai/simple-evals 仓库 browsecomp_eval.py，MIT；数据本体在 HF）：终局答案精确匹配的浏览调研题，方向上可补答案型 evaluator；但 HF 数据集门控（本轮实测 401），与 GAIA 同类阻塞。备查（见 Q-M）。
- **WorkArena / WorkArena++**（ServiceNow/WorkArena，NOASSERTION，pushed 2026-04-25）：ServiceNow 平台企业工作流任务，类别 3 备选；运行需申请 ServiceNow 开发者实例。备查（申请门）。
- **OSWorld**（xlang-ai/OSWorld，Apache-2.0，pushed 2026-08-21）：整虚拟机桌面环境与执行状态评价；环境过重，本地不可行。备查。
- **Mind2Web 2 / Online-Mind2Web**（OSU-NLP-Group，MIT，pushed 2026-05-17 / 2026-06-25）：网页代理任务但评价以 LLM judge 为主，无原生确定性评价器，不满足硬门槛的原生评价器要求。备查（不入主抽样框）。

### 3.4 不合格

- **Humanity's Last Exam**（Center for AI Safety；HF 数据集 hle 本轮实测 401 门控）：任务形态为单答案专家题，落排除条款第 3.6 节第一条（只有一个回答/选择/最终数字的题）；且门控。**不合格**。
- **Frames**（google/frames-benchmark，本轮实测：gated=no，apache-2.0，lastModified 2024-10-15，824 题）：单答案检索增强问答题，落排除条款第一条；可作材料池不入主抽样框。**不合格**。
- **PaperBench**（OpenAI，论文公开资料编号 arXiv:2504.01848）：GitHub openai/paperbench 本轮返回 **404 未找到**，GitHub 广搜亦无 OpenAI 名下对应仓库——获取失败，六条标准无法判定。**不合格（获取失败，如实记录，不以任务形态猜测替代核验）**。
- **SWE-Lancer**（openai/SWELancer-Benchmark，本轮实测：许可证=无，archived=True，pushed 2025-07-18）：无许可证且仓库已归档，合规与维护状态双失。**不合格**。

## 第四部分：总账更新

### 4.1 全部候选资产盘点（本轮后）

| 来源集合 | 状态 | 类别 1 | 类别 2 | 类别 3 | 反馈时延 | 原生 evaluator 类型 |
| --- | --- | --- | --- | --- | --- | --- |
| HANDBOOK（沿用第二轮） | 不变 | 1（9b2f7a29） | 0 | 候选 3，正式上限 2 | 延迟 | 外部世界状态 |
| SWE-bench（沿用第二轮） | 不变 | 0 | 池足，正式上限 2 | 0 | 即时 | 文件/测试 |
| τ-bench / τ2-bench（本轮新增） | 来源级推荐 | 0 | 0 | 候选（第 3 题出处） | 静默/终局 | DB 状态比对 |
| AssistantBench（本轮新增） | 来源级推荐，元数据已获取 | 边缘候选（归属待判） | 0 | 主形态 | 静默/终局 | 答案/数值精确匹配 |
| Terminal-Bench（本轮新增） | 来源级推荐 | 0 | 候选（第 3 题出处） | 0 | 静默/终局 | 隐藏测试 |
| TheAgentCompany（本轮新增） | 来源级推荐 | 候选（文档产出题） | 0 | 候选 | 延迟（checkpoint 制） | checkpoint 部分得分 |
| Agents' Last Exam（本轮新增） | 有条件推荐 | 候选（专业产物题） | 0 | 部分任务 | 静默/终局 | 确定性程序评分 |
| GAIA（门控搁置，沿用） | 不变 | 未知 | 未知 | 未知 | 未知 | 未知 |

### 4.2 四个缺口的补齐状态

| 缺口 | 第二轮结论 | 本轮结论 |
| --- | --- | --- |
| 静默/终局反馈 × 2 题 | 缺口，只能等 GAIA | **2/2 理论补齐**：τ 系 1 题 + AssistantBench 1 题，均无需凭证；两题的反馈时延归属需实测确认（首次不依赖 GAIA） |
| 答案/数值型 evaluator × 2 题 | 缺口，只能等 GAIA | **1/2 部分补齐**：AssistantBench validation 1 题落实（含数值答案）；第 2 题未找到免凭证来源（GAIA/BrowseComp 门控、MLE-bench 需 Kaggle 凭证），如实记录 |
| 类别 3 第 3 题 | 只能等 GAIA Level 2-3 | **可补**：τ-bench/τ2-bench，轻量 Python 环境，不依赖 Docker |
| 类别 1 补位 | 限定来源内无出处 | **方向上可补**：TheAgentCompany（文档/表格产出类任务）+ Agents' Last Exam（专业工作流产出）+ AssistantBench（边缘候选）；任务级归属需实测 |

### 4.3 9 题凑齐与否（理论核算）

按 design.md 3 类各 3 题与第 3.4 节来源集中度约束（同一来源集合最多 4、同类别同一来源最多 2）：

- **类别 1**：9b2f7a29（HANDBOOK）+ TheAgentCompany / Agents' Last Exam 任务级过筛后取 2 题 = 3。同类别同来源不超 2，满足。
- **类别 2**：SWE-bench test 分片 2 题（不同仓库，沿用第二轮口径）+ Terminal-Bench 1 题 = 3。类别 2 自此不再单一来源。
- **类别 3**：HANDBOOK 2 题 + τ 系 1 题 = 3。
- **理论合计 9/9，首次凑齐**。来源分布：HANDBOOK 3、SWE-bench 2、τ 系 1、Terminal-Bench 1、TAC/ALE 2——无任一来源集合超 4，满足第 3.4 节。
- 每类抽样框最低 5 个合格候选：类别 1 候选池为 TAC 175 题方向过筛 + ALE 公开约 150 任务 + AssistantBench 边缘候选，池足但逐题过筛未开始；类别 3 候选池新增 τ 系（两代任务集），足。

### 4.4 结构差异硬门槛逐格状态

| 门槛 | 第二轮状态 | 本轮状态 |
| --- | --- | --- |
| 即时反馈 ≥2 题 | SWE-bench 有条件可达（练习实测防 3.6 排除条款） | 不变 |
| 延迟反馈 ≥2 题 | 满足（HANDBOOK 3 题） | 不变（TAC checkpoint 制任务归属待逐题判定，只增不减） |
| 静默/终局反馈 ≥2 题 | **缺口：只能等 GAIA** | **理论满足**：τ 系 1 + AssistantBench 1；两题归属均需实测确认（Q-H/Q-I） |
| ≥3 种原生 evaluator 且每种 ≥2 题 | 第三种（答案/数值）空缺 | **2/3 种满足**：外部世界状态（HANDBOOK）、文件/测试（SWE-bench）各 ≥2；答案/数值已落实 1（AssistantBench），第 2 题依赖凭证；隐藏测试（TB）与 DB 状态比对（τ）作为评价器形态冗余备位 |
| ≥4 种局部决定 | 五类决定有望覆盖 | 不变；τ 系新增政策遵循型、TAC 新增多系统协同型，逐题冻结标注后核实 |
| ≥3 题后果经两步以上显现 | 有望满足 | 不变（τ 系 DB 状态链条结构上支持，逐题标注） |
| 任意两题四元组不同 | 无冲突 | 新增题四元组（τ：对话+DB 状态 / 政策判断 / 静默终局 / DB 比对；AssistantBench：web 笔记 / 聚合判断 / 静默终局 / 精确答案）与既有各题均不同，冻结时逐对核对 |

### 4.5 一句话结论

全网扩展后，四个缺口中**三个有免凭证的落实路径**（静默/终局反馈 2/2、类别 3 第 3 题、类别 1 方向上可补），答案/数值型 evaluator **补齐一半**，另一半如实记'未找到免凭证来源'；**9 题理论上首次凑齐**，但落地依赖三项实测——Docker 环境（Q-E，卡 Terminal-Bench 与 TheAgentCompany 两来源）、τ 用户模拟器与 fork 协议适配（Q-H）、AssistantBench live web 稳定性（Q-I）；实测完成前不得把理论配置写成既成结论（原则 12）。

## 第五部分：凭证/申请清单

| 来源 | 门控类型 | 需要的动作 | 状态 |
| --- | --- | --- | --- |
| GAIA | HF 门控（gated=auto） | HF 账号并同意数据集条款（Q-A 延续） | 未解除 |
| BrowseComp | HF 门控（本轮实测 401） | HF 账号并同意条款 | 未解除 |
| MLE-bench | Kaggle 凭证 | Kaggle 账号与 kaggle.json，同意竞赛规则 | 未解决 |
| WorkArena | 平台申请 | 申请 ServiceNow 开发者实例 | 未解决 |
| Humanity's Last Exam | HF 门控（本轮实测 401） | 无需申请（来源已判不合格） | 关闭 |
| Agents' Last Exam | 待核实 | 全集访问路径（.gitmodules 指向）与 LICENSE-DATA 条款核实 | 待核实（可能无需凭证） |

## 第六部分：开放问题

- **Q-A（延续）**：GAIA 门控未解除。本轮变化：静默/终局反馈格与类别 3 第 3 题不再依赖它；答案/数值型 evaluator 第 2 题仍依赖（或改走 BrowseComp，见 Q-M）。
- **Q-D（延续）**：SWE-bench 正式抽样框冻结在 test 分片（练习用 dev），证据已备，待用户拍板。
- **Q-E（延续，优先级上升）**：Docker/WSL 环境与被测隔离仍是三线共同阻塞；本轮新增 Terminal-Bench、TheAgentCompany 两个推荐来源同样被它卡住——环境问题从'阻塞两类题'升级为'阻塞五个推荐来源中的两个'。
- **Q-F（延续）**：MiniSWE-bench 登记出处存疑，待用户核对；本轮未重复核验。
- **Q-G（延续，证据已更新）**：先行还是等待。第二轮情形 B 的前提（'硬门槛两格只能等 GAIA'）已不成立——静默/终局格有免凭证路径、答案/数值格补齐一半；决策证据应按本轮总账重估，本文不代选。
- **Q-H（新）**：τ 系用户模拟器的非确定性与 checkpoint fork 协议如何适配：模拟器种子/版本冻结方案、对话轮级分叉可行性、pass^k 评分与本线单次分叉的关系，需出实测方案后再冻结来源。
- **Q-I（新）**：AssistantBench 选题范围（validation 33 题答案公开可直接用；test 181 题答案不公开，是否向作者申请）；live web 页面漂移算环境因素还是任务失败，可复现性口径需冻结。
- **Q-J（新）**：类别 2 第 3 题取 Terminal-Bench（免凭证、需 Docker）还是 MLE-bench（需 Kaggle 凭证、评价器为数值型可兼补答案/数值第 2 题）？优先级待决策。
- **Q-K（新）**：TheAgentCompany 175 题中哪些算类别 1（结构化记录与分析产物）需任务级过筛口径；其 checkpoint 部分得分如何作为本线 evaluator 使用；30GB 量级 Docker 服务栈的可部署性。
- **Q-L（新）**：Agents' Last Exam 全集获取路径（.gitmodules 指向何处、是否需申请）与 LICENSE-DATA 条款合规核验；本轮内容级核销失败（raw 直读受限），下轮补齐。
- **Q-M（新）**：若用户批准 BrowseComp 访问，是否优先以它补答案/数值型 evaluator 第 2 题（作为 GAIA 的替代路径，同为终局答案精确匹配形态）。

## 附录：证据与存放位置

- 本地数据与脚本（.materials-cache/，.gitignore 覆盖，不入库）：
  - round3/assistantbench_test.parquet（33,155 字节，181 题）、round3/assistantbench_validation.parquet（28,095 字节，33 题）；
  - terminal-bench-2.1 任务级元数据（round3_fetch.ps1 获取）；
  - 脚本：round3_fetch.ps1（下载）、round3_check_hf*.ps1（HF 门控/许可核验）、round3_check_gh*.ps1（GitHub 许可证/维护状态/目录结构核验）、round3_check_ale*.ps1（ALE 仓库结构核验）、round3_analyze_ab*.py（AssistantBench 答案类型统计）；
  - 中文写入测试文件 round3_test.md。
- API 实测记录（均为 2026-08-25）：
  - GitHub API：sierra-research/tau-bench（MIT，pushed 2026-03-18，1403 stars）、sierra-research/tau2-bench（MIT，pushed 2026-08-18，1866 stars，data/ 含 tau2/ 与 voice/）、TheAgentCompany/TheAgentCompany（MIT，pushed 2025-11-17，770 stars，workspaces/tasks 恰 175 目录）、laude-institute/terminal-bench（Apache-2.0，pushed 2026-07-11，2552 stars，original-tasks 241 目录）、rdi-berkeley/agents-last-exam（Apache-2.0，pushed 2026-08-21，969 stars，含 LICENSE-DATA、secret/、selected_tasks/、.gitmodules）、ServiceNow/WorkArena（NOASSERTION，pushed 2026-04-25）、openai/mle-bench（NOASSERTION，pushed 2026-04-24）、openai/SWELancer-Benchmark（无许可证，archived，pushed 2025-07-18）、xlang-ai/OSWorld（Apache-2.0，pushed 2026-08-21）、web-arena-x/webarena（Apache-2.0，pushed 2025-11-26）、OSU-NLP-Group/Mind2Web-2（MIT，pushed 2026-05-17）、OSU-NLP-Group/Online-Mind2Web（MIT，pushed 2026-06-25）、openai/simple-evals（MIT，含 browsecomp_eval.py 但无数据文件）、openai/paperbench（**404 未找到**，广搜亦无 OpenAI 名下对应仓库）。
  - HF API：AssistantBench/AssistantBench（gated=False，apache-2.0，lastModified 2024-07-26）、harborframework/terminal-bench-2.1（gated=False，apache-2.0，lastModified 2026-08-21）、google/frames-benchmark（gated=no，apache-2.0，lastModified 2024-10-15，824 题）、openai/BrowseComp（**401 门控**）、Center for AI Safety/hle（**401 门控**）。
- 论文与公开资料：GAIA arXiv:2311.12983；SWE-bench arXiv:2310.06770；PaperBench arXiv:2504.01848（仅论文，代码获取失败）；Agents' Last Exam arXiv:2606.05405；τ-bench、τ2-bench、AssistantBench、TheAgentCompany、Terminal-Bench、MLE-bench、BrowseComp、Frames、WorkArena、WebArena、OSWorld、Mind2Web 2 均以官方仓库 README 与论文公开摘要为据（链接见第三部分各条）。
- 本仓库文档：design.md、source-selection.md、candidate-sources-v0.md、candidate-search-round2.md、research-ledger.md。
- 声明：本轮未运行任何基准任务、未启动任何代理、未产生任何模型行为数据；全部题目内容原样引用自真实数据集，无 AI 编写或改写；所有'需实测'条目均未写成结论；获取失败的来源（PaperBench 仓库 404、ALE LICENSE-DATA 内容级核销）如实记录，不用推测补写。
