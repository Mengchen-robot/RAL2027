# 调研总结：部署记忆的生命周期 —— 一手证据与空白判定

> 日期：2026-08-31
> 方法：本地 PDF 全文 `pdftotext` 抽取 + 去连字符归一化后的全文 grep（避免 PDF 断词漏检）。所有"未提及"结论均由零命中 grep 交叉验证。
> 语料：`memory-vla/papers/10_retrieval_augmented_frozen/`（7 篇）、`memory-vla/papers/01/05/07/08/`（分层与理论族）、`RAL2027/memory_cross_embodied/covariates/`（2 篇 UQ/去噪方差）。
> **本会话全网不可达**（`export.arxiv.org` / `arxiv.org` / 任意外站 curl 均返回 000）。因此**凡本地无 PDF 的条目一律标【待核】，投稿前必须补一手证据。**

---

# 0. 三句话结论

1. **`stale` / `obsolet` / `prune` / `non-stationar` / `short-term` 这五个词，在七篇持久检索记忆论文中合计出现 0 次。** 这不是"做得不够好"，是**这个概念在该文献族里还没有词汇**。
2. **两篇最相关的工作（Retrieve-then-Steer、Dejavu）都在 Limitations 里亲口指出了这个陷阱，都明说没做。** R-t-S 甚至逐字写出了本文的题目：*"mechanisms for **detecting environment changes**"*。
3. **但"库越大越好"在现有数据里是成立的**：R-t-S 0→∞ 单调升至饱和（61.0→71.2），ReCAP 11→35 任务单调升且未饱和（9.0→31.5）。**所以"库变大会变差"这个主张，若不加限定条件，会被现有证据直接打脸。** 唯一的救法见 §4：把它改成**规模 × 漂移的交互**，而不是规模的主效应。

---

# 1. 七篇持久检索记忆的横向对比（全部一手）

| | **Retrieve-then-Steer** `2605.10094` | **Dejavu/EFN** `2510.10181` | **VLA-Pro** `2605.29562` | **RoboHarness** `2603.24060` | **ReCAP** `2606.15631` | **RoboMME** `2603.04639` | **Di Palo&Johns** `2312.12345` |
|---|---|---|---|---|---|---|---|
| **粒度** | step 索引 / chunk 值 | step（rollout 分组） | **task** | task-instance / episode | subframe → chunk | *无持久条目*（episode 内） | per-object / demo |
| **key** | VLA 视觉 patch，2×2 pool，多视角拼接归一 | VLA 视觉特征 mean–max fusion | 结构化 procedural state `{a,o,e,p}` 文本嵌入 | **CLIP**(obs, instr) | SAM3 位姿 + 语言 + proprio → **DINOv3** | – | **DINO ViT** RGB 特征 |
| **value** | 动作 chunk `a_t` | 基座动作 `a_t^(0)` + 后继特征 | **LoRA 参数 Δθ_i** | 诊断文本 + 关键帧 + 工具参数 | 异体 state-action chunk | – | 末端速度轨迹 + goal image |
| **谁写** | 机器人自己（在线） | 机器人自己（在线） | 离线构建，部署期不写 | 机器人自己（每任务后异步） | **人工添加演示** | – | 训练期人工 + 自主 |
| **成功门控** | ✅ VLAC critic η=0.95，**progress-peak 前缀截断** | ✅ 部署期仅成功（嵌入相似度阈值） | ✗ 不适用 | ✗ **成功+失败都写**（双分区） | ✗（专家演示） | – | ✗ |
| **淘汰** | **FIFO**（3.5k 上限） | ✗ 未实现（仅口头提 reservoir/recency） | ✗ 静态库 | ✗ 只增不减 | ✗ 只增不减 | token 预算 512（episode 内） | ✗ |
| **合并/聚类/抽象/巩固** | **✗** | **✗** | **✗** | **⚠️ 半个**（见 §2） | **✗** | ⚠️ episode 内 token 压缩 | **✗** |
| **staleness / 条目年龄** | **✗**（Limitations 明写 future work） | **✗**（Limitations 明写 future work） | ✗ | ✗ | ✗ | ✗ | ✗ |
| **条目级结果反馈** | ✗（反馈只在写入前） | ✗ | ✗ | ⚠️ 有 `S_i` 位，**但无"被引用后失败→降权"闭环** | ✗ | ✗ | ✗ |
| **容量消融** | **0/1k/2k/3k/4k/5k/∞ → 61.0/64.0/66.2/68.5/70.2/70.8/71.2**（Table 6, p.17） | Vol 300 vs 1000；Fig C.1 曲线 0→1000 | ✗ 无库大小消融；仅 top-k | ✗ **完全无**（连库中条目数都未报告） | **11/17/23/29/35 任务 → 9.0/18.5/19.5/22.0/31.5**（Fig 7） | token 64–512（仅图） | 仅 1 vs 10 demos/object |
| **观察到下降？** | 否（**4k 后饱和**） | 否（边际递减） | **是**（top-k：k=2 **20.9** → k=3 **16.4**） | – | 否（**未饱和**） | 否 | 否 |
| **harm rate** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **层级** | 扁平 | 扁平 | 扁平 | 扁平双分区 | 扁平 | 分类法分层 / **模型扁平** | 扁平 |

