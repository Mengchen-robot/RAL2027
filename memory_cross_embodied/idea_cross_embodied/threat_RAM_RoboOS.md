# 威胁评估：RAM (CoRL'24) 与 RoboOS —— 对 v4「跨本体持久记忆」主张的冲击

日期：2026-08-22
触发：arXiv 检索 `"embodiment-agnostic" AND "memory"` 命中 RAM；`"shared memory" AND "cross-embodiment"` 命中 RoboOS
证据来源：全文 `pdftotext`，PDF 存于 `memory-vla/papers/10_retrieval_augmented_frozen/{2407.04689,2505.03673}.pdf`

---

## 一句话结论

**RAM 不杀方向，杀措辞。** v4 §2 第 42 行的主张句按字面可被 RAM 一句话证伪，必须加限定词。SQ1 / SQ2 / SQ3 与 P1–P4 全部存活。

---

## 1. RAM — 威胁等级：**严重（不致命）**

**arXiv**：2407.04689 · CoRL 2024 · *RAM: Retrieval-Based Affordance Transfer for Generalizable Zero-Shot Robotic Manipulation*

### 存的是什么

条目 = (物体中心交互首帧 RGB, 自然语言任务类别, 2D 像素接触点 + 接触后路点序列)

读出时经 VFM 对应关系迁移 + RANSAC 拟合为 **一个 3D 接触点 + 一个接触后直线方向** `A3D = (c3D, τ3D)`，由 AnyGrasp + MoveIt!/cuRobo 执行。

### 是否部署中累积：**否**

| 证据 | 内容 |
|---|---|
| Table 5 | 全库 **660 条**，离线取自 DROID / HOI4D / 互联网图片 |
| Custom Data | 唯一扩充通道是**人在 RGB 图上点起终点** |
| 附录 B.1 | "some affordance demonstrations are further refined manually by adding an offset or being removed due to inaccurate camera parameters" |
| §4.5 | 成功 rollout 被**蒸馏成 ACT 权重**（30.0% → 65.0%），**而非追加为记忆条目** |

最后一条是最有力的区分证据：**RAM 自己选择了「把经验变成权重」而不是「把经验变成条目」**——这正是我们主张要打破的那个默认。

### 逐字原文

> "…transfers such out-of-domain 2D affordance to in-domain 3D executable affordance in a **zero-shot and embodiment-agnostic** manner." — Abstract

> "Notably, our method is **embodiment-agnostic** and data-efficient—qualities that prior methods are struggling with—which is substantiated by abundant experiments conducted across various robotic platforms." — §1

> "we also utilize a Unitree B1 robot dog equipped with a Z1 arm … to show our method's **cross-embodiment nature**, which is covered in §4.5." — §4.1

**注意**：§4.5 只有定性 demo，**无跨本体成功率表**。这是我们的机会——RAM 声明了跨本体，但没有量化它。

### 可用作我们旁证的 RAM 实验

- **Table 3 消融**：去掉 geometrical retrieval，SR 38.3 → 26.7，DTM 3.39 → 9.36 → **支撑 P2（瓶颈在 key 侧）**
- **Fig. 6**：性能随数据量单调上升，但上限仅 660 条 → **论证我们 10⁴–10⁵ 条 scaling 实验的必要性**

---

## 2. RoboOS — 威胁等级：**轻微—中等**

**arXiv**：2505.03673 · *RoboOS: A Hierarchical Embodied Framework for Cross-Embodiment and Multi-Agent Collaboration*

shared memory 在 **planner 层**，不含动作知识。

> "…maintains **spatial memory** (spatial relationship, locations of objects and robots), **temporal memory** (task feedback, tool-calling history), and **embodiment memory** (motion domain, joint states and battery levels)…"

> "Robotic memory stores real-time system attributes such as motion domain constraints, joint states, and battery levels, optimizing task allocation…"

