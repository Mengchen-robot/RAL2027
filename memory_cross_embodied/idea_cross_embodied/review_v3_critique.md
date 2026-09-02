# 对 `vla_memory_cl_feasibility.md` (v3) 的审查、批判与重构建议

审查日期：2026-08-22
审查方式：逐条核对 `memory-vla/papers/` 本地 PDF 原文 + arXiv API 一手元数据 + OpenReview 记录。
所有指控均给出可复现证据（arXiv ID / PDF 原文引文）。

---

## 0. 一句话结论

**这个 idea 的核心方法在三个月前已被发表。**

`arXiv:2605.10094` **Retrieve-then-Steer: Online Success Memory for Test-Time Adaptation of Generative VLAs**（2026-05-11）的摘要原文：

> "…asking whether a partially competent **frozen VLA** can improve its reliability by reusing its successful test-time experience… the robot stores progress-calibrated successful observation-action segments in a **long-term memory**. At inference, it **retrieves state-relevant action chunks**… and aggregates them into an **elite action prior**… **injects the elite prior into an intermediate state of the flow-matching action sampler** and adjusts the guidance strength based on **retrieval confidence**… enables lightweight, **non-parametric** test-time adaptation **without requiring parameter updates**."

对照 v3 §5.1：冻结主干（第 4 点）、外部记忆库存 action-chunk 潜码（第 1 点）、**检索条目引导 flow-matching 去噪方向（CFG 式）（第 3 点 = SQ3 核心技术贡献）**——逐条命中。v3 认为"离散 token 时代没有对应物、是开放问题"的记忆注入点，对方已经做了，还多做了一个 v3 没想到的 confidence-adaptive 门控。

所以本文的结论不是"打磨一下即可"，而是：**§2 的格局图、§4 的 SQ1/SQ3、§5 的方法框架都要重做。** 但资源（双本体 + 数百小时真机数据 + 百卡）依然支持一篇好论文——只是必须换一个立足点。下面按"事实错误 → 论证断裂 → 方法 → 实验 → 重构方案"展开。

---

## 1. 事实性错误（一读即穿，必须先修）

### 1.1 【致命】Behrouz 统一理论被误读，而它是全文的理论支柱

v3 §2.4/§2.6/§3 反复主张：Behrouz 框架把四类记忆基底统一了，**"理论预言了空白，我们去填"**。

原文核对（`papers/01_unified_memory_theory/Its_All_Connected_ICLR2026.pdf`，实为 **arXiv:2504.13173，2025-04**，ICLR 2026 Poster）：

- 框架名叫 **Miras**，四个设计轴是 attentional bias（记忆目标）/ retention gate / memory architecture / memory learning algorithm。
- Table 1 列出它统一的模型：Transformer, RetNet, Linear Attention, DFW, Lightning Attention, GLA, Mamba, HGRN2, DeltaNet, Longhorn, TTT-Linear, Gated DeltaNet, RWKV-7, DeltaProduct, Titans。**无一例外全是参数化序列模型骨干。**
- 全文词频：`RAG` = 0，`external memory` = 0，`database` = 0，`retriev*` = 2（均为无关的类比与评测名）。
- 文中 "non-parametric" 出现 2 次，**指的是"记忆目标有闭式解、不用梯度下降"**（Table 1 里 Transformer 那一行的 learning algorithm 就写作 "Nonparametric"，因为 softmax attention 是那个回归问题的闭式解），**不是外部数据库**。

结论：**Miras 既没有覆盖外部检索记忆，也没有把"VLA 权重被 SGD 顺序微调"当作它的实例。** v3 那张 2×2 图下方那句"四格皆为关联记忆+在线优化的不同实例化，右上格未被实例化"是本文自己编的推论。这条会被任何读过 Miras 的审稿人（正是你要投的圈子）一眼看穿，而且看起来像"只读了摘要没读 Table 1"。