---

# 2. RoboHarness 的 consolidation 到底是什么（风险 B 的结案）

**这是本 idea 的头号威胁，现已一手核实，结论：不构成致命冲突，但必须精确划界，并且交出一个词。**

`consolidat` 在七篇里**只有 RoboHarness 命中（20 次）**。其机制（§III-D Stage 2, Eq. 15）：

```
{e*_new, e^{1*}_sim, ..., e^{N*}_sim} = MemConsol(e_new, E_sim)
```

原文：*"The orchestrator performs **batch-level differential analysis to correct historical failure descriptions and optimize correction plans** using new evidence, enabling **iterative self-correction of M rather than monotonic expansion**."*

**逐条对照**：

| 维度 | RoboHarness 的 consolidation | 本文的巩固算子 | 冲突？ |
|---|---|---|---|
| 输入 | 新条目 + top-N 相似条目 | 同 cell 内 K 条 L1 | 相似 |
| 操作 | **就地改写旧条目的诊断文本 `D_i` 与干预方案** | **把 K 条压成 1 条，携带不变量 + 包络 + 接地假设** | **不同** |
| 条目数 | **不减**（输出仍是 N+1 条） | **减**（`ρ = |L2|/|L1| < 1`） | **不同** |
| 被改写的是什么 | **自然语言诊断** | **几何不变量与接地参数** | **不同** |
| value 是什么 | 诊断文本 + 关键帧 + 工具参数，**不含动作** | 可执行动作内容 | **不同** |
| 动机原文 | 防止 *"knowledge stagnation"*（旧条目的**结论**不够好） | 防止 *staleness*（旧条目**所描述的世界**已改变） | **不同** |
| `stale`/`non-stationar` 词频 | **0** | — | 空白仍在 |

**结论**：
- ✅ **Contribution 3 存活**，但**必须在 Related Work 用整整一句话主动点名它**，并把界画在"改写诊断文本 vs 提炼几何不变量 + 接地假设"、"条目数不减 vs 减"、"防知识停滞 vs 防世界改变"三处。
- ❌ **"offline memory consolidation" 这个词组必须交出去。** 本文一律用 **`promotion`（提升）** 或 **`episodic→procedural abstraction`**，**不用 consolidation 作为方法名或 Contribution 的关键词**。
- ⚠️ **命名雷区**：RoboHarness 逐字使用了 *"a **self-evolving** consolidation mechanism"*。→ **本文的标题、摘要、方法名一律不得出现 `self-evolving`。** （用户口语里的"自进化"在英文成稿里必须换词。）

---

# 3. 两条被亲口写下的 future work（既是授权，也是抢跑警报）

### 3.1 Retrieve-then-Steer，附录 I（Limitations），逐字

> *"when object layouts, camera viewpoints, task goals, or robot calibration change rapidly, **previously stored action priors may become less informative or even misleading**"*
>
> *"larger-scale deployment may require more **structured memory organization**, **long-term forgetting**, task-aware indexing, and **mechanisms for detecting environment changes**"*

