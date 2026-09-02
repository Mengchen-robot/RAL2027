# 能力地图与分叉修复：把零样本评测变成定向后训练的数据引擎

> 日期：2026-09（本轮）
> 状态：**调研完成，四个零成本 gate 待跑**
> 上游：`idea-by-myself.md`（用户原始构想）、`../memory_cross_embodied/idea_cross_embodied/vla_memory_cl_feasibility_v5.md`（基座/算力/统计纪律的真值来源）
> **定位（2026-09 用户拍板）：本文替换 idea 2（`idea_lifelong_memory.md` 及其施工图转为已归档，不再推进）。** idea 1（跨本体持久动作记忆）不受影响，继续独立进行。
> 标注约定：**【核】**=本轮一手核实（OpenAlex / GitHub API / raw 文件 / 本地 PDF）；**【待核】**=未验证。
> **本轮工具事实**：`export.arxiv.org` 与 `arxiv.org` 全程 TLS 重置不可用；一手核实全部走 **OpenAlex**（`api.openalex.org/works/doi:10.48550/arXiv.<ID>`）与 **GitHub API / raw.githubusercontent.com**。

---

## 0. 一句话

> 一个预训练 VLA 的能力覆盖是**不完整且不可见的**。零样本评测的副产品不是一个分数，是**一张能力地图**。
> 本文把这张地图做出来，用它定向生成修复数据，并证明：**在等数据预算下，地图导向的定向数据优于等量的大规模无导向数据。**

**这不是一篇追 SOTA 的论文。** 主张是关于**数据分配效率**的，不是关于榜单名次的。

---

## 1. 平台：RoboLab 是什么，它给了什么、没给什么

**全部一手核实**（`github.com/NVlabs/RoboLab`，Apache-2.0，467 star，建于 2026-04-08，last push 2026-08-12；论文 `2604.09860` *RoboLab: A High-Fidelity Simulation Benchmark for Analysis of Task Generalist Policies*，2026-04-10）。

**它是建在 NVIDIA Isaac Lab 上的评测 benchmark，不是数据生成器。** 这一条必须先说清楚，因为原始构想里把它当成了数据生成器。

### 1.1 它白给的六样东西（每一样都直接抵掉一条风险）

| 资产 | 内容 | 抵掉的风险 |
|---|---|---|
| **能力坐标系** | RoboLab-120：120 任务 × 三条 competency 轴 × 三个难度。细粒度属性标签现成：`color(26) / semantics(60) / size(6)`（visual，84 任务）· `conjunction(8) / counting(7) / spatial(29)`（relational，42）· `affordance(12) / reorientation(6) / sorting(12) / stacking(6)`（procedural，34）+ `vague(7)`；难度 simple 64 / moderate 39 / complex 17 | **"没有公认失败分类学 ⇒ 归因粒度太粗 ⇒ 定向退化成域随机化"这条头号风险。** 归因不再自由发挥，直接索引到一张离散、可预注册、可审计的网格上 |
| **失败位置是真值** | composable predicate 状态机 + 逐 env subtask 日志（`log_{run}_env{i}.json`、`scripts/read_subtask_status_from_hdf5.py`、`robolab/core/events/subtask_recorder.py`） | **VLM 归因不可靠。** *where* 是仿真真值，VLM 只需回答 *why* |
| **完整可重置状态** | HDF5 里 `initial_state` 含 `articulation.robot.{joint_position, joint_velocity, root_pose, root_velocity}` 与每个 `rigid_object.root_pose`；`examples/run_recorded.py` 可 restore 初态并开环重放（支持 `--validate-states`） | **分叉锚点从哪来**（见 §3） |
| **并行评测便宜** | 官方口径 **~40 GPU-hours / 120 任务**（假设 ~200 ms 推理步，1.4 it/s）；`--num_envs N` 逐 env 独立终止与独立 subtask 状态机 | **闭环轮数受限。** 百卡下一次全量扫 ≈ 2 小时 ⇒ **瓶颈从评测转移到重训**，轮数不再是 2–3 |
| **自然语言生成接口** | `skills/robolab-taskgen`、`skills/robolab-scenegen`（Claude Code skill，CC-BY-NC-4.0）；task 是一个绑定 USD 场景 + 语言指令 + 终止判据的 `Task` dataclass，**robot / observation / action space 无关**；taskgen **自动生成 `vague` 与 `specific` 指令变体** | **"失败总结"到"新任务"的接口。** 总结的自然语言直接就是 taskgen 的 prompt；且指令具体度三档是白给的诊断轴（§3.3） |
| **配套工程** | `scripts/convert_to_lerobot.py`（训练数据导出）、`docs/statistical_significance.md`、`analysis/sensitivity_analysis/posterior_inference.py`、接触力传感器（`get_contact_force` / `is_supported_on_surface`）、结果 dashboard | 训练数据格式、统计协议、接触信号（**真机 Piper 恰好没有力/触觉通道**） |