**可用的修法**（保住这块弹药，且更强）：不要说"框架预言了空白"，改说"**我们把 Miras 的四选设计空间外推到它明确不覆盖的区域**"：

| Miras 设计轴 | 参数化序列记忆（Miras 覆盖） | 外部持久记忆（本文所处区域） |
|---|---|---|
| memory architecture | 有界、参数化（矩阵 / 深 MLP） | 无界、非参数（显式条目表） |
| learning algorithm | 在线梯度优化（Δ 规则、动量） | 单步硬写入（η=1，写入互不干涉） |
| retention gate | 权重衰减式软遗忘 | 条目级显式删除 + 时效衰减 |
| attentional bias | ℓ2 回归 / 点积相似度 | 检索相似度（同族，可对齐） |

这个表述是诚实的、可辩护的，而且把"外部记忆 = Δ 规则在容量→∞、学习率→1 的退化极限"这条连线讲清楚，本身就是有价值的一段。但注意：**它只能当 framing，不能当 novelty**——见第 2 节。

### 1.2 【严重】CLARE 被放错象限，导致"可撤销性"这条差异化整条失效

v3 §2.6 把 CLARE 和"顺序微调/EWC"一起塞进"权重（终身但不可审计）"格。核对 `CLARE_RAL2026.pdf`（arXiv:2601.09512，TUM Schoellig 组，RA-L 2026）摘要原文：

> "…introduces lightweight **modular adapters**… **autonomously expands the model only where necessary** when learning a new task… During deployment, an **autoencoder-based routing mechanism dynamically activates the most relevant adapters without requiring task labels**… significantly outperforming even exemplar-based methods."

即 CLARE 已经是**可增长、可寻址、条目化（adapter 即条目）、可删除**的记忆——删掉一个 adapter 就删掉一个技能，还不需要 task id。

于是：

- v3 §3 支点 3「治理缺口：权重基底不可删除…**记忆条目级删除是唯一工程上干净的答案**」——被 CLARE 直接证伪。
- v3 §5.3 阶段 B「杀手级 demo：技能级遗忘」——CLARE 也能演。而且这个 demo 在你的设计里是**构造性成立**的（删条目→检索失败→技能失效），它是一个 sanity check，不是一个发现。

**模块化参数记忆是第五种基底**，且正是你想占的那一格的强占位者。2×2 图必须重画。

### 1.3 【严重】动机所依赖的"遗忘"前提，被你自己下载的论文推翻

`Pretrained_VLAs_Resistant_Forgetting_ICML2026.pdf`（arXiv:2603.03818，Huihan Liu / Yuke Zhu，UT Austin——LIBERO 原作者组）摘要原文：

> "pretrained VLAs are **remarkably resistant to forgetting**… Simple **Experience Replay (ER) works surprisingly well** on VLAs, **sometimes achieving zero forgetting even with a small replay data size**… VLAs can **retain relevant knowledge from prior tasks despite performance degradation**… enables **rapid recovery of seemingly forgotten skills**."

而 `InfoVLA_Continual_Alignment.pdf`（arXiv:2603.13335）同样在 LIBERO 上开篇就说 "suffer from **severe catastrophic forgetting**"。

**两篇正面打架。** v3 把 Liu et al. 仅列为「风险 #3」，严重低估了：如果 Liu et al. 对，**SQ1 特性矩阵里"遗忘率"这根主列会全线趋同，整张表就没内容了**——而那张表是 v3 自称"论文被引用的理由"。

### 1.4 其余需要订正的条目

