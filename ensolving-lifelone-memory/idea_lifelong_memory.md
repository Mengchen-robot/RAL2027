# 结构性部署记忆：从 episode 记忆自演化到 lifelong 记忆 · idea clean 版

> 日期：2026-08-31
> 上游：`memory_cross_embodied/idea_clean.md`（idea 1）、`vla_memory_cl_feasibility_v5.md`（硬件/预算/基座的唯一真值来源）、`review_v3_critique.md`（**本 idea 的直接授权来源**：其 §5.1 把「记忆生命周期在长时间尺度上的行为」列为存活方向 #2）、`reframe_primitive_conditional.md`（idea 1 的重构，本文的**去重对象**）
> 本文件只回答一件事：**这是一篇什么文章，它的承重结构在哪里，什么条件下它成立。**
> 标注约定：**【复算】**=本轮/前序亲自跑过；**【继承】**=来自 idea 1 已核实的一手证据；**【待核】**=本会话全网不可达，投稿前必须补一手证据。

---

## 0. 先说清楚这是第二篇，不是第一篇的一节

`review_v3_critique.md` §5.1 在枪毙了 v3 的 CAMEL 之后，列出五条"还活着"的方向，按可辩护性降序：

1. 跨本体记忆迁移 → **已被 idea 1 占用**
2. **记忆生命周期在长时间尺度上的行为**（容量 / 淘汰 / 时效 / 条目间干扰）→ **本文**
   > 原文逐字："记忆库涨到 10⁴–10⁵ 条会发生什么，**目前无人研究**（现有工作全是单环境、短部署）。这是真空白，而且你的存量数据能直接把记忆库灌到那个规模。"
3. 写入代价坐标系 → 本文的 Table I
4. 闭环延迟约束下的记忆读取 → **idea 1 已主动砍掉且预注册不复活**（10⁵ 条暴力 cosine 亚毫秒，"实验必然无事发生"）。**本文同样不复活。**
5. 表征级仲裁研究 → 与本文正交，不并入

所以本文不是"idea 1 的一个补充实验"，而是那份对抗审查亲手指定的第二条主线。**它的合法性来自那份文件，不需要重新论证。**

---

## 1. 一句话

> 一个机器人在部署中不断往自己的成功记忆库里写条目。**写到第 10⁴ 条、跨过三个月、世界已经变了之后，这个库还是资产吗？**
> 如果不是，那么这个库必须**对自己做什么**，才能重新变回资产？

第二问才是论文。第一问只是让第二问有意义。

**注意这两问的形状**：它们问的不是"检索增强有没有用"（R-t-S 已经答了：有用），而是**"有用性是不是条目数的单调函数"**。没有人报过这条曲线的右半段。

---

## 2. 生态位：把格子从"谁能读"换成"多久还能读"

idea 1 的 2×2 是 `持久性 × 跨本体可读性`。本文必须换一张，否则就是同一张图的第二次使用。

```
                        库自身随时间是否重组 →
                 只增不改（append-only + FIFO）      自我重组（巩固 / 降级 / 淘汰）
        ┌──────────────────────────────────────┬────────────────────────────────┐
  短部署 │ Retrieve-then-Steer, Dejavu,         │ RoboHarness 的 offline Memory  │
 （单场景，│ RECAP(Retrieve-Don't-Retrain),       │ Consolidation 【待核：它到底做  │
  数百条， │ RTCF, Remember Smarter, SkillMemo    │ 了什么，是不是本文的巩固算子】   │
  世界不变）│ ——库满了走 FIFO，条目永不合并、       │                                │
        │   永不过期、永不因结果被降权            │                                │
        ├──────────────────────────────────────┼────────────────────────────────┤
  长部署 │  ★ 无人测量                           │  ★ 空白（本文）                 │
 （跨场次， │  这条曲线的右半段没有人画过：          │                                │
  10⁴ 条， │  N 从 10² 涨到 10⁴、条目从"今天写的"   │  结构性原因：短部署里这两格看不出 │
  世界会变）│  变成"三个月前写的"之后，SR 怎么走     │  差别——库还没大到会互相干扰，     │
        │  ——**这是本文的被测对象**              │  世界还没变到条目会腐坏            │
        └──────────────────────────────────────┴────────────────────────────────┘
```

**空白是结构性的，不是没人想到**：要观测右半格，你必须同时具备 (a) 一个能灌到 10⁴ 条的真实语料、(b) 一个跨了多个采集场次、世界真的发生过变化的部署环境、(c) 一台冻结的、能被记忆注入的真机策略。**这三件东西同时到位的组只有极少数，而本组三件都有**（数百小时家居语料 / 多场次采集 / π0.5 + openpi-agilex）。

### 2.1 第二条空白（一手复算，比上面那张格子更锋利）

> **"在 episode 内起作用的那个记忆"和"能活过 episode 的那个记忆"，在现有全部工作里从来不是同一个对象。**

全库被干净地劈成互不相交的两半【复算·`survey_memory_lifecycle.md` §11】：

| | 谁 | 证据（逐字） |
|---|---|---|
| **只读不写** | MemoryVLA / LaMem-VLA / ReMem-VLA / MEM / RoboMME | 短期存储全程条件化动作生成，但 episode 一结束全部蒸发。ReMem-VLA 最硬：*"At episode boundaries, we **hard-reset** the slot's recurrent state"*；MemoryVLA 的条目位置编码就是 `TE(episode timestep)` |
| **只写不读** | **Retrieve-then-Steer** | `B^(i)` 是**纯写入暂存区**——*"we maintain a **temporary buffer** to **record** candidate memory entries"*。**episode 内策略从不查询它**；被读的只有跨 episode 的 `M` |
| **两边都没有** | Dejavu / VLA-Pro | 整条 rollout 结束后原样 append；VLA-Pro 的 `H_<t` 只用来拼检索 query，无写出通路 |

