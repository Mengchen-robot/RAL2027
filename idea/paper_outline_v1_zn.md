# 跨本体持久动作记忆 — IEEE RA-L 最终写作大纲 v1.1（施工图）

生成日期：2026-08-22 · **最后更新：2026-08-24（按 v5 §9 补丁清单 + 硬件答复 + demo 规划）**
上游依据：**`vla_memory_cl_feasibility_v5.md`（现行规格书，优先级高于 v4）**、`vla_memory_cl_feasibility_v4.md`、`review_v3_critique.md`、`threat_RAM_RoboOS.md`、三位审稿人对四节大纲的对抗意见、以及 RoboMME / Retrieve-then-Steer / RECAP / Dejavu 四篇一手 PDF 精读记录、`RAL2027/kinematics/` 的一手运动学复算。

**本文档的用法**：这是施工图，不是 idea 描述。每一节的每一条要么是可执行的写作/实验指令，要么是可验证的断言。凡标 **【待确认】** 的，写进论文前必须有一手证据。

> ## ⚠️ 2026-08-24 硬件变更：本体已从 FR3 + 移动臂 改为 双臂 Piper ↔ 双臂 PiperX
>
> 全文凡出现 `Franka FR3` / `移动臂` / `mobile manipulator` / `锁底盘` 的地方均已作废或改写。**若下文某处仍残留旧本体名，以 v5 为准。**
>
> **已确认的硬件事实**（v5 §1.6，用户 2026-08-24 答复）：
> - ✅ PiperX 是**官方 `piper_x`**（偏置腕 UR 型）→ "different kinematic family" 可写，谱系不会反转成压平
> - ✅ **无腕部力/触觉通道**，但**拉链任务已训练成功、数据可用** → 拉链**保留**在 confirmatory（③层用抓后夹爪位姿代理＝本体感觉，成功判据在释放回 home 后的静止帧上测，两处都绕开了触觉文献里的遮挡机理）
> - ⚠️ **两台夹爪不同款** → **§4.7 之前所有可行率数字必须用实测 TCP 偏置重算**；同时这使 embodiment 阶梯的"换夹爪"档变成免费且原生
> - ⚠️ **铰链未做标定**，目前直接用采集动作训练 → 需确认家电采集期间是否移动过；未移动则可**追溯标定**（存量数据零重采变③层可用）
> - ✅ HuggingFace 可达（VLAC 路径确认）；✅ JAX 在 5090 推理可跑（训练待实测）
> - ✅ 数据可用性已由专职采集团队验证，**不再是风险项**


---

# 0. 一页速览

## 0.1 标题推荐

| # | 候选 | 评价 |
|---|---|---|
| **T1（推荐）** | **谁的记忆能够被读取？冻结 VLA policy 的持久动作记忆的跨本体可读性（Whose Memory Can Be Read? Cross-Body Readability of Persistent Action Memory for Frozen VLA Policies）** | 问句式把“谁能读”这条新轴放进标题；“cross-body”避开 RECAP 已占用的 cross-embodiment 术语；“persistent action memory”含两个关键限定词（persistent / action） |
| T2 | 读取另一台机器人的记忆：一个持久动作存储必须包含什么才能在脱离其身体后仍然可用（Reading Another Robot's Memory: What a Persistent Action Store Must Contain to Outlive Its Body） | 叙事性强，但“outlive its body”是修辞，RA-L 审稿人可能嫌软 |
| T3（保守） | 面向两种已部署操作机器人的共享持久动作记忆（A Shared Persistent Action Memory for Two Deployed Manipulators） | 最不可攻击，但也最不吸引人；作为 rebuttal 后改名的退路 |

**决策规则**：若 §4 的 P1 主结果为正（谱系存在且有内部工作点），用 T1；若主结果为负（跨本体读取整体不可行），改用“为什么机器人的动作记忆无法跨身体迁移：一项分层测量（Why a Robot's Action Memory Does Not Transfer Across Bodies: A Layered Measurement）”，全文转为负面结果论文（见 §6 G4/G5）。

**方法名**：`PORTMEM` — **【待确认】重名检索尚未执行**（v3 的 CAMEL 已撞车一次）。检索完成前，正文一律用占位符 `\sysname`，用 LaTeX 宏定义，改名成本为零。名字**不进标题**（标题不依赖名字，是防守性设计）。

## 0.2 摘要中文译稿（对应英文约 195 词，含全部限定词）

> 一个在部署过程中持续改进的机器人，必须把它学到的内容存放在某处。检索增强的冻结 vision-language-action (VLA) policies 已经能够在不进行梯度更新的情况下累积部署经验，跨本体检索池也已经存在。但尚未被展示的是这样一种持久存储：其中包含由机器人在其**自身部署过程中**写入的*可执行动作内容*，并且能够被**第二个同样处于部署中的、属于不同运动学族的机器人**读取，而其 policy **不再进行任何进一步更新**。我们追问：要实现这一点，一条经验必须包含什么内容。每条经验以四个抽象层级写入——可重新 grounding 的语言摘要、以对象为中心的子目标序列、**锚点系下的接触点运动并显式拆出 (T_abs, T_rel)**，以及关节空间动作 chunk——这些内容存储在一个带有学习得到对齐映射的、与身体无关的 key 之下；并且每一层都会在注入到读者的冻结 flow-matching sampler 之前，被解码到读者自身的动作空间中。**两个已部署的双臂平台——球形手腕的 Piper 与偏置手腕的 PiperX，DoF、负载、重复精度全同，臂展相差 6.9%——对同一个存储进行双向写入与读取。** 我们报告四个层级上的可迁移性谱系，将跨本体损失分解为 **key 侧、限位包络、架构与 value 侧四部分**，并报告每次试验的 memory-harm rate 与使这些数字具有可解释性的 injection rate。接纳第三个此前未见过的 reader 的代价为 \todo{N} 个配对 episodes 和 \todo{M} GPU-minutes，且不需要任何 policy gradient。

**Abstract 写作红线**：
- 不得出现 first / novel / unexplored / we fill the gap。
- 必须出现的**四个**限定词：*executable action content*、*during its own deployment*、*no further update to its policy*、***of a different kinematic family***。少一个，Table I 里的 RoboOS 或 RAM 或 RECAP 或 R-t-S 就是反例。
  - **第四个限定词的写法取决于 v5 §1.6 #1**：已确认为官方 `piper_x`（偏置腕）→ 用 `of a different kinematic family`。
- 必须出现 injection rate —— 这是主动交出“transfer rate 可被弃权刷高”这一击（Reviewer #2 R2-B1）。

## 0.3 故事线（3 句话）

1. 检索增强的冻结 VLA 已经跑通，跨本体检索池也已经存在（RECAP：人手/UR5 写、机器人读；RAM：660 条离线 affordance 库被两种本体读）——**而且冻结 π0.5 + 持久成功记忆已经被证明能在双臂 AgileX PiPER 上帮助叠 T 恤（R-t-S 附录 D，42.0→50.0，每任务 50 trials）**——这些都不是我们要论证的东西。
2. 但没有一个**由部署中的机器人自己写下的、含可执行动作内容的持久库**被第二具**同样在部署中的、属于不同运动学族的**机器人**不经任何策略梯度**读过：换读者要么付一次 target 侧微调（RECAP 摘要自陈），要么条目本身就是权重（CLARE / VLA-Pro），要么跨过身体的根本不是动作（RoboOS 自陈其 shared memory 无动作内容），要么读者就是写者本人（R-t-S / Dejavu）。
3. 我们把每条经验同时写在四个抽象层级上、用一张一次性训练的对齐图索引、在读出时一律解码回读者自己的动作空间，然后在两台**都在部署中**的双臂机器人（球腕 Piper 与偏置腕 PiperX）之间双向读写同一个库，测出**两条曲线在哪一层交叉**、以及跨本体损失中有多少来自检索、多少来自限位包络、多少来自架构、多少来自动作本身不可用；**并给出一个纯离线的运动学统计量，它能预测迁移不对称的方向与逐任务排序。**


## 0.4 四条贡献（中文译稿）

> **1) 我们以无阈值的方式量化 reader 置换对检索记忆造成的代价。**
> 我们在四种 key 构造下测量同本体查询与跨本体查询的检索质量，基于我们自己的 (task, phase) 标注导出的正样本对定义，报告 precision@k 和 ROC-AUC，并进一步报告跨本体 reader 为达到与同本体 reader 相同精度所必须付出的 recall 代价（等价地，也就是 abstention 代价）。我们有意避免基于任何单一系统的默认相似度 gate 来论证：最先进同本体 retriever 的 gate 值是每次部署中的权衡旋钮，而不是表征本身的性质，并且其自身的敏感性研究表明，该方法在这一取值范围上几乎是平坦的。

> **2) 我们使一条经验的可迁移性成为一个可以通过实验分离的变量，并把主张收窄到交叉点。**
> 一次收集在共享 key 之下为每个条目生成四个 value 层级，并且关键在于，它们共享同一个 readout 接口：每一层都被解码到 reader 的动作空间，并在同一个冻结 sampler 的同一位置注入，因此在保持注入路径固定的同时，只改变抽象层级。**我们报告的不是"一条谱系"，而是一个交叉点：同本体保真度与跨本体可迁移性发生权衡的那一层。** 我们对每一层同时报告 oracle 内容与自动生成内容，从而将表征本身的代价与内容生成器的代价区分开来；同时，我们还与一种 derive-on-read 存储进行比较，该存储只物化最低层级，并在读取时重建其余层级。
> **为什么必须收窄到交叉点**：单调"越抽象越可迁移"不是 finding——GR00T N1.7 的 README 已用自己的话主张过（relative EEF action space 是 "a key factor in the model's cross-embodiment performance"）。**没有哪一层永远最好，这才是"谱系"而不是"层级排序"。**

> **3) 我们报告了一个由两个已部署本体共享、双向写入和读取的持久动作存储，并且一旦部署完成，就没有梯度会到达任何一个 policy。**
> 每个本体的基础 policy 都只在部署前 fine-tuned 一次，所用任务与记忆评估任务互不相交；当存储被接入时，或当它持续增长时，都不会进行任何更新。我们进一步接纳第三个此前未见过的 reader 本体（**单臂模式读者：动作维度 14→7，`T_rel` 字面消失**），并以配对 episodes 和 GPU-minutes 报告其接入成本，同时给出在同一对本体上进行按本体 target-side fine-tune 的成本。我们报告每次试验的 memory-harm rate——即在初始状态匹配且 sampler 噪声匹配的配对试验中，存储使 reader 的表现劣于其无记忆基础版本的比例——以及对其进行条件化解释的 injection rate。

> **4) 我们分解跨本体损失并刻画一个共享存储。**
> 一个 oracle 阶梯将同本体 reader 与跨本体 reader 之间的差距归因到**四个可加项——检索、限位包络、几何/架构，以及 value 不可执行性**——而无需对失败进行事后人工标注。**（离线实测：限位项 19.2 pt，几何项 0.0 pt——两者机理不同，不得合并叙述。）** **预注册的负值处理**：若任一 Δ < 0，禁止画堆叠柱状图，改画阶梯折线并在正文声明"这是一串干预，不是方差分解"。在一个由语料预填充、跨任务与跨本体共享、包含 \todo{10⁴–N_max}（**明写 N_max，不硬凑 10⁵**）个条目（\todo{N} episodes）的存储上，我们表明真正的约束项是检索精度与跨本体干扰，而不是容量。

> **我们明确不主张**：向 flow-matching sampler 注入中间状态、置信度自适应的 guidance 强度、低置信度时 abstain-on-low-confidence 的回退机制，或对检索到的 chunks 进行 component-aware aggregation——这些都采纳自 Retrieve-then-Steer [R-t-S]，并且一旦某个 entry 被解码到 reader 的动作空间后即不加修改地使用。**我们同时指出，带软逐元素掩码的中间态注入在 GR00T N1.7 的 real-time chunking 中也有工业实现（`vel_strength` + 指数 ramp），这进一步支持"注入机制不是本文贡献"这一立场。** 我们也不主张 retrieval pool 的无梯度增长，这一点已由 RECAP 证明；也不主张 entry-level 的可撤销性，这一点已由 CLARE 证明。
> **但我们确实主张一项额外的机制增量**：**双臂条目在聚合之前的坐标变换**——先把每条候选从 (left, right) 转到 (T_abs, T_rel)，对 `T_rel` 用更紧权重或最近邻回退、对 `T_abs` 自由聚合，再映回。**其正当理由只能建立在 IK 可行性上，不能建立在约束破坏上**（实测逐臂独立 retarget 的 `T_rel` 保持误差中位仅 0.6 mm / 0.0°，可忽略）。


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
- **我们的处理**：**放弃"机制性否决"这条论证路线。** Fig. 3 改为与阈值无关的检索质量图（precision@k / AUC + 重标定后的工作点），Contribution 1 改为“量化 reader swap 的重标定代价”。caption 里主动写明：“γ_sim is re-calibrated per condition; the 0.9992 default of [R-t-S] is tuned on LIBERO-10 and is a coverage/quality knob, not a property of the representation.”
- **残余风险**：若重标定后跨本体 precision@10 仍显著高于 chance，则“key 侧是瓶颈”（P2）会被削弱，论文重心必须转到 value 侧与 retarget 侧。**这是 G1 gate 的判定内容（§6）。**

### 风险 B：**"zero policy-side gradient" 在我们自己的实验计划里就不成立**（Reviewer #3·R3-B1 + Reviewer #2·R1-B5）

- **事实**：v4 阶段 B 第一句是“双本体基座微调（数百小时存量数据）”。每引入一个读者本体仍要跑一次策略级梯度——这正是 RECAP 的成本。且 n=2 时两个本体的数据**都**用来训对齐图，“admitting a new reader”这个动作在整个计划里**从未被执行过一次**，分界线不可证伪。
- **后果若不改**：Contribution 3、Table I 末行、Fig. 1(a) 的 “no policy update” 徽章同时失效，贡献被压成常数因子之争 → RA-L 拒稿理由。
- **我们的处理（两条同时做，缺一不可）**：
  1. **实验 E0**：在读者本体的基座微调数据切分中**剔除全部记忆评测任务**，训练完成后冻结，再去读取写者写下的这些任务条目。全文措辞统一为 “the reader's base policy is fine-tuned once, before deployment, on tasks disjoint from the memory-evaluation tasks, and is never touched again”。
  2. **实验 E1（reader #3）**：**单臂模式读者**——把一条臂单独作为读者。动作维度 14→7，`T_rel` 字面消失，③/④ 双臂条目结构性不可读，①② 仍可指导顺序策略。**AgileX 单臂 Piper 是独立在售 SKU，零新硬件。** 报告 “admitting reader #3” 的实测代价（配对 episode 数 + 对齐图 GPU-分钟），并与在同一 body pair 上进行 RECAP 式 target 侧微调的代价并排比较。
  3. 全文**删除** O(T·B) → O(1) 的复杂度论据，改为一张三列实测代价表。
- **残余风险**：单臂模式是同一台机器的一种配置，审稿人可能会说这不算新本体。**但它通过全部五条判准**（下表），这是关键区别：**受损读者在自己写的条目上的成功率必须仍然接近未受损时，且必须与跨本体数字并排报出**。我们在正文中用 “a single-arm configuration, an in-catalogue SKU, unseen by the alignment map” 描述它，并明确说明这是 admission cost 的下界估计。

**★ embodiment 阶梯的五条判准（必须写进补充材料，并对每一档逐条打分）** —— 用于防御"人为制造困难"这一刀：

| # | 判准 | 说明 |
|---|---|---|
| 1 | **Catalog test** | 该构型是否作为产品在售，或属于常规维护后的自然状态 |
| 2 | **★ Own-task competence test（唯一可一票否决）** | 受损读者在**自己写的条目**上的成功率必须仍然接近未受损时，**且必须与跨本体数字并排报出**。若同比例下降，你造的是一台更差的机器，不是另一台机器 |
| 3 | **Rule-not-choice test** | 修改必须由**预注册的规则**决定，而非由"哪个关节最能打破 SE(3)"决定 |
| 4 | **Symmetry test** | 同一修改双向施加 |
| 5 | **Predictability test** | 若逐任务结果可解析预测则不做（**可预测的实验不携带信息**） |

> **按判准 3 与 5，"锁关节"档当前不合格**（锁定角被硬编码为零位＝人为最劣化配置，且 j6 是在算出"6→5 DoF"之后才选中的，属后验选择）。锁关节降为 plan B，且必须做**锁定角 sweep**（取写者轨迹中位角 + 5 点扫描）。
> **一个免费且原生的新档**：v5 §1.6 #6 确认**两台夹爪不同款**——接触几何差异是真实产品差异，通过全部五条判准，比 3D 打印手指自然得多。


### 风险 C：**P1 的抽象轴与注入通路、与内容生成器质量二重共线**（Reviewer #2·R1-B2 + Reviewer #2 R2-B4）

- **事实**：RoboMME 实测同一份 memory content 仅更换注入机制，SR 30.68（FrameSamp+Context）→ 44.51（FrameSamp+Modul），相差 14 个点；同一层级仅更换写入内容的 VLM，GroundSG+Oracle 84.08±1.86 vs GroundSG+QwenVL 32.70±0.61，相差 51 个点。而基线设计里 ①② 走 condition-side 注入、③ 走 retarget→Eq.(6)、④ 直接 Eq.(6)。
- **后果若不改**：Fig. 4（money figure）的任何形状都无法归因于 abstraction，主实验无效。
- **我们的处理（一个修复解决两个 blocking issue）**：
  1. **统一注入通路**：所有层级在读出时一律解码到 reader 动作空间中的 H×D prior，四层共用 Eq.(6)。副作用：`adopted unchanged from Retrieve-then-Steer` 从不实陈述变成真陈述（解决 R1-B7）。解码器（①②→子目标→EE 轨迹→retarget；③→retarget）明确声明为本文贡献。
  2. **每层报两次**：oracle content 与 automatic content。Fig. 4 绘制 oracle 版（表示层的干净读数）与 automatic 版（系统实际值）两组曲线，两者之差即生成器代价。
  3. **删除 P1 后半句**：“same-body precision falls monotonically with abstraction” 与现有最佳证据相反。改为 “same-body precision is governed by content fidelity rather than by abstraction level”。
- **残余风险**：统一通路可能导致 ①② 层因两次有损解码而整体崩掉，谱系塌缩成两点。**由 G2 gate 判定（§6）**；若崩，则将 P1 降级为三点谱系，并同步改写 Fig. 4 与 Contribution 2。

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
| R1-B9 | P3 机理（工作空间子集）运动学上错 + 写入端污染 | **机理换成限位包络覆盖率**（旧机理已被体素 IoU=0.528 证伪，两者互不包含）；对照换成**工作空间交集核对照**；写入端配平 | §4.5 P3′ |
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
| **R4-B1** | **层③失败被误归因于"不同运动学族"** —— 把 PiperX 限位放宽到 ±189° 后可行率 **80.8% → 100.0%**，架构贡献 **0.0%**。审稿人 20 行代码可证伪 | **归因拆两项**：层④←架构（标定后仍 7.10 cm / 17.8°）、层③←限位包络（Piper j5 ±70° 是全臂最紧关节）。**两者不得合并叙述** | §4.5 P5 / §4.8 V-C |
| **R4-B2** | **层④只报朴素复制（82.8°）是稻草人** —— 审稿人第一句就是"你标定了吗"，5 分钟工作量、落差 80% | **必须自己先报三档标定值**（朴素 82.8° / 逐关节仿射 52.4° / 全线性 42 参数 **17.8°**）+ **A7 消融**（④+腕部重解算 → 6.7°） | §4.4 A7 / §4.5 P5 |
| **R4-B3** | **"+10 pt 双臂协同增益"是搜索预算伪影** —— 协同侧拿到 40×3=120 次 IK 尝试，是独立侧的 15 倍，且额外获准把整个任务挪 ±10 cm/±20° | equal-budget 重跑（同预算同 float、N≥400、报 Wilson 区间）。**若增益 <5 pt 或落在 CI 内 → 删掉这条 Contribution**，换成纯定性的 R-t-S 聚合缺陷 | §0.4 C-额外 / §4.4 |
| **R4-B4** | **两台夹爪不同款**，而全部 φ 数字建在"同款夹爪、仅安装 rpy 差 90°"上 | 实测两台 TCP 偏置 → 重跑 `RAL2027/kinematics/` 全部脚本 → **把"夹爪差异单独贡献几个点"报成阶梯上的一档**。**重跑之前正文不得写任何可行率数字** | §4.5 P5 / §7 P0 |


