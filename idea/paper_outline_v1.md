# 跨本体持久动作记忆 — IEEE RA-L 最终写作大纲 v1（施工图）

生成日期：2026-08-22
上游依据：`vla_memory_cl_feasibility_v4.md`（规格书）、`review_v3_critique.md`、`threat_RAM_RoboOS.md`、三位审稿人对四节大纲的对抗意见、以及 RoboMME / Retrieve-then-Steer / RECAP / Dejavu 四篇一手 PDF 精读记录。

**本文档的用法**：这是施工图，不是 idea 描述。每一节的每一条要么是可执行的写作/实验指令，要么是可验证的断言。凡标 **【待确认】** 的，写进论文前必须有一手证据。

---

# 0. 一页速览

## 0.1 Title 推荐

| # | 候选 | 评价 |
|---|---|---|
| **T1（推荐）** | **Whose Memory Can Be Read? Cross-Body Readability of Persistent Action Memory for Frozen VLA Policies** | 问句式把"谁能读"这条新轴放进标题；"cross-body"避开 RECAP 已占用的 cross-embodiment 术语；"persistent action memory"含两个关键限定词（persistent / action） |
| T2 | Reading Another Robot's Memory: What a Persistent Action Store Must Contain to Outlive Its Body | 叙事性强，但"outlive its body"是修辞，RA-L 审稿人可能嫌软 |
| T3（保守） | A Shared Persistent Action Memory for Two Deployed Manipulators | 最不可攻击，但也最不吸引人；作为 rebuttal 后改名的退路 |

**决策规则**：若 §4 的 P1 主结果为正（谱系存在且有内部工作点），用 T1；若主结果为负（跨本体读取整体不 work），改用 "Why a Robot's Action Memory Does Not Transfer Across Bodies: A Layered Measurement"，全文转为负面结果论文（见 §6 G4/G5）。

**方法名**：`PORTMEM` — **【待确认】重名检索尚未执行**（v3 的 CAMEL 已撞车一次）。检索完成前，正文一律用占位符 `\sysname`，用 LaTeX 宏定义，改名成本为零。名字**不进标题**（标题不依赖名字，是防守性设计）。

## 0.2 Abstract 英文初稿（约 195 词，含全部限定词）

> A robot that improves during deployment must put what it learned somewhere. Retrieval-augmented frozen vision-language-action (VLA) policies already accumulate deployment experience without gradient updates, and cross-embodiment retrieval pools already exist. What has not been shown is a persistent store of *executable action content*, written by a robot during its own deployment, that a *second deployed robot* reads with no further update to its policy. We ask what an entry must contain for this to be possible. Each experience is written at four levels of abstraction — a re-groundable language summary, an object-centric subgoal sequence, object-anchored end-effector deltas, and a joint-space action chunk — under a body-agnostic key with a learned alignment map, and every level is decoded into the reader's own action space before it is injected into the reader's frozen flow-matching sampler. A fixed-base Franka FR3 and a mobile manipulator both write to and read from one store, in both directions. We report the transferability spectrum across the four levels, decompose the cross-body loss into key-side, retargeting and value-side terms, and report the per-trial memory-harm rate and the injection rate that make these numbers interpretable. Admitting a third, previously unseen reader costs \todo{N} paired episodes and \todo{M} GPU-minutes, and no policy gradient.

**Abstract 写作红线**：
- 不得出现 first / novel / unexplored / we fill the gap。
- 必须出现的三个限定词：*executable action content*、*during its own deployment*、*no further update to its policy*。少一个，Table I 里的 RoboOS 或 RAM 或 RECAP 就是反例。
- 必须出现 injection rate —— 这是主动交出"transfer rate 可被弃权刷高"这一击（Reviewer #2 R2-B1）。

## 0.3 故事线（3 句话）

1. 检索增强的冻结 VLA 已经跑通，跨本体检索池也已经存在（RECAP：人手/UR5 写、机器人读；RAM：660 条离线 affordance 库被两种本体读）——这些都不是我们要论证的东西。
2. 但没有一个**由部署中的机器人自己写下的、含可执行动作内容的持久库**被第二具**同样在部署中的**机器人**不经任何策略梯度**读过：换读者要么付一次 target 侧微调（RECAP 摘要自陈），要么条目本身就是权重（CLARE / VLA-Pro），要么跨过身体的根本不是动作（RoboOS 自陈其 shared memory 无动作内容）。
3. 我们把每条经验同时写在四个抽象层级上、用一张一次性训练的对齐图索引、在读出时一律解码回读者自己的动作空间，然后在两台**都在部署中**的机器人（FR3 与移动臂）之间双向读写同一个库，测出哪一层扛得住换身体、以及跨本体损失中有多少来自检索、多少来自 retarget、多少来自动作本身不可用。

## 0.4 四条 Contribution（英文成稿）

> **1) We quantify what a reader swap costs a retrieval memory, in threshold-free terms.**
> We measure retrieval quality for same-body and cross-body queries under four key constructions, reporting precision@k and ROC-AUC against a positive-pair definition derived from our own (task, phase) annotation, and reporting the recall (equivalently, abstention) that a cross-body reader must pay to reach the same precision as a same-body reader. We deliberately avoid arguing from the default similarity gate of any single system: the gate value of a state-of-the-art same-body retriever is a per-deployment trade-off knob, not a property of the representation, and its own sensitivity study shows the method is nearly flat across it.

> **2) We make the transferability of an experience an experimentally separable variable.**
> One collection produces four value levels per entry under a shared key and, crucially, a shared readout interface: every level is decoded into the reader's action space and injected at the same point of the same frozen sampler, so that abstraction level is varied while the injection path is held fixed. We report each level with oracle content and with automatically generated content, separating what the representation costs from what the content generator costs, and we compare against a derive-on-read store that materialises only the lowest level and reconstructs the rest at read time.

> **3) We report a persistent action store that two deployed bodies share, write and read bidirectionally, with no gradient reaching either policy once deployed.**
> Each body's base policy is fine-tuned once, before deployment, on tasks disjoint from the memory-evaluation tasks; nothing is updated when the store is admitted or when it grows. We further admit a third, previously unseen reader body and report its admission cost in paired episodes and GPU-minutes, alongside the cost of a per-body target-side fine-tune on the same pair. We report the per-trial memory-harm rate — the fraction of paired trials, at matched initial state and matched sampler noise, in which the store makes the reader worse than its memoryless base — together with the injection rate that conditions it.

> **4) We decompose the cross-body loss and characterise a shared store.**
> An oracle ladder attributes the gap between a same-body and a cross-body reader to three additive terms — retrieval, retargeting, and value inexecutability — without post-hoc human labelling of failures. On a corpus-seeded store of \todo{1e4–1e5} entries (\todo{N} episodes) shared across tasks and bodies, we show that the binding constraint is retrieval precision and cross-body interference rather than capacity.

> **We explicitly do not claim**: the intermediate-state injection into a flow-matching sampler, the confidence-adaptive guidance strength, the abstain-on-low-confidence fallback, or the component-aware aggregation of retrieved chunks — all adopted from Retrieve-then-Steer [R-t-S] and used unchanged once an entry has been decoded into the reader's action space. Nor do we claim gradient-free growth of a retrieval pool, demonstrated by RECAP, nor entry-level revocability, demonstrated by CLARE.

## 0.5 页数分配总表（**全文唯一的一份预算表**，各节引用此表，禁止另立）

RA-L 正文 6 页硬预算，IEEEtran 双栏。当前基线设计经排版估算为 **7.49 页**（Reviewer #3 逐项核算），必须执行以下裁剪。

| Section | 预算（页） | 承载的图表 | 备注 |
|---|---|---|---|
| I. Introduction | 1.00 | Fig. 1 (0.22, 跨双栏 teaser, 仅 2 panel) | 正文 5 段 + Contributions，约 800 词 |
| II. Related Work | 0.75 | Table I (0.22, 跨双栏, 8 行 × 6 列纯符号) | 正文 5 段，II-D 并入 II-C 末段 |
| III. Method | 1.30 | Fig. 2 (0.20, 单栏系统图) + Algorithm 1 (0.12) | 含 problem formulation |
| IV. Experimental Setup | 0.40 | Table II (0.15, baseline & 协议) | 含机器人小时预算句 |
| V. Results | 2.05 | Fig. 3 (0.16 检索质量) + Fig. 4 (0.20 谱系) + Fig. 5 (0.18 oracle 阶梯) + Table III (0.28 主结果) + Table IV (0.20 消融) | 评审重心，不可压 |
| VI. Conclusion & Limitations | 0.15 | — | |
| References | 0.35 | — | **40 条**，按族打包（每族只单列 2–3 篇，其余合并 e.g.） |
| **合计** | **6.00** | 6 个图表对象 | |

**相对基线设计执行的裁剪（总计 −1.49 页）**：
1. Table I 从 14 行 × 8 列散文改为 8 行 × 6 列纯符号，散文下沉 caption：0.62 → 0.22（**−0.40**）
2. 参考文献 65 → 40 条按族打包：1.13 → 0.35（**−0.78**，需严格执行）
3. Fig. 1 删除 panel (c)（谱系曲线只在 §V 的 Fig. 4 出现一次）：**−0.07**
4. II-D 并入 II-C 末段，省一个 subsection header：**−0.12**
5. 仿真结果不进正文（只作内部 go/no-go 与 key 侧离线分析）：§IV −0.05、§V −0.20（**−0.25**）
6. 删除 Intro 的成本复杂度段（O(T·B) 论据）：**−0.12**
7. 删除 ANN 检索延迟-规模曲线（10⁵ 条暴力扫描亚毫秒，实验必然"无事发生"）：**−0.15**

**若买 1 页（7 页，付超页费）**，新增的 1.0 页只允许用于：§V +0.55（把仿真 2×2 因子表与 reader#3 admission 表放回正文）、§III +0.25（四层 value 的解码器细节）、References +0.20（回到 52 条）。**不允许**用于加基线或加叙事。

## 0.6 审稿人已识别的 3 个最致命风险 + 应对（决定要不要做）

### 风险 A：**"mechanical veto" 论证被 Retrieve-then-Steer 自己的敏感性表证伪**（Reviewer #2·R1-B1，最致命）

- **事实**：Retrieve-then-Steer 附录表 8（一手确认）γ_sim ∈ {0.9988, 0.9990, 0.9992, 0.9995, 0.9998} → SR {93.7, 94.1, 94.4, 94.0, 93.5}，全程波动 0.9 pp；最松的 0.9988 仍是 93.7 > 无记忆基座 92.4。原文把 γ_sim 描述为 "controls the trade-off between prior coverage and prior quality"。
- **后果若不改**：Intro ¶3（自称全文唯一定量论证）、Fig. 2、Contribution 1 四处同时塌；被判 straw-man。
- **我们的处理**：**放弃"机制性否决"这条论证路线。** Fig. 3 改为阈值无关的检索质量图（precision@k / AUC + 重标定后的工作点），Contribution 1 改为"量化 reader swap 的重标定代价"。caption 里主动写明："γ_sim is re-calibrated per condition; the 0.9992 default of [R-t-S] is tuned on LIBERO-10 and is a coverage/quality knob, not a property of the representation."
- **残余风险**：若重标定后跨本体 precision@10 仍显著高于 chance，则"key 侧是瓶颈"（P2）会被削弱，论文重心必须转到 value 侧与 retarget 侧。**这是 G1 gate 的判定内容（§6）。**

### 风险 B：**"zero policy-side gradient" 在我们自己的实验计划里就不成立**（Reviewer #3·R3-B1 + Reviewer #2·R1-B5）

- **事实**：v4 阶段 B 第一句是"双本体基座微调（数百小时存量数据）"。每引入一个读者本体仍要跑一次策略级梯度 —— 这正是 RECAP 的成本。且 n=2 时两个本体的数据**都**用来训对齐图，"admitting a new reader"这个动作在整个计划里**从未被执行过一次**，分界线不可证伪。
- **后果若不改**：Contribution 3、Table I 末行、Fig. 1(a) 的 "no policy update" 徽章同时失效，贡献被压成常数因子之争 → RA-L 拒稿理由。
- **我们的处理（两条同时做，缺一不可）**：
  1. **实验 E0**：读者本体的基座微调数据切分中**剔除全部记忆评测任务**，训好后冻结，再读取写者写的这些任务的条目。全文措辞统一为 "the reader's base policy is fine-tuned once, before deployment, on tasks disjoint from the memory-evaluation tasks, and is never touched again"。
  2. **实验 E1（reader #3）**：FR3 换一副夹爪 + 移动相机位姿 + 锁一个关节 = 一具对齐图与基座微调都从未见过的本体（零新硬件）。报"admitting reader #3"的实测代价（配对 episode 数 + 对齐图 GPU-分钟），与同一 body pair 上做 RECAP 式 target 侧微调的代价并排。
  3. 全文**删除** O(T·B) → O(1) 的复杂度论据，换成一张三列实测代价表。
- **残余风险**：reader #3 是"同一台 FR3 的变体"，审稿人可能说这不算新本体。**诚实标注为未完全解决**：我们在正文用 "a modified fixed-base configuration unseen by the alignment map" 描述它，不称其为第三个 embodiment，并明说这是 admission cost 的下界估计。

### 风险 C：**P1 的抽象轴与注入通路、与内容生成器质量二重共线**（Reviewer #2·R1-B2 + Reviewer #2 R2-B4）

