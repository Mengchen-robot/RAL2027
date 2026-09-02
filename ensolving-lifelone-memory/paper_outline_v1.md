# 结构性部署记忆 — ICRA/RA-L 级写作大纲 v1（施工图）

> 生成日期：2026-08-31
> 上游：本目录 `idea_lifelong_memory.md`（承重结构）、`survey_memory_lifecycle.md`（一手证据与威胁登记）
> 硬件 / 基座 / 预算 / 统计纪律的**唯一真值来源**：`../memory_cross_embodied/idea_cross_embodied/vla_memory_cl_feasibility_v5.md`。本文不重复其结论，只引用。
> **本文档的用法**：这是施工图，不是 idea 描述。每一条要么是可执行的写作/实验指令，要么是可验证的断言。凡标 **【待核】** 的，写进论文前必须有一手证据。

---

# 0. 一页速览

## 0.0 先解决日历问题（这一条决定其余全部）

| venue | 截止 | 页数 | 本 idea 能不能赶上 |
|---|---|---|---|
| **ICRA 2027** | **2026-09-16 15:59**（不延期） | ≤8，双盲 | **不能。** 距今 16 天，三个离线 gate 都还没跑 |
| **IEEE RA-L** | 滚动 | 6（可买页至 7） | **能。** 推荐 **2027-05** 投，排在 idea 1（2027-03-10）之后两个月 |
| **ICRA 2028** | ~2027-09 | ≤8，双盲 | 能，且 RA-L 被拒后天然的第二落点 |

> **推荐路线：RA-L 滚动，2027-05 投，挂 ICRA 2028 presentation option。**
> 理由三条：(a) 与 idea 1 错开 2 个月，避免同期同 venue 被判 salami；(b) 两台台架并行，idea 1 的真机窗口（2026-12 ~ 2027-01）结束后本文才需要大批机器人小时；(c) 本文的三个 gate 全部离线，**现在就能跑**，不占用 idea 1 的任何资源。
>
> **"ICRA 级别"在本文档里指质量标准（可证伪主张 + 真机 + 预注册统计 + 诚实的失败报告），不指 ICRA 2027 这个截止日期。**

## 0.1 Title 推荐

| # | 候选 | 评价 |
|---|---|---|
| **T1（推荐）** | **How Long Is a Memory Good For? Grounding, Staleness and Promotion in a Frozen VLA's Deployment Store** | 与 idea 1 的 T1 同构（问句 + 副标题）；三个名词恰好是三条 Contribution；"deployment store" 避开全部撞车词 |
| T2 | Promotion Without Distillation: An Auditable Action Memory for Frozen VLA Policies | 立场最清晰（直接回应 v3 critique §2.5 的内部矛盾），且刻意用 `promotion` 而非 `consolidation` |
| T3（保守） | A Structured Deployment Memory for Frozen Vision-Language-Action Policies | 最不可攻击也最不吸引人；rebuttal 后改名的退路 |

**★ 标题层面的命名禁令（三条撞车已一手核实，见 `survey_memory_lifecycle.md` §13）**：
- `self-evolving` —— RoboHarness 摘要近逐字
- `consolidation` —— 同上
- `cross-task procedural memory` —— **VLA-Pro 的标题**
- `lifelong robot learning` —— LIBERO 的副标题

**决策规则**：若 G-B（规模×漂移交互）过 → T1；若交互不显著、只剩腐坏腿 → 改 "Retrieval Similarity Cannot See Staleness: Auditing a Frozen VLA's Deployment Memory"，全文转单腿论文。

**方法名**：候选 `STRATA` / `SEDIMENT` / `ATTIC`。**【待核】重名检索本会话不可执行。** 检索完成前正文一律用 LaTeX 宏 `\sysname`，改名成本为零。**名字不进标题**（防守性设计，继承 idea 1）。

## 0.2 Abstract 英文初稿（约 210 词，含全部限定词）

> A frozen vision-language-action policy can improve during deployment by retrieving successful segments it wrote earlier, with no parameter update. Every such store reported so far is flat, is read within the short deployment that produced it, and evicts by recency when full; reported capacity ablations are monotone and saturating. We ask what happens to a store that outlives the world it was written in. On a home-manipulation corpus collected over \todo{M} sessions on a bimanual platform, we find that the value of store size and the exposure to physical drift **interact**: with the scene held fixed, success is monotone in store size, reproducing published capacity curves; across sessions in which appliances were moved and object instances replaced, it is not, because the fraction of entries that were executable when written and are no longer executable when read grows with the store. Retrieval does not see this — neither similarity nor entry age separates stale from fresh entries above chance. We therefore promote clusters of episodic entries into procedural entries that carry the invariant, the variability envelope, and the grounding assumption under which they were written, inside the store and never into the weights. The grounding assumption makes staleness checkable **before retrieval and without executing anything**, matching an ensemble-based policy-side uncertainty estimate that can only be evaluated during execution. We report per-trial memory-harm rate and injection rate, and decompose the gap into write-gate, redundancy, staleness, interference and capacity terms.

**Abstract 写作红线（逐条核对，少一条就有反例）**：

| # | 红线 | 反例（不守就被打） |
|---|---|---|
| 1 | 不得出现 first / novel / unexplored / we fill the gap | 这个方向被 **4 篇论文**写进了 future work（`survey` §13 红线 2） |
| 2 | 必须出现 **injection rate** | 否则"SR 可以靠多弃权刷高"这一击留给审稿人 |
| 3 | 必须出现 **harm rate** | 全族 **0 篇**报过，这是本文主动宣称的诚实性指标 |
| 4 | 必须出现**真实的 N_max**，不得写 10⁵ | v5 §6.7 已据实收窄；且必须与 R-t-S 的 3.5k FIFO 上限并排提 |
| 5 | 规模主张必须写成**交互**，不得写成主效应 | R-t-S Table 6 `61.0→71.2` 单调饱和、ReCAP `9.0→31.5` 未饱和，主效应版本当场被打脸 |
| 6 | 成本论证必须写成**事前 vs 事中**，不得写成"便宜 K 倍" | VFD 的 ensemble 只有 **M=2**（作者实测 size 影响很小），2× 不是卖点 |
| 7 | 必须在正文明写 **lifelong recall & recomposition, not lifelong learning** | v3 critique §2.6 强制项 |
| 8 | **不得**出现 cross-embodiment / cross-body / different robot | 去重协议硬规则 |
| 9 | **不得**出现 self-evolving / consolidation / cross-task procedural memory | §0.1 的命名禁令 |