| v3 写法 | 事实 | 影响 |
|---|---|---|
| "SOP（GR00T 在线后训练系统）" | arXiv:2601.03044，基座是 **π0.5** + RECAP + HG-DAgger；GR00T 只出现在参考文献里 | PI / NVIDIA 背景审稿人一眼识破 |
| "RA-VLA（ICLR 2026 submission）" | OpenReview 记录为 **ICML 2026**，且无 arXiv 公开版（`papers/README.md` 自己也承认没下到） | 它是你最近的竞争者，弄错会显得没做功课 |
| "Episodic Memory Banks" | **查无此文**，全库唯一凭空条目 | 一条假引用会让审稿人不信任整份书目 |
| "MemoryVLA/MemoryVLA++（ICLR 2026）" | MemoryVLA (2508.19236) 是 ICLR 2026；**MemoryVLA++ (2606.09827) 是 2026-06 预印**，晚于 ICLR 决议 | 时间上不可能，比笔误更难看 |
| §2.5 "Grant et al. mechanistic study … Not-all-features 等"（当成两篇） | 同一篇：arXiv:2603.19233 *Not All Features Are Created Equal: A Mechanistic Study of VLA Models*，且是 **ICLR Workshop** 论文 | 不能当作主力机理证据承重 |
| "SRPO（CVPR 2026）" | arXiv:2511.15605，**查不到任何 CVPR 2026 收录证据** | 降级为 arXiv 引用 |
| "Info-Theoretic Continual VLA **Alignment**" | 真题名含 **Constraints for** | 小错，顺手改 |
| VLAC / LifeLong-RFT / EMV / Dual Latent Memory | 均为方法名≠题名；EMV 实际叫 **H²-EMV** | 用真题名引用 |

另：全部 8 个被抽查的 arXiv ID 都解析正确，`memory-vla/papers/` 里 27 篇 PDF 也都是真论文。**书目的"存在性"没问题，问题全出在venue 标注与解读上。**

### 1.5 规划自相矛盾：ICRA 2027 已经来不及

`ICRA2027/paper_plan.md`：**截止 2026-09-16，≤8 页，双盲，不延期**。今天 2026-08-22 → 剩 **3.5 周**。
v3 §6 的时间估计是 **6–7.5 个月**。

文件却放在 `ICRA2027/idea/`，`paper_src/root.tex` 骨架已建。**按 v3 的计划，ICRA 2027 完全不可能。** 这个冲突要么现在处理，要么 9 月 16 日自动处理掉。

### 1.6 小瑕疵

- 第 26 行有一个孤立的 `Memory` 字符串（v2→v3 编辑残留）。
- 正文里写"引用 351 / 引用 157 / 引用 67"这类 Google Scholar 引用数，写进论文会过期且显得不专业；调研笔记里留着可以，正文别带。

---

## 2. 论证断裂：novelty 主张已经站不住

### 2.1 "四象限空白"是错的，而且是最危险的一种错

不是"有一两篇擦边"，而是**已经形成一个有基准（benchmark）、有设计空间综述（design-space meta-analysis）的子领域**。以下全部经 arXiv API 一手核实（题名/日期/收录均为原始元数据）：

**Tier 1 — 直接命中你的方法**