技能封装在各机器人**本地**的 Cerebellum Skill Library，不跨本体共享。其 "embodiment memory" 恰恰是**本体绑定信息的显式存储**——反而是我们论点的正面例证。真机部分只有 demo，全文无操作成功率。

---

## 3. 必须落实的修改

### 3.1 §2 第 42 行主张句（**唯一不可协商项**）

中文：
> 所有**由部署中的机器人自己写入的**持久记忆，都只有写它的那个本体能读；能被任意本体读的记忆，要么不是机器人自己写的（RAM：离线第三方语料 + 人工标注），要么存的不是动作知识（RoboOS：场景图与调度状态）。

英文（§8 叙事句同步改）：
> Every memory a robot **writes for itself during deployment** can only be read by the body that wrote it. The memories that any body can read are either not written by robots at all (RAM: an offline, partly hand-curated corpus) or do not store action knowledge (RoboOS: scene graphs and scheduling state).

### 3.2 §2 的 2×2 格子

右上角不再是空白。必须把 RAM / RoboOS 显式画进去并标注各自的 value 层级与**写入端缺失**，空白格改为「部署中自写 + 任意本体可读 + 动作层」。

### 3.3 §5.1 第 1 点贡献降级

「提出分层 value 表示」→「**首次在同一采集、同一协议下并排测量该谱系的迁移率–精度权衡**」。RAM 已占据 ② 层附近位置。

### 3.4 §6 基线表加一行

本体无关 affordance 检索（RAM / Robo-ABC）作为 ② 层级的**直接对照**。

### 3.5 新增一条区分维度（写进 contribution）

**读出端是冻结的 VLA action expert，而非运动规划器。** RAM 的读出经 AnyGrasp + MoveIt!/cuRobo，只能表达「接触点 + 一个直线方向」。这条把 RAM 从竞争者转为谱系高抽象端的**基线**。

---

## 4. Related Work 可直接使用的英文段落

> Embodiment-free retrieval is not new. RAM [Kuang et al., CoRL 2024] stores a 660-entry affordance memory of (object-centric initial frame, language task label, 2D contact waypoints) mined offline from DROID, HOI4D and web images, and transfers a contact point plus a single post-contact direction to a Franka arm and a Unitree B1+Z1 quadruped, executed by an off-the-shelf grasp generator and motion planner. That memory is authored once from third-party corpora and partly by hand, and is never written to by the robots that read it: RAM converts its own successful rollouts into ACT policy weights rather than appending them as entries. RoboOS [Tan et al., 2025] does maintain a shared memory that grows during deployment and is read by heterogeneous robots, but its content is environment and hardware state — a scene graph, tool-calling logs, and per-robot "motion domain constraints, joint states, and battery levels" — so what crosses embodiments is where things are and which robot is free, not how to act. Neither work varies the abstraction level at which an experience is written, and neither reports a transfer rate.

---

---

# 第二轮：Ag2Manip / Robo-ABC / DINOBot（全文已读，题名均核对通过）

## 5. 判定汇总

| 论文 | arXiv | 等级 | 核心事实 |
|---|---|---|---|
| Ag2Manip | 2404.17521 | **轻微** | **根本没有记忆库**。"知识"在 EPIC-KITCHENS 训出的编码器**权重** + 手工设计的自由漂浮球形 proxy 动作空间。单本体（sim Franka / real FR3）。顶着 "Agent-Agnostic" 标题却从没测过第二个 agent |
| Robo-ABC | 2401.07487 | **中等** | affordance memory = (无遮挡物体 RGB crop, 2D 接触点集)，51 类。RAM 的前驱，同族。单 Franka Panda。**全文 "embodiment" 出现 0 次**（已 grep 确认） |
| DINOBot | 2402.13181 | **中等（三篇最高）** | **唯一把③层做成检索条目的工作**：(bottleneck 腕部 RGB-D, **末端执行器坐标系速度序列** `V=[vx,vy,vz,wx,wy,wz]`, 任务名)。人工动觉示教写入，单 Sawyer，视觉伺服对齐后**开环重放** |