**这段话里有本文四条 Contribution 中的三条。**

- **好消息**：问题的重要性不需要本文自己论证，最强前作已经替我们论证了，且可以逐字引用进 Intro ¶2。
- **坏消息（必须写进风险表最高一格）**：**R-t-S 团队已经把这件事写进了自己的路线图。** idea 1 的抢跑风险登记里已有这一条（他们同时拥有 PiPER 与 OpenArm）；现在证实**他们在时间轴上也已经瞄准了**。→ **G-A/G-B 一过就必须 arXiv 占位，与 idea 1 的占位合并成一次。**

### 3.2 Dejavu，附录 D.3 / D.4，逐字

> *"if the scene is structurally reconfigured (e.g., the tabletop is completely rearranged), **old experiences can become misleading**"*
>
> *"the bank will **grow without bound** unless additional mechanisms are introduced... it will be necessary to design more sophisticated **caching, compression, and replacement strategies** (e.g., **task-aware coreset selection, time- or novelty-based forgetting, or hierarchical multi-bank structures**)"*

`recency` / `reservoir` / `coreset` / `novelty` 在全批共 4 次命中，**全部集中在 Dejavu 的这同两句里，全部是"可以做但我们没做"**。

---

# 4. ★ 最重要的一条：现有证据不支持"库越大越差"，必须改主张形态

这是本轮调研对 idea 最大的一次修正。**若不改，第一个审稿人就会拿 R-t-S 的 Table 6 打过来。**

**现有数据全部指向"越大越好、最多是饱和"**：

| 来源 | 曲线 | 形状 |
|---|---|---|
| R-t-S Table 6（Moka Pots，300 轨迹） | `C = 0/1k/2k/3k/4k/5k/∞` → `61.0/64.0/66.2/68.5/70.2/70.8/71.2` | **单调升，4k 后饱和，无下降** |
| ReCAP Fig. 7（RoboTwin，11→35 任务池） | `9.0/18.5/19.5/22.0/31.5` | **单调升，未饱和** |
| Dejavu Fig. C.1（0→1000） | 大跳后边际递减 | 单调升 |
| RoboMME Fig. 4（token 64→512） | 单调 | 单调升 |

**唯一的两条反向证据，机理都不是"库大"**：
- **VLA-Pro top-k**：`k=2 → 20.9`，`k=3 → 16.4`。这是**检索条数**变多，不是库变大 → 对应本文的 `Δ_inter`（干扰）。
- **Dejavu Fig. C.5**：部署 500 episode，"appending **all** rollouts **gradually harms performance**"，而只写成功则不会。这是**写入门控质量**问题 → 对应本文的 `Δ_write`。**这是整个文献族里唯一一条随时间退化的曲线，而它的成因恰好是本文五项归因中的第一项。**

### → 主张必须从"主效应"改成"交互"

```
旧（会被打脸）：  SR(N) 存在内部极大值 N*，N > N* 之后下降
新（可辩护）：    SR(N | drift = 0) 单调饱和    ← 这正是 R-t-S 与 ReCAP 已观测到的
                 SR(N | drift > 0) 非单调      ← 因为陈旧条目占比随 N 增长
                 主张 = 规模 × 漂移的交互项显著 ≠ 0
```

**这个改写有三重好处**：
1. **把最强前作的结果变成自己模型的特例**（`drift = 0` 那一档），而不是与它冲突。这是能拿到的最强位置。
2. **解释了为什么至今没人看到下降**：现有全部实验都在单场景、短部署、世界不变的条件下跑 —— 这不是猜测，是七篇的实验设定逐条核实的结果。
3. **把 idea 的独占资源变成了主张的必要条件**：只有同时拥有跨场次真实语料 + 冻结真机策略的组才能观测这个交互。

**配套的设计后果**：主端点必须是 **2×2 析因**（`{单场次库, 跨场次库} × {小 N, 大 N}`），不是一条曲线。**Fig. 3 从"一条曲线"改成"两条曲线 + 交互"。**

---

# 5. 五项归因在文献里的对应物（说明这套拆分不是凭空造的）