| 论文 | ID / 日期 | 命中了什么 |
|---|---|---|
| **Retrieve-then-Steer** | 2605.10094 · 2026-05-11 | 持久部署 + 冻结 VLA + 长期记忆存 obs-action 段 + 检索 action chunk + **注入 flow-matching 采样器中间态** + 置信度自适应引导 + 零参数更新 + 仿真&真机。**= v3 §5.1 全部四点 + SQ3** |
| **RECAP** (*Retrieve, Don't Retrain*) | 2606.15631 · 2026-06-14 | "**新任务通过向检索池追加演示来加入。冻结策略在每个控制步条件于检索到的轨迹，新任务靠索引数据而非更新参数来吸收**" = 你的"跨任务持久增长、零梯度" |
| **Dejavu** | 2510.10181 · 2025-10 | 冻结 VLA + 检索执行记忆 + **部署中持续扩充记忆库**，"learning from experience" |
| **RAEA** | 2404.11699 · **CVPR 2024** | "policy retriever" + "**external policy memory bank**"。这一格 **2024 年就被开垦了** |

**Tier 2 — 严重威胁**

RTCF (2608.04527，training-free 冻结 VLA 记忆修正)、**RoboHarness (2603.24060, IROS 2026**，冻结 π0/π0.5/SmolVLA 的记忆增强 harness + **离线 Memory Consolidation**——连你的 SQ2 巩固都占了)、**VLA-Pro (2605.29562**，跨任务程序性记忆迁移，存 LoRA 条目并在推理时融合)、Remember Smarter (2608.15269，π0 上即插即用经验记忆，LIBERO-Plus 53.6→70.6)、SkillMemo (2608.05970)、ExpReS-VLA (2511.06202, **ICRA 2026**)、DRAE (ACL 2025)、MAP-VLA、EchoVLA、Uni-Skill (ICRA 2026)。

**Tier 0 — 这个领域已经在被"评分"了**

- **RoboMME (2603.04639, ICML 2026)**：VLA 记忆的**基准**，含记忆分类法（temporal/spatial/object/procedural）与 **14 个 memory-augmented π0.5 变体**的横向比较。
- **Reuse Before You Retrieve (2608.17484, ECCV 2026 workshop)**：冻结 VLA 的测试期增强**设计空间分析**——检索 vs 重采样该选哪个。

> 一个领域不会在还"完全空白"的时候就有基准论文和"该选哪种干预"的元分析。

**投稿前必须做的一件事**：读 RoboMME。你的论文将被拿它的分类法来打分，而 v3 的"记忆基底四象限"和它的分类法完全没对齐。

### 2.2 连"flow 源分布"这条退路也被占了

v3 把 SQ3（记忆注入 flow expert）当作"flow-matching 时代特有的新问题"。实际：

- **WarmPrior** (2605.13959, 2026-05)：把 flow 的标准高斯源分布换成时序先验，结语原话 "**identify the source distribution as an important and underexplored design axis in generative robot control**"——连"underexplored"这个词都被人先说了。
- **Flowing With Purpose / LAFM** (2606.23420, 2026-06)：把"单一各向同性源分布"换成"**自适应的先验分布库**"，按观测选专门的基分布。"按观测选先验库"在结构上离"检索记忆"只差一步。
- **RAGDP** (2507.21452, 2025-07)：向量库检索专家 (obs, action)，**在中间去噪步注入**，无需额外训练。
- **Retrieve-then-Steer** (2605.10094)：中间态注入 + 引导强度自适应。

四个注入点（prefix-KV / 源分布 / 速度场引导 / 轨迹混合）里，**已被占的是源分布 + 中间态引导两个**。剩下的空间窄到不足以撑一篇论文的主贡献。

### 2.3 episodic control 是审稿人最便宜的一枪

Model-Free Episodic Control (1606.04460)、Neural Episodic Control (1703.01988)、Continuous Episodic Control (2211.15183，开篇即"**Non-parametric episodic memory** can be used to quickly latch onto high-rewarded experience"，对比慢速反向传播)、Agentic Episodic Control (2506.01442)。

预期审稿意见，逐字：*"This is Neural Episodic Control with a VLA backbone."* 你需要一句准备好的回答。

### 2.4 缺失的、也是最致命的基线：Experience Replay

v3 §5.3 的基线是"顺序微调 / EWC / CLARE"。**没有 ER。**

而你的"外部记忆库 = 部署经验的资产负债表"在**存什么**这一层，和 replay buffer 没有区别；差别只在**怎么用**（零梯度条件化 vs 梯度回放）。Liu et al. 已证明 plain ER 在 VLA 上近乎零遗忘。审稿人一定会问，而且这一问会要命。

必须正面比较，但**比较轴不是成功率**：

| | ER（梯度回放） | CLARE（adapter 扩展） | 显式记忆（零梯度） |
|---|---|---|---|
| 新技能写入耗时 | 小时（重训） | 分钟~小时（训 adapter） | **秒** |
| 写入所需数据量 | 数十条 | 数十条 | **1 条** |
| 部署中在线可写 | 否（要停机） | 否 | **是** |
| 删除某技能 | 做不到（已进权重） | 删 adapter（可） | 删条目（可） |
| 跨本体复用 | 不可 | **不可**（adapter 绑骨干） | **可**（语言/潜码层） |

只要这张表成立，**ER 成功率更高也不伤论文**——你换了坐标系。这才是 v3 缺的那句话。

### 2.5 内部矛盾：SQ2「巩固」会摧毁 §3「可撤销性」

SQ2 要把外置记忆蒸馏进权重；§3 又把"条目级可删除"当核心卖点。**一旦巩固发生，删条目并不能删知识**——权重基底的原罪被你自己请了回来。v3 完全没意识到。

两个出路：(a) 明确"巩固可选，巩固后的条目标记 non-deletable，并用 membership-inference 式探针**量化删除后的残留泄漏**"；(b) 砍掉 SQ2，做纯零梯度并把"不巩固"变成立场。**建议 (b)**——SQ1–SQ5 五个问题，RA-L 六页装不下，砍一个换立场清晰。（注意 RoboHarness 已有 Memory Consolidation，(a) 路线还得跟它比。）

### 2.6 冻结主干 → 能力上界必须自己先说

主干全程冻结，记忆只能**重组/召回基座已经会的东西**，学不到基座没有的运动技能。所以这是 lifelong **recall & recomposition**，不是 lifelong learning。这不丢人（in-context 那派一样），但**必须自己先划边界**，否则审稿人会拿"学一个全新技能"来打。

Retrieve-then-Steer 的局限更极端：它只存**自己成功过**的片段 → 严格来说是自我强化，无法积累新东西。**这恰恰是你可以攻击它的地方**（见 §5）。

可做的实证：设计"基座能力内 vs 能力外"的任务二分，展示记忆在前者接近 oracle、后者失败。**主动画出自己的边界，比被审稿人画出来强得多。**

---

## 3. 方法层

### 3.1 SQ4（容量界）大概率交付不了

Hopfield / 关联记忆容量结论管的是**模式召回**，不是**闭环策略成功率**。从预算 B 推到"终身性能下界"，中间要跨越 检索命中率 → 动作正确率 → 闭环成功率 三层，每层都不可控。

**建议降级**：(a) 检索层可证的界（预算 B 下 top-k 命中率——这个能做）+ (b) 成功率的经验 scaling 曲线。假定理是 RA-L 审稿人最不留情的地方。

### 3.2 缺失机制：检索失败与负迁移

记忆返回错条目可能**比没有记忆更差**。v3 全文没有 abstain / gating / 置信度机制，也没有"负迁移率"指标。Retrieve-then-Steer 有（confidence-adaptive guidance + trajectory-level consistency filtering）——**这是能力差距，不只是叙述差距**。必须补：检索置信阈值 + 回退到无记忆策略 + 报告"记忆有害率"。

### 3.3 被忽略的系统约束 = 被忽略的机会

动作策略是 ~50 Hz 闭环，一次记忆读取要在 chunk 边界内完成。**"O(1) 检索 vs O(context) 注意力"是显式记忆对 in-context 阵营（RoboTTT 走 8K context）的硬优势**，v3 只在指标里提了半句"存储/算力曲线"。应该提到卖点级：延迟-记忆规模曲线，记忆库涨到 10^5 条时 in-context 早就爆了。这条至今没人认真做。

### 3.4 命名

CAMEL 与 NeurIPS'23 的 CAMEL (Communicative Agents for "Mind" Exploration) 撞车，对方引用量很高。换名。

---

## 4. 实验层

### 4.1 LIBERO 承载不了核心实验

(a) π0/GR00T 在 LIBERO 上已近饱和（Liu et al. 的热力图大量 0.94–1.00）；(b) Liu et al. 已证 LIBERO-Object/Goal 上顺序微调几乎不遗忘（只有 LIBERO-10 有明显掉点，出现 0.30–0.54）；(c) 10 个任务的流对"终身"来说太短。

若仍要做基底对比，必须：更长任务流（LIBERO-90 排列 + **多个随机任务序**）、更难的套件（RoboCasa / 自建长流）、**低样本 regime**（每任务演示压到 5–10 条，差异才显现）。**必须报告多任务序的方差**——CL 结论对任务序极其敏感，单序结果不可信。

### 4.2 基线清单不够

必加：**ER（多个 buffer size）**、多任务联合训练 oracle（上界）、per-task LoRA + oracle task id（可塑性上界）、frozen-base zero-shot（下界）、retrieval-then-finetune（Behavior Retrieval 2304.08742 / STRAP 2412.15182 式）、**Retrieve-then-Steer 与 RoboHarness（现在是必比项，不是可选项）**。缺 oracle 上下界，任何矩阵都没有参照系。

### 4.3 真机预算没被算过

阶段 B "10–20 任务流按序部署"，粗算一次完整评测：20 任务 × 15 trials × ~1.5 min（含复位）≈ **7.5 机器人小时 /（方法 × 检查点）**。5 方法 × 5 检查点 ≈ **190 小时纯评测**，不含采数、故障、重跑。1.5–2 个月做不完。

→ 砍到 **8–10 个真机任务、3 个方法、3 个检查点**，省下的时间全给跨本体。

### 4.4 建议新增（把 §2.5 的洞见变成实验——免费的增量贡献）

v3 §2.5 说"遗忘首先是表征结构事件而非性能事件"，然后**没有任何实验去测它**。加两个便宜的探针：沿任务流测 (a) V-L-A 跨模态对齐漂移（CKA / 互信息，沿用 Info-VLA 的度量）、(b) 线性探针可解码性。

这一步顺便**仲裁 Info-VLA 与 Liu et al. 的正面矛盾**——"成功率没掉但表征塌了" 或 "表征没塌只是动作头漂了"，无论哪个结论都可发表，而且**纯仿真、成本极低**。

### 4.5 跨本体（SQ5）被严重低估

双本体是你**唯一别人复制不了**的资源，却排在最后、给 1–1.5 个月、还写成"独占实验维度"式的附加项。而它恰好是所有竞争者结构上都做不到的事：

- **RECAP 自己承认**：新任务免训练，但**换本体需要微调**。
- **VLA-Pro** 的记忆条目是 LoRA 权重 → 天然绑死骨干与本体。
- **Retrieve-then-Steer / Dejavu / RoboHarness** 全是单机器人、单环境。

这是唯一还开着的大门。

---

## 5. 重构方案

### 5.1 死掉的和活着的

**必须放弃**：
- "四象限空白" / "首次在 VLA 动作层实例化外部记忆" → 2024 年 RAEA 就有，2026 年一打。
- "SQ3 记忆注入 flow expert 是开放问题" → Retrieve-then-Steer + RAGDP + WarmPrior + LAFM。
- "Behrouz 理论预言了空白" → Miras 不覆盖非参数外部记忆。
- "遗忘率"作为主要指标 → Liu et al.。
- "条目级删除是唯一干净答案" → CLARE。

**还活着（按可辩护性降序）**：

1. **跨本体记忆迁移**。竞争者结构性做不到；你有 FR3 + 移动机械臂 + 数百小时数据。可证伪的强命题：**「记忆能跨本体迁移，而权重与 adapter 不能」**，并给出分层迁移率谱系（语言摘要 > 潜码 > 原始动作）。
2. **记忆生命周期在长时间尺度上的行为**。容量、淘汰、时效（staleness）、条目间干扰——记忆库涨到 10^4–10^5 条会发生什么，**目前无人研究**（现有工作全是单环境、短部署）。这是真空白，而且你的存量数据能直接把记忆库灌到那个规模。
3. **写入代价坐标系**（§2.4 那张表）。把评价轴从"成功率/遗忘率"换成"获取一个新技能要多少数据、多少时间、能不能在线、能不能撤销、能不能换本体"。
4. **闭环延迟约束下的记忆读取**（§3.3）。
5. **仲裁 Info-VLA vs Liu et al. 的表征级研究**（§4.4）——独立成篇也成立。

### 5.2 建议的新定位（可直接替换 §7）

> Retrieval-augmented frozen VLAs now work — but every existing system remembers **one robot, one environment, one deployment**. We ask what happens when the memory **outlives** all three: when it grows to 10⁵ entries over months, when entries go stale, and when it must be read by a **different body** than the one that wrote it. We show that an explicit action memory transfers across embodiments where weights and adapters structurally cannot, and we characterize the capacity–staleness–interference regime that determines whether a robot's memory is an asset or a liability.

跟 v3 那句"we instantiate the missing memory substrate"相比：不再宣称占领空白（会被证伪），而是**接着已有工作往下问一个没人问过的问题**——这才是能过审的姿态。

### 5.3 时间线的现实处理

ICRA 2027 剩 3.5 周（截止 2026-09-16，不延期）。以下三选一：

- **A. 放弃 ICRA 2027，专攻 RA-L 滚动**（推荐）。目录改名 `RAL2027/`。按 §5.1 重组，跨本体前置：仿真 2 个月 → 真机 2 个月 → 跨本体 1.5 个月 → 写作 1 个月 ≈ 6.5 个月，2027 年 3 月投 RA-L，仍可挂 IROS/ICRA option。
- **B. 抢 ICRA 2027，投 §5.1 第 5 条**（表征级仲裁研究）。纯仿真、无需真机、无需新方法，3.5 周是极限但不荒谬；且天然成为大论文的 §2 动机。风险：3.5 周做完 8 页双盲，质量难保证，失败会占用重组主线的时间。
- **C. 坚持 substrate matrix 作主贡献** → RA-L 六页装不下，改投 CoRL 2027 / TMLR。但在 RoboMME (ICML 2026) 已经做了 14 个 π0.5 记忆变体横向比较之后，这条路的新颖性也已经受损。

---

## 6. 修订检查清单（无论走哪条路都要做）

- [ ] 删除第 26 行残留的 `Memory`
- [ ] §2.4 §2.6 §3 重写 Behrouz 部分（改成"外推到框架未覆盖区域"，附 §1.1 的表）
- [ ] §2.6 2×2 图重画：加入"模块化参数记忆（CLARE / VLA-Pro）"这一类；右上格标注为**已被占据**并列出占据者
- [ ] 新增 §2.x「检索增强的冻结策略」小节，点名 Retrieve-then-Steer / RECAP / Dejavu / RTCF / RoboHarness / RAEA，逐个说清差异
- [ ] 新增 RoboMME 对齐段落（你的分类法要能映射到它的分类法）
- [ ] §3 支点 3 删除"唯一干净答案"的表述
- [ ] 动机主轴从"遗忘"换成"写入代价 / 可撤销 / 跨本体"
- [ ] §5.3 基线补 ER、oracle 上下界、Retrieve-then-Steer、RoboHarness
- [ ] SQ2 与"可撤销性"的矛盾：二选一并写明
- [ ] SQ4 降级为"检索层可证界 + 经验 scaling 曲线"
- [ ] 新增检索置信门控与"记忆有害率"指标
- [ ] 换名（CAMEL 已被占）
- [ ] 修 §1.4 表格里全部 venue / 题名错误；删除 "Episodic Memory Banks"
- [ ] 正文去掉所有 Google Scholar 引用数
- [ ] 真机实验规模按 §4.3 重算并写进计划