- **事实**：RoboMME 实测同一份 memory content 仅换注入机制，SR 30.68（FrameSamp+Context）→ 44.51（FrameSamp+Modul），14 个点；同一层级仅换写内容的 VLM，GroundSG+Oracle 84.08±1.86 vs GroundSG+QwenVL 32.70±0.61，51 个点。而基线设计里 ①② 走 condition-side 注入、③ 走 retarget→Eq.(6)、④ 直接 Eq.(6)。
- **后果若不改**：Fig. 4（money figure）的任何形状都无法归因到 abstraction，主实验无效。
- **我们的处理（一个修复解决两个 blocking issue）**：
  1. **统一注入通路**：所有层级在读出时一律解码到读者动作空间的 H×D prior，四层共用 Eq.(6)。副作用：`adopted unchanged from Retrieve-then-Steer` 从不实陈述变成真陈述（解决 R1-B7）。解码器（①②→子目标→EE 轨迹→retarget；③→retarget）显式声明为本文贡献。
  2. **每层报两次**：oracle content 与 automatic content。Fig. 4 画 oracle 版（表示层的干净读数）与 automatic 版（系统实际值）两组曲线，两者之差即生成器代价。
  3. **删除 P1 后半句**："same-body precision falls monotonically with abstraction" 与现有最好证据相反。改为 "same-body precision is governed by content fidelity rather than by abstraction level"。
- **残余风险**：统一通路可能让 ①② 层因两次有损解码而整体崩掉，谱系塌成两点。**G2 gate 判定（§6）**；若崩，P1 降级为三点谱系并同步改写 Fig. 4 与 Contribution 2。

### （附）三位审稿人全部 blocking issue 的处理映射

| 编号 | 质疑 | 我们的处理 | 落点 |
|---|---|---|---|
| R1-B1 | mechanical veto 被 Table 8 证伪 | 放弃该论证；Fig.3 改阈值无关 | §0.6-A / §1 ¶3 / §4 Fig.3 |
| R1-B2 | P1 与注入通路、生成器质量共线 | 统一注入通路 + oracle/auto 双报 + 删 P1 后半句 | §0.6-C / §3.6 / §4 |
| R1-B3 | derive-on-read 使分层冗余 | 立为主表一列，用读出延迟辩护必要性 | §4 基线表 / §3.3 |
| R1-B4 | instruction-only 对照可抹平 ① 层 | 立为主表一列 + headline 移到 ③ + 增设语言不可表达任务 | §4 基线表 / §4.2 任务集 |
| R1-B5 | 成本论据自我否定，没有 reader 被 admit 过 | 删 O(1)；加 reader #3 实测代价表 | §0.6-B / §4 E1 |
| R1-B6 | C3（自写）与 C4（语料灌库）互斥 | 拆 S_deploy / S_corpus，全文贯彻 | §3.7 / §4.3 |
| R1-B7 | "adopted unchanged" 是不实陈述 | 统一通路后成立；解码路径显式认领 | §3.6 边界声明 |
| R1-B8 | 为什么不共训（最强"轴是硬造的"质疑） | 价值命题从成本轴移到时效轴 + 实验 E5 | §1 ¶1/¶5 / §4 E5 |
| R1-B9 | P3 机理（工作空间子集）运动学上错 + 写入端污染 | 改为 viewpoint 假设 + 锁底盘对照 + 写入端配平 | §4.5 P3 |
| R1-B10 | 两份页数预算打架，§V 装不下 | 单一预算表 + 裁剪清单 | §0.5 / §5 |
| R2-B1 | TR 可被弃权刷到 1.0 | 强制并报 injection rate；forced-injection 列；<20% 标 n.i. | §4.6 指标 / §4 Table III |
| R2-B2 | LIBERO↔RoboCasa 同时换 8 个变量，body 效应不可识别 | 2×2 因子（同模拟器内换机器人模型）；不可行则仿真退出正文 | §4.1 / §6 G3 |
| R2-B3 | P3 效力≈0，15 trials 低于同族标准 | 12 任务 × 20 成对 trial；P3 用任务级符号检验 | §4.5 / §4.6 |
| R2-B4 | 层级效应与注入通路混淆 | 同 R1-B2，另加 2 个 crossover arm（仅仿真/4 任务） | §4.4 |
| R2-B5 | 语料泄漏 + 对齐图在评测任务上被监督 | 语料按场景/物体实例三分；对齐图 held-out-task；training-free 语言 key 地板 | §4.3 |
| R2-B6 | Fig.2 稻草人且可能给出相反结果 | 四条分布 + AUC 面板 + 预写 fallback 文案 | §4 Fig.3 |
| R2-B7 | 真机预算低估 4×，未算成对 base | 机器人小时预算算式进 §IV | §4.7 / §5.2 |
| R2-B8 | 两本体任务集不可比 | 任务集分 S/M/F 三层；一律报相对自身 base 的成对 Δ | §4.2 |
| R2-B9 | 缺 random-entry / self-prior / fixed-t0 等控制 | 6 个控制 arm 写进消融表 | §4.4 |
| R2-B10 | P2 二分法循环论证，缺第三桶 | oracle 阶梯（五级四差） | §4.5 P2 / Fig.5 |
| R2-B11 | 基线多数不可跑或不公平 | 真机只留 4 个条件 + 保真度门槛 + 结构性排除声明 | §4.3 |
| R2-B12 | 低样本 regime 会打坏写入机制 | headroom 用分布偏移制造，不用样本饥饿 | §4.1 |
| R2-B13 | 有害率定义有洞；删除泄漏是空实验 | 有害率写死为同 init 同噪声成对 + McNemar；删除泄漏实验砍掉 | §4.6 |
| R2-B14 | 规模主张单位不成立（Dejavu 到 1000 episode 仍单调升） | 双单位报数 + 主张改为"瓶颈性质变化" | §4.3 / §0.4 C4 |
| R2-B15 | 共享池设置未定义 | 三条件（own / shared tag-blind / shared tag-aware）+ 条目配平 | §4.5 P4 |
| R3-B1 | 基座微调 = 策略梯度，主张不成立 | E0 + 措辞改为 "before deployment, on disjoint tasks" | §0.6-B |
| R3-B2 | 实际 7.49 页 | §0.5 裁剪清单 | §0.5 / §5.1 |
| R3-B3 | Table I 自带两行反证核心句 | 母句加三限定词 + Table I 列序重排 | §2.3 |
| R3-B4 | entry 粒度未定义，三个数字不成立 | 片段级定义（夹爪状态机 + 速度过零） | §3.2 |
| R3-B5 | 库来源与"自写"冲突 | 同 R1-B6 | §3.7 |
| R3-B6 | ②③ 共用物体位姿前端，无双失败预案 | G2 开环重放 gate + 抓后用夹爪位姿代理 + 三点谱系退路 | §6 G2 / §3.4 |
| R3-B7 | 基线复现 3–4 人月不可交付 | 真机 4 条件；R-t-S 复现与我方注入器同一份代码 | §4.3 / §5.2 |
| R3-B8 | ANN 延迟曲线在 10⁵ 条上必然平坦 | 删除，换成对 in-context 的一句话对比 | §0.5 裁剪 7 |
| R3-B9 | Fig.2 平凡为真 | 同 R2-B6 | §4 Fig.3 |
| R3-B10 | 弱配对双本体数据未排期，在关键路径上 | 第 1 周启动采集；退路 = training-free 语言 key | §6 G3 / §5.2 |
| R3-B11 | 人力缺口近 2 倍 | FTE 假设写死 + MVP 清单 | §5.2 / §5.3 |
| R3-B12 | VLAC 可获得性未核实 | 本周核实；退路 = 遥操隐含标签 + 轻量成功分类器 | §7 优先级 1 |

**未解决 / 已接受的风险（诚实标注，不粉饰）**：
- **n=2 的一般性**：两具本体不足以支撑关于 embodiment 的一般规律。措辞一律限定为 "a spectrum measured on this pair"，绝不写 generalizes across embodiments。无技术解。
- **reader #3 是同一台 FR3 的改装**，不是真正的第三种形态。admission cost 只是下界。
- **绝对成功率可能很低**（对照：RECAP 真机 close-cabinet 30%；RoboMME 最好方法 44.51% 而人类 90.5%）。已在 §1 ¶5 主动划边界并在所有图里画 frozen-base 地板线。
- **抢跑窗口**：Dejavu 附录逐字写出我们的方案（"unified latent representation spaces or lightweight alignment layers that enable cross-robot retrieval and reuse of experience, while guarding against negative transfer"，一手核实）；RECAP §6 把跨本体检索表示标为 open question；RoboMME §6 点名 memory-bank methods + mobile manipulation；VLA-Pro future work 点名 hierarchical procedural states。**建议 G1 通过后立即 arXiv 占位 P1–P4。**

---

# 1. Section I. Introduction — 故事线与动机

**预算 1.00 页 = Fig. 1 (0.22) + 正文 5 段 ~660 词 + Contributions 4 条 ~150 词。**

## 1.0 全节写作红线（交稿前逐条核对）

- [ ] 全文无 first / blank / unexplored / no prior work / novel framework
- [ ] ¶2 内有一整句准确描述 RECAP 是 cross-embodiment 论文
- [ ] 母句三限定词（executable action content / written during its own deployment / no further policy update）在 Title-Abstract-¶2-C1-Fig.1 caption 五处逐字一致
- [ ] ¶4 主动交代基座微调的存在与其任务切分（E0），措辞为 "no gradient reaches either policy once deployed"
- [ ] 非贡献声明出现在 ¶4 与 Contributions 末尾两处
- [ ] Retrieve-then-Steer / RECAP / RoboMME / Dejavu 一律标 arXiv preprint（四者 PDF 内页均无 venue 标记）
- [ ] Retrieve-then-Steer 的记忆描述为 "(pooled visual-feature key, action chunk)"，不写"原始 obs-action 段"
- [ ] ¶3 的表示层级论断**只**限定在 cross-body readability，不外推到同本体精度
- [ ] 不出现 γ_sim = 0.9992 作为"机制性否决"的论据（风险 A）
- [ ] 不出现 O(T·B) / O(1) 复杂度论据（风险 B）
- [ ] transfer rate 若在 Intro 出现，必须当场给定义式

## 1.1 ¶1 — *The phenomenon, and why the obvious answer is not the answer*

**功能**：把"检索增强冻结 VLA 有效"设为既定前提；同时**当场堵死"为什么不共训"**（R1-B8，最强的"轴是硬造的"质疑）。这两件事必须在同一段完成，否则读者会带着这个疑问读完全文。

**核心句**：
> Retrieval-augmented frozen vision-language-action (VLA) policies now work. A deployed robot can store successful experience, retrieve it at test time, and improve its reliability without updating a single weight. This is no longer a conjecture: the design space has been surveyed, the mechanisms have been ablated, and the area has a benchmark.

> The obvious way to hand one robot's experience to another is to wait for the next training run. That answer is correct and it is not enough. Co-training amortises what a fleet already knows; it cannot amortise what one body learned an hour ago — a newly encountered object instance, a re-arranged workcell, a failure mode discovered this morning. A memory is worth crossing bodies precisely for experience that must be reusable before the next training run.