| 本文的项 | 文献里的直接对应 | 出处 |
|---|---|---|
| `Δ_write` 写入门控假阳 | R-t-S：无验证记忆 `92.4 → 87.6`；"Predicted Successful Full Trajectory"（不截断）`91.8 < 92.4`；判别器 precision 0.970 / recall 0.678 | R-t-S Table 5 |
| | Dejavu：全写入随 500 episode 逐渐退化 | Dejavu Fig. C.5 |
| `Δ_redun` 近重复挤占 top-k | 无直接对应（**本文新增**） | — |
| `Δ_stale` 陈旧 | **无（全族 0 命中）**（**本文新增**） | — |
| `Δ_inter` 跨任务干扰 | VLA-Pro：`k=3` 回落 16.4 | VLA-Pro Fig. 8 |
| `Δ_cap` 容量残差 | R-t-S：`∞` 档 71.2 的天花板 | R-t-S Table 6 |

> 五项里有三项在文献里有独立佐证，两项是新增。**这比"我们提出一个五项分解"强得多，写作时必须逐项给出这个对应表。**

---

# 6. Retrieve-then-Steer 的两个可直接复用的工作点

| 量 | 值 | 用途 |
|---|---|---|
| 写入门控（VLAC critic）precision / recall | **0.970 / 0.678**，η = 0.95 | 本文 `Δ_write` 的先验；v5 §5.6 已要求用本组语料自测替换 |
| 容量与 FIFO 上限 | **3.5k 条，FIFO** | 本文 `N_max`（10⁴–3×10⁴）**比它大一个量级**，这一点必须在 §IV 明确写出 |
| top-K 敏感性 | `K=1/3/5/10/20 → 93.6/93.8/94.1/94.4/94.2` | K=20 略降 → `Δ_inter` 的独立佐证 |
| 聚合方式 | top-K 相似度加权 + **SO(3) 测地均值** | **本文的管半径计算可直接复用这套 SO(3) 机器**（`covariates/so3.py` 亦有） |

---

# 7. RoboMME 的分类法（本文的 L0–L3 必须映射过去）

RoboMME 明确援引 Atkinson & Shiffrin：long-term memory → procedural + declarative → episodic + semantic，落到四个评测维度：

| RoboMME 维度 | suite | 本文的对应 |
|---|---|---|
| temporal (when) | Counting | — |
| spatial (where) | Permanence | — |
| object (what) | Reference | — |
| **procedural (how)** | Imitation | **本文的 L2** |

**三条必须写进 Related Work 的事实**：
1. RoboMME 的全部 16 个任务、1,600 演示、770k 时间步**都是 episode 内的**，记忆在 episode 边界即消失。
2. 它的 14 个 MME-VLA 变体**全部是扁平单一记忆表征**，`short-term` / `hierarchic` 0 命中。
3. 它的 Limitations **明写把 memory-bank 类方法列为未覆盖的未来工作**。
   → **所以"测量持久库的生命周期"这件事，连基准都还不存在。** 这句话可以写，但必须用它自己的 Limitations 作为引证，不能自己下判断。

**它的两个数必须被本文引用为设计依据**（idea 1 的施工图已用过，本文沿用）：
- 同一份 memory content 只换注入机制：`30.68 → 44.51`（14 个点）
- 同一层级只换写内容的 VLM：`84.08 → 32.70`（51 个点）
→ **所以本文的一切对照必须固定注入路径与内容生成器，只变库的结构。这是 §III 的纪律来源。**

---

# 8. 腐坏判别的竞争者（本地一手，`covariates/`）