**未解决 / 已接受的风险（诚实标注，不粉饰）**：
- **n=2 的一般性**：两具本体不足以支撑关于 embodiment 的一般规律。措辞一律限定为 "a spectrum measured on this pair"，绝不写 generalizes across embodiments。**加入单臂 reader 后 n 从 2 提到 3**，缓解但不解决。无技术解。
- **reader #3 是同一台机器的单臂模式**，不是真正的第三种形态；但它是**在售 SKU** 且通过 own-task-competence 检验。admission cost 只是下界。
- **绝对成功率可能很低**（对照：RECAP 真机 close-cabinet 30%；RoboMME 最好方法 44.51% 而人类 90.5%；**R-t-S 在同款双臂 AgileX PiPER 上叠 T 恤 39–48%**）。已在 §1 ¶5 主动划边界并在所有图里画 frozen-base 地板线。**好消息**：R-t-S 的 39–48% 正落在 headroom 窗口 → **叠衣族不需人为制造 headroom；但门族必须做**（否则天花板）。
- **★ 谱系交叉点可能不存在（新增，最致命）**：在 6-DoF 无零空间的臂上，**同本体** FK→IK 几乎无损（实测 position-only 可行率 100.0%），③与④很可能生成数值上几乎相同的轨迹。**由 G0.5 判定，成本 0 机器人小时**；`SR_same(④) − SR_same(③) < 5 pp` → 四层谱系框架当场死亡，切 **cross-body admissibility** 的 fallback framing（预注册文本必须现在就写进补充材料）。
- **★ 可形变物无法复现初始状态（新增）**：一件衣服的初始褶皱物理上不可复现，而 McNemar / harm rate / 成对 Δ 三个量全部建立在 matched initial state 上。→ 拆两个预注册主端点 + 容差化配对（模板 IoU ≥ 0.90）+ **A/A 噪声地板控制（不可砍）**。F 族的配对只能称 "state-matched to within a pre-registered tolerance"，**绝不写 identical initial state**。
- **抢跑窗口（排序已变，R-t-S 升到第一位）**：**Retrieve-then-Steer 团队**已同时拥有 6-DoF ALOHA-PiPER 与 7-DoF OpenArm 两具异构双臂本体，并在正文里点名二者 "different arm kinematics, gripper designs, and workspace layouts"——**做跨本体记忆只差一个实验**；Dejavu 附录逐字写出我们的方案（"unified latent representation spaces or lightweight alignment layers that enable cross-robot retrieval and reuse of experience, while guarding against negative transfer"，一手核实）；RECAP §6 把跨本体检索表示标为 open question；RoboMME §6 点名 memory-bank methods + mobile manipulation；VLA-Pro future work 点名 hierarchical procedural states。**建议 G2a 通过后立即 arXiv 占位 P1′/P2/P3′。**


---

# 1. 第 I 节：引言——故事线与动机

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
- [ ] **不出现 "Piper vs PiperX" 作为本体对的门面**（框架反转，见下）
- [ ] **不写"连杆长度不同"**——审稿人会认为不足以支撑跨本体主张
- [ ] **不把层③的失败写成"不同运动学族"**（放宽限位即 100%，20 行代码可证伪）
- [ ] **不只报 82.8°**——必须自己先报标定后的 7.10 cm / 17.8°
- [ ] ④层的表述里**不出现"潜码 / latents"**（那正是 GR00T EmbodimentTag 在做的事）

**★ 框架反转（零成本，收益最大，写进 ¶5 与 §IV）**：正文**永远不要以 "Piper vs PiperX" 作为本体对的门面**。用最宽的一档（单臂 reader，14→7 维）开场，把 Piper↔PiperX 放在阶梯的**最难/最保守**一端，写成：

> even between two arms from the same vendor and generation, with the same DoF, the same payload, the same repeatability and a 6.9 % difference in reach, joint-space content does not transfer.

这句话比"我们跨了两台臂"强一个量级，而且它**把审稿人的先天怀疑变成论文的论点**。


## 1.1 ¶1 — *现象，以及为什么显而易见的答案并不是答案*

**功能**：把“检索增强冻结 VLA 有效”设为既定前提；同时**当场堵死“为什么不共训”**（R1-B8，最强的“轴是硬造的”质疑）。这两件事必须在同一段完成，否则读者会带着这个疑问读完全文。

**核心句**：
> 检索增强的冻结 vision-language-action (VLA) policy 现在已经可行。一个已部署的机器人可以存储成功经验，在测试时检索这些经验，并在不更新任何一个权重的情况下提升其可靠性。这不再是一个猜想：这一设计空间已经被系统梳理，其作用机制已经被消融分析，而且该方向已经拥有了 benchmark。

> 将一个机器人的经验交给另一个机器人的显而易见做法，是等待下一轮训练。这个答案是正确的，但还不够。共训能够摊销一个机器人群体已经知道的内容；却无法摊销某一个本体在一小时前刚学到的东西——一个新遇到的物体实例、一个被重新布置的工作单元、一个今天早上才发现的失效模式。记忆之所以值得跨本体传递，恰恰在于这类经验必须在下一轮训练开始之前就能够被复用。