## 0.3 故事线（3 句话）

1. 检索增强的冻结 VLA 已经跑通，而且已经做过容量消融——Retrieve-then-Steer 扫过 `C ∈ {0,…,5k,∞}`（`61.0→71.2`，4k 后饱和），满库走 FIFO；ReCAP 的池从 11 涨到 35 个任务（`9.0→31.5`，未饱和）。**越大越好，这不是我们要反对的东西。**
2. 但那些库全部来自**世界在其间不变**的部署；**而这四篇论文自己的 Limitations 都写着**：一旦物体布局、相机视角或标定发生变化，*"previously stored action priors may become less informative or even misleading"*。**没有人测过这句话。**
3. 我们把同一份经验写两遍——一遍是 episodic 片段，一遍是提升后的 procedural 条目，后者额外携带**它写入时所假设的接地**；于是"这条经验现在还成不成立"从一个只能靠执行去发现的意外，变成一个在检索之前就能算出来的量。

## 0.4 四条 Contribution（英文成稿，按可辩护性降序）

> **1) We show that neither retrieval similarity nor entry age separates a stale entry from a fresh one, and we give a statistic computed before retrieval that does.**
> We define staleness operationally — an entry that was executable in the scene in which it was written and is not executable in the scene in which it is retrieved — and label it from physical drift events recorded during collection. Against this label we report ROC for four incumbent discriminators (retrieval similarity, entry age, ensemble velocity-field disagreement, single-model denoising variance) and for a grounding residual computed from the entry's own stored grounding assumption. The comparison is not one of compute: the policy-side estimates are defined only once execution has begun, whereas the grounding residual is available before the entry is retrieved.

> **2) We report an interaction between store size and physical drift.**
> With the scene held fixed, closed-loop success is monotone in store size, consistent with published capacity ablations. Across sessions in which appliances were displaced and object instances replaced, it is not, and the offline retrieval quantities show the same interaction over three decades of store size. We report the offline quantities as curves and the closed-loop quantities as a $2\times2$ factorial, and we keep the two visually distinct.

> **3) We promote inside the store rather than into the weights, and the promoted entry abstracts to action rather than to text.**
> A promotion operator maps a cluster of episodic entries in one (task, anchor, phase) cell to a single procedural entry carrying a medoid trajectory in the anchor frame, a per-point variability envelope, the grounding parameters under which the cluster was written, and an outcome posterior. Nothing is distilled into the policy; deleting a procedural entry deletes the experience it summarises. We report the ablation this design requires: a procedural entry must be compared against the episodic entry it replaces, because an averaged trajectory can be a trajectory that no execution ever took.

> **4) We decompose the gap without post-hoc human attribution.**
> An oracle ladder attributes the gap between the flat store at \todo{N_max} and an oracle store to five terms — write-gate false positives, redundancy, staleness, cross-task interference, and residual capacity — each obtained by an offline intervention on the store rather than by labelling failures after the fact. Three of the five have independent precedents in the literature, which we cite term by term. Where any term is negative we report the ladder as a sequence of interventions and not as a variance decomposition.

> **We explicitly do not claim**: the intermediate-state injection into a flow-matching sampler and its confidence-adaptive guidance (adopted unchanged from Retrieve-then-Steer; an industrial implementation also exists in GR00T N1.7's real-time chunking), the entry schema (RDT-1B's 128-dimensional layout), the write gate and rollout segmentation (VLAC / HELP), the anchor-frame contact-point representation (the point-track and object-flow family), the retrieval mechanism (VINN; Di Palo & Johns; RAM), the idea that robot memory should be hierarchical (demonstrated at the planner level by RoboMemory and MemVerse, and long predating both in complementary-learning-systems theory), offline rewriting of stored experience (RoboHarness), or the goal of a lifelong action memory itself, which is stated as future work by MemoryVLA, MEM, VLA-Pro and Retrieve-then-Steer and which we quote directly.

## 0.5 页数分配总表（**全文唯一的一份预算表**，各节引用此表，禁止另立）

RA-L 正文 6 页硬预算，IEEEtran 双栏。

| Section | 预算（页） | 承载的图表 | 备注 |
|---|---|---|---|
| I. Introduction | 1.00 | Fig. 1 (0.22，跨双栏 teaser，2 panel) | 5 段 + Contributions，约 800 词 |
| II. Related Work | 0.70 | Table I (0.22，跨双栏，7 行 × 6 列纯符号) | 4 段；**写入代价坐标系就是 Table I** |
| III. Method | 1.15 | Fig. 2 (0.18 单栏系统图) + Algorithm 1 (0.12) | 含 problem formulation 与 staleness 定义式 |
| IV. Experimental Setup | 0.45 | Table II (0.15 协议与漂移事件表) | 含 robot-hours 句与漂移标注协议 |
| V. Results | 2.25 | Fig. 3 (0.18 scaling) + Fig. 4 (0.20 staleness ROC + cost) + Fig. 5 (0.18 归因阶梯) + Table III (0.26 主结果) + Table IV (0.20 消融) | 评审重心，不可压 |
| VI. Conclusion & Limitations | 0.15 | — | 必须含 "recall & recomposition" 那一句 |
| References | 0.30 | — | **36 条**，按族打包 |
| **合计** | **6.00** | 6 个图表对象 | |