| # | 方法 | 出处 | 关键事实 |
|---|---|---|---|
| **B3** | **VFD**（velocity-field disagreement，flow VLA 的 epistemic 不确定度） | `2606.18043`，TUM/ETH（Schoellig, Krause） | 摘要逐字点名 *"non-stationary environments"*。**M=2 的两成员 ensemble 即足够**（Fig. 2：ensemble size 对标定影响很小，作者据此全程用 M=2）。校准：`−Spearman 0.71±0.03`，优于 GU(0.62) / Action-L2(0.50) / ACE(0.31) / DECU(0.31) / Entropy(0.10) / Perplexity(−0.04)。失败检测：Accuracy **0.67**、TPR **0.79**、TWA 0.54，优于 ACE / STAC / RND-OE。用 conformal prediction 从 10 条成功 rollout 标定阈值。 |
| **B4** | **DVAC**（去噪方差自适应分块） | `2606.03847` | 单模型、无 ensemble。核心观察："clean-action estimates remain stable during predictable motion phases, but **fluctuate more strongly around contact-rich or precision-sensitive operations**"。π0.5 上 LIBERO `94.75 → 98.00` 且重规划减少 43.0%。 |

**对本文的三条后果**：
1. **B3/B4 是必比项。** 不比会被问"为什么不用策略自己的不确定度"，而这一问有两篇现成论文撑腰。
2. **成本论证必须诚实收窄**：VFD 的 `K` 只有 **2**，不是 10。所以"我们比 ensemble 便宜 K 倍"这句话里 `K=2`，**收益是 2×，不是一个数量级**。→ **成本轴不能作为唯一优势**，真正的优势必须写成：VFD 是**在线的、逐时间步的、需要执行才能知道**；本文的接地残差是**离线的、在检索之前就能算、不需要执行**。**这是"事前 vs 事中"的差别，不是"便宜 2 倍"。**
3. VFD 的标定用 conformal prediction + 10 条成功 rollout —— **本文的阈值 `c` 应当照抄这套标定协议**，这样比较才公平，且省掉一轮"你们的阈值是调出来的"。

---

# 9. 空白判定（三条，按硬度降序）

### 空白 1（最硬）· 记忆只有"写入门控"，没有"写入后的生命周期"

七篇全部把质量控制**前置**到写入那一刻，写完即冻结为永久等价的条目。
**合并/聚类/抽象在七篇里全部为零**，`prune` 全批 0 命中。三个看起来像的都不是：
- R-t-S 的 elite prior 加权 —— **读取时**加权平均，不回写，库中条目数不变
- VLA-Pro 的 LoRA fusion —— **读取时**融合，chunk 执行完即卸载，从不回写
- RoboHarness 的 consolidation —— **就地改写诊断文本**，条目数不减（详见 §2）

### 空白 2 · "条目会过时"在整个文献族里没有词汇，更无度量

`stale` / `obsolet` / `non-stationar` 七篇合计 **0 次**。`decay` 的 9 次命中**全是 optimizer 的 weight decay**。
没有任何一篇为条目记录年龄、写入时间、时效性或命中后效用。`timestamp` / `expire` / `downweight` / `demote` / `re-evaluat` 全部 0 命中。

### 空白 3 · 没有条目级结果反馈，harm rate 作为指标全族未报告

**结果反馈只反映到"写不写"，从不反映到"已写的这条好不好用"。** RoboHarness 最接近（每条带 `S_i` 成功位 + 失败归因），但 `S_i` 记录的是**该条目自身那次执行**的成败，不是**它被别人检索引用后**的成败 —— 缺的正是这一跳。

现有的负向证据全是聚合量或基线对比，**无法回答"读了记忆的 N 次里有几次反而更差"**：

| 证据 | 出处 | 形态 |
|---|---|---|
| `92.4 → 87.6`（未验证记忆） | R-t-S Table 5 | 聚合 |
| Direct Replay `87.8`（低于 92.4 基线） | R-t-S Table 4 | 聚合 |
| kNN-RAG 真机 `25.8 → 18.2`；DrawerStore `5.3 → 0.0` | Dejavu Table 2 | 基线对比 |
| All-rollouts 随 500 episode 逐渐退化 | Dejavu Fig. C.5 | **唯一的时间退化曲线** |
| top-k `20.9 → 16.4` | VLA-Pro Fig. 8 | **唯一的规模回落数字** |
| No-RAG orchestrator *"counterproductive"* | RoboHarness Table IV | 聚合 |

---

# 10. 【待核】清单（本会话全网不可达，投稿前逐条一手核实）