## 6. SQ1 是否失效：**否**

三篇里**没有一篇改变过存储表示的抽象层级并测量其后果**；没有一篇有第二个本体；没有一篇报告任何跨本体成功率数字。

- Robo-ABC 消融全在 **key 侧**：retriever 编码器（CLIP-B32/B16/ResNet50）、correspondence 模型（DIFT/SD-DINO/DINO-ViT/LDM-SC）、库类别数（18/36/51）、top-k
- DINOBot 消融同样全在 key 侧与对齐模块：编码器对比（ResNet50/CLIP/R3M/DINO-ViT, Fig.7）、对齐方法（RoboTAP/RAFT/DINOBot, Fig.8）、干扰物、物体尺寸。**value 抽象层级固定不变**

## 7. 代价：贡献声明必须再收紧一次

§3.3 原写「RAM 已占据②层附近位置」，现在必须补上「**DINOBot 已占据③层位置**」。

①②③三层里**有两层的表示设计已有先例**。剩下的干净新意只有四条：

1. ①④两层
2. **写入端为部署中机器人自身**（三篇全是离线/人工/第三方语料）
3. **读出端为冻结 VLA action expert**（三篇全是运动规划器 / 视觉伺服 / 开环重放）
4. **同一采集、同一协议下并排测量四层的迁移率–精度权衡** ← **核心，仍然无人做过**

第 4 条是唯一不可替代的。写作时贡献必须挂在它上面，而不是挂在"我们提出分层表示"上。

## 8. 可为我们所用的旁证

**Ag2Manip Table I**：`Ours (Proxy)` 85.7% vs `Ours` 78.7% —— **抽象表示 retarget 到实体损失 7.0 个点**。这是同本体内的"抽象代价"实测，**正面支撑我们权衡曲线的前提**（P1 说同本体精度随抽象度单调下降）。但它只有单一抽象层级、单一本体，所以只是一个点，不是曲线——这恰好说明我们要画的是什么。

## 9. Related Work 英文段落（第二轮补充）

> Retrieval memories for manipulation predate ours, but every one of them is authored offline and read back by a single body. Robo-ABC [Ju et al., 2024] mines an affordance memory of (unoccluded object crop, 2D contact points) over 51 categories from EPIC-KITCHENS-100 — hand-filtered for lighting and blur, and hand-checked for usability — and reads it out through diffusion correspondence into one AnyGrasp pose on a single Franka; DINOBot [Di Palo and Johns, 2024] is the closest prior instance of an end-effector-frame value, storing (bottleneck wrist image, EE-frame velocity trajectory, task name) tuples collected by a human via kinesthetic teaching and replayed open-loop after visual servoing on a single Sawyer. Ag2Manip [Li et al., 2024] keeps no memory at all: its "agent-agnostic" knowledge lives in encoder weights and a hand-designed free-floating proxy, and although it does report what abstraction costs — 85.7% for the proxy against 78.7% after retargeting — every experiment it runs uses one Franka arm. Across this literature the abstraction level of a stored experience is fixed by design, no experience is ever written by the robot that later reads it, and no transfer rate between embodiments is ever reported.

---

# 第三轮：Di Palo & Johns (RA-L'23) 与 VINN —— **本轮改变贡献结构**

## 10. Di Palo & Johns, *On the Effectiveness of Retrieval, Alignment, and Replay in Manipulation*

**arXiv 2312.12345 · IEEE RA-L，2023 年 12 月接收**（ID 形似占位符，已用 arXiv API + PDF 页眉双重核实为真）
**威胁等级：严重（不致命）** —— 三篇里唯一改变我们贡献结构的。

### 为什么它最危险

**同 venue、同谱系、③层的真正首位占据者，且已有 key 侧与 value 侧的分离测量。**