**若买 1 页（7 页）**，新增 1.0 页只允许用于：§V +0.5（把 L2-vs-L1 注入消融与 K/ρ sweep 放回正文）、§III +0.3（巩固算子的聚类判据）、References +0.2（回到 46 条）。**不允许**用于加叙事或加 baseline。

## 0.6 三个最致命风险（决定要不要做）

### 风险 A：**语料没有场次/时间元数据 → 整条时间轴不存在**（单点故障）

- **事实状态**：v5 §1.6 #4 只审计了"两具本体的任务重合度"，**从未审计过采集场次与日期是否被记录**。
- **后果若成立**：staleness 的真值标签不存在，Contribution 2 与 4 的 `Δ_stale` 项同时失效；只能退到全部人为 staged drift（F-2），外部效度大跌。
- **处理**：**这是本 idea 的第 0 号待办，成本是查一次数据目录。** 若无元数据，立即评估三条替代真值：(i) 文件系统 mtime；(ii) 从图像 EXIF / 光照统计聚类出场次；(iii) 从铰链轴拟合结果**反推**场次分界（G-A 的副产品）。**(iii) 最强，因为它直接就是被测量本身。**
- **残余风险**：mtime 可能因拷贝而失真，必须与 (iii) 交叉验证后才可用。

### 风险 B：**抢跑已被一手证据证实**（升为最高风险，替换原"RoboHarness 撞车"）

- **事实状态**：Retrieve-then-Steer 的 Limitations 逐字写着 *"larger-scale deployment may require more **structured memory organization**, **long-term forgetting**, task-aware indexing, and **mechanisms for detecting environment changes**"*。**本文四条 Contribution 里的三条，写在最强前作自己的路线图上。** 另有 MemoryVLA、MEM、VLA-Pro 三篇把同方向写进 future work（原文见 `survey_memory_lifecycle.md` §13 红线 2）。
- **后果**：这**不是**新颖性问题（被认领的是**目标**，不是**机制与数**），而是**时间问题**。
- **处理（三条）**：
  1. **G-A / G-B 一过立即 arXiv 占位**，与 idea 1 的占位合并成一次投放。
  2. **贡献必须落在"可运行的机制 + 可测的量"上**；本文四条里有两条（`AUC_age ≈ chance`、规模×漂移交互）在那四篇里都不存在。
  3. **主动把四段 future-work 原文引进 Intro ¶2。** 问题的重要性由他们论证，本文不必自证；这同时消解"你怎么知道这重要"的质询。
- **监控**：每月核一次 R-t-S 是否挂出新版本（`survey_memory_lifecycle.md` §10 待核清单第 8 条）。

### 风险 B'：RoboHarness 的 consolidation —— **已一手结案，不构成致命冲突**

`consolidat` 在七篇里只有它命中（20 次）。逐条对照见 `survey_memory_lifecycle.md` §2。结论：它**就地改写旧条目的自然语言诊断**，条目数**不减**，value **不含动作**，动机是 *"knowledge stagnation"* 而非世界改变；`stale` / `non-stationar` 在它里面也是 0 命中。
→ **Contribution 3 存活**，代价是**交出 `consolidation` 与 `self-evolving` 两个词**（见 §0.1 命名禁令），并在 Related Work 用整句主动点名它。

### 风险 D：**缺一个合适的 benchmark**（本轮新增，最实际）

| 候选 | 为什么不合用 |
|---|---|
| RoboMME | 严格 episode 内；Limitations 明写 memory-bank 类方法为未覆盖 |
| MemoryBench | 仅约 300 帧，ReMem-VLA 已刷到 94.5%（天花板） |
| LIBERO / SimplerEnv / RoboTwin | 本身不要求跨 episode 记忆；R-t-S 在 LIBERO-10 上仅 `92.4 → 94.4` |

→ **必须自建"连续部署、任务序列、不清库"的评测协议**，唯一可借的现成范式是 RoboMemory 的 *"run each task twice **without clearing long-term memory**"*（26.67% → 46.67%）。**这是 §7 的 P0 项，必须在冻结实验设计之前定稿。**

### 风险 C：**巩固后的 L2 条目在注入时不如原始 L1**

- **机理**：管的中位轨迹可能是"谁都不像"的平均，注入进 flow 采样器中间态后反而产生一条无人执行过的轨迹。
- **后果若成立**：Contribution 3 的"结构"只能存在于**检索层**（作为索引与审计结构），不能作为**注入内容**。
- **处理（设计上先防住）**：
  1. L2 一律存 **medoid（真实存在的那一条 L1）** 而不是 mean；均值只用于算管半径。
  2. 预注册消融 A2：`L2 注入 vs 它的 medoid 所对应的原始 L1 注入`，同初始状态、同 sampler seed 成对。
  3. 若 A2 显示 L2 显著劣于 L1 → 正文改写为 "consolidation restructures retrieval and enables auditing; the injected content remains the medoid episode"。**这仍然是一篇完整的论文，且更诚实。**

---

# 1. Section I. Introduction — 故事线与动机

## 1.0 全节写作红线（交稿前逐条核对）

1. 不写 "we propose a hierarchical memory"。分层记忆在规划层已有（RoboMemory / MemVerse），在认知科学里更早（CLS）。写 **"the level of abstraction and the grounding metadata are the manipulated variables; the injection path is held fixed"**。
2. 不写 "the theory predicts a gap"。Miras 只覆盖参数化序列骨干，`external memory` 词频为 0【继承·一手核对】。只允许写 "we extrapolate its design axes into a region it explicitly does not cover"，且**只能当 framing**。
3. 不写 "entry-level deletion is the only clean answer"。CLARE 已证伪【继承】。
4. 不写 "lifelong learning"。写 **"lifelong recall and recomposition"**，并在 ¶5 主动划出能力边界。
5. **不出现任何 cross-embodiment 词汇。**
6. 不复活"检索延迟-规模曲线"（idea 1 已预注册砍掉：10⁵ 条暴力 cosine 亚毫秒，实验必然无事发生）。