| # | 条目 | 为什么必须核 |
|---|---|---|
| 1 | Remember Smarter `2608.15269`（π0 即插即用经验记忆，LIBERO-Plus 53.6→70.6） | 可能有规模消融 |
| 2 | SkillMemo `2608.05970` | 名字直指程序性记忆 |
| 3 | RTCF `2608.04527`（training-free 冻结 VLA 记忆修正） | 同族 |
| 4 | ExpReS-VLA `2511.06202`（**ICRA 2026**） | 已发表，必须引 |
| 5 | Reuse Before You Retrieve `2608.17484`（ECCV'26 workshop，设计空间元分析） | **元分析论文，本文的分类法必须与它对齐** |
| 6 | RAEA `2404.11699`（**CVPR 2024**，external policy memory bank） | 最早的占位者 |
| 7 | 方法名 `STRATA` / `SEDIMENT` / `ATTIC` 的重名检索 | v3 的 CAMEL 已撞车一次 |
| 8 | R-t-S 是否已挂出后续版本（时间轴/遗忘方向） | **抢跑监控，建议每月一次** |

> 核查路径（来自项目记忆）：`WebSearch` 无后端不可信；`WebFetch` 对 arxiv 域名封锁；可用的是 **`curl https://export.arxiv.org/api/query?id_list=<ID>`（必须 https）**，以及本地 PDF 的 `pdftotext -f 1 -l 1`。本会话两条路径均因全网不可达而失效。

---

# 11. ★ episode 内记忆族：**"短期记忆"与"长期记忆"从来不是同一个对象**

这是本轮调研的第二个硬发现，比 §9 的三条空白更锋利，也更贴近用户"从 episode 级长短记忆自演化到 lifelong"的原始表述。

全库被干净地劈成互不相交的两半，**从无交集**：

| | 谁 | 逐字证据 |
|---|---|---|
| **只读不写**<br>（episode 内条件化动作生成，episode 结束全部蒸发） | MemoryVLA / LaMem-VLA / ReMem-VLA / MEM / RoboMME | ReMem-VLA：*"At episode boundaries, we **hard-reset** the slot's recurrent state"*<br>MemoryVLA：条目位置编码就是 `TE(episode timestep)` |
| **只写不读**<br>（episode 内存在一个缓冲区，但策略从不查询它） | **Retrieve-then-Steer** | *"we maintain a **temporary buffer** to **record** candidate memory entries"*。`B^(i)` 是纯写入暂存区；被读的只有跨 episode 的 `M` |
| **两边都没有** | Dejavu / VLA-Pro | Dejavu 整条 rollout 结束后原样 append；VLA-Pro 的 `H_<t` 只用来拼检索 query，无写出通路 |

**四个可直接引用的补充事实**：

1. **MemoryVLA 与 LaMem-VLA 的两层用同一条更新规则** —— MemoryVLA Eq.9 与 LaMem-VLA Eq.4–5 是**同一个** `argmax cos(相邻) → 平均` 算子；LaMem-VLA 明说 *"applies **the same** memory updating strategy to the long-term memory vault"*。**⇒ 层间本质上不存在差异，"分层"是命名而非机制。**
2. **A 组全部需要训练**（记忆模块有梯度）。本文冻结策略，因此**不能、也不打算**与它们在同一坐标系比。
3. **抽象只到文本，从不到动作** —— RoboMemory 的 VLM CRUD、MemVerse 的 `O_extract`、MEM 的 LLM 语义压缩、RoboHarness 的失败归因重写，全部抽象成自然语言或图三元组。RoboMemory 甚至直言真机上技能库路线不可行：*"making it challenging to construct a **reusable, code-based skill library**"*。
4. **全库唯一形式化的抽象式巩固算子**是 MemVerse 的 LTM→参数 SFT 蒸馏（Eq.7–8），但它作用在**对话知识图**上，**没有具身、没有动作空间**。
   > 附带一个有用的经验支撑：MemVerse Table 10 显示分阶段蒸馏在 **75% 记忆量时峰值 75.69、100% 时反降到 75.62**，作者结论是 *"the importance of **periodic, well-paced** memory updates rather than relying solely on full-memory consolidation"*。**这是"提升比 ρ 存在内部最优"的独立佐证**，正是本文 A5 消融要扫的那条。