### 1.2 它**不给**的一样东西（本文方法的落点）

> **RoboLab 只记录策略跑出来的轨迹，不产生专家轨迹。** 仓库全树 3336 个路径中零 `mimic`、零 `curobo`、零运动规划器、零遥操。`robolab/scene_gen/llm_scene_gen/{physical,spatial}_solver.py` 是**场景布局**求解器，不是轨迹求解器。

**所以"用 RoboLab 定向构造数据"这句话里，缺的正是轨迹那一环。§3 就是补这一环，而且这一环就是本文的 method。**

### 1.3 本体（决定了 §2 的轴）

内置三个，全部 `single-arm · fixed-base · parallel-jaw`：

| 本体 | 构成 | 特征 |
|---|---|---|
| **DROID**（benchmark 默认） | Franka Panda + Robotiq 2F-85 | 720p 腕相机，**内参按 pi05 / DreamZero 训练数据标定**；高 PD (400/80)，臂重力关闭 |
| **Franka Panda** | 原厂手指夹爪 | **无腕相机**；标准 PD (80/4) 与高 PD 两个变体 |
| **Kinova Gen3** | Gen3 7-DoF + Robotiq 2F-85 | 腕相机；仅关节位置动作空间 |

"Bring your own robot"：任务与本体解耦，任何 IsaacLab 兼容机器人可插入。**Piper/PiperX 的官方 URDF 是 MIT 且已下载，但需 USD 转换 + 控制器接入，本文不做**（见 §7 去重协议）。

---

## 2. 生态位：这篇文章站在哪

### 2.1 撞车地图（全部一手核实）

**前三段全部有人做完了。**

