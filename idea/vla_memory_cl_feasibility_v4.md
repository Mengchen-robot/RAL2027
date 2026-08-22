# 跨本体持久动作记忆：面向 IEEE RA-L 的科研可行性报告（v4 · 重构版）

日期：2026-08-22
目标 venue：**IEEE RA-L（滚动投稿，2027 Q1–Q2）**，接收后可挂 IROS 2027 / ICRA 2028 presentation option
v3 → v4 的变更依据：`review_v3_critique.md`（逐条附 arXiv ID 与 PDF 原文证据）

---

## 0. v4 相对 v3 改了什么

**放弃的主张**（均已被证伪，证据见审查报告）：

| v3 主张 | 为何放弃 |
|---|---|
| "外部持久记忆在 VLA 动作层完全空白" | RAEA (CVPR'24)、Retrieve-then-Steer (2605.10094)、RECAP (2606.15631)、Dejavu (2510.10181)、RTCF、RoboHarness (IROS'26) 已占据；RoboMME (ICML'26) 已是该方向的**基准论文** |
| "SQ3 记忆注入 flow expert 是开放问题" | Retrieve-then-Steer 已做中间态注入 + 置信度引导；RAGDP、WarmPrior、LAFM 已做源分布替换 |
| "Behrouz 统一理论预言了这个空白" | Miras (2504.13173) Table 1 只统一参数化序列骨干；全文 `RAG`/`external memory`/`database` 各出现 **0** 次 |
| "遗忘率是核心指标" | Liu et al. (ICML'26, 2603.03818)：预训练 VLA 抗遗忘，**简单 ER 有时零遗忘** |
| "条目级删除是唯一干净的可撤销方案" | CLARE (RA-L'26) 的 adapter 同样可删可路由 |

**保留并提升为主线的**：v3 的 SQ5（跨本体）。它是唯一**结构性**未被占据的方向，且与本组双本体资源唯一匹配。

**新增的**：跨本体检索的 key 对齐问题（v3 完全没意识到）、迁移方向不对称性、共享记忆池的净收益检验。

---

## 1. 工作条件

| 资源 | 规模 | 在 v4 中的作用 |
|---|---|---|
| 真机数据 | 数百小时 | ① 领域微调 FR3 / 移动臂基座；② **把记忆库灌到 10⁴–10⁵ 条**以研究规模效应——这是竞争者（单环境短部署）拿不到的量级 |
| 算力 | 百卡（5090 + H20） | H20：双本体基座微调、检索服务；5090：仿真并行 rollout、跨本体对齐模块预训练 |
| 本体 | **Franka FR3（7 DoF 定基）+ π0.5 同款移动机械臂（臂 + 底盘）** | **本论文的全部立论基础**。桌面 ↔ 移动 是"低 DoF ↔ 高 DoF、定视角 ↔ 变视角"的干净二元对照 |

---

## 2. 核心结论（TL;DR）

检索增强的冻结 VLA 在 2026 年已经**跑通并拥挤**。但把这一族工作全部摆开会发现一个共同前提，没有人写出来过：

> **所有能持久的机器人记忆，都只有写它的那个本体能读。**

- RECAP 明说：新任务靠往检索池追加演示即可免训练吸收，**但换本体需要微调**。
- VLA-Pro 的记忆条目是 LoRA 权重 → 天然绑死骨干与本体。
- CLARE 的条目是 adapter → 同上。
- Retrieve-then-Steer / Dejavu / RTCF / RoboHarness → 单机器人、单环境、存原始 obs-action 段。

反过来，**能跨本体读的记忆全是易失的**：RoboTTT / MimicDroid 证明了机器人可以从**人类**视频里 in-context 地学（这已经是最激进的跨本体读取），但 context 用完即弃，不积累。

于是格局是一个**结构性空缺**，而不是一个"还没人做"的偶然空缺：

```
                      谁能读这段记忆 →
              只有写它的那个本体            任意本体
        ┌────────────────────────────┬──────────────────────────┐
   持久 │ RECAP, Retrieve-then-Steer, │  ★ 空白（本文）           │
  （跨  │ Dejavu, RTCF, RoboHarness   │                          │
   部署 │ VLA-Pro (LoRA), CLARE(adpt) │  结构性原因：一旦要求持久 │
   保留）│ ER / 权重 / RL 后训练全家桶  │  且有用，现有方案都把记忆 │
        │                            │  存成了本体绑定的表示     │
        ├────────────────────────────┼──────────────────────────┤
   易失 │ MemoryVLA, LaMem-VLA,       │ RoboTTT, MimicDroid       │
  （用完│ ReMem-VLA, MEM              │ （人类视频 → 机器人，     │
   即弃）│ （episode 内工作记忆）        │  已证跨本体可读，但不积累）│
        └────────────────────────────┴──────────────────────────┘
```

**生态位判断**：右上角空缺不是因为没人想到，而是因为**"存什么"这个问题被绕过去了**——大家都默认存"这个机器人当时做了什么"。本文的主张是：**记忆的价值上限由它的表示层级决定，而不是由检索或注入机制决定**；把 value 分层重构之后，记忆可以比写它的那个身体活得更久。

---

## 3. 相关工作（诚实重绘）

### 3.1 检索增强的冻结策略（本文的直接基础，不是竞争对手）

这一族在 2025–2026 已经成立。**v4 的姿态是站在它们肩上，而不是宣称填补空白。**

| 工作 | ID / venue | 做了什么 |
|---|---|---|
| RAEA | 2404.11699 · CVPR 2024 | policy retriever + external policy memory bank，最早的形态 |
| Dejavu | 2510.10181 | 冻结 VLA + 检索执行记忆，部署中持续扩充 |
| **Retrieve-then-Steer** | 2605.10094 | 冻结 VLA + 成功经验长期记忆 + 检索 action chunk + **注入 flow 采样器中间态** + 置信度自适应引导；**本文的读出机制直接采用其形态** |
| **RECAP** | 2606.15631 | 追加演示到检索池 = 免训练吸收新任务；**自承换本体需微调** |
| RoboHarness | 2603.24060 · IROS 2026 | 冻结 π0/π0.5/SmolVLA 的记忆 harness + 离线 Memory Consolidation |
| RTCF | 2608.04527 | training-free 频域残差修正 |
| Remember Smarter | 2608.15269 | π0 上即插即用双曲经验空间，LIBERO-Plus 53.6→70.6 |
| SkillMemo | 2608.05970 | 技能级 episodic memory bank |
| **RoboMME** | 2603.04639 · **ICML 2026** | **VLA 记忆基准 + 分类法 + 14 个 memory-augmented π0.5 变体横评**——本文必须与其分类法对齐并在其上报数 |
| Reuse Before You Retrieve | 2608.17484 · ECCV'26 wksp | 冻结策略的测试期增强设计空间元分析 |

血统提醒：Model-Free / Neural Episodic Control (1606.04460, 1703.01988)、Continuous Episodic Control (2211.15183)。**预期审稿意见"This is NEC with a VLA backbone"必须有备答**（备答：NEC 的记忆是单智能体单体的 Q 值表，本文的命题恰恰是记忆的**跨体可读性**，这是 NEC 从未涉及的维度）。

### 3.2 模块化参数记忆（可删除性的真正占位者）

CLARE (2601.09512, RA-L'26)：模块化 adapter + 按需自主扩展 + 部署期无标签 autoencoder 路由。VLA-Pro (2605.29562)：跨任务程序性记忆迁移，存 LoRA 条目并在推理时融合。

**这两者已经具备条目级可删除性**，所以"可撤销性"不再是本文的卖点，而是**本文与它们共享的性质**。本文与它们的差异只有一条，但是结构性的：**权重型条目不可能跨本体。**

### 3.3 权重基底与 RL 后训练

VLA-RFT (2510.00406)、VLAC (2509.15937)、RIPT-VLA (2505.17016)、SOP (2601.03044，基座是 **π0.5** 不是 GR00T)、SRPO (2511.15605)、PriorVLA (2605.10925)、Self-improving VLA (2511.00091, ICLR'26)、CRL-VLA (2602.03445)、LifeLong-RFT (2602.10503)。

**与本文正交**：它们改权重，本文不改权重；记忆库可以记录后训练产生的部署经验并跨本体复用。

### 3.4 episode 内记忆

MemoryVLA (2508.19236, ICLR'26)、MEM (2603.03596, Physical Intelligence)、ReMem-VLA (2603.12942)、LaMem-VLA (2607.07608)、Explicit Language Memory (2608.04765)。全部服务单任务长时程，跨 episode 清零。

### 3.5 遗忘到底存不存在（本文刻意不站队）

Info-VLA (2603.13335) 说 "severe catastrophic forgetting"；Liu et al. (2603.03818, ICML'26) 说 "remarkably resistant… simple ER sometimes achieves **zero** forgetting"。两篇正面矛盾且都在 LIBERO 上。

**v4 的处理：把遗忘率降级为报告项而非主张项。** 本文的价值命题不依赖遗忘存在——即使 ER 在成功率上赢，它也无法跨本体。

### 3.6 理论工具（Miras，诚实版）

Behrouz et al. *It's All Connected* (2504.13173, ICLR'26) 提出 **Miras** 框架：associative memory architecture / attentional bias / retention gate / memory learning algorithm 四个设计轴。它统一的是**参数化序列骨干**（Table 1 的 15 个模型）。

本文**不宣称 Miras 预言了外部记忆**，而是把它当作**描述语言**，用于说明本文所处的区域在框架中的位置：

| Miras 设计轴 | 参数化序列记忆（Miras 覆盖） | 外部持久记忆（本文） |
|---|---|---|
| memory architecture | 有界、参数化 | 无界、非参数显式条目表 |
| learning algorithm | 在线梯度优化（Δ 规则） | 单步硬写入（η=1，写入互不干涉） |
| retention gate | 权重衰减式软遗忘 | 条目级显式删除 + 时效衰减 |
| attentional bias | ℓ2 / 点积 | 检索相似度（同族） |

即：外部显式记忆是 Δ 规则在「容量→∞、学习率→1」的退化极限。这段写在方法节开头当 framing，**不作为 novelty 主张**（半页以内）。

---

## 4. 科学问题（收敛为 3 个，RA-L 六页可承载）

**SQ1（可迁移性谱系 · 核心）**：技能记忆在**哪个表示层级**上本体无关？沿抽象度排列的四层 value——
① 语言摘要 → ② 物体中心子目标序列（"抓门把 → 拉 15cm → 松开"）→ ③ 任务坐标系下的末端位姿增量 → ④ 关节空间原始动作 / action-expert 潜码
——各自的**跨本体迁移率**与**同本体精度**是多少？最优工作点在哪？

**SQ2（key 对齐 · 真正的技术难点）**：跨本体检索的瓶颈在 **key 侧还是 value 侧**？机器人 A 写入的条目以 A 的观测为 key（相机内参、视角、夹爪外观全不同），B 观测"同一情境"会落到嵌入空间的另一处。候选 key 表示：语言 / 物体中心关系图 / 冻结 VLM 前缀嵌入 / 少量配对数据学出的对齐映射。**归因实验必须能区分"检索错了"与"检索对了但动作用不了"。**

**SQ3（共享记忆池的净效应）**：双本体读写同一记忆库，是 1+1>2 还是互相污染？在哪个 value 层级上共享才是净正收益？

**降级为消融/次要贡献**（v3 的 SQ1/SQ2/SQ4）：基底特性矩阵 → 缩为一张对照表；巩固（consolidation）→ **砍掉**（与可撤销性冲突，且 RoboHarness 已做）；容量界 → 降级为「检索层 top-k 命中率的可证界 + 成功率的经验 scaling 曲线」，不做闭环性能定理。

### 可证伪的预测（写在引言，审稿人喜欢，也逼自己诚实）

- **P1**：迁移率随抽象度单调上升、同本体精度单调下降，二者存在交叉点；最优工作点在②–③之间而非端点。
- **P2**：跨本体检索的主要瓶颈在 **key 侧**——失败案例中检索错条目的占比 > 50%。
- **P3**：**迁移方向不对称**：FR3（低 DoF、定基）→ 移动臂 的迁移率显著高于反向，因为定基记忆是移动记忆的子集。
- **P4**：共享池仅在 value 层级 ≥ ② 时对双方净正；在 ③–④ 层共享会产生负迁移。

四条中任意一条被自己的实验推翻，都是可发表的结果。

---

## 5. 方法框架

**暂定名**：`PORTMEM`（Portable Memory）/ 备选 `XEM`（Cross-Embodiment Memory）。
**投稿前务必检索重名**——v3 的 CAMEL 与 NeurIPS'23 的 CAMEL (Communicative Agents) 撞车。

### 5.1 架构

对齐 π0.5 / GR00T-N 式 flow-matching VLA，主干与 action expert **全程冻结**。

1. **分层 value 的记忆条目**。每条经验同时存四层（①语言摘要 ②物体中心子目标序列 ③任务坐标系末端位姿增量 ④本体特定潜码/关节动作）+ 本体标签 + 成功度校准分。存四层的边际成本极低，却让 SQ1 变成一次数据采集、四条曲线。
2. **本体无关的 key**。key **不用** action expert 的潜码（绑本体），改用冻结 VLM 前缀嵌入 + 物体中心关系编码。跨本体对齐模块（小 MLP）用双本体各自采的**同任务**数据做弱配对训练——这是全系统里**唯一**需要梯度的部件，且离线一次性完成，不随任务流更新。
3. **分层回退读出**。同本体：优先取④，精度最高。跨本体：④不可用 → 回退③ → ②。**回退层级本身就是 SQ1 的实验读数。**
4. **注入机制沿用 Retrieve-then-Steer**（检索 → 一致性过滤 → elite prior → 注入 flow 采样器中间态 → 置信度自适应引导强度）。**明确声明这不是本文贡献**，本文贡献在"存什么"而非"怎么注"。这既诚实，又把对方从竞争者变成基础设施。
5. **置信度门控与弃权**。检索置信低于阈值 → 回退到无记忆的基座策略。必须报告**记忆有害率**（有记忆比无记忆更差的比例）——v3 完全缺失，而 Retrieve-then-Steer 已经有，这是能力差距不只是叙述差距。
6. **生命周期管理**：条目时效衰减 + 容量上限下的淘汰策略 + 条目级删除。

### 5.2 为什么这个设计能跨本体而对手不能（一句话版）

> 对手把记忆存成"这个身体当时做了什么"，所以记忆随身体死亡；本文把记忆存成"当时那个情境需要什么"，并让身体在读出时才决定如何执行。

---

## 6. 实验设计（三阶段，跨本体前置）

### 阶段 A：仿真跨本体（2 个月）

- 平台：LIBERO（定基单臂）+ RoboCasa（移动操作）构成仿真侧的双本体对照；基座 π0 / GR00T-N 系开源权重。
- **A1（SQ1 主实验）**：A 本体写记忆 → B 本体读，四个 value 层级各测迁移率与同本体精度 → 画出 P1 的交叉曲线。
- **A2（SQ2 归因）**：把失败拆成"检索错条目"vs"条目对但动作不可用"，比较四种 key 表示。
- **A3（SQ3）**：单体记忆池 vs 双体共享池，在各层级上测双方增益。
- 注意 LIBERO 的天花板：π0 在 LIBERO 上已近饱和（Liu et al. 热力图大量 0.94–1.00），**必须压到低样本 regime（每任务 5–10 条演示）+ 多个随机任务序并报方差**，否则差异淹没在噪声里。

### 阶段 B：真机跨本体（2 个月，本文的分量所在）

- 双本体基座微调（数百小时存量数据，H20）。
- **B1**：FR3 写入 → 移动臂读取；**B2**：反向。验证 P3 的方向不对称性。
- **B3（生命周期）**：用存量数据把记忆库灌到 10⁴–10⁵ 条，测检索命中率、成功率、**检索延迟-规模曲线**。这是竞争者结构上拿不到的实验（他们全是单环境短部署），也是本文的第二贡献。
- 真机预算硬约束：一次完整评测 ≈ 任务数 × trials × 1.5 min。**上限锁定 8–10 个任务 × 15 trials × 3 方法 × 3 检查点 ≈ 30 机器人小时/轮**，不得扩张。

### 阶段 C：收尾与对齐（1.5 个月）

- 在 **RoboMME (ICML'26)** 的分类法与协议上补一组数，让本文可被该基准直接比较。
- 可撤销性：条目删除后的**残留泄漏检验**（membership-inference 式探针），证明"删了就是真删了"——这是相对 CLARE/VLA-Pro 的定量补充，不是卖点。

### 基线（必须齐全，v3 的清单不够）

| 类别 | 基线 |
|---|---|
| 下界 | frozen base zero-shot |
| 上界 | 多任务联合训练 oracle；per-task LoRA + oracle task id |
| **必比** | **ER（多 buffer size）** ← v3 遗漏，Liu et al. 证明它极强 |
| 同本体检索 SOTA | **Retrieve-then-Steer**、RoboHarness |
| 跨任务持久 | **RECAP**、**VLA-Pro** |
| 模块化参数记忆 | **CLARE** |
| 检索后微调 | Behavior Retrieval (2304.08742) / STRAP (2412.15182) |

### 指标

跨本体迁移率 · 同本体精度 · **记忆有害率（负迁移）** · 写入代价（数据条数 / 墙钟时间 / 是否在线可写）· 检索延迟-规模曲线 · 删除后残留泄漏 · 前向迁移 · 遗忘率（**报告项，非主张项**）

---

## 7. 可行性评估

| 维度 | 评估 |
|---|---|
| 新颖性 | ★★★☆☆ 不再是"开辟新方向"，而是"在已成立的方向上问一个结构性没人问的问题"。**这是更容易过审的形态**，但要求相关工作节写得极其扎实 |
| 竞争烈度 | 中。检索增强冻结策略这一族拥挤，但**跨本体那一列没人**，且需要双本体真机——天然壁垒 |
| 技术风险 | ①跨本体 key 对齐可能根本做不好（最大风险，缓解见下）②真机双本体调试成本 ③RoboMME 协议对齐的工作量 |
| 理论深度 | 中。Miras 只作描述语言，不作 novelty 主张。**深度来自可证伪预测 P1–P4 而非定理** |
| 投稿匹配 | RA-L 良好（真机 + 6 页 + 双本体 demo 视频）。若 P1–P4 全部成立且数据完整，可考虑 CoRL 2027 全文 |
| 时间 | A 2 月 + B 2 月 + C 1.5 月 + 写作 1 月 ≈ **6.5 月** → **2027 年 3 月投 RA-L** |

### 风险与对策

1. **跨本体 key 对齐失败**（最大风险）→ 退化路径清晰：即使 key 必须靠语言（最粗但最不变），P1 的曲线依然可测，只是最优工作点右移。**论文不死，只是结论换了。**
2. **迁移率整体太低，跨本体不 work** → 这本身就是 P1–P4 的否定性结果，配合归因实验（SQ2）依然可发表：*"为什么机器人记忆无法跨本体"* 是一篇有价值的负面结果论文。
3. **有人抢先做跨本体持久记忆** → RECAP 团队最可能（他们已点出这个 limitation）。对策：**双本体真机是硬壁垒**，且尽早把 P1–P4 的预测公开（arXiv 占位）。
4. **RoboMME 的分类法与本文冲突** → 主动对齐，不另起炉灶（见阶段 C）。
5. **π0 在 LIBERO 饱和导致差异不显著** → 低样本 regime + 多任务序方差 + 换 RoboCasa（已写入阶段 A）。

---

## 8. 叙事一句话（v4）

> Retrieval-augmented frozen VLAs now work — but every deployed memory can only be read by the one body that wrote it. We ask what a robot's memory must **store** in order to outlive its own body: we lay out a transferability spectrum from language summaries down to joint-space actions, show that the bottleneck is **key alignment rather than action reuse**, and demonstrate an explicit action memory that a mobile manipulator can read from entries written by a fixed-base arm — something weights and adapters structurally cannot do.

---

## 9. 关键参考文献（v4 · 已订正 venue）

**检索增强的冻结策略（直接基础）**：RAEA (CVPR'24, 2404.11699)；Retrieve-then-Steer (2605.10094)；RECAP (2606.15631)；Dejavu (2510.10181)；RoboHarness (IROS'26, 2603.24060)；RTCF (2608.04527)；Remember Smarter (2608.15269)；SkillMemo (2608.05970)；RAGDP (2507.21452)
**基准与设计空间**：**RoboMME (ICML'26, 2603.04639)**；Reuse Before You Retrieve (ECCV'26 wksp, 2608.17484)；LIBERO (NeurIPS'23, 2306.03310)；Continual World (NeurIPS'21)
**模块化参数记忆**：CLARE (RA-L'26, 2601.09512)；VLA-Pro (2605.29562)
**VLA 持续学习（权重基底）**：CRL-VLA (2602.03445)；LifeLong-RFT (2602.10503)；Liu et al. *Pretrained VLAs are Surprisingly Resistant to Forgetting* (ICML'26, 2603.03818)；Zhao et al. *Information-Theoretic **Constraints for** Continual VLA Alignment* (2603.13335)
**RL 后训练**：VLA-RFT (2510.00406)；VLAC (2509.15937)；RIPT-VLA (2505.17016)；SOP (2601.03044, **基座 π0.5**)；SRPO (2511.15605, **arXiv，CVPR 收录未证实**)；PriorVLA (2605.10925)；Self-improving VLA (ICLR'26, 2511.00091)
**test-time / in-context（跨本体但易失）**：RoboTTT (2607.15275)；MimicDroid (2509.09769)；RA-VLA (**ICML 2026**，无公开 PDF)；SAIL (2603.08269)；RoboSSM (IROS'26, 2509.19658)；WorMI (2509.03956)
**VLA 内部记忆**：MemoryVLA (ICLR'26, 2508.19236)；MemoryVLA++ (**2606.09827，预印，非 ICLR**)；MEM (2603.03596)；ReMem-VLA (2603.12942)；LaMem-VLA (2607.07608)；Explicit Language Memory (2608.04765)
**flow 源分布 / 先验**：WarmPrior (2605.13959)；LAFM (2606.23420)；Golden Ticket (2603.15757)
**检索增强模仿学习（对照类，全为梯度式）**：Behavior Retrieval (RSS'23, 2304.08742)；FlowRetrieval (CoRL'24, 2408.16944)；STRAP (ICLR'25, 2412.15182)；COLLAGE (2508.01131)；ExpReS-VLA (ICRA'26, 2511.06202)
**episodic control 血统**：MFEC (1606.04460)；NEC (1703.01988)；Continuous EC (2211.15183)；Agentic EC (2506.01442)
**统一记忆理论（仅作描述语言）**：Titans (NeurIPS'25, 2501.00663)；Atlas (2505.23735)；Miras / *It's All Connected* (ICLR'26, 2504.13173)；TNT (ICLR'26, 2511.07343)
**具身记忆系统（planner 层，非动作层）**：RoboMemory (2508.01415)；H²-EMV *Learning to Forget* (2604.11306)；MemVerse (2512.03627)；Parisi et al. (2018)
**机理与诊断**：Grant et al. *Not All Features Are Created Equal* (**ICLR Workshop**, 2603.19233)；VLA-Trace (2605.30117)

> v3 书目中的 "Episodic Memory Banks" 查无此文，已删除。所有 venue 标注经 arXiv API / OpenReview 一手核对。

---

## 10. 立即待办

- [ ] 读 **RoboMME (2603.04639)** 全文——本文将被它的分类法打分，方法节写作前必须完成
- [ ] 读 **Retrieve-then-Steer (2605.10094)** 与 **RECAP (2606.15631)** 全文，确认 §5.1 第 4 点的复用边界与 RECAP 对"换本体需微调"的确切措辞
- [ ] 在 openpi 源码中确认 π0 action expert 的注意力掩码与前缀 KV 结构（关系到注入点实现）
- [ ] `PORTMEM` / `XEM` 重名检索
- [ ] 补下载 RA-VLA (ICML'26)、以及 §9 中新增的 Tier-1/Tier-2 论文
- [ ] `RAL2027/paper_src/` 现为 ICRA 的 `ieeeconf` 模板，投 RA-L 需换 `IEEEtran` 期刊格式