**证据与引用**（全部来自一手 PDF）：Retrieve-then-Steer（冻结 π0.5，LIBERO-10 92.4→94.4，推理开销 1.10×）；RECAP（策略冻结、只往池加演示，RoboTwin held-out 4.0→31.5）；Dejavu（部署过程中记忆库增长，LIBERO + AgiBot-G1）；RoboMME（该方向已有 benchmark 与 leaderboard）。RAEA (CVPR'24) 可用一个 e.g. 带过。

**注意**：¶1 引用的 92.4→94.4 是接近天花板的 regime，而我们预期的跨本体绝对值在地板附近。必须在本段末加一个从句区分两种 regime，否则与 ¶5 的能力边界叙事不自洽（Reviewer #2 指出的节间矛盾）：
> 这些增益是在各自 benchmark 接近天花板的 regime 下报告的；而我们研究的恰恰是相反的 regime，即 base policy 已经不可靠的情形。

## 1.2 ¶2 — *无人明写下来的前提*（**全文转轴，措辞精度决定生死**）

**功能**：点名共同前提，用可被逐条核对、可被证伪的形式陈述。

**母句（五处逐字一致的那一句）**：
> 然而，在这一系列工作中，还没有任何一种由机器人*在其自身部署过程中写入*、包含*可执行动作内容*的 persistent store，曾在*不对第二个已部署本体的 policy 做任何进一步更新*的情况下，被第二个已部署本体读取。

**逐个走一遍（每篇一句，含一手证据）**：
- **RECAP**（必须极小心，**这是唯一一句漏掉就等于 misrepresent related work 的**）：它是一篇跨 embodiment 论文——其 pool 可由 disc pusher、UR5 或 human hand 写入，并由不同的目标机器人读取。它与我们所提问题有两点区别：其摘要明确写道 *“Fine-tuning is needed only to take on a new, unseen embodiment, not for each new task,”*，并且其 pool embodiment *“is never deployed.”*
- **Dejavu**：其 Limitations 逐字（一手核实）“each VLA backbone maintains its own experience bank, tailored to a single domain or embodiment; this simplifies training but prevents reusing experience across ... different manipulation platforms”，并把 “unified latent representation spaces or lightweight alignment layers that enable cross-robot retrieval and reuse of experience, **while guarding against negative transfer**” 列为 future work。**这是全领域最接近我们命题的一手空白证据。**
- **Retrieve-then-Steer**：key 是复用 VLA 自己 visual encoder 的多视角池化特征；记忆**每个任务开始时重新初始化**（附录 D.3），连跨任务都不是。
- **VLA-Pro / CLARE**：条目就是 LoRA adapter / adapter 模块，与骨干和 action head 同生共死。
- **RAM / RoboOS**（必须主动点名，否则 Table I 自带反例）：RAM 的 660 条 affordance 库确实被两种本体读取，但它由第三方语料离线策划、部分人工修正，且 RAM 把自己成功的 rollout **蒸馏成 ACT 权重而非追加为条目**；RoboOS 的 shared memory 确实跨异构机器人且部署中增长，但其内容自陈是 scene graph、tool-calling 历史与各机器人的 joint/battery 状态 —— 跨过身体的是**东西在哪、哪台机器人有空**，不是怎么动。
- **镜像观察（收尾）**：确实被外来身体读取的动作知识——RoboTTT 的人类视频上下文、MimicDroid 的 human play video → 人形机器人（靠腕部位姿 retargeting）——用完即弃，不跨 episode 累积、不可检索、不可删除。

**结论句**：
> 持久性、自主写入性，以及第二个 reader，迄今尚未在同一个存储体中同时出现。

## 1.3 ¶3 — *为什么这是条目的属性，而不是任何人的疏漏（Why this is a property of the entry, not of anyone's oversight）*

**功能**：把现象升格为机制。**注意：此段的论证强度必须比基线设计低一档**（风险 A），改为“表示决定了什么必须被重新标定/重新解码”，而不是“机制性否决”。

**核心句**：
> 一个条目的两端——key 和 value——都是在生成它的身体坐标系中写下的。value 记录的是该身体实际做了什么：joint commands、action-expert latents，或 adapter weights，而这些都不是另一条不同运动链能够直接执行的。key 则用该身体自身的感知特征来索引该条目，因此来自外来身体的 query 不只是相似度更低，而是*分布不同*：同一身体的 retriever 所工作的 similarity threshold 是按部署逐一校准的，而 reader 的更换会迫使系统重新校准；这一代价——为了维持 precision，必须牺牲多少 recall——至今从未被测量。**(§V-A, Fig. 3)**

> 该领域一直在固定条目表示的前提下优化 retrieval 和 injection。对于*跨身体可读性*——且只针对这一点；在同体场景下，injection 机制在准确率上已被证明占主导——真正的约束在于条目究竟由什么构成。

**加分句（半句，若有余量）**：
> 机器人记忆已经被赋予了 *when*、*where*、*what* 和 *how* 的分类学——这是关于“记住了什么”的四个问题，却没有一个问题涉及“谁可以读取它”。

**红线**：不得写 v4 §2 那句“记忆的价值上限由表示层级决定，而不是由检索或注入机制决定”（RoboMME 实测 memory-as-modulator 44.51 vs memory-as-context 30.68 直接反驳）。

## 1.4 ¶4 — *我们改变了什么、为什么现在可解，以及我们没有发明什么（What we change, why it is solvable now, and what we did not invent）*

**功能**：四句交代方法 + 主动交代全部梯度 + 非贡献声明 + why now。

**(a) 分层 value**：
> 我们改变的是“存什么”。一个条目记录的不是身体做了什么，而是当时情境需要什么，并且同时在四个抽象层级上记录：一个语言摘要，用于指称物体及其关系，但*不包含 writer-frame pixel coordinates*，从而 reader 可以在自己的图像中重新 grounding；一个以物体为中心的 subgoal sequence；一个在物体锚定任务坐标系中的 end-effector deltas；以及一个 joint-space action chunk。

**注意（Reviewer #2 抓到的冲突）**：RoboMME 实测 GroundSG（带像素坐标）全面优于 SimpleSG —— 但那是**同一台 Franka、同一相机**下测的。像素坐标是写入者相机系的量，换本体后无意义。**我们的 ① 层必须是“可重新 grounding 的语言”而不是“带写入者像素坐标的语言”**，并在 ¶4 用半句说明为什么不能照搬 RoboMME 的结论。

**(b) body-agnostic key**：冻结 VLM 前缀 embedding + 物体中心关系编码，外加一张**只训练一次**的对齐图。

**(c) 统一读出接口（本文的机制增量，必须写清）**：
> 每一个层级在 readout 之前都会先被解码到 reader 自身的动作空间中，因此被改变的是抽象层级，而 injection point 保持不变。

**(d) 主动交代全部梯度（不可省）**：
> 这个系统中有两部分会被训练，并且两者都不会在部署期间训练。每个身体的 base policy 都在部署前仅 fine-tune 一次，所用任务与 memory-evaluation tasks 相互不重合。对齐图只在线下训练一次，使用的是弱配对数据——两个身体执行同一任务，但数据是彼此独立采集而非一一对应——并且不会随着任务或条目的累积而更新。一旦某个身体完成部署，就不会有任何 gradient 到达其 policy，而接纳存储体也不会改变任何权重。我们还报告了一个完全 training-free、以 language-keyed 为基础的变体，作为诚实的下限。

**(e) 非贡献声明（第一处）**：
> 一旦条目已被解码到 reader 的动作空间中，之后所有将其转化为动作的部分——聚合为 elite prior、在 flow-matching sampler 的中间状态进行 injection、按置信度自适应地调节 guidance strength，以及在置信度低时 abstention——都原样采用自 Retrieve-then-Steer。我们不对此主张贡献。

**(f) Why now（两个刚成立的前提）**：
- π0.5 级骨干只有在共训过大规模 visual grounding 数据后，才真正能够吃下符号记忆（RoboMME 实测换 OpenVLA-OFT 骨干后，同样的符号记忆从 32.70 掉到 19.5）。
- 跨本体的写入门控已经存在：VLAC 式 critic 依赖视觉状态与语言目标，而非统一动作空间；Retrieve-then-Steer 报告其 precision 0.970 / recall 0.678，正是记忆写入所需的高 precision 工作点。**【待确认：VLAC 权重是否公开可得，见 §7 优先级 1】** 若不可得，本句改为“高 precision、低 recall 的写入门控在少量标注下可达”，并把 0.970/0.678 引为目标工作点而非现成组件。

## 1.5 ¶5 — *我们验证什么、预期是什么，以及边界在哪里（What we verify, the predictions, and the boundary）*

**核心句**：
> 我们在两个都实际部署的身体上测试这一问题：一台**球形手腕的双臂 Piper**，以及一台**偏置手腕的双臂 PiperX**——二者 DoF、负载、重复精度完全相同，臂展相差 6.9%，但分属不同运动学族（Puma 型 vs UR 型；同名关节语义不同：Piper 的 j4 是腕部 roll，PiperX 的 j4 是肘平面 pitch）。二者都向同一个存储体写入，也都从中读取，并且两个方向都测。我们报告的是在这一对身体上测得的一条谱系，而不是关于所有身体的一条定律。

**预注册预测（一句三分句，~60 词，带前向引用）**：
> 我们在报告结果之前先陈述预测。**(P1′)** 存在一个抽象层级 ℓ\*，使得同本体读取上更具体的层更精确、而跨本体读取上更抽象的层更可迁移——**即两条曲线在 ℓ\* 处交叉**，我们预测 ℓ\* 落在③与④之间 (§V-B)。 **(P2)** Cross-body 损失主要由 retrieval 和 retargeting 两项主导，而不是由 value 不可执行性主导 (§V-C)。 **(P3′)** 两个身体之间的 transfer 在方向上是不对称的，我们将这种不对称归因于**读者的关节限位包络对写者任务盒位姿的覆盖率**，并且**可以用一个纯离线的运动学统计量预测其方向与逐任务排序** (§V-D)。

> **P1′ 的措辞为什么必须收窄**：单调"越抽象越可迁移"不是 finding（GR00T N1.7 已主张）。**交叉点才是。没有哪一层永远最好。**
> **P3′ 的机理为什么换掉**：旧机理"定基记忆是移动记忆的子集"在本硬件上被证伪——两者工作空间体素 **IoU=0.528**，互不包含（Piper 被 X 覆盖 72.2%，X 被 Piper 覆盖 66.3%）。新机理有实测支持：Piper→X 层③ IK 可行 **80.0%** vs X→Piper **57.3%**，差 22.7 pt，因为 Piper 的 j5 只有 ±70°、是全臂最紧关节。

**P4 与 P5 不进 Intro**（P4 共享池负迁移是 P1′ 的推论；P5 是归因层的技术命题）；分别在 §V-E 与 §V-C 定义。


**主动划边界（不可省）**：
> 由于两个 backbone 都保持冻结，memory 所能带来的，是对 base policy 已经具备的行为进行召回与重组，而不是获得新的 motor skills。我们报告逐次试验的 memory-harm rate；并且在每一个 success rate 旁边同时报告 injection rate——即实际注入了某个 prior 的试验所占比例——因为一个经常选择 abstain 的 retrieval 系统，否则可能会在实际上什么都没做的情况下，看起来实现了完美迁移。

**最后一句（时效性论据的实验兑现，指向 E5）**：
> 我们还直接报告 crossover point：reader 需要多少个新鲜 demonstrations，以及收集这些 demonstrations 需要多长时间，才能达到它通过读取 writer 条目所获得的效果。

## 1.6 Fig. 1 设计与 caption

**Fig. 1（跨双栏，p.1 顶部，0.22 页，两 panel 横排 —— 已删除原 panel (c)）**

**Panel (a) "一个存储，两个已部署的身体"（"One store, two deployed bodies"）**：左 = **双臂 Piper**（球腕）实拍；右 = **双臂 PiperX**（偏置腕）在**不同工位/不同视角**执行同一任务实拍。中间数据库圆柱标 `persistent store`。Piper → DB 实线 `write`，DB → PiperX 实线 `read`，读箭头挂徽章 `no gradient after deployment`（**不是 "no policy update"** —— 措辞必须与 ¶4(d) 一致）。浅色反向箭头表 bidirectional。角标小字：`both bodies deployed · both write · both read`。**建议在角标补一句 `same DoF · same payload · different wrist topology`——把最弱的一面主动交出来，然后用运动学族反击。**

**Panel (b) "条目中包含什么，以及它如何被读取"（"What is in an entry, and how it is read"）**：一张卡片，四条色带 ①grounded-but-re-groundable language ②object-centric subgoals ③**anchor-frame contact-point motion，含显式 (T_abs, T_rel) 拆分** ④joint-space action chunk（**物理单位**）；左侧钥匙图标标 `body-agnostic key`；**右侧画出统一读出接口**：四层各有一条箭头汇入同一个 `decode → reader's action space` 方框，再汇入 `frozen flow sampler, intermediate-state injection [R-t-S]`。这张图同时完成两件事：展示分层，以及**用图形声明注入通路是常量**（对抗 R1-B2 的共线质疑）。

**制作所需数据**：(a) 两台真机同任务实拍各 1 张（需现场补拍，含工位背景差异）；(b) 从我们自己的库导出的**一条真实条目**的四层内容（不要手编）。**(b) 的素材直接来自 demo 第二段（§4.10），不另拍。**


**Caption 英文初稿**：
> Fig. 1. **由两个已部署身体共享的持久动作存储。** (a) 一台**球腕双臂 Piper** 和一台**偏置腕双臂 PiperX** 都已部署——二者 DoF、负载与重复精度相同，臂展相差 6.9%，但分属不同运动学族；二者都向同一个 persistent store 写入，也都从中读取，并且各自都会读取由对方写入的条目，而在部署之后没有任何 gradient 到达其 policy。(b) 每个条目以四个抽象层次保存同一段经验，从由 reader 在其自身图像中重新 grounding 的语言摘要，一直到以物理单位保存的 joint-space action chunk，并由一个 body-agnostic key 索引。每一层都会先被 decode 到 reader 自身的 action space，然后再注入到 reader 冻结的 flow-matching sampler 的某个 intermediate state 中，因此被改变的是抽象层次，而被固定不变的是注入点；实际到达的层次本身也是一个测量量（§V-B）。

## 1.7 待定决策（Intro 专属，写第一个字之前必须定）

1. **母句最终措辞** —— 已定为 §1.2 那句。五处派生对象（Title / Abstract / ¶2 / C1 / Fig.1 caption）必须逐字一致。
2. **Fig. 1 是否用真机照片** —— 是。RA-L 对首页真机照片有正反馈，且是我们相对纯仿真团队的可见壁垒。需在 G3 之前补拍。
3. **仿真是否进 Intro** —— 否（按 §0.5 裁剪 5）。¶5 只说 "on two bodies"，不写 "in simulation and on hardware"。
4. **P4 是否进 Intro** —— 否。


---

# 2. 第 II 节：相关工作

**预算 0.75 页 = Table I (0.22, 跨双栏, 置于 p.2 顶部) + 正文 5 段 ≈ 480 词。**

## 2.0 划分依据（写作前必须内化的一句话）

**按“记忆在物理上住在哪里”分区，不按“用了什么方法”分区。** 因为本文的命题是“谁能读一段记忆，由这段记忆被存成什么决定”，所以分区必须沿存储基底（上下文 → 参数 → 显式条目）切，"读者集合"就成为分区的推论而非另一条独立的轴。三个基底各自只能给出“持久”与“可跨体读”中的一个。

**术语锁定（全文 glossary，§III 开头一句话对齐）**：`writer body` / `reader body` / `reader swap`。RECAP 已占用 query embodiment / pool embodiment / cross-embodiment retrieval 且语义不同（其 pool 从不部署），我们**不沿用**它的词汇，只在 §III 用一句话做映射：*"Unlike [RECAP], where the pool embodiment is never deployed, both of our bodies are deployed and each is both a writer and a reader."*

## 2.1 II-A. 随 Episode 结束的记忆（Memory That Ends With the Episode，1 段，~110 词）

**功能**：提前拆掉“cross-embodiment reading is already done”这颗雷。

- 用 RoboMME 把这一族的形式化定义钉死：策略从 `a_t ~ π(·|l,o_t)` 扩展为 `a_t ~ π(·|l,o_t,M_t)`，历史定义为 `H_t = {(I_τ,a_τ)}_{τ<t}` —— **下标锁死在同一条 episode 内**。
- **采用其表示轴与注入轴的术语**（symbolic / perceptual / recurrent；context / modulator / expert），声明不另起炉灶。**但不宣称对齐其 when/where/what/how 四类任务**——那四类是 episode 内非马尔可夫推理的类别，我们的条目是跨部署动作先验，硬对齐是修辞而非事实（Reviewer #2 指出的节间矛盾）。四维只在 Intro ¶3 作为一句修辞出现（“四个问题都是记什么，没有一个是谁能读”）。
- **主动交出最危险的事实**：跨本体读取在这一族里已经发生过——MimicDroid 做人手腕部位姿到人形机器人的 retarget 以 bridge the embodiment gap；RoboTTT 从 in-context 人类视频做 one-shot imitation；RoboMME 真机的 TrackCube / RepickBlock 参考视频里操作者就是人类。
- **落点句**：这一族证明的是“另一具身体可以被读取”，不是“另一具身体可以读取被保存下来的东西”；上下文用完即弃，没有任何东西可以被索引、复访、删除。
- 免费引文：RoboTTT 自陈 long-term reasoning "can be delegated to external memory banks" —— in-context 阵营亲口把持久记忆的位置让出来。
- **不在 RoboMME 上报数**（决策已定，理由见 §7 优先级 6）。因此 II-A 只能写“我们采用其表示/注入轴的术语”，不能写“我们在其协议下报数”。

## 2.2 II-B. 写入参数的记忆（Memory Written Into Parameters，1.5 段，~150 词）

**¶2 —— 写一次经验 = 跑一次梯度。**
- Info-VLA（π0.5 骨干，LIBERO，摘要开篇 "suffer from severe catastrophic forgetting"）vs Liu et al.（预训练 π0 "remarkably resistant to forgetting"，"simple ER works surprisingly well… sometimes achieving zero forgetting even with a small replay data size"）。
- **遗忘之争的三句话（定稿，不站队，给可核对的方法学差异）**：
> 预训练 VLA 是否会遗忘，在同一个 benchmark 上目前仍有争议。两种立场在 replay budget，以及任务流开始前 policy 是否已经预训练，这两个方面存在差异；我们不在此作出裁决。我们把 forgetting 作为诊断量而不是前提来报告：无论哪一种立场成立，保存在 weights 中的知识都只能通过承载它的 weights 被访问——它不能被枚举、不能按条目逐一删除，也不能交给另一台机器人。

- **ER 立为一等 baseline**，但比较轴是写入代价而非 success rate。

**¶3 —— 参数记忆已经条目化、可删除、可检索。**
- CLARE（模块化 adapter + 按层特征相似度自主扩展 + 部署期无标签 autoencoder 路由；LIBERO + 5 个真机任务，全部单台 Panda）；VLA-Pro（把 task-specific LoRA adapter 当作 parameterized procedural memory 存进 bank，推理时检索并动态融合）。
- **主动认输的那句话**：删掉一个 adapter 就删掉一个技能 —— **条目级可撤销性因此不是本文卖点，而是共享性质**；“对参数条目做检索”也已被 VLA-Pro 做掉。
- **一个从句主动点出** VLA-Pro 的 future work 已写到 "hierarchical or compositional procedural states"，即分层记忆表示对它不是盲区而是排期项，且发生在参数基底内。
- **大规模跨本体共训（RT-X / OpenVLA 一族）并入本段**：同样把跨本体知识写进参数，只是粒度是整个预训练；一组权重可以驱动多具身体，但身体集合与技能集合在梯度跑完时就冻结了。**共训不产生记忆对象，故不进 Table I**（有原则的排除，正文写明一句）。**【待确认】RT-X / OpenVLA 一手 PDF 本组尚未读过，只能作结构性表述，不得引用任何数字或 venue。**

## 2.3 II-C. 写成显式条目的记忆（Memory Written As Explicit Entries，2 段，~200 词，全节最重）

**¶4 —— 按条目里 value 的抽象层级排成阶梯（这是 §III 分层设计的动机来源）。**
- **④ 逐帧原始动作**：VINN 存储逐时间步的 (观测 embedding, 专家动作)，读出是 embedding 空间中 k 近邻的 softmin 加权平均；当人手演示迁移到机器人时，需要一个**手工调节的逐轴系数**来补偿本体差异（来源：`threat_RAM_RoboOS.md` §11）。**venue 未核实，引用时只标 arXiv。**
- **③ 物体相对末端速度 / 锚点系接触点运动**：Di Palo & Johns（**RA-L 2023**）提出 retrieve–align–replay，使用 DINO-ViT 检索 bottleneck 目标图 + 视觉伺服对齐 + 开环回放 6-DoF EE 速度轨迹，training/intra-class/inter-class 分别为 80% / 73% / 67%；DINOBot (ICRA'24) 保留了完全相同的 value，仅替换了对齐机制。**同一 venue，必须主动引用、主动划界。**
  - **★ 还必须补上 GR00T N1.7**：其 README 明文主张 relative EEF action space —— "Representing actions as **deltas from the current pose** … is **a key factor in the model's cross-embodiment performance**"，且已参数化为 `ActionConfig(rep=RELATIVE, type=EEF)`。→ **③层不能再宣称新颖**，重新定位为"**已知会迁移的那一层**，纳入谱系是为了给另外三层提供标定基准（upper anchor）"。
  - **★ 还必须补上 point-track / flow 一族（9 篇，按族打包为 1–2 条引用）**：ATM (2401.00025)、Track2Act (ECCV'24)、Im2Flow2Act (CoRL'24)、MT-π、3DFlowAction、PointAction、ContactFlow、Point Policy、P3-PO；以及 kPAM 2.0 (RA-L) 的 "object-centric action representation in terms of … oriented keypoints"。**全部自带跨本体证据。**
  - **本文在③层的新颖点因此收窄为**："把它做成**持久、自写入、跨本体可读**的记忆条目"，而不是"提出这种表示"。

- **② 物体中心 affordance**：Robo-ABC（51 类，(无遮挡 crop, 2D 接触点)）；RAM（660 条，离线提取自 DROID / HOI4D / 互联网图片，读出为一个 3D 接触点 + 一个接触后方向，由 AnyGrasp + MoveIt!/cuRobo 执行，自称 zero-shot、embodiment-agnostic，跨本体仅有定性 demo、没有 success rate 表）。
- **① 语言 / 规划层**：RoboHarness（success/failure 双库 + 两阶段 consolidation，围绕冻结的 π0/π0.5/SmolVLA，全部为 LIBERO 仿真、无真机）；RoboOS（跨异构机器人的 shared memory：场景图、工具调用历史、各机器人 motion domain constraints / 关节状态 / 电量）。
- **落点句（= SQ1 的动机句）**：这四层分别被不同论文占据，运行在不同机器人上，采用不同协议与不同读出端（运动规划器 / 视觉伺服+开环回放 / k-NN 平均 / 提示词重写）—— 正因如此，层与层之间的权衡至今无法比较。
- **必须主动说清 RoboOS 的边界**：跨越身体传递的是**东西在哪、哪台机器人有空**，而不是怎么动；技能仍然封装在各机器人本地的 skill library 中；其 "embodiment memory" 恰恰是本体绑定信息的显式存储，反而正面例证了我们的论点。
- **必须主动说清 RAM 的边界**：660 条全部是离线提取自第三方语料且部分经过人工修正；**RAM 将自己成功的 rollout 蒸馏为 ACT 权重，而不是追加为条目**（最有力的一击）；读出端是抓取生成器 + 运动规划器。
- Ag2Manip 用半句带过，仅用于拆解 "agent-agnostic" 的命名撞车（它根本没有记忆库，知识在编码器权重里，且仅限单一本体）。

**¶5 —— 现代冻结 VLA 系统：条目是谁写的 / 更换 reader 要付出什么代价。**
- **Dejavu**：冻结 VLA + Experience Feedback Network，记忆库在部署过程中持续扩充；但 EFN 是通过 RL 训练得到的，而且其 Limitations 逐字写道（已做一手核实）："each VLA backbone maintains its own experience bank, tailored to a single domain or embodiment; this simplifies training but prevents reusing experience across ... different manipulation platforms"，并将 alignment layers 与 guarding against negative transfer 列为 future work。
- **Retrieve-then-Steer**：冻结 π0/π0.5/CogACT，在部署中在线写入由 VLAC 校准的成功片段；条目是 (VLA visual-encoder 池化特征 key, action chunk)；注入点位于 flow 采样器的中间态，并结合置信度自适应引导；**记忆在每个任务开始时都会重新初始化**；淘汰机制只有 FIFO。
  - **★ 必须升级为"同硬件同任务的直接前作"，不再只是"注入机制提供者"**（v5 §2.3）：其附录 D 已在**同款双臂 AgileX PiPER**（ALOHA 式配置、两只 6-DoF PiPER + 两指夹爪）上做过 **bimanual T-shirt folding**，π0.5+Ours 在 in-domain 黄 T 恤 **42.0→50.0**、OOD 白 T 恤 36.0→46.0，**每任务 50 trials、成对同初始状态、评测时基座冻结**。另一平台是 7-DoF OpenArm，原文明说二者 "provide complementary testbeds for evaluating our method across **different arm kinematics**, gripper designs, and workspace layouts"。
  - **划界措辞（正文可直接用）**：*Retrieve-then-Steer demonstrates online success memory on an ALOHA-PiPER platform for bimanual T-shirt folding (42.0→50.0 over 50 trials on a single task), but its memory is written and read by the same platform; it reports no transfer between its two platforms, and cross-embodiment reuse does not appear among its stated limitations or future work.*
  - **一手核实的边界**：全文 `cross-platform` / `cross-embodiment` / `shared memory` / `across platforms` **零命中**；future work 只提"更可靠的成功验证、不确定性感知检索、可扩展记忆管理、更动态的环境"，**没有跨本体**。
  - **反过来可为我所用的一句**：其 Limitations 逐字写道，当 "object layouts, camera viewpoints, task goals, or **robot calibration** change rapidly, previously stored action priors may become less informative or **even misleading**" —— **既承认记忆是标定/本体绑定的，又给了我们 harm rate 指标一个可引的出处。**

- **RECAP**：在配对演示上训练一次后即冻结，依靠向池中追加 pool 侧演示、且无需训练来吸收新任务；共享表示是 SE(3) EE pose + gripper；pool embodiment "is never deployed"；摘要逐字写道 "Fine-tuning is needed only to take on a new, unseen embodiment, not for each new task"；Limitations 亲口将 "what constitutes an effective representation for cross-embodiment retrieval" 标为 open question。
- retrieve-then-finetune 一族（Behavior Retrieval / STRAP）：检索的是**训练数据**，取回后仍然需要运行梯度，用一句话带过。**【待确认】本组尚未通读这两篇全文，Table I 中该族已整行删除（见 2.4）。**
- 其余同族（RAEA / RTCF / Remember Smarter / SkillMemo / RAGDP）打包为一个 e.g.。
- **落点句**：这些系统中的 reader embodiment 在设计时就已固定。RECAP 将适配代价在任务维度上摊薄，却没有在身体维度上摊薄；Retrieve-then-Steer 的相似度门是在每次部署时分别标定的，更换 reader 需要重新标定，而这一代价从未被测量过（前向引用 Fig. 3）；Dejavu 则直接把跨机器人复用写成了自己的 future work。
- **同段声明沿用**（不能没有）：中间态注入与置信度自适应引导来自 Retrieve-then-Steer；零梯度池增长的证明范式来自 RECAP（其 Fig.4 PushT 6.0→34.9、Fig.7 RoboTwin 池 11→35 个任务时 9.0→31.5，policy 全程冻结）。

**II-D 已并入 ¶5 末尾（3 句，不引入新文献）**：
1. 合取式一次说完：由部署中的机器人自己以零梯度、单步方式写入；作为可删除的显式条目跨部署留存；由另一具同样处于部署中的身体在无 policy 梯度下读取；读出端是冻结的 VLA action expert 加一个非学习的 retarget 算子（**必须补上 retarget，否则是 overclaim**）。
2. 诚实清单（不可省）：注入机制来自 Retrieve-then-Steer，**且同类机制在 GR00T N1.7 的 real-time chunking 中已有工业实现**；零梯度池增长来自 RECAP；条目级删除来自 CLARE；表示/注入轴的术语来自 RoboMME；embodiment-agnostic 检索来自 RAM；**②③④ 三层的表示设计分别有 RAM / Di Palo & Johns（+GR00T N1.7 + point-track 一族）/ VINN 的先例**；**条目 schema 直接采用 RDT-1B 的 128 维 `STATE_VEC_IDX_MAPPING`（③④按臂并列具名 + `action_mask`）**；**冻结 π0.5 + 检索记忆在双臂 AgileX PiPER 上叠 T 恤已由 Retrieve-then-Steer 附录 D 完成**。
3. 贡献钉在唯一不可替代的那条：**在同一次采集、同一套协议、同一个读出接口下并排测量四个抽象层级的迁移率并定位交叉点，并把跨本体损失分解为 key / 限位包络 / 几何 / value 四项。**
4. **★ 一个必须主动引用的对照（Intro 也用）**：**GR00T 用"更新参数"解决跨本体**——其 `CategorySpecificLinear.W = 0.02*randn(num_categories, in, out)` 意味着新本体拿到一片**随机初始化**的 state/action 编解码权重、必须用该本体数据训练；**而本文的主张恰恰是"不更新策略参数"**。这是全文最好用的一句对照。
5. **★ 一个已核实的真空白**：`all:"cloth manipulation" AND all:"cross-embodiment"` 在 arXiv **0 条**。跨机器人的布料操作经验迁移无人做过，**这个空白是真的，可写**。


## 2.4 Table I（完整 Markdown，8 行 × 6 列，纯符号）

**caption 必须承载全部散文与判定标准，否则每一格都可能被质疑不公平。**

**列定义**：
- **Value** = 持久保存内容的抽象层级（①语言 ②物体中心 ③任务坐标系 EE ④关节动作/潜码；`par`=参数；`env`=环境/调度状态；`ctx`=仅上下文）
- **Persist** = 是否跨 episode 且跨部署存活
- **Self-write** = 是否由部署中的机器人自己写入，且写入过程无梯度
- **2nd reader** = 是否有第二具身体消费该条目（`✓*` = 需要 target 侧梯度）
- **Readout** = 取回后由什么转换成动作（`pol`=学习策略；`plan`=运动规划器/伺服/开环回放；`grad`=再训练；`ctx`=上下文条件化）
- **New-reader cost** = 引入一个新 reader embodiment 的代价

**列序刻意排成 Value → Persist → Self-write → 2nd reader → Readout**，读者顺着列读下来，就会自动得到母句中的三个限定词。

| # | Family (representative) | Value | Persist | Self-write | 2nd reader | Readout | New-reader cost |
|---|---|---|---|---|---|---|---|
| 1 | Within-episode context (RoboMME; RoboTTT; MimicDroid; **Instant-Fold**) | ctx | ✗ | ✓ (episode) | ✓ (human→robot) | ctx | n/a |
| 2 | Parametric, monolithic (seq. FT; ER) | par | ✓ | ✗ | ✗ | grad | full retrain |
| 3 | Parametric, modular (CLARE; VLA-Pro) | par | ✓ | ✗ | ✗ | pol | impossible (bound to backbone) |
| 4 | Explicit entries, planner readout (VINN; Di Palo & Johns; Robo-ABC; RAM) | ②③④ | ✓ | ✗ | ✓ (RAM, qualitative) | plan | n/a (no policy) |
| 5 | Explicit entries, agent level (RoboHarness; RoboOS) | ①/env | ✓ | ✓ | ✓ (RoboOS) | ctx / plan | none, but no action content |
| 6 | Deployment-written, same body (**Retrieve-then-Steer**; Dejavu) | ④ | per-task ↺ / ✓ | ✓ / ✓(bank) | ✗ | pol | not supported |
| 7 | Curated cross-body pool (RECAP) | ③ | ✓ | ✗ (pool never deployed) | ✓* | pol | one target-side fine-tune |
| 8 | **Ours** | **①–④ + tag** | **✓** | **✓** (deployment store) | **✓** (both deployed, bidirectional, **different wrist topology**) | **pol + retarget** | **one alignment map, no policy gradient** |

**★ 第 6 行的 body 列必须补注**：`ALOHA-PiPER (bimanual, 6-DoF ×2) + OpenArm (7-DoF ×2)` —— **他们已经有两具异构双臂本体，只是没有让记忆跨过去。** 这既是最诚实的写法，也是最有力的定位：我们做的正是他们硬件上具备、却没有做的那一个实验。


**相对 baseline 设计的三处判定修正（必须执行）**：
- **RECAP 的 Delete 列已整列删除** —— 原先判为 ✓ 的依据是 "4 episodes removed by hand"，但那是训练期为了对齐卫生而剔除的 query episode（训练数据清洗），不是部署期的条目删除；属于范畴错误。删除该列也同时节省版面。
- **Retrieve-then-Steer 的 Persist 写作 `per-task ↺`（重新初始化），不给 ✓** —— 附录 D.3 明确写道每个任务评测开始时记忆都会被初始化。
- **Behavior Retrieval / STRAP 整行删除** —— 本组尚未通读全文，原表中有 4 个 `?`。现改为在 ¶5 中用一句话带过。**不得靠推测填格。**

**Table I caption 英文初稿（承载散文与证据来源）**：
> TABLE I. **机器人的 memory 存在于何处，以及谁可以读取它。** Value：持久化内容的抽象层级——① language，② object-centric subgoal/affordance，③ task-frame end-effector motion，④ joint-space actions or latents；`par` = parameters，`env` = environment/scheduling state，`ctx` = context only。Self-write：由机器人在其自身部署期间、且不使用 gradients 写入。2nd reader：论文报告或展示了除 writer 之外的另一具 body 消费所存储的条目；`✓*` 表示需要在目标侧进行 fine-tune。Readout：`pol` = a learned policy，`plan` = a motion planner、visual servo 或 open-loop replay，`grad` = further gradient training，`ctx` = context conditioning。逐行证据如下：(1) memory 仅被形式化为当前 episode；(4) RAM 的 660 个条目是从第三方 corpora 离线挖掘而来，并经过部分人工校正，而且其自身成功的 rollouts 被蒸馏进 policy weights，而不是作为条目追加；(5) RoboOS 说明其 shared memory 保存 scene graphs、tool-calling history 以及每个机器人的 joint 与 battery state——不包含 action content；(6) Retrieve-then-Steer 在每个任务开始时重新初始化其 memory；(7) RECAP 的 pool embodiment “is never deployed”，且其摘要指出，对新的 embodiment 需要 fine-tuning。刻意不纳入大规模 cross-embodiment co-training：它产生的是 weights，而不是 memory objects。

## 2.5 审稿人备答清单（每条英文反驳，写进 rebuttal 模板）

| 预期质疑 | 英文备答（可直接粘贴） |
|---|---|
| "RECAP already does cross-embodiment retrieval." | RECAP 是一篇 cross-embodiment 论文，我们也在 §II 中如此表述。它的 pool embodiment 从未被部署，而且它的 reader 在训练时就是固定的：其摘要明确写道，接纳一个新的、未见过的 embodiment 需要 fine-tuning。我们的问题是：让一个*新的 reader*接入一个*既有的* store 需要付出什么代价；我们测量这一代价（§V-F），而不是支付它。 |
| "RAM already claims embodiment-agnostic memory." | RAM 的 memory 是离线地由 DROID、HOI4D 和 web images 构建而成，并经过部分人工修订；读取它的机器人从未向其中写入——相反，RAM 将其自身成功的 rollouts 转换为 ACT weights。它的 readout 是一个 grasp generator 加一个 motion planner，并且没有报告 cross-embodiment success rate。它是我们层级阶梯中 object-centric 层级的一个 baseline，我们也将其如此对待。 |
| "RoboOS already has a shared memory across heterogeneous robots." | 确实如此，而且其中跨 body 共享的是物体的位置以及哪台机器人处于空闲状态——RoboOS 本身将其 memory 描述为空间、时间和 embodiment state。skill 仍然保留在每台机器人的本地 library 中。我们的主张被限定在*可执行的 action content*上，而这恰恰是 RoboOS 不共享的内容。 |
| "The similarity-gate argument is a straw man; you would just recalibrate." | 我们同意，而且我们并没有提出那个论点。我们按条件分别进行 recalibrate，并报告无 threshold 的 retrieval quality（Fig. 3）；我们测量的是 cross-body reader 为了维持 precision 必须放弃多少 recall。 |
| "This is Neural Episodic Control with a VLA backbone." | NEC 的 memory 是一个按 agent、按 body 划分的 value estimates 表；而我们研究的性质——由一个 body 写入的条目能否被另一个 body 读取——在那个设定中并未被定义，也从未被测量。 |
| "Persistent, gradient-free growth was already shown by RECAP." | 的确如此，我们也将其作为该主张的标准进行引用。我们并不声称这一点；相反，我们保持 store 固定，仅替换 reader。 |
| "Entry-level deletion was already shown by CLARE." | 是的。可撤销性是我们与模块化 adapter memories 共享的一种性质，而不是我们的贡献。adapter 不可能具备的性质是第二个 reader。 |
| "Di Palo & Johns showed open-loop replay beats a learned policy." | 当对齐使 replay 在 frame 上不变、且由单一 body 定义 end-effector frame 时，这一结果成立。一旦读取的 body 发生变化，所存储 end-effector trajectory 的语义便不再保持，这正是我们测量的量（§V-C，retargeting term）。 |
| "Your sweep is much thinner than RoboMME's 14 variants." | 我们的 sweep 是沿着 body 轴展开的（2 个已部署 body × 4 个 value levels × k 种 key constructions），而不是沿着表示轴展开；我们采用 RoboMME 的表示与 injection 术语体系，而不是与其覆盖范围竞争。 |
| "Two bodies cannot support a claim about embodiment." | 两个 body 是这一问题得以存在的最小数量，我们将每一个结论都表述为在这一 body 对上测得的谱系。此外，我们还引入了第三种先前未见的 reader configuration 以报告接纳代价。 |


---

# 3. 第 III 节：方法——结构 / 数据管线 / 模块

**预算 1.30 页 = Fig. 2 (0.20) + Algorithm 1 (0.12) + 正文 ~0.98 页。**
子节：III-A Problem setting (0.20) / III-B Entry (0.25) / III-C Key and alignment (0.22) / III-D Readout (0.25) / III-E Write gate and lifecycle (0.14) / Fig.2 + Alg.1 (0.32)。

## 3.1 III-A. 问题设置（Problem Setting，含 LaTeX）

**术语对齐句（第一句）**：
> 我们将生成某个条目的 body 称为其 *writer*，将消费该条目的 body 称为 *reader*；*reader swap* 指在保持 store 固定的情况下，用一个替换另一个。不同于 [RECAP] 中 pool embodiment 从未被部署的设定，我们的两个 body 都被实际部署，并且每一个既是 writer 也是 reader。

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
\mathrm{SR}^{\mathrm{same}}_{\ell},\ \mathrm{SR}^{\mathrm{cross}}_{\ell}\ \ \text{（绝对 success rate）}\\
\mathrm{TR}_{\ell}=\mathrm{SR}^{\mathrm{cross}}_{\ell}\big/\mathrm{SR}^{\mathrm{same}}_{\ell}
\qquad\text{（仅为提供上下文而报告；所有主张均使用绝对 SR 与成对 }\Delta)
```

**为什么主张不建在 TR 上（一句话写进正文，对抗 R2-B1）**：
> success rate 的比值可以通过更频繁地 abstain 而被推高到接近 1；因此，我们对每一项主张都在匹配初始状态下，相对于每个 reader 自身的无记忆 base，以绝对 success rate 进行表述，并同时报告 injection rate。

## 3.2 III-B. 什么是一个 entry（含粒度定义 —— R3-B4）

**粒度（必须写死，否则 §V 的三个数字都不成立）**：
> 一个 entry 是一个*运动片段*，由夹爪开/合事件以及末端执行器速度的零交叉点共同界定。分段通过一个运行在我们语料中已有信号上的状态机完成；不使用任何学习式 segmenter。平均片段长度为 \todo{L} 步，因此一个包含 \todo{N} 个 entries 的 store 对应于 \todo{M} 个 episodes；我们在全文中同时报告这两种单位，因为既有工作中按 timestep 计数的 entries 与片段级计数不可直接比较。

**四层 value 的数据结构与生成方式**：

| 层 | 内容 | 生成方式 | 存储量级 | 已有占位者（RW 必须引用） |
|---|---|---|---|---|
| ① language | 一句摘要：动作动词 + 物体名 + 物体间关系（**无写入者像素坐标**），例 `"pull the top drawer handle toward the operator side"` | 冻结 VLM 对片段首末帧 + 任务指令生成；oracle 版由演示脚本/人工提供 | ~40 B | 无直接占位者 |
| ② object-centric subgoal | 子目标序列。**必须显式声明两套 anchor 原语词表**（否则两类任务上②层数字不可比、R2-B8 复活）：<br>• 铰接/DLO：`(primitive, joint_id 或 arc_station, Δθ 或 Δs)`（沿用 Kinematic-aware Prompting）<br>• 可形变：`(pick keypoint_i) → (place at keypoint_j / keypoint 系下偏移)`（沿用 CLASP 词表）<br>统一形式 `(contact point, target displacement in anchor frame)` | 由 ① + 物体/关键点跟踪构造；oracle 版由演示脚本 | ~200 B | RAM / Robo-ABC |
| ③ **anchor-frame contact-point motion** | **受控接触点（们）的轨迹**，表达在一个**低维、任务相关、与本体无关的几何锚点系**中；存在约束坐标时**退化为该标量剖面**；双臂情形额外存 **`(T_abs(t), T_rel(t))`**。<br>**四类任务的锚点**：铰链螺旋轴 (â,o)（一维 θ）→ DLO 弧长站（一维 s）→ 语义关键点元组（衣物）→ SOI 环（袋，**无成熟检测器，排除**） | 由末端位姿轨迹 + 锚点系变换。**布料上不需要 6-DoF 物体位姿**——见下 | 铰接门仅 **~100 B**（6T→T 个数）；其余 ~2 KB | **Di Palo & Johns (RA-L'23)** / DINOBot / **GR00T N1.7 (relative EEF)** / point-track 一族 9 篇 |
| ④ joint-space chunk | 写入本体的关节动作序列（双臂 14 维），按读出本体的 action horizon `H` 切块。**★ 一律存物理单位（关节角弧度、夹爪 [0,1]），绝不存归一化值**；读出时由读者用自己的 norm stats 重新归一化 | 直接来自 rollout | ~4 KB | VINN |

> **④层为什么必须删掉"潜码/latents"这个词**：那正是 GR00T 的 per-embodiment action head 在做的事，照原样写评审会说"这就是 EmbodimentTag"。正确定义：**④ = writer 写下的原始关节指令，reader 侧不允许有任何被训练过的解码器；唯一允许的桥是基于模型的（非学习的）FK/IK retarget。** 这样④的意义从"另一种表示"变成"**测量原始关节内容失效得多彻底**"。
>
> **④层为什么必须存物理单位**：两具本体各算 norm stats 会导致同一物理动作在两边归一化数值不同，④层的跨体失败中会混入**纯归一化失配**——审稿人一眼能看穿的平凡混淆。**这条必须写进 §IV 正文，不是实现细节。**

**存储成本一句话（必须给实测，不可空口）**：`bytes/entry = \todo{}`；\todo{N_max} 条 = \todo{} GB。**但成本不是争点，必要性才是** —— 见 III-D 的 derive-on-read 论证。

**②③ 共用同一个感知前端（必须主动写明，R3-B6）**：
> object-centric subgoals 与 anchor-frame contact-point motion 都需要锚点估计。我们在抓取前通过 detector 和 tracker 获得，在抓取后则利用夹爪自身位姿；因此 ② 和 ③ 共享同一种失效模式，我们也将按此方式进行报告。

**★ 但"刚性附着假设"对布料不成立，必须改写（v5 §4.4）**：
> 抓住布料后我们并不知道物体位姿，但**确切知道抓住了哪个物质点**，而夹爪位姿正好给出该物质点的精确轨迹。所以布料上的③应写成 **被抓物质点（们）相对关键点锚定系的轨迹**——形式上就是 point-track / flow 表示。这保住了 D2 的工时估计（不需要 6-DoF 位姿估计），同时对布料是**正确的**。

**★ 为什么③在铰接体上比 6-DoF 物体位姿更好用（可写进 §III 的论证）**：
- **几何论证**：单自由度旋转铰接体的位形空间是 S¹ 的一个区间。给定轴 (â, o) 与把手到轴的半径 r，末端接触点整条路径由标量 θ(t) 唯一生成。**其余 5 个自由度由约束规定而非由记忆规定**——记忆只需存"开到多少度、什么角速度剖面、在哪个角度有阻尼/卡扣"。
- **对前端误差的敏感度结构性更低**：自由刚体的位姿估计误差全额传导到③层；铰接体只有沿弧长一个方向的误差是表征误差，法向误差要么被柔顺吸收、要么变成内力。
- **经典引文（Crossref 已核）**：Task Frame Formalism（Bruyninckx & De Schutter, IEEE T-RA 1996, DOI 10.1109/70.508440）；Task Space Regions（Berenson et al., IJRR 2011, DOI 10.1177/0278364910396389）。
- **必须写进论文的诚实警告**：门固定于世界、物体系静止，这是**最容易的一档**；且门任务上②与③几乎退化为同一件事（②=`rotate by Δθ`，③=同句加 θ(t) 剖面）。**门任务能证明③可定义，但压不出②/③差异——这必须写成预测而非意外。**


## 3.3 III-C. 与本体无关的 key 与对齐映射

- **key 构造（4 种，作为 §V-A 的对照）**：
  1. `lang`：冻结文本编码器编码 ① 层摘要。**完全无训练**，是诚实地板（R2-B5 要求的、不受对齐图泄漏影响的唯一 arm）。
  2. `vlm-prefix`：冻结 VLM 前缀 embedding 池化。
  3. `obj-rel`：物体中心关系编码（物体类别 + 相对位姿图），采用 RECAP 式 20-D sign-flip 不变 proprio 编码（位置权重 4.0）作为几何分量 —— **直接沿用并引用，省一轮调参**。
  4. `aligned`：`vlm-prefix ⊕ obj-rel` 经一张 2 层 MLP `h_b(·)` 映射到共享空间。
- **对齐图的训练协议（对抗 R2-B5 的泄漏质疑）**：
> 对齐映射使用弱配对数据训练——即两个本体执行同一任务，但数据是彼此独立采集而非一一对应的——训练任务集合 `T_align` 与评测任务 `T_eval` 不相交。主表中的所有数字均采用 held-out-task 协议；domain 内数字仅作为上界展示。
- **损失**：同任务同阶段的跨本体样本为正对，InfoNCE。参数量 <2M，训练 <\todo{} GPU-minutes（这个数字进 §V-F 的 admission cost 表）。

## 3.4 III-D. 读出：一个接口，四个层级（**本文的机制增量**）

**统一接口（这是同时解决 R1-B2 与 R1-B7 的关键设计）**：
> 每一层都会在 injection 之前被解码到 reader 的动作空间：
> ① → 冻结 VLM 在 reader 当前图像中对摘要重新 grounding，并输出 subgoals → ②；
> ② → subgoals 被实例化为物体系下的 waypoints → ③；
> ③ → 物体系下的 deltas 被变换到 reader 的任务坐标系中，并被求解为 joint-space chunk（IK / differential IK）→ ④；
> ④ → 直接使用。
> 因此，四个层级都进入同一 aggregation 与同一 intermediate-state injection，从而在保持 injection 路径固定的同时，只改变抽象层级。

**回退读出**：同本体优先 ④；跨本体从 ④ 起逐级上移，直到解码成功且 IK 可行。**回退到哪一层本身是实验读数。**

**与 Retrieve-then-Steer 的边界声明（英文一句，正文原文 —— 已按 v5 §2.3 加强）**：
> We adopt unchanged from [R-t-S] the aggregation, the intermediate-state initialisation of the flow sampler, the confidence-adaptive guidance strength, and the abstain-and-fall-back rule, including its component-aware aggregation of Euclidean, $SO(3)$ and gripper components. We note that intermediate-state injection with a soft per-element mask also has an industrial implementation in GR00T N1.7's real-time chunking (`vel_strength`, exponential ramp), which further supports our position that the injection mechanism is not the contribution. What is not from that method, and what we describe here, is the decoding path that maps entries at different levels of abstraction into a common action-space prior, **and the change of coordinates that precedes aggregation for bimanual entries** (Sec. III-D).

**★ 双臂条目的坐标变换（本文第二项机制增量，必须写清正当理由）**：
> R-t-S 的 component-aware aggregation 对**拼接后的双臂动作向量逐分量**做相似度加权平均。**K 条候选 chunk 的逐坐标平均，其相对变换一般不等于各候选相对变换的任何保约束平均**——即在 retarget 之前，聚合本身就可能破坏双臂闭链/接触约束。
> **修法**：先把每条候选从 (left, right) 转到 `(T_abs, T_rel)`，对 `T_rel` 用更紧权重或最近邻回退（与其对夹爪冲突的保守回退同构）、对 `T_abs` 自由聚合，再映回。**它改的是聚合前的坐标，不是注入路径，不违反"注入机制沿用 R-t-S"的诚实声明。**
> **★ 但正当理由只能建立在 IK 可行性上**：实测逐臂独立 retarget 的 `T_rel` 保持误差中位仅 **0.6 mm / 0.0°**，可忽略——**所以不能拿"约束破坏"当理由**。且"协同 +10 pt"这个数字目前是搜索预算伪影（协同侧拿到 15× 的 IK 尝试），**必须 equal-budget 重跑；若增益 <5 pt 或落在 CI 内则删掉这条 Contribution**，换成上面那条纯定性的聚合缺陷。


**derive-on-read 的必要性论证（对抗 R1-B3，本文唯一的辩护）**：
> 层级 ①–③ 都是层级 ④ 与所存储帧共同决定的确定性函数，因此，一个信息等价的 store 完全可以只物化 ④，而在读出时再推导其余层级。区别只在于成本在何处支付。我们对其进行了测量：在读出时推导 ① 和 ② 需要在控制环内进行一次 VLM 调用，并在 chunk 边界处相对于 \todo{Y} ms 的预算额外增加 \todo{X} ms 的每次 retrieval 开销。**如果 \todo{X} 落在预算之内且 success rate 匹配，则贡献 2 将被重述为一个协议/测量贡献，而非表示贡献** —— 这个 fallback 必须现在写好（见 §6 G4 的判定）。

## 3.5 III-E. 写入门控与生命周期

- **写入门控**：episode 结束后按跨本体进度评估器打分，只写 progress-peak 之前的前缀（沿用 Retrieve-then-Steer 的写入范式并引用）。目标工作点：**高 precision 低 recall**（其报告 precision 0.970 / recall 0.678）。**【待确认】VLAC 权重可得性；退路见 §7 优先级 1。**
- **生命周期**：容量上限 + 时效衰减 + **条目级删除**（声明为与 CLARE 共享的性质，不作卖点）。
- **删除后的残留泄漏探针已砍掉**（对显式条目表平凡为真；R2-B13）。若审稿人问，备答：残留通道只有三条（对齐图训练集、ANN 索引码本、按本体对的置信度标定量），我们的对齐图在 `T_align` 上训练、不含部署条目，故不存在该通道。

## 3.6 两个 store 的定义（全文贯彻，对抗 R1-B6 / R3-B5）

| | `S_deploy` | `S_corpus` |
|---|---|---|
| 来源 | 评测期两台机器人自己 rollout + 写入门控 | 数百小时存量遥操语料离线灌入（**curated**） |
| 规模 | \todo{~10³–10⁴} 条 | \todo{**10⁴–N_max**，明写 N_max} |
| 用途 | **P1′ / P2 / P3′ 与全部主结果**；Self-write 主张的唯一证据；在线增长曲线 | **仅**规模、串扰、P4 |
| 图表标题 | 无标注 | 必须写 `corpus-seeded` |

Table I 的 ours 行 Self-write 脚注：`✓ for the deployment store; the scaling study uses a corpus-seeded store.`

> **★ 规模据实收窄**：按实际语料核算，`S_corpus` 稳落在 **10⁴–3×10⁴** 量级，**够不到 10⁵**（家居长时程 episode 均长约 180 s → 40 h/本体 ≈ 800 episode/本体 × 12–18 段 ≈ 10k–14k 条/本体）。**不硬凑 10⁵**：报到实际能达到的 N_max，规模曲线做**对数下采样**（10², 10³, 10⁴, N_max）。


## 3.7 Fig. 2 设计（单栏，0.20 页）

三块横排：**(a) Write** —— rollout → 分段 → 写入门控 → 四层 value + key + body tag 写入 store；**(b) Index** —— 四种 key 构造与对齐图 `h_b`，标注“在 `T_align` 上离线训练一次（trained once, offline, on `T_align`）”；**(c) Read** —— query → top-K → **四条解码路径汇入同一个 `reader action space` 方框** → elite prior → 冻结 flow 采样器中间态注入（灰底标 `[R-t-S], unchanged`）。灰底是图形化的非贡献声明。

**Caption**：
> Fig. 2. **系统概览。** 一个 rollout 被分割为若干运动片段；写入门控仅接纳经进展验证的前缀，并将每个被接纳的片段以四个抽象层级、连同一个与 body 无关的 key 和一个 writer tag 存入 store。读取时，在任意层级检索到的条目都会被解码到 *reader* 的 action space 中，因此所有层级共享同一条注入路径。灰色阴影块直接采用自 [R-t-S] 且未作修改。

## 3.8 Algorithm 1（伪代码，0.12 页）

```
Algorithm 1: 面向 reader body b 的部署循环（policy 冻结）
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
| D1 | 片段分割 | **★ 双轨**。轨 A（**零依赖，立即可做**）= 夹爪 open/close 事件 ∪ **双臂任务系**速度过零 ∪ 固定时长上限（如 8 s），受最小片段长度约束；轨 B（感知就绪后）= 补约束坐标里程碑（铰链角 Δθ / 弧长 Δs / 重抓事件） | **轨A 1 周 / 轨B 1 周** | 轨A 是 | **禁止让主线任何一个数等待轨 B**；顺带报"轨A vs 轨B 对 precision@k 的影响"当一行便宜 ablation |
| D2a | 铰链一次性标定 | 固定家电，标定夹具 + 尺量一次 | **0.5 周** | 是（confirmatory） | **★ 若家电采集期间未移动过，可追溯标定**——存量数据零重采变③层可用 |
| D2b | DLO 拉头 + 刻度带 | 抓后夹爪位姿代理 + 轨道弧长 | **3 周** | 是 | — |
| D2c | 叠衣语义关键点 | 检测器 + Cloth Funnels 式规范化前缀 | **4 周** | 是（F 族） | **MVP 中砍**（叠衣降 exploratory） |
| D3 | 锚点系与任务坐标系 | 由 D2a/b/c 输出定义 anchor frame；③ 层轨迹变换 + `(T_abs,T_rel)` 拆分 | **2 周** | 是 | — |
| D4 | ① 层生成 | 冻结 VLM 对首末帧 + 指令生成摘要；**禁止写入者像素坐标**；oracle 版另做 | **2 周** | 否 | 批处理离线跑 |
| D5 | ② 层生成 | 由 ①+D2 构造子目标序列（**两套 anchor 词表**）；oracle 版由演示脚本 | **1.5 周** | 否 | — |
| D6 | key 编码器 ×4 + 对齐图 | 冻结编码器封装 + InfoNCE 训练脚本 | **2 周** | 是 | — |
| D7 | store + 索引 + 生命周期 | 条目表、暴力 cosine（10⁴ 条足够）、FIFO+时效、删除 | **1 周** | 是 | **不做 ANN**（省 1 周，且删掉了一个空实验） |
| D8 | 读出与注入 | 四条解码路径 + retarget/IK + **双臂 (T_abs,T_rel) 聚合改造** + Eq.(6) 注入 | **3 周** | 是 | **与 R-t-S 复现共用同一份代码**（省 4 周） |
| D9 | 写入门控 | **VLAC-8b 可得（MIT，327 star，HF 可达）** + progress-peak 截断 | **1–2 周** | 是 | **HELP / VLAC-Cut 已实现 progress/idle/failure/recovery 分段**，D9 大概率能压到 1 周 |
| D10 | 仿真 harness | 同一 MuJoCo 场景内换 **AgileX 官方 piper / piper_x / piper_h / piper_l 四套 URDF**（MIT，已下载至 `RAL2027/kinematics/`）+ 2×2 因子评测 | **3 周** | 否（G3a 后可砍） | 不进正文则只做 key 侧离线分析（省 2 周） |
| D11 | 真机基础设施 | 双平台评测自动化、成对同 init/同噪声 rollout、复位、日志 | **4 周** | 是 | — |
| D12 | 弱配对数据采集 | 10–12 任务 × 30 episode × 2 本体 | **2–3 周**（31 机器人小时） | **是（最被低估的一条）** | 第 1 周就启动；**用户已确认可随机启动采集** |
| **D13** | **★ PiperX 侧 openpi 移植** | policy input/output 类、norm stats、**按偏置腕重写 pinocchio+casadi FK/IK**（官方那份 28 KB 的 `piper_IK-ros2.py` 是按 Piper 硬编码的）、piper_sdk 驱动、相机标定 | **3.5 周** | **是（单点故障）** | **第 1 周设 FK 一致性硬验收**：20 构型，位置残差 <5 mm、姿态 <2°。**不通过就不要往下写任何 policy 代码** |
| **D14** | **★ 8 个自动判据的夹具与传感** | AprilTag / 簧片开关（¥5）/ 印刷刻度带 / 俯视 RGB-D | **3 周** | 是，但**不依赖策略与记忆库，9 月即可开工** | 闭合缝分割与包内物体检测**改人工复核**（各约 100 trial × 5 s），砍掉两套视觉工程 |
| **D15** | **★ demo 录制基础设施** | 第三方电影机位 + **rollout 元数据与视频帧同步落盘** + 角标数字录制时烧进日志 | **0.5 周** | **是（第一天就要做）** | 不做则 §4.10 第三段（harm 案例）永远拍不出来——它完全依赖能从日志检索出 `base 成功 & ours 失败` 的成对样本 |

**★ 一个必须先做、成本半天的前置**：把 `pi0.py::sample_actions` 的 `jax.lax.while_loop` 展开为 Python for 循环 + 同 seed 数值一致性检查。**已核源码**：carry 就是 `(x_t, time)`，`x_t` 即 flow 中间态，`num_steps` 默认 10。**排在所有记忆库工程之前**——这是注入机制的最小可行验证。


**合计 ≈ 26.5–29.5 周 ≈ 6.2–6.9 人月的纯工程**，另加实验执行 1.5 PM + 分析画图 1.0 PM + 写作 1.0 PM + 基座微调与调试 1.5 PM ≈ **11–12 人月**（不含额外 baseline 复现）。详见 §5.2。


---

# 4. 第 IV/V 节：实验（Experiments）

**预算：§IV 0.40 页（setup）+ §V 2.05 页（results）。**

## 4.0 实验问题 → 表图映射

| 问题 | 交付对象 | 页数 | 若砍到 4 个图表时的去留 |
|---|---|---|---|
| reader swap 的检索代价（C1） | **Fig. 3** 检索质量（直方图 + precision@k/AUC） | 0.16 | **保留（第 4 位）** |
| 迁移率谱系（P1, C2） | **Fig. 4** 四层 × {cross, same} × {oracle, auto} | 0.20 | **保留（第 2 位）** |
| 跨本体损失分解（P2, C4） | **Fig. 5** oracle 阶梯（五级四差） | 0.18 | **保留（第 3 位）** |
| 主结果 + 方向不对称（P3, C3） | **Table III** 真机主表（含 injection rate / harm rate / 成对 Δ） | 0.28 | **保留（第 1 位）** |
| 控制与消融 | **Table IV** 6 个控制 arm + 共享池三条件（P4） | 0.20 | 砍到 4 个时移出正文 → 补充材料 |
| 协议与 baseline | **Table II** | 0.15 | 砍到 4 个时并入正文文字 |
| reader #3 admission cost | 正文 3 行 + 2 个数字 | 0.05 | 保留（文字） |
| 时效性交叉点（E5） | 正文 2 行 + 3 个数字 | 0.04 | 保留（文字） |
| 规模与串扰（C4 后半） | 正文 2 行 + precision@k vs 规模的一句话 | 0.04 | 保留（文字） |

**图表优先级（砍到 4 个留哪些）**：`Table III > Fig. 4 > Fig. 5 > Fig. 3`。Fig. 1 与 Fig. 2 不参与这个排序（teaser 与系统图在 RA-L 是刚需）。

## 4.1 仿真设计（**不进正文**，只作内部 go/no-go 与离线分析）

**决策依据**：LIBERO↔RoboCasa 作为双本体设置时，会同时改变 body / scene / assets / 相机 / 任务语义 / demo 生成管线 / 动作维度等至少 8 个变量，因此 body 主效应不可识别（R2-B2）。

**必须做的 2×2 因子设计（若做，就必须四格齐）**：

| | scene S1 | scene S2 |
|---|---|---|
| body A | SR(A,S1) | SR(A,S2) |
| body B | **SR(B,S1)** ← 因果估计量 | SR(B,S2) |

- **落地路径**：**在同一 MuJoCo 场景/物体/相机位姿下替换第二个机器人模型**——标的改为 AgileX 官方 `agx_arm_urdf` 的四套 Piper 家族 URDF（**MIT 许可，已下载至 `RAL2027/kinematics/`**）。这条从"可行性待验证"升级为"**已有现成资产**"。可行性用 ≤1 周验证（**G3a**）。
- **★ ④轴必须改报二维 (位置误差, 姿态误差)**：Piper→Piper-H 与 Piper→Piper-L 的朴素复制**姿态误差同为 0.0°**（同架构，末端朝向完全一致），位置误差分别 0.98 cm 与 9.41 cm——**在④轴上它们是同一个点**，一维报法会画出假曲线。修正后这条阶梯反而更有力：**0°（同架构，任意尺度）vs 82.8°（异架构）——这个对比本身就是"架构差异 ≠ 尺度差异"的证明。**
- **不可行则**：仿真退出正文，只保留 key 侧离线分析（Fig. 3 的一部分可先在仿真上跑），并在 §IV 用一句话说明这一决定。
- **headroom 的制造方式（对抗 R2-B12）**：**不用样本饥饿**。保持每任务演示量足以让基座在训练分布内表现强劲（否则写入门控没有成功轨迹可写，memory store 近乎为空，测到的将是写入率而非迁移率），改为在**评测端**施加扰动。
  - **★ 但必须分族限定**（施工图原来那句"不需人为制造 headroom"只对 F 族成立）：**F 族不需要**——R-t-S 在同款双臂 PiPER 同任务上实测 39–48%，正落在窗口；**D 族必须做**——否则天花板（基座 SR 会落在 70–90%，20 对里可能只有 1–2 个不一致对，对 McNemar 零贡献）。具体：门初始开合角 `[0°,25°]` 均匀随机、家电本体位置 ±8 cm / ±10° yaw 随机、加 1 个遮挡干扰物；pilot 里把每个 D 变体的基座 SR 调进 **25–65%**。

## 4.2 真机设计

### 平台与任务集分层（对抗 R2-B8）

| 层 | 定义 | 任务数 | 用途 |
|---|---|---|---|
| **S 层** | 两体皆可执行 | **12** | **唯一的 confirmatory 端点** |
| **R 层** | 仅 PiperX 可（**reach 受限**，跨度超 Piper 626 mm 臂展） | 2 | scope 说明 + 定性视频 |
| **W 层** | 仅 Piper 可（**腕部 roll 受限**，需 >±89° roll；Piper j4 ±100° vs X ±89°） | 2 | scope 说明 + 定性视频 |

> **R/W 层比原 M/F 层更有价值**：它们是**双向**的单侧任务，直接图示化"两个工作空间**互不包含**"（体素 **IoU=0.528**，Piper 被 X 覆盖 72.2%、X 被 Piper 覆盖 66.3%），在任务层面证伪"子集"直觉——正是旧 P3 机理死掉的原因。
> R 层例：R1 折叠大号床单；R2 够到深式微波炉腔体后壁取物。W 层例：W1 拧瓶盖式大 roll 动作；W2 衣架挂取。

### S 层的 12 个变体（任务粒度 = **族 × 物体实例 × 目标位形**，必须在 §IV 主动交代）

| # | 变体 | 族 | exec+复位 | 判定 |
|---|---|---|---|---|
| F1–F4 | 叠短袖 T 恤 / 长袖衬衫 / 长裤 / 毛巾四折 | F | 3.5 min（**含拒收重做后约 4.0 min**） | rubric + 盲评 κ |
| F5 | **叠 T 恤至指定外接矩形**（塞进给定抽屉） | F | 3.5 min | **全自动** |
| D1–D4 | 开/关微波炉门、开/关洗衣机门（含卡扣与胶条压合） | D | 0.6 min | **全自动** |
| Z1–Z3 | 拉开 / 拉合 / 放物入包→拉合 | Z | 2.1 min | **全自动** |

**主分析同时在「全 12 个」与「客观 8 个」上跑**，作为稳健性检查——**论文主结论不建立在最有争议的判据上**。

> **★ 但存在一个必须先解决的结构性缺口**：5 个任务族撑不起"12 个评测任务 + 不相交的 `T_base`"，且 E0 与"基座 SR 落在 20–60%"在只有 3 个族的结构下**近乎不相容**（折 T 恤 vs 折长裤基本是同一技能）。**两条出路都要走**：
> 1. 把 4 个门变体换成 **4 台不同铰接家电**各 1–2 个变体（微波炉 / 洗衣机 / **抽屉（prismatic，不同约束类型）** / 柜门），把 3 个拉链变体换成 **3 个不同的拉链包**。硬件成本几百块。
> 2. **增加族数 3→5**（加抽屉、加双臂交接/放置），总任务数保持 12–14，**n_eff 从约 4 抬到约 7**。
> **必须在 G3b 冻结切分前做完。**

**S 层任务必须包含 ≥3 个"语言不可表达"任务**（对抗 R1-B4，全篇唯一能够结构性击败 instruction-only 对照的实验）。**判据**：同一句自然语言指令对应多条成功轨迹分布，且它们的成功率显著不同。实取 4 个：

| # | 任务 | 为什么语言表达不了 |
|---|---|---|
| **L1** | **F5 叠至指定外接矩形** | "把衣服叠好"不指定折线位置、折叠顺序与目标尺寸。要塞进给定抽屉，折线必须落在特定位置——这是**连续几何量**，用语言表达需要念出坐标，而坐标是写入者相机系的量，**与 body-agnostic 直接冲突** |
| **L2** | **Z2 拉合时的卡阻恢复节律** | 拉头被布料咬住时须回退约 1 cm、由稳定臂重新张紧、再以特定速度推进。**接触/速度剖面，不是语义步骤**。（无力传感器时，卡阻判定改为**指令位置与实际位置偏差超阈**） |
| **L3** | **F1/F2 双臂张紧-扫掠的相位差** | 一臂保持张力、另一臂扫掠，两臂间存在**相对位姿轨迹 `T_rel(t)` 与时序偏置**。**语言无法表达一条连续的相对位姿轨迹。★ 这是硬件变更带来的净收益——单臂方案不可能有这一类** |
| **L4** | **D4 关洗衣机门的胶条压合剖面** | 门接触胶条后需一段特定的减速-加压-越过卡扣的力/速剖面 |

**Intro ¶5 的措辞相应收窄**：`compared on a task set both bodies can execute`，并主动声明这是 embodiment gap 的**下界估计**。

### ★ 主端点：拆成两个预注册主端点（co-primary，Bonferroni 各 α=0.025）

> **核心问题一句话**：**这个任务集里，配对有效的任务没有统计头room，有统计头room的任务配不了对。**
> 门族初始状态完全可复现但会天花板；叠衣族有真实头room 但**一件衣服的初始褶皱物理上不可复现**——而 McNemar、harm rate、成对 Δ 三个全文贯穿的量**全部建立在 matched initial state 上**。

**(P-rigid)** D + Z 共 7 个变体，**成对 McNemar**（同初始状态 + 同 flow 噪声种子 ε）。D 族必须人为制造 headroom（见 §4.1）。

**(P-deformable)** F 共 5 个变体，**放弃 trial 级配对**，改**分层随机化**：每次重置后由脚本随机分配到 base 或 ours，用初始状态难度协变量分层；主量为 **0–4 分进度分的 stratified 均值差**；检验用**任务层 cluster bootstrap**。

**HR 的定义随之分裂**（§IV 必须明写两者**不可 pooled 成一个数字**）：D+Z 用 `HR = n10/n`（per-trial）；F 用 `HR_dist = P(ours 失败|层) − P(base 失败|层)`。

**★ 'matched initial state' 在可形变物上的可操作定义（三件事，缺一不可）**：
- **(a) 容差化配对 + 拒收重做**：桌面印衣物轮廓模板；重置后拍俯视 RGB-D，只有 **mask 与模板 IoU ≥ 0.90 且主轴角差 <10° 且褶皱能量代理落在预设带内**才算合法初始状态，否则重做。**把达成的 IoU 直方图报进补充材料——让配对是测量出来的，不是假设出来的。**
- **(b) A/A 噪声地板控制（不可砍，约 2.3 robot-hours）**：选 1 个 F 变体，**base 对 base** 跑 20 对，测不一致率 `π_d^AA`。**这就是 McNemar 的噪声地板**。理由：在 SR≈50%、初始状态方差大的情形下，**纯噪声就能给出 20–25% 的 n10**，把它写成 "memory-harm rate 25%" 是硬性误述——而 HR 是 Abstract 里主动宣称的诚实性指标。
- **(c) 条件污染审计**：base 组与 ours 组的初始 IoU / 褶皱能量分布做 t 检验。
- **另必须明写一条限制**：matched sampler seed ε **只控制第一个 chunk**，首个动作分叉后轨迹即发散——**seed 匹配对长时程任务是装饰性的**。刚体任务同样成立，**主动写出来比被问出来强**。

### ★ 效力：`n = 785·π_d`，π_d 预注册并 pilot 实测

McNemar 的效力由**不一致对数量**决定，不由 n 决定：
```
n = (z_{α/2}+z_β)² · π_d / δ²  =  785 · π_d      (δ=0.10, α=0.05, 1−β=0.8)
```
- `π_d=0.30` → n≈240（**这正好反推出施工图原来继承的那个数，但它从未被声明过**）
- `π_d=0.50` → **n=392 对/arm** → 主端点从 48.9 h 涨到 **79.9 h**，总预算 152 → **约 183 h**

**执行**：每族选 1 个变体各跑 15 对（可与 A/A 控制合并采集），读出族别 `π_d`，**在冻结主端点之前**决定加 trial 还是降效力目标。若 `π_d^F > 0.40`，F 族强制走 (P-deformable) 的连续型进度分。**§4.7 预算表的每一行都应标注其隐含 π_d。**

### P3′ 的检验方式（三级，力度递增）

**旧的任务级符号检验 n=12 是伪重复**：F1–F5 共享同一套关键点前端与同一折叠技能；D1/D2 是同一台微波炉的两个方向；Z1–Z3 是同一个包同一条拉链。族内相关 ρ≈0.6、族规模 m≈4 → **n_eff ≈ 4.3**；全同向时符号检验单边 p 从 **0.000244（n=12）** 变成 **0.0625（n=4）——不显著**。

1. **方向检验**：**族级** cluster 重抽样（cluster = **族**，不是任务）或带族随机截距的混合效应模型。**报族聚类的 p 与 naive n=12 的 p 两个数，摘要里只准用前者。**
2. **★ 排序检验（本设计的核心增量）**：逐任务的**离线 φ 差值** 与 **实测 Δ 差值** 的 **Spearman 秩相关**（族级 cluster bootstrap CI）。若显著，主张升级为 **"一个离线运动学统计量可以预测在线迁移不对称，无需部署"**——这比"存在不对称"强一个量级，且对系统集成者有直接价值。
3. **机理确证对照（替代已失效的"锁底盘"）**：把双方写入条目都限制在**两者工作空间的交集核**（体素 IoU 的 52.8%）内重跑。若不对称性消失 → 机理坐实为限位包络覆盖率。**免费**（只是对条目做一次过滤）。

**另外三条一起上**：用 **ordinal 进度分消除 tie**（D 族天花板时两方向 Δ 常恰为 0，符号检验**静默丢弃 tie**；**必须为 D/Z 也预注册 ordinal 阶梯** approach/grasp/partial-actuation/complete，并**明写被丢弃的 tie 数**）；**提高族数 3→5**（真正决定效力的量）；从 pilot 估出族内 ρ 并把 n_eff 计算写进 §IV。

### 其余 arm（exploratory，表中加标记，不进 Abstract）

- 四层 value sweep：**4 个任务 × 15 trials × 4 层 × 2 方向**
- **8 个**控制 arm（含新增 A7/A8）：4 个任务 × 15 trials
- 重实现的 Retrieve-then-Steer（同本体）：12 任务 × 15 trials × 2 本体
- **reader #3（单臂模式）admission**：6 任务 × 15 trials × {base, ours}
- E5 时效性：3 个场景变更 × 15 trials × 3 条线


## 4.3 Baseline 表（含开源可得性与复现成本）

**真机成功率表只保留 4 个条件**（对抗 R2-B11 / R3-B7）：

| 条件 | 角色 | 可得性 | 复现成本 | 是否进真机表 |
|---|---|---|---|---|
| frozen base, no memory | 下界（成对 baseline） | 自有 | 0 | **是** |
| **ours @ L\*** | 主方法 | 自有 | — | **是** |
| **ours @ ④**（退化对照） | 显示分层的必要性 | 自有 | 0 | **是** |
| **reimplemented Retrieve-then-Steer**（同本体） | **同硬件同任务的直接前作**（不只是"同本体检索 SOTA"）——其附录 D 已在同款双臂 AgileX PiPER 上做 bimanual T-shirt folding（π0.5 42.0→50.0，50 trials/任务） | **代码未开源**（仅匿名可视化链接）；t_min / 评估间隔 Δ / DTW 剔除阈值 / action horizon H **四个值论文未给** | **≈0 边际成本 —— 其注入器就是我们自己要实现的那一份** | **是** |

| ER / 双体数据 co-train | 上界，且是成本论据的唯一实证支撑 | 自有 | 训练 1–2 天 | **是（仅 4 个任务）** |
| derive-on-read | 表示 vs 缓存的对照（R1-B3） | 自有 | 1 周 | **是（4 个任务）** |
| instruction-only | 记忆 vs prompt 的对照（R1-B4） | 自有 | 3 天 | **是（4 个任务）** |
| Dejavu / RECAP / CLARE / VLA-Pro | — | Dejavu 需 RL 训练 EFN；RECAP 需 **paired demonstrations** + Cosmos WAM 骨干；CLARE 无代码；VLA-Pro 有代码但目标问题不同 | 3–4 人月 | **否 —— 只留在 Table I** |

**结构性排除声明（正文原句，比跑一个残废版诚实且省几十机器人小时）**：
> 我们不在我们的硬件上运行 [RECAP]：它要求在固定任务分布上的 paired demonstrations，而我们独立采集的语料并不提供这一点；在其本身并未作出的假设下运行它并不能提供有信息量的结论。[Dejavu] 的 experience-feedback network 需要针对每个 backbone 用强化学习进行训练；[CLARE] 和 [VLA-Pro] 关注的是持续任务获取，而非 reader 替换。因此，我们改为在 Table I 中对这四者进行定位。

**Retrieve-then-Steer 的保真度门槛（必须先做）**：在 π0.5 + LIBERO-10 上复现 92.4 → 94.4（其报 std 0.2–0.8）。只有落在噪声范围内才允许将其用作对照；否则全文降级为 `our reimplementation (four hyperparameters unspecified in the original; set to X, sensitivity in the supplement)`，且**不做“我们优于它”的主张**。
**一句有力的受控对比论据（必须写进正文）**：
> 同本体检索 baseline 与我们共享相同的注入实现，仅在 key 的构造和 value 的层级上不同，因此该比较隔离了“存了什么”。

### 数据切分与泄漏审计（对抗 R2-B5）

- 存量语料三分，**按场景与物体实例互斥**（不是按 episode 随机切）：`base-finetune split` / `store split` / `eval split`。
- **E0**：`base-finetune split` 的任务集与记忆评测任务集不相交，且基座**只用本体自己的数据**微调（无跨本体 co-train，否则 reader 已通过权重读过 writer 的数据）。
- 对齐图：`T_align ∩ T_eval = ∅`，主表只报 held-out 数字。
- **★ 实例 id 纳入互斥维度**：对折叠而言"另一件 T 恤"的关键点语义完全一致，泛化强度很弱。**eval 实例必须在颜色/尺码/材质上与 store 实例明确不同，并在审计行里报出来。**
- **★ 基座能力必须落在 20–60% 窗口**（最容易被忽略却最致命的一条）：>70% → 天花板，注入增益淹没在噪声里；<15% → 写入门控收不到成功片段，库是空的。**这个窗口应当成为 `T_base` / `T_eval` 划分的设计目标**（例：微波炉门进 `T_base`、洗衣机门进 `T_eval`）。→ **新增 gate G3c**：10k 步小规模微调探一次窗口（约半天），**必须早于 G3b 的切分冻结**，否则改不动了。
- **★ 预注册一条排除规则**：pilot 中基座 SR <15% 或 >70% 的 eval 任务，或调整其初始状态分布、或在冻结前替换。**规则必须在看到主结果之前定死。**
- §IV 报一行审计：eval episode 与 store 条目的最近邻 key 相似度分布，以及与 base-finetune split 的重合度。

**★ 必须预备的两个反驳（v5 §5.4）**：
1. *"π0.5 的预训练里本来就有别的机器人的数据，reader 早就通过权重读过了"*——最锋利的一刀。**唯一 airtight 的答法**：所有 arm 共享同一个预训练底座，主端点是**同本体内配对的 Δ**（同 init state、同 sampler seed，McNemar），预训练先验对 base 和 ours 两个 arm 完全相同，**在数学上无法解释 Δ**。**这句话必须逐字写进 §IV，不能只写在 rebuttal 里。**
2. *P3′ 跨的是两个不同的策略检查点*——这是真混淆。对策：每个方向的 Δ 只与**自己的 base** 比，并在主表额外报两具本体各自 base 在 `T_eval` 上的 SR，让读者看得见基线差。


## 4.4 消融清单（Table IV，6 个控制 arm + 共享池三条件）

**控制 arm（缺 random-entry 与 self-prior 这两条，效果可被“注入本身在缩小采样方差”解释掉 —— R2-B9）**：

| # | arm | 排除的替代解释 |
|---|---|---|
| A1 | **random-entry**：从库里随机取条目走同一注入通路 | 增益来自注入本身而非记忆内容 |
| A2 | **self-prior**：用基座自己多次采样的均值 chunk 当 `a_elite`，同一 t0 | 纯方差缩减（注意 t0 实际工作区 ≈0.6，仍保留约 60% 噪声，此解释很有竞争力） |
| A3 | **fixed-t0, no confidence gate** | 分离“门控退回基座”的贡献 |
| A4 | **wrong-body / wrong-task 条目** | 负控制 |
| A5 | **Replay-Only（跨体）**：检索条目 retarget 后开环执行 | 对齐 RECAP 的 Retrieval Only（RoboTwin unseen 26.0 vs 31.5）与 Dejavu 的 kNN-RAG（我们已一手核实：其 kNN-RAG “常常会降低性能”）。**不做会被点名。** |
| A6 | **retarget-feasibility oracle**：真值锚点做 retarget 后单测运动学可行率 | 把 ③ 层失败里属于 IK/标定的部分剥出来 |
| **A7** | **★ ④ + 腕部重解算**（复制 j1–j3、自由重解 j4–j6） | **必须加**。实测该操作把姿态残差从 **82.8° 降到 6.7°**。不加这一行，审稿人会说层④是稻草人 |
| **A8** | **★ coordination-oracle**（把 `T_rel` 作为硬等式约束求双臂耦合 IK，`T_abs` 为软目标） | oracle 阶梯的**第四桶**：双臂协同约束不可满足，是原三桶不覆盖的失败模式。**纯软件、零机器人小时** |

**★ A7 的论证（这反而使论点更强，但必须主动写）**：腕部重解算**需要读者的运动学模型并求解 IK**——那正是层③的定义。所以 **`④+wrist-repair ≡ ③`，层④在跨本体下没有独立存在**。这把命题从"关节动作不能迁移"精确化为：

> **关节动作的可迁移部分恰好等于它的任务空间投影；剩下的部分是本体私有的。**

更强、更可证。**6.7° 不是 0**，它是 j1–j3 语义也不完全对应的残留。


**crossover arm（去注入通路共线，仅仿真/4 任务，R2-B4）**：
- X1：② 内容解码后走 Eq.(6)（已是默认，作为参照）
- X2：③ 内容文本化后走 condition-side prompt 注入
→ 用于估计注入通路主效应并从 P1 曲线中扣除。**若两个 crossover 做不到，P1 措辞必须降级为“层级+通路的联合配置”。**

**共享池三条件（P4，对抗 R2-B15）**：
1. `own-body-only pool`
2. `shared pool, tag-blind retrieval` ← **P4 只在此条件上定义**
3. `shared pool, tag-aware retrieval`（仅在读出时才使用 tag 决定回退层级）
**条目按本体配平**：下采样到 min。理由必须写进 §IV：写入门控 recall ≈0.678 且两体基座 success rate 不同 → 自然写入率必然不等，这是 P3/P4 的隐藏系统性偏差。

## 4.5 P1′–P5 的检验方式与双向预期结论

| | 预测 | 检验方式 | 若成立 → 论文形态 | 若被推翻 → 论文形态（**必须现在写好**） |
|---|---|---|---|---|
| **P1′** | **存在 ℓ\* 使 (a) 同本体 `SR_same(④) > SR_same(③)` 且 (b) 跨本体 `SR_cross(③) > SR_cross(④)`——即两曲线交叉**，预测 ℓ\* ∈ (③,④) | (a) 由 **G0.5** 判定：`SR_same(④) − SR_same(③) ≥ 10 pp`（同本体，成对，McNemar）；(b) 由主端点判定（pooled，族层 cluster bootstrap CI） | Fig. 4 两条曲线交叉；**交叉点本身才是 Fig. 4 的主张**；Title 用 T1 | **(a) 不成立 → 四层谱系框架当场死亡，切 cross-body admissibility framing，不等 G4。** 预注册文本必须现在就写进补充材料 |
| **P2** | 跨本体损失由 retrieval + retargeting 主导，而非 value 不可执行 | **oracle 阶梯（六级五差，见下）** | Fig. 5 四桶加和；C4 成立 | 若 value 项主导 → "检索可救、动作不可救"，重心移到 retarget 与分层回退 |
| **P3′** | **方向不对称由读者的关节限位包络对写者任务盒位姿的覆盖率决定，且可由纯离线运动学统计量 φ 预测方向与逐任务排序** | 三级：族级符号检验 + **Spearman 秩相关（核心增量）** + **工作空间交集核对照** | §V-D 一段 + 秩相关 p 值；主张升级为"无需部署即可预测迁移不对称" | 报 "no directional asymmetry detected at this power" + 效力说明；**并补一句限定性发现**：同形态本体对不存在"工作空间包含"这一在定基↔移动设置中驱动不对称的机制 |
| **P4** | 共享池仅在 value 层级 ≥② 时净正；③–④ 层共享产生负迁移 | 三条件 × 层级的 2×3 表（Table IV），**条目按本体配平下采样到 min** | §V-E 两行 | 若全层净正 → 更好的结果，改写为"在此规模下未观测到跨体串扰" |
| **★ P5（新增）** | **层④失败 ← 运动学架构**（任何固定的、无观测条件的关节空间标定映射的最优残差都超出任务容差一个量级）；**层③失败 ← 关节限位包络**（放宽限位即消失）。**两者不是同一个原因** | **已由离线实测支持**（见下）；真机侧只需确认 FK 一致性 | §V-C 两句 + 一张三档标定表 + 一张限位对照表 | **若真机 FK 残差 >5 mm → 全部离线数字作废，P5 撤回** |

**★ P5 的离线证据（一手复算，脚本在 `RAL2027/kinematics/`）**：

| 标定映射 | 参数量 | 位置残差中位 | **姿态残差中位** |
|---|---|---|---|
| 朴素复制 `q'=q` | 0 | 23.55 cm | **82.8°** |
| 逐关节仿射 `q'=s⊙q+b` | 12 | 11.11 cm | 52.4° |
| **全线性 `q'=Aq+b`** | 42 | **7.10 cm** | **17.8°** |
| sin/cos 提升线性 | 114 | 6.12 cm | 16.0° |

- **拟合出的逐关节尺度** `s = [0.919, 1.010, 0.836, **−0.012**, **−0.064**, 0.638]` —— **j4/j5 的尺度约等于零，最小二乘对腕部关节直接放弃拟合。这是"同名关节语义不同"的直接定量证据（Piper j4 = 腕 roll，PiperX j4 = 肘平面 pitch），应做成一张图。**
- **层③限位对照**：PiperX 真实限位 **80.8%** → 放宽到 ±189°（几何不变）**100.0%**。**架构对层③失败的贡献是 0.0%，全部 19.2 pt 来自限位。**
- **容差扫描（预堵"IK 容差调出来的"）**：0.10 mm/0.06° → 80.5%；1 mm/1° → 80.0%；10 mm/10° → 86.0%。**容差放宽 100 倍只买到 +6 个点，80% 不是容差伪影。这张表必须放进补充材料。**
- **正文的正确措辞**：*任何固定的（无观测条件的）关节空间标定映射的最优残差仍达 7.1 cm / 17.8°，超出任务容差一个量级。* **绝对不能只报 82.8°**——那是 by-construction 的稻草人，被发现后不是数字错误，是诚信问题。
- **⚠️ 前置**：两台夹爪不同款，**上述全部数字需用实测 TCP 偏置重算后才能写进正文**（v5 §1.7 后果 B）。

**oracle 阶梯（P2 的非循环分解，★ 六级五差，全部可自动化 —— 对抗 R2-B10）**：
```
base (no memory)
  ↓ Δ_total
cross-retrieved (normal cross-body retrieval)
  ↓ Δ_key         ← key 侧损失
retrieval-oracle (force the correct writer entry for this task & phase)
  ↓ Δ_limit       ← ★ 限位包络受限（实测 19.2 pt）
limit-oracle     (relax reader joint limits, geometry unchanged)
  ↓ Δ_geom        ← ★ 几何/架构不可达（实测 0.0 pt）
retarget-oracle  (ground-truth anchor & task frame)
  ↓ Δ_coord       ← ★ 双臂协同约束不可满足（A8 第四桶）
coordination-oracle (T_rel as hard equality constraint)
  ↓ Δ_value       ← value 侧跨体不可用
same-body-value  (the reader's own entry for the same situation)
```
- 正例定义来自**我们自己的 (task, phase) 标注**（片段边界天然给出 phase），不做事后人工归因。
- **★ 限定域并明说**：oracle 阶梯**只在 D 与 Z 两族上跑**（锚点是铰链轴与拉链轨道，一次性物理标定，真值免费）；**§V-C 必须明写 F 族 "anchor-oracle not available"**——衣物关键点真值只能靠逐帧人工标注（估 1200–1800 次），这恰恰是该阶梯当初为对抗 R2-B10 而承诺要避免的"事后人工归因"。
- **★ 预注册负值处理**：`Δ_key` 完全可能为负（强制"正确"的写者条目对读者运动学不可行）。**若任一 Δ < 0，禁止画堆叠柱状图**，改画阶梯折线并在正文声明"这是一串干预，不是方差分解"。
- 锚点检测器在两个本体相机上的精度作为**协变量**报出（②③ 共享前端，必须暴露）。

**★ 双臂失败模式必须用预注册的自动 first-fault 规则**：不做事后人工归因。连续记录两臂最小间距（URDF 可算）、`|T_rel(t) − T_rel_ref(t)|`、"一臂张开而另一臂正在扫掠"等事件，**时间上最早触发的事件即为归因类别**。类别至少覆盖：臂间碰撞、`T_rel` 漂移、角色反转、相位失同步、单臂中止。**一个日志脚本的成本，换掉一整轮"你怎么知道是这个原因"的质询。**


## 4.6 指标定义式（§IV 的 “Reporting protocol” 段，约 4 行，全表执行）

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
1. 每个报出 success rate 的格子**必须并列 IR**。任何 arm 若 `IR < 20%`，其 transfer 数字在表里**灰掉并标 n.i.（not interpretable）**。
2. 每个 value 层级**同时报两列**：`gated`（门控开，系统读数）与 `forced`（关掉相似度门与 DTW 过滤，强制注入 top-1，记忆内容读数）。**P1 的主张建在 forced 列上；系统级增益的主张建在 gated 列上。** 这个改动零硬件成本，把 R2-B1 从致命降为可辩护。
3. 有害率**同时报 gated 与 forced 两个版本**（gated 版可被门控刷低，forced 版才是记忆内容的有害性）。
4. **★ 每个报出 success rate 的格子必须并列 reader 自身的 memoryless base SR。** 没有它，读者无法判断某任务的 Δ=0 是"记忆没用"还是"天花板/地板"。这一列同时是 tie 分析的输入。
5. **★ HR 在 rigid 与 deformable 两族上定义不同，明写不得 pooled 成一个数字。**

## 4.7 机器人小时预算算式（进 §IV 正文，约 2 行 + 附录表）

### 单次 rollout 时长（含复位）—— 这是原预算错得最狠的地方

施工图一律用 1.5 min，对家居长时程任务错 2–3 倍。实测量级（**待用存量语料统计确认**）：

| 族 | exec | 复位 | **合计/rollout** |
|---|---|---|---|
| 叠衣 F | 150 s | 60 s（抖开摊平） | **3.5 min** |
| 门 D | 25 s | 10 s | **0.6 min** |
| 拉链 Z | 90 s | 35 s | **2.1 min** |

> **★ F 族的复位时长不能按 60 s 记账**：加了拒收重做之后，期望重置时间是 `60/p_accept`；若 `p_accept≈0.7` 则约 86 s，单次 rollout 从 3.5 涨到约 **4.0 min**。**这与 1.4 失败因子是相乘关系**（1.4 覆盖硬件故障，不覆盖重置拒收），不要混为一谈。

跑一遍任务子集的耗时：**S12**（5F+4D+3Z）= **26.2 min**；**M6**（2F+2D+2Z）= **12.4 min**；**S4**（1F+2D+1Z）= **6.8 min**。

```
robot-hours = Σ_arm ( #rollouts × 该 arm 任务子集的平均分钟 ) / 60 × failure-factor(1.4)
```

| arm | 子集 | rollout 数算式 | 分钟 | 小时（×1.4） |
|---|---|---|---|---|
| **主端点**（2 方向 × {base, ours} 成对） | S12 | 2 dir × 20 pair × 2 = 80 遍全集 | 26.2 | **48.9** |
| 四层 sweep（探索性） | S4 | 15 × 4 层 × 2 方向 = 120 遍 | 6.8 | **19.0** |
| 8 个控制 arm（A8 纯软件不计） | S4 | 15 × 7 = 105 遍 | 6.8 | **16.7** |
| R-t-S 复现（同本体 ×2） | M6 | 15 × 2 = 30 遍 | 12.4 | **8.7** |
| **reader #3（单臂模式）准入** | M6 | 15 × 2 = 30 遍 | 12.4 | **8.7** |
| **★ G0.5 交叉点 gate** | 1F+1D | 200 条条目离线 + 40 真机确认 | — | **2.3** |
| **★ A/A 噪声地板控制（不可砍）** | 1F | 20 对 base-vs-base | 4.0 | **2.3** |
| **★ π_d pilot** | 3 族各 1 | 3 × 15 对 × 2 | ~2.1 | **3.5** |
| E5 时效性 | D+Z only | 3 场景 × 3 线 × 15 | ~1.35 | **4.2** |
| ER / co-train 上界 | S4 | 15 × 2 = 30 遍 | 6.8 | **4.8** |
| **评测小计** | | | | **≈ 119** |
| **★ demo 增量**（§4.10.6） | — | 五段里三段纯复用主实验素材 | — | **1.8** |
| D12 弱配对采集 | S12 | 12 任务 × 30 ep × 2 本体（×1.2 重拍） | 2.18 | **31** |
| **总计** | | | | **≈ 152 robot-hours** |

### ★ 一个错误假设被推翻带来的红利（必须改写正文）

> 施工图原文："跨本体 trials 需要进行物理本体更换与复位，因此其单位成本高于同一本体 trials"

**这在新硬件下是错的。** Piper 与 PiperX 是**两套独立台架**，reader swap 只是换台跑，**没有任何物理拆装，且两台可并行运行**。正文改写为：

> Two platforms run in parallel; a cross-body trial costs the same as a same-body trial. We report robot-hours alongside wall-clock.

**wall-clock**（按 **3 productive h/day/台**，非 5——家居长时程 + 布料人工复位 + 每台需一名操作员）：152 h / 2 台 = 76 h/台 ÷ 3 = **约 25 个工作日/台 ≈ 5 周/台**。
**唯一的串行依赖**：写者必须先产出条目，读者才能评测 → 分两相：**相 1 双台并行写入**，**相 2 双台并行读取**。

### 若超预算，按此顺序砍

1. E5 时效性（−4.2）→ 降级为 discussion 一句
2. ER/co-train 上界（−4.8）→ 但这是"E0 这条主张的标价"的唯一实证，**尽量保**
3. reader #3（−8.7）→ 会把 R1-B5 变回未解决风险，须在 Limitations 明写
4. 四层 sweep 从 4 任务降到 3（−4.8）
5. 主端点 trials 从 20 降到 15（−12.2，效力从检测 10 pp 降到约 12 pp）

**绝不砍**：G0.5、A/A 控制、π_d pilot（三者合计 8.1 h，是全部统计主张的前提）；S 层任务数不得低于 12；**族数不得低于 4**。


## 4.8 §V 的叙述顺序（2.05 页怎么用）

1. **V-A Reader 更换成本**（0.30 页 + Fig. 3）：四种 key × {same-session, cross-session/scene, cross-viewpoint, cross-body} 的分布 + 重标定后的 precision@k / AUC。**caption 必须写死**："γ_sim is re-calibrated per condition; the 0.9992 default of [R-t-S] is a coverage/quality knob tuned on LIBERO-10, not a property of the representation."
   **预写的 fallback 段落（若重标定后跨本体 precision 显著高于 chance）**：结论改为“key 侧是可恢复的，但需要一个 alignment map，而其成本我们会报告”—— 这反而直接支撑我们的对齐图，叙事更强。
2. **V-B 可迁移性谱系**（0.45 页 + Fig. 4）：四层 × {cross, same} × {oracle content, automatic content}，gated 与 forced 两列；derive-on-read 与 instruction-only 并列。
3. **V-C 损失流向何处**（0.35 页 + Fig. 5）：oracle 阶梯三桶。
4. **V-D 方向性**（0.20 页）：P3′ 族级检验 + **Spearman 秩相关（离线 φ 预测在线 Δ）** + **工作空间交集核对照**（把双方写入条目都限制在体素 IoU 的 52.8% 内重跑；不对称若消失则机理坐实）+ 两个 writer 的条目质量统计（条目数、门控分分布、任务覆盖）。
5. **V-E 共享、规模与危害**（0.35 页 + Table IV）：共享池三条件、corpus-seeded 规模下的 precision@k 下降曲线与跨体误检率、harm rate。
6. **V-F 接纳一个 reader 的成本**（0.20 页）：reader #3（单臂模式）的 admission cost 三列实测表（paired episodes / GPU-minutes / wall-clock）vs 同 pair 上的 target 侧微调；E5 时效性交叉点三条线。
7. **主表 Table III 贯穿 V-B/V-D**（0.28 页）。

## 4.9 必须在 §IV 主动交代的**七**件事（各一句，少任何一句都会在 rebuttal 变成一轮质询）

1. 两个基座策略都在部署前用存量数据微调过，且微调任务集与记忆评测任务集不相交（E0），**且各自只用本体自己的数据**（无跨本体 co-train）。
2. `S_deploy` 与 `S_corpus` 的条目数、episode 数与来源；**规模写实际 N_max，不硬凑 10⁵**。
3. **两个平台并行运行，跨本体 trial 的单位成本与同本体相同**；同时报 robot-hours 与 wall-clock。
4. 单 checkpoint、单策略种子；真机做不了 3 seeds，用**族层 bootstrap** 代替 seed 方差（主动说明比被问强）。
5. **★ 每条自动判据在约 50–100 个人标样本上报一次 precision/recall**，与 VLAC 写入门控的标定**用同一批数据、同一套流程**。（"12 个中 8 个全自动"偏乐观：F5 依赖目标矩形标定、Z1–Z3 依赖模板匹配与分割阈值、D1/D3 依赖 AprilTag 不被门体自遮挡。）
6. **★ 初始状态配对容差与达成的 IoU 直方图 + A/A 噪声地板 `π_d^AA`**；F 族的配对只能称 "state-matched to within a pre-registered tolerance"，**绝不写 identical initial state**。
7. **★ ④层存物理单位，读出时由读者用自己的 norm stats 重新归一化**——防止④层跨体失败中混入纯归一化失配这个平凡混淆。**必须进正文，不是实现细节。**

**另必须主动写的三条（可并进上面或单列）**：
- **环境非平稳性**：拉链数百次开合后齿列磨损、T 恤折 300 次后形成固化折痕——**等于环境本身携带了"记忆"，会系统性偏向后跑的那个条件**。对策：每变体 **≥3 件物理相同实例**轮换并记录 instance id；配对内随机化先后；**漂移审计（一行，免费）**——把 base arm 的成功/进度分对 trial 序号做回归，报斜率与 CI。
- **盲评**：κ 度量 reliability 不是 validity。标注者只看末帧、文件名随机化、条件剥离、base 与 ours 交错混排；每批嵌入约 20 张 anchor items；**至少一名标注者不是本文作者且不知道假设**；**κ 报在盲评批次上**；**重置者也要盲**（脚本只在重置完成后才抽取条件）。
- **F1–F4 判据的一处必改**：施工图写的"中心厚度 ≥ k × 单层厚度"**物理上测不出来**（T 恤单层 0.5–1 mm、四层 2–4 mm，消费级深度相机 0.6 m 上 RMS 噪声 2–5 mm，布料低纹理更差）。**改用面积判据**：`A_final ∈ [A0/2^n × (1−τ), A0/2^n × (1+τ)]`，`A0` 为摊平俯视 mask 面积、`n` 为预注册折叠次数、`τ≈0.20`。**"揉成一团"被下界拒掉，折不到位被上界拒掉，且对深度噪声免疫。**

## 4.10 ★ 真机 demo 规划

> **定位**：demo 不是用来展示成功率的——表格已经干了那件事。**demo 的唯一职责是让一个怀疑的审稿人在 15 秒内相信一件他本来不信的事。**
> 素材**必须在主实验跑的同时录**，不另开一轮（见 §4.10.6）。

### 4.10.1 先确定"什么是没人拍过的"

| 已有工作的视频拍了什么 | 我们不能重复的 |
|---|---|
| R-t-S：冻结策略 + 记忆让**同一台**机器人变好（**同款双臂 PiPER、同样冻结 π0.5、叠 T 恤 42.0→50.0**） | ❌ "记忆让机器人叠衣服变好"——拍这个等于自证增量 |
| RECAP：往检索池加演示、不重训就会新任务 | ❌ "不重训学新任务" |
| RAM：检索 affordance 迁到别的机器人，**但库是离线静态第三方语料** | ❌ "跨本体读一个预先建好的库" |
| GR00T：跨本体，但**要更新参数** | ❌ 任何含训练步骤的迁移 |
| MimicDroid / RoboTTT / Instant-Fold：人类视频 → 机器人，**用完即弃** | ❌ in-context 单次演示 |

> **没有一个拍过：一台机器人在自己部署中产生的经验，被另一台机器人读走，中间没有任何重训。**
> **这就是那一枪。全片的结构都围绕它。**

### 4.10.2 分段脚本（总长约 3 分钟）

| 段 | 画面 | 角标 | 它证明什么 | 前置条件 |
|---|---|---|---|---|
| **一（40 s）唯一真正重要的那一枪** | Piper 反复尝试某变体，失败 2 次、第 3 次成功 → **不切黑场**推到 PiperX，同一变体同一初始状态 → 先跑无记忆基座（失败）→ 再跑读取记忆（成功） | `entry written · 0 parameters updated` + **从 Piper 成功那刻开始走的真实墙钟计时器** | 计时器停在几十秒。**这个数字是全片最有说服力的东西**——"跨本体迁移"在所有其他论文里意味着几小时到几天的重训 | 需 Piper 基座 SR 落在 30–50% 的变体（失败 2 次再成功是自然发生而非摆拍）；写入门控在线跑通 |
| **★ 一的加强版** | Piper 成功后**断电、推出画面**，再让 PiperX 读 | — | 同时干掉"两台是不是在实时通信"，并把"**记忆比写它的身体活得久**"变成字面画面 | — |
| **二（50 s）这才是论文的贡献** | **同一条条目、同一初始状态、同一台 PiperX，只换读出层级**：④直接关节回放 → 姿态歪掉、抓空、失败；③锚点系接触点运动 → 成功。并排 | 层级标签 | 把**交叉点**从一条曲线变成**看得见**的事：同一段经验在一个层级上是废的、在另一个层级上是好的。**没人拍过，因为没人分层存** | **G0.5 已确认交叉点存在**；④层回放必须用**物理单位**，否则失败会混入纯归一化失配这个平凡原因 |
| **三（30 s）诚实本身就是差异化** | 一个**读了外体条目反而变差**的案例 → 置信度门控挡下 → 回退基座 | harm 标记 + IR | 三件事同时兑现：Abstract 主动宣称的 harm rate；**"相似度门看不见可执行性"**；以及"我们知道它什么时候不该跨"。**大部分 demo 不敢拍失败，审稿人看到你敢拍，对前两段的信任度会明显上升** | **要先"打捞"到这样的案例**——全片唯一需要专门找的素材 |
| **四（30 s）机理而非现象** | Piper→PiperX 成功；反向同任务失败。**失败瞬间叠腕关节角度条**，显示撞到 Piper j5 的 ±70° 限位 | 字幕 `the reader's wrist envelope, not the workspace size` | 把 **P3′** 从一个 p 值变成**看得见的物理原因**；同时预先堵掉"你们的 gap 就是工作空间大小差异"（已被 IoU=0.528 证伪，但视频比文字快） | 需挑一个真会触限的变体——由**离线 per-task φ** 预先筛出候选 |
| **五（20 s，可选）换读者的代价** | **单臂模式读者**读双臂条目：③④结构性不可读 → **分层回退**到②层子目标序列 → 仍能完成，只是慢、精度低 | 回退层级标出 | 兑现 "admitting a new reader costs \todo{N} paired episodes and no policy gradient"；也是 D6 通过 own-task-competence 判准的可视证据 | — |

### 4.10.3 任务选角

| 任务 | 派什么用场 | 理由 |
|---|---|---|
| **拉链（Z）** | **第一、二段主角** | 成败**二值可见**（拉链开没开一眼看到）；时长适中（2.1 min）；③层的**弧长锚点可以直接在画面上叠一条进度条** |
| **门（D）** | 第四段方向不对称 | 腕部限位的故事最干净；开合角可视化容易；单次仅 0.6 min，可连拍多组 |
| **叠衣 F5（叠至指定外接矩形）** | "语言不可表达"的证据 | 旁边**并排放 instruction-only 对照，让它折出一个塞不进抽屉的形状**——这一个对比就证明了"记忆 ≠ 更好的 prompt"（对抗 R1-B4） |

### 4.10.4 四条让它经得起看的规矩

1. **成对试次连拍 3–4 组，不要只放一组。** 一组是轶事，四组同向才是证据。**实时不剪**，加速必须标注倍率。
2. **屏幕上挂 injection rate。** 论文报它，视频也报它——预先堵掉"你是靠多弃权刷高的"（R2-B1）。
3. **无记忆基座的尝试必须完整播完**，包括它挣扎的过程。只放我方成功片段是 demo 里最容易被识破的作弊。
4. **每段角标写清 trial 计数**（第几组 / 共几组），不给"精选"留空间。

### 4.10.5 不要拍的

- ❌ **"记忆让机器人叠衣服变好"**——R-t-S 已拍过
- ❌ **长时程炫技**（抽衣→叠→入篮一镜到底）。好看，但它证明的是**策略能力**不是**记忆能力**
- ❌ **记忆库规模曲线的动画**。那是表格的活
- ❌ 任何含"训练中…"进度条的镜头——与 "no gradient once deployed" 直接冲突

### 4.10.6 预算与录制纪律

**核心原则：demo 素材在主实验跑的同时录，不另开一轮。**

| 段 | 素材来源 | 增量机器人小时 |
|---|---|---|
| 一 | 主端点的成对 trial（Z 族）+ **断电推走那一镜需专拍** | **+0.5** |
| 二 | 四层 sweep 的③/④两档（本来就要跑） | **0**（纯复用） |
| 三 | **需要打捞**：从全部 trial 日志筛 `base 成功 & ours 失败` 的成对样本，回放复现 | **+1.0** |
| 四 | P3′ 的双向 trial（本来就要跑） | **0**（纯复用） |
| 五 | reader #3 准入实验（本来就要跑） | **0**（纯复用） |
| F5 vs instruction-only | 对照本来就在消融里 | **+0.3**（补拍并排机位） |
| **合计增量** | | **≈ 1.8 robot-hours** |

**★ 三条录制纪律必须从第一天就执行，否则事后补拍成本是这个数字的 10 倍**：

1. **第三方电影机位从第一个 trial 就架好并常开。** 实验用的三路相机（base + 双腕）画幅和角度都不适合出片。补一个固定第三方机位全程录制，事后只剪辑不重拍。
2. **每条 rollout 的元数据必须与视频帧同步落盘**（trial id / 方向 / 层级 / 条件 / injection 与否 / 成败）。**第三段的"打捞"完全依赖这个**——没有它就得靠人肉翻录像。
3. **所有角标（计时器、injection rate、回退层级、trial 计数）在录制时就烧进日志**，剪辑时叠加。**事后估算的数字不能上屏。**

### 4.10.7 与 gate 的关系

| Gate | 对 demo 的含义 |
|---|---|
| **G0.5**（9-05） | **不过则第二段拍不出来**（无交叉点则③④没有对比）。demo 结构改为：第一段 + 第三段扩写为主体（cross-body admissibility framing 的可视化） |
| **G2a**（9-26） | 通过则第一、二段的③层素材可开始录 |
| **G5**（12-19） | 首批跨本体真机数出来即可拍第一段样片，**不要等到 G6**——早拍一版能暴露机位与角标问题 |

### 4.10.8 一句话

> **第一段证明"能跨"，第二段证明"为什么能跨"，第三段证明"我们知道它什么时候不该跨"。**
> 三段拍成，这个 demo 就没法被归到任何现有工作里。



---

# 5. 页数与工程量对账

## 5.1 6 页硬预算的逐节对账

**基线设计的实测排版估算（Reviewer #3 逐项核算）**：I 1.10 + II（0.57 正文 + 0.62 Table I）+ III（1.40 + 0.20 方法图）+ IV（0.45 + 0.12 Fig.2）+ V 1.75 + VI 0.15 + Refs 1.13（65 条） = **7.49 页**。

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

> **★ 2026-08-24 重估**：施工图原自评 ≈11 PM，硬件变更后的净增量如下。

| 项 | 周 |
|---|---|
| 叠衣关键点前端（原 D2 的"抓后夹爪代理"3 周方案对布料只保住一半） | +4 |
| 铰链前端与夹具 | +1.5 |
| 拉链 DLO / 拉头 / 刻度带 | +3 |
| 双臂 `(T_abs,T_rel)` retarget 与聚合改造 | +2.5 |
| 分段规则重写（双轨） | +1.5 |
| **PiperX openpi 移植（D13）** | **+3.5** |
| 几百小时转 RLDS + idle filter + TB 级存储 IO | +2 |
| 8 个自动判据的夹具与传感（D14） | +3 |
| VLAC 在 500 条留出 rollout 上的 precision/recall 标定 | +1 |
| embodiment ladder（夹爪档 + 仿真档 + 锁关节 sweep + 单臂 reader） | +1.5 |
| 两具本体各一次基座微调（而非一次）+ SR 窗口探针 | +2 |
| demo 录制基础设施（D15） | +0.5 |
| **小计** | **+26 周** |
| 扣掉移动臂消失省下的 | −2 周 |
| **净增量** | **≈ +5.5 PM** |

**总计 ≈ 16–16.5 PM / 28 周 → 需要 2.5 FTE。**

- **≥2.5 FTE**：执行完整版。
- **1–1.5 FTE**：**执行 §5.3 的 MVP，不要中间态。**
- **<1 FTE**：不要启动本课题的完整形态。

**robot-hours 侧**：152 h，两台并行，按 3 productive h/day/台 → **约 25 个工作日/台 ≈ 5 周/台**；再加 D12 的 31 h（约 2 周/台）。base fine-tune（两具 × 60k 步 @bs256，H20 上每具 3–5 天，**且大概率要重训一次**才能把 `T_eval` SR 调进 20–60% 窗口）排进去 → **policy 就绪最早 2026-12-01，与 G5(12-19) 几乎顶格**。

> **★ G5→G6 的 6 周要塞下 119 robot-hours + 对齐图训练 + 8 个控制 arm。任何一次重训就直接撞穿 G6。必须留 ≥1.5 周 buffer——现在这个排期的 slack 是 0。**

**三个省工替换（合计省 1.5–2 PM，已计入）**：
1. 时间分段用**轨 A 双轨规则**（夹爪状态机 + 双臂任务系速度过零 + 时长上限），不用学习式分段，且**不等感知前端**。
2. 锚点估计：铰链走**一次性标定**（0.5 周，若家电未移动过可**追溯标定**）；布料走 **point-track**（不需 6-DoF 位姿估计）。
3. **Retrieve-then-Steer 的复现与我们自己的注入器是同一份代码**（省 1 PM），且这在论文里同时是一个极强的受控对比论据。

## 5.3 最小可发表版本（MVP，1 FTE / 6.5 个月，≈9–10 PM）

> **这是真正推荐的形态**，除非确认 ≥2.5 FTE。**把 confirmatory 从"叠衣撑谱系"换成"门 + 拉链 + 单臂 reader 撑谱系"。**

**保留**：
1. 两台真机、共享单库、双向读写、**E0**（零梯度的唯一证据）。
2. **7 个客观自动判定的变体**：4 个铰接家电（**微波炉 / 洗衣机 / 抽屉 / 柜门**，解决伪重复）+ 3 个**不同的**拉链包。
3. **3 个 value 层（①③④）**——砍②（与③共用前端且更贵；④免费作退化对照）。
4. **P1′（三点）+ G0.5 交叉点 gate**。
5. **P2 归因（oracle 阶梯六级五差 + `Δ_retarget` 拆 limit/geom 两项）**——最便宜且最独有，**不可砍**。
6. **P3′ 方向不对称**（双向本来就要跑，免费）+ **P5**（离线已成立）。
7. **per-trial memory-harm rate + injection rate + base SR**。
8. **derive-on-read 与 instruction-only 两个对照**（4 任务）——**不可砍**（R1-B3/B4 的解药）。
9. **A7（④+腕部重解算）**——不加会被判稻草人。
10. **单臂模式 reader 作第三具本体**（零硬件成本，通过全部五条判准）。
11. **A/A 控制 + π_d pilot**（8.1 h，全部统计主张的前提）。
12. **demo 五段**（增量仅 1.8 h）。
13. 真机：**7 任务 × 20 成对 trial × 2 方向 × {base, ours}** ≈ 45 robot-hours；加单臂 reader、A7、对照与 pilot ≈ **75–85 robot-hours**。

**砍掉**：叠衣全族（降为 exploratory 定性视频 + scope 说明）；②层；套垃圾袋；仿真全部结果（只作内部 gate）；RoboMME 报数；P4 降为一行；ANN 延迟曲线；删除泄漏探针；E5（降级为 discussion 一句）；除 R-t-S 之外的全部 baseline 复现。

**这一换解掉三件事**：砍掉最贵的感知（叠衣关键点前端 4 周）与最有争议的判据（rubric + κ + 人评分级）；砍掉 G2b 依赖，G2a 成为唯一的③层 gate；工程量从 16.5 PM 落到 **≈9–10 PM**。

**代价必须诚实写进 Limitations**：
> 门与拉链的双臂耦合度低，因此我们报告的谱系展开幅度是**下界**；"紧耦合可形变任务上谱系更陡"作为**预注册但未检验的预测**留给 future work。

**二选一的规则**：如果坚持要叠衣进主表（它确实是唯一能撑开谱系的族），**那就砍拉链**。**不要两个都留。**
> **2026-08-24 更新**：拉链的力/触觉顾虑已排除（拉链任务已训练成功、数据可用；③层用抓后夹爪位姿代理＝本体感觉；成功判据在释放回 home 后的静止帧上测——两处都绕开了触觉文献里的遮挡机理）。所以这条规则回到"由预算与工期决定"，而不是由硬件决定。**MVP 推荐仍是门 + 拉链 + 单臂 reader**（拉链的③层前端最便宜——抓后夹爪位姿代理，零检测器）。

**MVP 仍然成立的理由**：论文的不可替代性在"**两台都部署的真机 + 更换 reader 无需策略梯度 + 同一协议下的谱系测量与损失分解 + 一个可预测迁移不对称的离线统计量**"，**不在 sweep 的宽度**。



---

# 6. Go/No-Go 检查点

今天 **2026-08-24**，目标投稿 **2027-03-10**（RA-L 滚动）。每个 gate 必须由具体的人在当天交出一个**数**，不接受“还在调”。

| Gate | 日期 | 交付物 | No-Go 判据 → 论文变成什么形态 |
|---|---|---|---|
| **G0** | **2026-08-29** | (a) ~~确认 PiperX 型号~~ **✅ 已确认为官方 `piper_x`**；剩余：读两台固件 DH 版本 `GetPiperFirmwareVersion()`；(b) **★ 实测两台夹爪 TCP 偏置并重跑全部运动学脚本**；(c) 两台台架几何实测（臂间距/倾角/立柱/相机）；(d) **★ 落锤 FTE 数字**；(e) 按 §0.6 判准重做**锁关节角 sweep**；(f) 跑完 `equalbudget.py`（双臂 equal-budget） | (b) 重跑前**正文不得写任何可行率数字**；(d) <2.5 FTE → **当天切 MVP** |
| **★ G0.5（最高优先，新增）** | **2026-09-05** | **同本体交叉点**：200 条 Piper 条目，同一台 Piper 上 ④直接回放 vs ③ FK→IK 回放，比 SR 与末端轨迹误差（离线 + 40 trial 真机确认） | **`SR(④)−SR(③) < 5 pp` → 四层谱系框架当场死亡，启用 cross-body admissibility framing。不等 G4。** 同时 **demo 第二段拍不出来**，demo 结构改为第一段 + 第三段扩写 |
| **G0.6** | 2026-09-05 | 用真实存量语料统计三族的**真实 exec+复位时长分布** → 锁定预算；**★ PiperX FK 一致性硬验收**（20 构型，<5 mm/<2°） | FK 残差 >5 mm → **全部离线阶梯与 φ 数字作废，P5 撤回**，必须先解决标定。**这是单点故障，必须最先做** |
| **G1** | **2026-09-12** | **Fig. 3 两联图（纯离线）**：四种 key × 四种条件（**含"相机重装位"这一纯 key 侧控制档**）的分布 + 重标定后 precision@10 / AUC vs chance；**π_d pilot 结果** | 四种 key 重标定后 precision@10 全 ≤ chance → 主结果改 language-keyed only，对齐图从方法降级为失败的 ablation，重心全移到 §V-C 归因；**π_d^F > 0.40 → F 族强制走 (P-deformable)** |
| **★ G2a（不可延）** | **2026-09-26** | **门 + 拉链**上的跨本体开环重放（各 50 episode，**离线可做**，前端只用"铰链一次性标定 + 抓后夹爪位姿代理"）：末端轨迹误差 + 接触点命中率 + **双臂 `T_rel` 保持误差** | 误差 >3 cm 或命中 <60% → **层③整体证伪**，论文重心立刻转 P2 归因。**通过后立即 arXiv 占位** |
| **★ G2b（新增）** | **2026-11-07** | **叠衣**上的同一套数，用关键点前端 | 不过 → **叠衣退出 confirmatory 降为定性**，主表只用门+拉链（即自动落到 §5.3 的 MVP） |
| **G3a** | 2026-10-03 | 同一 MuJoCo 场景内换 piper_h / piper_l URDF 重跑（官方 MIT 资产，已具备）；**④轴改报二维 (位置, 姿态)** | 不可行 → 仿真退出正文 |
| **★ G3c（新增）** | **2026-11-07** | **基座 SR 窗口探针**：10k 步小规模微调，测 `T_eval` 零样本 SR 是否落在 **20–60%**（约半天） | 不落窗口 → **当天改 `T_base`/`T_eval` 划分**（此时切分尚未冻结）。**必须早于 G3b** |
| **G3b** | **2026-10-17** | D12 采集完成 + **E0 切分冻结**（+ 家电/包实例扩充完成，**族数 3→5**） | 完成度 <60% → 放弃对齐图，转 training-free language-key。**注意：基座微调一旦开始，E0 切分不可更改** |
| **G4** | 2026-11-14 | 任一层跨本体 SR 显著高于 frozen base（>2 pp）；derive-on-read 读出延迟数 | 无 → 转负面结果论文；derive-on-read 延迟在预算内且 SR 持平 → Contribution 2 改写为 protocol/measurement 贡献 |
| **G5** | 2026-12-19 | 前 4 任务首批跨本体真机数（含 injection rate）；**demo 第一段样片（不要等到 G6）** | 跨体 SR < base 或 IR<20% → 当天转向 |
| **G6** | 2027-01-30 | 实验冻结；Fig. 4 实测绘制；决定 6 页还是买 1 页 | 与 P1′ 不符 → **同步替换 Title / Abstract / ¶5 预注册句 / Contribution 2 四处**（绑定，不可只改一个） |
| **G7** | 2027-02-28 | 内审（逐条核对 §1.0 写作红线与 Table I 每格证据来源） | — |
| — | **2027-03-10** | 投稿 | — |

**★ 排期上最重要的一条改动**：原 G2 放在 9-26 且任务选叠衣，**那天必然交不出数**（叠衣语义关键点检测器 5 周内不可能就绪 → 假 gate）。拆成 **G2a**（门+拉链，离线可做，不可延）与 **G2b**（叠衣，11-07）之后，9-26 一定有数可交，**且交的是决定论文骨架的那个数**。

**buffer**：G5→G6 之间必须留 **≥1.5 周**的重训/重跑 buffer。**现在这个排期的 slack 是 0。**

**最可能烂尾的一环（明确点名，已更换）**：不再是"③层 object-anchored 在移动本体上的定义与标定"（移动臂已消失），而是 **叠衣语义关键点前端**。典型烂尾方式：前 3 个月一直显示"基本 work"，第 5 个月做真机跨本体时才发现关键点误差吃掉全部迁移增益，而那时四点谱系已写进 Intro 和 Fig. 1。**对策**：G2a/G2b 拆分；MVP 直接把叠衣降为 exploratory。
**第二个未量化的风险**：通用点跟踪器（SAM2 / CoTracker / TAPIR）在**布料自遮挡**下的 drift——**查不到任何 benchmark**。对策：用 **Flat'n'Fold (2409.18297) 的多视角序列**自建小规模评测，零采集成本。**诚实标注：目前无解，只能自测。**

**arXiv 占位建议**：**G2a 通过后立即**把 P1′/P2/P3′ 的预注册预测挂上 arXiv（G1 的 Fig. 3 是纯离线，也可作为占位内容）。抢跑风险源排序已变：
1. **Retrieve-then-Steer 团队（升到第一位）**——已同时拥有 6-DoF ALOHA-PiPER 与 7-DoF OpenArm 两具异构双臂真机，正文点名二者 "different arm kinematics"，**做跨本体记忆只差一个实验**
2. Dejavu（逐字写出我们的方案）
3. RECAP（把跨本体检索表示标为 open question）
4. RoboMME 团队（有基准、代码、leaderboard、π0.5 pipeline，做 v2 的边际成本远低于我们）



---

# 7. 开写前必须先定的事（带优先级）

**P0 — 本周内（阻塞其他一切）**

1. **★ 实测两台夹爪的 TCP 偏置并重跑全部运动学脚本**（零成本，**新增最高优先**）。用户已确认**两台夹爪不同款**，而 `RAL2027/kinematics/` 里每一个数（82.8° / 7.10 cm / 17.8° / 80.8% / 57.3%）都建在"同款夹爪、仅安装 rpy 差 90°"这个前提上。**重跑之前正文不得写任何可行率数字。** 顺带把"夹爪差异单独贡献几个百分点"报成 embodiment 阶梯上的一档（这一档现在是**免费且原生**的）。
2. **★ 在存量 Piper 真实轨迹上重算 per-task 层③可行率 φ**（零成本，**全文最关键的一个数**）。均匀关节采样的任务盒位姿分布与真实家居操作（集中在把手高度、桌面、包口这少数几处）完全不同；真实分布下 φ 可能是 99%（**谱系当场压平**）也可能是 40%。同时报 (a) 全局 φ、(b) **per-task φ**（P3′ 的秩相关直接需要，也是 demo 第四段挑变体的依据）、(c) φ 沿 episode 时间轴的分布。**与第 1 条合并做——夹爪 TCP 修正后一次算完。**
3. **★ 从已采集的门任务轨迹反推铰链轴**（零成本）。用户确认**尚未做铰链标定**。门把手轨迹是圆弧，对末端位姿序列拟合共同螺旋轴即可。**多条 episode 拟合出的轴一致（残差小）则同时证明两件事**：家电在采集期间没移动过、且轴已经拿到——**存量数据直接变成③层可用、零重采**。若不一致则需按场次标定或退到在线估轴（3–4 周）。
4. **母句的最终措辞落锤**（§1.2 那句 + **第四个限定词** `of a different kinematic family`），在一个文件里写死，Title / Abstract / ¶2 / C1 / Fig.1 caption 五处派生。
5. **E0 的数据切分方案落锤**。**★ 加两条前置**：必须先过 **G3c**（SR 20–60% 窗口探针），且必须先完成**家电/包实例扩充（族数 3→5）**。**基座微调一旦开始就不可改。**
6. **★ 第一天就架第三方电影机位 + rollout 元数据与视频帧同步落盘**（§4.10.6）。**不做则 demo 第三段（harm 案例）永远拍不出来**——它完全依赖能从日志检索出 `base 成功 & ours 失败` 的成对样本。事后补拍成本是 ×10。
7. **启动 D12 弱配对数据采集**（用户已确认可随机启动采集，不受存量语料重合度限制）。
8. **★ 把 `pi0.py::sample_actions` 的 `jax.lax.while_loop` 展开为 Python 循环 + 同 seed 数值一致性检查**（半天）。**已核源码**：carry 是 `(x_t, time)`，`num_steps` 默认 10。**排在所有记忆库工程之前。**
9. **★ 把 cross-body admissibility framing 写成一段 pre-registration 放进补充材料**，G0.5 触发即启用。

**P1 — 两周内**

10. **JAX 训练侧实测**：跑 `uv run scripts/train.py debug_pi05` 十步（半天）。用户已确认 5090 **推理**可跑，但 JAX 对新架构常常**推理 kernel 先于训练 kernel 就绪**。
11. **是否在 RoboMME 上报数 → 决定：不报数。** 只沿用其表示轴/注入轴术语并引用其 §6 把 mobile manipulation 与 memory-bank methods 留待未来研究。
12. **主打新颖性排序 → 决定：multi-reader / bidirectional 共享库为主，"换读者无策略梯度"为代价论据。**
13. **"零梯度"口径 → 决定：全文写 "no gradient reaches either policy once deployed"，并在 ¶4 主动交代基座微调 + E0。** 同时**必跑** training-free language-keyed 变体作诚实地板。
14. **真机 trials 数 → 改为 `n = 785·π_d`**，`π_d` 预注册并在 G1 前 pilot 实测。对照锚点：**R-t-S 真机 50 trials/任务（同硬件同任务）**、RECAP 10、VLA-Pro 20。
15. **Retrieve-then-Steer 的可比性 → 先做 LIBERO-10 + π0.5 的保真度复现门槛**（92.4→94.4，其 std 0.2–0.8）。未通过则全文改称 reimplementation 且不做"优于"主张。
16. **★ 跑完 `equalbudget.py`（双臂 equal-budget 三 arm 对照）与 `lockedsweep.py`（锁关节角 sweep）**。前者决定"协同 +10 pt"这条 Contribution 留不留；后者决定锁关节档还能不能当 plan B。

**P2 — 一个月内**

17. **Miras / Titans 的理论 framing → 决定：全砍。**
18. **RT-X / OpenVLA 一族是否给 Table I 一行 → 决定：不给**（共训产生权重而非记忆对象）。**【本组尚未读过一手 PDF】**
19. **Behavior Retrieval / STRAP → 决定：Table I 整行删除**，正文一句话划走。**不得靠推测填格。**
20. **RA-VLA (ICML'26) → 决定：从参考文献删除**，除非拿到一手 PDF。
21. **VINN 的 venue 核实**（arXiv comment 无 venue 字段）。引用时暂标 arXiv。
22. **LaTeX 模板**：`RAL2027/paper_src/` 现为 ICRA 的 `ieeeconf`（**按用户指示保留**）。若最终投 RA-L 需换 `IEEEtran`，换完立刻用真实字数做排版对账。
23. ~~openpi 源码中确认注入点~~ **✅ 已完成**（见 P0 第 8 条）。
24. **`PORTMEM` / `XEM` 重名检索**：**arXiv 已查零命中**（`"cross-embodiment memory"` / `"transferable memory"+cs.RO` 同样零命中），**仍需查 ACM/DBLP**。
25. **★ 页数决定提前**：新增内容（P5、三档标定表、两个主端点、六级 oracle 阶梯）会挤爆 §V 的 2.05 页。**建议现在就决定买 1 页（7 页）**，而不是拖到 G6。
26. **★ 参考文献按族打包**：v5 §9.5 新增约 30 条（铰接感知 / 可形变 / DLO / point-track / 双臂协同 / 基座对照 / 任务坐标系理论）。**40 条硬预算下必须每族只单列 2–3 篇，其余合并 e.g.**，或买 1 页。
27. **venue 订正三条**：VLAC → **ICML 2026**（README 挂 OpenReview `i7mfaYYLDf`）；SRPO → **CVPR**（PDF 页眉逐字）；TwinVLA → **ICLR 2026 Poster**（新增）。

**P3 — 写作期**

28. Fig. 1 的两张真机实拍（**双臂 Piper / 双臂 PiperX**，含工位背景差异）—— G3b 之前补拍。
29. Fig. 1(b) 的四层内容必须从我们自己的库导出真实样例，**不要手编**；素材直接来自 demo 第二段。
30. Table I 每一个非平凡格子在 caption 或脚注给出证据来源（页码）。**任何一格被作者本人认为不实，整节可信度归零。**
31. 所有 venue 逐条经 arXiv API / 一手 PDF 复核；无已发表 venue 的（Retrieve-then-Steer、RECAP、VLA-Pro、Dejavu、RoboMME）**只能标 arXiv preprint**。v3 的 venue 错误密集，复发一次就会让审稿人不信任整份书目 —— 而本文的说服力**完全**建立在书目精确度上。


---

## 附 A：本大纲相对 v4 的主要修订清单（供追溯）

| v4 的写法 | 本大纲的写法 | 依据 |
|---|---|---|
| “所有能持久的机器人记忆，都只有写它的那个本体能读” | 加三限定词：executable action content / written during its own deployment / no further policy update | RECAP、RAM、RoboOS 三个反例（threat_RAM_RoboOS.md + 一手 PDF） |
| γ_sim=0.9992 构成 mechanical veto | 放弃该论证，改为阈值无关的检索质量与重标定代价 | Retrieve-then-Steer 表 8：0.9988–0.9998 全程 93.5–94.4，最松阈值仍高于无记忆基座 |
| P1：迁移率上升、同本体精度下降、有交叉点 | P1：cross-body 随抽象度上升；same-body 由内容保真度主导 | RoboMME：GroundSG+Oracle 84.08 > FrameSamp+Modul 44.51 |
| ①② condition-side、③ retarget→Eq.6、④ Eq.6 | **四层统一解码到读者动作空间，共用 Eq.(6)** | 去除层级 × 注入通路共线；并使 “adopted unchanged” 成为真陈述 |
| “零策略梯度” | “no gradient reaches either policy **once deployed**” + E0 + reader #3 admission cost | v4 阶段 B 自带双本体基座微调 |
| 记忆库 = 存量语料灌到 10⁴–10⁵ 条 | 拆 `S_deploy`（主结果）/ `S_corpus`（仅规模与串扰） | “部署中自写”与“语料灌库”互斥 |
| 检索延迟-规模曲线为第二贡献 | **删除**（10⁵ 条暴力扫描亚毫秒）；改为对 in-context 的一句话对比 | 必然“无事发生”的实验 |
| 条目删除后的残留泄漏检验 | **删除**（对显式条目表平凡为真） | 空实验 |
| 8 类 baseline 必须齐全 | 真机 4 条件 + 结构性排除声明 | 3–4 人月复现不可交付；跑残废版是拒稿理由 |
| 8–10 任务 × 15 trials | 12 任务 × 20 成对 trial（同 init + 同噪声种子） | P3 的效力由任务数决定；15 trials 低于同族标准 |
| P2：检索错 vs 动作不可用（二分） | oracle 阶梯五级四差（key / retarget / value 三桶） | 二分法循环论证且漏掉 retarget 桶 |
| 记忆有害率 | 有害率 + **injection rate** + forced-injection 列 + `IR<20%` 标 n.i. | TR 与有害率都能被“多弃权”刷好看 |
| ① 层用 grounded 语言（带像素坐标） | ① 层用**可重新 grounding** 的语言（物体名 + 关系，无写入者像素坐标） | 像素坐标是写入者相机系的量，与 body-agnostic 直接冲突 |
| 沿用 RoboMME 的 when/where/what/how 四维分类 | 只沿用其表示轴与注入轴术语；四维仅作 Intro 一句修辞 | 我们的任务在其意义上基本是马尔可夫的，硬对齐是修辞 |
| entry 粒度未定义 | **片段级**（夹爪状态机 + 速度过零），双单位报数 | 粒度不定则规模主张与存储成本论证都不成立 |
| 成本论据 O(T·B) → O(1) | **删除**，改为三列实测代价表 + **时效性论据** + E5 实验 | O(1) 无依据；且回答不了“为什么不共训” |

---

## 附 B：v1 → v1.1 的修订清单（硬件变更 + v5 §9 补丁，2026-08-24）

| # | v1 的写法 | v1.1 的写法 | 依据 |
|---|---|---|---|
| 1 | 本体 = FR3（定基 7-DoF）+ 移动臂；对照轴 = 定基↔移动、定视角↔变视角 | **双臂 Piper（球腕 Puma 型）↔ 双臂 PiperX（偏置腕 UR 型）**；对照轴 = **运动学族 + 关节限位包络** | 无 FR3 真机数据 |
| 2 | 三个限定词 | **四个**（加 `of a different kinematic family`） | PiperX 确认为官方 `piper_x` |
| 3 | P1：cross-body 随抽象度上升 | **P1′：交叉点是唯一主张**（同本体 ④>③ 且跨本体 ③>④） | 单调上升不是 finding——GR00T N1.7 已主张 relative EEF |
| 4 | P3：归因 viewpoint variability；对照 = 锁底盘 | **P3′：归因读者限位包络覆盖率**；对照 = **工作空间交集核**；**新增 Spearman 秩相关（离线 φ 预测在线 Δ）** | 旧机理被证伪：体素 **IoU=0.528**，两者互不包含 |
| 5 | — | **★ 新增 P5**：层④失败←架构（标定后仍 7.10 cm/17.8°）；层③失败←限位（放宽即 100%）。**两者不得合并叙述** | 一手复算；**这是审稿人 20 行代码就能证伪的地方** |
| 6 | ③ = object-anchored EE deltas（依赖 6-DoF 刚体位姿） | ③ = **anchor-frame contact-point motion + `(T_abs,T_rel)` 拆分**；四类任务四种锚点（铰链螺旋轴 / DLO 弧长 / 语义关键点 / SOI 环） | 衣物、垃圾袋**没有刚体系** |
| 7 | ④ = 关节动作 / **action-expert 潜码** | ④ = **原始关节指令，物理单位，reader 侧不允许任何被训练过的解码器** | "潜码"正是 GR00T EmbodimentTag 在做的事；物理单位防**纯归一化失配**这个平凡混淆 |
| 8 | 单一 pooled 主端点（12×20 McNemar） | **两个 co-primary 端点**：(P-rigid) 门+拉链成对 McNemar / (P-deformable) 叠衣分层随机化 + 连续进度分。**HR 定义随之分裂，不可 pooled** | 配对有效性与统计头room **系统性反相关** |
| 9 | 240 成对 trial，效力 80% | **`n = 785·π_d`**，π_d 预注册并 pilot 实测 | π_d≈0.30 这个隐含假设从未被声明；长时程可形变任务可能到 0.5 → n=392 |
| 10 | P3 任务级符号检验 n=12，p≈0.0005 | **族级 cluster 重抽样**；**族数 3→5**；ordinal 进度分消除 tie | 伪重复：12 变体只来自 3 族，**n_eff≈4.3**，全同向 p 从 0.000244 变成 **0.0625（不显著）** |
| 11 | 消融 A1–A6 | **+A7**（④+腕部重解算，82.8°→6.7°，附 `④+wrist-repair ≡ ③` 论证）**+A8**（coordination-oracle，第四桶） | 不加 A7 会被判层④是稻草人 |
| 12 | oracle 阶梯五级四差 | **六级五差**（`Δ_retarget` 拆 `Δ_limit`(19.2pt) + `Δ_geom`(0.0pt)，插入 coordination-oracle）；**限定只在 D/Z 两族跑**；**预注册负值处理** | 归因错误比压平更致命；F 族 anchor-oracle 不可得 |
| 13 | 分段 = 夹爪状态机 + EE 速度过零 | **双轨分段**：轨 A（零依赖，立即可做）/ 轨 B（感知就绪后）。**禁止主线任何一个数等待轨 B** | 对拉链与门退化为 1 段/episode；新规则会把并行支路拧成串行 |
| 14 | 跨本体 trial 单位成本高于同本体 | **两平台并行运行，单位成本相同** | Piper 与 PiperX 是**两套独立台架**，无物理拆装 |
| 15 | 预算 135–155 h | **≈152 h**（按族计时 + G0.5 + A/A + π_d pilot + demo 增量 1.8 h） | 1.5 min/rollout 对家居长时程错 2–3 倍 |
| 16 | 记忆库 10⁴–10⁵ 条 | **10⁴–N_max，明写 N_max**，规模曲线对数下采样 | 按实际语料核算只到 10⁴–3×10⁴ |
| 17 | reader #3 = FR3 换夹爪+移相机+锁关节 | **单臂模式 reader**（在售 SKU，14→7 维，通过全部五条判准）；锁关节降 plan B 且须做锁定角 sweep | 锁关节按原定义把关节锁在**零位**＝人为最劣化配置，违反判准 3 与 5 |
| 18 | 人月 ≈11 PM | **≈16–16.5 PM**，需 2.5 FTE；MVP ≈9–10 PM | 逐项重估 |
| 19 | G2（9-26，叠衣）| **拆 G2a（门+拉链，9-26，不可延，离线可做）/ G2b（叠衣，11-07）**；新增 **G0.5 / G0.6 / G3c** | 叠衣关键点检测器 5 周内不可能就绪 → 原 G2 是**假 gate** |
| 20 | 最可能烂尾 = ③层在移动本体上的标定 | **= 叠衣语义关键点前端**；第二风险 = 点跟踪器在布料自遮挡下的 drift（**查不到任何 benchmark**） | 移动臂已消失 |
| 21 | R-t-S = 注入机制提供者 | **= 同硬件同任务的直接前作**（附录 D：双臂 AgileX PiPER 叠 T 恤，π0.5 42.0→50.0，50 trials/任务）；**抢跑风险升到第一位** | 一手核实 |
| 22 | — | **★ 新增 §4.10 真机 demo 规划**（五段脚本 + 任务选角 + 四条规矩 + 录制纪律 + 与 gate 的关系） | demo 的职责是让审稿人 15 秒内相信一件他本来不信的事 |
| 23 | — | **★ Table I 第 6 行 body 列补注** `ALOHA-PiPER + OpenArm`——他们**已经有两具异构双臂本体，只是没让记忆跨过去** | 最诚实也最有力的定位 |
| 24 | ③层占位者 = Di Palo & Johns / DINOBot | **+GR00T N1.7（relative EEF）+ point-track 一族 9 篇**；③层**不能再宣称新颖**，重定位为"已知会迁移的那一层，作 upper anchor" | 一手核实 |
| 25 | — | **★ 两台夹爪不同款** → 全部 φ 数字需用实测 TCP 偏置重算；同时"换夹爪"档变成**免费且原生** | 用户 2026-08-24 答复 |
| 26 | — | **★ 铰链未标定** → 需确认家电采集期间是否移动过；未移动则可**追溯标定**（存量数据零重采变③层可用）。**零成本自检：对门轨迹拟合共同螺旋轴** | 用户 2026-08-24 答复 |