| 论文 | ID | 日期 | 它做到哪一步 | 界画在哪 |
|---|---|---|---|---|
| **VLAMotor** | `2606.00053` | 2026-05 | 摘要逐字：*"the **first analysis framework for VLA enhancement**, which integrates distance-aware model **testing for failure exposure** and agent-based **data synthesis for model finetuning**"* | **最致命。** 它的合成走"抽象成结构化语义 → 规划参数化修复技能序列 → IK 变可执行轨迹"，是**从头求解**；本文是**从策略自己的失败状态分叉**，产出 on-policy。且它零泄漏意识 |
| **PLD**（ICLR'26） | `2511.00091` | 2025-10 | residual actor 探测失败区 → 仿真采 deployment-aligned 恢复数据 → 蒸馏回 generalist；LIBERO 99%、SimplerEnv +50% | **曝光度最高。** 它需要**训练一个 residual RL actor** 才换到分布对齐；本文构造性地得到分布对齐，**零额外训练**。这是最重要的一句划界 |
| Reflection-Based Task Adaptation | `2510.12710` | 2025-10 | VLM 因果反思 → 合成稠密奖励 + quality-guided SFT，全自主闭环 | 它合成的是**奖励**，本文合成的是**轨迹**；它是 RL，本文零策略梯度 |
| Unsup. Discovery of Failure Taxonomies | `2506.06570` | 2025-06 | VLM 归因 → 语义空间聚类出跨 episode 复现失败模式，**明说用于指导定向数据采集** | 它到"发现分类学"为止且**不重训**；本文的分类学是 RoboLab 现成的，贡献不在分类学 |
| FLARE | `2608.26645` | 2026-08 | MLLM 离线分析视频 → 识别 OOD 失败态 → 定向采集 Reset 技能数据 → 训练 | 闭环完整度最高。界：它靠 MLLM 判定，本文靠 predicate 真值；它采的是 reset 技能 |
| AHA(ICLR'25)/FailGen · RoboFAC · Guardian | `2410.00371` / `2505.12224` / `2512.01946` | — | 失败推理 VLM + **程序化扰动成功演示**造失败数据 | **方向相反且不配对**：它们"扰动成功→失败"，本文"从失败→修复"，且严格同初态配对 |
| TwinRL | `2602.09023`（本地 PDF） | 2026-02 | 孪生并行 RL 找 failure-prone 构型 → 定向 HIL 真机补点，20 min 真机交互 | **开篇动机句与原始构想一字不差**（"constrained by the high cost of expert demonstrations"）→ **Intro 不得用这句话开场** |
| MimicGen / DexMimicGen / DemoGen / RoboSplat / RoboTwin 2.0 / RoboCasa / GenSim / RoboGen | — | — | 数据生成器 | **十个主流生成器全部是"沿预设轴枚举/随机覆盖"，没有一个以能力缺陷为条件生成**【核】。这既是机会也是工作量 |

### 2.2 真空白（两个独立调研通道确认，检索零命中）

1. **没有任何工作把「零样本 benchmark 评测」当作 data engine 的入口**——现有自改进要么在训练任务上自主练习（SOAR `2407.20635` CoRL'24、Self-Improving EFM `2509.15155`、PLD），要么在部署日志上做（`2506.06570`）。
2. **「用测试结果指导训练」的自适应泄漏，在机器人自改进领域从没被提出过。** PLD / FLARE / VLAMotor 全都在犯。
3. **没有人从失败状态分叉重采样、把成功分支缝回去当 SFT 数据。** RIPT-VLA / SimpleVLA-RL 是整条 rollout 的稀疏奖励 RL；PLD 是 residual actor。这一格是空的。
4. `2608.18433`（*The Embodiment Gap in Robot Foundation Models*，2026-08 综述）点名批评：**这个领域连"适配到新设定要花多少工作量"的上报口径都没有。**

### 2.3 与 RoboLab 自己的划界（必须写，否则被当作用别人的 benchmark 灌水）

RoboLab 摘要第一句：*"Existing benchmarks often exhibit significant **domain overlap between training and evaluation**, trivializing success rates."*

> **它说的是静态泄漏**（benchmark 造出来时训练/评测分布就重叠）。**本文说的是自适应泄漏**（闭环把测试结果当决策输入，反复迭代后引入的过拟合）。**两者机理不同、修法不同、可测量不同**——RoboLab 的修法是造新任务，本文的修法是切 probe / frozen holdout 并报 gap。**这一段必须在 §II 用整句话写出来。**

---

## 3. 承重方法：Branch-and-Stitch（分叉—缝合）

### 3.0 一句话

> **不去从头求解任务。把策略自己失败的那条轨迹，在 predicate 判定的最后一个已完成 subtask 边界处切开，从那里并行分叉 K 条，用 predicate 自动筛出成功分支，把「策略自己的前缀 + 成功分支」缝成一条训练轨迹。**

零额外模型、零额外训练、零额外求解器。只用 RoboLab 已有的三样：可重置的 `initial_state`、`--num_envs` 并行、predicate 自动判定。

### 3.1 为什么这是 method 而不是 plumbing（四条，按可辩护性降序）

1. **数据构造性地 on-policy。** 前缀是策略自己走出来的真实状态。**PLD 花了一整个 residual RL stage 才换到的 "deployment distribution alignment"，这里是定义上成立的。** 这是最强的一句划界，直接进 rebuttal。
2. **产出两个标量，把能力地图升级成度量空间。**
   - `β(s)` = 从状态 `s` 分叉 K 条的成功率
   - `δ` = 修复编辑距离（被替换段长度 + 状态偏离范数）
   两者给出天然课程序（先修 δ 小的），也给出"缺口有多深"的定量刻画。**"能力地图"若只是一张定性的表，审稿人不会认；带标量它才是 method。**
3. **一条可预注册的二分——本文最锋利的一句话。**
   ```
   β > 0  →  可修复：策略"会做，只是这次没做好"  →  缝合成 on-policy 修复数据（便宜、in-distribution）
   β = 0  →  真能力缺口："不会做"              →  调用 taskgen 生成同属性更简单一级，递归
   ```
   > **现有全部自改进工作把"不会做"和"这次没做好"混在一起。** 这个判据把它们分开，且它就是「模型能力欠缺」的**操作化定义**——不是形容词，是一个可算的量。
4. **反事实严格配对。** 同一 `initial_state`、同一场景、同一指令，失败轨迹与修复轨迹**只在失败段不同**。⇒ 成对统计（McNemar，直接继承 idea 1/2 的纪律）+ 因果可定位。**现有失败数据集（RoboFAC / FailGen / RoboFail）全是"扰动成功→失败"，方向相反且不配对。**

### 3.2 分叉锚点怎么拿（工程细节，也是 G-0 的内容）

RoboLab 的重放是 **restore 初态 + 开环重放动作**（`docs/replay.md`），不是任意中途状态直接落点。所以分叉 = 重放到 step `t` → 从那里换成闭环采样 K 条。

**官方明确警告**：IsaacSim 5.0 与 5.1 的 PhysX 构建不同，接触密集动力学**跨版本不可复现**；且"faithful reproduction requires recording and replaying with a **single env**"。
→ **两条必须写进论文的实验纪律**：(a) 预注册一个 IsaacSim/IsaacLab 版本，全程不动；(b) 重放与录制在同一 env 配置下进行。
→ **G-0 必须先量化重放保真度**（见 §5）。

### 3.3 分叉的三个维度（每一维都有仿真真值，VLM 只当叙述者）

| 维度 | 怎么做 | 分开的是什么 | 成本 |
|---|---|---|---|
| **采样噪声** | π0.5 是 flow matching，采样自带随机性；加温度/噪声尺度参数 | **运气 vs 系统性偏差** | 0（并行 env 白给） |
| **指令具体度** | RoboLab taskgen **自动产出 `vague` / `default` / `specific` 三档** | **语言接地缺口 vs 运动执行缺口** | 0（现成） |
| **难度降级** | taskgen 生成同属性更简单一级 | **能力缺口的深度** | 低（LLM 调用） |

> **这一节是全文对"归因不可靠"这一击的答案：承重的归因量全部来自仿真真值（predicate、β、δ、三档指令对照），VLM 只负责把它们写成人读的总结与 taskgen 的 prompt。** 若 VLM 完全去掉，管线仍然成立——**这一点必须在 §III 明说，并做成一个消融**（A3：无 VLM 的纯网格版 vs 有 VLM 版）。

### 3.4 自评估头（用户第四诉求的落点）

`β(s)` 是**每个状态"我在这里有多大把握"的真值标签，免费且非 VLM 猜测**。把它蒸馏成一个**执行前**（instruction × scene 级）的 competence predictor：

- 训练数据：评测扫描的副产品，零边际成本
- 用途：弃权 / 求助 / 触发下一轮定向造数
- **论证轴照抄 idea 2 已确立的"事前 vs 事中"**：策略侧 UQ（VFD `2606.18043`、去噪方差 `2606.03847`）**只在执行开始之后才有定义**，是熔断器；本文的 predictor 在**执行之前**给分，是准入。**两者不可互相替代，必须都报。**
- **诚实纪律**：这一条是 Contribution 4，不是 headline。它成立与否不影响 §3.1–3.3。

---

## 4. 主张与四条 Contribution

### 4.1 主端点（用户指定，不可改）

> **在等数据预算下，能力地图导向的定向数据训练效果 > 等量的大规模无导向数据。**

形式化：固定生成轨迹条数 `N`，比较
- `A_targeted`：按 β/δ 地图分配的 N 条（分叉修复 + 递归降难度）
- `A_uniform`：在 RoboLab 任务空间上均匀/随机生成的 N 条
- `A_frozen`：不训练的地板

**预注册**：主端点是 `SR(A_targeted) − SR(A_uniform)` 在 **frozen holdout** 上的差，配对统计。**这是审稿人必然要求的那个消融，本文把它当主端点而不是消融——这是正确的位置。**

### 4.2 四条 Contribution（可辩护性降序）

1. **Branch-and-Stitch**：一个不需要额外求解器、额外 actor、额外策略梯度的 on-policy 修复数据生成机制；配套两个可测量 `β` / `δ` 与一条可预注册的二分（可修复 vs 真缺口）。
2. **等预算主张**：定向 > 等量无导向（§4.1），并给出**换算率**——"一条定向修复轨迹 ≈ 多少条随机生成轨迹"。这个数字直接回应 `2608.18433` 对"缺少适配成本上报口径"的批评。
3. **自适应泄漏审计**：probe / frozen holdout 协议 + `probe增益 − holdout增益` 的 gap 作为一等指标。**首次在机器人自改进中提出并量化这个问题**，并对至少一条现有管线（重现 PLD 式的全量闭环）测出它的 gap。
4. **执行前的 competence predictor**：由 `β` 蒸馏而来，与执行中 UQ（VFD / 去噪方差）并列报，论证轴是"事前 vs 事中"而非"便宜几倍"。

### 4.3 Abstract 红线

- **命名禁令（全部一手撞车）**：`self-evolving`（RoboHarness 摘要逐字）· `self-improving`（`2510.12710`/`2511.00091` 等多篇标题）· `consolidation`（RoboHarness）· `lifelong robot learning`（LIBERO 副标题）· `cross-embodiment`（**留给 idea 1**）。**用户口语里的"自进化"在英文成稿里一律换词。**
- 不得出现 first / novel / unexplored / we fill the gap。
- 必须出现 **frozen holdout 上的数字**，且 probe 上的数字与 holdout 上的数字**必须并列出现**。
- 必须写明这是 **simulation-only**，并把外部效度写进 Limitations（见 §6 R3）。
- **Intro 不得以"expert demonstrations are expensive"开场**——TwinRL 摘要首句逐字占用。

---

## 5. 五个 gate（全部零机器人小时，按依赖排序）

| Gate | 内容 | 不过怎么办 |
|---|---|---|
| **G-0 · 重放保真度**（前置） | 固定 IsaacSim 版本与 env 配置，重放到 step `t` 与原轨迹的状态偏差分布；用 `--validate-states` | 若接触密集任务上重放发散 → 分叉锚点不可靠 → **只能从 `t=0` 分叉**（退化成"同初态重采样"，仍成立但 δ 失去意义） |
| **G-1 · 死穴：β 的分布** | π0.5 在 RoboLab-120 / DROID 上零样本扫一遍，取全部失败，在最后一个已完成 subtask 边界分叉 `K=16`，画 `β` 的直方图 | **若 β 全域 ≈ 0** → 失败是确定性的、重采样修不好 → **Branch-and-Stitch 半边死亡**，退到"纯 taskgen 难度课程"单腿论文。**若 β 双峰** → §3.1 的二分是真的，全文成立 |
| **G-2 · 基座 SR 窗口** | π0.5 零样本 SR 必须落在 **20–60%**（直接继承 v5 §5.8 的纪律）。RoboLab 论文自称 *"exposing significant performance gap in current SOTA"*，大概率不会太高，但**必须实测** | >70% 天花板 / <15% 地板 → 调整任务子集或难度档，**必须在看到主结果之前定死** |
| **G-3 · 指令具体度轴** | `vague` vs `specific` 三档的 SR 差是否显著 | 不显著 → 砍掉"语言接地 vs 运动执行"这一维，分叉降为二维 |
| **G-4 · 等预算随机基线可构造** | 能否真的造出"等量的随机 RoboLab 任务数据"（随机 taskgen + 随机 rollout 筛选），且其成功轨迹产出率可接受 | 产出率过低 → 基线定义改为"同等 **GPU-hours**"而非"同等条数"，**口径必须预注册** |

> **五个 gate 全部离线、全部零机器人小时。** 本文相对 idea 1 的最大工程优势：生死判定不消耗任何机器人小时，且不与 idea 1 的真机窗口争资源。

**算力核算**：一次 120 任务全量扫 ≈ **40 GPU-h**（官方口径）。G-1 需要 1 次基线扫 + 分叉（K=16 × 失败任务数，可并行）。RoboLab 建议 **48 GB+ 显存**（`docs/env_vram_size_guide.md`）→ **H20（96 GB）可用，RTX 5090（32 GB）需实测**，这是一条待确认项。

---

## 6. 风险表

| # | 风险 | 有没有解 |
|---|---|---|
| **1** | **G-1 不过：β 全域 ≈ 0。** π0.5 的失败若是系统性偏差，重采样修不好 | **这是死穴，必须最先跑。** 有退路（纯 taskgen 课程单腿论文）但少一条主贡献 |
| **2** | **VLAMotor / PLD 抢跑。** 两者都已公开，且 VLAMotor 自称 "first analysis framework for VLA enhancement" | 无解（这是竞争）。**对策**：贡献必须落在 `β`/`δ`/二分/泄漏 gap 这些**可测的量**上，不能落在"管线"这个概念上；Related Work 主动整句点名两者 |
| **3** | **simulation-only。** RA-L 审稿人会问真机 | 有解但要主动写：本文主张是**数据分配效率**，不是绝对性能；且 RoboLab 的 DROID 本体腕相机内参按 pi05 训练数据标定、只有 68.7% 物体在 DROID 词表内，是**为真机策略分析而建**的。仍须写进 Limitations，并可选加一个 Piper 扩展档（§7） |
| **4** | **缝合出来的轨迹在动力学上不连续**（前缀末与分叉首的衔接） | 构造上应连续（同一条仿真展开），但**必须做一个可视化 + 关节速度跳变审计**，否则会被问 |
| **5** | **taskgen 生成的任务质量不可控**（LLM 生成的任务可能不可解或判据错误） | 预注册一条人工抽检规则：每轮随机抽 10% 生成任务人工验收，报**通过率**。不报这个数字会被质疑 |
| **6** | **IsaacSim 版本漂移**导致跨轮结果不可比 | 官方已明确警告。**预注册版本，全程冻结，写进 §IV** |
| **7** | Contribution 4（competence predictor）与已有 VLA UQ 工作重合 | 论证轴用"事前 vs 事中"（继承 idea 2 已建立的框架），且它是第四条不是 headline |
| **8** | 与 idea 1 被判 salami | §7 的去重协议 + **单本体** + 全仿真 + 完全不同的图 |

---

## 7. 与 idea 1 的去重协议（现在定死）

| 维度 | idea 1（跨本体持久动作记忆） | 本文 |
|---|---|---|
| 轴 | **谁能读**（本体） | **模型不会做什么**（能力覆盖） |
| 本体 | 双向 Piper ↔ PiperX **真机** | **单本体 DROID（仿真）**；Kinova Gen3 只作复现档 |
| 是否更新权重 | 否（冻结 + 记忆注入） | **是**（定向 SFT/LoRA） |
| 资源 | 75–85 robot-hours | **0 robot-hours**，纯 GPU |
| "cross-embodiment" 这个词 | **idea 1 独占** | **全文禁用**；第二本体一律写 "replicated on a second platform" |
| venue | RA-L，2027-03 投 | RA-L，与 idea 1 错开 ≥2 个月 |

> **两篇不得在同一窗口投同一 venue。** 双盲下本文不得写 "our prior work"；需要 idea 1 结论的地方自带最小复算。

**已归档**：`idea_lifelong_memory.md` / `paper_outline_v1.md` / `survey_memory_lifecycle.md`（原 idea 2）。其中 `survey_memory_lifecycle.md` 的**命名禁令表**与 `idea_lifelong_memory.md` §8.4 的**"事前 vs 事中"论证轴**在本文继续复用，其余不再推进。

---

## 8. 立即待办（按依赖排序）

1. **【前置】装 RoboLab 并跑通** `uv sync --extra isaac50` + `pytest tests/`（官方自带端到端安装验证）；**同时实测 RTX 5090 32 GB 能否跑**（官方建议 48 GB+）。
2. **【G-2，最便宜】π0.5 零样本扫 RoboLab-120 / DROID 一遍**（≈40 GPU-h），看 SR 是否落在 20–60% 窗口。这一次扫描同时产出 G-1 需要的全部失败轨迹与 subtask 日志。
3. **【G-0】重放保真度审计**（`run_recorded.py --validate-states`）。
4. **【G-1，死穴】β 直方图。** 这一条决定全文形态，**必须在写任何一行正文之前跑完**。
5. **【G-3】三档指令的 SR 对照**（同一次扫描的副产品，零边际成本）。
6. **【G-4】等预算随机基线的口径预注册。**
7. **【设计】probe / frozen holdout 的分层切分方案**：按 `attribute × difficulty` 分层，保证两侧的属性分布可比；**切分必须在看到任何闭环结果之前冻结并写进预注册文档**。
8. **【待核】逐篇一手精读**：VLAMotor `2606.00053`（最致命）、PLD `2511.00091`、FLARE `2608.26645`、`2506.06570`、RoboLab 论文 `2604.09860` 正文。**本轮只核到摘要级，Related Work 的划界句必须建立在正文之上。**
9. **【决策】π0.5 在 RoboLab 里怎么接**：RoboLab 是 server-client 策略架构、`policies/` 下有策略客户端；需确认 openpi 侧的接入工作量。