---

# 12. 统一记忆理论：**框架里根本没有"巩固"这根轴**（只能当 framing）

- Miras（*It's all connected*, ICLR'26）的四个设计轴——associative memory architecture / attentional bias / retention gate / memory learning algorithm——**全部描述同一个 `W`**。没有"记忆层数"轴，没有"层间写入策略"轴，没有 replay/rehearsal 轴。
- `consolidat` 在 Its_All_Connected **0 命中**；在 Titans / ATLAS 各 1 次且**只出现在参考文献里**。
- Miras **Remark 3** 论证连擦除都不存在（*"there is **no memory erasing or forgetting process**"*），并把 forget gate 改名为 retention gate ⇒ **单存储假设被写死在框架的哲学层面**。
- 多存储只以**架构接线**出现（MAC / MAG / MAL、hybrid+SWA）；唯一的跨模块写入 Titans Eq.24 `M_t = M_{t-1}(y_t)` 自述动机是**防溢出的相关性过滤**，不是巩固。
- **TNT** 是唯一自称 hierarchical memory 的，但 local 层是**周期性重置**以换取 context parallelism，**local→global 零通路**。
- **ATLAS 留了一句可直接引用的空缺声明**：*"**no persistent learning or skill acquisition carries over** to new, independent global context once the memory is cleared."*
- **Parisi 2019**（CLS 综述）全文 8 个编号公式，**§2.3(CLS) 与 §3.4(CLS+replay) 两节零公式**，作者自认 *"the exact neural mechanisms remain **poorly understood**"*。

**可以写的一句**：把 store-to-store 的转移算子形式化为 Miras 式框架的第五根轴，在数学上是空白的。
**绝不能写的一句**：*"理论预言了这个空白"* —— v3 critique §1.1 已因这句话被一手核对枪毙过一次（Miras Table 1 的 15 个模型全是参数化序列骨干，`external memory` / `database` / `RAG` 词频为 0）。**这一条只做 framing，一个 Contribution 都不占。**

---

# 13. ★ 三条必须提前拆掉的红线

### 红线 1 · 措辞撞车严重，必须改名

| 撞车词组 | 被谁占了 |
|---|---|
| `self-evolving consolidation mechanism` | **RoboHarness 摘要，近逐字** |
| `cross-task procedural memory for VLA` | **VLA-Pro 的标题** |
| `lifelong robot learning` | **LIBERO 的副标题** |

→ 差异化必须写成**机械描述**而非概念口号，每个从句都承重。可用的一句：
> *a two-tier store whose short-term tier conditions the action expert within an episode and is distilled, by an abstracting promotion operator, into a cross-task long-term **action** memory that carries the grounding assumption under which it was written.*

### 红线 2 · 这个 idea 被**四篇论文**写进了 future work，审稿人会知道

| 论文 | 逐字 |
|---|---|
| **MemoryVLA** | *"building **lifelong memory through biologically inspired consolidation** that distills frequently reused experiences into permanent representations"* |
| **MEM** | *"scale memory to last **beyond the horizon of a single episode**"* |
| **VLA-Pro** | *"**continual memory expansion** … **hierarchical or compositional procedural states**"* |
| **Retrieve-then-Steer** | *"more **structured memory organization**, **long-term forgetting**, task-aware indexing, and **mechanisms for detecting environment changes**"* |

→ **贡献必须是"可运行的机制 + 可测的量"，绝不能是概念本身。**
→ **写作策略：主动把这四段原文引进 Intro ¶2**。被四篇论文共同认领为未来工作的问题，其重要性不需要本文再论证；而"谁先把它变成数"才是竞争。

### 红线 3 · 缺一个合适的 benchmark（最实际的风险）

| 候选 | 为什么不合用 |
|---|---|
| **RoboMME** | 严格 episode 内；16 任务 / 1,600 演示 / 770k 步全部无跨 episode 持久性；Limitations 明写 memory-bank 类方法为未覆盖 |
| **MemoryBench** | 仅约 300 帧，且 ReMem-VLA 已刷到 **94.5%**（天花板） |
| LIBERO / LIBERO-PRO / SimplerEnv / RoboTwin | **本身不要求跨 episode 记忆**；R-t-S 在 LIBERO-10 上只有 `92.4 → 94.4`，天花板效应明显 |