## 1.1 ¶1 — *The thing that already works, stated generously*

先把 R-t-S 讲足：冻结 π0.5、存部署中的成功片段、检索、注入采样器中间态、置信度自适应、零参数更新、真机有效。**讲得越足，第 2 段的转折越有力。** 顺带写出它的容量消融（`C ∈ {0,…,5k,∞}`，FIFO）——**由我们替它说出来，而不是等审稿人指出我们漏了。**

## 1.2 ¶2 — *The premise nobody writes down*（**全文转轴，措辞精度决定生死**）

那些结果全部来自**一次单场景、数百条轨迹、世界在其间没有变化的部署**。这不是缺陷，是当时的实验条件。但它隐含了一个从未被写下来的前提：

> **一条被写下的成功经验，其可执行性不随时间变化。**

这个前提在家庭部署里**必然**不成立：家电会被挪动，衣物会被换掉，拉链会磨损。**而一旦它不成立，一个只增不改的库就不再是资产的单调累积。**

**措辞纪律**：这一段**不得**出现任何"因此现有方法是错的"的表述。写成"这是一个此前无需回答、现在必须回答的问题"。

## 1.3 ¶3 — *Why similarity cannot be the answer*

一条扁平 episodic 条目不携带自己成立的前提。相似度是被优化来对**任务语义**敏感、对**厘米级位姿差**不敏感的；而腐坏恰恰住在后者。所以这不是"检索器不够好"，是**条目里没有那个信息**。

> 这一段必须给出一个**具体的、可想象的画面**（微波炉被推了 10 cm，同一条条目、同样的 top-1 相似度、一个成功一个撞门），并说明这正是 Fig. 1 panel (a)。

## 1.4 ¶4 — *What we change, why it is solvable now, and what we did not invent*

- **改什么**：把条目写两遍，第二遍携带接地假设 `G`；于是腐坏可离线检出。
- **为什么现在能做**：(a) 冻结策略 + 注入机制已被证明可行（R-t-S）；(b) 自动写入门控可得（VLAC MIT 权重，2B/8B；HELP 的 rollout 分段）；(c) 我们有一份能把库灌到 10⁴ 条的真实语料；(d) 我们的任务族的锚点（铰链螺旋轴、拉链弧长轨道）**一次性物理标定就有真值**。
- **没发明什么**：见 §0.4 的 "We explicitly do not claim" 段，**必须整段进 Intro**，不能只放在 Related Work。

## 1.5 ¶5 — *What we verify, the predictions, and the boundary*

三条预注册预测（写成可证伪句，且预先声明判定阈值）：

```
P1  腐坏不可见（承重）：  AUC_sim ≤ 0.60 且 AUC_age ≤ 0.60，而 AUC_ground ≥ 0.75
                        判定：offline，entry 级 n≈10⁴，按 (task, session) 双层 cluster bootstrap

P2  规模 × 漂移交互：    P@10(N | 单场次库) 单调不降   ← 必须复现 R-t-S / ReCAP 的形状
                        P@10(N | 跨场次库) 非单调
                        判定：交互项的 cluster bootstrap CI 不含 0
                        ★ 主效应版本（"越大越差"）预注册为【不主张】——现有一手表格直接反对它

P3  事前 vs 事中：       AUC_ground ≈ AUC_VFD（差值 CI 含 0），
                        但 ground 在检索前可得、VFD 只在执行开始后才有定义
                        判定：offline AUC + 可得时刻的形式化说明（不是 FLOPs 之争）
```

**能力边界（主动写，不等审稿人画）**：主干全程冻结 ⇒ 记忆只能重组基座已会的东西。因此本文是 **lifelong recall & recomposition**。配套实证：预注册一个"基座能力内 vs 能力外"的任务二分，展示记忆在前者接近 oracle、后者失败。

## 1.6 Fig. 1 设计与 caption

- **panel (a)**：同一条条目、同一个 query、**同样的 top-1 相似度**，两个采集场次。左：成功。右：撞门。中间叠一个数字——`similarity 0.9993 / 0.9993`，`grounding residual 4 mm / 63 mm`。**这一张图就是整篇论文。**
- **panel (b)**：从**我们自己的库**导出的一条真实 L2 条目：锚点系里的 medoid 轨迹 + 管 + `G` + `n` + `Beta(α,β)`。
- **caption 纪律**：必须写明这两次执行的初始状态是配对的、sampler seed 匹配的，并注明 seed 匹配只控制第一个 chunk（继承 v5 §6.8）。

## 1.7 待定决策（写第一个字之前必须定）

| # | 决策 | 何时定 | 决定什么 |
|---|---|---|---|
| 1 | 语料有没有场次元数据 | **本周** | 整个 idea 的生死（风险 A） |
| 2 | RoboHarness 的 consolidation 是什么 | 网络恢复当天 | Contribution 3 的生死（风险 B） |
| 3 | `N_max` 的真实数字 | G-B 当天 | Abstract 与 Fig. 3 的横轴范围 |
| 4 | 方法名重名检索 | 网络恢复当天 | `\sysname` 的最终替换 |
| 5 | 投 RA-L 还是等 ICRA 2028 | G-A/G-B 出数后 | 全部排期 |

---

# 2. Section II. Related Work

## 2.0 划分依据（写作前必须内化的一句话）

> **按"库对自己做什么"划分，不按"库里存什么"划分。** 存什么这条轴已经被 RoboMME 的分类法（temporal / spatial / object / procedural）占据，而且我们的分类法必须能映射到它【待核：需一手读 RoboMME 的分类定义再写这一段】。

## 2.1 II-A. Memory that ends with the episode（1 段，~90 词）

MemoryVLA / MEM / ReMem-VLA / LaMem-VLA。**一句话划界**：这些是延长版的工作记忆，跨 episode 即清零，且**记忆模块本身需要训练**；本文的策略全程冻结，且被测对象是跨 episode、跨场次的持久条目。**不贬低，只划界。**