**这正是"从 episode 级短/长记忆自演化到 lifelong 记忆"要跨的那道缝，而它目前是一道真空。**

### 2.2 第三条空白：现有的"提升"只有三种，没有第四种

【复算】现有全部层间提升是以下三者之一：

1. **逐字拷贝** —— R-t-S 把原始 `(k_t, a_t)` 整体并入 `M`，唯一加工是 progress-peak 前缀截断；Dejavu 原样 append。
2. **同层去冗余** —— MemoryVLA Eq.9 与 LaMem-VLA Eq.4–5 是**同一个** `argmax cos(相邻) → 平均` 算子；LaMem-VLA 明说 *"applies **the same** memory updating strategy to the long-term memory vault"*。**两层用同一条规则 ⇒ 层间本质上不存在差异。**
3. **抽象但只到文本/规划层** —— RoboMemory 的 VLM CRUD、MemVerse 的 `O_extract`、MEM 的 LLM 语义压缩、RoboHarness 的失败归因重写。**全都抽象成自然语言或图三元组，从不抽象成动作。** RoboMemory 甚至直言真机上技能库路线不可行：*"making it challenging to construct a **reusable, code-based skill library**"*。

> **没有任何一篇把 episode 级的动作/程序性记忆压缩、归并、泛化成一个结构上不同的长期表示。**
> 全库唯一形式化的抽象式巩固算子是 MemVerse 的 LTM→参数 SFT 蒸馏（Eq.7–8），但它作用在**对话知识图**上，**没有具身、没有动作空间**。

### 2.3 理论侧也是空的（只能当 framing，不能当 novelty）

【复算】Miras（*It's all connected*, ICLR'26）的四个设计轴——associative memory architecture / attentional bias / retention gate / memory learning algorithm——**全部描述同一个 `W`**。没有"记忆层数"轴，没有"层间写入策略"轴，没有 replay/rehearsal 轴。

- `consolidat` 在 Its_All_Connected **0 命中**；在 Titans / ATLAS 各 1 次且**只在参考文献里**。
- Miras Remark 3 论证连擦除都不存在（*"there is **no memory erasing or forgetting process**"*），把 forget gate 改名 retention gate ⇒ **单存储假设被写死在框架的哲学层面**。
- TNT 是唯一自称 hierarchical memory 的，但 local 层是**周期性重置**以换取 context parallelism，**local→global 零通路**。
- ATLAS 留了一句可直接引用的空缺声明：*"**no persistent learning or skill acquisition carries over** to new, independent global context once the memory is cleared"*。
- Parisi 2019 全文 8 个编号公式，**§2.3(CLS) 与 §3.4(CLS+replay) 两节零公式**，作者自认 *"the exact neural mechanisms remain **poorly understood**"*。

> **可以写的一句**：把 store-to-store 的转移算子形式化为 Miras 式框架的第五个轴，在数学上是空白的。
> **绝不能写的一句**：*"理论预言了这个空白"*——v3 critique §1.1 已经因为这句话被一手核对枪毙过一次。**这一条只做 framing，一个 Contribution 都不占。**

**四条必须守住的界**（与 idea 1 的表并列，不重复）：