→ **必须自建"连续部署、任务序列、不清库"的评测协议。**
→ 唯一可借的现成范式：**RoboMemory 的 *"run each task twice **without clearing long-term memory**"***（26.67% → 46.67%）。
→ 这一条必须在冻结实验设计之前定稿，是 `paper_outline_v1.md` §7 的 P0 项。

---

# 14. A/B/C/D 四组的"谁做了什么"总表

| | 分层存储 | 短期层被 episode 内读 | 跨 episode 持久 | 旧条目会被改写 | 层间提升算子 | 抽象到动作 | 有淘汰/保持规则 | 记忆条件化动作 | 零梯度 | 真机 |
|---|---|---|---|---|---|---|---|---|---|---|
| **MemoryVLA** | ✓ 名义两层 | ✓ | ✗ | ✗ | ✗ 两层同规则 | — | 固定预算 | ✓ | ✗ 需训练 | ✓ |
| **LaMem-VLA** | ✓ 名义两层 | ✓ | ✗ | ✗ | ✗ 两层同规则 | — | 固定预算 | ✓ | ✗ 需训练 | ✓ |
| **ReMem-VLA** | ✗ | ✓ | ✗ **hard-reset** | ✗ | ✗ | — | ✗ | ✓ | ✗ 需训练 | ✓ |
| **MEM** | ✓ 多尺度 | ✓ | ✗ | ✗ | LLM 语义压缩 | **✗ 只到文本** | ✗ | ✓ | ✗ 需训练 | ✓ |
| **RoboMemory** | ✓ 多层 | — | ✓ | ✓ VLM CRUD | ✓ 但**只到文本/图** | **✗** | ✗ | ✗ 规划层 | ✓ | ✓ |
| **MemVerse** | ✓ STM/LTM | — | ✓ | ✓ | **✓ 唯一形式化的抽象巩固**（Eq.7–8 SFT 蒸馏） | **✗ 无具身无动作空间** | ✓ | ✗ 对话 | ✗ 需 SFT | ✗ |
| **Neural ASM** | ✗ 权重即记忆 | — | ✗ 冻结 | ✗ | ✗ | — | ✗ | ✓ | ✗ | ✗ 仅仿真 |
| **Retrieve-then-Steer** | ✗ 缓冲+库 | **✗ 缓冲不被读** | ✓ | ✗ | **✗ 逐字拷贝** | — | 成功门+峰值截断+**FIFO** | ✓ | ✓ | ✓ |
| **Dejavu/EFN** | ✗ 单库 | — | ✓ | ✗ | ✗ 原样 append | — | 成功过滤（淘汰未实现） | ✓ 残差 | ✓(库)/✗(EFN 需 SAC) | ✓ |
| **RoboHarness** | ✗ 单库按成败分区 | — | ✓ | **✓ 同层重写** | ✗ | **✗ 只到文本** | ✗ 无容量 | **✗ 改输入** | ✓ | ✗ |
| **VLA-Pro** | ✗ | `H_<t` 只做查询 | ✗ 卸载还原 | ✗ | ✗ | ✗ 参数 | ✗ | ✓ LoRA 融入 | **✗ 全离线** | ✓ |
| **RoboMME** | ✗ 单层 512-token | ✓ | ✗ | ✗ | ✗ | — | 仅固定预算 | ✓ | ✗ | ✓ |
| **ReCAP** | ✗ 演示池 | — | ✓ | ✗ | ✗ | — | ✗ | ✓ 残差 | ✗ 人工加 demo | ✓ |
| **本文** | **✓ L0–L3** | **✗ 只作边界，不实现**（2026-08-31 决策，方案 B 转 idea 3） | ✓ | ✓ 降级/淘汰 | **✓ 抽象式** | **✓ 到动作** | **✓ 接地残差 + 结果后验** | ✓ | ✓ | ✓ |