**证据与引用**（全部来自一手 PDF）：Retrieve-then-Steer（冻结 π0.5，LIBERO-10 92.4→94.4，推理开销 1.10×）；RECAP（策略冻结、只往池加演示，RoboTwin held-out 4.0→31.5）；Dejavu（部署中记忆库增长，LIBERO + AgiBot-G1）；RoboMME（该方向已有基准与 leaderboard）。RAEA (CVPR'24) 可用一个 e.g. 带过。

**注意**：¶1 引用的 92.4→94.4 是接近天花板的 regime，而我们预期的跨本体绝对值在地板附近。必须在本段末加一个从句区分两种 regime，否则与 ¶5 的能力边界叙事不自洽（Reviewer #2 指出的节间矛盾）：
> These gains are reported near the ceiling of their benchmarks; the regime we study is the opposite one, where the base policy is already unreliable.

## 1.2 ¶2 — *The premise nobody writes down*（**全文转轴，措辞精度决定生死**）

**功能**：点名共同前提，用可被逐条核对、可被证伪的形式陈述。

**母句（五处逐字一致的那一句）**：
> Yet across this family, no persistent store of *executable action content*, written by a robot *during its own deployment*, has been read by a *second deployed body without any further update to that body's policy*.

**逐个走一遍（每篇一句，含一手证据）**：
- **RECAP**（必须极小心，**这是唯一一句漏掉就等于 misrepresent related work 的**）：It is a cross-embodiment paper — its pool is written by a disc pusher, a UR5, or a human hand, and read by a different target robot. Two things separate it from the question we ask: its abstract states that *"Fine-tuning is needed only to take on a new, unseen embodiment, not for each new task,"* and its pool embodiment *"is never deployed."*
- **Dejavu**：其 Limitations 逐字（一手核实）"each VLA backbone maintains its own experience bank, tailored to a single domain or embodiment; this simplifies training but prevents reusing experience across ... different manipulation platforms"，并把 "unified latent representation spaces or lightweight alignment layers that enable cross-robot retrieval and reuse of experience, **while guarding against negative transfer**" 列为 future work。**这是全领域最接近我们命题的一手空白证据。**
- **Retrieve-then-Steer**：key 是复用 VLA 自己 visual encoder 的多视角池化特征；记忆**每个任务开始时重新初始化**（附录 D.3），连跨任务都不是。
- **VLA-Pro / CLARE**：条目就是 LoRA adapter / adapter 模块，与骨干和 action head 同生共死。
- **RAM / RoboOS**（必须主动点名，否则 Table I 自带反例）：RAM 的 660 条 affordance 库确实被两种本体读取，但它由第三方语料离线策划、部分人工修正，且 RAM 把自己成功的 rollout **蒸馏成 ACT 权重而非追加为条目**；RoboOS 的 shared memory 确实跨异构机器人且部署中增长，但其内容自陈是 scene graph、tool-calling 历史与各机器人的 joint/battery 状态 —— 跨过身体的是**东西在哪、哪台机器人有空**，不是怎么动。
- **镜像观察（收尾）**：确实被外来身体读取的动作知识——RoboTTT 的人类视频上下文、MimicDroid 的 human play video → 人形机器人（靠腕部位姿 retargeting）——用完即弃，不跨 episode 累积、不可检索、不可删除。

**结论句**：
> Persistence, self-authorship, and a second reader have so far not co-occurred in one store.

## 1.3 ¶3 — *Why this is a property of the entry, not of anyone's oversight*

**功能**：把现象升格为机制。**注意：此段的论证强度必须比基线设计低一档**（风险 A），改为"表示决定了什么必须被重新标定/重新解码"，而不是"机制性否决"。

**核心句**：
> Both ends of an entry — the key and the value — are written in the coordinates of the body that produced it. The value records what that body did: joint commands, action-expert latents, or adapter weights, none of which a different kinematic chain can execute. The key indexes the entry by that body's own perceptual features, so a foreign query is not merely less similar, it is *differently distributed*: the similarity threshold that a same-body retriever operates at is calibrated per deployment, and a reader swap forces a recalibration whose cost — how much recall must be given up to hold precision — has never been measured. **(§V-A, Fig. 3)**

> The field has optimised retrieval and injection while holding the entry representation fixed. For *cross-body readability* — and only for that; injection mechanisms demonstrably dominate same-body accuracy — the binding constraint is what the entry is made of.

**加分句（半句，若有余量）**：
> Robot memory has been given a taxonomy of *when*, *where*, *what* and *how* — four questions about what is remembered, and none about who may read it.

**红线**：不得写 v4 §2 那句"记忆的价值上限由表示层级决定，而不是由检索或注入机制决定"（RoboMME 实测 memory-as-modulator 44.51 vs memory-as-context 30.68 直接反驳）。

## 1.4 ¶4 — *What we change, why it is solvable now, and what we did not invent*

**功能**：四句交代方法 + 主动交代全部梯度 + 非贡献声明 + why now。

**(a) 分层 value**：
> We change what is stored. An entry records not what the body did but what the situation required, at four levels of abstraction at once: a language summary that names objects and relations but *no writer-frame pixel coordinates*, so that the reader re-grounds it in its own image; an object-centric subgoal sequence; end-effector deltas in an object-anchored task frame; and a joint-space action chunk.

**注意（Reviewer #2 抓到的冲突）**：RoboMME 实测 GroundSG（带像素坐标）全面优于 SimpleSG —— 但那是**同一台 Franka、同一相机**下测的。像素坐标是写入者相机系的量，换本体后无意义。**我们的 ① 层必须是"可重新 grounding 的语言"而不是"带写入者像素坐标的语言"**，并在 ¶4 用半句说明为什么不能照搬 RoboMME 的结论。

**(b) body-agnostic key**：冻结 VLM 前缀嵌入 + 物体中心关系编码，外加一张**只训练一次**的对齐图。

**(c) 统一读出接口（本文的机制增量，必须写清）**：
> Every level is decoded into the reader's own action space before readout, so that abstraction level is varied while the injection point is held fixed.

**(d) 主动交代全部梯度（不可省）**：
> Two things in this system are trained, and neither is trained during deployment. Each body's base policy is fine-tuned once before deployment, on tasks disjoint from the memory-evaluation tasks. The alignment map is trained once offline on weakly paired data — the two bodies performing the same task, collected independently rather than in correspondence — and is not updated as tasks or entries accrue. Once a body is deployed, no gradient reaches its policy, and admitting the store changes no weight. We also report a fully training-free, language-keyed variant as the honest floor.

**(e) 非贡献声明（第一处）**：
> Once an entry has been decoded into the reader's action space, everything that turns it into an action — aggregation into an elite prior, injection at an intermediate state of the flow-matching sampler, confidence-adaptive guidance strength, and abstention when confidence is low — is adopted unchanged from Retrieve-then-Steer. We claim no credit for it.

**(f) Why now（两个刚成立的前提）**：
- π0.5 级骨干共训过大规模 visual grounding 数据才吃得下符号记忆（RoboMME 实测换 OpenVLA-OFT 骨干后同样的符号记忆从 32.70 掉到 19.5）。
- 跨本体的写入门控已存在：VLAC 式 critic 依赖视觉状态与语言目标而非统一动作空间；Retrieve-then-Steer 报告其 precision 0.970 / recall 0.678，正是记忆写入需要的高 precision 工作点。**【待确认：VLAC 权重是否公开可得，见 §7 优先级 1】** 若不可得，本句改为"高 precision 低 recall 的写入门控在少量标注下可达"，并把 0.970/0.678 引为目标工作点而非现成组件。

## 1.5 ¶5 — *What we verify, the predictions, and the boundary*

**核心句**：
> We test this on two bodies that are both deployed: a fixed-base 7-DoF Franka FR3 and a π0.5-class mobile manipulator. Both write to and read from one store, in both directions. Two is the smallest number of bodies at which the question can be asked at all, and the pair is chosen as a clean binary contrast — fixed versus mobile base, fixed versus varying viewpoint. We report a spectrum measured on this pair, not a law about bodies.

**预注册预测（一句三分句，~60 词，带前向引用）**：
> We state our predictions before reporting results. **(P1)** Cross-body transfer rises with abstraction, while same-body accuracy is governed by content fidelity rather than by abstraction level (§V-B). **(P2)** The cross-body loss is dominated by the retrieval and retargeting terms rather than by value inexecutability (§V-C). **(P3)** Transfer is directionally asymmetric between the two bodies, and we attribute the asymmetry to viewpoint variability rather than to workspace inclusion (§V-D).

**P4 不进 Intro**（共享池负迁移是 P1 的推论，独立信息量最低，且需要一句设置说明）；在 §V-E 定义。

**主动划边界（不可省）**：
> Because both backbones stay frozen, what a memory buys is recall and recomposition of behaviour the base policy already possesses, not the acquisition of new motor skills. We report the per-trial memory-harm rate, and alongside every success rate we report the injection rate — the fraction of trials in which a prior was actually injected — because a retrieval system that abstains often can otherwise appear to transfer perfectly while doing nothing.

**最后一句（时效性论据的实验兑现，指向 E5）**：
> We also report the crossover point directly: how many fresh demonstrations the reader would need, and how long they would take to collect, to match what it gets by reading the writer's entries.

## 1.6 Fig. 1 设计与 caption

**Fig. 1（跨双栏，p.1 顶部，0.22 页，两 panel 横排 —— 已删除原 panel (c)）**

**Panel (a) "One store, two deployed bodies"**：左 = Franka FR3（定基 7-DoF，桌面场景）实拍；右 = π0.5 同款移动机械臂在**不同房间/不同视角**执行同一任务实拍。中间数据库圆柱标 `persistent store`。FR3 → DB 实线 `write`，DB → mobile 实线 `read`，读箭头挂徽章 `no gradient after deployment`（**不是 "no policy update"** —— 措辞必须与 ¶4(d) 一致）。浅色反向箭头表 bidirectional。角标小字：`both bodies deployed · both write · both read`。

**Panel (b) "What is in an entry, and how it is read"**：一张卡片，四条色带 ①grounded-but-re-groundable language ②object-centric subgoals ③object-anchored EE deltas ④joint-space action chunk；左侧钥匙图标标 `body-agnostic key`；**右侧画出统一读出接口**：四层各有一条箭头汇入同一个 `decode → reader's action space` 方框，再汇入 `frozen flow sampler, intermediate-state injection [R-t-S]`。这张图同时完成两件事：展示分层，以及**用图形声明注入通路是常量**（对抗 R1-B2 的共线质疑）。

**制作所需数据**：(a) 两台真机同任务实拍各 1 张（需现场补拍，含房间背景差异）；(b) 从我们自己的库导出的**一条真实条目**的四层内容（不要手编）。

**Caption 英文初稿**：
> Fig. 1. **A persistent action store shared by two deployed bodies.** (a) A fixed-base Franka FR3 and a mobile manipulator are both deployed; both write to and both read from a single persistent store, and each reads entries written by the other with no gradient reaching its policy after deployment. (b) Each entry holds the same experience at four levels of abstraction, from a language summary that the reader re-grounds in its own image down to a joint-space action chunk, indexed by a body-agnostic key. Every level is decoded into the reader's own action space before it is injected at an intermediate state of the reader's frozen flow-matching sampler, so that the level of abstraction is varied while the injection point is held fixed; the level actually reached is itself a measurement (§V-B).

## 1.7 待定决策（Intro 专属，写第一个字之前必须定）

1. **母句最终措辞** —— 已定为 §1.2 那句。五处派生对象（Title / Abstract / ¶2 / C1 / Fig.1 caption）必须逐字一致。
2. **Fig. 1 是否用真机照片** —— 是。RA-L 对首页真机照片有正反馈，且是我们相对纯仿真团队的可见壁垒。需在 G3 之前补拍。
3. **仿真是否进 Intro** —— 否（按 §0.5 裁剪 5）。¶5 只说 "on two bodies"，不写 "in simulation and on hardware"。
4. **P4 是否进 Intro** —— 否。


---

# 2. Section II. Related Work

**预算 0.75 页 = Table I (0.22, 跨双栏, 置于 p.2 顶部) + 正文 5 段 ≈ 480 词。**

## 2.0 划分依据（写作前必须内化的一句话）

**按"记忆物理上住在哪里"分区，不按"用了什么方法"分区。** 因为本文的命题是"谁能读一段记忆，由这段记忆被存成什么决定"，所以分区必须沿存储基底（上下文 → 参数 → 显式条目）切，"读者集合"就成为分区的推论而非另一条独立的轴。三个基底各自只能给出"持久"与"可跨体读"中的一个。

**术语锁定（全文 glossary，§III 开头一句话对齐）**：`writer body` / `reader body` / `reader swap`。RECAP 已占用 query embodiment / pool embodiment / cross-embodiment retrieval 且语义不同（其 pool 从不部署），我们**不沿用**它的词汇，只在 §III 用一句话做映射：*"Unlike [RECAP], where the pool embodiment is never deployed, both of our bodies are deployed and each is both a writer and a reader."*

## 2.1 II-A. Memory That Ends With the Episode（1 段，~110 词）

**功能**：提前拆掉"cross-embodiment reading is already done"这颗雷。

- 用 RoboMME 把这一族的形式化定义钉死：策略从 `a_t ~ π(·|l,o_t)` 扩展为 `a_t ~ π(·|l,o_t,M_t)`，历史定义为 `H_t = {(I_τ,a_τ)}_{τ<t}` —— **下标锁死在同一条 episode 内**。
- **采用其表示轴与注入轴的术语**（symbolic / perceptual / recurrent；context / modulator / expert），声明不另起炉灶。**但不宣称对齐其 when/where/what/how 四类任务**——那四类是 episode 内非马尔可夫推理的类别，我们的条目是跨部署动作先验，硬对齐是修辞而非事实（Reviewer #2 指出的节间矛盾）。四维只在 Intro ¶3 作为一句修辞出现（"四个问题都是记什么，没有一个是谁能读"）。
- **主动交出最危险的事实**：跨本体读取在这一族里已经发生过——MimicDroid 做人手腕部位姿到人形机器人的 retarget 以 bridge the embodiment gap；RoboTTT 从 in-context 人类视频做 one-shot imitation；RoboMME 真机的 TrackCube / RepickBlock 参考视频里操作者就是人类。
- **落点句**：这一族证明的是"另一具身体可以被读取"，不是"另一具身体可以读取被保存下来的东西"；上下文用完即弃，没有任何东西可以被索引、复访、删除。
- 免费引文：RoboTTT 自陈 long-term reasoning "can be delegated to external memory banks" —— in-context 阵营亲口把持久记忆的位置让出来。
- **不在 RoboMME 上报数**（决策已定，理由见 §7 优先级 6）。因此 II-A 只能写"我们采用其表示/注入轴的术语"，不能写"我们在其协议下报数"。

## 2.2 II-B. Memory Written Into Parameters（1.5 段，~150 词）

**¶2 —— 写一次经验 = 跑一次梯度。**
- Info-VLA（π0.5 骨干，LIBERO，摘要开篇 "suffer from severe catastrophic forgetting"）vs Liu et al.（预训练 π0 "remarkably resistant to forgetting"，"simple ER works surprisingly well… sometimes achieving zero forgetting even with a small replay data size"）。
- **遗忘之争的三句话（定稿，不站队，给可核对的方法学差异）**：
> Whether a pretrained VLA forgets is currently disputed on the same benchmark. The two positions differ in replay budget and in whether the policy is pretrained before the task stream begins, and we do not adjudicate them here. We report forgetting as a diagnostic rather than as a premise: whichever position holds, knowledge retained in weights can only be addressed through the weights that hold it — it cannot be enumerated, deleted one item at a time, or handed to another robot.
- **ER 立为一等基线**，但比较轴是写入代价而非成功率。

**¶3 —— 参数记忆已经条目化、可删除、可检索。**
- CLARE（模块化 adapter + 按层特征相似度自主扩展 + 部署期无标签 autoencoder 路由；LIBERO + 5 个真机任务，全部单台 Panda）；VLA-Pro（把 task-specific LoRA adapter 当作 parameterized procedural memory 存进 bank，推理时检索并动态融合）。
- **主动认输的那句话**：删掉一个 adapter 就删掉一个技能 —— **条目级可撤销性因此不是本文卖点，而是共享性质**；"对参数条目做检索"也已被 VLA-Pro 做掉。
- **一个从句主动点出** VLA-Pro 的 future work 已写到 "hierarchical or compositional procedural states"，即分层记忆表示对它不是盲区而是排期项，且发生在参数基底内。
- **大规模跨本体共训（RT-X / OpenVLA 一族）并入本段**：同样把跨本体知识写进参数，只是粒度是整个预训练；一组权重可以驱动多具身体，但身体集合与技能集合在梯度跑完时就冻结了。**共训不产生记忆对象，故不进 Table I**（有原则的排除，正文写明一句）。**【待确认】RT-X / OpenVLA 一手 PDF 本组尚未读过，只能作结构性表述，不得引用任何数字或 venue。**

## 2.3 II-C. Memory Written As Explicit Entries（2 段，~200 词，全节最重）

**¶4 —— 按条目里 value 的抽象层级排成阶梯（这是 §III 分层设计的动机来源）。**
- **④ 逐帧原始动作**：VINN 存逐时间步 (观测嵌入, 专家动作)，读出是嵌入空间 k 近邻的 softmin 加权平均；人手演示落到机器人时需一个**手调的逐轴系数**补本体差（来源：`threat_RAM_RoboOS.md` §11）。**venue 未核实，引用时只标 arXiv。**
- **③ 物体相对末端速度**：Di Palo & Johns (**RA-L 2023**) 的 retrieve–align–replay，DINO-ViT 检索 bottleneck 目标图 + 视觉伺服对齐 + 开环回放 6-DoF EE 速度轨迹，training/intra-class/inter-class 80% / 73% / 67%；DINOBot (ICRA'24) 保留完全相同的 value，只换对齐机制。**同 venue，必须主动引用、主动划界。**
- **② 物体中心 affordance**：Robo-ABC（51 类，(无遮挡 crop, 2D 接触点)）；RAM（660 条，离线取自 DROID / HOI4D / 互联网图片，读出为一个 3D 接触点 + 一个接触后方向，由 AnyGrasp + MoveIt!/cuRobo 执行，自称 zero-shot、embodiment-agnostic，跨本体只有定性 demo 无成功率表）。
- **① 语言 / 规划层**：RoboHarness（success/failure 双库 + 两阶段 consolidation，围绕冻结 π0/π0.5/SmolVLA，全部 LIBERO 仿真无真机）；RoboOS（跨异构机器人的 shared memory：场景图、工具调用历史、各机器人 motion domain constraints / 关节状态 / 电量）。
- **落点句（= SQ1 的动机句）**：这四层各自被不同的论文、在不同的机器人上、用不同的协议与不同的读出端（运动规划器 / 视觉伺服+开环回放 / k-NN 平均 / 提示词重写）占据 —— 正因如此，层与层之间的权衡至今无法被比较。
- **必须主动说清 RoboOS 的边界**：跨越身体的是**东西在哪、哪台机器人有空**，不是怎么动；技能仍封装在各机器人本地的 skill library；其 "embodiment memory" 恰是本体绑定信息的显式存储，反而是我们论点的正面例证。
- **必须主动说清 RAM 的边界**：660 条全部离线取自第三方语料且部分人工修正；**RAM 把自己成功的 rollout 蒸馏成 ACT 权重而非追加为条目**（最有力的一击）；读出端是抓取生成器 + 运动规划器。
- Ag2Manip 用半句带过，仅为拆掉 "agent-agnostic" 的命名撞车（它根本没有记忆库，知识在编码器权重里，单本体）。

**¶5 —— 现代冻结 VLA 系统：条目是谁写的 / 换读者要付什么。**
- **Dejavu**：冻结 VLA + Experience Feedback Network，记忆库在部署中持续扩充；但 EFN 是 RL 训出来的，且其 Limitations 逐字（一手核实）"each VLA backbone maintains its own experience bank, tailored to a single domain or embodiment; this simplifies training but prevents reusing experience across ... different manipulation platforms"，并把 alignment layers + guarding against negative transfer 列为 future work。
- **Retrieve-then-Steer**：冻结 π0/π0.5/CogACT，部署中在线写入经 VLAC 校准的成功片段；条目是 (VLA visual-encoder 池化特征 key, action chunk)；注入点是 flow 采样器中间态 + 置信度自适应引导；**记忆每个任务重新初始化**；淘汰只有 FIFO。
- **RECAP**：配对演示训练一次后冻结，靠往池追加 pool 侧演示免训练吸收新任务；共享表示是 SE(3) EE pose + gripper；pool embodiment "is never deployed"；摘要逐字 "Fine-tuning is needed only to take on a new, unseen embodiment, not for each new task"；Limitations 把 "what constitutes an effective representation for cross-embodiment retrieval" 亲口标为 open question。
- retrieve-then-finetune 一族（Behavior Retrieval / STRAP）：检索的是**训练数据**，取回后仍要跑梯度，一句话划走。**【待确认】两篇全文本组尚未读，Table I 中该族已整行删除（见 2.4）。**
- 其余同族（RAEA / RTCF / Remember Smarter / SkillMemo / RAGDP）打包一个 e.g.。
- **落点句**：这些系统里读者本体在设计时就固定了。RECAP 把适配代价在任务上摊薄，没有在身体上摊薄；Retrieve-then-Steer 的相似度门是逐部署标定的，换读者要重新标定，代价从未被测过（前向引用 Fig. 3）；Dejavu 直接把跨机器人复用写成自己的 future work。
- **同段声明沿用**（不能没有）：中间态注入与置信度自适应引导来自 Retrieve-then-Steer；零梯度池增长的证明范式来自 RECAP（其 Fig.4 PushT 6.0→34.9、Fig.7 RoboTwin 池 11→35 任务 9.0→31.5，策略全程冻结）。

**II-D 已并入 ¶5 末尾（3 句，不引入新文献）**：
1. 合取式一次说完：由部署中的机器人自己零梯度单步写入；作为可删除的显式条目跨部署留存；被另一具同样在部署中的身体在无策略梯度下读取；读出端是冻结 VLA action expert 加一个非学习的 retarget 算子（**必须补上 retarget，否则是 overclaim**）。
2. 诚实清单（不可省）：注入机制来自 Retrieve-then-Steer；零梯度池增长来自 RECAP；条目级删除来自 CLARE；表示/注入轴的术语来自 RoboMME；embodiment-agnostic 检索来自 RAM；②③④ 三层的表示设计分别有 RAM / Di Palo & Johns / VINN 的先例。
3. 贡献钉在唯一不可替代的那条：**在同一次采集、同一套协议、同一个读出接口下并排测量四个抽象层级的迁移率，并把跨本体损失分解为 key / retarget / value 三项。**

## 2.4 Table I（完整 Markdown，8 行 × 6 列，纯符号）

**caption 必须承载全部散文与判定标准，否则每一格都可被质疑不公平。**

**列定义**：
- **Value** = 持久保存的内容的抽象层级（①语言 ②物体中心 ③任务坐标系 EE ④关节动作/潜码；`par`=参数；`env`=环境/调度状态；`ctx`=仅上下文）
- **Persist** = 是否跨 episode 且跨部署存活
- **Self-write** = 是否由部署中的机器人自己写入且写入无梯度
- **2nd reader** = 是否有第二具身体消费该条目（`✓*` = 需 target 侧梯度）
- **Readout** = 取回后由什么变成动作（`pol`=学习策略；`plan`=运动规划器/伺服/开环回放；`grad`=再训练；`ctx`=上下文条件化）
- **New-reader cost** = 引入一个新读者本体的代价

**列序刻意排成 Value → Persist → Self-write → 2nd reader → Readout**，读者顺着列读下来就自动得到母句的三个限定词。

| # | Family (representative) | Value | Persist | Self-write | 2nd reader | Readout | New-reader cost |
|---|---|---|---|---|---|---|---|
| 1 | Within-episode context (RoboMME; RoboTTT; MimicDroid) | ctx | ✗ | ✓ (episode) | ✓ (human→robot) | ctx | n/a |
| 2 | Parametric, monolithic (seq. FT; ER) | par | ✓ | ✗ | ✗ | grad | full retrain |
| 3 | Parametric, modular (CLARE; VLA-Pro) | par | ✓ | ✗ | ✗ | pol | impossible (bound to backbone) |
| 4 | Explicit entries, planner readout (VINN; Di Palo & Johns; Robo-ABC; RAM) | ②③④ | ✓ | ✗ | ✓ (RAM, qualitative) | plan | n/a (no policy) |
| 5 | Explicit entries, agent level (RoboHarness; RoboOS) | ①/env | ✓ | ✓ | ✓ (RoboOS) | ctx / plan | none, but no action content |
| 6 | Deployment-written, same body (Retrieve-then-Steer; Dejavu) | ④ | per-task ↺ / ✓ | ✓ / ✓(bank) | ✗ | pol | not supported |
| 7 | Curated cross-body pool (RECAP) | ③ | ✓ | ✗ (pool never deployed) | ✓* | pol | one target-side fine-tune |
| 8 | **Ours** | **①–④ + tag** | **✓** | **✓** (deployment store) | **✓** (both deployed, bidirectional) | **pol + retarget** | **one alignment map, no policy gradient** |

**相对基线设计的三处判定修正（必须执行）**：
- **RECAP 的 Delete 列已整列删除** —— 原判 ✓ 的依据是"4 episodes removed by hand"，但那是训练期为对齐卫生剔除的 query episode（训练数据清洗），不是部署期条目删除；范畴错误。删除列同时省版面。
- **Retrieve-then-Steer 的 Persist 写作 `per-task ↺`（重新初始化），不给 ✓** —— 附录 D.3 明说每个任务评测开始时记忆被初始化。
- **Behavior Retrieval / STRAP 整行删除** —— 本组未读全文，原表 4 个 `?`。改为 ¶5 一句话划走。**不得靠推测填格。**

**Table I caption 英文初稿（承载散文与证据来源）**：
> TABLE I. **Where a robot's memory lives, and who may read it.** Value: the abstraction level of what persists — ① language, ② object-centric subgoal/affordance, ③ task-frame end-effector motion, ④ joint-space actions or latents; `par` = parameters, `env` = environment/scheduling state, `ctx` = context only. Self-write: written by a robot during its own deployment, without gradients. 2nd reader: the paper reports or demonstrates a body other than the writer consuming stored entries; `✓*` denotes that a target-side fine-tune is required. Readout: `pol` = a learned policy, `plan` = a motion planner, visual servo or open-loop replay, `grad` = further gradient training, `ctx` = context conditioning. Evidence, by row: (1) memory is formalised over the current episode only; (4) RAM's 660 entries are mined offline from third-party corpora and partly hand-corrected, and its own successful rollouts are distilled into policy weights rather than appended as entries; (5) RoboOS states that its shared memory holds scene graphs, tool-calling history and per-robot joint and battery state — no action content; (6) Retrieve-then-Steer re-initialises its memory at the start of each task; (7) RECAP's pool embodiment "is never deployed", and its abstract states that fine-tuning is needed for a new embodiment. Large-scale cross-embodiment co-training is deliberately absent: it produces weights, not memory objects.

## 2.5 审稿人备答清单（每条英文反驳，写进 rebuttal 模板）

| 预期质疑 | 英文备答（可直接粘贴） |
|---|---|
| "RECAP already does cross-embodiment retrieval." | RECAP is a cross-embodiment paper and we say so in §II. Its pool embodiment is never deployed and its reader is fixed at training time: its abstract states that fine-tuning is needed to take on a new, unseen embodiment. Our question is what it costs to admit a *new reader* to an *existing* store; we measure that cost (§V-F) rather than pay it. |
| "RAM already claims embodiment-agnostic memory." | RAM's memory is authored offline from DROID, HOI4D and web images, partly refined by hand, and is never written to by the robots that read it — RAM converts its own successful rollouts into ACT weights instead. Its readout is a grasp generator plus a motion planner, and it reports no cross-embodiment success rate. It is a baseline at the object-centric level of our ladder, and we treat it as one. |
| "RoboOS already has a shared memory across heterogeneous robots." | It does, and what crosses bodies there is where objects are and which robot is free — RoboOS itself describes its memory as spatial, temporal and embodiment state. Skills stay in each robot's local library. Our claim is restricted to *executable action content*, which is exactly the content RoboOS does not share. |
| "The similarity-gate argument is a straw man; you would just recalibrate." | We agree, and we do not make that argument. We recalibrate per condition and report threshold-free retrieval quality (Fig. 3); what we measure is the recall a cross-body reader must give up to hold precision. |
| "This is Neural Episodic Control with a VLA backbone." | NEC's memory is a per-agent, per-body table of value estimates; the property we study — whether an entry written by one body can be read by another — is not defined in that setting and is never measured there. |
| "Persistent, gradient-free growth was already shown by RECAP." | It was, and we cite it as the standard for that claim. We do not claim it; we hold the store fixed and swap the reader instead. |
| "Entry-level deletion was already shown by CLARE." | Yes. Revocability is a property we share with modular adapter memories, not a contribution. The property adapters cannot have is a second reader. |
| "Di Palo & Johns showed open-loop replay beats a learned policy." | That result holds when alignment makes replay frame-invariant and when a single body defines the end-effector frame. Once the reading body differs, the semantics of a stored end-effector trajectory are no longer preserved, which is precisely the quantity we measure (§V-C, retargeting term). |
| "Your sweep is much thinner than RoboMME's 14 variants." | Our sweep runs along the body axis (2 deployed bodies × 4 value levels × k key constructions), not along the representation axis; we adopt RoboMME's representation and injection vocabulary rather than competing with its coverage. |
| "Two bodies cannot support a claim about embodiment." | Two is the smallest number at which the question exists, and we phrase every conclusion as a spectrum measured on this pair. We additionally admit a third, previously unseen reader configuration to report admission cost. |


---

# 3. Section III. Method — 结构 / 数据管线 / 模块

**预算 1.30 页 = Fig. 2 (0.20) + Algorithm 1 (0.12) + 正文 ~0.98 页。**
子节：III-A Problem setting (0.20) / III-B Entry (0.25) / III-C Key and alignment (0.22) / III-D Readout (0.25) / III-E Write gate and lifecycle (0.14) / Fig.2 + Alg.1 (0.32)。

## 3.1 III-A. Problem setting（含 LaTeX）

**术语对齐句（第一句）**：
> We call the body that produced an entry its *writer* and the body that consumes it a *reader*; a *reader swap* is the substitution of one for the other with the store held fixed. Unlike [RECAP], where the pool embodiment is never deployed, both of our bodies are deployed and each is both a writer and a reader.

**形式化**：

```latex
% Bodies and policies
\mathcal{B}=\{b_A,b_B\},\qquad
\pi_b(\mathbf{a}\mid \mathbf{o},\ell),\ \ \mathbf{a}\in\mathbb{R}^{H\times d_b}
% each pi_b is a flow-matching VLA, frozen after a single pre-deployment
% fine-tune on task set T_base with T_base \cap T_eval = \emptyset   (E0)

% Store
\mathcal{M}=\{e_i\}_{i=1}^{N},\quad
e_i=\bigl(\mathbf{k}_i,\ \{v_i^{(\ell)}\}_{\ell=1}^{4},\ \beta_i,\ c_i,\ t_i\bigr)
% k: body-agnostic key ; v^(l): value at abstraction level l
% beta: writer-body tag ; c: write-gate calibration score ; t: timestamp

% Write (single step, no gradient)
\mathcal{M}\leftarrow\mathcal{M}\cup\{\,e(\sigma)\ :\ \sigma\in\mathrm{Seg}(\tau),\ g(\tau)=1\,\}
% Seg: segmentation of a rollout into motion segments ; g: write gate

% Read at time t on reader b
\mathcal{I}= \mathrm{TopK}\bigl(\mathrm{sim}(\mathbf{q}_b(\mathbf{o}_t),\ \mathbf{k}_i)\bigr),\qquad
\hat{\mathbf{a}}_i=\mathcal{D}_b^{(\ell)}\bigl(v_i^{(\ell)},\ \mathbf{o}_t\bigr)\in\mathbb{R}^{H\times d_b}
% D_b: level-l decoder into the READER's action space -- the shared interface

\mathbf{a}_{\mathrm{elite}}=\textstyle\sum_{i\in\mathcal{I}} w_i\,\hat{\mathbf{a}}_i,\qquad
\mathbf{x}_{t_0}=(1-t_0)\,\mathbf{a}_{\mathrm{elite}}+t_0\,\boldsymbol{\epsilon}
% aggregation weights w_i, guidance start t_0 and abstention: unchanged from [R-t-S]
```

**指标定义（必须在此处给出，Table I 最后一列与 P1 都依赖它）**：

```latex
\mathrm{SR}^{\mathrm{same}}_{\ell},\ \mathrm{SR}^{\mathrm{cross}}_{\ell}\ \ \text{(absolute success rates)}\\
\mathrm{TR}_{\ell}=\mathrm{SR}^{\mathrm{cross}}_{\ell}\big/\mathrm{SR}^{\mathrm{same}}_{\ell}
\qquad\text{(reported for context only; all claims use absolute SR and paired }\Delta)
```

**为什么主张不建在 TR 上（一句话写进正文，对抗 R2-B1）**：
> A ratio of success rates can be driven to one by abstaining more often; we therefore state every claim in absolute success rate against each reader's own memoryless base at matched initial state, and report the injection rate alongside.

## 3.2 III-B. What an entry is（含粒度定义 —— R3-B4）

**粒度（必须写死，否则 §V 的三个数字都不成立）**：
> An entry is one *motion segment*, delimited by gripper open/close events and by zero-crossings of end-effector speed. Segmentation is a state machine over signals already present in our corpus; no learned segmenter is used. Mean segment length is \todo{L} steps, so a store of \todo{N} entries corresponds to \todo{M} episodes; we report both units throughout, since per-timestep entry counts in prior work are not comparable to segment-level counts.

**四层 value 的数据结构与生成方式**：

| 层 | 内容 | 生成方式 | 存储量级 | 已有占位者（RW 必须引用） |
|---|---|---|---|---|
| ① language | 一句摘要：动作动词 + 物体名 + 物体间关系（**无写入者像素坐标**），例 `"pull the top drawer handle toward the operator side"` | 冻结 VLM 对片段首末帧 + 任务指令生成；oracle 版由演示脚本/人工提供 | ~40 B | 无直接占位者 |
| ② object-centric subgoal | 子目标序列 `[(approach, handle), (grasp, handle), (translate, +0.15 m along handle axis), (release)]`，坐标在**物体系** | 由 ① + 物体跟踪结果构造；oracle 版由仿真真值/演示脚本 | ~200 B | RAM / Robo-ABC |
| ③ object-anchored EE deltas | `Δp ∈ R^{T×3}`, `Δr ∈ so(3)^{T}`, gripper，锚定在**物体坐标系**（**不是机器人基座系** —— 移动底盘下基座系无意义） | 由末端位姿轨迹 + 物体位姿序列做变换 | ~2 KB | **Di Palo & Johns (RA-L'23)** / DINOBot |
| ④ joint-space chunk | 写入本体的关节动作序列，按读出本体的 action horizon `H` 切块 | 直接来自 rollout | ~4 KB | VINN |

**存储成本一句话（必须给实测，不可空口）**：`bytes/entry = \todo{}`；10⁵ 条 = \todo{} GB。**但成本不是争点，必要性才是** —— 见 III-D 的 derive-on-read 论证。

**②③ 共用同一个感知前端（必须主动写明，R3-B6）**：
> Both the object-centric subgoals and the object-anchored deltas require a 6-DoF object pose. We obtain it with a detector and tracker before grasp, and with the gripper pose itself after grasp, exploiting the rigid attachment; ② and ③ therefore share a failure mode, and we report them as such.

## 3.3 III-C. A body-agnostic key and the alignment map

- **key 构造（4 种，作为 §V-A 的对照）**：
  1. `lang`：冻结文本编码器编码 ① 层摘要。**完全无训练**，是诚实地板（R2-B5 要求的、不受对齐图泄漏影响的唯一 arm）。
  2. `vlm-prefix`：冻结 VLM 前缀嵌入池化。
  3. `obj-rel`：物体中心关系编码（物体类别 + 相对位姿图），采用 RECAP 式 20-D sign-flip 不变 proprio 编码（位置权重 4.0）作为几何分量 —— **直接沿用并引用，省一轮调参**。
  4. `aligned`：`vlm-prefix ⊕ obj-rel` 经一张 2 层 MLP `h_b(·)` 映射到共享空间。
- **对齐图的训练协议（对抗 R2-B5 的泄漏质疑）**：
> The alignment map is trained on weakly paired data — the two bodies performing the same task, collected independently rather than in correspondence — on a task set `T_align` disjoint from the evaluation tasks `T_eval`. All main-table numbers use the held-out-task protocol; in-domain numbers appear only as an upper bound.
- **损失**：同任务同阶段的跨本体样本为正对，InfoNCE。参数量 <2M，训练 <\todo{} GPU-minutes（这个数字进 §V-F 的 admission cost 表）。

## 3.4 III-D. Readout: one interface, four levels（**本文的机制增量**）

**统一接口（这是同时解决 R1-B2 与 R1-B7 的关键设计）**：
> Every level is decoded into the reader's action space before injection:
> ① → a frozen VLM re-grounds the summary in the reader's current image and emits subgoals → ② ；
> ② → subgoals are instantiated as object-frame waypoints → ③ ；
> ③ → object-frame deltas are transformed into the reader's task frame and solved to a joint-space chunk (IK / differential IK) → ④ ；
> ④ → used directly.
> All four therefore enter the same aggregation and the same intermediate-state injection, so that the level of abstraction is varied while the injection path is held fixed.

**回退读出**：同本体优先 ④；跨本体从 ④ 起逐级上移，直到解码成功且 IK 可行。**回退到哪一层本身是实验读数。**

**与 Retrieve-then-Steer 的边界声明（英文一句，正文原文）**：
> For entries decoded into the reader's action space, we adopt the aggregation, the intermediate-state initialisation of the flow sampler, the confidence-adaptive guidance strength, and the abstain-and-fall-back rule of [R-t-S] unchanged, including its component-aware aggregation of Euclidean, SO(3) and gripper components. What is not part of that method, and what we describe here, is the decoding path that maps entries at different levels of abstraction into a single such action-space prior.

**derive-on-read 的必要性论证（对抗 R1-B3，本文唯一的辩护）**：
> Levels ①–③ are deterministic functions of level ④ together with the stored frames, so an information-equivalent store could materialise only ④ and derive the rest at read time. The difference is where the cost is paid. We measure it: deriving ① and ② at read time requires a VLM call inside the control loop and adds \todo{X} ms per retrieval against a budget of \todo{Y} ms at the chunk boundary. **If \todo{X} is within budget and success rates match, Contribution 2 is restated as a protocol/measurement contribution rather than a representation contribution** —— 这个 fallback 必须现在写好（见 §6 G4 的判定）。

## 3.5 III-E. Write gate and lifecycle

- **写入门控**：episode 结束后按跨本体进度评估器打分，只写 progress-peak 之前的前缀（沿用 Retrieve-then-Steer 的写入范式并引用）。目标工作点：**高 precision 低 recall**（其报告 precision 0.970 / recall 0.678）。**【待确认】VLAC 权重可得性；退路见 §7 优先级 1。**
- **生命周期**：容量上限 + 时效衰减 + **条目级删除**（声明为与 CLARE 共享的性质，不作卖点）。
- **删除后的残留泄漏探针已砍掉**（对显式条目表平凡为真；R2-B13）。若审稿人问，备答：残留通道只有三条（对齐图训练集、ANN 索引码本、按本体对的置信度标定量），我们的对齐图在 `T_align` 上训练、不含部署条目，故不存在该通道。

## 3.6 两个 store 的定义（全文贯彻，对抗 R1-B6 / R3-B5）

| | `S_deploy` | `S_corpus` |
|---|---|---|
| 来源 | 评测期两台机器人自己 rollout + 写入门控 | 数百小时存量遥操语料离线灌入（**curated**） |
| 规模 | \todo{~10³} 条 | \todo{10⁴–10⁵} 条 |
| 用途 | **P1 / P2 / P3 与全部主结果**；Self-write 主张的唯一证据；在线增长曲线 | **仅**规模、串扰、P4 |
| 图表标题 | 无标注 | 必须写 `corpus-seeded` |

Table I 的 ours 行 Self-write 脚注：`✓ for the deployment store; the scaling study uses a corpus-seeded store.`

## 3.7 Fig. 2 设计（单栏，0.20 页）

三块横排：**(a) Write** —— rollout → 分段 → 写入门控 → 四层 value + key + body tag 写入 store；**(b) Index** —— 四种 key 构造与对齐图 `h_b`，标注"trained once, offline, on `T_align`"；**(c) Read** —— query → top-K → **四条解码路径汇入同一个 `reader action space` 方框** → elite prior → 冻结 flow 采样器中间态注入（灰底标 `[R-t-S], unchanged`）。灰底是图形化的非贡献声明。

**Caption**：
> Fig. 2. **System overview.** A rollout is segmented into motion segments; a write gate admits only progress-verified prefixes, and each admitted segment is stored at four levels of abstraction with a body-agnostic key and a writer tag. At read time, retrieved entries at any level are decoded into the *reader's* action space, so that all levels share one injection path. The shaded block is adopted unchanged from [R-t-S].

## 3.8 Algorithm 1（伪代码，0.12 页）

```
Algorithm 1: Deployment loop for reader body b (policy frozen)
Input: store M, frozen policy pi_b, key encoder q_b, alignment map h_b
 1: for each control step t at a chunk boundary do
 2:    k_q <- h_b(q_b(o_t))
 3:    I <- TopK_i sim(k_q, k_i) ; filter by consistency (DTW)          # [R-t-S]
 4:    if I = empty then a <- pi_b(o_t, l) ; continue                    # abstain, [R-t-S]
 5:    for i in I: l_i <- highest executable level ; a_i <- D_b^(l_i)(v_i, o_t)
 6:    drop i whose IK/retarget fails ; if none left then abstain
 7:    a_elite <- sum_i w_i a_i ; c <- alpha*s~ - beta*sigma_DTW         # [R-t-S]
 8:    t0 <- t_min + (1-t_min)*sigmoid(-gamma*c)                         # [R-t-S]
 9:    a <- FlowSample(pi_b, o_t, l, x_{t0}=(1-t0)a_elite + t0*eps)      # [R-t-S]
10:    execute a ; buffer (k_q, executed chunk)
11: end for
12: at episode end: s <- WriteGate(rollout) ; if s>=eta then
13:    for sigma in Seg(prefix up to progress peak): M <- M U {e(sigma, tag=b)}
```
**记录项（用于 §V 的报表）**：第 4 行与第 6 行触发次数 → abstain rate；第 9 行执行次数 → **injection rate**。

## 3.9 离线数据管线的分步骤工程清单（含工时）

| # | 组件 | 内容 | 工时 | 关键路径 | 省工替换 |
|---|---|---|---|---|---|
| D1 | 片段分割 | 夹爪 open/close 状态机 + EE 速度过零；输出片段边界 | **1 周** | 是 | 禁止上学习式分段（省 2 周） |
| D2 | 物体检测与跟踪 | 抓取前用检测器+跟踪；**抓取后用夹爪位姿代理**（刚性附着） | **3 周** | 是（②③ 共同前端） | 代理法把 6 周压到 3 周 |
| D3 | 物体系与任务坐标系 | 由 D2 输出定义 object-anchored frame；③ 层轨迹变换 | **2 周** | 是 | — |
| D4 | ① 层生成 | 冻结 VLM 对首末帧 + 指令生成摘要；**禁止写入者像素坐标**；oracle 版另做 | **2 周** | 否 | 批处理离线跑 |
| D5 | ② 层生成 | 由 ①+D2 构造子目标序列；oracle 版由演示脚本 | **1.5 周** | 否 | — |
| D6 | key 编码器 ×4 + 对齐图 | 冻结编码器封装 + InfoNCE 训练脚本 | **2 周** | 是 | — |
| D7 | store + 索引 + 生命周期 | 条目表、暴力 cosine（10⁵ 条足够）、FIFO+时效、删除 | **1 周** | 是 | **不做 ANN**（省 1 周，且删掉了一个空实验） |
| D8 | 读出与注入 | 四条解码路径 + retarget/IK + Eq.(6) 注入 | **3 周** | 是 | **与 R-t-S 复现共用同一份代码**（省 4 周） |
| D9 | 写入门控 | VLAC 或替代成功判别器 + progress-peak 截断 | **2–4 周** | 是 | VLAC 若可得取下界 |
| D10 | 仿真 harness | 单模拟器内双机器人 + 2×2 因子评测 | **3 周** | 否（G3 后可砍） | 不进正文则只做 key 侧离线分析（省 2 周） |
| D11 | 真机基础设施 | 双平台评测自动化、成对同 init/同噪声 rollout、复位、日志 | **4 周** | 是 | — |
| D12 | 弱配对数据采集 | 10 任务 × 30 episode × 2 本体 | **2–3 周**（40–60 机器人小时） | **是（最被低估的一条）** | 第 1 周就启动 |

**合计 ≈ 26.5–29.5 周 ≈ 6.2–6.9 人月的纯工程**，另加实验执行 1.5 PM + 分析画图 1.0 PM + 写作 1.0 PM + 基座微调与调试 1.5 PM ≈ **11–12 人月**（不含额外基线复现）。详见 §5.2。


---

# 4. Section IV/V. Experiments

**预算：§IV 0.40 页（setup）+ §V 2.05 页（results）。**

## 4.0 实验问题 → 表图映射

| 问题 | 交付对象 | 页数 | 若砍到 4 个图表时的去留 |
|---|---|---|---|
| reader swap 的检索代价（C1） | **Fig. 3** 检索质量（直方图 + precision@k/AUC） | 0.16 | **保留（第 4 位）** |
| 迁移率谱系（P1, C2） | **Fig. 4** 四层 × {cross, same} × {oracle, auto} | 0.20 | **保留（第 2 位）** |
| 跨本体损失分解（P2, C4） | **Fig. 5** oracle 阶梯（五级四差） | 0.18 | **保留（第 3 位）** |
| 主结果 + 方向不对称（P3, C3） | **Table III** 真机主表（含 injection rate / harm rate / 成对 Δ） | 0.28 | **保留（第 1 位）** |
| 控制与消融 | **Table IV** 6 个控制 arm + 共享池三条件（P4） | 0.20 | 砍到 4 个时移出正文 → 补充材料 |
| 协议与基线 | **Table II** | 0.15 | 砍到 4 个时并入正文文字 |
| reader #3 admission cost | 正文 3 行 + 2 个数字 | 0.05 | 保留（文字） |
| 时效性交叉点（E5） | 正文 2 行 + 3 个数字 | 0.04 | 保留（文字） |
| 规模与串扰（C4 后半） | 正文 2 行 + precision@k vs 规模的一句话 | 0.04 | 保留（文字） |

**图表优先级（砍到 4 个留哪些）**：`Table III > Fig. 4 > Fig. 5 > Fig. 3`。Fig. 1 与 Fig. 2 不参与这个排序（teaser 与系统图在 RA-L 是刚需）。

## 4.1 仿真设计（**不进正文**，只作内部 go/no-go 与离线分析）

**决策依据**：LIBERO↔RoboCasa 当双本体会同时改变 body / scene / assets / 相机 / 任务语义 / demo 生成管线 / 动作维度至少 8 个变量，body 主效应不可识别（R2-B2）。

**必须做的 2×2 因子设计（若做，就必须四格齐）**：

| | scene S1 | scene S2 |
|---|---|---|
| body A | SR(A,S1) | SR(A,S2) |
| body B | **SR(B,S1)** ← 因果估计量 | SR(B,S2) |

- **落地路径**：LIBERO 建在 robosuite/MuJoCo 上，**在同一套 LIBERO 场景/物体/相机位姿下换第二个机器人模型并重跑 demo 回放**。可行性用 ≤1 周验证（**G3a**）。
- **不可行则**：仿真退出正文，只保留 key 侧离线分析（Fig. 3 的一部分可在仿真上先跑），并在 §IV 用一句话说明这个决定。
- **headroom 的制造方式（对抗 R2-B12）**：**不用样本饥饿**。保持每任务演示量足以让基座在训练分布内是强的（否则写入门控没有成功轨迹可写，记忆库近乎空，测到的是写入率而非迁移率），改在**评测端**施加光照 / 干扰物 / 初始位姿 / 相机位姿扰动，把基座压到 **40–60%** 区间。§IV 必须写明这个 regime 选择的理由。

## 4.2 真机设计

### 平台与任务集分层（对抗 R2-B8）

| 层 | 定义 | 任务数 | 用途 |
|---|---|---|---|
| **S 层** | 两体皆可执行、底盘静止 | **12** | **唯一的 confirmatory 端点** |
| **M 层** | 仅移动臂可（需底盘导航/变工作空间） | 2 | scope 说明 + 定性视频 |
| **F 层** | 仅 FR3 可（需高刚度，如插装） | 2 | scope 说明 |

**S 层任务必须包含 ≥3 个"语言不可表达"任务**（对抗 R1-B4，全篇唯一能结构性击败 instruction-only 对照的实验）：非语义化轨迹形状、指定接触/速度剖面。例：按图案擦拭、沿非规则路径推动、带特定进给节律的插销。**若没有这类任务，"记忆 ≠ 更好的 prompt" 无法证明。**

**Intro ¶5 的措辞相应收窄**：`compared on a task set both bodies can execute`，并主动声明这是 embodiment gap 的**下界估计**。

### 主端点（confirmatory，预注册，只有一个）

- **12 任务 × 20 成对 trial × 2 个 reader 方向**，成对 = **同初始状态 + 同 flow 噪声种子 ε**。
- 每个 trial 跑两次：memoryless base 与 ours@L\*（L\* 由仿真/离线预选，**在看真机结果之前锁定**）。
- 统计：Clopper–Pearson 精确 CI；成对比较用 McNemar，报不一致对 (n01, n10)；pooled 数用任务层 cluster bootstrap。
- **效力**：12×20 = 240 成对 trial/arm，检测 10 pp 净增益的效力 ≈ 80%。

### P3 的检验方式（对抗 R2-B3）

**不做 trial 级差之差**（方差是单个成对比较的 ~4 倍，需 ~640 成对 trial/方向）。改为**任务级配对符号检验 / Wilcoxon**：每个任务算两个方向的 Δ，检验 `Δ(A→B) > Δ(B→A)` 的符号一致性。n=12 时全同向 p≈0.0005，10/12 p≈0.04。**P3 的效力由任务数而非 trial 数决定** —— 宁可每任务降 trials 也要保任务数 ≥12。

### 其余 arm（exploratory，表中加标记，不进 Abstract）

- 四层 value sweep：**4 个任务 × 15 trials × 4 层 × 2 方向**
- 6 个控制 arm：4 个任务 × 15 trials
- reimplemented Retrieve-then-Steer（同本体）：12 任务 × 15 trials × 2 本体
- reader #3 admission：6 任务 × 15 trials × {base, ours}
- E5 时效性：3 个场景变更 × 15 trials × 3 条线

## 4.3 Baseline 表（含开源可得性与复现成本）

**真机成功率表只保留 4 个条件**（对抗 R2-B11 / R3-B7）：

| 条件 | 角色 | 可得性 | 复现成本 | 是否进真机表 |
|---|---|---|---|---|
| frozen base, no memory | 下界（成对基线） | 自有 | 0 | **是** |
| **ours @ L\*** | 主方法 | 自有 | — | **是** |
| **ours @ ④**（退化对照） | 显示分层的必要性 | 自有 | 0 | **是** |
| **reimplemented Retrieve-then-Steer**（同本体） | 同本体检索 SOTA | **代码未开源**（仅匿名可视化链接）；t_min / 评估间隔 Δ / DTW 剔除阈值 / action horizon H **四个值论文未给** | **≈0 边际成本 —— 其注入器就是我们自己要实现的那一份** | **是** |
| ER / 双体数据 co-train | 上界，且是成本论据的唯一实证支撑 | 自有 | 训练 1–2 天 | **是（仅 4 个任务）** |
| derive-on-read | 表示 vs 缓存的对照（R1-B3） | 自有 | 1 周 | **是（4 个任务）** |
| instruction-only | 记忆 vs prompt 的对照（R1-B4） | 自有 | 3 天 | **是（4 个任务）** |
| Dejavu / RECAP / CLARE / VLA-Pro | — | Dejavu 需 RL 训 EFN；RECAP 需 **paired demonstrations** + Cosmos WAM 骨干；CLARE 无代码；VLA-Pro 有代码但目标问题不同 | 3–4 人月 | **否 —— 只留在 Table I** |

**结构性排除声明（正文原句，比跑一个残废版诚实且省几十机器人小时）**：
> We do not run [RECAP] on our hardware: it requires paired demonstrations on a fixed task distribution, which our independently collected corpus does not provide, and running it under assumptions it does not make would not be informative. [Dejavu]'s experience-feedback network is trained with reinforcement learning per backbone; [CLARE] and [VLA-Pro] address continual task acquisition rather than reader swap. We position all four in Table I instead.

**Retrieve-then-Steer 的保真度门槛（必须先做）**：在 π0.5 + LIBERO-10 上复现 92.4 → 94.4（其报 std 0.2–0.8）。落在噪声内才允许用作对照；否则全文降级为 `our reimplementation (four hyperparameters unspecified in the original; set to X, sensitivity in the supplement)`，且**不做"我们优于它"的主张**。
**一句有力的受控对比论据（必须写进正文）**：
> The same-body retrieval baseline shares our injection implementation and differs only in key construction and value level, so the comparison isolates what is stored.

### 数据切分与泄漏审计（对抗 R2-B5）

- 存量语料三分，**按场景与物体实例互斥**（不是按 episode 随机切）：`base-finetune split` / `store split` / `eval split`。
- **E0**：`base-finetune split` 的任务集与记忆评测任务集不相交，且基座**只用本体自己的数据**微调（无跨本体 co-train，否则 reader 已通过权重读过 writer 的数据）。
- 对齐图：`T_align ∩ T_eval = ∅`，主表只报 held-out 数字。
- §IV 报一行审计：eval episode 与 store 条目的最近邻 key 相似度分布，以及与 base-finetune split 的重合度。

## 4.4 消融清单（Table IV，6 个控制 arm + 共享池三条件）

**控制 arm（缺 random-entry 与 self-prior 这两条，效果可被"注入本身在缩小采样方差"解释掉 —— R2-B9）**：

| # | arm | 排除的替代解释 |
|---|---|---|
| A1 | **random-entry**：从库里随机取条目走同一注入通路 | 增益来自注入本身而非记忆内容 |
| A2 | **self-prior**：用基座自己多次采样的均值 chunk 当 `a_elite`，同一 t0 | 纯方差缩减（注意 t0 实际工作区 ≈0.6，仍保留约 60% 噪声，此解释很有竞争力） |
| A3 | **fixed-t0, no confidence gate** | 分离"门控退回基座"的贡献 |
| A4 | **wrong-body / wrong-task 条目** | 负控制 |
| A5 | **Replay-Only（跨体）**：检索条目 retarget 后开环执行 | 对齐 RECAP 的 Retrieval Only（RoboTwin unseen 26.0 vs 31.5）与 Dejavu 的 kNN-RAG（一手核实：其 kNN-RAG "often degrades performance"）。**不做会被点名。** |
| A6 | **retarget-feasibility oracle**：真值物体位姿做 retarget 后单测运动学可行率 | 把 ③ 层失败里属于 IK/标定的部分剥出来 |

**crossover arm（去注入通路共线，仅仿真/4 任务，R2-B4）**：
- X1：② 内容解码后走 Eq.(6)（已是默认，作为参照）
- X2：③ 内容文本化后走 condition-side prompt 注入
→ 用于估计注入通路主效应并从 P1 曲线中扣除。**若两个 crossover 做不到，P1 措辞必须降级为"层级+通路的联合配置"。**

**共享池三条件（P4，对抗 R2-B15）**：
1. `own-body-only pool`
2. `shared pool, tag-blind retrieval` ← **P4 只在此条件上定义**
3. `shared pool, tag-aware retrieval`（读出时才用 tag 决定回退层级）
**条目按本体配平**：下采样到 min。理由必须写进 §IV：写入门控 recall ≈0.678 且两体基座成功率不同 → 自然写入率必然不等，是 P3/P4 的隐藏系统性偏差。

## 4.5 P1–P4 的检验方式与双向预期结论

| | 预测 | 检验方式 | 若成立 → 论文形态 | 若被推翻 → 论文形态（**必须现在写好**） |
|---|---|---|---|---|
| **P1** | cross-body SR 随抽象度上升；same-body SR 由内容保真度而非抽象度主导 | 两个离散对比：`SR_cross(①) − SR_cross(④) > 0`（pooled，任务层 cluster bootstrap CI）；`SR_same(oracle ①) ≈ or > SR_same(④)` | Fig. 4 两条曲线 + 内部工作点；Title 用 T1 | 若 cross-body 也随抽象度下降 → 结论变成"抽象不买单，跨本体损失全在 key/retarget"，与 P2 合并成一篇更聚焦的归因论文；Fig. 4 改为单调下降 + Fig. 5 承重 |
| **P2** | 跨本体损失由 retrieval + retargeting 两项主导，而非 value 不可执行 | **oracle 阶梯**（下方） | Fig. 5 三桶加和；C4 成立 | 若 value 项主导 → 结论变成"检索可救、动作不可救"，直接支撑 ③ 层作为唯一可行层，论文重心移到 retarget 与分层回退 |
| **P3** | 方向不对称，**归因于 viewpoint variability 而非 workspace inclusion** | 任务级配对符号检验（n=12）；**关键对照：移动臂锁底盘再跑一次，不对称性若消失则机理坐实** | §V-D 一段 + 一个符号检验 p 值 | 若无不对称 → 报 "no directional asymmetry detected at this power"，并给出效力说明；这不伤主线 |
| **P4** | 共享池仅在 value 层级 ≥② 时净正；③–④ 层共享产生负迁移 | 三条件 × 层级的 2×3 表（Table IV） | §V-E 两行 | 若全层净正 → 更好的结果（共享无代价），改写为"我们没有观测到跨体串扰，在此规模下" |

**oracle 阶梯（P2 的非循环分解，五级四差，全部可自动化 —— 对抗 R2-B10）**：
```
base (no memory)
  ↓ Δ_total
cross-retrieved (normal cross-body retrieval)
  ↓ Δ_key        ← 差 = key 侧损失
retrieval-oracle (force the correct writer entry for this task & phase)
  ↓ Δ_retarget   ← 差 = retarget/标定损失
retarget-oracle  (ground-truth object pose & task frame)
  ↓ Δ_value      ← 差 = value 侧跨体不可用
same-body-value  (the reader's own entry for the same situation)
```
- 正例定义来自**我们自己的 (task, phase) 标注**（片段边界天然给出 phase），不做事后人工归因。
- 物体检测器在两个本体相机上的精度作为**协变量**报出（②③ 共享前端，必须暴露）。

## 4.6 指标定义式（§IV 的 "Reporting protocol" 段，约 4 行，全表执行）

```
success rate            SR with Clopper-Pearson 95% CI
paired improvement      Delta = SR(ours) - SR(base) at matched (init state, sampler seed);
                        McNemar with discordant pairs (n01, n10) reported
injection rate          IR = fraction of trials in which a prior was actually injected
                        (also reported per control step)
abstain rate            AR = 1 - IR, split into empty-retrieval / gate / IK-infeasible
memory-harm rate        HR = n10 / n, i.e. paired trials where base succeeds and ours fails
transfer rate           TR = SR_cross / SR_same   (context only; no claim rests on it)
```
**两条硬规则写进 §IV**：
1. 每个报出成功率的格子**必须并列 IR**。任何 arm 若 `IR < 20%`，其 transfer 数字在表里**灰掉并标 n.i.（not interpretable）**。
2. 每个 value 层级**同时报两列**：`gated`（门控开，系统读数）与 `forced`（关掉相似度门与 DTW 过滤，强制注入 top-1，记忆内容读数）。**P1 的主张建在 forced 列上；系统级增益的主张建在 gated 列上。** 这个改动零硬件成本，把 R2-B1 从致命降为可辩护。
3. 有害率**同时报 gated 与 forced 两个版本**（gated 版可被门控刷低，forced 版才是记忆内容的有害性）。

## 4.7 机器人小时预算算式（进 §IV 正文，约 2 行 + 附录表）

```
robot-hours = sum over arms of  (#tasks x #trials x #rollouts-per-trial x minutes) / 60 x failure-factor(1.4)
```

| arm | 任务 | trials | rollouts/trial | 分钟 | 小时（含 1.4×） |
|---|---|---|---|---|---|
| 主端点（2 方向 × {base, ours}，成对） | 12 | 20 | 2 | 1.5 | **33.6** |
| 四层 sweep（exploratory） | 4 | 15 | 4 层 × 2 方向 | 1.5 | **16.8** |
| 6 个控制 arm | 4 | 15 | 6 | 1.5 | **12.6** |
| R-t-S 复现（同本体 ×2） | 12 | 15 | 2 | 1.5 | **12.6** |
| reader #3 admission | 6 | 15 | 2 | 1.5 | **6.3** |
| E5 时效性 | 3 场景 | 15 | 3 | 2.0 | **6.3** |
| ER / co-train 上界 | 4 | 15 | 2 | 1.5 | **4.2** |
| **评测小计** | | | | | **≈ 92** |
| 弱配对数据采集（D12） | 10 | 30 ep | ×2 本体 | — | **40–60** |
| **总计** | | | | | **≈ 135–155 机器人小时** |

**必须写进正文的一句（用工作量透明度换 trials 数）**：
> Cross-body trials require a physical body swap and reset, so their unit cost exceeds that of same-body trials; we therefore report robot-hours alongside trial counts. Total: \todo{} robot-hours over \todo{} weeks on two platforms.

## 4.8 §V 的叙述顺序（2.05 页怎么用）

1. **V-A Reader swap cost**（0.30 页 + Fig. 3）：四种 key × {same-session, cross-session/scene, cross-viewpoint, cross-body} 的分布 + 重标定后的 precision@k / AUC。**caption 必须写死**："γ_sim is re-calibrated per condition; the 0.9992 default of [R-t-S] is a coverage/quality knob tuned on LIBERO-10, not a property of the representation."
   **预写的 fallback 段落（若重标定后跨本体 precision 显著高于 chance）**：结论改为 "the key side is recoverable but requires an alignment map, whose cost we report" —— 这反而直接支撑我们的对齐图，叙事更强。
2. **V-B Transferability spectrum**（0.45 页 + Fig. 4）：四层 × {cross, same} × {oracle content, automatic content}，gated 与 forced 两列；derive-on-read 与 instruction-only 并列。
3. **V-C Where the loss goes**（0.35 页 + Fig. 5）：oracle 阶梯三桶。
4. **V-D Direction**（0.20 页）：P3 符号检验 + 锁底盘对照 + 两个 writer 的条目质量统计（条目数、门控分分布、任务覆盖）。
5. **V-E Sharing, scale, and harm**（0.35 页 + Table IV）：共享池三条件、corpus-seeded 规模下的 precision@k 下降曲线与跨体误检率、harm rate。
6. **V-F The cost of admitting a reader**（0.20 页）：reader #3 的 admission cost 三列实测表（paired episodes / GPU-minutes / wall-clock）vs 同 pair 上的 target 侧微调；E5 时效性交叉点三条线。
7. **主表 Table III 贯穿 V-B/V-D**（0.28 页）。

## 4.9 必须在 §IV 主动交代的四件事（各一句，少任何一句都会在 rebuttal 变成一轮质询）

1. 两个基座策略都在部署前用存量数据微调过，且微调任务集与记忆评测任务集不相交（E0）。
2. `S_deploy` 与 `S_corpus` 的条目数、episode 数与来源。
3. 跨本体 trial 的单位成本（换本体 + 复位）与总机器人小时数。
4. 单 checkpoint、单策略种子；真机做不了 3 seeds，用任务层 bootstrap 代替 seed 方差（主动说明比被问强）。


---

# 5. 页数与工程量对账

## 5.1 6 页硬预算的逐节对账

**基线设计的实测排版估算（Reviewer #3 逐项核算）**：I 1.10 + II (0.57 正文 + 0.62 Table I) + III (1.40 + 0.20 方法图) + IV (0.45 + 0.12 Fig.2) + V 1.75 + VI 0.15 + Refs 1.13（65 条） = **7.49 页**。

**裁剪后 = 6.00 页**（清单见 §0.5）。三处最容易失守，必须专人盯：

| 风险点 | 症状 | 补救 |
|---|---|---|
| **参考文献 40 条** | 按族打包很容易在写作后期失控回到 60 条 | 建一个 `refs_allowlist.txt`，超出必须删一条才能加一条 |
| **Table I 纯符号** | 作者本能想在格子里解释，一解释就回到 0.6 页 | 所有散文只允许出现在 caption 的分号列表，每条 ≤12 词 |
| **§V 2.05 页装 5 个对象** | 图注写长、表格加列 | Table IV 与 Fig. 3 是第一批候选移出物（移到补充材料 + 项目页） |

**超页顺序（若最终仍超）**：
1. Table IV → 补充材料（−0.20）
2. Fig. 3 → 补充材料，正文只留两个数字（−0.16）
3. Algorithm 1 → 压成 6 行（−0.06）
4. **买 1 页付超页费**（7 页，RA-L 允许至 8 页）—— 这比砍实验划算，且 7 页是常见落点。**但必须在 G6 之前决定**，不能临交稿时慌乱。

**绝对不可砍的**：Intro ¶2 与 ¶3（全文唯一的立论承重墙）；§IV 的 Reporting protocol 段（injection rate 规则）；主表 Table III；derive-on-read 与 instruction-only 两个对照（它们是 R1-B3/B4 的解药，砍了等于保留不可识别的主实验、砍掉唯一能救它的对照）。

## 5.2 组件工程量 → 人月 → 与 6.5 个月计划的对账

| 模块 | 人月 |
|---|---|
| 数据/标注管线（D1–D5：分段、物体跟踪、任务坐标系、①②生成） | 2.5 |
| store / 索引 / 生命周期（D7） | 0.25 |
| 四种 key 编码器 + 对齐图（D6） | 0.5 |
| 读出与注入 + retarget/IK（D8，**含 R-t-S 复现**） | 1.5 |
| 写入门控（D9） | 0.5–1.0 |
| 仿真 harness（D10，G3a 通过才做） | 0.75 |
| 真机基础设施（D11：双平台、基座微调、成对 rollout 自动化、复位、日志） | 1.5 |
| 弱配对数据采集（D12） | 0.75 |
| 跑实验 / 分析 / 画图 | 1.5 |
| 写作 | 1.0 |
| **合计（不含额外基线复现）** | **≈ 10.75–11.25 PM** |

**对账**：6.5 个月 × 1 FTE = 6.5 PM → **缺口约 1.7 倍**。
- **≥2 FTE**：执行本大纲的完整版（含仿真 2×2、reader #3、E5、6 个控制 arm）。
- **1.5 FTE**：执行 §5.3 的 MVP。
- **1 FTE**：不要启动本课题的完整形态；改做 §6 G4 的负面结果形态（纯归因研究）。

**三个省工替换（合计省 1.5–2 PM，已计入上表）**：
1. 时间分段用夹爪状态机，不用学习式分段（省 0.5 PM）。
2. 物体 6-DoF 位姿在抓取后用夹爪位姿代理，只在抓取前用检测器（②③ 感知从 3 PM 压到 1.5 PM）。
3. **Retrieve-then-Steer 的复现与我们自己的注入器是同一份代码**（省 1 PM），且这在论文里同时是一个极强的受控对比论据。

## 5.3 最小可发表版本（MVP，1.5 FTE / 3.5 个月）

**保留**：
1. 两台真机、共享单库、双向读写、**E0**（零梯度的唯一证据）。
2. value 谱系降为**三点 ①③④**（砍 ②：它与 ③ 共用感知前端且更贵；④ 免费，作退化对照）。
3. **P1（三点）**，允许无内部工作点 —— 若单调则报"最优点在端点"并同步改 Fig. 4 与 Contribution 2。
4. **P2 归因（oracle 阶梯）** —— 最便宜且最独有的分析，**不可砍**。
5. **P3 方向不对称** —— 跑双向本来就要跑，免费。
6. **per-trial memory-harm rate + injection rate**。
7. **derive-on-read 与 instruction-only 两个对照**（4 个任务）—— **不可砍**。
8. 真机：**8 任务 × 20 成对 trial × 2 方向 × {base, ours}** ≈ 45 机器人小时。

**砍掉**：仿真全部结果（只作内部 gate）；RoboMME 报数；P4 降为一行；ANN 延迟曲线；删除泄漏探针；reader #3（降级为一句 limitation：*"admitting a further reader is not evaluated here"* —— **注意这会把 R1-B5 变回未解决风险，必须在 Limitations 明写**）；E5（降级为 discussion 一句）；除 R-t-S 之外的全部基线复现；Intro 成本段。

**MVP 仍然成立的理由**：论文的不可替代性在"两台都部署的真机 + 换读者无策略梯度 + 同一协议下的谱系测量与损失分解"，不在 sweep 的宽度。


---

# 6. Go/No-Go 检查点

今天 **2026-08-22**，目标投稿 **2027-03-10**（RA-L 滚动）。每个 gate 必须由具体的人在当天交出一个**数**，不接受"还在调"。

| Gate | 日期 | 交付物 | No-Go 判据 → 论文变成什么形态 |
|---|---|---|---|
| **G0** | **2026-08-29** | (a) `PORTMEM`/`XEM` 重名检索结果；(b) VLAC 权重可得性核实；(c) 存量语料的双本体任务重合度审计（有多少任务两台都做过） | (c) 若重合任务 <6 个 → 立刻把 D12 采集扩到 12 任务并推迟 G3；(b) 若 VLAC 不可得 → 写入门控改为遥操隐含标签 + 轻量成功分类器，Intro ¶4(e) 的 why-now 论据同步改写 |
| **G1** | **2026-09-12** | **Fig. 3 两联图（纯离线，无需策略、无需真机 rollout）**：四种 key × 四种条件的分布 + 重标定到同弃权率后的 precision@10 / AUC vs chance | 若四种 key 在重标定后 precision@10 全部 ≤ chance → 主结果改为 language-keyed only，P2 的答案定为"key 侧且不可修复"，对齐图从方法降级为一个失败的 ablation，论文重心全部移到 §V-C 的归因 |
| **G2** | **2026-09-26** | **③ 层 object-anchored 坐标系的跨本体开环重放误差**（各 50 条 episode，先仿真、再真机空跑）：末端轨迹误差 + 接触点命中率 | 误差 >3 cm 或接触点命中 <60% → **P1 立刻降为三点谱系**（①③④ 或 ①②④，取表现好的），同步改 Fig. 1(b)、Fig. 4 与 Contribution 2 措辞。**这是最容易烂尾的一环**，见下 |
| **G3a** | **2026-10-03** | 单模拟器内换第二个机器人模型 + 重跑 demo 生成的可行性（≤1 周验证） | 不可行 → 仿真退出正文，只做 key 侧离线分析，D10 的 0.75 PM 转给真机 |
| **G3b** | **2026-10-17** | 双本体弱配对数据采集完成（10–12 任务 × 30 episode × 2 本体）+ **基座微调数据切分（含 E0 切分）冻结** | 采集完成度 <60% → 放弃对齐图，全面转向 training-free language-key 变体作主结果（论文不死，结论换了）。**注意：基座微调一旦开始，E0 切分不可更改，否则要重训** |
| **G4** | **2026-11-14** | 仿真（或离线代理）上任一 value 层的跨本体成功率显著高于 frozen base（>2 个点，3 seeds）；同时给出 derive-on-read 的读出延迟数 | 无任何层超过 frozen base → **不要启动完整阶段 B**，转为负面结果论文（"Why a robot's action memory does not transfer across bodies"），把省下的时间全给 P2 归因深度。若 derive-on-read 延迟在预算内且成功率持平 → Contribution 2 改写为 protocol/measurement 贡献（措辞已在 §3.4 预写） |
| **G5** | **2026-12-19** | 前 4 个任务的首批跨本体真机数字（含 injection rate） | 跨本体 SR < frozen base，或 IR < 20% → 同 G4 的转向。此时只剩 2.5 个月，**必须当天决定** |
| **G6** | **2027-01-30** | 实验冻结；Fig. 4 由实测数据绘制；决定 6 页还是买 1 页 | Fig. 4 若与 P1 预测不符 → 按 §4.5 的"若被推翻"列同步替换 Title、Abstract、¶5 预注册句、Contribution 2 四处（**它们是绑定的，不可只改一个**） |
| **G7** | **2027-02-28** | 内审完成（含逐条核对 §1.0 写作红线与 Table I 每一格的证据来源） | — |
| — | **2027-03-10** | 投稿 | — |

**最可能烂尾的一环（明确点名）**：**不是 key 对齐**（它有清晰的退化路径：退到语言 key，P1 曲线依然可测，只是工作点右移），而是 **③ 层 object-anchored 任务坐标系在移动本体上的定义与标定**。对移动底盘而言基座锚定坐标系无意义，只能物体锚定，于是它退化为一个 6-DoF 物体位姿估计问题 —— 一个会一直"差不多能用"但永远不够准的问题，而且它同时是 ② 和 ③ 的前端。典型烂尾方式：前 3 个月一直显示"基本 work"，第 5 个月做真机跨本体时才发现误差量级吃掉了全部迁移增益，而那时四点谱系已经写进 Intro 和 Fig. 1。**G2 的开环重放实验是强制早期暴露的手段** —— 它不需要策略、不需要记忆库、不需要完整管线，两周内可做完，且给出一个可判定的 cm 级数字。

**arXiv 占位建议**：**G1 通过后立即**把 P1–P3 的预注册预测挂上 arXiv。抢跑风险源已明确：Dejavu（逐字写出我们的方案）、RECAP（把跨本体检索表示标为 open question）、Retrieve-then-Steer 团队（已有 OpenArm + ALOHA-PiPER 两套双臂真机，硬件上完全具备顺手做跨平台共享的条件）、RoboMME 团队（有基准、代码、leaderboard、π0.5 pipeline，做 v2 的边际成本远低于我们）。


---

# 7. 开写前必须先定的事（带优先级）

**P0 — 本周内（阻塞其他一切）**

1. **VLAC 权重可得性核实**（半天）。**【待确认】** VLAC 论文中作 critic 用的是 8B 规模的 InternVL 版本，PDF 内查不到代码/权重发布声明。若不可得：写入门控改为"遥操数据的隐含成功标签 + 轻量任务级成功分类器"，Intro ¶4(e) 的 why-now 论据从"跨本体 critic 已存在"改为"写入门控只需高 precision 低 recall 的工作点，少量标注即可达"。另需预算：8B critic 对 10⁴ episode 打分，按 0.3 s/次 × 30 评估点/episode ≈ 25 GPU-hours。
2. **`PORTMEM` / `XEM` 重名检索**（半天）。Table I 末行、§II-D、Title、Abstract 四处已按已定名书写；v3 的 CAMEL 已撞车一次。
3. **母句的最终措辞落锤**（§1.2 那句），并在一个文件里写死，Title / Abstract / ¶2 / C1 / Fig.1 caption 五处派生。
4. **E0 的数据切分方案落锤**（哪些任务进 `base-finetune`、哪些进 `T_eval`、哪些进 `T_align`）。**基座微调一旦开始就不可改**。
5. **启动 D12 弱配对数据采集**（10–12 任务 × 30 episode × 2 本体），与仿真验证并行。这是唯一"不做完后面全部实验都不能开始"的数据依赖，且在基线计划里一次都没出现过。

**P1 — 两周内**

6. **是否在 RoboMME 上报数 → 决定：不报数。** 理由：其仿真与真机都只有一台 Franka Panda，无法承载核心实验；移植成跨本体版需重跑 ManiSkill planner，且 Imitation/Video 任务的"演示阶段"本身就是那台 Franka 的运动，换本体后演示与执行本体不一致会改变任务语义。**只沿用其表示轴/注入轴的术语并引用其 §6 "leaving mobile manipulation and ... memory-bank methods ... for future study"。** 这条决定 II-A 的最后一句与 II-D 的第 3 句。
7. **主打新颖性排序 → 决定：multi-reader / bidirectional 共享库为主，"换读者无策略梯度"为代价论据。** RECAP 的 pool 从不部署，双向读写是它结构上没有的设置。此决定改变 Title、Abstract 首句与 Contribution 排序（已按此写）。
8. **"零梯度"口径 → 决定：全文写 "no gradient reaches either policy once deployed"，并在 ¶4 主动交代基座微调 + E0。** 同时**必跑** training-free language-keyed 变体作为诚实地板（成本近零，是唯一不受对齐图泄漏影响的 arm）。
9. **真机 trials 数 → 决定：主端点 12 任务 × 20 成对 trial。** 对照：Retrieve-then-Steer 真机 50 trials/任务、RECAP 10 trials/任务、VLA-Pro 20 trials/任务。我们用工作量透明度（机器人小时表）换 trials 数的不足。
10. **Retrieve-then-Steer 的可比性 → 决定：先做 LIBERO-10 + π0.5 的保真度复现门槛**（92.4→94.4，其 std 0.2–0.8）。未通过则全文改称 reimplementation 且不做"优于"主张，四个未公开值（t_min / 评估间隔 Δ / DTW 剔除阈值 / action horizon H）在附录给敏感性扫描。

**P2 — 一个月内**

11. **Miras / Titans 的理论 framing → 决定：全砍。** 理由：(a) 6 页里 0.25 页 ≈ 一张实验图，而这段不做任何主张；(b) v3 已在 Miras 上栽过一次（把它读成"预言了外部记忆空白"），任何多余的 Miras 表述都是纯增的攻击面；(c) 按 Miras 四轴，我们、Retrieve-then-Steer、RECAP、Dejavu 会落在同一格，做不了定位工作。若坚持保留，压到 1 句放 §III 第一段。
12. **RT-X / OpenVLA 一族是否给 Table I 一行 → 决定：不给**（共训产生权重而非记忆对象，有原则的排除，正文写明一句）。若改主意，**必须先读一手 PDF**，不得引用任何未核对的数字/venue。**【待确认：本组尚未读过这一族任何一手 PDF】**
13. **Behavior Retrieval (2304.08742) / STRAP (2412.15182) → 决定：Table I 整行删除**，正文一句话划走（"检索的是训练数据，取回后仍要跑梯度"）。若要保留该行，必须先读全文补齐 4 个 `?`。**不得靠推测填格。**
14. **RA-VLA (ICML'26) → 决定：从参考文献删除**，除非拿到一手 PDF。不能凭 OpenReview 条目描述引用。
15. **VINN 的 venue 核实**（arXiv comment 无 venue 字段）。引用时暂标 arXiv。
16. **LaTeX 模板**：`RAL2027/paper_src/` 现为 ICRA 的 `ieeeconf` 模板，投 RA-L 需换 `IEEEtran` 期刊格式。换完立刻用真实字数做一次排版对账，验证 §0.5 的 6.00 页估算。
17. **openpi 源码中确认 π0/π0.5 action expert 的注意力掩码与前缀 KV 结构**（关系到注入点实现与 D8 的工期）。

**P3 — 写作期**

18. Fig. 1 的两张真机实拍（含房间背景差异）—— G3b 之前补拍。
19. Fig. 1(b) 的四层内容必须从我们自己的库导出真实样例，不要手编。
20. Table I 每一个非平凡格子在 caption 或脚注给出证据来源（页码）。**任何一格被作者本人认为不实，整节可信度归零。**
21. 所有 venue 逐条经 arXiv API / 一手 PDF 复核；无已发表 venue 的（Retrieve-then-Steer、RECAP、VLA-Pro、Dejavu、RoboMME）**只能标 arXiv preprint**。v3 的 venue 错误密集（SOP 基座、RA-VLA 会议、MemoryVLA++ 时间线、Episodic Memory Banks 查无此文），复发一次就会让审稿人不信任整份书目 —— 而本文的说服力**完全**建立在书目精确度上。

---

## 附：本大纲相对 v4 的主要修订清单（供追溯）

| v4 的写法 | 本大纲的写法 | 依据 |
|---|---|---|
| "所有能持久的机器人记忆，都只有写它的那个本体能读" | 加三限定词：executable action content / written during its own deployment / no further policy update | RECAP、RAM、RoboOS 三个反例（threat_RAM_RoboOS.md + 一手 PDF） |
| γ_sim=0.9992 构成 mechanical veto | 放弃该论证，改为阈值无关的检索质量与重标定代价 | Retrieve-then-Steer 表 8：0.9988–0.9998 全程 93.5–94.4，最松阈值仍高于无记忆基座 |
| P1：迁移率上升、同本体精度下降、有交叉点 | P1：cross-body 随抽象度上升；same-body 由内容保真度主导 | RoboMME：GroundSG+Oracle 84.08 > FrameSamp+Modul 44.51 |
| ①② condition-side、③ retarget→Eq.6、④ Eq.6 | **四层统一解码到读者动作空间，共用 Eq.(6)** | 去除层级 × 注入通路共线；并使 "adopted unchanged" 成为真陈述 |
| "零策略梯度" | "no gradient reaches either policy **once deployed**" + E0 + reader #3 admission cost | v4 阶段 B 自带双本体基座微调 |
| 记忆库 = 存量语料灌到 10⁴–10⁵ 条 | 拆 `S_deploy`（主结果）/ `S_corpus`（仅规模与串扰） | "部署中自写"与"语料灌库"互斥 |
| 检索延迟-规模曲线为第二贡献 | **删除**（10⁵ 条暴力扫描亚毫秒）；改为对 in-context 的一句话对比 | 必然"无事发生"的实验 |
| 条目删除后的残留泄漏检验 | **删除**（对显式条目表平凡为真） | 空实验 |
| 8 类基线必须齐全 | 真机 4 条件 + 结构性排除声明 | 3–4 人月复现不可交付；跑残废版是拒稿理由 |
| 8–10 任务 × 15 trials | 12 任务 × 20 成对 trial（同 init + 同噪声种子） | P3 的效力由任务数决定；15 trials 低于同族标准 |
| P2：检索错 vs 动作不可用（二分） | oracle 阶梯五级四差（key / retarget / value 三桶） | 二分法循环论证且漏掉 retarget 桶 |
| 记忆有害率 | 有害率 + **injection rate** + forced-injection 列 + `IR<20%` 标 n.i. | TR 与有害率都能被"多弃权"刷好看 |
| ① 层用 grounded 语言（带像素坐标） | ① 层用**可重新 grounding** 的语言（物体名 + 关系，无写入者像素坐标） | 像素坐标是写入者相机系的量，与 body-agnostic 直接冲突 |
| 沿用 RoboMME 的 when/where/what/how 四维分类 | 只沿用其表示轴与注入轴术语；四维仅作 Intro 一句修辞 | 我们的任务在其意义上基本是马尔可夫的，硬对齐是修辞 |
| entry 粒度未定义 | **片段级**（夹爪状态机 + 速度过零），双单位报数 | 粒度不定则规模主张与存储成本论证都不成立 |
| 成本论据 O(T·B) → O(1) | **删除**，改为三列实测代价表 + **时效性论据** + E5 实验 | O(1) 无依据；且回答不了"为什么不共训" |