| 邻居 | 它做到了什么 | 界在哪 |
|---|---|---|
| **Retrieve-then-Steer** | 冻结 π0.5 + 持久成功记忆；容量消融 `C ∈ {0,1k,2k,3k,4k,5k,∞} → 61.0/64.0/66.2/68.5/70.2/70.8/71.2`，**单调升、4k 后饱和、无下降**，满库走 **FIFO**（3.5k 上限）【复算·一手 PDF Table 6 p.17】 | 它的库来自**单场景、300 条轨迹、世界在其间不变**的短部署。**关键**：它的 Limitations 逐字写下了本文的题目——*"previously stored action priors may become **less informative or even misleading**"*、*"mechanisms for **detecting environment changes**"*。**问题的重要性由最强前作替我们论证；本文接着它往下做。同时这意味着抢跑风险已被证实（见 §11-1）。** |
| **RoboHarness (IROS'26)** | 七篇里**唯一**有真 consolidation（`consolidat` 20 次命中，其余六篇 0 次）：用新证据**就地改写旧条目的诊断文本与干预方案** | **已一手结案（`survey_memory_lifecycle.md` §2）：不构成致命冲突。** 它改写的是**自然语言诊断**、条目数**不减**、value **不含动作**、动机是 *"knowledge stagnation"*（旧条目的**结论**不够好）而非世界改变；`stale`/`non-stationar` 在它里面也是 0 命中。**但它逐字用了 "a self-evolving consolidation mechanism"** → **本文交出两个词：`consolidation` 不作方法名/Contribution 关键词（改用 `promotion` / `episodic→procedural abstraction`），`self-evolving` 全文禁用。** |
| **CLARE (RA-L'26)** | 模块化 adapter = 可增长、可寻址、**可删除**的记忆 | idea 1 的 v3 critique 已经用它枪毙过"条目级删除是唯一干净答案"这条主张。**本文不得复活"可撤销性"作为卖点**，只能把它作为 Table I 的一列（写入代价坐标系）。 |
| **Miras / Titans / Atlas** | 把 retention gate / forget gate 形式化为设计轴 | 它们**只覆盖参数化序列骨干**（Table 1 里 15 个模型全是），`external memory`/`database`/`RAG` 词频为 0【继承·v3 critique §1.1 一手核对】。**绝不能再写"理论预言了空白"** —— 只能写"我们把它的设计轴外推到它明确不覆盖的区域"，且这**只能当 framing，不能当 novelty**。 |

---

## 3. 主张句（Abstract 红线）

> 检索增强的冻结 VLA 已经证明：把部署中的成功片段存进一个持久库，能在不更新任何参数的情况下提升可靠性。**尚未被展示的是这个库在一个足够长、以至于世界本身发生了变化的部署里的行为**：它的价值是否仍随条目数单调增长；**在写入时可执行、在读取时已不可执行**的条目占多大比例；以及**检索侧的置信度能否看见这个差别**。

四个限定词，缺一不可：

- *long enough that the world itself has changed* —— 由**跨采集场次**保证（家电被移动过、衣物实例被换过、拉链被磨损过），不是模拟的时间戳
- *executable when written, no longer executable when read* —— 这是**条目的属性**，与读者能力无关（区别于 idea 1 的"读者本体不同"）
- *retrieval-side confidence cannot see it* —— 这是**机制**主张，直接推出设计结论
- *whether its value still grows with size* —— **必须写成"规模 × 漂移的交互"，不得写成"规模的主效应"**。见 §7.1：现有证据（R-t-S 单调升至饱和 61.0→71.2；ReCAP 单调升且未饱和 9.0→31.5）**全部支持"越大越好"**，主效应版本会被一手表格当场打脸。

**Abstract 红线（继承 idea 1 的纪律 + 本轮新增三条）**：
- 不得出现 first / novel / unexplored / we fill the gap
- 必须出现 **injection rate** 与 **harm rate**（主动交出"可以靠多弃权刷高"这一击）
- 必须出现 **N_max 的真实数字**，不得写 10⁵（v5 §6.7 已据实收窄为 10⁴–N_max）
- 必须写明 **frozen backbone ⇒ 这是 lifelong recall & recomposition，不是 lifelong learning**（v3 critique §2.6 的强制项）
- **★ 新增·命名雷区（三条，全部一手撞车）**：
  - `self-evolving` —— RoboHarness 摘要逐字 *"a **self-evolving** consolidation mechanism"*。**用户口语里的"自进化"在英文成稿里必须换词**（建议 `promotion` / `store-to-store abstraction`）
  - `consolidation` 作为方法名或 Contribution 关键词 —— 同上，RoboHarness 已占
  - `cross-task procedural memory` —— **VLA-Pro 的标题逐字**
  - `lifelong robot learning` —— LIBERO 的副标题
- **★ 新增**：差异化必须写成**机械描述**而非概念口号，每个从句都承重。可用的一句：
  > *a two-tier store whose short-term tier conditions the action expert within an episode and is distilled, by an abstracting promotion operator, into a cross-task long-term **action** memory that carries the grounding assumption under which it was written.*
- **★ 新增**：**这个 idea 被三篇论文写进了 future work，审稿人会知道**——MemoryVLA（*"building **lifelong memory through biologically inspired consolidation** that distills frequently reused experiences into permanent representations"*）、MEM（*"scale memory to last **beyond the horizon of a single episode**"*）、VLA-Pro（*"**continual memory expansion** … **hierarchical or compositional procedural states**"*）。
  → **贡献必须是"可运行的机制 + 可测的量"，绝不能是概念本身。**

---

## 4. 承重结构：**结构的作用是可审计性，不是压缩**

这是全文唯一的、不可替代的那句话。

一条**扁平的 episodic 条目**（obs 片段 + action chunk）**没有携带自己成立的前提**。它只能被相似度检索命中，而相似度看的是像素/嵌入，看不见"我写下这条的时候，微波炉在那个位置"。所以：

> **扁平库在结构上无法判断自己的条目是否仍然有效。**

一条**巩固后的 procedural 条目**（不变量 + 变异包络 + **显式接地假设**）携带了自己成立的前提：锚点系参数 `(â, o)` 或弧长轨道 `s`、容许的管半径、支持条目数、结果后验。所以：

> **结构化库可以对当前场景重新接地，把"我当时假设的锚点"和"现在实际的锚点"相减。这个残差是纯离线的、零机器人小时的、且不需要执行就能算出来。**

**P1′（唯一的核心主张）**：

> 存在一个**纯离线的接地残差统计量** `r(e, s_now)`，它对"条目 e 在当前场景 s_now 下是否仍可执行"的判别 AUC 显著高于：
> (a) 条目年龄 / 新近度（预测：**接近随机**）
> (b) 检索相似度本身（预测：**接近随机，因为相似度是被优化来忽略这类差异的**）
> 且该统计量**只有在条目被巩固成携带接地假设的形式之后才存在**——扁平条目上它无定义。

**这句话把"要不要做结构"从一个工程偏好变成了一个可证伪的命题。**

### 为什么 (a) 必须被主动测量、且必须报出来

审稿人的第一反应是"加个时间戳、丢掉老条目不就完了"。**这是本文的 82.8° 时刻**（对应 idea 1 里"绝不能只报朴素复制的 82.8°，必须报最优标定后的 17.8°"）：

> 必须自己先把最强的平凡修法做出来并报出它的残差。年龄是**事件驱动**的腐坏的坏代理：一条三个月前写的、关于一台从未移动过的洗衣机的条目完全有效；一条昨天写的、关于一台刚被推了 10 cm 的微波炉的条目是陷阱。
> **若 `AUC_age` 显著 > 0.7，本文的机制主张作废，退到 §6 的 fallback。**

### 死穴（必须最先测，成本近零）

**三个零机器人小时的 gate，任何一个不过，主张形态立刻改变：**

| Gate | 内容 | 成本 | 不过怎么办 |
|---|---|---|---|
| **G-A · 腐坏存在性** | 对存量**门任务**轨迹**逐 episode / 逐场次**拟合铰链螺旋轴 `(â, o)`，看轴参数是否随采集场次漂移；漂移量与 idea 1 实测的任务容差比较 | **0 机器人小时、0 GPU**（这条**同时是 idea 1 §10 待办第 3 条**，两篇共享交付物） | 若轴在全部场次上一致（残差 < 任务容差）→ **本组语料里没有自然腐坏**，全部漂移必须人为制造（合法但弱一档），且 Fig. 1 的 teaser 换成 staged drift |
| **G-B · 饱和存在性** | 纯离线：在真实语料上按 `N ∈ {10², 10³, 10⁴, N_max}` 对数下采样建库，算 precision@k 与跨任务误检率 | **0 机器人小时** | 若 precision@10 从 10² 到 N_max **平坦**（无干扰、无饱和）→ **规模那条腿死亡**，全文收缩为纯 staleness 论文（仍然成立，见 §6） |
| **G-C · 巩固可行性** | 在 `(任务, 锚点类型, 阶段)` cell 内做锚点系轨迹聚类，报**管半径分布**与巩固比 `ρ = |L2|/|L1|` | **0 机器人小时** | 若管半径普遍大于任务容差（簇内根本没有不变量）→ **巩固算子无意义**，退到"只做腐坏检测、不做巩固"的单腿论文 |

> **三个 gate 全部离线、全部本周可做、全部与 idea 1 的既有待办重叠。这是本 idea 相对 idea 1 最大的工程优势：它的生死判定不消耗任何机器人小时。**

---

## 5. 四级记忆与两个算子（方法侧的全部内容）

用户的原话是"从任务的 episode 级别的长短记忆，自进化到 lifelong 记忆"。落成可写的形式：

| 级 | 名称 | 内容 | 生存期 | 谁写 | **是不是本文的贡献** |
|---|---|---|---|---|---|
| **L0** | 工作记忆 | episode 内的观测/chunk 历史 | episode 结束即清零 | 采样器自身 | ❌ **不是**。MemoryVLA / MEM / ReMem-VLA / LaMem-VLA / RoboMME 全在这一层，且**都需要训练**。本文冻结策略，L0 只作为阶梯底端被引用与划界。**一手证据**：ReMem-VLA *"At episode boundaries, we **hard-reset** the slot's recurrent state"* |
| **L1** | 情景记忆 | 单条成功片段（idea 1 的条目 schema，RDT-1B 128 维） | 直到被提升或淘汰 | **写入门控**（VLAC-8b + HELP 分段） | ❌ **不是**。这正是 R-t-S / Dejavu / RECAP 的**整个**库。**一手证据**：R-t-S 的 `B^(i)` 是 *"a **temporary buffer** to **record** candidate memory entries"*，**episode 内策略从不查询它** |
| **L2** | 程序记忆 | 一簇 L1 的**不变量 + 变异包络 + 显式接地假设 + 结果后验** | 长期 | **提升算子（本文）** | ✅ **且这是全库第四种提升方式**：现有三种是逐字拷贝 / 同层去冗余 / 抽象到文本，**没有一种抽象到动作**（§2.2） |
| **L3** | 语义 / 任务先验 | 任务级约束统计（铰链角可达域、弧长剖面族）与失败模式 | 终身 | 聚合（本文，更便宜） | ✅（次要） |

**两个算子（"自进化"的全部实质，且全程零策略梯度）**：

```
提升 PROMOTE:  L0 → L1   = 写入门控（先验：VLAC / HELP）          ← 不主张
               L1 → L2   = 巩固：同 cell 内 K 条 L1 → 1 条 L2      ← 主张
               L2 → L3   = 聚合：多条 L2 → 任务级约束统计           ← 主张（次要）

降级 DEMOTE:   L2 → 隔离 = 接地残差 r(e, s_now) 超出自身管半径      ← 主张（核心）
               L1/L2 → 淘汰 = 结果后验 Beta(α,β) 的下界低于阈值      ← 主张
```

**唯一被更新的量是几何不变量与计数，没有任何梯度到达策略。** 这一条同时解掉了 v3 critique §2.5 指出的内部矛盾：

> v3 的 SQ2 想把记忆**蒸馏进权重**，而 §3 又把"条目级可删除"当卖点——一旦蒸馏发生，删条目删不掉知识。
> **本文的立场：巩固发生在库内，不进权重（consolidation without distillation）。** 这不是回避，这是**被那份对抗审查逼出来的、更强的立场**：它让"删掉一条 L2 就删掉那簇经验"在数学上仍然成立。

### L2 条目的具体形式（直接复用 idea 1 的③层机器，零新增前端）

```
L2 = ( cell_id,
       ξ̄(u)        锚点系下的中位轨迹，u = 约束坐标（门：θ；拉链：弧长 s）
       R(u)        逐点管半径（切空间协方差；SO(3) 部分用 covariates/so3.py 的 Karcher 均值）
       G           显式接地假设：写入时的锚点参数 (â, o) 或轨道标定
       n, Beta(α,β) 支持条目数与结果后验 )
```

> **关键：`G` 这一项是全文的机制承重点。** 扁平 L1 条目没有 `G`，所以腐坏在它上面**不可观测**；L2 有 `G`，所以 `r(e, s_now) = d(G, ĝ(s_now))` 可算。
> **"结构 ⇒ 可审计" 这条因果链就是靠 `G` 成立的，不是靠聚类省了空间。**

---

## 6. 若主张不成立：两条已预注册的 fallback（按 gate 分流）

**F-1（G-B 不过，规模腿死）· 纯腐坏论文**
> *Staleness in deployment memory.* 我们量化"写入时可执行、读取时已不可执行"的条目比例，给出一个零成本的离线判别量，并证明它优于年龄与相似度。
> 代价：Contribution 从 4 条降到 3 条；Fig. 4（scaling 曲线）降为补充材料。**主线不死。**

**F-2（G-A 不过，语料里没有自然漂移）· staged-drift 论文**
> 全部漂移由预注册规则制造（家电位姿 ±8 cm/±10° yaw、衣物实例轮换、拉链磨损循环数）。
> **注意这不是致命伤**：idea 1 的 v5 §6.8 修法 1 **本来就要**对门族做位姿随机化来制造 headroom，§6.8 修法 6 **本来就要**准备 ≥3 件物理实例轮换来控制磨损。
> **idea 1 把非平稳性当作必须控制的混淆；本文把同一批操作当作被测的自变量。同一批机器人小时，两篇论文各取所需。**
> 代价：措辞一律为 "drift induced under a pre-registered protocol"，**绝不写 "natural drift over months"**；外部效度写进 Limitations。

**F-3（G-C 不过，簇内无不变量）· 只做检测不做巩固**
> 退到"腐坏检测 + 淘汰"，删掉 L2/L3 与巩固算子。此时 `G` 必须直接挂在 L1 上（写入时一并记录锚点参数），机制主张仍然成立，但"结构"的论证被削弱为"元数据"。**这是最弱但仍可发表的形态。**

---

## 7. 三个支撑性发现（都不需要新硬件）

### 7.1 部署经验的 scaling —— **必须写成交互，不能写成主效应**（本轮调研最大的一次修正）

**先摆出会打脸的证据**（全部一手，`survey_memory_lifecycle.md` §4）：

| 来源 | 曲线 | 形状 |
|---|---|---|
| R-t-S Table 6 | `C = 0/1k/2k/3k/4k/5k/∞` → `61.0/64.0/66.2/68.5/70.2/70.8/71.2` | **单调升，4k 后饱和，无下降** |
| ReCAP Fig. 7 | 池 `11/17/23/29/35` 任务 → `9.0/18.5/19.5/22.0/31.5` | **单调升，未饱和** |
| Dejavu Fig. C.1 | `0 → 1000` | 单调升，边际递减 |

> **"库越大越差"若作为主效应写出来，第一个审稿人就会拿 R-t-S 的 Table 6 打过来。**

**唯一的两条反向证据，机理都不是"库大"**：
- VLA-Pro top-k：`k=2 → 20.9`，`k=3 → 16.4`。这是**检索条数**多了 → 对应 `Δ_inter`。
- Dejavu Fig. C.5：部署 500 episode，*"appending **all** rollouts **gradually harms performance**"*，只写成功则不会 → 对应 `Δ_write`。**这是全族唯一一条随时间退化的曲线，而它的成因恰好是本文五项归因的第一项。**

**→ 主张改写**：

```
旧（会被打脸）：  SR(N) 存在内部极大值 N*，N > N* 之后下降
新（可辩护）：    SR(N | drift = 0) 单调饱和     ← 这正是 R-t-S 与 ReCAP 已观测到的
                 SR(N | drift > 0) 非单调       ← 陈旧条目占比随 N 增长
                 主张 = 规模 × 漂移的交互项显著 ≠ 0
```

**三重好处**：
1. **把最强前作的结果变成自己模型的特例**（`drift = 0` 那一档），而不是与它冲突。这是能拿到的最强位置。
2. **解释了为什么至今没人看到下降**——现有全部实验都在单场景、短部署、世界不变下跑，这是七篇实验设定逐条核实的结果，不是猜测。
3. **把本组的独占资源变成主张的必要条件**：只有同时拥有跨场次真实语料 + 冻结真机策略的组才能观测这个交互。

**设计后果**：主端点是 **2×2 析因**（`{单场次库, 跨场次库} × {小 N, 大 N}`），**不是一条曲线**。Fig. 3 画两条曲线 + 交互项，不画一条。

**诚实纪律**：离线部分（P@k、跨任务误检率）是**曲线**，真机部分只有 **2×2 四个格**（每格 20 成对 trial）。**图上两者必须用不同图元，caption 明写哪条是 offline proxy；Abstract 里的形状主张只能建立在离线量上，SR 只能说 "consistent with"。**

### 7.2 lifelong gap 的五项归因（Fig. 5，继承 idea 1 的 oracle 阶梯纪律）

把"扁平库在 N_max"与"oracle 库"之间的差拆成：

| 项 | 含义 | oracle 怎么给 | 成本 |
|---|---|---|---|
| `Δ_write` | 写入门控假阳（VLAC precision < 1） | 只保留人工确认成功的条目 | 离线，需人标 ~500 条（v5 §5.6 **本来就要做**） |
| `Δ_redun` | 近重复条目挤占 top-k | 按真值簇去重 | 离线，免费 |
| `Δ_stale` | 写入时可执行、现在不可执行 | 按真值漂移标签过滤 | 离线，免费（漂移事件有记录） |
| `Δ_inter` | 跨任务/跨阶段误检 | 检索限制在真值同 cell 内 | 离线，免费 |
| `Δ_cap` | 残差（top-k 只能承载这么多） | — | — |

**预注册**：若任一 Δ < 0，禁止画堆叠柱状图，改画阶梯折线并声明"这是一串干预，不是方差分解"（逐字继承 idea 1 §5.3）。

### 7.3 写入代价坐标系（Table I，继承 v3 critique §2.4）

**这张表是本文对抗 "ER 成功率更高" 这一击的唯一答案**——它换坐标系而不是比数字。

| | ER（梯度回放） | CLARE（adapter 扩展） | **本文（结构化零梯度库）** |
|---|---|---|---|
| 新技能写入耗时 | 小时 | 分钟~小时 | **秒** |
| 写入所需数据量 | 数十条 | 数十条 | **1 条** |
| 部署中在线可写 | 否 | 否 | **是** |
| 删除某技能 | 做不到 | 删 adapter | 删条目/删 L2 簇 |
| **库变大之后是否退化** | 不适用 | **【本文测量】** | **【本文测量】** |
| **世界变化后是否可检出** | 否 | 否 | **是（接地残差）** |

> 最后两行是本文新增的两列坐标，也是这张表相对 v3 critique 版本的净增量。

---

## 8. 实验骨架（只写支撑主张所必需的）

### 8.1 本体：**单本体**，这是与 idea 1 去重的硬规则

> **本文只用一台双臂 Piper 作 writer=reader。跨本体是 idea 1 的轴，本文一个字都不碰。**

第二台（PiperX）的唯一用途：**在另一台独立台架上重复同一条 scaling 曲线**，作为"这个现象不是单台机器的性质"的复现，**不作跨本体读写**。措辞一律为 "replicated on a second, independently deployed platform"，**绝不写 cross-embodiment**。

**收益**：机器人小时减半；与 idea 1 的实验可在两台台架上并行；审稿人不会把两篇看成一篇。

### 8.2 任务集：直接沿用 idea 1 的 confirmatory 集

门（4 台不同铰接家电）+ 拉链（3 个不同的包）= **7 个客观自动判定的变体**。叠衣降 exploratory。

**为什么这个任务集对本文比对 idea 1 更合适**：本文的接地残差 `r` 需要一个**可标定的锚点**。门的铰链螺旋轴与拉链的弧长轨道都是一次性物理标定就能拿到真值的（v5 §6.7 修法 7 已限定 oracle 阶梯"只在 D/Z 两族跑"）。**叠衣没有 anchor-oracle，本文正好不需要它。**

### 8.3 漂移的四个来源（全部已在 idea 1 的计划内，零边际硬件成本）

| 来源 | idea 1 里的角色 | 本文里的角色 | 成本 |
|---|---|---|---|
| 跨采集场次的家电位姿变化 | §1.7 后果 C 的**待查项** | **自变量**（G-A 直接测） | 0 |
| 家电位姿 ±8 cm / ±10° yaw 随机化 | §6.8 修法 1：**为门族制造 headroom** | **staged drift 发生器** | 0 |
| ≥3 件物理实例轮换 | §6.8 修法 6：**控制磨损混淆** | **实例漂移** | 0 |
| 拉链磨损 / 衣物固化折痕 | §6.8 修法 6：**必须被控制的非平稳性** | **自然漂移** | 0 |

> 一句话：**idea 1 花力气把这四样东西压成噪声，本文把同样四样东西读成信号。**

### 8.4 腐坏判别的基线表（这一张决定 Contribution 1 的成色）

| # | 判别量 | 需要什么 | **何时可得** | 预期 |
|---|---|---|---|---|
| B1 | 检索相似度（R-t-S 默认门控） | 无 | 检索时 | **≈ 随机**（承重预测） |
| B2 | 条目年龄 / 新近度 | 时间戳 | 检索前 | **≈ 随机**（承重预测；且这是"平凡修法"，必须自己先做） |
| B3 | 策略侧 UQ：velocity-field disagreement | **M=2 的 ensemble**（原文实测 ensemble size 对标定影响很小） | **执行开始后** | 强【一手：`covariates/2606.18043.pdf`，失败检测 Acc 0.67 / TPR 0.79 / TWA 0.54；校准 −Spearman 0.71±0.03，优于 GU 0.62 / Action-L2 0.50 / ACE 0.31】 |
| B4 | 去噪方差（DVAC 式，单模型） | 无 ensemble | **执行开始后** | 中等【一手：`covariates/2606.03847.pdf`】 |
| **B5** | **本文：接地残差 `r(e, s_now)`** | **L2 的 `G` 项** | **✅ 检索之前** | **≈ B3 的判别力** |

> **★ 论证轴必须是"何时可得"，不是"便宜几倍"。**
> VFD 的 ensemble 只有 **M=2**，"便宜 K 倍"里 `K=2`——**这不是卖点，写出来反而显得在凑优势**。
> 真正的差别是结构性的：**B3/B4 只在执行开始之后才有定义**（它们度量的是策略在当前观测下的不确定度），所以它们能做的是"执行到一半发现不对、中止"；**B5 在条目被检索出来之前就能算**，所以它能做的是"根本不把这条拿出来"。
> **一个是熔断器，一个是准入。这两件事不可互相替代，本文两个都报。**
> **B3/B4 是必比项，不是可选项。** 不比会被问"为什么不用策略自己的不确定度"，而这一问有两篇现成论文撑腰。
> **阈值标定协议照抄 VFD 的做法**（conformal prediction + 10 条成功 rollout），这样比较才公平，且省掉一轮"你们的阈值是调出来的"。

### 8.5 机器人小时（单台，MVP）

沿用 v5 §6.6 的实测时长：门 0.6 min / 拉链 2.1 min / rollout（含复位），失败因子 1.4。

| arm | 内容 | rollout 数 | 小时（×1.4） |
|---|---|---|---|
| 规模端点（**2×2 析因**：`{单场次库, 跨场次库} × {N_small, N_max}`） | 4 格 × 7 变体 × 20 成对 | 1120 → 按门/拉链混合均分 | **~26** |
| 腐坏端点 | `{fresh, stale} × {门控开, 关}` × 4 变体 × 20 成对 | 640 | **~20** |
| 提升消融（L1 vs L2 vs L2 无包络） | 3 × 4 变体 × 15 | 180 | **~6** |
| 判别量基线 B3/B4 在线对照 | 2 × 4 变体 × 15 | 120 | **~4** |
| A/A 噪声地板 + π_d pilot | 继承 v5，不可砍 | — | **~6** |
| **合计** | | | **≈ 62 robot-hours** |

**对比**：idea 1 的 MVP 是 75–85 h。本文 ≈62 h，且**离线部分（三个 gate + 五项归因的 oracle）全部零机器人小时**。

---

## 9. 与 idea 1 的去重协议（**必须现在定死，否则两篇互相抢跑**）

| 维度 | idea 1 | 本文 |
|---|---|---|
| 轴 | **谁能读**（本体） | **多久还能读**（时间/规模） |
| 本体 | 双向 Piper ↔ PiperX | **单本体**；第二台只作复现 |
| 承重主张 | 四层 value 的交叉点 `ℓ*` / 逐阶段 `Δ𝔸` | **接地残差可判腐坏，年龄与相似度不能** |
| 谁拥有 "similarity ≠ executability" 这句话 | **idea 1**（其 `reframe` §1.3-N5 已升为主端点，机制=读者运动学） | 本文**不得**把它写成 headline；只能作为 `Δ_stale` 这一项的机制解释，且机制不同（**世界变了** vs **读者不同**） |
| harm rate | 跨本体 harm | **时间 harm**（老条目的 harm），定义式必须并列写出且**不可 pooled** |
| Fig. 4 | 层级谱系交叉点 | **规模曲线 + 腐坏 ROC** |
| 共享交付物 | 铰链轴拟合、per-task φ、VLAC precision 标定、A/A 地板、π_d pilot | **同上，一次做完两篇都用** |

**双盲下的实操问题（必须现在处理）**：若两篇同期在审，本文**不能**写 "our prior work"。处理办法：本文所有需要 idea 1 结论的地方**自带最小复算**（例如接地残差需要的 IK 可行率，本文自己跑一次逐任务版），并在 Related Work 里把 idea 1 作为**匿名并发投稿**处理。**这一条不落实，会被判自引泄漏身份。**

---

## 10. 这篇文章长什么样

**转轴**：不是"我们做了一个分层记忆"，是"**我们测出了一个部署记忆库在变大、变老之后会发生什么，并证明结构的价值在于可审计性而不是压缩**"。

**Contributions（四条，按可辩护性降序）**：

1. **一个纯离线的接地残差判别量**，对"条目是否已腐坏"的 AUC 显著高于条目年龄与检索相似度（两者预测为**接近随机**），并与需要**执行才能得到**的策略侧 UQ 同档。**这是最硬的一条，且判定成本为零机器人小时。**
2. **一条部署经验的 scaling —— 写成规模 × 漂移的交互**：`drift = 0` 下单调饱和（复现 R-t-S 的 61.0→71.2 与 ReCAP 的 9.0→31.5），`drift > 0` 下非单调。**把最强前作的曲线变成本文模型的特例。**
3. **一个抽象式的提升算子**（L1→L2），把 episodic 动作条目压成携带**不变量 + 变异包络 + 显式接地假设**的 procedural 条目。**这是全库第四种提升方式**——现有三种是逐字拷贝 / 同层去冗余 / 抽象到文本，**没有一种抽象到动作**。且它**留在库内、不进权重**，所以"删掉一条 L2 就删掉那簇经验"在数学上仍成立。
4. **lifelong gap 的五项归因**（write / redundancy / staleness / interference / capacity），全部由离线 oracle 给出，无事后人工归因。**其中三项在文献里已有独立佐证**（`Δ_write` ← Dejavu Fig. C.5 与 R-t-S Table 5；`Δ_inter` ← VLA-Pro top-k 回落；`Δ_cap` ← R-t-S 的 ∞ 档天花板），**两项是新增**。

**明确不主张**：
- 注入机制（R-t-S；GR00T N1.7 的 RTC 亦有工业实现）
- 条目 schema（RDT-1B 128 维）
- 写入门控与 rollout 分段（VLAC / HELP）
- 锚点系表示（point-track / flow 族 9+ 篇）
- 检索机制（VINN / Di Palo & Johns / RAM）
- **"记忆应该分层"这个想法本身**（RoboMemory / MemVerse 在规划层已有；CLS 理论更早）
- **"offline memory consolidation" 这个词组**（RoboHarness 已占用，本文改用 `promotion`）
- **"把 lifelong 记忆做出来"这个目标本身**（MemoryVLA / MEM / VLA-Pro / R-t-S **四篇的 future work 都写了**）

**必须预备的五刀与答法**：

| 刀 | 答法 |
|---|---|
| *"这四篇论文的 future work 里都写了你这个想法。"* | **对，而且我们主动引用了这四段原文。** 被认领的是**目标**；本文交付的是**一个可运行的机制加四个可测的量**，其中两个量（`AUC_age ≈ chance`、规模×漂移交互）在这四篇里都不存在。 |
| *"This is Neural Episodic Control with a VLA backbone."* | NEC 存的是**值函数表**，写入靠 TD 目标、读出靠最近邻插值，且假设**平稳 MDP**。本文的被测对象恰恰是非平稳性；策略冻结，库不参与任何值估计。 |
| *"加个时间戳丢掉老条目不就行了？"* | **我们做了，AUC = 【G-1 后填】，接近随机。** 腐坏是**事件驱动**的，不是年龄驱动的。 |
| *"ER 的成功率更高。"* | 换坐标系，见 §7.3 的 Table I，并主动承认 ER 在 SR 上可能更高。 |
| *"冻结主干，你根本没在 lifelong learning。"* | 主动写：this is lifelong **recall & recomposition**，并给出"基座能力内 vs 能力外"的任务二分实证（v3 critique §2.6 的强制项）。 |

---

## 11. 这篇文章可能死于什么（按致命度）

| # | 风险 | 有没有解 |
|---|---|---|
| **1** | **抢跑（已由一手证据证实，升为头号风险）**：R-t-S 的 Limitations 逐字写着 *"more **structured memory organization**, **long-term forgetting**, task-aware indexing, and **mechanisms for detecting environment changes**"* —— **本文四条 Contribution 里的三条，写在最强前作自己的路线图上。** 另有 MemoryVLA / MEM / VLA-Pro 三篇也把这个方向写进 future work | 无解（这是竞争）。**对策：G-A/G-B 一过立即 arXiv 占位，与 idea 1 的占位合并成一次；此后每月核一次 R-t-S 的新版本。** 并且贡献必须落在**可运行的机制 + 可测的量**上，因为**概念本身已经被四篇论文公开认领为未来工作** |
| **2** | 语料的场次/时间元数据不存在或不可靠 | **可能无解。这是单点故障，必须第一周确认。** 若采集时没记录场次与日期，"时间轴"就没有真值。三条替代真值见 `paper_outline_v1.md` §0.6-A |
| **3** | 三个 gate 有两个不过（无腐坏 + 无饱和/交互） | 有解但很痛：退到 F-2 + F-1 的交集 = staged drift 上的腐坏检测。**仍可发表但只剩一条腿** |
| **4** | 巩固后的 L2 条目在注入时不如原始 L1（管的中位轨迹是"谁都不像"的平均） | **真实风险。** 对策：L2 存 **medoid（真实存在的那一条）**而非 mean；预注册消融 A2。**若 A2 显示 L2 显著劣于 L1，结构只作检索/审计层，不作注入内容——这仍是一篇完整且更诚实的论文** |
| **5** | 缺一个合适的 benchmark | **最实际的风险。** RoboMME 严格 episode 内；MemoryBench 约 300 帧且 ReMem-VLA 已刷到 94.5%；LIBERO / SimplerEnv / RoboTwin **本身不要求跨 episode 记忆**（R-t-S 在 LIBERO-10 上只有 92.4→94.4，天花板明显）。→ **必须自建"连续部署、任务序列、不清库"的评测协议。** 唯一可借的现成范式：RoboMemory 的 *"run each task twice **without clearing long-term memory**"*（26.67%→46.67%） |
| **6** | 真机只有 2×2 四个格，"曲线"被判为四个点 | 无技术解。措辞纪律见 §7.1 末段 |
| **7** | 与 idea 1 被判 salami slicing | 有解：§9 的去重协议 + 单本体设定 + 完全不同的 Fig. 3/4。**但两篇不得在同一窗口投同一个 venue** |
| **8** | RoboHarness 的 consolidation 命中 | **已一手结案：不命中**（`survey_memory_lifecycle.md` §2）。**代价是交出 `consolidation` 与 `self-evolving` 两个词** |

---

## 12. 最小可发表形态

**confirmatory = 门 + 拉链 + 单本体 + 三个离线 gate + 两个真机端点（规模、腐坏）。**

保留：三个零成本 gate / scaling 曲线（离线全曲线 + 真机 3 点）/ 腐坏判别五基线（含 B3 UQ 与 B4 去噪方差）/ 五项归因 / 写入代价坐标系 Table I / harm rate + injection rate + base SR / L2-vs-L1 注入消融（不可砍，见风险 7）/ A/A 地板 + π_d pilot。

砍掉：L3 语义层（降为一行）/ 叠衣族 / 跨本体任何内容 / 检索延迟-规模曲线（预注册不复活）/ 仿真 / 除 R-t-S 与 RoboHarness 之外的全部 baseline 复现。

**MVP 成立的理由**：不可替代性在"**一个真机上灌到 10⁴ 条、跨过真实世界变化的部署库，以及在它上面做的第一次生命周期测量**"，不在算子的精巧。

---

## 13. 立即待办（按依赖排序，前四条本周，全部零机器人小时）

1. **【最高优先·单点故障】确认存量语料是否记录了采集场次与日期。** 没有时间真值，本文的整条时间轴不存在。这一条的答案决定要不要启动。
2. **【G-A，零成本】逐场次拟合门任务的铰链螺旋轴**，看轴参数漂移量 vs 任务容差。**这条同时交付 idea 1 §10 待办第 3 条。**
3. **【G-B，零成本】2×2 析因的离线版**：`{单场次库, 跨场次库} × N ∈ {10², 10³, 10⁴, N_max}`，算 precision@k 与跨任务误检率，**看交互项**（不是主效应）。顺带落实 `N_max` 的真实数字（v5 §6.7 估 10k–14k 条/本体）。
4. **【G-C，零成本】锚点系轨迹聚类，报管半径分布与提升比 ρ。**
5. ~~逐字读完 RoboHarness~~ **✅ 本轮已结案**（`survey_memory_lifecycle.md` §2）：不构成致命冲突，代价是交出 `consolidation` 与 `self-evolving` 两个词。
6. **【待核】补齐威胁登记表**：Remember Smarter (2608.15269)、SkillMemo (2608.05970)、RTCF (2608.04527)、ExpReS-VLA (2511.06202, ICRA'26)、**Reuse Before You Retrieve (2608.17484 — 设计空间元分析，本文分类法必须与它对齐)**、RAEA (2404.11699, CVPR'24) —— 六篇本会话全网不可达，**投稿前必须逐篇一手核实**。
7. **【一天】把 B3（VFD，M=2 ensemble）与 B4（去噪方差）在 openpi 的 flow 采样器上接通**，与 idea 1 的"while_loop 展开为 Python 循环"是同一件工程（v5 §10 待办第 7 条）。**再次共享交付物。**
   > **注意**：VFD 的 ensemble 只有 **M=2**（作者实测 ensemble size 对标定影响很小），所以"比 ensemble 便宜 K 倍"里 `K=2`。**成本轴不能作为唯一优势**；真正的差别是**事前 vs 事中**——接地残差在检索之前就能算，VFD 必须执行起来才知道。
8. **【设计】自建"连续部署、任务序列、不清库"的评测协议。** 现有 benchmark 全部不合用（风险 5）。唯一可借的范式是 RoboMemory 的 *"run each task twice without clearing long-term memory"*。**这一条必须在冻结实验设计之前定稿。**
9. **【决策】投稿目标**：ICRA 2027 截止 **2026-09-16**（16 天），**本 idea 不可能赶上**。见 `paper_outline_v1.md` §0.0 的日历。
10. ~~episode 级短期层（L0）的角色~~ **✅ 2026-08-31 已决策：只作边界，不实现**（`paper_outline_v1.md` §8）。方案 B（episode 内条目立即可检索 + 在线 progress 门控）转为 **idea 3**。