谱系已查清：C2F-IL (Johns, ICRA'21) → **本篇 (RA-L'23)** → DINOBot (2402.13181, **ICRA'24**)。同作者（Imperial Robot Learning Lab）。DINOBot 与本篇 **value 完全相同**，只把 alignment 从学习式伺服网络换成 DINO-ViT 像素对应。

> **修正第二轮的判定**：③ 层占位者应标为**本篇（RA-L'23）**，DINOBot 是其后续。RA-L 审稿人大概率知道这篇。

### 三阶段与存储内容

| 阶段 | 问题 | 内容 |
|---|---|---|
| Retrieval | *what* | DINO-ViT 特征余弦相似度 argmax，同时取回 bottleneck 目标图 `o_{b,n}` 与演示轨迹 `s_n` |
| Alignment | *where* | goal-conditioned 视觉伺服网络，腕部图像对齐到 bottleneck 观测（4-DoF） |
| Replay | *how* | **开环回放**末端速度轨迹（6-DoF） |

value = `s = [V₁ᴱ,…,V_Tᴱ]`，`V = [vx,vy,vz,wx,wy,wz]`。对齐到刚性附着于物体帧的 bottleneck 位姿，故是**物体相对**的 EE 速度序列 → **③层**。

### 它做了什么、没做什么（决定 SQ2 命运）

**没做**：全文 `failure` / `fail` / `ablation` / `attribution` 词频**均为 0**。无失败模式分解，无 `P(fail | 检索正确)` 条件统计。

**做了三件很接近的事**（必须让出这三种措辞）：

| 位置 | 内容 | 结论 |
|---|---|---|
| §IV-C / Fig. 6 | {retrieval 有/无} × {decomposition 有/无} **2×2 因子消融** | 逐字："**retrieval alone is not sufficient to enable efficiency and effective transfer**" |
| §IV-D / Table I | 逐字 "**We ignore the retrieval phase here**"，人工指定 goal image + trajectory | = **key 侧强制完美下的 value 侧隔离测量**。Replay 0.73±0.12 / BC-GUAPO-10 0.62±0.24 / BC-GUAPO-1 0.23±0.16 |
| §IV-E / Fig. 7 | 定义脱离下游成功率的 **retrieval accuracy**（"retrieves … an observation of the object **belonging to the same class**"），横扫 ResNet-50 / CLIP / R3M / ViT-DINO | = **key 侧隔离测量**，用途是选编码器 |

**关键缺口**：他们**分别**有 key 侧指标和 value 侧指标，**从未把两者接起来**。而且——

1. key 侧指标是**类别命中率代理**，不是「取回的 value 能不能用」
2. Table I 变的是**读出机制**（回放 vs 学习策略），**不是 value 的抽象层级**；全文 value 表示只有一种
3. **只有一具身体**，所以「检索正确但这具身体执行不了」这一失败模式在其设定中**不可能发生**

### 库的写入端

**人写的；部署中不增长。** 最硬的证据是 **Algorithm 2（test time）只有读、没有写**。

> "the **human operator manoeuvres the end-effector** to provide a demonstration, e.g. with **kinesthetic teaching**" (§III-C1)
> "We extract these features for all the observations in the buffer **offline, after the training stage**."

**必须预判的反驳**：§IV-C 有一句 "the decomposition … enables the robot to **autonomously gather a large buffer of demonstrations without the need for human supervision**"。审稿人可能拿这句打我们。**反制事实**：机器人自采的只是**对齐观测** `o_{i,t}`（Alg. 1 内层循环），**每条轨迹都是 `Operator records demo from b^W`**（Alg. 1 外层），且全发生在 training stage 而非部署期。

### 本体与泛化轴

- 单本体：`Sawyer + Robotiq gripper` + 腕部 RealSense。跨本体数字**零**。
- `embodiment` 全文出现 **2 次，且都在同一条参考文献里**（Open X-Embedded 跨行断词所致）。**正文本体内 0 次。**
- 其泛化轴是 **object identity**：训练物体 80% / intra-class 73% / inter-class 67%（10 训练物体 → 35 测试物体，350 episode）。机器人始终是同一台 Sawyer。**object generalisation ⊥ embodiment transfer** —— 这是我们最干净的切分线。

### 一个必须小心的预先反驳

Table I 里他们**明确论证开环回放优于学习策略**（0.73 vs 0.62），逐字 "This clearly proves the effectiveness of trajectory replay compared to explicitly learning an end-to-end policy"。等于预先反驳了「用学习式 policy 读出」的设计。

**我们的反制**（写进 §5.1 或 §6）：该结论成立**仅当** (a) 对齐把回放变成帧不变的，且 (b) 只有一具身体、EE 速度在同一身体的 EE 系下语义相同。**一旦换本体，EE 速度序列的语义不再守恒，开环回放的优势立即失效**——这正是我们要量化的东西。

---

## 11. VINN (2112.01511) —— **威胁等级：轻微—中等**

存逐帧 `(观测, 专家动作)`（SfM 从 GoPro 恢复的平移量 + 4 类夹爪状态）。BYOL 编码器 → 嵌入 L2 取 k 近邻 → **距离 SoftMin 加权平均**：

`â = Σᵢ exp(−‖e−e⁽ⁱ⁾‖₂)·a⁽ⁱ⁾ / Σᵢ exp(−‖e−e⁽ⁱ⁾‖₂)`

离线固定数据集（71 训练 / 21 测试演示），部署中不累积。单本体 Hello Robot Stretch，`embodiment` 0 次。**④层检索的经典先例**，引用时定位为「把模仿学习整体降格为最低抽象层检索」的原型 + 我们谱系最底端的基线。

**一处对我们极有利的细节**：其动作源自人手 reacher-grabber 演示，落到机器人时要乘一个**手调的逐轴系数 `c`**（每元素 <1）"to … improve **transfer from human demonstrations to robot execution**"。这是一个未被承认的本体差，且是用**手调常数**补的 —— **④层原始动作换了身体就得手工重标定，这是我们论点的正面例证。**

> venue **未核实**（arXiv comment 无 venue 字段）。引用时勿标 RSS 或其他，需另行核实。

---

## 12. 两个是/否（第三轮判定）

### SQ1（四层 value 并排测迁移率–精度）—— **否，无人做过，且现在更值钱**

两篇都只有**一种** value 表示，都没有第二个本体，都没有报告 transfer rate。

**更值钱的理由**（应直接写成 SQ1 的动机句）：②（RAM）、③（本篇 / DINOBot）、④（VINN）**各自被不同论文、不同协议、不同机器人占据**——这本身就证明「同一采集、同一协议下并排测量」没人做过，而且正是因为没人做，这四层之间的权衡至今无法比较。

### SQ2（key 侧 vs value 侧归因）—— **存活，但原始措辞已被占据，必须重新定位**

**必须让出的三种措辞**：
- 「我们把系统分解为检索与执行并分别评估」→ §IV-C 已占
- 「我们单独测量检索准确率」→ §IV-E / Fig. 7 已占
- 「我们在检索固定的条件下单独测量执行」→ §IV-D / Table I 已占

**重新定位（推荐，不建议放弃）**：把归因**条件化到本体转移上**，并把 value 轴从「读出机制」换成「抽象层级」：

> 不是「瓶颈在检索还是执行」（Di Palo & Johns 已在单本体下回答），而是：**当写入本体 ≠ 读出本体时，性能损失有多少来自 key 侧跨本体检索退化、多少来自 value 侧跨本体不可执行；且这一分解如何随 value 抽象层级 ①→④ 变化。**

**核心论据**：他们的 value 侧失败**只能**是物体几何失败，因为只有一具身体；「检索正确但这具身体执行不了」在其设定中不可能出现。这是唯一不重叠的干净空间。

**命名建议**：不要用 `retrieval / execution` 这组词命名归因实验（会被直接对号入座），改用 **`key-side transfer loss` / `value-side transfer loss`**，并在 RW 中**主动引用**这篇、主动划界——RA-L 审稿人大概率知道它，主动划界比被质问好。

---

## 13. Related Work 英文段落（第三轮）

> Retrieve–align–replay is an established manipulation paradigm, and it is established in this venue. Di Palo and Johns [RA-L 2023] decompose interaction into a retrieval phase that fetches the most visually similar training object from a memory buffer using DINO-ViT features, an alignment phase that visually servos a wrist camera onto a stored bottleneck pose, and a replay phase that open-loop executes the retrieved 6-DoF end-effector velocity trajectory, reaching 80%, 73% and 67% success on training, intra-class and inter-class objects; its successor DINOBot [Di Palo and Johns, ICRA 2024] keeps exactly this stored value and replaces only the alignment mechanism with pixel-level DINO correspondences. VINN [Pari et al., arXiv:2112.01511] sits one rung lower, storing per-timestep expert actions frame by frame and predicting each action as a softmin-distance-weighted average over the k nearest demonstration embeddings. Both buffers are authored by a human operator before deployment — in [RA-L 2023] every trajectory is recorded kinesthetically and the robot autonomously collects only the alignment observations, while at test time the deployment algorithm exclusively reads — and both are evaluated on a single arm: the word "embodiment" appears in [RA-L 2023] only inside a bibliography entry, and VINN patches the human-to-robot gap with a hand-tuned per-axis scaling constant. Critically, their generalisation axis is object identity, not embodiment; the failure mode we target, in which retrieval is correct but the retrieved action is unexecutable on the reading body, cannot arise when only one body exists. Neither work varies the abstraction level at which an experience is stored, and neither reports a transfer rate across bodies.

---

## 14. 四层 value 的占位现状（三轮汇总，写作时必须照此引用）

| 层 | 表示 | 已有占位者 | 我们的位置 |
|---|---|---|---|
| ① 语言摘要 | 任务/子目标语言 | **无直接占位者** | 干净 |
| ② 物体中心子目标 | affordance / 接触点 | **RAM (CoRL'24)**；Robo-ABC (前驱) | 已有先例，降级为"并排测量" |
| ③ 任务坐标系 EE 增量 | 物体相对 EE 速度序列 | **Di Palo & Johns (RA-L'23)** ← 首位；DINOBot (ICRA'24) 后续 | 已有先例，**且在目标 venue** |
| ④ 关节动作 / 潜码 | 逐帧原始动作 | **VINN (2112.01511)** | 已有先例 |

**结论：四层里三层的表示设计都有先例。** 贡献**只能**挂在以下四条上，不能挂在"提出分层表示"：

1. **写入端为部署中机器人自身**（所有先例均为离线 / 人工 / 第三方语料）
2. **读出端为冻结 VLA action expert**（所有先例均为运动规划器 / 视觉伺服 / 开环重放 / k-NN 平均）
3. **同一采集、同一协议下并排测量四层的迁移率–精度权衡**（SQ1，唯一不可替代）
4. **跨本体条件下的 key/value 迁移损失分解**（SQ2 重定位版）

---

## 15. 下一步待查

- [ ] **2304.08742 Behavior Retrieval** —— 优先级最高。检索的是**训练数据**而非动作（检索出来去训策略），与我们不同轴，但**名字最像，最容易被审稿人拿来说事**，必须有备答
- [ ] 2201.12716 You Only Demonstrate Once · 2204.02863 DOME · 2203.00352 Affordance Learning from Play
- [ ] Vosylius & Johns, *Few-shot In-context Imitation Learning via Implicit Graph Alignment*, CoRL'23（= 2310.12238）
- [ ] Vitiello, Dreczkowski, Johns, *One-shot Imitation Learning: A Pose Estimation Perspective*, CoRL'23
- [ ] 核实 VINN 的 venue

> VINN 参考文献中**无新增**检索式动作知识工作（检索相关引用只有 FAISS 1702.08734 与 DemoAT 采集工具）。