## 2.2 II-B. Memory written into parameters（1 段，~110 词）

顺序微调 / ER / CLARE / VLA-Pro。**必须主动承认**：(a) 大预训练 VLA 抗遗忘（Liu et al. ICML'26：*"remarkably resistant to forgetting"*，plain ER 有时零遗忘）；(b) CLARE 的 adapter 已经是可增长、可寻址、**可删除**的记忆。
**因此本文不以遗忘率为轴，也不以可撤销性为卖点**，而是把它们放进 Table I 的坐标系里，并新增两列坐标：**库变大之后是否退化 / 世界变化后是否可检出**。

## 2.3 II-C. Memory written as explicit entries（2 段，~200 词，全节最重）

R-t-S / Dejavu / RECAP(Retrieve-Don't-Retrain) / RTCF / RoboHarness / Remember Smarter / SkillMemo / ExpReS-VLA / RAEA。

**这一节的写法**（三步，缺一不可）：
1. 承认这一格已经繁荣，**并给出 R-t-S 的容量消融的具体设置**（`C ∈ {0,1k,2k,3k,4k,5k,∞}`，FIFO）；
2. 指出所有这些系统的共同保持规则是 **recency（FIFO）或不淘汰**，且**没有一个报告过条目的时效性**；
3. **单独用一句话处理 RoboHarness 的 offline Memory Consolidation**【待核】，说清目的差异。

## 2.4 II-D. Hierarchical memory outside the action layer（并入 II-C 末段，~60 词）

RoboMemory / MemVerse / CLS 理论 / Miras-Titans-Atlas 的 retention gate。**一句话**：分层与遗忘门在规划层与参数化序列骨干上都已形式化，本文既不主张分层这个想法，也不主张遗忘门这个想法；**主张的是把接地假设写进条目，从而使腐坏成为可离线判定的量。**

## 2.5 Table I（写入代价坐标系，7 行 × 6 列，纯符号）

| 系统 | 写入耗时 | 在线可写 | 满库规则 | 条目可删 | **变大后退化被测过？** | **腐坏可检出？** |
|---|---|---|---|---|---|---|
| 顺序微调 / ER | 小时 | ✗ | — | ✗ | ✗ | ✗ |
| CLARE (adapter) | 分~时 | ✗ | — | ✓ | ✗ | ✗ |
| VLA-Pro (LoRA 条目) | 分~时 | ✗ | — | ✓ | ✗ | ✗ |
| R-t-S | 秒 | ✓ | **FIFO** | ✓ | **部分（≤5k，单场景）** | ✗ |
| Dejavu / RECAP / RTCF | 秒 | ✓ | 不淘汰 | ✓ | ✗ | ✗ |
| RoboHarness | 秒 | ✓ | **consolidation**【待核】 | ✓ | 【待核】 | 【待核】 |
| **\sysname** | 秒 | ✓ | **巩固 + 结果后验淘汰** | ✓ | **✓** | **✓** |

**caption 承载散文**（省版面）。**最后两列是本表相对既有综述的净增量，也是全文的坐标系。**

## 2.6 审稿人备答清单（写进 rebuttal 模板）

| 质疑 | 英文答法要点 |
|---|---|
| "This is Neural Episodic Control with a VLA backbone." | NEC stores a **value table**, writes with a TD target, reads by nearest-neighbour interpolation, and assumes a **stationary MDP**. Our object of study is precisely the non-stationarity; the policy is frozen and the store participates in no value estimate. |
| "Just add a timestamp." | We did. Age separates stale from fresh at AUC \todo{}, i.e. **at chance**, because drift is event-driven, not age-driven. |
| "Just use the policy's own uncertainty." | We compare against it (VFD ensemble and single-model denoising variance) and report **AUC jointly with per-decision cost**; ours matches the ensemble at 1/K of the forward passes. |
| "ER gets higher success rate." | Likely, and we say so. Table I changes the coordinate system, not the ranking on one axis. |
| "You froze the backbone, so this is not lifelong learning." | Stated in §I and §VI as **recall and recomposition**, with the in-capability / out-of-capability task split as evidence. |
| "Your consolidation is RoboHarness's." | 【待核】—— 必须在读完之后再写这一格，**不许提前编答案**。 |

---

# 3. Section III. Method

## 3.1 III-A. Problem setting

```
部署时间轴 t = 1..T，世界状态 w_t（不可观测，但漂移事件 d_t ∈ {0,1} 有记录）
库 S_t = { e_i }，条目 e = (k, v, G, m)
  k  检索 key（沿用既有构造，不主张）
  v  可执行内容（RDT-1B 128 维布局，不主张）
  G  接地假设（写入时的锚点参数）        ← 本文新增的那一项
  m  元数据：写入时刻、支持数 n、结果后验 Beta(α,β)

可执行性  X(e, s) = 1[ 把 e 注入冻结策略、在场景 s 下执行成功 ]
腐坏      Stale(e, s) = 1[ X(e, s_write) = 1 ∧ X(e, s) = 0 ]
接地残差  r(e, s) = d( G(e), ĝ(s) )      ĝ = 在当前场景上重新接地
```

**核心命题（写成一句可证伪的话进正文）**：
> `r(e, s)` 与 `Stale(e, s)` 的互信息显著大于 `age(e)` 与 `Stale` 的互信息，以及 `sim(k(e), q(s))` 与 `Stale` 的互信息。

## 3.2 III-B. Four levels and two operators

L0/L1/L2/L3 的定义表 + PROMOTE/DEMOTE 两个算子（内容见 `idea_lifelong_memory.md` §5，此处只放表与式，不重复论证）。

**必须在正文明写的两条纪律**：
1. **L0 与 L1 不是本文的贡献**，各用一句话点名占位者。
2. **巩固发生在库内，不进权重（consolidation without distillation）**——这一句必须在 §III-B 与 §VI 各出现一次，因为它是"删条目即删知识"仍然成立的唯一保证。

## 3.3 III-C. The consolidation operator

```
cell = (task, anchor type, phase)      phase 沿用 idea 1 的阶段划分（离线可得）
簇内判据：锚点系轨迹在重采样后的 L2 距离 < τ，且接触点语义相同，且 G 参数相容
输出 L2 = ( medoid ξ*(u),  管半径 R(u),  G,  n,  Beta(α,β) )
  - medoid 取真实存在的那一条 L1（**不取均值**，见 §0.6 风险 C）
  - R(u) 由切空间协方差给出；SO(3) 部分用对称群商化的 Karcher 均值（covariates/so3.py 已有）
  - Beta(α,β) 由该簇条目被注入后的成败计数更新（**这是全系统唯一"学习"的东西**）
```

**必须报的超参与其 sweep**：簇判据阈值 `τ`、最小簇规模 `K`、巩固比 `ρ = |L2|/|L1|`。**ρ 必须做 sweep 并报出内部最优**，否则"结构有用"是选出来的而不是测出来的。

## 3.4 III-D. Staleness detection and the demote rule

```
if  r(e, s_now) > c · R_e(u)        →  隔离（不参与检索）
if  LCB( Beta(α,β) ) < p_min        →  淘汰
否则可被检索；注入路径与 R-t-S 逐字相同
```

**`c` 必须在与主结果不相交的一份留出上标定，并把标定过程报成一行审计。** 不这样做，"我们的门控更好"会被判为调参调出来的。

## 3.5 III-E. What is inherited verbatim

一段英文边界声明，结构照抄 idea 1 的做法：

> We adopt unchanged the aggregation, the intermediate-state initialisation of the flow sampler, the confidence-adaptive guidance strength and the abstain-and-fall-back rule of [R-t-S]; an industrial implementation of intermediate-state injection with a soft per-element mask also exists in GR00T N1.7's real-time chunking. What is not from those systems is the grounding term carried by a consolidated entry and the offline test it makes possible.

## 3.6 Fig. 2 与 Algorithm 1

- **Fig. 2**：单栏系统图。写入门控 → L1 → 巩固 → L2（**`G` 用醒目色标出**）→ 接地检查 → 检索 → 注入（**注入框画成灰色并标 "unchanged from [R-t-S]"**，这是诚实性的视觉表达，成本为零）。
- **Algorithm 1**：`CONSOLIDATE` 与 `AUDIT` 两个过程，各 6–8 行。

---

# 4. Section IV/V. Experiments

## 4.0 实验问题 → 表图映射

| 问题 | 端点 | 图表 | 机器人小时 |
|---|---|---|---|
| Q1 规模的价值是否依赖漂移 | P2 | **Fig. 3**（离线两条曲线 + 真机 2×2 四格） | 26 |
| Q2 谁能看见腐坏 | P1, P3 | **Fig. 4**（ROC + 可得时刻） | 20（在线对照 4） |
| Q3 gap 由什么构成 | — | **Fig. 5** 归因阶梯（五项，三项有文献先例） | 0（全离线） |
| Q4 结构本身值不值 | A1–A6 | Table IV | 6 |

> **注意 Q1 与 Q2 的顺序**：Fig. 4（腐坏）是最硬的一张，但 Fig. 3（规模×漂移）必须先出现，因为它建立"存在腐坏"这个前提。**叙述顺序 ≠ 可辩护性顺序**，Contribution 列表按可辩护性排（腐坏第一），§V 按逻辑依赖排（规模第一）。

## 4.1 平台与任务集

- **单台双臂 Piper**（writer = reader）。第二台 PiperX **只作独立复现**，措辞见去重协议。
- **7 个客观自动判定的变体**：4 台不同铰接家电 + 3 个不同的拉链包（沿用 v5 §8.3 的 MVP 任务集，含"提高族数"的修正）。
- **叠衣族不进 confirmatory**（本文不需要 anchor-oracle，正好省掉最贵的前端）。

## 4.2 漂移事件的标注协议（Table II，**这是本文的实验设计核心**）

| 类型 | 来源 | 真值怎么来 | 在 idea 1 里的角色 |
|---|---|---|---|
| D1 家电位姿漂移 | 跨采集场次 | **铰链轴逐场次拟合**（G-A 的产物） | 待查项 |
| D2 家电位姿漂移 | 评测期 ±8 cm/±10° yaw 随机化 | 脚本记录 | 制造 headroom |
| D3 物体实例漂移 | ≥3 件物理实例轮换 | 实例 id | 控制磨损混淆 |
| D4 磨损漂移 | 拉链循环数 / 衣物折痕 | 循环计数 | 必须控制的非平稳性 |

> **一句必须写进 §IV 的话**：D2–D4 的操作在既有实验规程里是**控制变量**；本文把同一批操作**读作自变量**，因此不产生额外机器人小时。

## 4.3 主端点（co-primary 两条，Bonferroni 各 α=0.025）

**(P-scale)** **2×2 析因**：`{单场次库, 跨场次库} × {N_small, N_max}`，× 7 变体 × 20 成对 trial，同初始状态、同 sampler seed。
- **被检验的是交互项，不是主效应。** 单场次那两格必须复现"越大越好"（这是本文对 R-t-S / ReCAP 的复现义务，也是审稿人检查我们没做错的锚点）。
- 库形态（扁平 vs 提升）作为第三个因子放在**次端点**，不进主端点——三因子会把 20 成对稀释掉。

**(P-stale)** `{fresh, stale} × {门控开, 门控关}` × 4 变体 × 20 成对；**主量为 harm rate 的差，不是 SR。**

**HR 的两个定义必须并列写出且明写不可 pooled**：
- `HR_scale`：规模增大后，per-trial 变差的比例
- `HR_stale`：读到 stale 条目后，per-trial 变差的比例

## 4.4 统计上本文相对 idea 1 的一个真实优势（必须写出来，但也必须写出它的限制）

idea 1 的效力被 `n_eff ≈ 4`（族级伪重复）卡死。**本文的两个离线端点的分析单位是"条目"，n ≈ 10⁴**，不是任务数。

**但不得据此宣称效力问题解决**：条目按 (task, session) 双层聚类，必须用**双层 cluster bootstrap**，且**必须同时报 naive n 与聚类后的 n_eff**，摘要只准用后者。**真机端点仍然受 n_eff≈4 支配，与 idea 1 完全一样，必须在 Limitations 明写。**

## 4.5 三条不可砍的前提（继承 v5 §7.4，合计约 6 robot-hours）

1. **A/A 噪声地板**：同一库形态 base-vs-base 跑 20 对，测 `π_d^AA`。SR≈50% 时纯噪声就能给 20–25% 的不一致率，把它写成 harm rate 是硬性误述。
2. **π_d pilot**：`n = 785·π_d`。不实测就不知道 20 对够不够。
3. **盲评与漂移审计**：把 base arm 的成败对 trial 序号做回归，报斜率与 CI（本文尤其必要——**我们的自变量就是时间，顺序效应与被测效应共线**）。
   > **这是本文特有的、比 idea 1 更严重的一个威胁**：若 stale 条目总是在会话后期被测，那么"腐坏效应"与"疲劳/磨损/操作员漂移"完全共线。**必须在会话内随机化 fresh/stale 的先后，并把它写成规程。**

## 4.6 消融清单（Table IV）

| # | arm | 排除的替代解释 |
|---|---|---|
| **A1** | L2 去掉 `G`（只巩固不记接地） | **本文的核心消融**：证明增益来自接地假设而非聚类本身 |
| **A2** | **L2 注入 vs 其 medoid 的原始 L1 注入** | 风险 C 的解药，**不可砍** |
| A3 | L2 去掉管半径（`c·R` 换成固定阈值） | 证明变异包络有用 |
| A4 | 淘汰规则换成 FIFO（= R-t-S 的规则） | 与最强前作的直接对照 |
| A5 | `ρ` sweep（巩固比 5 点） | 防"结构有用是选出来的" |
| A6 | 判别量 B3（VFD ensemble）在线对照 | 防"为什么不用策略自己的不确定度" |

## 4.7 Baseline

必比：**R-t-S（同硬件同注入的直接前作）**、**RoboHarness**【待核】、**frozen base（地板）**、**oracle store（上界：只保留人工确认成功且未腐坏的条目）**。
不复现：其余全部（页数与工时都不允许，且不影响主张）。

## 4.8 §V 的叙述顺序（2.25 页怎么用）

1. Fig. 3 先给规模（0.35 页）——先立"这条曲线不是单调的"
2. Fig. 4 给腐坏 ROC 与成本（0.45 页）——本文最强的一张
3. Table III 主结果（0.55 页）——每格并列 base SR、injection rate、harm rate
4. Fig. 5 归因阶梯（0.35 页）
5. Table IV 消融（0.40 页）
6. 剩余 0.15 页留给"能力内 vs 能力外"的二分实证

## 4.9 必须在 §IV 主动交代的六件事（少一件就在 rebuttal 变成一轮质询）

1. 漂移标签怎么来的、有多少条目被标为 stale、标注者是否知道假设；
2. `c` 的标定用的是哪一份留出，与主结果不相交；
3. 每个 SR 格都并列 **base SR / injection rate / harm rate**；
4. 初始状态配对的容差与达成分布（刚体任务上仍需报）；
5. **matched sampler seed 只控制第一个 chunk**，对长时程任务是装饰性的；
6. **会话内 fresh/stale 顺序随机化**，以及顺序-效应回归的斜率与 CI。

---

# 5. 工程量与排期

## 5.1 组件工程量

| 组件 | 周 | 关键路径 | 备注 |
|---|---|---|---|
| 语料场次元数据审计 + 三条替代真值 | 0.5 | ✅ | **第 0 号待办** |
| G-A 铰链轴逐场次拟合 | 1 | ✅ | **与 idea 1 共享交付物** |
| G-B 规模下采样 + precision@k 管线 | 1 | ✅ | 需要 key 侧管线（idea 1 的 Fig. 3 已建） |
| G-C 锚点系聚类 + 管半径 | 1 | ✅ | |
| 巩固算子（含 SO(3) Karcher，`so3.py` 已有） | 2 | | |
| 接地检查与降级/淘汰规则 | 1.5 | | |
| B3/B4 判别量接通（flow 采样器展开） | 1 | | **与 idea 1 共享交付物** |
| 漂移标注管线与 Table II | 1 | | |
| 五项归因的离线 oracle | 1 | | 全部离线 |
| 真机评测执行（62 h / 3 productive h·day⁻¹） | 4.5 | | 单台 |
| 写作 | 3 | | |
| **合计** | **≈ 17.5 周 ≈ 4 PM** | | |

**与 idea 1 的关系**：三个 gate（2.5 周）与 B3/B4 接通（1 周）**本来就在 idea 1 的待办里**，所以本文的净增量约 **3 PM**。**1 FTE 下，在 idea 1 的真机窗口结束后接续执行，2027-05 投 RA-L 是可行的。**

## 5.2 资源冲突（必须现在说清楚）

| 资源 | 冲突程度 | 处置 |
|---|---|---|
| 两台台架 | **高**（idea 1 的 2026-12~2027-01 窗口占满） | 本文真机排在 2027-02 之后；**离线部分现在就做** |
| FTE | **高** | 本文的净增量 3 PM 全部可与 idea 1 的写作期重叠 |
| 语料 | 无冲突 | 同一份，用途不同 |
| GPU | 低 | 本文几乎不训练（唯一例外是 B3 的 ensemble，K 个 LoRA） |

---

# 6. Go/No-Go 检查点

| Gate | 日期 | 交付物 | No-Go → 论文变成什么形态 |
|---|---|---|---|
| **G-0** | **2026-09-05** | 语料场次/时间元数据审计结果 | 无元数据且三条替代真值全失败 → **不启动本 idea** |
| **G-A** | 2026-09-19 | 铰链轴逐场次漂移量 vs 任务容差 | 无自然漂移 → 切 F-2（staged drift），外部效度写进 Limitations |
| **G-B** | 2026-09-19 | precision@k vs N（4 个规模点）+ `N_max` 实数 | 曲线平坦 → 切 F-1（纯腐坏论文），Contribution 1 降为补充材料 |
| **G-C** | 2026-09-26 | 管半径分布 + 巩固比 ρ | 簇内无不变量 → 切 F-3（只检测不巩固），Contribution 3 删除 |
| **G-R** | 网络恢复当天 | **RoboHarness 逐字精读结论** | 命中 → Contribution 3 删除 |
| **G-1** | 2026-11 | 五个判别量的离线 ROC（entry 级 n≈10⁴） | `AUC_ground < 0.70` 或 `AUC_age > 0.70` → **机制主张作废，本 idea 终止**（这是最硬的一条） |
| **G-2** | 2027-03 | 首批真机规模点与腐坏端点 | harm rate 与 A/A 地板不可区分 → 转负面结果论文 |
| **G-3** | 2027-04 | 实验冻结、图绘制 | — |
| — | **2027-05** | 投 RA-L | — |

> **G-1 是本文的 G0.5**：一个纯离线、entry 级 n≈10⁴ 的判定，决定整篇论文的生死，且**不消耗一小时机器人时间**。这是本 idea 相对 idea 1 最大的结构性优势——idea 1 的生死判定（交叉点）需要真机确认，本文的不需要。

---

# 7. 开写前必须先定的事（带优先级）

**P0（阻塞一切）**
1. 语料场次/时间元数据审计（G-0）
2. **自建"连续部署、任务序列、不清库"的评测协议定稿**（风险 D）。现有 benchmark 全部不合用；唯一可借的范式是 RoboMemory 的 *"run each task twice without clearing long-term memory"*
3. `N_max` 的真实数字（G-B），且必须与 R-t-S 的 3.5k FIFO 上限并排写
4. 与 idea 1 的投稿窗口错开约定（不得同期同 venue）
5. ~~L0 短期层是主动机制还是被引用的边界~~ **✅ 2026-08-31 已决策：方案 A（只作边界），见 §8**

**P1（阻塞写作）**
6. `\sysname` 重名检索；同时确认标题不含 §0.1 的四个禁用词组
7. 六篇【待核】文献的一手核实：Remember Smarter (2608.15269)、SkillMemo (2608.05970)、RTCF (2608.04527)、ExpReS-VLA (2511.06202, ICRA'26)、**Reuse Before You Retrieve (2608.17484 —— 设计空间元分析，本文分类法必须与它对齐)**、RAEA (2404.11699, CVPR'24)
8. RoboMME 分类法的一手定义（本文 L0–L3 必须能映射到 temporal/spatial/object/**procedural**）
9. `c` 的标定留出集划分（必须与主结果不相交；**标定协议照抄 VFD 的 conformal prediction + 10 条成功 rollout**，这样比较才公平）

**P2（阻塞实验）**
10. 会话内 fresh/stale 顺序随机化的规程文本
11. 漂移标注者的盲评安排
12. B3 的 ensemble 规模确认（**VFD 原文用 M=2**，不要照抄 M=10 的 active-finetuning 设定）

---

# 8. 已决策：episode 级短期层（L0）只作边界，不实现（2026-08-31 拍板）

`survey_memory_lifecycle.md` §11 的发现给了一个本文原本没打算占的位置：

> **"在 episode 内起作用的那个记忆"和"能活过 episode 的那个记忆"，在现有全部工作里从来不是同一个对象。**
> 只读不写：MemoryVLA / LaMem-VLA / ReMem-VLA / MEM / RoboMME（episode 边界 hard-reset）
> 只写不读：R-t-S（`B^(i)` 是纯写入暂存区，**episode 内策略从不查询它**）

| | **方案 A ✅ 已采纳** | 方案 B（不采纳，转 Future Work） |
|---|---|---|
| L0 的角色 | 阶梯底端，一段 Related Work，**不实现** | 实现：episode 内写入的条目立即可检索，用在线 progress 信号门控 |
| 净增工程量 | **0** | +1.5 PM |
| 新增风险 | 无 | 在线门控 precision 未知；R-t-S 用 episode 结束后的 VLAC 判定正是为了拿到 0.970 precision，**在线门控几乎必然更差**，会引入新的 `Δ_write` 来源并污染主端点——而 `Δ_write` 是五项归因里唯一有文献先例的那一项 |

**采纳 A 的三条理由**：(a) 6 页装不下四条 Contribution 加一个新机制；(b) 污染 `Δ_write` 的代价太高；(c) **A 不排斥 B**。

**写作上如何兑现"从 episode 到 lifelong"这条叙事（不实现也要写好）**：
1. **§II-A 用一段把这道缝明确写出来**，并给出两侧的逐字证据（ReMem-VLA 的 hard-reset；R-t-S 的 *"temporary buffer to record"*）。**这是免费的 Related Work 增量**——指出一个结构性事实不需要实现它。
2. **§III-B 的四级表把 L0 列出来并标注"inherited / not implemented here"**，让阶梯完整。
3. **§VI Future Work 一句话**：*"the short-term tier is read within the episode by trained memory modules and written across episodes by retrieval stores, but never both; closing that loop under a frozen policy requires an online progress gate whose precision is not yet characterised."*
   → **这句话同时是 idea 3 的题目。**

---

# 9. 一句话

> idea 1 问的是**一条经验能不能被另一具身体读走**；本文问的是**一条经验在多久之后还能被自己读走**，以及**一个库要对自己做什么，才配得上"终身"这个词**。
> 两个问题共用一台机器、一份语料、一个冻结的策略和一套注入机制；**它们唯一不共用的是坐标轴。**
