# 跨本体持久动作记忆：面向 IEEE RA-L 的科研可行性报告（v5 · 硬件变更修订版）

日期：2026-08-24
目标 venue：**IEEE RA-L（滚动投稿，2027 Q1–Q2）**
上游：`vla_memory_cl_feasibility_v4.md`（本文的被修订对象）、`paper_outline_v1.md` / `_zn.md`（施工图）、`threat_RAM_RoboOS.md`（威胁登记表）
本次修订依据：真机条件变更（FR3 + 移动臂 → 双臂 Piper + 双臂 PiperX）+ 四轮一手核查 + 两份对抗审查

> **本文档的用法**：v5 是 v4 的**修订版**。v4 中未被本文件点名推翻的内容**继续有效**（尤其：主张句的三个限定词、四层 value 的思路、SQ1/SQ2/SQ3、与 Retrieve-then-Steer 的边界声明、三轮威胁核查的结论、§9 参考文献表）。凡本文件与 v4 冲突，以本文件为准。凡标 **【待确认】** 的，写进论文前必须有一手证据。

---

# 0. v4 → v5 变更摘要

## 0.0 先回答那个问题：换成 Piper↔PiperX 之后，这篇论文还成不成立？

> ## **判断：需补救才成立。**
> 不是"成立"，也不是"不成立需换主线"。**跨本体 gap 客观存在且量级足够**（这一点比 v4 的 FR3↔移动臂设定更可证），但**论文的承重结构不是 gap 的大小，而是四层谱系的交叉点，而这个交叉点至今没有任何人估过一个数**。三条补救缺一不可，全部有明确的、成本近零的执行方式。

**为什么 gap 客观存在（三条已核实的硬数字）**：

| 证据 | 数字 | 来源（本次一手复算） |
|---|---|---|
| 层④朴素关节复制的末端姿态误差 | 中位 **82.8°**，p90 126.7°；位置中位 23.55 cm | `/tmp/agxurdf/redteam.py`，n=146 held-out |
| 层④**做完最好的固定标定**之后仍剩 | 中位 **17.8° / 7.10 cm**（全线性 42 参数）；sin/cos 提升 114 参数仅到 16.0°/6.12 cm | 同上 |
| 层③（任务系末端位姿）在家居任务盒内的跨本体 IK 可行率 | **80.8%**（补偿夹爪 90° 安装差）；不补偿则 67.2% | `/tmp/agxurdf/taskspace.py` / `redteam2.py`，n=250 |

7.10 cm / 17.8° 对本文任一任务（拉链是毫米级、门把手是厘米级）都完全不可用。**所以"关节空间内容不可跨本体迁移"这个命题成立，而且是在给了对手最有利的离线最小二乘标定之后仍然成立。**

**为什么仍然"需补救"（三条 blocking，全部来自对抗审查且我已复算确认）**：

1. **谱系的交叉点从未被估过，而它是唯一的承重结构。** 若同本体上层④不显著优于层③，四层谱系退化为"越抽象越可迁移"的单调阶梯——GR00T N1.7 已经用自己的话主张过这件事（"deltas from the current pose … a key factor in the model's cross-embodiment performance"）。减去 VLAC/HELP（写入门控）、RAM/VINN/Di Palo&Johns（检索）、R-t-S 与 GR00T RTC（注入）、RDT-1B（条目 schema）、R-t-S 附录 D（**同款双臂 AgileX PiPER 上的检索记忆叠 T 恤，π0.5 42.0→50.0**）之后，净增量只剩"我们在两台臂之间跑了一遍"。**这不是 RA-L finding。**
2. **层③失败的归因写错了，而这是审稿人用 20 行代码就能证伪的地方。** 见 §0.1 第 2 行与 §3.4。
3. **工程量 ≈16 PM，对 6.5 个月 / 1 FTE 缺口 2.5 倍**；且关键路径被自己新写的分段规则串行化。见 §8。

**三条补救（全部零/低成本，必须同时做）**：

| # | 补救 | 成本 | 解掉什么 |
|---|---|---|---|
| **R-a** | 新增 **G0.5 交叉点 gate**（同本体 200 条条目，④直接回放 vs ③ FK→IK 回放），预注册门槛 `SR(④)−SR(③) ≥ 10 pp`；不达标当场切已预注册的 fallback framing（**cross-body memory admissibility**） | 0 机器人小时（离线回放）+ 约 2 机器人小时（真机确认） | blocking 1 |
| **R-b** | **本体对扩展 + 框架反转**：把**单臂模式**（AgileX 在售 SKU，14→7 维，T_rel 字面消失）升为主实验第二条腿；正文本体对的门面用最宽的一档开场，Piper↔PiperX 放在阶梯**最保守端**，写成"即便同厂同代、同 DoF、同负载、臂展仅差 6.9%，关节空间内容仍不可迁移" | 0（同一台机器换个模式跑） | "同厂同代不算跨本体"的先天怀疑 |
| **R-c** | **MVP 换 confirmatory 任务集**：门 + 拉链 + 锁关节 reader 撑谱系，叠衣全族降 exploratory | −6.5 PM | blocking 3（同时砍掉最贵的感知与最有争议的判据） |

**明确不推荐的路**：换主线。理由是这个硬件条件下没有更好的主线可换——数百小时家居数据 + 两具双臂异构本体，正好是这个问题的天然实验台，而任何"换成同本体持续学习"的退路都直接撞上 R-t-S 附录 D。

## 0.1 逐条变更表

| # | v4 / 施工图的哪一条 | 为何作废 | v5 换成什么 | 详见 |
|---|---|---|---|---|
| 1 | v4 §1 表第 3 行：本体 = `Franka FR3（7 DoF 定基）+ π0.5 同款移动机械臂`，及其"桌面↔移动 是低 DoF↔高 DoF、定视角↔变视角的干净二元对照" | 无 FR3 真机数据；无移动臂 | 双臂 Piper（球腕 Puma 型）↔ 双臂 PiperX（偏置腕 UR 型），对照轴改为**运动学族 + 关节限位包络** | §1 |
| 2 | 施工图把 Piper↔PiperX 全部 gap 归因于 "different kinematic families" | **本次复算证伪一半**：把 PiperX 关节限位放宽到 ±189° 后层③可行率 **80.8% → 100.0%**（`redteam2.py`，n=250，restarts=14）。**架构对层③失败的贡献是 0%，全部来自关节限位** | 归因分开写：**层④失败 ← 架构**（可证，标定后仍 17.8°）；**层③失败 ← 关节限位包络**（可证，放宽即 100%）。两者**不得合并叙述** | §3.4 |
| 3 | 施工图 §1.2 表 `-- best-fit per-joint affine retarget q'=s*q+b` 那一行 | **误标**：`taskspace.py` 从未拟合任何仿射映射，那一行算的是"复制 j1–j3 + 自由重解 j4–j6"（6.7°） | 三档标定实测值单列（82.8° / 52.4° / 17.8°），"复制 j1–j3 + 重解腕部"单列为消融 **A7**；同时修正 `RESULTS_taskspace.txt` 的误标 | §3.4 / §6.4 |
| 4 | v4 §4 的 **P3**：`FR3（低 DoF、定基）→ 移动臂 的迁移率显著高于反向，因为定基记忆是移动记忆的子集` | 机理在运动学上被证伪：两者工作空间体素 **IoU=0.528**，互不包含（Piper 被 X 覆盖 72.2%，X 被 Piper 覆盖 66.3%） | **P3′**：不对称性由**读者的关节限位包络对写者任务盒位姿的覆盖率**决定，且可由纯离线统计量预测方向与逐任务排序（Piper→X 80.0% vs X→Piper 57.3%） | §3.3 |
| 5 | 施工图 §4.5 P3 行 + §4.8 V-D 的"移动臂锁底盘再跑一次"对照 | 两台都是固定躯干双臂，没有底盘可锁 | 替换为**工作空间交集核对照**：把双方写入条目都限制在体素交集的 52.8% 内重跑；不对称若消失则机理坐实 | §3.3 |
| 6 | v4 §6 阶段 A：`LIBERO（定基单臂）+ RoboCasa（移动操作）构成仿真侧双本体对照` | 双本体对照定义已变；且 R2-B2（一次改 8 个变量）本来就未解 | 同一 MuJoCo 场景内换 AgileX 官方 `agx_arm_urdf` 的 piper / piper_x / piper_h / piper_l 四套 URDF（MIT 许可，已下载） | §6.2 |
| 7 | v4 §6 阶段 B 预算句：`8–10 任务 × 15 trials × 3 方法 × 3 检查点 ≈ 30 机器人小时/轮` | 1.5 min/rollout 对家居长时程任务错 2–3 倍（叠衣含复位 3.5 min） | 按族分别计时的预算算式，见 §6.6 | §6.6 |
| 8 | 施工图 §4.7 正文必写句：`跨本体 trials 需要进行物理本体更换与复位，因此其单位成本高于同一本体 trials` | **这句现在是错的**。Piper 与 PiperX 是两套独立台架，reader swap 只是换台跑，无物理拆装，且两台可并行 | 改写为"两个平台并行运行，跨本体 trial 的单位成本与同本体相同；我们同时报告 robot-hours 与 wall-clock" | §6.6 |
| 9 | 施工图 §4.2 任务集 M 层（仅移动臂）/ F 层（仅 FR3） | 移动臂消失 | **R 层**（reach 受限，仅 PiperX 可）/ **W 层**（腕部 roll 受限，仅 Piper 可）；**双向**单侧任务，直接图示化"工作空间互不包含" | §6.3 |
| 10 | 施工图 §4.2 "语言不可表达"三例：按图案擦拭 / 沿非规则路径推动 / 带特定进给节律的插销 | 三个都不在家居任务集里 | L1–L4（叠至指定外接矩形 / 拉链卡阻恢复节律 / 双臂张紧-扫掠相位差 / 关门胶条压合剖面） | §6.5 |
| 11 | 施工图 §3.2 层③定义 `object-anchored EE deltas … 锚定在物体坐标系（不是机器人基座系——移动底盘下基座系无意义）` | 括号里的理由随移动臂消失而失效；且衣物/垃圾袋无刚体物体系 | ③ = **锚点系下的接触点运动 + 双臂 (T_abs, T_rel) 分解**；锚点按任务类型分四种 | §4 |
| 12 | 施工图 §3.2/§3.9-D2 `抓取后用夹爪位姿代理（刚性附着假设）` 与"②③ 共用 6-DoF 物体位姿前端" | 对布料不成立 | 改写为"**已知抓住了哪个物质点**，夹爪位姿给出该物质点的精确轨迹"（即 point-track 表示） | §4.4 |
| 13 | 施工图 §3.9 D1 分段规则 `夹爪 open/close 状态机 + EE 速度过零` | 对拉链（单次抓持长行程）与门（单抓单转）退化为 1 段/episode | **双轨分段**：轨 A（零依赖，立即可做）= 夹爪事件 + 双臂任务系速度过零 + 固定时长上限；轨 B（感知就绪后）= 补约束坐标里程碑。**禁止主线任何一个数等待轨 B** | §6.7 |
| 14 | 施工图 §6 的 **G2**（③层 object-anchored 开环重放，2026-09-26，任务选叠衣） | 叠衣语义关键点检测器 5 周内不可能就绪 → 假 gate | 拆为 **G2a**（门+拉链，9-26，不可延，离线可做）与 **G2b**（叠衣，11-07） | §8.2 |
| 15 | 施工图 §0.6-B 实验 E1：`FR3 换夹爪 + 移动相机位姿 + 锁定一个关节` | 本体名作废；且**锁关节档按当前定义是稻草人**（`dual_out.txt` 把关节锁在**零位**，而 PiperX 零位是伸直构型 → 平凡 0%） | 主 plan 换为**单臂模式 reader**（在售 SKU，通过全部五条判准）；锁关节降为 plan B，且必须做锁定角 sweep | §6.2 |
| 16 | 施工图 §4.3 baseline 表脚注对 Retrieve-then-Steer 的定位（"同本体检索 SOTA / 注入机制来源"） | R-t-S 附录 D 已在**同款双臂 AgileX PiPER** 上做过 bimanual T-shirt folding（π0.5+Ours：in-domain 黄 T 恤 42.0→50.0，OOD 白 T 恤 36.0→46.0，每任务 50 trials） | 升级为**同硬件同任务的直接前作**；相关工作与 baseline 措辞同步升级；G2a 通过后立即 arXiv 占位 | §2.3 / §9 |
| 17 | v4 §1 "把记忆库灌到 **10⁴–10⁵** 条" | 按实际语料核算只到 10⁴–3×10⁴ | 据实收窄为 **10⁴–N_max 并明写 N_max**；规模曲线做对数下采样 | §6.7 |
| 18 | 施工图 §4.4 消融表（A1–A6） | 缺一行 | 新增 **A7 `④ + 腕部重解算`**；并新增 **A8 `coordination-oracle`**（第四桶） | §6.4 |
| 19 | 施工图 §4.2 主端点（12 任务 × 20 成对 trial，单一 pooled McNemar） | **配对有效性与统计头room 在任务集上系统性反相关**：门族配对理想但会天花板、产不出不一致对；叠衣族有头room 但初始褶皱物理不可复现 | 拆成两个预注册主端点：**(P-rigid)** 门+拉链走成对 McNemar；**(P-deformable)** 叠衣放弃 trial 级配对，改分层随机化 + 连续进度分 | §6.8 |
| 20 | 施工图 §4.2 "12×20=240 成对 trial 检测 10 pp、效力 80%" | 隐含假设不一致对比例 π_d≈0.30 从未声明；长时程可形变任务 π_d 可能到 0.5 → **n=392/arm** | π_d 写成预注册参数，G1 之前 pilot 实测，用 `n = 785·π_d` 重算 | §6.8 |
| 21 | 施工图 §4.5 P3 的任务级符号检验 `n=12 全同向 p≈0.0005` | **伪重复**：12 个变体只来自 3 个族、3 个物理物体；n_eff ≈ 3–5 | 检验层级改**族级**（混合效应 / cluster bootstrap）；靠**增加物体实例数与族数**提效力，不靠增加变体数 | §6.8 |
| 22 | v4 §8 叙事句中的 `a mobile manipulator can read from entries written by a fixed-base arm` | 本体名作废 | 见 §2.4 新叙事句 | §2.4 |
| 23 | v4 §7 风险表技术风险第②项 `真机双本体调试成本`（隐含"换本体"） | 两套独立台架，无换本体 | 改为"双平台并行运行成本 + 两具本体各一次基座微调" | §7 |
| 24 | 施工图 §6 "最可能烂尾的一环"整段论证（依赖移动底盘） | 理由链失效 | 新的最可能烂尾环 = **叠衣语义关键点前端**；G2a/G2b 拆分即针对它 | §8.2 |
| 25 | 施工图 §3.5 写入门控引用 R-t-S 的 `precision 0.970 / recall 0.678` | 借来的数字 | 用 VLAC-8b 在本文五族任务的 ~500 条留出 rollout 上自测 precision/recall 替换 | §5.6 |

## 0.2 v4 中**继续有效、本次不动**的部分（防止修订过度）

- **主张句的三个限定词**：*executable action content* / *written during its own deployment* / *no further update to its policy*。三个都不依赖硬件。**Abstract 红线不变。**
- **2×2 格局图**（持久×跨体可读）与"右上角空缺是结构性的"这一判断。硬件变更不影响格局。
- **SQ1 / SQ2 / SQ3** 三个科学问题的定义。
- **与 Retrieve-then-Steer 的边界声明**（注入机制非本文贡献）——但**措辞需加强**，见 §2.3。
- **E0**（基座微调任务集与记忆评测任务集不相交）——这是"零策略梯度"主张的唯一形式保证，**不可动摇**。
- **三轮威胁核查的结论**（RAM / RoboOS / RECAP 三个反例的处理）与 `threat_RAM_RoboOS.md` 的登记表结构。
- **v4 §9 参考文献表**（venue 已逐条核对）；本次只新增，不改旧条目。
- 施工图 §0.5 的页数预算表、§4.6 的指标定义式（IR / AR / HR / forced-vs-gated 双列）、§4.9 的四件事。

---

# 1. 工作条件（更新）

## 1.1 本体

**两套独立台架**：双臂 Piper 与双臂 PiperX。**不是同一台机器换臂**——这一点推翻了施工图关于跨本体 trial 单位成本的假设（§6.6）。

### Piper（已核实）

来源：`https://global.agilex.ai/products/piper` + AgileX 官方 URDF `agilexrobotics/agx_arm_urdf`（MIT，本地 `/tmp/agxurdf/piper.urdf`）

| 项 | 值 |
|---|---|
| DoF | 6（纯 6R，无升降柱/腰关节） |
| 负载 / 臂展 / 重复精度 | 1.5 kg / **626 mm**（URDF 算得 627.7 mm）/ 0.1 mm |
| 自重 / 价格 | 4.2 kg / $1,999 |
| 架构 | **Puma 型**：j1 立轴 → j2,j3 平行 pitch → **j4/j5/j6 球形手腕**（三轴交点，d(4,5)=0.00000 m，d(5,6)=0.00009 m） |
| 连杆 | base→j1 **0.123 m**；大臂 **0.28503 m**；小臂 0.25171 m；腕 0.091 m |
| 关节限位（度） | j1 ±150 / j2 0…180 / j3 −170…0 / j4 **±100** / j5 **±70** / j6 ±120 |
| 夹爪法兰安装 | rpy=(0,0,0) |

### PiperX（已核实，但见 §1.6 待确认 #1）

来源：`https://global.agilex.ai/products/piper-x` + `agx_arm_urdf/piper_x/`

| 项 | 值 |
|---|---|
| DoF / 负载 / 重复精度 | **6 / 1.5 kg / 0.1 mm（与 Piper 全同）** |
| 臂展 | **669 mm**（URDF 668.3 mm），仅差 **6.9%** |
| 自重 | **官网未列，查不到，需用户提供** |
| 架构 | **UR 型**：j1 立轴 → **j2,j3,j4 三轴互相平行**（\|cos\|=1.000）→ j5∩j6 交点，但 **j4 到腕点有 74.66 mm 固定偏置（offset wrist）** |
| 连杆 | 大臂 **0.28503 m（与 Piper 完全相同）** → 0.27364 → **0.07466** → 0.035 |
| 关节限位（度） | j1/j2/j3/j6 与 Piper **相同**；**j4 ±89（Piper ±100）**；**j5 ±89（Piper ±70）** |
| 夹爪法兰安装 | **rpy=(0,0,π/2)** ← 与 Piper 差 **90°**，实测值 13.6 个百分点的层③可行率 |

**关键：j4 的物理语义不同。** Piper 的 j4 是腕部 **roll**；PiperX 的 j4 是肘平面内的第三个 **pitch**。同名关节不对应。两者**都**满足 Pieper 判据、**都**有闭式解，但走两条不同分支（Piper 靠末三轴交点解耦，PiperX 靠中间三轴平行），8 个解分支语义不可一一对应。

**URDF 与官网互相印证**（说明这套 URDF 是在售实物）：Piper 连杆段求和 627.7 mm vs 官网 626 mm；PiperX 668.3 mm vs 官网 669 mm。

### 两者的可测量差异汇总（全部本次一手复算，`/tmp/agxurdf/`）

| 量 | 值 | 脚本 |
|---|---|---|
| 工作空间体素 IoU（法兰原点，2 cm 体素，20 万点 MC） | **0.528**；Piper 被 X 覆盖 72.2%，X 被 Piper 覆盖 66.3% | `analyze.py` |
| 全局近奇异比例（w<0.005，各 5 万构型） | Piper **58.1%** vs PiperX **47.1%**；cond>100 占 26.6% vs 22.8% | `analyze.py` |
| URDF 零位是否奇异 | Piper **是**（w=2e-6, cond=28198）；PiperX **否**（w=1.44e-3, cond=40.6） | `analyze.py` |
| 家居任务盒接受率（关节空间均匀采样） | **3.1–4.9%** | `taskspace.py` |

**任务盒定义**（躯干系）：x∈[0.20,0.65] m，y∈[−0.55,0.55]，z∈[−0.20,0.30]，夹爪接近轴与竖直向下夹角 <60°。

### 双臂台架（AgileX 官方 `dual_piper`，**本组台架待实测**）

- 左臂基座 xyz=(0.0075, **−0.285**, 0.01)，右臂 (0.0075, **+0.285**, 0.0)，rpy 均为 0 → **基座间距 570 mm，平行同向**（非内八字）。左右臂 z 差 1 cm，疑似建模残留。
- `slider_joint`：base→slider，z=**0.609 m**，但在该 URDF 中建成 **fixed**（AgileX 另有 `lifting_ws` 仓库，说明升降柱在别的产品线可动）。
- 立柱顶相机 rpy=(0, **0.87267**, 0) → **下俯 50°**。
- **官方 SRDF 只有单臂 group，没有双臂 group、没有双臂标定流程**，手眼标定只有单臂的 `handeye_calibration_ros`。→ **双臂协同约束的迁移没有现成工具，要自己写。**

### 官方软件资产（已核实可用）

- URDF/mesh：`agilexrobotics/agx_arm_urdf`（**MIT**），覆盖 piper / piper_h / piper_l / piper_x / nero / Revo2 灵巧手，每型号都有裸臂 URDF + 带夹爪 xacro + 带左右 Revo2 灵巧手 xacro。
- ROS2：`agx_arm_ros`（`arm_type:=piper` 统一支持所有型号含 piper_x），含 MoveIt2 完整配置。IK 插件是 **KDL 数值 IK**，不是解析 IK。
- SDK：`piper_sdk`（Python），README 提到固件 **S-V1.6-3 前后 DH 参数有新旧两版**（`dh_is_offset` 开关）与 `start_sdk_joint_limit` 软限位开关。
- **★ `agilexrobotics/openpi-agilex`**（Apache-2.0，34 stars，last push **2026-02-02**）：`scripts/` 下**同时**有 `aloha_inference-joint-ros2.py`（关节空间＝④层，94 KB）与 `aloha_inference-pose-ros2.py`（末端位姿＝③层，94 KB），以及 `piper_FK-ros2.py`（8 KB）、`piper_IK-ros2.py`（28 KB，pinocchio+casadi 数值 IK，含 `check_self_collision`）。**厂商已把③/④两套控制器在同一平台交付。这是本项目最大的一块免费午餐。**
- **PiperX 侧的 openpi 接入：官方零支持。** 唯一存在的是 `mamengyiyi/openpi-piperx`（**1 star**，last push 2026-06-12，分支 `codex/piperx-github-ready`——命名强烈提示是未经真机验证的 AI 移植）。**reader 侧全部要自己写**，见 §5.2。

## 1.2 数据

数百小时家居操作遥操语料，分布在两具本体上。**精确构成待确认（§1.6 #4）。**

## 1.3 任务

用户给出五个任务族：拉链收纳包（开拉链→放物→合拉链）、**叠衣服**、给垃圾桶套垃圾袋、开关微波炉门、开关洗衣机门。

**v5 的处理**：套垃圾袋**排除出 confirmatory**（§6.3）；拉链**条件性保留**（取决于是否有力/触觉通道）；叠衣在完整版是主力、在 MVP 中降为 exploratory。

## 1.4 算力

百卡（RTX 5090 + H20）。**关键约束（已核实）**：openpi 的 JAX 训练脚本 README 明文 "does not yet support **multi-node** training"（`scripts/train.py` 中只有 `jax.device_count()`，无 `jax.distributed.initialize()`）；PyTorch 路径支持 torchrun 多机但**明文不支持 LoRA / FSDP / 混合精度 / EMA / π0-FAST**。→ **"百卡"用不到单次基座微调上**，它的正确用途是横向并行（两具本体同时训 + 超参扫 + VLAC 全语料打分 + 离线 value 生成 + 仿真评测）。

官方显存门槛（README 表格原文）：Inference >8 GB；**Fine-Tuning (LoRA) >22.5 GB**（RTX 4090）；Fine-Tuning (Full) >70 GB（A100 80GB / H100）。

## 1.5 人力

**未知，且这是本课题最大的不确定项。** §8 给出 16–16.5 PM 的重估与 1 FTE 下的 MVP。**G0 当天必须落锤 FTE 数字**，否则不要启动完整形态。

## 1.6 待确认清单（**2026-08-24 用户答复后更新**）

> ✅ = 已确认并已折算进本文档；⚠️ = 已答复但引出新问题；⏳ = 仍待确认。
> 连锁后果见 §1.7。

| # | 待确认项 | 状态 | 结论与后果 |
|---|---|---|---|
| **1** | 用户的「PiperX」是不是官方 `piper_x`？ | ✅ **是官方型号** | **偏置腕 UR 型确认。** §3.4 的全部归因（层④←架构 / 层③←限位）成立；§2.1 的第四个限定词可写 `of a different kinematic family`；**R4 的残余风险（若为 piper_h/l 则谱系反转成压平）关闭**。不必再走"量臂展"这一步 |
| **2** | 两台固件 DH 版本；URDF FK 与真机一致性 | ⏳ **仍待确认** | 仍是单点故障（R9）。FK 残差 >5 mm 则 §3.4 全部离线数字作废。**G0.6 硬验收不可省** |
| **3** | 是否有腕部力/力矩或触觉通道 | ✅ **没有，但拉链任务已训练成功、数据可用** | **★ 拉链族保留在 confirmatory。** 见 §1.7 后果 A（已修订）。原先据 2112.06442 判定出局是**过度外推**——那是单臂 + 深度预测学习的设定，且其触觉替代的是"被夹爪遮挡的袋体形变状态"，而本文③层用**抓后夹爪位姿代理**（本体感觉，非视觉），§6.9 的成功判据也规定在释放回 home 后的静止帧上测量。**两处都绕开了那个遮挡机理。** 残余影响仅限 L2（卡阻恢复节律），见 §1.7 |
| **4** | 两具本体的任务重合度与小时分布 | ✅ **不构成约束**（可随机启动采集） | `T_align` 可按需现采，不必依赖存量语料的重合度。**D12 的 31 robot-hours 不能省，但不再是排期风险**（可与其他工作并行启动）。G3b 的推迟条件解除 |
| **5** | 本组两套双臂台架的真实几何 | ⏳ **仍待确认** | 全部双臂数字仍建立在官方 `dual_piper` 的 ±285 mm 平行同向上。**卷尺 + 标定板，1 小时的事** |
| **6** | 两台夹爪是否同款 | ⚠️ **不同款，有差异**（均为自带平移夹爪） | **既是加分项也是新混淆**，见 §1.7 后果 B。**这一条推翻了 §3.4 全部 φ 数字的一个前提**——官方 URDF 假设两台用同一款夹爪、仅安装 rpy 差 90° |
| **7** | 是否拥有 Revo2 灵巧手实物 | ⏳ 仍待确认 | D7 档是否可用 |
| 8 | 三族任务真实 exec+复位时长分布 | ⏳ 仍待确认 | §6.6 预算的最大不确定源。**可从存量语料直接统计，零成本** |
| 9 | 集群侧能否拉 HuggingFace 权重 | ✅ **可以**（有付费加速通道） | **R15 关闭。** VLAC-8b 写入门控路径确认可用；仍需独立 venv（ms-swift 3.3 与 openpi 依赖树冲突） |
| 10 | JAX 能否在 5090（sm_120）上跑 | ⚠️ **推理确认可跑；训练"应该可以"但未实测** | 推理可跑即 policy server / 仿真评测 / 离线管线全部可上 5090。**训练仍须跑 `debug_pi05` 十步实测**——JAX 对新架构的 kernel 支持常常推理先于训练就绪 |
| 11 | 两臂真实关节速度/力矩上限 | ⏳ 仍待确认 | URDF 里 effort=100 / velocity=5.0 是 SolidWorks 占位值 |
| 12 | 微波炉/洗衣机能否做一次性铰链标定 | ⚠️ **尚未做**；目前直接用采集动作训练，数据已验证可用 | **这是"未做"不是"不能做"**，见 §1.7 后果 C。门族③层的定义直接依赖铰链轴 |

## 1.7 本轮确认引出的四条连锁后果

### 后果 A ✅ 拉链族**保留**在 confirmatory —— §8.3 的 MVP 方案维持不变

> **修订记录（2026-08-24）**：本节初稿据 2112.06442 判定"无触觉 → 拉链出局"，**这个推断被用户以实测推翻，且推断本身有两处错误**。保留错误与更正过程，因为这类外推错误会重复发生。

**原推断**：2112.06442 报纯视觉 56.7% vs 视觉+触觉 93.3%（摘要逐字已核实），36.6 pt 缺口大于任何迁移增益 → 拉链不能进 confirmatory。

**为什么这个推断是错的（三条，按重要性）**：

1. **本文③层不依赖看见拉头。** §4.1 的定义是「拉头抓后**刚性附着假设成立**」——抓住之后夹爪位姿**就是**拉头位姿。这是**本体感觉，不是视觉**。2112.06442 里触觉替代的恰恰是"被夹爪遮挡的袋体形变状态"（原文："the gripper grasps the puller, which **hides the bag state**…"）。**那个遮挡机理对本文的条目抽取完全无影响。**
2. **成功判据也已绕开遮挡。** §6.9 已明确规定 Z1–Z3 "必须在释放并回到 home 位之后的静止帧上测量"，并注明理由正是这条遮挡发现。**写的时候考虑到了，判断的时候忘了用。**
3. **设定不可比。** 2112.06442 是**单臂 + 深度预测学习 + 少量演示**；本文是**双臂 + π0.5 级骨干 + 数百小时数据 + 三路相机**。双臂的稳定臂改变了几何，多视角改变了可观测性。**用前者给后者设天花板是过度外推。**

**并且 56.7% 对本文不是缺陷而是理想值**：§5.8 要求基座在 `T_eval` 上落在 **20–60%** 窗口。一个纯视觉、成功率 50–60% 的拉链基座正好在窗口正中，**headroom 天然存在，不需要人为制造**（与叠衣族同样情形）。

**残余影响（缩小到一处，仍须处理）**：**L2「拉链卡阻恢复节律」**（§6.5 的语言不可表达任务之一）依赖对**卡阻**的感知。无触觉时，卡阻只能靠视觉（布带咬入的外观变化）或电流/位置误差间接推断。
- **对策**：把 L2 的判定改为**可从关节位置误差检出**的形态（拉头推进受阻 → 指令位置与实际位置偏差超阈），这在无力传感器时依然可读；
- 若 L2 站不住，§6.5 仍有 L1 / L3 / L4 三条，**满足"≥3 个语言不可表达任务"的下限**，主张不受影响。

**结论：S 层维持 12 个变体（5F + 4D + 3Z），族数维持 3，§8.3 的 MVP（门 + 拉链 + 单臂 reader）维持原方案，工程量维持 9–10 PM。**


### 后果 B ⚠️ 夹爪不同款 → **§3.4 的全部 φ 数字需要重算**

官方 `agx_arm_urdf` 里 Piper 与 PiperX **用的是同一款平行夹爪**，两者只差 `gripper_base_joint` 的 rpy 90°（实测值 13.6 个百分点的层③可行率）。**现在这个前提不成立。**

夹爪不同款意味着 **TCP 相对法兰的变换不同**（指长、指宽、行程、可能还有安装深度）。而 §3.4 的每一个数——82.8° / 7.10 cm / 17.8° / 80.8% / 57.3%——都是在**法兰**或**假定同款夹爪的 TCP** 上算的。

**必须做（零机器人小时，但阻塞正文所有可行率数字）**：
1. 实测两台夹爪的 TCP 偏置（指尖中点相对法兰的 SE(3)），各测一次；
2. 把正确的 tool transform 接进 `redteam.py` / `taskspace.py` / `followup.py` 重跑；
3. **报"夹爪差异单独贡献了多少个百分点"**——把它从混淆变成阶梯上的一档。

**这同时是加分项**：§6.2 的 D2 档（"换夹爪指，<¥200"）**现在是免费且原生的**——两台本来就不同款，接触几何差异是真实产品差异，通过全部五条判准，比 3D 打印手指自然得多。§6.1 的三句话模板可以加一句：*两台连夹爪都不是同一款*，进一步强化"这是两台真正不同的机器"。

### 后果 C ⚠️ 无铰链标定 → 门族③层目前没有定义，但**可能可以追溯补上**

现状是"直接用采集动作训练"，即数据是④层（关节动作）形态，**③层所需的铰链轴 (â, o) 从未被记录**。

关键判断：**这是"未做"，不是"不能做"。** §4.3 给的方案 i（一次性标定，0.5 周）针对的是固定家具。所以真正要问的是一个新问题：

> **微波炉/洗衣机在整个数据采集期间有没有移动过？**

- **若没移动过** → 铰链轴可以**追溯标定**：现在去量一次轴的位置与朝向，套用到全部已采集的历史 episode 上。**存量数据直接变成③层可用，零重采。**
- **若移动过（换过位置/换过场次）** → 需要按场次分别标定，或退到方案 ii（在线估轴，ScrewNet / FlowBot3D，3–4 周）。

**这一条必须在 G0 当天问清楚**，因为它决定门族③层前端是 0.5 周还是 3–4 周，而门族在后果 A 之后是 confirmatory 的两根支柱之一。

**顺带一个可用的自检**：即使不做标定，也能从已采集的门任务轨迹**反推**铰链轴——门把手的运动轨迹是一段圆弧，对末端位姿序列拟合一个螺旋轴即可（最小二乘拟合共同旋转轴）。若多条 episode 拟合出的轴一致（残差小），既证明家电没移动过，又直接给出了轴。**这是零成本的离线检验，建议并入 §10 第 4 条一起做。**

### 后果 D ✅ 两条风险关闭，一条降级

- **R4 残余风险关闭**：PiperX 确认为官方偏置腕型号，谱系论证不会反转成压平。
- **R15 关闭**：HF 可达，VLAC 路径确认。
- **§1.6 #10 降级**：JAX 推理在 5090 上确认可跑 → policy server、仿真评测、离线 value 管线、对齐图训练全部可以放 5090，H20 专供训练。**训练侧仍须实测**（`debug_pi05` 十步，半天），因为 JAX 对新架构常常推理 kernel 先于训练 kernel 就绪。


---

# 2. 核心主张与生态位（是否需要改写）

## 2.1 三个限定词：全部继续成立

主张句（v4 §2 / 施工图 §1.2 的转轴句）：

> 尚未被展示的是这样一种持久存储：其中包含由机器人在其**自身部署过程中**写入的**可执行动作内容**，并且能被**第二个同样处于部署中的机器人**读取，而其 policy **不再进行任何进一步更新**。

**逐条检查**：

| 限定词 | 硬件变更是否影响 | 结论 |
|---|---|---|
| *executable action content* | 否。四层 value 全部含动作内容 | **不动** |
| *written during its own deployment* | 否。E0 保证 | **不动** |
| *no further update to its policy* | 否。冻结 π0.5 | **不动** |
| *a second **deployed** robot* | **是，且被削弱**。R-t-S 附录 D 已在同款双臂 AgileX PiPER 上做过检索记忆 + 冻结 π0.5 + 叠 T 恤 | **不动，但相关工作必须升级**（§2.3） |

**新增的第四个限定词（建议，防守性）**：把"a second deployed robot"改为"a second deployed robot **of a different kinematic family**"。理由：这一句把 R-t-S 的同本体结果显式排除在外，且我们能用 URDF 量化证明"different family"（§3.4）。**但注意**：这一句只在 §1.6 待确认 #1 的答案是 `piper_x` 时才能写。若答案是 H/L，改用"**of a different action-space dimensionality**"（单臂 reader 档）。

## 2.2 2×2 格局图：不改

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
   易失 │ MemoryVLA, LaMem-VLA,       │ RoboTTT, MimicDroid,      │
  （用完│ ReMem-VLA, MEM              │ Instant-Fold (2606.04269) │
   即弃）│ （episode 内工作记忆）        │ （无梯度读一条演示，不积累）│
        └────────────────────────────┴──────────────────────────┘
```

**唯一改动：右下角新增 `Instant-Fold (2606.04269)`。** 它是可形变物操作的 in-context imitation learning：给一条人类演示，策略**无梯度更新**地推断并执行多种折叠模式；时序对比预训练 + demo-conditioned **flow-matching transformer**。**这是"不更新参数地读取一条折叠经验"的最近先例，必须主动引用并划界**——其记忆是 episodic/context、用完即弃、不跨本体，正落在下半区。不引用会被点名。

## 2.3 与 Retrieve-then-Steer 的边界声明：**必须加强，这是本次最重要的相关工作变更**

**新核实的事实**（一手，`memory-vla/papers/10_retrieval_augmented_frozen/2605.10094.pdf`，附录 D.1/D.2/D.3 + 正文 §5.2）：

- 平台原文：`The ALOHA-PiPER platform follows an ALOHA-style bimanual setup and uses two 6-DoF AgileX PiPER arms with two-finger grippers`；另一平台 OpenArm 为 `two 7-DoF humanoid robot arms`。原文明说二者 `provide complementary testbeds for evaluating our method across different arm kinematics, gripper designs, and workspace layouts`。
- 任务含 **Bimanual T-shirt Folding**（ALOHA-PiPER）。
- 数字：π0.5 + Ours，in-domain 黄 T 恤 **42.0% → 50.0%**；OOD 白 T 恤 **36.0% → 46.0%**；平均 **39.0% → 48.0%**。每任务 100 条演示微调基座、8k–10k steps、bs=64、lr=2.5e-5，**每任务 50 trials**，评测时基座冻结、成对同初始状态。
- 长时程 4/4 全成功 18.0% → 24.0%，平均完成段数 1.54 → 1.94。
- 记忆容量消融：300 条轨迹，C ∈ {0,1k,2k,3k,4k,5k,∞}，超出用 FIFO。
- component-aware aggregation 形式为 `a_{i,h} = (Δp_{i,h}, Δr_{i,h}, g_{i,h})`（其 Eq.22），Δp 明文允许是 `end-effector position increments **or joint-angle increments**`，并声称支持 `end-effector pose control, joint-space control, and different gripper parameterizations`。

**三个后果**：

1. **它是同硬件、同任务的直接前作**，不再只是"注入机制提供者"。§II-C 与 baseline 表脚注必须升级。
2. **好消息**：39–48% 的基线成功率**正落在施工图 §4.1 要求的 40–60% headroom 窗口**，叠衣任务**不需要人为制造 headroom**（可省掉评测端扰动设计）。
3. **抢跑风险高于施工图当前点名的 RECAP/Dejavu**：他们已同时拥有 6-DoF PiPER 与 7-DoF OpenArm 两具异构本体、并在正文里点名二者 "different arm kinematics"，**做跨本体记忆只差一个实验**。→ **G2a 通过后立即 arXiv 占位 P1/P2/P3′ 的预注册预测。**

**同时是好消息的一条**：其 Δp 明文允许是关节角增量，且声称支持三种控制空间 → **本文把③层改成"锚点系下的接触点运动"后，仍能原样喂进其 Eq.(6)，统一读出接口不受影响。**

**边界声明的新措辞**（替换施工图 §3.4 的英文原句后半）：

> We adopt unchanged from [R-t-S] the aggregation, the intermediate-state initialisation of the flow sampler, the confidence-adaptive guidance strength, and the abstain-and-fall-back rule. We note that intermediate-state injection with a soft per-element mask also has an industrial implementation in GR00T N1.7's real-time chunking (`vel_strength`, exponential ramp), which further supports our position that the injection mechanism is not the contribution. What is not from that method, and what we describe here, is the decoding path that maps entries at different levels of abstraction into a common action-space prior, **and the change of coordinates that precedes aggregation for bimanual entries** (Sec. III-D).

## 2.4 新的叙事一句话

> Retrieval-augmented frozen VLAs now work, and a persistent store of successful chunks has already been shown to help a frozen $\pi_{0.5}$ fold shirts on a bimanual AgileX PiPER. But every such store is read by the body that wrote it. We ask what an entry must contain to survive a change of body. Each experience is written at four levels of abstraction under a body-agnostic key, and every level is decoded into the reader's own action space before injection. Two deployed bimanual platforms of **different kinematic families** — a spherical-wrist Piper and an offset-wrist PiperX, identical in DoF, payload and repeatability, differing by 6.9 % in reach — write to and read from one store in both directions. We report where along the spectrum the crossover lies, decompose the cross-body loss into key-side, limit-envelope and architecture terms, and report the per-trial memory-harm rate and the injection rate that make these numbers interpretable.

**注意措辞**："differing by 6.9 % in reach" 是**主动交出**最弱的一面，然后用运动学族反击。这比藏着强。

## 2.5 若 G0.5 不过：预注册的 fallback framing

**必须现在写进补充材料，不能等主线塌了再想。**

> **Cross-body memory admissibility.** 当两具本体足够相似时，外来条目在**检索侧看起来完全可用、在执行侧却部分不可用**；我们量化这个 admissibility gap，并给出一个**不更新参数**的拒绝准则。

- 主端点从 SR 换成 **harm rate**（读了外来条目后成功率低于 frozen base 的比例）与 **admissibility AUC**（用离线可行率 φ 预测该条目能否被本读者执行）。
- **为什么这个 framing 在小 gap 下反而更强**：条目看起来可用、实际不可用，正是最危险的情形。
- **为什么它不会被"用最近邻策略就能证"打掉**：拒绝准则必须在**采样器中间态**上生效（低置信度时不注入、部分维度不注入），这天然需要冻结策略 + 注入机制。
- **增量成本 ≈ 0**：复用 §6.2 的 D1/D2 档位与 §6.8 的 harm rate 协议。

---

# 3. 科学问题与可证伪预测（更新）

## 3.1 SQ1 / SQ2 / SQ3：定义不变，但 SQ1 的判定标准必须改

- **SQ1（可迁移性谱系 · 核心）**：技能记忆在哪个表示层级上本体无关？四层 value 各自的**跨本体迁移率**与**同本体精度**是多少？最优工作点在哪？→ **定义不变。但"最优工作点"的判定必须落在交叉点上，见 §3.2 的 P1′。**
- **SQ2（key 对齐）**：跨本体检索的瓶颈在 key 侧还是 value 侧？→ **不变。**
- **SQ3（共享记忆池的净效应）**：双本体读写同一库，1+1>2 还是互相污染？→ **不变。**

## 3.2 P1 → P1′：把"单调 + 交叉点"改成"交叉点是唯一的主张"

**v4 的 P1**（施工图已改过一次）：cross-body SR 随抽象度上升；same-body SR 由内容保真度而非抽象度主导。

**问题**：这个措辞让"cross-body 单调上升"看起来是主张的一部分。但**单调上升不是 finding**——GR00T N1.7 的 README 已经用自己的话主张过（"N1.7 adopts a **relative end-effector action space** shared across robot and human embodiments… Representing actions as **deltas from the current pose** … is **a key factor in the model's cross-embodiment performance**"），并已参数化到每个 action key（`ActionConfig(rep=RELATIVE, type=EEF)`）。

> **P1′**：存在一个抽象层级 ℓ\*，使得 (a) 在**同本体**读取上 `SR_same(ℓ\*+1) > SR_same(ℓ\*)`（更具体的层更精确），且 (b) 在**跨本体**读取上 `SR_cross(ℓ\*) > SR_cross(ℓ\*+1)`（更抽象的层更可迁移）。**即两条曲线在 ℓ\* 处交叉。** 我们预测 ℓ\* 落在 ③（锚点系接触点运动）与 ④（关节 chunk）之间。

**为什么这个改写是必要的**：单调下降的曲线**不是发现**；交叉点才是。**没有哪一层永远最好**——这才是"谱系"而不是"层级排序"。

**判定（预注册，写进 §IV）**：
- (a) 由 **G0.5** 判定：`SR_same(④) − SR_same(③) ≥ 10 pp`（同本体，成对，McNemar）。
- (b) 由主端点判定：`SR_cross(③) − SR_cross(④) > 0`（pooled，任务层 cluster bootstrap CI）。
- **若 (a) 不成立 → 四层谱系框架当场死亡，切 §2.5 的 fallback framing。不等 G4。**

**为什么 (a) 有真实风险**（必须诚实写在这里）：在 6-DoF 无零空间的臂上，**同本体** FK→IK 几乎无损（本次实测 position-only 可行率 100.0%），因此同本体的③与④很可能生成数值上几乎相同的轨迹，Δ≈0。**这是本课题最大的单一风险，而它的检验成本是 0 机器人小时。**

## 3.3 P3 → P3′：机理换掉，且升级为"可离线预测"

**v4 的 P3 已死**：机理"定基记忆是移动记忆的子集"在本硬件上被证伪（工作空间体素 IoU=0.528，互不包含）。

> **P3′**：跨本体迁移的方向不对称性，由**读者的关节限位包络对写者任务盒位姿的覆盖率**决定，并且可以在**不跑任何机器人**的前提下、用纯离线运动学统计量预测其方向与**逐任务排序**。

**离线预测量 φ**：对每个任务 t，把写者一侧该任务的全部轨迹逐帧做 `FK(writer) → 锚点系位姿 → IK(reader)`，得到 per-task 层③可行率 `φ(writer→reader, t)`。

**已算出的全局值**（`/tmp/agxurdf/followup.py`，任务盒内）：

| 方向 | 层③ IK 可行率 |
|---|---|
| **Piper → PiperX** | **80.0%** |
| **PiperX → Piper** | **57.3%** |
| 差 | **22.7 个百分点** |

**机理（改写后）**：PiperX 的 j4/j5 限位是 ±89°/±89°，Piper 是 ±100°/**±70°**。**Piper 的 j5 只有 ±70°，是全臂最紧的关节**。所以作为读者，PiperX 的限位包络更宽容；作为读者，Piper 更挑剔。**这不是"工作空间大小"的差异**（那已被 IoU 证伪），是**限位包络覆盖率**的差异。

**三级检验（力度递增）**：
1. **方向检验**：任务级配对，`Δ(Piper→X) > Δ(X→Piper)` 的符号一致性。**但必须做族级聚类**（§6.8），naive n=12 是伪重复。
2. **★ 排序检验（本设计的核心增量）**：逐任务的离线 φ 差值 与 实测 Δ 差值 的 **Spearman 秩相关**（族级 cluster bootstrap CI）。若显著，主张升级为**"一个离线运动学统计量可以预测在线迁移不对称，无需部署"**——这比"存在不对称"强一个量级，且对系统集成者有直接价值。
3. **机理确证对照（替代已失效的"锁底盘"）**：把双方写入条目都限制在**两者工作空间的交集核**（体素 IoU 的 52.8%）内重跑。若不对称性消失 → 机理坐实为可达性/限位覆盖，而非条目质量或基座能力差异。**免费**（只是对条目做一次过滤），且与原"锁底盘对照"结构同构。

**偏差控制（沿用施工图 §4.4）**：条目按本体配平、下采样到 min。理由：写入门控 recall 不足且两体基座 SR 不同 → 自然写入率必然不等，这是 P3′ 的隐藏系统性偏差。

**若被推翻**：报 "no directional asymmetry detected at this power"，并补一句——**同形态本体对不存在"工作空间包含"这一在定基↔移动设置中驱动不对称的机制，这本身是一个可发表的限定性发现**，且不伤主线。

## 3.4 ★ 新增 P5：跨本体损失的两项归因，且两项机理不同

**这是本次修订最重要的新增，也是对"你们的 gap 就是一份 spec 差异"这一刀的正面回答。**

> **P5**：层④的跨本体失败由**运动学架构**造成（任何**固定的、无观测条件的**关节空间标定映射的最优残差都超出任务容差一个量级）；层③的跨本体失败由**关节限位包络**造成（放宽限位即消失）。**两者不是同一个原因。**

### 证据 A：层④ ← 架构（本次一手复算，`redteam.py`，364 训练对 / 146 留出，IK 最近分支配对，**对标定方法最有利**）

| 标定映射 | 参数量 | 位置残差中位 | **姿态残差中位** | 姿态 p90 |
|---|---|---|---|---|
| 朴素复制 `q'=q` | 0 | 23.55 cm | **82.8°** | 126.7° |
| 逐关节仿射 `q'=s⊙q+b` | 12 | 11.11 cm | **52.4°** | 79.0° |
| **全线性 `q'=Aq+b`** | 42 | **7.10 cm** | **17.8°** | 38.7° |
| sin/cos 提升线性 | 114 | 6.12 cm | 16.0° | 38.3° |

**拟合出的逐关节尺度**：`s = [0.919, 1.010, 0.836, **−0.012**, **−0.064**, 0.638]`
**这行数字比 82.8° 更有说服力**：j4/j5 的尺度约等于零，**最小二乘对腕部关节直接放弃拟合**。这是"同名关节语义不同"的直接定量证据（Piper j4 = 腕 roll，PiperX j4 = 肘平面 pitch），应做成一张图。

**论文里的正确措辞**（可证伪、可复现、不夸张）：
> 任何固定的（无观测条件的）关节空间标定映射的最优残差仍达 **7.1 cm / 17.8°**，超出任务容差一个量级。

**绝对不能只报 82.8°**：这是 by-construction 的稻草人，审稿人第一句话就是"你标定了吗"，5 分钟工作量、落差 80%。被发现后不是数字错误，是诚信问题。**必须由论文自己先说出来。**

### 证据 B：层③ ← 关节限位（本次一手复算，`redteam2.py`，n=250，restarts=14）

| 条件 | 层③可行率 |
|---|---|
| PiperX 真实关节限位 | **80.8%** |
| PiperX 限位放宽到 ±189°（几何不变） | **100.0%** |

→ **架构对层③失败的贡献是 0.0%，全部（19.2 pt）来自关节限位。**

**逐关节触限归因**（成功样本中位于限位 3° 以内的比例）：`[0, 0, 0.015, 0, 0, 0.030]` → 成功样本几乎不贴限位，说明失败集中在**被限位整块切掉的那部分位姿**，而非边缘构型。这支持"包络覆盖率"而非"边缘数值问题"的解释。

### 证据 C：80% **不是** IK 容差伪影（本次新做，解决两份对抗审查之间的矛盾）

一份对抗审查指出 `RESULTS_taskspace.txt` 里失败样本的位置残差中位只有 0.23 cm，因此 80% 可能是把 1 mm 容差判成"结构性不可行"的伪影。**本次直接扫了容差**（`redteam.py` B 部分，n=200）：

| 位置容差 / 姿态容差 | 层③可行率 |
|---|---|
| 0.10 mm / 0.06° | **80.5%** |
| 1.00 mm / 1.00° | **80.0%** |
| 3.00 mm / 3.00° | 81.5% |
| 5.00 mm / 5.00° | 81.5% |
| **10.00 mm / 10.00°** | **86.0%** |

**结论：容差放宽 100 倍只买到 +6 个点。80% 不是容差伪影。** 那个 0.23 cm 是阻尼最小二乘求解器在**局部极小**处的终止残差，不是"存在一个 2.3 mm 邻域解"的证据。**这张表必须放进补充材料，预先堵掉"IK 容差调出来的"这一刀。**

### 对论文的直接后果（三条，必须执行）

1. **正文描述本体差异时**：不写"连杆长度不同"；也**不写**"层③的失败源于不同运动学族"。正确写法是两句话：*层④*的失败源于不同运动学族（球腕 Puma vs 偏置腕 UR，Pieper 判据走不同分支，同名关节语义不同）；*层③*的失败源于关节限位包络（Piper j5 ±70° 是全臂最紧关节）。
2. **§V-C 的 oracle 阶梯必须把 `Δ_retarget` 拆成两项**：`Δ_limit`（限位受限）与 `Δ_geom`（几何不可达）。实测为 19.2 pt + 0.0 pt。这一拆分是免费的（同一批离线数据），且它把一个可能被 20 行代码打穿的地方变成一个自己给出的测量。
3. **若坚持保留 "architecture" 叙事作为层③的解释，就必须找到一个架构真正起作用的可测量**（IK 解分支数、零空间维数、奇异面拓扑）并证明它对某个下游指标有影响。**否则删掉这个叙事。**

## 3.5 P2 与 P4：不变

- **P2**：跨本体损失由 retrieval + retargeting 两项主导，而非 value 不可执行。检验方式 = oracle 阶梯（施工图 §4.5），但**新增第四桶**（§6.4 的 A8 `coordination-oracle`）与 `Δ_retarget` 的两项拆分（§3.4）。
- **P4**：共享池仅在 value 层级 ≥② 时净正；③–④ 层共享产生负迁移。三条件（own / shared tag-blind / shared tag-aware）不变。

## 3.6 预测汇总表（替换 v4 §4 的 P1–P4 列表）

| # | 预测 | 检验 | 何时判定 | 被推翻 → 论文形态 |
|---|---|---|---|---|
| **P1′** | 同本体 ④>③ 且跨本体 ③>④，即两曲线交叉于 ℓ\* ∈ (③,④) | (a) G0.5 同本体成对；(b) 主端点 pooled | **(a) G0.5，2026-09-05** | **切 fallback framing（§2.5）** |
| **P2** | 跨本体损失主要在 key + retarget，非 value 不可执行 | oracle 阶梯（五级 + 第四桶，`Δ_retarget` 拆两项） | G5 | "检索可救、动作不可救"，重心移到 retarget 与分层回退 |
| **P3′** | 方向不对称由读者限位包络覆盖率决定，且可由离线 φ 预测方向与**逐任务排序** | 族级符号检验 + **Spearman 秩相关** + 交集核对照 | G6 | 报 "no asymmetry at this power"；补"同形态本体对无工作空间包含机制"这一限定性发现 |
| **P4** | 共享池仅在 ≥② 层净正 | 三条件 × 层级 2×3 表 | G6 | "在此规模下未观测到跨体串扰"（更好的结果） |
| **★P5** | 层④失败←架构（标定后仍 7.1 cm/17.8°）；层③失败←限位（放宽即 100%） | **已由离线实测支持**；真机侧只需确认 FK 一致性（§1.6 #2） | **已成立**（待真机 FK 验证） | 若真机 FK 残差 >5 mm → 全部离线数字作废，P5 撤回 |

---

# 4. 四层 value 的新定义

## 4.0 统领性的改写

**把 ③ 从 "object-anchored EE deltas（物体系下末端位姿增量）" 改写为 "anchor-frame task-point motion（锚点系下任务点运动）"。**

理由：原定义把③绑死在"存在一个 6-DoF 刚体物体位姿"上。这个前提在新任务集上**四选一才成立**（只有拉链的拉头满足，且仅在抓后）。

> ③ = **受控接触点（们）的轨迹**，表达在一个**低维、任务相关、与本体无关的几何锚点系**中；存在约束坐标时退化为该标量剖面；双臂情形额外存两接触点间的相对变换 `T_rel(t)`。

**四类任务的锚点**：铰链螺旋轴（一维 θ）→ DLO 弧长站（一维 s）→ 语义关键点元组（衣物）→ SOI 环（袋）。

**代价（必须进施工图 §346 的诚实清单）**：这一族表示（point tracks / object flow / semantic keypoints）**本身不新颖**，有 9+ 篇独立先验，且**全部自带跨本体证据**：ATM (2401.00025)、Track2Act (ECCV'24, 2405.01527)、Im2Flow2Act (CoRL'24, 2407.15208)、MT-π (2501.06994)、3DFlowAction (2506.06199)、PointAction (2606.03943)、ContactFlow (2607.26579)、Point Policy (2502.20391)、P3-PO (2412.06784)。**收益**：P1′ 的可信度上升（该族表示确证跨本体可读）。**本文新颖点收窄为"把它做成持久、自写入、跨本体可读的记忆条目"。**

## 4.1 四类任务 × 四层的定义表

| | **铰接门**（微波炉/洗衣机） | **拉链**（收纳包） | **叠衣**（T恤/衬衫/裤/毛巾） | **套垃圾袋** |
|---|---|---|---|---|
| **① 语言** | `"open the microwave door"` | `"close the zip on the pouch"` | `"fold the shirt in half"` | `"line the bin"` |
| **② 子目标** | `[(grasp, handle), (rotate about joint_id by Δθ), (release)]`（沿用 Kinematic-aware Prompting 2311.02847 的"kinematic joints + contact location"统一文本表示） | `[(stabilize fabric at s0), (grasp slider), (advance to s1), (regrasp), (advance to L)]`（序数弧长站，与 BUDS 的 stabilize/act 分工吻合） | `[(pick keypoint_i) → (place at keypoint_j 或 keypoint 系下偏移)]`（沿用 CLASP 2507.19983 的语义关键点词表） | `[(grasp rim_A), (grasp rim_B), (open to area A), (evert over bin lip)]` |
| **③ 锚点系接触点运动** | **锚点 = 铰链螺旋轴 (â, o)**；③ 塌缩为 `θ(t) ∈ R^T` + 固定抓取偏置 `g_handle ∈ SE(3)`。**从 6T 个数降到 T 个数（~2 KB → ~100 B）** | **锚点 = DLO 轨道弧长坐标**；③ = `s(t)` 剖面 + 法向偏差 ε(s)（+ 理想情况下的张力/接触力通道）。拉头抓后**刚性附着假设成立**——四类里唯一保住原前端的可形变任务 | **锚点 = ≥3 个语义关键点构造的系**（例：原点在下摆中点，x̂ 由左下摆指向右下摆，ẑ 取桌面法向）；③ = **被抓物质点（们）相对该系的轨迹** | **锚点 = SOI 环**（袋口边缘环）。**无成熟检测器** |
| **③ 双臂** | `(T_abs(t), T_rel(t))`，锚点刚性 → 无松弛 | 同左，紧松弛 ±2 cm/5° | 同左，松松弛 ±10 cm/20° | 同左 |
| **④ 关节 chunk** | 双臂 14 维物理单位（每臂 6 关节弧度 + 1 夹爪 [0,1]） | 同左 | 同左 | 同左 |
| **③ 适用性** | ✅ **最强**（约束坐标一维，前端最便宜） | ✅（抓后） | ⚠️ 需关键点检测器 | ❌ **不适用，排除** |
| **②/③ 是否可分** | ❌ **几乎退化为同一件事**（②=`rotate by Δθ`，③=同句加 θ(t) 剖面）→ **谱系压平的第二个来源** | ✅ | ✅ **最能分开** | — |

## 4.2 为什么③在铰接体上比 6-DoF 物体位姿更好用（可写进 §III 的论证）

**几何论证**：单自由度旋转铰接体的位形空间是 S¹ 的一个区间。给定轴 (â, o) 与把手到轴的半径 r，末端接触点整条路径由标量 θ(t) 唯一生成。**其余 5 个自由度由约束规定而非由记忆规定**——记忆只需存"开到多少度、什么角速度剖面、在哪个角度有阻尼/卡扣"，这恰是部署经验里真正可复用的部分。

**对前端误差的敏感度结构性更低**：自由刚体的轨迹在物体系内 6 自由度无约束，位姿估计误差全额传导到③层。铰接体只有沿弧长一个方向的误差是表征误差，法向误差要么被柔顺吸收、要么变成内力。

**经典引文（Crossref 已核）**：Task Frame Formalism（Bruyninckx & De Schutter, IEEE T-RA 1996, DOI 10.1109/70.508440）——把任务分解到附着于**约束**（而非物体）的任务坐标系；Task Space Regions（Berenson et al., IJRR 2011, DOI 10.1177/0278364910396389）——受约束任务应指定为任务空间中的**流形/区域**而非位姿。

**必须写进论文的诚实警告**：门固定于世界、物体系静止，这是**最容易的一档**；而且门任务上②与③几乎退化为同一件事。**门任务能证明③可定义，但压不出②/③差异。** 这必须写成**预测**而非意外，见 §4.5。

## 4.3 感知前端：需要什么、工程量多大

| 任务 | 需要的前端 | 可复用资产 | 估工时 | 判定 |
|---|---|---|---|---|
| **门** | 铰链轴 (â,o) + 开合角 | **方案 i：一次性标定**（固定家具，标定夹具+尺量一次）；**方案 ii：在线估轴** ScrewNet (2008.10518, ICRA'21，螺旋理论统一 revolute/prismatic，不需先验知道类别) / FlowBot3D (2205.04382, RSS'22 Best Paper Finalist，Sawyer 上零微调部署) / Ditto (2202.08227, CVPR'22 Oral) / 在线轴估计+SAM2 (2409.16287) / GSAM (2605.30740, PPSN'26，50 hinge 任务 ×5 类 ×50 配置，成功率比最优基线 +36.0%) | **i：0.5 周；ii：3–4 周** | 全套里**最便宜、最可辩护**。confirmatory 走 i，ii 放 exploratory |
| **拉链** | 拉头位姿（抓后夹爪代理即可）+ DLO 轨道弧长 + **力/触觉** | mBEST (2302.09444, RA-L'23) / DLOFTBs (2302.13694, ICRA'23) / UniStateDLO (2512.17764) | **4–6 周 + 硬件风险** | 纯视觉会撞上 2112.06442 的遮挡墙（原文：`the gripper grasps the puller, which hides the bag state … making it difficult to obtain information to perform the task by vision alone`；**纯视觉 56.7% → 视觉+触觉 93.3%**）。**无力通道则降 exploratory** |
| **叠衣** | 语义关键点检测器 + **规范化前缀** | 2401.01734（RA-L，合成训练 **64% AP / 18 px**；真实微调后 **74% mAP / 9 px**）；2606.06292（关键点 MPE **1.7615 px**，称无需微调可迁真实布料）；2306.14553（IROS'23，**仅 10 分钟人操作视频**训练，抓取成功率折叠件 92%/皱缩件 80%/三件堆 50%）；**Flat'n'Fold (2409.18297)** 直接当离线评测集（1,212 人类 + 887 机器人演示、44 件衣物、8 类，自带 grasping-point prediction 与 subtask decomposition 两个 benchmark） | **3–4 周** | 资产支持最好。**但 2401.01734 的检测器只对 "almost-flattened" 布料有效**，皱缩态 OOD → **必须把 Cloth Funnels (2210.09347) 式规范化写进任务协议**（SpeedFolding, IROS'22 走同一路线：4300 条标注后平均 120 s 内从任意皱缩构型折好，成功率 93%） |
| **套袋** | 袋口 SOI 环检测 | **无现成检测器**；AutoBag (2210.17217, ICRA'23) 需 **UV 荧光标记**做自监督标注，且"打开袋子并放入至少一件物体"仅 **16/30 ≈ 53%** | **5–8 周，定制** | **排除出 confirmatory** |
| 共用底座 | 视频分割 + 点跟踪 | SAM 2 (2408.00714)、CoTracker (2307.07635)、TAPIR (ICCV'23, 2306.08637) | 1–2 周集成 | **风险未量化**：查不到任何在布料自遮挡下 benchmark 通用点跟踪器的论文，drift **必须自测**（建议用 Flat'n'Fold 多视角序列，零采集成本） |
| 相机外参若缺失 | — | **CalibAll (2511.17001)**：training-free、robot-independent 离线外参标注（temporal PnP + 可微渲染精化），已用于 4 平台 16 数据集约 97K episodes | — | ③层需要 camera→anchor 外参，这条能省一大块工 |

## 4.4 替代"刚体附着假设"的正确写法（施工图 §3.2/§3.9-D2 的改写）

抓住布料后不知道物体位姿，但**确切知道抓住了哪个物质点**，而夹爪位姿正好给出该物质点的精确轨迹。所以布料上的③应写成：

> **被抓物质点（们）相对关键点锚定系的轨迹**——形式上就是 point-track / flow 表示。

这保住了 D2 的 3 周工时估计（不需要 6-DoF 位姿估计），同时对布料是**正确的**。

## 4.5 ②层的两套 anchor 原语词表（必须显式定义，否则②层数字不可比）

施工图 §3.2 的②示例是 `(translate, +0.15 m along handle axis)`——**这套原语在布料上无对应物**。

| 类 | 原语 | 沿用 |
|---|---|---|
| 铰接 / DLO | `(primitive, joint_id 或 arc_station, Δθ 或 Δs)` | Kinematic-aware Prompting (2311.02847, ICRA'24)：把铰接物统一表示为**含 kinematic joints + contact location 的文本描述**；48 实例/16 类别，8 个未见类别零样本 |
| 可形变 | `(pick keypoint_i) → (place at keypoint_j / keypoint 系下偏移)` | CLASP (2507.19983；早期版 2408.08160 为 ICRA'25)；BiFold (2501.16458, ICRA'25)；MetaFold (2503.08372，**显式把 task planning 与 action prediction 解耦**，即②/③分层已被证明能提升多类别泛化)；FoldNet (2505.09109) |

**统一形式**：`(contact point, target displacement in anchor frame)`。
**但必须显式声明两套 anchor 词表**，否则 Table 里②层在两类任务上的数字是苹果比橘子，R2-B8（任务集不可比）会直接复活。

## 4.6 ④层的重新定义（防止被 GR00T EmbodimentTag 吃掉）

**v4 写的是"关节空间动作 / action-expert 潜码"。"潜码"必须删掉**——那正是 GR00T 的 per-embodiment action head 在做的事，照原样写，评审会说"这就是 EmbodimentTag"。

**已核实的 GR00T 机制**（`gr00t/model/modules/embodiment_conditioned_mlp.py`）：
```python
class CategorySpecificLinear(nn.Module):
    def __init__(self, num_categories, input_dim, hidden_dim):
        self.W = nn.Parameter(0.02 * torch.randn(num_categories, input_dim, hidden_dim))
```
用在 `state_encoder` / `action_encoder` / `action_decoder` 三处。**新本体 = 一片全新随机初始化的 state/action 编解码权重，必须用该本体数据训练。GR00T 没有零样本跨本体动作解码。**

> **④ = writer 机器人写下的原始关节指令（物理单位），reader 侧不允许有任何被训练过的解码器；唯一允许的桥是基于模型的（非学习的）FK/IK retarget。**

这样④的意义从"另一种表示"变成"**测量原始关节内容失效得多彻底**"，而 §3.4 的证据保证这个失效可测、量级足够大。

**并且这给了 Intro 一句最好用的对照**：GR00T 用"**更新参数**"解决跨本体，而本文的主张恰恰是"**不更新策略参数**"。建议在 Intro 直接引用。

## 4.7 条目 schema：直接采用 RDT-1B 的 128 维布局

无论策略用哪个，记忆条目的③④两层按 RDT `configs/state_vec.py` 的 `STATE_VEC_IDX_MAPPING` 存（`STATE_VEC_LEN = 128`）：

| 区间 | 内容 |
|---|---|
| [0,10) / [10,15) | 右臂 joint pos / 右夹爪（`gripper_open`=10） |
| [15,25) / [25,30) | 右臂 / 右夹爪 joint vel |
| [30,33) / [33,39) | 右 **EEF pos** x,y,z / 右 **EEF 6D pose** |
| [39,42) / [42,45) | 右 EEF 线速度 / 角速度 |
| [50,100) | **左臂完全对称的同一套** |
| [100,103) | base 线速度 x,y + 角速度 |
| [45,50) / [103,128) | reserved |

配套 `action_mask`（0-1 float）标记有效维。

**收益四条**：③④天然并列可比；按层消融只需改 mask；**双臂对称布局天然承载协同约束**（两臂写在同一条向量里，检索与注入以整条向量为单位）；这是**最干净的公开先例**。

**★ 一条必须写进 §IV 正文（不是实现细节）的技术决定**：
> ④层一律存**物理单位**（关节角弧度、夹爪 [0,1]），**绝不存归一化值**；读出时由读者用自己的 norm stats 重新归一化。

理由：两具本体各算 norm stats 会导致同一物理动作在两边归一化数值不同，④层的跨体失败中会混入**纯归一化失配**——审稿人一眼能看穿的平凡混淆。

---

# 5. 基座模型与训练方案

## 5.1 选型：π0.5，走 `agilexrobotics/openpi-agilex`

**硬约束筛选**（六个 arXiv ID 全部经 `export.arxiv.org` API 核实标题与日期）：

| 候选 | arXiv | flow/diffusion 采样器 | 双臂 | 开源权重 | Piper 适配 | 注入点 |
|---|---|---|---|---|---|---|
| **π0 / π0.5 (openpi)** | 2410.24164 / 2504.16054 | ✅ flow matching | ✅ 14 维 | ✅ | ✅ **厂商官方** | ✅ 易 |
| GR00T N1.7 | 2503.14734（论文是 N1） | ✅ flow matching DiT | ✅ | ✅ Apache 2.0 | ❌ 无 | ✅✅ 已内建 RTC API |
| RDT-1B | 2410.07864 (ICLR'25) | ✅ DPM-Solver（**非 flow**） | ✅ 专为双臂 | ✅ | ⚠️ Mobile ALOHA | ⚠️ 仅 5 步，`prediction_type: sample` |
| SmolVLA | 2506.01844 | ✅ flow matching | ⚠️ 先验弱 | ✅ | ❌ | ✅ |
| OpenVLA-OFT | 2502.19645 | ❌ **L1 回归** | ✅ | ✅ | ❌ | ❌ **无中间态** |

**OpenVLA-OFT 直接出局**：OFT recipe 是 "parallel decoding, action chunking, continuous action representation, and a simple **L1 regression**-based learning objective"，没有采样器，不存在可注入的中间态。只能当 baseline（其论文在双臂 ALOHA 上以默认 recipe 击败 π0 和 RDT-1B 达 15% 绝对成功率）。

**选 π0.5 的四条理由（按权重）**：
1. **只有它有厂商官方维护的双臂 Piper 部署链路**，且③/④两套控制器（`aloha_inference-pose-ros2.py` / `-joint-ros2.py`）与双臂 FK/IK（pinocchio+casadi，含自碰撞检查）都已交付。**③ vs ④对比需要的正是"同平台上的关节控制器 + 位姿控制器"。**
2. flow 采样器干净（§5.2）。
3. **`pi0_aloha_towel` 检查点存在**："can fold diverse towels 0-shot on ALOHA robot platforms"——给叠衣任务托底，也是可形变物先验的现成探针。
4. LoRA 22.5 GB，5090 可跑。

**退路（按触发条件）**：
- **触发：JAX 打不动 5090/H20，或必须多机** → 退 **GR00T N1.7**（纯 PyTorch、torchrun 多机）。代价：自写两份 modality config；**且有一条硬性工程阻塞**——官方 `getting_started/policy.md` 明文 "Only **one** `NEW_EMBODIMENT` modality config may be registered **per Python process**"，writer(Piper) 与 reader(PiperX) 无法同进程共存 → 跨本体读写实验必须提前按双进程架构设计。另注：PyTorch 路径**没有 LoRA**。
- **不推荐 RDT-1B 当主基座**：仅 5 步 DPM-Solver 且 `prediction_type: sample`（预测 x0 不是速度场），注入粒度太粗；T5-XXL 依赖重。**但其 128 维统一向量作为条目 schema 采用**（§4.7）。
- **SmolVLA 仅作容量消融。**

## 5.2 注入点实现路径

**openpi 的 flow 采样器**（`src/openpi/models/pi0.py::sample_actions`，已核源码）：
```python
dt = -1.0 / num_steps          # num_steps 默认 10
x_0, _ = jax.lax.while_loop(cond, step, (noise, 1.0))
# step 内部：v_t = self.action_out_proj(suffix_out[:, -self.action_horizon:])
#            return x_t + dt * v_t, time + dt
```
carry 就是 `(x_t, time)`，`x_t` 即 flow 中间态。`num_steps` 是默认 10 的标量，**while_loop 可平凡替换为 Python for 循环**。

**执行顺序（半天成本，必须排在所有记忆库工程之前）**：
1. 把 `jax.lax.while_loop` 展开为 Python for 循环。
2. **数值一致性检查**：同 seed 下展开前后输出逐元素相同。
3. 这就是注入机制的最小可行验证。

**版本管理**：`openpi-agilex` last push 2026-02-02（距今 6.7 个月），已是冻结的旧 fork。**锁死一个 commit 并写进补充材料，明确声明不与上游同步**（之后的任何同步都是手工 merge）。

**PiperX 侧接入（3.5 周，必须指定一个人，第 1 周设硬验收）**：
- 官方零支持；`mamengyiyi/openpi-piperx` 只有 1 star、分支名 `codex/piperx-github-ready`（AI 移植未验证）。
- 要自己写：policy input/output 类、norm stats、PiperX 的 pinocchio+casadi FK/IK（官方那份 28 KB 的 `piper_IK-ros2.py` 是按 Piper 硬编码的，要按偏置腕重写）、piper_sdk 对 PiperX 的驱动、相机标定。
- **第 1 周硬验收（同时验掉 §1.6 的 #1 与 #2）**：PiperX 真机示教 20 个构型，读关节角，与官方 `piper_x` URDF 做 FK，与标定板实测 TCP 位姿对比，要求 **位置残差 <5 mm、姿态 <2°**。**不通过就不要往下写任何 policy 代码**——URDF 与真机对不上的话后面所有 IK 可行率数字都是废的。

**可参考的社区实现**：`mamengyiyi/openpi-piperx` 的 `src/openpi/policies/piperx_policy.py`：`PiperXInputs` 用 base + left_wrist + right_wrist 三相机，`PiperXOutputs(action_dim)` 裁剪回真实维度；config 支持 `action_dim ∈ {7, 14}`，`use_delta_joint_actions` 时 mask 为 `make_bool_mask(6, -1, 6, -1)`（每臂 6 关节增量 + 夹爪绝对值）。**可读、不可直接信。**

## 5.3 FFT vs LoRA：明确推荐 LoRA（openpi 口径），不做全参

### 两条训练路径互斥（这是本次最具决策价值的发现，README 原文）

- **JAX 路径**（`scripts/train.py`）：支持 LoRA、FSDP（`fsdp_devices`）、混合精度、EMA；**明文 "does not yet support multi-node training"**。
- **PyTorch 路径**（`scripts/train_pytorch.py`）：支持 torchrun 多机；**明文不支持 LoRA / FSDP / 混合精度 / EMA / π0-FAST**；训练精度只有 full-bf16 或 full-fp32。

→ **要 LoRA 就只能单节点 JAX；要多节点就只能 PyTorch + 全参 + 纯 bf16。**

### openpi "LoRA" 的真实可训练范围（核 `pi0_config.py:88-117` + `pi0.py:73-100`）

freeze filter = `All(PathRegex(".*llm.*"), Not(PathRegex(".*lora.*")))`。模块树是 `self.PaliGemma = nnx.Dict(llm=…, img=…)`，**SigLIP 在 `PaliGemma.img.*`，不匹配 `.*llm.*`**。因此实际：

- **冻结**：Gemma-2B LLM 主干 + 300M action expert 的非 LoRA 参数
- **全参训练**：**SigLIP So400m/14 视觉塔（约 4 亿参数）**、`action_in_proj` / `action_out_proj` / `state_proj` / `action_time_mlp_*`
- LoRA 秩：PaliGemma `rank=16, alpha=16.0`；action expert `rank=32, alpha=32.0`；均作用于 attn + ffn
- 可训练量 ≈ 4.3 亿 ×16 B/param ≈ 6.9 GB + 3.3B 冻结权重 → **与官方 22.5 GB 自洽**；全参 3.3B×16 B ≈ 53 GB + 激活 → **与官方 70 GB 自洽**

**→ openpi LoRA 不是"轻微改动"：它恰好训练了必须适配的部件（视觉前端 + 动作 I/O 投影），冻结了记忆注入所依赖的部件（LLM 语义先验 + action expert 运动先验）。**

### 三条独立证据同向支持 LoRA

**(a) E0 在结构上保证评测任务对基座是 OOD。** PriorVLA (2605.10925，基座就是 π0.5) 的 RoboTwin 2.0 Table 2（本地 PDF `pdftotext -layout` 直取）：

| | Easy-Few | Easy-Std | Easy-Large | Hard-Few | Hard-Std | Hard-Large |
|---|---|---|---|---|---|---|
| π0.5 | 29% | 67% | **89%** | 20% | 42% | 59% |
| PriorVLA（仅更新全参 25% 的参数） | 41% (+12) | 77% (+10) | **88% (−1)** | 31% (+11) | 53% (+11) | 65% (+6) |

**保留先验的方案只在"同分布 + 大数据"这一格输（Easy-Large −1），而本文按定义永远不在那一格。** 其原文："full fine-tuning treats the pretrained model mainly [as initialization] and lead to **prior forgetting, especially when evaluated under OOD scenes**"。

**(b) LoRA 的冻结边界恰好是本文需要的边界。** 全参微调会把 action expert 的去噪动力学收窄到 `T_base` 的动作模式上，直接削弱注入的可操控性。PriorVLA 的 `Trainable PE` 消融是直接实证：**可训练先验专家反而掉点**（Easy 73 / Hard 44，对比冻结的 77 / 49）；且 Random 冻结分支 43 ≈ w/o PE 42，证明增益来自预训练运动先验而非"多加一条分支"。

**(c) 工程可行性**：LoRA 22.5 GB 在两种卡上都宽裕，能把两具本体的微调**并行**跑完，省一半墙钟；全参 >70 GB 只能在 H20 上跑且逼近上限。

### 必须付的代价与对策

**openpi 没有 π0.5 的 LoRA 官方配置**（全部 `*_low_mem_finetune` 只有 π0 / π0-FAST；π0.5 的 6 个配置全是全参）。机制上支持（`get_freeze_filter` 挂在 `Pi0Config` 上、含 `pi05` 标志），但**属于自写未验证配置**：

```python
model=pi0_config.Pi0Config(pi05=True, action_dim=32, action_horizon=16),
freeze_filter=pi0_config.Pi0Config(
    pi05=True, action_dim=32, action_horizon=16,
    paligemma_variant="gemma_2b_lora", action_expert_variant="gemma_300m_lora",
).get_freeze_filter(),
ema_decay=None,   # LoRA 必须关 EMA（官方注释 "Turn off EMA for LoRA finetuning"）
```

**一个必须验证的坑**：π0.5 的 AdaRMS 调制层是 `RMSNorm` 内的 `nn.Dense`，路径在 `PaliGemma.llm.*` 下（`pre_attention_norm_1` / `pre_ffw_norm_1` / `final_norm_1`），会被 `.*llm.*` 连带冻结。建议加一条 `Not(PathRegex(".*norm.*"))` 放开它们，并与不放开的版本 A/B 一次（4 个任务的仿真对照，成本近零）。

**风险对冲**：把 "π0.5 全参 vs π0.5 LoRA" 做成基座层的**一次性对照**（同 `T_base`、同步数，比 `T_eval` 上的 zero-shot SR 与 harm rate）。这条对照本身是 §IV 的一行审计，且预答"你们为什么不全参"。

### 具体配置

| | H20（假定 ≥80 GB，**待核 §1.6 #10**） | RTX 5090（假定 32 GB，待核） |
|---|---|---|
| **LoRA π0.5（推荐）** | **主用**。8 卡 × bs32 = 256，`fsdp_devices=1` | 可行但需降 batch。openpi 无梯度累积字段且 `batch_size % device_count == 0`；够不到 256 就按线性缩放降 `peak_lr` |
| 全参 π0.5 | 可行。`XLA_PYTHON_CLIENT_MEM_FRACTION=0.9`；OOM 则 `fsdp_devices=2`→`4` | **不推荐**（每层 all-gather 6.6 GB 走 PCIe，无 NVLink，必然通信瓶颈） |
| 其他用途 | 基座微调（两具本体并行）、RLDS 数据服务 | **VLAC 全语料打分、四层 value 离线管线、对齐图训练、仿真评测、policy server** |

### 训练量换算（可直接用的公式）

```
steps@bs256 = 小时数 × 3600 × 控制Hz × epochs / 256
```

**官方锚点**（`examples/droid/README_train.md` L51-52 逐字）："Our DROID training config requires approximately **2 days on 8x H100 GPUs** for convergence (**100k iterations, bs256, approx. 1 epoch**)."；DROID 本体 = 76k 轨迹 / **350 小时**（arXiv 2403.12945 摘要）。

按每具本体约 95 h 的 base-finetune 切分：30 Hz 下 1.5 epoch ≈ 60k 步；50 Hz 下 1 epoch ≈ 65k 步。
→ **主运行 60k 步 @ bs256**，超参照抄 `pi05_full_droid_finetune`（**唯一的大数据官方配方**）：`warmup_steps=1_000, peak_lr=5e-5, decay_lr=5e-5, clip_gradient_norm=1.0, save_interval=5000`。
**按 `T_base` 留出验证集上的成功率选检查点，不按 loss 选。**

**数据格式硬约束**：数百小时**必须转 RLDS**。官方原文："We use LeRobot here, since we assume the custom DROID fine-tuning dataset to be relatively small (**<10s of hours**). For larger datasets … **we recommend using RLDS**"。**必做 idle filter**（官方称此项 "significantly improve policy performance"；家居长时程数据空闲占比更高）。

## 5.4 E0 约束下的分体微调：确认，且这个约束比想象中便宜

**做法**：两次独立 LoRA 微调，各自只吃自己本体的数据、只吃 `T_base` 的任务，产出两个检查点，之后全程冻结。**不做任何 co-train、不做跨体 ER、不共享 LoRA。**

**动作空间对齐（免费）**：π0/π0.5 的规范布局（`docs/norm_stats.md` 逐字）
```
dim_0:dim_5   left arm joint angles
dim_6         left arm gripper position
dim_7:dim_12  right arm joint angles (bi-manual only)
dim_13        right arm gripper position (bi-manual only)
```
关节角单位弧度；夹爪 [0.0, 1.0]，0=全开 1=全闭。**与双臂 6-DoF Piper 逐位对齐。** `LeRobotAlohaDataConfig` 的 `delta_action_mask = make_bool_mask(6, -1, 6, -1)` 同样逐位对齐。可复用的预训练 norm stats asset_id 含 `trossen`（"6-DoF dual arm robot with parallel grippers"）与 `arx`（"Bi-manual ARX-5"）。官方建议两种都试；**但主结果用同一套复用 stats**，理由是归因干净。

**代价有多大——不要猜，把它变成论文的一个数**：
- 直接代价：训练算力 ×2（LoRA 下可接受；这是选 LoRA 的第四个理由）。
- 成功率代价：无法引用现成数字。但施工图已列 `ER / 双体数据 co-train` 作为上界 arm。**把它跑出来，报成"E0 这条主张的标价"**：`SR(co-train) − SR(own-body-only base)`。这比任何文献引用都强，且直接回应 R3-B1。
- 参考量级：Liu et al. (ICML'26, 2603.03818) 证明 **2% 回放缓冲即可近零遗忘** → π0.5 这一级骨干对"少见一份数据"不敏感，co-train 增量很可能是个位数点。**支持"E0 代价小"这一预期，但必须实测，不能引用。**

**必须预备的两个反驳**：
1. *"π0.5 的预训练里本来就有别的机器人的数据，reader 早就通过权重读过了"*——最锋利的一刀。**唯一 airtight 的答法**：所有 arm 共享同一个预训练底座，主端点是**同本体内配对的 Δ**（同 init state、同 sampler seed，McNemar），预训练先验对 base 和 ours 两个 arm 完全相同，**在数学上无法解释 Δ**。**这句话必须逐字写进 §IV，不能只写在 rebuttal 里。**
2. *P3′ 跨的是两个不同的策略检查点*——这是真混淆。对策：每个方向的 Δ 只与**自己的 base** 比，并在主表额外报两具本体各自 base 在 `T_eval` 上的 SR，让读者看得见基线差。

## 5.5 RL 后训练：明确不做，但把"为什么不做"写成正面论证

**不是因为冲突（部署前做在 E0 字面上合法），而是三条更硬的理由**：

**(a) 它与记忆机制争夺同一份收益，是替代品而非正交。** SRPO（arXiv 2511.15605；本地 PDF 页眉逐字 "This CVPR paper is the Open Access version… identical to the accepted version"，**venue 可订正为 CVPR**）用"当前 batch 内模型自己产生的成功轨迹"作自参照；PLD (2511.00091, ICLR'26) 用残差 RL 探测失败区、采数、蒸馏回 generalist；RIPT-VLA (2505.17016) 用自身 rollout 的稀疏成功奖励。**这些正是本文记忆库要吃的同一份信号——部署中自己跑出来的成功经验。** 先做 RL 后训练 = 提前把记忆本该展示的 headroom 烧掉，主表 Δ 直接缩水。

> **审稿人问"为什么不结合 RL"时的答案**："RL post-training and our store draw on the same signal — successful experience produced during deployment. Combining them would confound the source of the gain; we deliberately freeze the policy so that the store is the only channel."

**(b) 它把已经最锋利的攻击面再放大一倍。** R3-B1（"基座微调 = 策略梯度，主张不成立"）是威胁登记表里最危险的一条，处理办法是 E0 + "once deployed" 措辞。再叠一层 RL，"部署前"这条线就从**原则**变成**漏洞**。

**(c) 预算不允许。** RIPT-VLA / SRPO 要在线真机 rollout；VLA-RFT (2510.00406) 要先训一个数据驱动世界模型。

**Related Work 的处理**：v4 §3.3 把 RL 后训练一族标为"与本文正交"。**改一个字**：不写 orthogonal，写 **complementary but confounding**，并补上 (a) 的解释。**两处 venue 可订正**：SRPO 确认 CVPR；VLAC 的 critic 主体论文是 **ICML 2026**（README 挂 OpenReview `i7mfaYYLDf`，bibtex booktitle 为 Forty-third ICML）——v4 §9 把 VLAC 列为纯 arXiv，可订正。

**但要做一件几乎免费、且必须做的事：用 VLAC 做基座微调语料的数据筛选（不是 RL）。**
- VLAC README 明写 "Trajectory quality screening"：按 VOC 值过滤低分轨迹、按负 pair-wise 分数 mask 动作，"improving the effect and efficiency of imitation learning"，附 `data_filtering_example.py`。
- **纯监督数据策展**，完全落在"部署前微调一次"的边界内，不产生任何新的梯度主张，与 openpi 自己的 idle filter 发现同向。
- **零边际成本**：VLAC 是写入门控本来就要装的部件，装一次用两处。
- 数百小时家居遥操语料必然含大量失败/空转/操作员犹豫段，**这一步的收益很可能大于任何 RL 后训练**。

## 5.6 写入门控：VLAC 可得，R3-B12 结案

**结论：VLAC 权重公开、MIT 协议、2B/8B 双档，施工图 §7 优先级 1 可以关闭。** 施工图 L864 的退路（"遥操隐含标签 + 轻量成功分类器"）不必启用，Intro ¶4(e) 的 why-now 论据可保留原措辞。

**已核实**（GitHub API 直取）：`InternRobotics/VLAC`，**327 star，MIT**，创建 2025-09-15，最近 push 2026-08-13。权重 `huggingface.co/InternRobotics/VLAC`（2B，InternVL2-2B 底座）与 `VLAC-8b`。依赖 python 3.10 / cuda12 / **transformers 4.51.3** / peft ≥0.15.2 / **ms-swift 3.3**（与 openpi 依赖树冲突，**需独立 venv**）。

**API**：`Critic.web_trajectory_critic(...)` 返回 `value_list, critic_list, done_list`；关键参数 `reference_video_path`（**one-shot in-context——可用写者本体的一条成功 episode 当参照，去判读者本体的 rollout，这正是跨本体门控需要的形态**）、`done_threshold=0.9`、`skip=5`、`fps=5`、`batch_num=5`。

**已核实的指标与工作点**（VLAC PDF）：沿用 GVL 的 VOC，自定义 VROC 与 `VOC-F1`。RT1 上跨实体跨场景 one-shot **VOC-F1 = 0.95**；RoboNet zero-shot VOC-F1 = 0，one-shot 大幅回升；**RoboFAC 上成功视频 0.89 / 失败视频 0.44**（成败可分）。真机 RL：四任务 SR 约 30% → 约 90%。

**后续工作 VLAC-Cut / HELP**（arXiv **2607.09776** = *HELP: Human-Efficient Large-Scale Robot Post-Training with Rollout Segmentation*，摘要逐字：VLAC "separates autonomous trajectories into **progress-making, idle, failure-inducing, and recovery segments**"）→ **这正是施工图 §III-E 要的"progress-peak 之前的前缀截断"的现成实现，D9 大概率能从 2–4 周压到 1 周。**

### ★ 关键：把两件事拆开（家居长时程成功判定问题的正解）

| | 写入门控 | 论文报出的成功率 |
|---|---|---|
| 判定者 | **VLAC-8b**（自动） | **人 / §6.9 的自动判据** |
| 量级 | 语料数千 episode/本体 + 数千评测 rollout | 约 3–4 千 trial |
| 需要的性质 | **高 precision、低 recall 可接受**、高吞吐 | 可信、可复现、可申诉 |
| 成本 | 单卡数十 GPU-小时；**百卡下 2–5 小时** | 自动为主；叠衣人评约 5 人小时 |

**这个拆分解决三个问题**：(1) 成功率是论文的记录指标，用人/客观传感判是唯一不会被质疑的做法，而且量级小到根本不贵；(2) 写入门控需要吞吐不需要完美，VLAC 正合适；(3) **可以把借自 R-t-S 的 precision 0.970 / recall 0.678 换成自己实测的**——在约 500 条留出 rollout 上同时取人标与 VLAC 标，报 VLAC-8b 在**本文五族任务上**的 precision/recall，据此把 `done_threshold` 调到高 precision 工作点。**这是一行 §IV 审计，把一个借来的假设变成一个自己的测量。**

## 5.7 对齐图：不变，但训练数据来源可能改变

`T_align` 从 `T_base` 中挑 10–12 个**两具本体都做过**的任务，`T_align ∩ T_eval = ∅`。这是全系统唯一需要梯度的部件，离线一次性完成。

**关键依赖（§1.6 #4）**：若存量语料的双本体任务重合度 ≥6，`T_align` 可直接从存量语料挖出，**省掉 D12 的 31 机器人小时**；若 <6，必须现采并推迟 G3b。**G0 当天必须出这个审计结果。**

**退路**：`lang` key（冻结文本编码器编码①层摘要）是完全无训练的诚实地板，**成本近零，必跑**，且是唯一不受对齐图泄漏影响的 arm。

## 5.8 数据切分：三份 + 一条硬规则

以 300 h 总量、150 h/本体为工作例（按比例线性缩放，**真值待 §1.6 #4**）：

| 份 | 定义 | 占比 | 150 h 下 | 用途 |
|---|---|---|---|---|
| `base-finetune` | **`T_base` 任务**，全部场景/物体实例 | 63% | **95 h** | 两次独立 LoRA 微调（60k 步 @ bs256） |
| `store` | **`T_eval` 任务**，场景/物体实例集合 **A** | 27% | **40 h** | 灌 `S_corpus`（规模与串扰） |
| `eval` | **`T_eval` 任务**，场景/物体实例集合 **B** | 10% | **15 h** | 评测初始状态分布、泄漏审计、VLAC 参照视频 |
| `T_align` | 从 `T_base` 挑两体都做过的 10–12 个任务 | 复用 | 0 h（若重合足够） | 对齐图 |

**硬规则：切分是二维的——任务集 × 场景/物体实例集，不是按 episode 随机切。**
- `T_base ∩ T_eval = ∅`（E0）
- `T_align ∩ T_eval = ∅`
- store 与 eval **同任务、不同场景与物体实例**
- **★ 实例 id 纳入互斥维度**：对折叠而言"另一件 T 恤"的关键点语义完全一致，泛化强度很弱。**eval 实例必须在颜色/尺码/材质上与 store 实例明确不同，并在审计行里报出来。**

### ★ 基座能力必须落在一个窗口里（最容易被忽略却最致命的一条）

微调后基座在 `T_eval` 上的成功率应落在 **20%–60%**。
- **>70%** → 天花板效应，注入的增益淹没在噪声里；
- **<15%** → 写入门控收不到成功片段，库是空的；注入也没有可被引导的基础。

**这个窗口应当成为 `T_base` / `T_eval` 划分的设计目标**：把同一技能族里的近邻任务分开放（例：微波炉门进 `T_base`、洗衣机门进 `T_eval`）。

**→ 新增 gate G3c**（§8.2）：用 10k 步小规模微调探一次这个窗口（约半天），落在 20–60% 才准启动 60k 步全量；不落窗口就当天改切分。**必须早于 G3b 的切分冻结**，否则改不动了。

### ★ 一个必须先解决的结构性缺口

用户给的 **5 个任务族撑不起"12 个评测任务 + 不相交的 `T_base`"**，而且 E0 与"基座 SR 落在 20–60%"在只有 3 个族的结构下**近乎不相容**：折 T 恤 vs 折长裤基本是同一技能——把 F 整族放进 `T_eval` 则基座没折过任何东西、SR 趋近 0（地板）；放一个折叠变体进 `T_base` 则 eval 变体几乎同分布、SR 趋近天花板。

**两条出路（都要走）**：
1. **把"任务"重定义到 (任务族 × 物体实例 × 目标位形) 粒度**，并在 §IV 明确交代这个粒度定义。可行，但必须主动写出来，否则会被当成灌水。
2. **增加族数（这才是真正决定 P3′ 效力的量）**：加**抽屉**（prismatic 铰接，与转动门是不同约束类型，ScrewNet 的螺旋表示免费覆盖）作第 4 族，加一个**双臂交接/放置**类作第 5 族，各 2 个变体。总任务数保持 12–14 不变，但族数 3→5，n_eff 从约 4 抬到约 7。**必须在 G3b 冻结切分前做完。**
3. 同时**预注册一条排除规则**：pilot 中基座 SR <15% 或 >70% 的 eval 任务，或调整其初始状态分布、或在冻结前替换。**规则必须在看到主结果之前定死。**

## 5.9 算力排期

**"百卡"用不到单次训练上**（JAX 无多节点）。正确用途是横向并行：

| 阶段 | 用什么 | 时长 |
|---|---|---|
| 语料 → RLDS + idle filter + VLAC 质量筛选 | 5090 集群（embarrassingly parallel） | 2 周（含 IO） |
| 两具本体 LoRA 微调（**并行**） | H20 各 8 卡 | 60k 步 @bs256；官方锚点 8×H100 约 1.2 天 → **8×H20 需乘实测比值（§1.6 待测）** |
| 四层 value 离线生成、对齐图训练、仿真评测 | 5090 集群 | 与微调并行 |
| VLAC 全语料打分 | 百卡 | 2–5 h |

**必须实测的一个比值**：用 `pi05_full_droid_finetune` 或自写配置在 H20 上跑 200 步读 it/s，与官方锚点（8×H100，bs256，1.73 s/step）相除。**所有墙钟估算线性依赖它，唯一可靠办法是实测。**

---

# 6. 真机实验设计

## 6.1 本体对论证：三句话版本（这是正文措辞的模板）

1. **不要写"连杆长度不同"**——审稿人会认为不足以支撑跨本体主张。
2. **层④的失败写架构**：Piper 是球腕 Puma 型（j4∩j5∩j6），PiperX 是偏置腕 UR 型（a4 = 74.66 mm，j2/j3/j4 三轴平行）；两者都满足 Pieper 判据但走不同分支；同名关节语义不同（Piper j4 = 腕 roll，X j4 = 肘平面 pitch）。**证据：最优固定标定残差 7.10 cm / 17.8°；最小二乘对 j4/j5 的拟合尺度为 −0.012 / −0.064，即直接放弃拟合。**
3. **层③的失败写限位包络**：Piper j5 ±70° 是全臂最紧关节；PiperX j4/j5 均 ±89°。**证据：放宽 PiperX 限位后层③可行率 80.8% → 100.0%，几何贡献 0.0%。**

**★ 框架反转（零成本，收益最大）**：正文**永远不要以 "Piper vs PiperX" 作为本体对的门面**。用最宽的一档（单臂 reader）开场，把 Piper↔PiperX 放在阶梯的**最难/最保守**一端，写成：

> even between two arms from the same vendor and generation, with the same DoF, the same payload, the same repeatability and a 6.9 % difference in reach, joint-space content does not transfer.

这句话比"我们跨了两台臂"强一个量级，而且它**把审稿人的先天怀疑变成论文的论点**。

## 6.2 受控的 embodiment-distance 阶梯

**判准（五条，必须写进补充材料并对每一档逐条打分）**——用于防御"人为制造困难"这一刀：

| # | 判准 | 说明 |
|---|---|---|
| 1 | **Catalog test** | 该构型是否作为产品在售，或属于常规维护后的自然状态 |
| 2 | **★ Own-task competence test（唯一可一票否决）** | 受损读者在**自己写的条目**上的成功率必须仍然接近未受损时，**且必须与跨本体数字并排报出**。若同比例下降，你造的是一台更差的机器，不是另一台机器 |
| 3 | **Rule-not-choice test** | 修改必须由**预注册的规则**决定（"锁最远端关节"），而非由"哪个关节最能打破 SE(3)"决定 |
| 4 | **Symmetry test** | 同一修改双向施加 |
| 5 | **Predictability test** | 若逐任务结果可解析预测则不做（可预测的实验不携带信息） |

### 阶梯表

| 档 | 定义 | 硬件成本 | gap 类型 | 预期层③可行率 | 五条判准 |
|---|---|---|---|---|---|
| **D0** | Piper → Piper（另一台同型机） | 0 | 无（同本体上界） | ~100% | 全过 |
| **D1** | Piper → Piper + **相机重装位** | 0 | **纯 key 侧** | ~100%（value 不变） | ⚠️ **这不是 embodiment 档，是 domain shift，不要当作谱系的一级**；作为 SQ2 归因的控制组 |
| **D2** | Piper → Piper + **换夹爪指**（3D 打印加长/加宽指） | <¥200 | **接触几何侧** | ~100%（接触点语义变） | 全过，且**被低估，应升级**（改变接触几何与③层接触点语义，最划算的一档） |
| **D3** | **Piper → PiperX** | 0 | 运动学族 + 限位包络 | **80.0%** | 全过（主实验） |
| **D4** | **PiperX → Piper**（反向） | 0 | 同上 | **57.3%** | 全过（主实验） |
| **★ D6** | **单臂模式 reader**（一条臂单独作为读者） | 0 | **动作维度 14→7，T_rel 字面消失** | ③/④ 双臂条目结构性不可读；①② 仍可指导顺序策略 | **全过**：AgileX 单臂 Piper 是独立在售 SKU；单臂读者在自己的单臂条目上完全胜任；规则明确；可双向；逐任务结果不可预测。**建议升为主实验第二条腿** |
| **D7** | **Revo2 灵巧手 reader**（官方 xacro 已存在） | 需实物（§1.6 #7） | ④层维度 + ③层接触语义**同时**改变 | 待测 | 全过（若有实物） |
| **D8** | **人手演示 writer** | 一台第一视角相机 + 手部跟踪 | ④层**字面上不存在**，③层为手部位姿 | — | ⚠️ 人→机器人是拥挤方向，**只作阶梯最远端的一档，不作主线** |
| **D5**（plan B） | Piper → PiperX **锁一个关节** | 0（`start_sdk_joint_limit` 软限位） | 结构性降维 6→5 < SE(3) 的 6 维 | **需重做，见下** | ⚠️ **当前定义不合格** |
| **S1/S2** | 仿真：Piper → Piper-H / Piper-L | 0（官方 MIT URDF，已下载） | 同架构、纯尺度 | 94.0% / 86.8% | 自然，但**④轴上退化**，见下 |

### D5 为什么当前不合格，以及怎么修

`dual_out.txt` 的 locked-joint ladder：锁 j4 → 6-DoF 0.0% / 5-DoF 0.0%；锁 j5 → 0.0% / 0.0%；锁 j6 → 6-DoF 0.0% 但 **5-DoF 71.7%**；无锁 6-DoF 参考 66.7%。

**三个问题**：
1. **锁定角是零位**（`dual_study.py` 的 `ik_pos_axis` 里 `q[locked]=0.0` 硬编码）。PiperX 零位是伸直构型，锁死肘部或腕俯仰后可达集塌缩到一条曲面——这是**人为最劣化的配置**，与"5-DoF 低于 SE(3) 六维"这个原理性论证无关。审稿人会说你造了个残废机器人。
2. **违反判准 3**：j6 是在算出"6→5 DoF"之后才选中的（后验选择）。
3. **违反判准 5**：j6 那行的 71.7% 说明——绕接近轴的 roll 对很多抓取本就自由，所以锁 j6 的 reader 相当能干，撑不起"硬性失败"；而锁 j4/j5 的全 0.0% 又是纸上可推的。

**修法（1 天，必须在 G0 那周做完，因为它决定型号确认失败时有没有 plan B）**：
- 锁定角不取 0，对每个任务从**写者轨迹里取该关节的中位角**（任务友好锁定），并对锁定角在该关节限位内做 **5 点 sweep**，报**最优锁定角下的可行率**作为上界。
- 判据从 full 6-DoF 换成**任务真实容差**（与 §3.4 证据 C 的容差扫描共用一套代码）。
- 若最优锁定角下锁 j6 的 5-DoF 可行率仍 >60%，改锁 **j5**（腕俯仰，对自上而下抓取是刚需）并报同样的 sweep。
- 任务集必须**混合 5-DoF 充分与不充分的子任务**，预测对象改为"**哪些条目变得不可读**"（admissibility），才通过判准 5。
- 脚本已备：`/tmp/agxurdf/lockedsweep.py`（**需先补一个通用的 position+approach-axis IK**，`taskspace.py` 里没有；`dual_study.py` 里那个把锁定值硬编码为 0）。**状态：待跑。**

### S1/S2 仿真档的一处修正

Piper→Piper-H 与 Piper→Piper-L 的朴素复制**姿态误差同为 0.0°**（同架构，末端朝向完全一致）——**在④轴上它们是同一个点**。位置误差分别是 0.98 cm 与 9.41 cm。

→ **④轴必须改报二维 (位置误差, 姿态误差)，否则"层④何时失效"的曲线是假的。** 修正后这条阶梯仍然有力：0°（同架构，任意尺度）vs **82.8°**（异架构）——**这个对比本身就是"架构差异 ≠ 尺度差异"的证明**。

**仿真档进正文与否**：建议进，但**明确标注 simulation-only**。它把 SQ1 从两个点升级成一条带运动学机理的曲线，成本近零（MIT URDF + 现成脚本），代价是引入"仿真结论外推到真机"的攻击面。

## 6.3 任务分层（S / R / W）

### 三族的正交定位（为什么三族都要）

| 族 | 双臂协同松弛（实测） | 锚点感知 | 在论文中的角色 |
|---|---|---|---|
| **门（D）** | 低（刚性锚定 82.7%） | **易**（一次性标定，0.5 周） | 层③的**存在性证据**；但②③几乎退化为同一件事 → **谱系压平的第二个来源，须写成预测** |
| **拉链（Z）** | 中（±2 cm/5°，84.7%） | 中（拉头抓后刚性附着成立） | 桥接档；**唯一保住原前端的可形变任务** |
| **叠衣（F）** | **高（±10 cm/20°，92.7%）** | 难（语义关键点） | **唯一能撑开谱系的族**：双臂紧耦合、无零空间、④最可能失败、③靠关键点系可读、②靠 pick-place 词表可读、①因语言欠定必然掉点 |

> **可预注册的任务级预测**：层③迁移率在衣物族最高、门族最低；而感知难度恰好相反。**两个效应正交**，这是任务集设计的原则性依据。

### S 层：12 个变体（唯一 confirmatory 端点）

任务粒度 = **(族 × 物体实例 × 目标位形)**，必须在 §IV 主动交代。

| # | 变体 | 族 | exec+复位 | 判定 |
|---|---|---|---|---|
| F1 | 叠短袖 T 恤（摊平起始） | F | 3.5 min | rubric |
| F2 | 叠长袖衬衫（袖需先折入，子目标数不同） | F | 3.5 min | rubric |
| F3 | 叠长裤（双侧对称折） | F | 3.5 min | rubric |
| F4 | 毛巾四折 | F | 3.5 min | rubric |
| F5 | **叠 T 恤至指定外接矩形**（塞进给定抽屉） | F | 3.5 min | **全自动** |
| D1 | 开微波炉门 | D | 0.6 min | **全自动** |
| D2 | 关微波炉门（含卡扣） | D | 0.6 min | **全自动** |
| D3 | 开洗衣机门 | D | 0.6 min | **全自动** |
| D4 | 关洗衣机门（含胶条压合） | D | 0.6 min | **全自动** |
| Z1 | 拉开收纳包拉链（全行程） | Z | 2.1 min | **全自动** |
| Z2 | 拉合收纳包拉链 | Z | 2.1 min | **全自动** |
| Z3 | 放物入包 → 拉合（时序） | Z | 2.1 min | **全自动** |

**主分析同时在「全 12 个」与「客观 8 个」上跑**，作为稳健性检查——**论文主结论不建立在最有争议的判据上**。

**★ 但见 §5.8 的结构性缺口**：为解决伪重复（§6.8）与 E0/headroom 窗口不相容，**建议把 4 个门变体换成 4 台不同铰接家电各 1–2 个变体**（微波炉、洗衣机、抽屉、柜门），把 3 个拉链变体换成 **3 个不同的拉链包**。硬件成本几百块，n_eff 从约 3 提到约 8–10，且顺带证明类别级泛化。**必须在 G3b 冻结切分前做完。**

### 排除：套垃圾袋

(a) `trash bag` / `garbage bag` / `bin liner` 在 arXiv 机器人文献 **0 篇**，无基线无检测器；(b) 最接近的 AutoBag（ICRA'23）需 UV 荧光标记做自监督标注，"撑开袋子并放入一件物体"仅 **16/30 ≈ 53%**，而且做的是"撑开袋子"不是"套桶"；(c) "翻转套过桶沿"是**拓扑变化 + 重度自遮挡**。→ **降级为定性视频 / scope 说明，不进主表。**

### 条件性排除：拉链

若两具本体**无腕部力/触觉通道** → 降为 exploratory。证据：2112.06442 纯视觉 56.7% vs 视觉+触觉 93.3%，差 36.6 个点，足以吃掉全部迁移增益。
- 若降级：S 层从 12 降到 9（5F+4D），族级检验的族数不变，预算省约 12 h。
- **文献空白已核实**：`ti:"zipper" AND cat:cs.RO` → **0 条**；`abs:"zipper" AND cat:cs.RO` → 仅 2 条，只有 2112.06442 是操作论文。**既是真新颖点，也意味着无基线、无现成检测器、审稿人无直觉。** 另：BUDS / "Stabilize to Act"（2309.01087, CoRL'23）四个双臂任务之一就是 **zipping jackets**（20 条演示/任务，四任务平均 76.9%）。

### R 层与 W 层（各 2 个，scope 说明 + 定性视频）

替换原 M/F 层，且这次**双向**（原方案的 M/F 是单向的）：

- **R 层（仅 PiperX 可，reach 受限）**：R1 折叠大号床单（跨度超 Piper 626 mm 臂展）；R2 够到深式微波炉腔体后壁取物。
- **W 层（仅 Piper 可，腕部 roll 受限）**：W1 需 >±89° 腕部 roll 的拧瓶盖式动作（Piper j4 ±100° vs X ±89°）；W2 需大 roll 的衣架挂取。

**这比原 M/F 更有价值**：**双向**单侧任务直接图示化"两个工作空间互不包含"（IoU=0.528），在任务层面证伪"子集"直觉——正是 P3 旧机理死掉的原因。

## 6.4 双臂：一个独立于连杆几何的 gap 源，但"+10 pt"这条 Contribution 必须重跑

### 正确的形式化（经典引文已 Crossref 核实）

- Uchiyama & Dauchez, *A symmetric hybrid position/force control scheme for the coordination of two robots*, **ICRA 1988**, DOI 10.1109/robot.1988.12073
- Chiacchio et al., *Direct and Inverse Kinematics for Coordinated Motion Tasks of a Two-Manipulator System*, **JDSMC 1996-12**, DOI 10.1115/1.2802344
- Caccavale et al., *Six-DOF Impedance Control of Dual-Arm Cooperative Manipulators*, **IEEE/ASME T-Mech 2008-10**, DOI 10.1109/tmech.2008.2002816
- **Extended Relative Jacobian**（1905.01248, ISRR 2019）：引入可调**非对称度**参数，把相对运动任务在两臂间分配，**无需指定绝对运动目标**。**这正是所需工具：记忆存"相对运动"（协同的关键部分），读者用自己的冗余度解"绝对运动"。**

学习侧对应物：BiRP（2307.05933, IEEE CDC'23，把人类双臂任务分为 leader-follower 与 synergistic 两类，用相对参数化编码协同）；BUDS（CoRL'23）；Co-VLA（2606.20285，共享隐变量编码任务级协同意图 + 残差隐变量编码每臂执行修正，紧耦合任务 +27%，真机 OOD 13%→27%）；TwinVLA（2511.05275, **ICLR 2026 Poster**，把两份预训练**单臂** VLA 组合成协同双臂 VLA，无需双臂预训练即超过同规模 RDT-1B → **证明逐臂模块化分解在 VLA 层可行**）。

### R-t-S 的一处具体缺陷（这是 Contribution 的**正当理由**）

R-t-S 的 component-aware aggregation（其 Eq.22–31）对**拼接后的双臂动作向量逐分量**做相似度加权平均（Δp/Δr）与夹爪加权投票。**K 条候选 chunk 的逐坐标平均，其相对变换一般不等于各候选相对变换的任何保约束平均。** 即：**在 retarget 之前，聚合本身就可能破坏双臂闭链/接触约束。**

**修法**：先把每条候选从 (left, right) 转到 (T_abs, T_rel)，对 `T_rel` 用更紧权重或最近邻回退（与其对夹爪冲突的保守回退同构）、对 `T_abs` 自由聚合，再映回。

**这是纯定性的方法学缺陷，不依赖任何数字。** 它改的是**聚合前的坐标**，不是注入路径，**不违反"注入机制沿用 R-t-S"的诚实声明**。

### ★ 但"+10 个百分点"这个数字目前是搜索预算伪影，必须重跑

**问题（读源码确认）**：`taskspace.py` 里 per-arm independent 每臂 `ik_multi(restarts=8)` **跑一次**；cooperative 则 `for trial in range(40)` 随机 SE(3) 偏置 g，每次再 `ik_multi(restarts=3)`——即协同侧最多拿到 **40×3=120 次 IK 尝试，是独立侧的 15 倍**，且**额外获准把整个任务挪 ±10 cm/±20°**。

**同一个量三次运行给出三个数**：`dual_study.py`（N=80, restarts=6）35.0%；`taskspace.py`（N=250, restarts=8）77.6%；`followup.py` 的 rigid 行（N=150, ntr=1, g=I, restarts=3）82.7%——**后者本质就是 per-arm independent，更小的搜索预算却更高的分数，只能是采样噪声**（n≈150–250，95% CI 约 ±6 pt）。

**最要命的一条**：`RESULTS_taskspace.txt` 明确记录 `relative-pose error when forced (clipped IK): pos median 0.06 cm, rot median 0.0 deg`——**逐臂独立 retarget 几乎没有破坏双臂相对位姿**。所以实测的差是 **IK 可行性**的差，**不是约束违反的差**。

**修法（必须做，否则审稿人读脚本就能拆）**：
1. **equal-budget 重跑**：给两条路径**完全相同的总 IK 预算**与**相同的任务级 float**，同一脚本、同一 seed、同一批 pair，N≥400，报 **Wilson 区间**。脚本已写：`/tmp/agxurdf/equalbudget.py`，三个 arm：A 独立无 float（120 restarts/臂）/ B 独立带 per-arm float（20×3）/ C 协同带刚体 float（20×3）。**状态：本次会话已启动，但 N=400 的预算在单核 numpy 下跑不完（>25 min 未出结果），被超时终止。需降到 N≈150 或改用多进程重跑。v5 不填这个数。**
   > **预期结果（写在这里以便事后对账）**：B 的约束集是 C 的**超集**（每臂可独立摆放 vs 整对刚性摆放），所以在**同预算同 float** 下 **C ≤ B** 必然成立。若实测确实如此，则"+10 pt 协同增益"被证实为**预算/float 伪影**，该 Contribution 应删除，换成下面那条纯定性的 R-t-S 聚合缺陷。
2. **把"约束违反"与"可行性"拆成两个独立指标分别报告。** 按现有证据，约束违反那一项的正确写法是"逐臂独立 retarget 的相对位姿保持误差中位 **0.6 mm / 0.0°**，可忽略"——即**这条 Contribution 的正当理由只能建立在可行性上，不能建立在约束破坏上**。
3. **n=150 太小**，所有百分比报 Wilson 区间，**不报一位小数**（`RESULTS` 记 93.6%、施工图写 92.7%，n=150 时两者不可区分）。
4. **若 equal-budget 下增益 <5 pt 或落在 CI 内 → 删掉这条 Contribution**，换成上面那条纯定性的 R-t-S 聚合缺陷。**它不是主线，删掉不伤谱系。**

### 协同松弛是任务相关的（实测阶梯，`followup.py`，n=150，**同样需 equal-budget 重跑**）

| 锚点刚性 | 可用松弛 | 层③双臂可行率 |
|---|---|---|
| 刚性锚定（门：铰链固定） | 0 | 82.7% |
| 紧（拉链：袋可微动） | ±2 cm / 5° | 84.7% |
| 松（衣物：可整体重放） | ±10 cm / 20° | 92.7% |

**注意**：松弛档用 30 次随机 g 采样，刚性档只用 1 次——**这个阶梯同样被预算污染**。重跑时三档必须同预算。
**且松弛只在任务允许整体重新摆放时合法**（叠衣可、门不可）。**每个任务变体的合法松弛量（0 / ±2cm5° / ±10cm20°）必须在采数前逐任务预注册**，否则 §6.3 的任务级预测无法检验。

### 消融表新增两行（施工图 §4.4 的 A1–A6 之外）

| # | arm | 排除的替代解释 |
|---|---|---|
| **A7** | **④ + 腕部重解算**（复制 j1–j3、自由重解 j4–j6） | **必须加**。实测该操作把姿态残差从 82.8° 降到 **6.7°**。不加这一行，审稿人会说层④是稻草人 |
| **A8** | **coordination-oracle**（把 `T_rel` 作为硬等式约束求双臂耦合 IK，`T_abs` 为软目标） | oracle 阶梯的**第四桶**：双臂协同约束不可满足，是原三桶不覆盖的失败模式。**纯软件、零机器人小时** |

**A7 的论证（这反而使论点更强，但必须主动写）**：腕部重解算**需要读者的运动学模型并求解 IK**——那正是层③的定义。所以 `④+wrist-repair ≡ ③`，**层④在跨本体下没有独立存在**。这把命题从"关节动作不能迁移"精确化为：

> **关节动作的可迁移部分恰好等于它的任务空间投影；剩下的部分是本体私有的。**

更强、更可证。6.7° 不是 0，它是 j1–j3 语义也不完全对应的残留。

## 6.5 "语言不可表达"任务（≥3，实取 4）

**判据**：同一句自然语言指令对应多条成功轨迹分布，且它们的成功率显著不同。
**检验**：instruction-only 对照拿同一句指令，ours 拿记忆条目。若 ours 在这批上显著胜出、在语义可表达的任务上不显著，则"记忆 ≠ 更好的 prompt"被**结构性**证明。

| # | 任务 | 为什么语言表达不了 |
|---|---|---|
| **L1** | **F5 叠至指定外接矩形** | "把衣服叠好"不指定折线位置、折叠顺序与目标尺寸。要塞进给定抽屉，折线必须落在特定位置——这是**连续几何量**，用语言表达需要念出坐标，而坐标是写入者相机系的量，**与 body-agnostic 直接冲突** |
| **L2** | **Z2 拉合时的卡阻恢复节律** | 拉头被布料咬住时须回退约 1 cm、由稳定臂重新张紧布料、再以特定速度推进。这是**接触/速度剖面**，不是语义步骤 |
| **L3** | **F1/F2 中双臂张紧-扫掠的相位差** | 一臂保持张力、另一臂扫掠，两臂间存在**相对位姿轨迹 `T_rel(t)` 与前后时序偏置**。这正是本设计存 (T_abs,T_rel) 的物理内容，语言无法表达一条连续的相对位姿轨迹 |
| **L4** | **D4 关洗衣机门的胶条压合剖面** | 门接触胶条后需一段特定的减速-加压-越过卡扣的力/速剖面 |

> **L3 是硬件变更带来的净收益**：单臂 FR3 方案不可能有这一类。它同时是双臂协同分解（§6.4）的实验兑现。

## 6.6 机器人小时预算（完整算式）

### 单次 rollout 时长（含复位）——这是原预算错得最狠的地方

施工图一律用 1.5 min。实测量级（**待 §1.6 #8 用存量语料统计确认**）：

| 族 | exec | 复位 | **合计/rollout** |
|---|---|---|---|
| 叠衣 F | 150 s | 60 s（抖开摊平） | **3.5 min** |
| 门 D | 25 s | 10 s | **0.6 min** |
| 拉链 Z | 90 s | 35 s | **2.1 min** |

**★ 但 F 族的复位时长不能按 60 s 记账**：加了 §6.8 的拒收重做之后，期望重置时间是 `60/p_accept`；若 `p_accept≈0.7` 则实际约 86 s，单次 rollout 从 3.5 min 涨到约 **4.0 min**。**这与 1.4 失败因子是相乘关系**（1.4 覆盖硬件故障，不覆盖重置拒收），不要混为一谈。

跑一遍任务子集的耗时：**S12**（5F+4D+3Z）= **26.2 min**；**M6**（2F+2D+2Z）= **12.4 min**；**S4**（1F+2D+1Z）= **6.8 min**。

### 预算表

```
robot-hours = Σ_arm ( #rollouts × 该 arm 任务子集的平均分钟 ) / 60 × failure-factor(1.4)
```

| arm | 子集 | rollout 数算式 | 分钟 | 小时（×1.4） |
|---|---|---|---|---|
| **主端点**（2 方向 × {base, ours} 成对） | S12 | 2 dir × 20 pair × 2 = 80 遍全集 | 26.2 | **48.9** |
| 四层 sweep（探索性） | S4 | 15 × 4 层 × 2 方向 = 120 遍 | 6.8 | **19.0** |
| 8 个控制 arm（含新增 A7/A8；A8 纯软件不计） | S4 | 15 × 7 = 105 遍 | 6.8 | **16.7** |
| R-t-S 复现（同本体 ×2） | M6 | 15 × 2 = 30 遍 | 12.4 | **8.7** |
| **reader #3（D6 单臂模式）准入** | M6 | 15 × 2 = 30 遍 | 12.4 | **8.7** |
| **★ G0.5 交叉点 gate（新增）** | 1F+1D | 200 条条目离线 + 40 真机确认 | — | **2.3** |
| **★ A/A 噪声地板控制（新增，不可砍）** | 1F | 20 对 base-vs-base | 4.0 | **2.3** |
| **★ π_d pilot（新增）** | 3 族各 1 | 3 × 15 对 × 2 | ~2.1 | **3.5** |
| E5 时效性 | D+Z only | 3 场景 × 3 线 × 15 | ~1.35 | **4.2** |
| ER / co-train 上界 | S4 | 15 × 2 = 30 遍 | 6.8 | **4.8** |
| **评测小计** | | | | **≈ 119** |
| **★ demo 增量**（§6.10.6：断电镜 + harm 案例打捞 + 并排机位） | — | 其余五段全部复用主实验素材 | — | **1.8** |
| D12 弱配对采集 | S12 | 12 任务 × 30 ep × 2 本体（×1.2 重拍） | 2.18 | **31** |
| **总计** | | | | **≈ 152 robot-hours** |

### ★ 可行性确认：一个错误假设被推翻带来的红利

> 施工图 §4.7 原文："跨本体 trials 需要进行物理本体更换与复位，因此其单位成本高于同一本体 trials"

**这在新硬件下是错的。** Piper 与 PiperX 是**两套独立台架**，reader swap 只是换台跑，没有任何物理拆装。因此：
- 跨本体 trial 的单位成本 **等于** 同本体 trial；
- **两台可并行运行**。

**wall-clock（按 3 productive h/day/台，非 5——家居长时程 + 布料人工复位 + 每台需一名操作员）**：150 h / 2 台 = 75 h/台 ÷ 3 = **25 个工作日/台 ≈ 5 周/台**。

**唯一的串行依赖**：写者必须先产出条目，读者才能评测。→ 分两相：**相 1 双台并行写入**（D12 + corpus 灌库），**相 2 双台并行读取**（全部评测 arm）。

### 若超预算，按此顺序砍

1. E5 时效性（−4.2）→ 降级为 discussion 一句
2. ER/co-train 上界（−4.8）→ 但这是"E0 这条主张的标价"的唯一实证，**尽量保**
3. reader #3 / D6（−8.7）→ 会把 R1-B5 变回未解决风险，须在 Limitations 明写
4. 四层 sweep 从 4 任务降到 3（−4.8）
5. 主端点 trials 从 20 降到 15（−12.2，但效力从检测 10 pp 降到约 12 pp）

**绝不砍**：G0.5、A/A 控制、π_d pilot（三者合计 8.1 h，是全部统计主张的前提）；S 层任务数不得低于 12；**族数不得低于 4**。

## 6.7 生命周期实验：条目怎么切、库怎么灌

### ★ 夹爪状态机分段不再充分，且新规则不得进关键路径

| 族 | 夹爪事件密度 | 单用状态机的结果 | 增补规则 |
|---|---|---|---|
| 叠衣 | 高（pick-place 原语） | **成立**，6–10 段/episode | 无需增补 |
| 拉链 | **极低**（单次抓持长行程） | **退化为 1 段/episode** | + 弧长里程碑（每 25% 行程）+ 重抓事件 |
| 门 | **极低**（单抓单转单放） | **退化为 1 段** | + 铰链角里程碑（每 30°） |

**问题**：铰链角与弧长是感知前端的输出。施工图 D1 原本是 1 周、零依赖，可以先把语料切完把库灌起来。**新规则把 D1 挂在最贵、最不确定的 D2（叠衣关键点检测器）后面**，把一条并行支路拧成串行，代价是 4–6 周日历时间。

### ★ 双轨分段（修法）

**轨 A（立即可做，0 依赖）**：
```
boundary = (任一臂的夹爪 open/close 事件)
         ∪ (双臂任务系速度过零)      ← 双臂任务系，不是各臂独立
         ∪ (固定时长上限，例如 8 s 强制切分)
       且 受最小片段长度约束（防过分段）
```
用它**先把全部语料切完灌 `S_corpus`**，规模/串扰实验立刻开跑。

**轨 B（感知就绪后）**：仅对 confirmatory 的门/拉链任务补约束坐标里程碑（铰链角 Δθ / 弧长 Δs / 接触模式变化：抓持/释放/重抓）。

**并在论文里报"轨 A vs 轨 B 分段对 precision@k 的影响"**——把一个工程妥协变成一行便宜的 ablation。
**禁止让主线的任何一个数等待轨 B。**

**双臂的关键决定**：边界取两臂事件的**并集**，但**一个 entry 同时覆盖两臂**（存 (T_abs, T_rel)）。**绝不按臂拆成两条独立条目**——那正是"单臂独立 retarget 破坏双臂约束"的来源。

### 两个 store 的规模核算

**`S_corpus`（仅用于规模与串扰，图标题必须写 `corpus-seeded`）**：
- 家居长时程 episode 均长约 180 s（含遥操）→ 40 h/本体 ÷ 180 s ≈ **800 episode/本体**
- × 12–18 段/episode ≈ **10k–14k 条/本体**，双体 **20k–29k**

→ 稳落在 10⁴ 量级，**够不到 10⁵**。诚实处理二选一：
1. 从 `base-finetune split` 挪小时进 `store split`：达 10⁵ 需约 **150 h/本体**投入 store，与基座微调争数据；
2. **（推荐）** 报到实际能达到的 N_max，规模曲线做**对数下采样**（10², 10³, 10⁴, N_max）并**明写 N_max**，不硬凑 10⁵。

**→ v4 §1 与规格书里"10⁴–10⁵ 条"的措辞据实收窄为「10⁴–N_max」。**

**`S_deploy`（承载 P1′/P2/P3′ 与全部主结果）**：来自评测期 rollout + 写入门控。量级 **10³–10⁴**。

### 该测什么（施工图已砍掉的不要复活）

- **保留**：precision@k 随规模的下降曲线、跨体误检率随规模的上升曲线、harm rate 随规模变化。
- **已砍且不复活**：检索延迟-规模曲线（10⁵ 条暴力 cosine 亚毫秒，必然"无事发生"）；删除后残留泄漏探针（对显式条目表平凡为真）。

## 6.8 ★ 统计与协议（这是本次重设计最薄弱、也最必须补的一环）

### 核心问题一句话

> **这个任务集里，配对有效的任务没有统计头room，有统计头room的任务配不了对。**

门族（D1–D4）初始状态完全可复现但会天花板（基座 SR 会落在 70–90%），20 对里可能只有 1–2 个不一致对，对 McNemar 零贡献；叠衣族（F1–F5）有真实头room（R-t-S 同硬件报 39–48%）但**一件衣服的初始褶皱物理上不可复现**，"matched initial state" 在其上是空话——而 McNemar、harm rate、成对 Δ 三个全文贯穿的量**全部建立在这个假设上**。

### 修法 1：拆成两个预注册主端点（层级 primary / co-primary，Bonferroni，各 α=0.025）

**(P-rigid)** D+Z 共 7 个变体，**成对 McNemar**。
- **必须为 D 族人为制造 headroom**（施工图那句"不需人为制造 headroom"**只对 F 族成立，对 D 族是错的**）：门初始开合角在 [0°,25°] 均匀随机、家电本体位置在 ±8 cm / ±10° yaw 内随机、加 1 个遮挡干扰物。
- pilot 里把每个 D 变体的基座 SR 调进 **25–65%**。

**(P-deformable)** F 共 5 个变体，**放弃 trial 级配对**，改**分层随机化**：每次重置后由脚本随机分配到 base 或 ours，用初始状态难度协变量分层；主量为 **0–4 分进度分的 stratified 均值差**；检验用**任务层 cluster bootstrap**。

**HR 的定义随之分裂**（§IV 必须明写两者**不可 pooled 成一个数字**）：
- D+Z：`HR = n10/n`（per-trial）
- F：`HR_dist = P(ours 失败|层) − P(base 失败|层)`

### 修法 2：'matched initial state' 在可形变物上的可操作定义（三件事，缺一不可）

**(a) 容差化的配对定义 + 拒收重做**：桌面印一个衣物轮廓模板（Cloth Funnels 式 canonicalization，但用于**重置**不是用于策略）。重置后拍俯视 RGB-D，只有 **mask 与模板 IoU ≥ 0.90 且主轴角差 <10° 且褶皱能量代理（深度图 total variation 或检出折痕数）落在预设带内**，才算合法初始状态；否则重做。**把达成的 IoU 直方图报进补充材料**——让配对是**测量出来的**，不是假设出来的。

**(b) A/A 控制（不可砍，约 2.3 robot-hours）**：选 1 个 F 变体，**base 对 base** 跑 20 对"配对" trial，测不一致率 `π_d^AA`。**这就是 McNemar 的噪声地板**：若 `π_d^AA ≥` 观测到的 A/B 不一致率，成对检验没有效力，必须整体切到 (P-deformable)。
> 为什么必须做：HR 是论文主动宣称的诚实性指标（Abstract 里就有）。在 SR≈50%、初始状态方差大的情形下，**纯噪声就能给出 20–25% 的 n10**，把它写成 "memory-harm rate 25%" 是硬性误述。

**(c) 条件污染审计**：base 组与 ours 组的初始 IoU / 褶皱能量分布做 t 检验，若显著说明重置被条件污染。

**另必须明写一条限制**：matched sampler seed ε **只控制第一个 chunk**，一旦首个动作分叉后轨迹即发散——**seed 匹配对长时程任务是装饰性的**。这对刚体任务同样成立，**主动写出来比被问出来强**。

### 修法 3：π_d 写成预注册参数，G1 之前 pilot 实测

McNemar 的效力由**不一致对数量**决定，不由 n 决定：
```
n = (z_{α/2}+z_β)² · π_d / δ²  =  785 · π_d      (δ=0.10, α=0.05, 1−β=0.8)
```
- `π_d=0.30` → n=235 ≈ 240（**这正好反推出施工图继承的那个数，但它从未被声明过**）
- `π_d=0.50` → **n=392 对/arm** → 主端点从 48.9 h 涨到 **79.9 h**，总预算 150 → **约 181 h**

**而这在 G2′ 之后才会暴露，那时 E0 切分已冻结、无法回退。**

**执行**：每族选 1 个变体，各跑 15 对 base-vs-ours，读出族别 `π_d`（可与 A/A 控制合并采集）。用实测 `π_d` 重算 `n=785·π_d`，**在冻结主端点之前**决定是加 trial 还是降效力目标。若 `π_d^F > 0.40`，F 族强制走 (P-deformable) 的连续型进度分——**连续量的效力不由 π_d 支配**，这是拆分的第二个独立理由。
**§6.6 预算表的每一行都应标注其隐含 π_d。**

### 修法 4：任务独立性——12 个变体实为 3 族，n_eff ≈ 4

F1–F5 共享同一套关键点前端、同一折叠技能、同一类失败模式；D1/D2 是同一台微波炉的两个方向；D3/D4 是同一台洗衣机；Z1–Z3 是同一个包同一条拉链。

- 族内相关 ρ≈0.6、族规模 m≈4 → `n_eff ≈ 12/(1+(m−1)ρ) ≈ 4.3`
- 全部同向时符号检验单边 p 从 **0.000244（n=12）** 变成 **0.0625（n=4）——不显著**
- 叠加 tie：D 族天花板时两方向的 Δ 常恰为 0，符号检验**静默丢弃 tie**，n 从 12 掉到 8（全同向 p=0.0039 仍可用，但 6/8 同向 p≈0.29 直接崩）

**四条一起上**：
1. **检验换成族级 cluster 重抽样**（cluster = **族**，不是任务）：报族聚类的 p 与 naive n=12 的 p 两个数，**摘要里只准用前者**；或用带族随机截距的混合效应模型。
2. **★ 提高族数（真正决定效力的量）**：加抽屉（prismatic）作第 4 族、双臂交接/放置作第 5 族，各 2 个变体；总任务数保持 12–14，族数 3→5，n_eff 从约 4 抬到约 7（全同向单边 p≈0.008）。**同时把 4 个门变体换成 4 台不同家电、3 个拉链变体换成 3 个不同的包**（§6.3）。
3. **用 ordinal 进度分消除 tie**：P3′ 的任务级量改为"两方向的平均进度分之差"，Wilcoxon 符号秩，D 族即使 SR 都是 100% 也仍有连续读数。**这要求为 D/Z 也预注册 ordinal 阶梯**（approach / grasp / partial-actuation / complete），不能只有 F 有 0–4 分。binary SR 降为次要报告，**并明写被丢弃的 tie 数**。
4. 从 pilot 直接估出族内 Δ 相关 ρ，把 n_eff 的计算写进 §IV。

### 修法 5：盲评（修复成本几乎为零，不做是教科书级实验者偏差入口）

施工图只写了"两名标注者 10% 样本算 Cohen κ"。**κ 度量 reliability，不是 validity**——两名都知道假设的作者互相同意得越好，偏差越一致。

- **(a) 盲评**：标注者只看末帧俯视图（进度分看固定 checkpoint 帧），**文件名随机化**，arm/方向/条件/试验序号全部剥离，base 与 ours 的帧交错混排。
- **(b) anchor items**：每批嵌入约 20 张预先定分的参考图（覆盖 0–4 全档），检测评分漂移与宽严偏移；报每位标注者的边际分布。
- **(c)** 至少一名标注者**不是本文作者、且不知道假设**。
- **(d)** κ 报在**盲评批次**上，非盲的 κ 无意义。
- **(e) 重置者也要盲**：做"抖开摊平"的人看得见上一条 trial 的结果与条件，会无意识地对失败条件重置得更仔细。**把重置者与条件解耦**（脚本只在重置完成后才抽取条件），并把重置时长与初始状态度量作为条件相关性审计的输入。

### 修法 6：环境非平稳性与试验顺序共线（可形变/易磨损物体特有，刚体任务无先例可抄）

拉链在数百次开合后齿列磨损、咬合力改变；一件 T 恤折 300 次后形成固化折痕——**等于环境本身携带了"记忆"，会系统性偏向后跑的那个条件**。

- **(a)** 每个变体准备 **≥3 件物理相同的实例**，轮换使用并记录 instance id。
- **(b)** 配对内随机化先后（明写为规程），跨会话随机化任务顺序。
- **(c) 漂移审计（一行，免费）**：把 base arm 的成功/进度分对 trial 序号做回归，报斜率与 CI；若斜率显著 ≠ 0，所有 pooled 数字必须加会话/实例协变量重算。**主动写进 §IV，比等审稿人问强。**

### 修法 7：oracle 阶梯在"可形变 + 双臂"下的三处失效

1. **`retarget-oracle` 要求 ground-truth 锚点，而衣物没有刚体位姿**——关键点真值只能靠逐帧人工标注（估 3–4 任务 ×15 trials ×~10 时刻 ×2 方向 ≈ **1200–1800 次标注**），这恰恰是该阶梯当初为对抗 R2-B10 而承诺要避免的"事后人工归因"。
   → **限定域并明说**：oracle 阶梯**只在 D 与 Z 两族上跑**（锚点是铰链轴与拉链轨道，一次性物理标定，真值免费）；§V-C 明写 F 族 "anchor-oracle not available"。若一定要覆盖 F，用**辅助通道 fiducial**（在 CLASP 关键点位置贴 5 个标记，用红外反光标记 + 独立标定的辅助相机，或普通标记但**在策略输入流里把标记像素 mask 掉**）——无论哪种，**"标记是否泄漏进观测"必须作为一行审计报出来**。
2. **双臂新增一个不在三桶里的失败模式**（`T_rel` 不可满足）→ **加第四桶 A8 `coordination-oracle`**（§6.4）。纯软件、零机器人小时。
3. **阶梯假设各级 Δ 非负可加，但 `Δ_key` 完全可能为负**（强制"正确"的写者条目对读者运动学不可行）。→ **预注册负值处理**：若任一 Δ < 0，**禁止画堆叠柱状图**，改画阶梯折线并在正文声明"这是一串干预，不是方差分解"。

**外加 §3.4 的要求**：`Δ_retarget` 必须拆成 `Δ_limit`（19.2 pt）与 `Δ_geom`（0.0 pt）。

### 修法 8：双臂失败模式必须用预注册的**自动 first-fault 规则**

不做事后人工归因。连续记录两臂最小间距（URDF 可算）、`|T_rel(t) − T_rel_ref(t)|`、"一臂张开而另一臂正在扫掠"等事件，**时间上最早触发的事件即为归因类别**。类别至少覆盖：臂间碰撞、`T_rel` 漂移、角色反转（谁稳定谁动作）、相位失同步、单臂中止。
**一个日志脚本的成本，换掉一整轮"你怎么知道是这个原因"的质询。**

### 修法 9：主端点必须并列报 base SR

施工图已要求并列 IR，但没要求并列 **base SR**。没有它，读者无法判断某任务的 Δ=0 是"记忆没用"还是"天花板/地板"。这一列同时是修法 1 与修法 4(3) 中 tie 分析的输入。

## 6.9 逐任务成功判据

**原则**：7 个门/拉链变体 + F5 全自动；4 个叠衣变体用**预注册 rubric + 人评分级进度**。后者有 venue 级先例——π0.5 与 VLAC 两篇都用"二值成功率 + 人评 task progress"双指标（VLAC 逐字："Task progress is evaluated by humans, allowing for more detailed progress assessments when the task is not fully completed"）。

| 变体 | 传感 | 成功条件 | 类型 |
|---|---|---|---|
| **D1 开微波炉** | 门板 AprilTag + 固定侧视相机 → 铰链角 θ | θ ≥ 70° 且保持 2 s；无整机位移 >2 cm | **自动** |
| **D2 关微波炉** | 同上 + 门框**簧片开关**（约 ¥5） | θ < 3° **且**开关闭合（卡扣真的咬上）持续 2 s | **自动** |
| **D3 开洗衣机** | 同 D1 | θ ≥ 60° 且保持 2 s | **自动** |
| **D4 关洗衣机** | 同 D2 + 簧片开关 | 开关闭合 且 θ<3°（胶条压合到位） | **自动** |
| **Z1 拉开** | 俯视相机 + 沿轨道印刷刻度带，模板匹配读拉头位置 | 拉头行程 ≥ 轨道 90%，且拉头未脱轨（仍在轨道 mask 内） | **自动** |
| **Z2 拉合** | 同上 + 闭合缝分割 | 已合缝长度 ≥ 轨道 90%，且两侧布带未咬入（咬入 = 缝宽 > 2×标称） | **自动** |
| **Z3 放物+拉合** | 同 Z2 + 包内物体检测 | 物体完全在包内 **且** Z2 条件成立 | **自动** |
| **F5 叠至指定矩形** | 俯视 RGB-D | 衣物全部像素落入目标矩形内，且外接矩形 ≤ W×H（预注册） | **自动** |
| **F1–F4 叠衣** | 俯视 RGB-D | **三项全中**（见下） | **rubric，需盲评 κ** |

### ★ F1–F4 的判据必须改一条：面积代替厚度

施工图/重设计写的 (iii) 是"中心厚度 ≥ k × 单层厚度"。**这在物理上测不出来**：T 恤单层约 0.5–1 mm、四层 2–4 mm；消费级深度相机在 0.6 m 上 RMS 噪声约 2–5 mm，且布料低纹理、深度质量更差。**判据里有一条不可执行，整个 rubric 的可复现性主张就破了。**

**修法（对深度噪声免疫，且直接编码折叠次数）**：
1. 外接矩形 ≤ W×H；
2. 无衣物像素越出目标区；
3. **面积判据**：预先测得该衣物摊平后的俯视 mask 面积 `A0`，要求末态 `A_final ∈ [A0/2^n × (1−τ), A0/2^n × (1+τ)]`，`n` 为该变体预注册的折叠次数，`τ` 例如 0.20。**"揉成一团"的面积显著小于 `A0/2^n`，被下界拒掉；折不到位的面积偏大，被上界拒掉。**

若确需厚度，改用**侧视相机对高对比背景的轮廓高度**（毫米级可读）或一支落下的轻探针作物理量规——**不要用俯视深度**。

### 叠衣族的三条纪律（缺一条就会在 rebuttal 变成一轮质询）

1. rubric 的 W、H、n、τ **在采数前冻结**并写进补充材料；
2. 两名标注者在 **10% 样本**上算 **Cohen κ**（**盲评批次上**）并报出来；
3. 同时报 **0–4 分分级进度**（袖1折入 / 袖2折入 / 主体对折 / 达标尺寸），使未完成的 trial 也有可比读数。

### 自动判据本身也要审计

"12 个中 8 个全自动"这个说法**偏乐观**：F5 依赖目标矩形的精确标定，Z1–Z3 依赖模板匹配与分割阈值，D1/D3 依赖 AprilTag 不被门体自遮挡。

- **每条自动判据都在约 50–100 个人标样本上报一次 precision/recall**，与 VLAC 写入门控的标定**用同一批数据、同一套流程**。一行审计，顺手把"自动判据可信"从声称变成测量。
- **Z1–Z3 必须规定在释放并回到 home 位之后的静止帧上测量**——否则夹爪遮挡拉头与刻度带（这正是 2112.06442 的核心发现）。"两侧布带咬入"的分割阈值需在约 50 张手标帧上标定并报假阳率。
- **D2/D4 的簧片开关只能确认卡扣咬合，不能确认"没有损坏/没有暴力压合"**。补一条 **abort 判据**：任一关节力矩超过预注册阈值即判失败并记录——否则一次把门压变形的执行会被记成成功。
- **降规格建议**：簧片开关和刻度带是几块钱的方案，保留；**闭合缝分割与包内物体检测改成人工复核**（Z2/Z3 各约 100 trial，人工 5 s/条完全可承受），砍掉两套视觉工程。

## 6.10 ★ 真机 demo 规划

> **定位**：demo 不是用来展示成功率的——表格已经干了那件事。**demo 的唯一职责是让一个怀疑的审稿人在 15 秒内相信一件他本来不信的事。**
> 本节独立于统计设计，但**素材必须在主实验跑的同时录**，不另开一轮（见 §6.10.6 预算）。

### 6.10.1 先确定"什么是没人拍过的"

| 已有工作的视频拍了什么 | 我们不能重复的 |
|---|---|
| R-t-S：冻结策略 + 记忆让**同一台**机器人变好（**同款双臂 PiPER、同样冻结 π0.5、叠 T 恤 42.0→50.0**） | ❌ "记忆让机器人叠衣服变好"——拍这个等于自证增量 |
| RECAP：往检索池加演示、不重训就会新任务 | ❌ "不重训学新任务" |
| RAM：检索 affordance 迁到别的机器人，**但库是离线静态第三方语料** | ❌ "跨本体读一个预先建好的库" |
| GR00T：跨本体，但**要更新参数** | ❌ 任何含训练步骤的迁移 |
| MimicDroid / RoboTTT：人类视频 → 机器人，**用完即弃** | ❌ in-context 单次演示 |

> **没有一个拍过：一台机器人在自己部署中产生的经验，被另一台机器人读走，中间没有任何重训。**
> **这就是那一枪。全片的结构都围绕它。**

### 6.10.2 分段脚本（总长约 3 分钟）

#### 第一段 · 唯一真正重要的那一枪（约 40 s）

| 项 | 内容 |
|---|---|
| **画面** | Piper 反复尝试某任务变体，失败 2 次，第 3 次成功 → **不切黑场**直接推到 PiperX，同一变体、同一初始状态 → 先跑无记忆基座（失败）→ 再跑读取记忆（成功） |
| **角标** | `entry written · 0 parameters updated`；**一个从 Piper 成功那刻开始走的真实墙钟计时器** |
| **它证明什么** | 计时器会停在几十秒。这个数字是全片最有说服力的东西——因为"跨本体迁移"在所有其他论文里意味着几小时到几天的重训 |
| **★ 建议的加强版** | Piper 成功后**把它断电、推出画面**，再让 PiperX 读。同时干掉必然被问的"两台是不是在实时通信"，并把"记忆比写它的身体活得久"变成字面画面 |
| **前置条件** | 需要一个 Piper 基座 SR 落在 30–50% 的变体（这样"失败 2 次再成功"是自然发生而非摆拍）；需要写入门控在线跑通 |

#### 第二段 · 这才是论文的贡献（约 50 s）

第一段只证明了"能迁"，没证明**论文在争什么**——论文争的是"一条经验必须存成什么才迁得动"。

| 项 | 内容 |
|---|---|
| **画面** | **同一条条目、同一初始状态、同一台 PiperX，只换读出层级**。读④层（关节直接回放）→ 姿态明显歪掉、抓空、失败；读③层（锚点系接触点运动）→ 成功。并排 |
| **它证明什么** | 把"交叉点"从一条曲线变成一件**看得见**的事：同一段经验在一个层级上是废的、在另一个层级上是好的。**没人拍过这个，因为没人分层存** |
| **复用** | 这段的静帧直接做 **Fig. 1 panel (b)** |
| **前置条件** | G0.5 已确认交叉点存在（否则这段拍不出对比）；④层回放要用**物理单位**（§4.7），否则失败会混入纯归一化失配这个平凡原因 |

#### 第三段 · 诚实本身就是差异化（约 30 s）

| 项 | 内容 |
|---|---|
| **画面** | 一个**读了外体条目反而变差**的案例 → 置信度门控把它挡下 → 回退到基座 |
| **它证明什么** | 三件事同时兑现：Abstract 主动宣称的 memory-harm rate；**"相似度门看不见可执行性"**（红队认定最非平凡的发现）；以及"我们知道它什么时候不该跨" |
| **为什么值得占 30 秒** | 大部分 demo 不敢拍失败。审稿人看到你敢拍，对前两段的信任度会明显上升 |
| **前置条件** | **要先找到这样的案例**——这是全片唯一需要"打捞"的素材，见 §6.10.6 |

#### 第四段 · 机理，而不是现象（约 30 s）

| 项 | 内容 |
|---|---|
| **画面** | Piper→PiperX 成功；反向同任务失败。**失败瞬间在画面上叠腕关节角度条**，显示撞到 Piper j5 的 ±70° 限位 |
| **字幕** | `the reader's wrist envelope, not the workspace size` |
| **它证明什么** | 把 **P3′** 从一个 p 值变成一个**看得见的物理原因**；同时预先堵掉"你们的 gap 就是工作空间大小差异"（已被 IoU=0.528 证伪，但视频比文字快） |
| **前置条件** | 需要挑一个真的会触限的变体——可由离线 φ 预先筛出（§10 第 4 条的 per-task φ 正好给出候选） |

#### 第五段 · 换读者的代价（约 20 s，可选）

| 项 | 内容 |
|---|---|
| **画面** | **单臂模式读者**（D6）读双臂条目：③④层结构性不可读 → **分层回退**到②层子目标序列 → 仍能完成，只是慢、精度低。回退层级在屏幕上标出 |
| **它证明什么** | 兑现 "admitting a new reader costs \todo{N} paired episodes and no policy gradient"；同时是 D6 通过 own-task-competence 判准的可视证据 |

### 6.10.3 任务选角

| 任务 | 派什么用场 | 理由 |
|---|---|---|
| **拉链（Z）** | **第一、二段的主角** | 成败**二值可见**（拉链开没开一眼看到）；时长适中（2.1 min）；③层的弧长锚点可以直接在画面上叠一条进度条 |
| **门（D）** | 第四段方向不对称 | 腕部限位的故事最干净；开合角可视化容易；单次仅 0.6 min，可连拍多组 |
| **叠衣 F5（叠至指定外接矩形）** | "语言不可表达"的证据 | "把衣服叠好"不指定折线位置；要塞进给定抽屉就必须折在特定位置。**旁边并排放 instruction-only 对照，让它折出一个塞不进去的形状**——这一个对比就证明了"记忆 ≠ 更好的 prompt"（对抗 R1-B4） |

### 6.10.4 四条让它经得起看的规矩

1. **成对试次连拍 3–4 组，不要只放一组。** 一组是轶事，四组同向才是证据。**实时不剪**，加速必须标注倍率。
2. **屏幕上挂 injection rate。** 论文报它，视频也报它——预先堵掉"你是靠多弃权刷高的"（R2-B1）。
3. **无记忆基座的尝试必须完整播完**，包括它挣扎的过程。只放我方成功片段是 demo 里最容易被识破的作弊。
4. **每段角标写清 trial 计数**（第几组 / 共几组），不给"精选"留空间。

### 6.10.5 不要拍的

- ❌ **"记忆让机器人叠衣服变好"**——R-t-S 已拍过（§6.10.1）
- ❌ **长时程炫技**（抽衣→叠→入篮一镜到底）。好看，但它证明的是**策略能力**不是**记忆能力**
- ❌ **记忆库规模曲线的动画**。那是表格的活
- ❌ 任何含"训练中…"进度条的镜头——与 "no gradient once deployed" 直接冲突

### 6.10.6 预算与录制纪律

**核心原则：demo 素材在主实验跑的同时录，不另开一轮。**

| 段 | 素材来源 | 增量机器人小时 |
|---|---|---|
| 一 | 主端点的成对 trial（Z 族）+ **断电推走那一镜需专拍** | **+0.5** |
| 二 | 四层 sweep 的③/④两档（本来就要跑） | **0**（纯复用） |
| 三 | **需要打捞**：从全部 trial 日志里筛 `base 成功 & ours 失败` 的成对样本，回放复现 | **+1.0** |
| 四 | P3′ 的双向 trial（本来就要跑） | **0**（纯复用） |
| 五 | D6 单臂 reader 准入实验（本来就要跑） | **0**（纯复用） |
| F5 vs instruction-only | instruction-only 对照本来就在消融里 | **+0.3**（补拍并排机位） |
| **合计增量** | | **≈ 1.8 robot-hours** |

**→ 计入 §6.6 预算表后总数从 ≈150 h 变为 ≈152 h，不影响任何结论。**

**但有三条录制纪律必须从第一天就执行，否则事后补拍的成本是这个数字的 10 倍**：

1. **第三方电影机位从第一个 trial 就架好并常开。** 实验用的三路相机（base + 双腕）画幅和角度都不适合出片。补一个固定第三方机位，全程录制，事后只做剪辑不做重拍。
2. **每条 rollout 的元数据必须与视频帧同步落盘**（trial id / 方向 / 层级 / 条件 / injection 与否 / 成败）。第三段的"打捞"完全依赖这个——没有它就得靠人肉翻录像。
3. **所有角标（计时器、injection rate、回退层级、trial 计数）在录制时就烧进日志**，剪辑时叠加。事后估算的数字不能上屏。

### 6.10.7 与 gate 的关系

| Gate | 对 demo 的含义 |
|---|---|
| **G0.5**（9-05） | **不过则第二段拍不出来**（无交叉点则③④没有对比）。此时 demo 结构改为：第一段 + 第三段扩写为主体（cross-body admissibility framing 的可视化） |
| **G2a**（9-26） | 通过则第一、二段的③层素材可开始录 |
| **G5**（12-19） | 首批跨本体真机数出来即可拍第一段样片，**不要等到 G6**——早拍一版能暴露机位与角标问题 |

### 6.10.8 一句话

> **第一段证明"能跨"，第二段证明"为什么能跨"，第三段证明"我们知道它什么时候不该跨"。**
> 三段拍成，这个 demo 就没法被归到任何现有工作里。

---

# 7. 新增风险与对策

> 排序按"会不会杀死论文"，不按发生概率。诚实标注**无解**的。

## R1（最致命）★ 谱系交叉点不存在 → 四层谱系框架死亡

**风险陈述**：在 6-DoF 无零空间的臂上，**同本体** FK→IK 几乎无损（实测 position-only 100.0%），③与④很可能生成数值上几乎相同的轨迹，`SR_same(④) − SR_same(③) ≈ 0`。谱系退化为"越抽象越可迁移"的单调阶梯——GR00T N1.7 已主张过，不是 finding。

**为什么这比"压平"更严重**：压平至少还能诚实报告（"我们测了，没有差异"）；**没有交叉点则整篇论文的净增量只剩"我们在两台臂之间跑了一遍"**——集成报告，不是 RA-L finding。

**对策**：
- **G0.5 gate（新增，排在一切之前，成本 ≈ 0 机器人小时 + 2.3 h 真机确认）**：从存量 Piper 语料取 200 条条目，在**同一台 Piper** 上分别以 ④（直接关节回放）与 ③（FK→锚点系→IK→关节）执行，比成功率与末端轨迹误差。
- **预注册效应量门槛**：`SR(④) − SR(③) ≥ 10 pp`（同本体，成对）。
- **若 Δ < 5 pp → 当场判定四层谱系框架死亡，切 §2.5 的 fallback framing，不等 G4。**
- 若显著 → 把这个 Δ 作为 Fig. 4 的**左端点**，与跨本体的右端点（③≈80%，④≈0）合成交叉，**交叉点本身才是 Fig. 4 的主张**。

**残余风险**：G0.5 用离线回放做，与在线注入下的行为可能不同。**诚实标注**：离线回放是 `SR_same` 差值的**上界代理**，真机确认只有 40 trial，效力有限。

## R2（次致命）★ 层③失败的归因写错 → 被 20 行代码证伪

见 §3.4。**已处理**：本次已复算并给出正确归因（层④←架构、层③←限位），以及容差扫描表（预堵"IK 容差调出来的"）。

**残余风险（无解）**：如果审稿人接受"关节限位差异只是 spec 差异，不算跨本体"，那么层③这一整层的跨本体 gap 都会被质疑。**唯一的防守是框架反转**（§6.1）+ 本体对扩展（D6 单臂 reader）：让 Piper↔PiperX 不是唯一的本体对。**这是本文最锋利的一刀，必须在 Intro 就正面处理，不要藏。**

## R3 ★ 可形变物无法复现初始状态 → HR / McNemar / 成对 Δ 三个量同时失去定义

见 §6.8 修法 2。**对策**：容差化配对定义 + 拒收重做 + **A/A 噪声地板控制**（不可砍，2.3 h）+ 条件污染审计 + (P-deformable) 独立端点。

**残余风险（部分无解）**：即使 IoU≥0.90 的模板配对，褶皱的**微观**构型仍不可复现。**诚实措辞**：把 F 族的配对称为 "state-matched to within a pre-registered tolerance"，**绝不写 "identical initial state"**；并在 §IV 给出达成的 IoU 直方图。

## R4 谱系压平（原风险 #1）：**已降级为可控，但风险方向反转了**

**原担心**：Piper↔PiperX 是同构双臂，④层做一次 retarget 就能用 → 谱系压平。
**实测否定**：④层朴素复制姿态误差 82.8°，最优固定标定后仍 17.8°/7.1 cm。

**★ 新的真实风险是"层④像稻草人"**：审稿人说"不同架构的臂当然关节空间不能迁移，这是常识"。
**对策**：
1. **必须加同本体条件**，设计成 2×2：`{Piper→Piper, Piper→PiperX} × {层①②③④}`。**层④在同本体上应当是精度最高的一层**（这正是"谱系"而非"层级排序"的关键）。→ 这就是 R1 的 G0.5。
2. **必须加 A7 消融**（④+腕部重解算，6.7°）并主动给出论证：`④+wrist-repair ≡ ③`（§6.4）。
3. **必须自己先报标定后的数字**（17.8°/7.1 cm），不留给审稿人说。

**残余风险**：若 §1.6 #1 的答案是 piper_h/l，本节全部反转成"压平"（H/L 与 Piper 同架构，朴素复制姿态误差**恰好 0.0°**，层③ IK 可行 94.0%/86.8%）。→ **立刻切 D6 单臂 reader 作主实验。** 确认成本是拿把尺量臂展。

## R5 工程量缺口 2.5 倍 + 关键路径串行化

见 §8。**对策**：明确 FTE；不足则切 MVP（§8.3）；双轨分段（§6.7）解串行；D12 现在就启动。

## R6 抢跑：Retrieve-then-Steer 团队

他们已有 6-DoF PiPER + 7-DoF OpenArm 两具异构本体，正文点名 "different arm kinematics"，**做跨本体记忆只差一个实验**。
**对策**：**G2a 通过后立即 arXiv 占位** P1′/P2/P3′ 的预注册预测。这比 G1 更早的时点不现实（G1 的 Fig. 3 是纯离线，也可作为占位内容）。
**残余风险（无解）**：这是竞争，不是技术问题。

## R7 基座 SR 不落在 20–60% 窗口 → 天花板/地板效应

见 §5.8。**对策**：新增 **G3c**（10k 步小规模微调探窗口，约半天），**必须早于 G3b 的切分冻结**。
**残余风险**：一次重训 = 3–5 天 × 2 台，会直接吃掉 G5→G6 的全部 slack。→ §8 要求留 1.5 周 buffer。

## R8 任务独立性伪重复 → P3′ 拿不到宣称的 p

见 §6.8 修法 4。**对策**：族级检验 + 增加族数（3→5）+ 增加物体实例数 + ordinal 进度分消除 tie。
**残余风险**：族级 n=5 时全同向单边 p≈0.031，**只是勉强显著**。若有一个族反向，p≈0.19。**必须在 Limitations 明写"P3′ 的效力由族数决定，而我们只有 5 个族"。**

## R9 PiperX 侧 openpi 接入全靠自写

见 §5.2。**对策**：排 3.5 周、指定一人、第 1 周 FK 一致性硬验收（<5 mm / <2°）。
**残余风险**：若 FK 残差 >5 mm，**全部离线阶梯不可用，所有 φ 数字作废**——包括 §3.4 的全部证据。这是**单点故障**，必须最先做。

## R10 感知前端在关键路径上（叠衣关键点检测器）

**这是新的"最可能烂尾的一环"**（替换施工图的"③层 object-anchored 在移动本体上的定义与标定"）。
典型烂尾方式：前 3 个月一直显示"基本 work"，第 5 个月做真机跨本体时才发现关键点误差吃掉全部迁移增益，而那时四点谱系已写进 Intro 和 Fig. 1。
**对策**：G2a/G2b 拆分（§8.2）；MVP 直接把叠衣降为 exploratory（§8.3）。

## R11 通用点跟踪器在布料自遮挡下的 drift

**查不到任何 benchmark**（SAM2 / CoTracker / TAPIR 在布料自遮挡下的表现无公开数据）。
**对策**：自建小规模评测，用 **Flat'n'Fold (2409.18297) 的多视角序列**，零采集成本。
**诚实标注：目前无解，只能自测。**

## R12 n=2 的一般性（v4 已接受的风险，继续接受）

两具本体不足以支撑关于 embodiment 的一般规律。措辞一律限定为 "a spectrum measured on this pair"，**绝不写 generalizes across embodiments**。
**D6/D7/D8 的加入把 n 从 2 提到 3–5**，缓解但不解决。**无技术解。**

## R13 绝对成功率可能很低

对照：RECAP 真机 close-cabinet 30%；RoboMME 最好方法 44.51% 而人类 90.5%；**R-t-S 在同款硬件同任务上 39–48%**。
**已在 §1 ¶5 主动划边界**，所有图里画 frozen-base 地板线。**好消息**：R-t-S 的 39–48% 正落在 headroom 窗口，**叠衣族不需人为制造 headroom**（但门族需要，§6.8 修法 1）。

## R14 环境非平稳（拉链磨损、衣物固化折痕）

见 §6.8 修法 6。**对策**：≥3 件物理实例轮换 + 条件顺序随机化 + 漂移审计回归。

## R15 HuggingFace 不可达

VLAC / VLAC-8b / VLAC-Cut 三个 URL 在本环境 curl 超时返回 000。
**对策**：集群侧实测；或走 ModelScope / 内网镜像。**退路（施工图已备）**：遥操隐含标签 + 轻量成功分类器。

---

# 8. 工程量与排期

## 8.1 人月重估

施工图自评 ≈11 PM 对 6.5 PM 已缺口 1.7 倍。**本次重设计的净增量（逐项）**：

| 项 | 周 |
|---|---|
| 叠衣关键点前端（原 D2 的"抓后夹爪代理"3 周方案对布料只保住一半） | +4 |
| 铰链前端与夹具 | +1.5 |
| 拉链 DLO / 拉头 / 刻度带 | +3 |
| 双臂 (T_abs,T_rel) retarget 与聚合改造 | +2.5 |
| 分段规则重写（双轨） | +1.5 |
| **PiperX openpi 移植** | **+3.5** |
| 几百小时转 RLDS + idle filter + TB 级存储 IO | +2 |
| 8 个自动判据的夹具与传感 | +3 |
| VLAC 在 500 条留出 rollout 上的 precision/recall 标定 | +1 |
| embodiment ladder（D1/D2 硬件 + S1/S2 仿真 + D5 sweep + D6 单臂） | +1.5 |
| 两具本体各一次基座微调（而非一次）+ SR 窗口探针 | +2 |
| **小计** | **+25.5 周** |
| 扣掉移动臂消失省下的 | −2 周 |
| **净增量** | **≈ +5.4 PM** |

**总计 ≈ 16–16.5 PM / 28 周 → 需要 2.5 FTE。**

- **≥2.5 FTE**：执行完整版。
- **1–1.5 FTE**：**执行 §8.3 的 MVP，不要中间态。**
- **<1 FTE**：不要启动本课题的完整形态。

**robot-hours 侧**：150 h，两台并行，按 **3 productive h/day/台** → **25 个工作日/台 ≈ 5 周/台**；再加 D12 的 31 h（约 2 周/台）。base fine-tune（两具 × 60k 步，H20 上每具 3–5 天，**且大概率要重训一次**才能把 `T_eval` SR 调进 20–60% 窗口）排进去 → **policy 就绪最早 2026-12-01，与 G5(12-19) 几乎顶格**。

**→ G5→G6 的 6 周要塞下 119 robot-hours + 对齐图训练 + 8 个控制 arm。任何一次重训就直接撞穿 G6。必须留 ≥1.5 周 buffer。**

## 8.2 Go/No-Go 检查点（更新版，日期沿用施工图 §6 的框架）

今天 **2026-08-24**，目标投稿 **2027-03-10**。每个 gate 必须由具体的人在当天交出一个**数**，不接受"还在调"。

| Gate | 日期 | 交付物 | No-Go 判据 → 论文变成什么形态 |
|---|---|---|---|
| **G0** | **2026-08-29** | **(a) ★ 确认 PiperX 型号**（量臂展：626/638/669/751 mm 四值可区分；或看 j4 到腕点是否有 74.66 mm 偏置）；(b) 读两台固件 DH 版本 `GetPiperFirmwareVersion()`；(c) 两台台架几何实测（臂间距/倾角/立柱/相机）；(d) 力/触觉通道有无；(e) **双本体任务重合度审计**；(f) **★ 落锤 FTE 数字**；(g) **★ 按 §6.2 重做锁关节角 sweep**（1 天）；(h) **★ 按 §3.4 出 tolerance-vs-feasibility 4×4 网格**（已部分完成，见 §3.4 证据 C） | (a) 若 = piper_h/l → **D6 单臂 reader 立刻升为主实验第一腿**，谱系论证改走"动作维度降维"而非"腕型差异"；(e) 重合任务 <6 → D12 扩到 12 任务并推迟 G3b；(f) <2.5 FTE → **当天切 MVP** |
| **★ G0.5（新增，最高优先）** | **2026-09-05** | **同本体交叉点**：200 条 Piper 条目，同一台 Piper 上 ④直接回放 vs ③ FK→IK 回放，比 SR 与末端轨迹误差（离线 + 40 trial 真机确认） | **`SR(④)−SR(③) < 5 pp` → 四层谱系框架当场死亡，启用 §2.5 的 cross-body admissibility framing。不等 G4。** |
| **G0.6** | 2026-09-05 | 用真实存量语料统计三族的**真实 exec+复位时长分布** → 锁定 §6.6 预算；**PiperX FK 一致性硬验收**（20 构型，<5 mm/<2°） | FK 残差 >5 mm → **全部离线阶梯与 φ 数字作废**，P5 撤回，必须先解决标定 |
| **G1** | **2026-09-12** | **Fig. 3 两联图（纯离线）**：四种 key × 四种条件（**新增 D1 相机重装档**）的分布 + 重标定后 precision@10 / AUC vs chance；**π_d pilot 结果** | 四种 key 重标定后 precision@10 全 ≤ chance → 主结果改 language-keyed only，对齐图从方法降级为失败的 ablation，重心全移到 §V-C 归因；π_d^F > 0.40 → F 族强制走 (P-deformable) |
| **★ G2a（不可延）** | **2026-09-26** | **门 + 拉链**上的跨本体开环重放（各 50 episode，**离线可做**，前端只用"铰链一次性标定 + 抓后夹爪位姿代理"）：末端轨迹误差 + 接触点命中率 + **双臂 `T_rel` 保持误差** | 误差 >3 cm 或命中 <60% → **层③整体证伪**，论文重心立刻转 P2 归因。**通过后立即 arXiv 占位** |
| **★ G2b（新增）** | **2026-11-07** | **叠衣**上的同一套数，用关键点前端 | 不过 → **叠衣退出 confirmatory 降为定性**，主表只用门+拉链（即自动落到 §8.3 的 MVP） |
| **G3a** | 2026-10-03 | MuJoCo 内换 piper_h / piper_l URDF 重跑（官方 MIT 资产，已具备）；④轴改报二维 (位置, 姿态) | 不可行 → 仿真退出正文 |
| **★ G3c（新增）** | **2026-11-07** | **基座 SR 窗口探针**：10k 步小规模微调，测 `T_eval` 零样本 SR 是否落在 20–60%（约半天） | 不落窗口 → **当天改 `T_base`/`T_eval` 划分**（此时切分尚未冻结） |
| **G3b** | **2026-10-17** | D12 采集完成 + **E0 切分冻结**（+ 家电/包实例扩充完成，族数 3→5） | 完成度 <60% → 放弃对齐图，转 training-free language-key。**注意：基座微调一旦开始，E0 切分不可更改** |
| **G4** | 2026-11-14 | 任一层跨本体 SR 显著高于 frozen base（>2 pp，3 seeds）；derive-on-read 读出延迟数 | 无 → 转负面结果论文；derive-on-read 延迟在预算内且 SR 持平 → Contribution 2 改写为 protocol/measurement 贡献 |
| **G5** | 2026-12-19 | 前 4 任务首批跨本体真机数（含 injection rate） | 跨体 SR < base 或 IR<20% → 当天转向 |
| **G6** | 2027-01-30 | 实验冻结；Fig. 4 实测绘制；决定 6 页还是买 1 页 | 与 P1′ 不符 → **同步替换 Title / Abstract / ¶5 预注册句 / Contribution 2 四处**（绑定，不可只改一个） |
| G7 | 2027-02-28 | 内审（逐条核对写作红线与 Table I 每格证据来源） | — |
| — | **2027-03-10** | 投稿 RA-L | — |

**★ 排期上最重要的一条改动**：施工图把 G2 放在 9-26 且任务选叠衣，**那天必然交不出数**。拆成 G2a（门+拉链，离线可做，不可延）与 G2b（叠衣，11-07）之后，9-26 一定有数可交，且交的是决定论文骨架的那个数。

**buffer**：G5→G6 之间必须留 **≥1.5 周**的重训/重跑 buffer。现在这个排期的 slack 是 0。

## 8.3 最小可发表版本（MVP，1 FTE / 6.5 个月，≈9–10 PM）

> **这是我真正推荐的形态**，除非 G0(f) 确认 ≥2.5 FTE。
>
> **2026-08-24 状态**：本节一度因"无触觉 → 拉链出局"被判作废，该判断已被推翻（§1.7 后果 A）。**本方案维持有效。** 拉链任务已训练成功、数据可用，且③层用抓后夹爪位姿代理、成功判据在释放后静止帧上测量，两处都绕开了触觉文献里的遮挡机理。

**把 confirmatory 从"叠衣撑谱系"换成"门 + 拉链 + 单臂 reader 撑谱系"。**

**保留**：
1. 两台真机、共享单库、双向读写、**E0**（零梯度的唯一证据）。
2. **7 个客观自动判定的变体**：4 个铰接家电（**微波炉 / 洗衣机 / 抽屉 / 柜门**，解决伪重复）+ 3 个不同的拉链包。
3. **3 个 value 层（①③④）**——砍②（与③共用前端且更贵；④免费作退化对照）。
4. **P1′（三点）+ G0.5 交叉点 gate**。
5. **P2 归因（oracle 阶梯 + 第四桶 + `Δ_retarget` 两项拆分）**——最便宜且最独有，**不可砍**。
6. **P3′ 方向不对称**（双向本来就要跑，免费）+ **P5**（离线已成立）。
7. **per-trial memory-harm rate + injection rate + base SR**。
8. **derive-on-read 与 instruction-only 两个对照**（4 任务）——**不可砍**（R1-B3/B4 的解药）。
9. **A7（④+腕部重解算）**——不加会被判稻草人。
10. **D6 单臂模式 reader 作第三具本体**（零硬件成本，通过全部五条判准）。
11. **A/A 控制 + π_d pilot**（8.1 h，全部统计主张的前提）。
12. 真机：**7 任务 × 20 成对 trial × 2 方向 × {base, ours}** ≈ 45 robot-hours；加 D6、A7、对照与 pilot ≈ **75–85 robot-hours**。

**砍掉**：叠衣全族（降为 exploratory 定性视频 + scope 说明）；②层；套垃圾袋；仿真全部结果（只作内部 gate）；RoboMME 报数；P4 降为一行；ANN 延迟曲线；删除泄漏探针；E5（降级为 discussion 一句）；除 R-t-S 之外的全部 baseline 复现。

**这一换解掉三件事**：
- 砍掉最贵的感知（叠衣关键点前端 4 周）与最有争议的判据（rubric + κ + 人评分级）；
- 砍掉 §8.2 的 G2b 依赖，G2a 成为唯一的 ③层 gate；
- 工程量从 16.5 PM 落到 **≈9–10 PM**。

**代价必须诚实写进 Limitations**：
> 门与拉链的双臂耦合度低，因此我们报告的谱系展开幅度是**下界**；"紧耦合可形变任务上谱系更陡"作为**预注册但未检验的预测**留给 future work。

**二选一的规则**：如果坚持要叠衣进主表（它确实是唯一能撑开谱系的族），**那就砍拉链**。**不要两个都留。**
**2026-08-24 更新**：拉链的力/触觉顾虑已排除（§1.7 后果 A），所以这条规则回到"由预算与工期决定"，而不是由硬件决定。MVP 推荐仍是**门 + 拉链 + 单臂 reader**（拉链的③层前端最便宜——抓后夹爪位姿代理，零检测器），叠衣留 exploratory。

**MVP 仍然成立的理由**：论文的不可替代性在"两台都部署的真机 + 更换 reader 无需策略梯度 + 同一协议下的谱系测量与损失分解 + 一个可预测迁移不对称的离线统计量"，**不在 sweep 的宽度**。

---

# 9. 对 `paper_outline_v1.md` 与 `root.tex` 的补丁清单

> 这是下一步施工的输入。每条：文件 / 位置 / 改成什么。
> `paper_outline_v1.md` 与 `paper_outline_v1_zn.md` 行号一致（各 917 行），下同。

## 9.1 `paper_outline_v1{,_zn}.md` — 必改（P0，阻塞写作）

| # | 位置 | 现状 | 改成 |
|---|---|---|---|
| O-1 | **§0.2 摘要中文译稿**（L24–31） | `一个固定底座的 Franka FR3 和一个移动操作机器人都对同一个存储进行双向写入与读取` | `两个已部署的双臂平台——球形手腕的 Piper 与偏置手腕的 PiperX，DoF、负载、重复精度全同，臂展相差 6.9%——对同一个存储进行双向写入与读取` |
| O-2 | **§0.2 Abstract 红线** | 三个必须出现的限定词 | **新增第四个**：`of a different kinematic family`（若 §1.6 #1 = piper_x）或 `of a different action-space dimensionality`（若 = h/l，走 D6 单臂 reader） |
| O-3 | **§0.3 故事线第 3 句** | `在两台都在部署中的机器人（FR3 与移动臂）之间双向读写` | 替换本体名；并**新增一句**：`并给出一个纯离线的运动学统计量，它能预测迁移不对称的方向与逐任务排序` |
| O-4 | **§0.4 Contribution 2** | 四层 value 的表述 | 保留，但**主张收窄为交叉点**：把 "a spectrum" 改为 "a crossover: the level at which same-body fidelity and cross-body transferability trade off"。**并加一句 oracle/auto 双报仍成立** |
| O-5 | **§0.4 Contribution 4** | `一个 oracle 阶梯将差距归因到三个可加项` | 改为**四个**（新增 coordination），且 retargeting 项**拆成 limit-envelope 与 geometry 两项**；并加"若任一 Δ<0 则不画堆叠柱状图"的预注册句 |
| O-6 | **§0.4「我们明确不主张」段** | 现有四项 | **加一句**：intermediate-state injection 的工业实现也见于 GR00T N1.7 的 RTC（`vel_strength` + 指数 ramp）；**同时新增一项主张**：`the change of coordinates that precedes aggregation for bimanual entries`（(T_abs,T_rel) 分解），并注明其正当理由**只能**建立在 IK 可行性上，不能建立在约束破坏上（实测逐臂 retarget 的 `T_rel` 保持误差中位 0.6 mm / 0.0°） |
| O-7 | **§0.6-B 实验 E1**（L96） | `FR3 更换一副夹爪 + 移动相机位姿 + 锁定一个关节` | 替换为 **D6 单臂模式 reader**（AgileX 在售单臂 SKU，动作维度 14→7，`T_rel` 字面消失）；锁关节降为 plan B 且必须做锁定角 sweep（§6.2）。**同时把 §6.2 的五条判准表整表插入 §0.6-B 后** |
| O-8 | **§0.6 未解决风险段** | `reader #3 是同一台 FR3 的改装` | 改为：D6 是同一台机器的单臂模式，但它是**在售配置**且通过 own-task-competence 检验；**必须与跨本体数字并排报出受损读者在自身条目上的 SR** |
| O-9 | **§0.6 抢跑窗口段** | 点名 Dejavu / RECAP / RoboMME / R-t-S | **把 R-t-S 提到第一位**，并补：其附录 D 已在**同款双臂 AgileX PiPER** 上做过 bimanual T-shirt folding（π0.5 42.0→50.0，每任务 50 trials），且已同时拥有 6-DoF PiPER 与 7-DoF OpenArm；**建议 G2a 通过后立即 arXiv 占位** |
| O-10 | **§0.6 附表新增两行** | — | `R4-B1 层③失败被误归因于运动学族（放宽限位即 100%）→ 归因拆两项，§3.4`；`R4-B2 层④只报朴素复制是稻草人（标定后 17.8°）→ 三档标定值 + A7 消融，§3.4/§6.4` |
| O-11 | **§3.2 四层 value 表第 3 行**（L459 附近） | `object-anchored EE deltas … 锚定在物体坐标系（不是机器人基座系——移动底盘下基座系无意义）` | 整行重写为 **anchor-frame task-point motion**（§4.0 的定义）；括号里的理由删掉；**四类任务的锚点表**（§4.1）插入为子表；占位者一列补上 ATM / Track2Act / Im2Flow2Act / MT-π / ContactFlow / Point Policy / P3-PO 等 9 篇 |
| O-12 | **§3.2 四层 value 表第 4 行** | `④ joint-space chunk：写入本体的关节动作序列` | 加一句硬约束：**一律存物理单位，绝不存归一化值**；并**删除 v4 遗留的"潜码"表述**（会被 GR00T EmbodimentTag 吃掉），改为"reader 侧不允许有任何被训练过的解码器" |
| O-13 | **§3.2「②③ 共用同一个感知前端」整段** | `抓取后则利用夹爪自身位姿并借助刚性附着假设` | 改为：**已知抓住了哪个物质点**，夹爪位姿给出该物质点的精确轨迹（point-track 表示）；并**显式定义两套 ② 层 anchor 原语词表**（§4.5）并声明两类任务上②层数字不可直接比较 |
| O-14 | **§3.9 D1 分段规则**（L546） | `夹爪 open/close 状态机 + EE 速度过零` | 改为**双轨分段**（§6.7）；D1 工时保持 1 周（轨 A），轨 B 另计 1 周且**明写不得进关键路径** |
| O-15 | **§3.9 D2** | `抓取后用夹爪位姿代理（刚性附着）3 周` | 拆成 D2a 铰链一次性标定（0.5 周，confirmatory）/ D2b DLO 拉头与刻度带（3 周）/ D2c 叠衣语义关键点（4 周，MVP 中砍） |
| O-16 | **§3.9 新增 D13** | — | `PiperX 侧 openpi 移植（policy I/O、norm stats、pinocchio+casadi FK/IK 重写、SDK 驱动、相机标定）：3.5 周，关键路径，第 1 周设 FK 一致性硬验收` |
| O-17 | **§3.9 新增 D14** | — | `8 个自动判据的夹具与传感（AprilTag/簧片开关/刻度带/俯视 RGB-D）：3 周，关键路径，但不依赖策略与记忆库，9 月即可开工` |
| O-18 | **§4.1 仿真落地路径**（L594） | `在同一套 LIBERO 场景下替换第二个机器人模型` | 替换标的改为 AgileX 官方 `agx_arm_urdf` 的四套 Piper 家族 URDF（**MIT 许可，已下载至 `/tmp/agxurdf/`**）；这条从"可行性待验证"升级为"已有现成资产"。**并加一句：④轴必须改报二维 (位置误差, 姿态误差)，否则 H/L 两档在④轴上是同一个点（姿态误差同为 0.0°）** |
| O-19 | **§4.1 headroom 制造方式** | `不用样本饥饿，改为在评测端施加扰动把基座压到 40–60%` | **保留，但分族限定**：F 族**不需要**（R-t-S 同硬件同任务实测 39–48%）；**D 族必须做**（否则天花板，20 对里只有 1–2 个不一致对）：门初始开合角 [0°,25°] 随机、家电位置 ±8 cm/±10° yaw、加 1 个遮挡干扰物，pilot 调进 25–65% |
| O-20 | **§4.2 平台与任务集分层整表**（L602–612） | S / **M（仅移动臂）** / **F（仅 FR3）** | S 层 12 变体（§6.3 的表）/ **R 层（仅 PiperX，reach 受限）** / **W 层（仅 Piper，腕 roll 受限）**，各 2 个。**并加一句：双向单侧任务直接图示化"工作空间互不包含"（体素 IoU=0.528）** |
| O-21 | **§4.2「语言不可表达」三例** | 按图案擦拭 / 沿非规则路径推动 / 带进给节律的插销 | 替换为 **L1–L4**（§6.5） |
| O-22 | **§4.2 主端点**（L616–620） | 单一 pooled `12 任务 × 20 成对 trial`，McNemar | **拆成两个预注册主端点**（§6.8 修法 1）：(P-rigid) D+Z 成对 McNemar α=0.025；(P-deformable) F 分层随机化 + 连续进度分 + cluster bootstrap α=0.025；Bonferroni。**HR 定义随之分裂，明写不可 pooled** |
| O-23 | **§4.2 效力句** | `240 成对 trial 检测 10 pp 效力 ≈ 80%` | 改为 `n = 785·π_d`，`π_d` **预注册并在 G1 前 pilot 实测**；每行预算表标注隐含 π_d |
| O-24 | **§4.2 P3 的检验方式**（L621–624） | 任务级配对符号检验，n=12，p≈0.0005 | 改为 **族级 cluster 重抽样 / 混合效应模型**（cluster=族）；并**同时报 naive n=12 的 p，但摘要只准用族级**；用 ordinal 进度分消除 tie；**明写被丢弃的 tie 数** |
| O-25 | **§4.3 baseline 表 R-t-S 脚注** | `代码未开源（仅匿名可视化链接）；四个值论文未给` | **补一句**：R-t-S 已在同款双臂 AgileX PiPER 上做 bimanual T-shirt folding，因此它是**同硬件同任务的直接前作**，不只是"同本体检索 SOTA" |
| O-26 | **§4.3 数据切分与泄漏审计**（L655–661） | 三分，按场景与物体实例互斥 | **加一条**：实例 id 纳入互斥维度，**eval 实例必须在颜色/尺码/材质上与 store 实例明确不同**，并在审计行报出；**加 §5.8 的"基座 SR 20–60% 窗口"作为切分设计目标** |
| O-27 | **§4.4 消融表** | A1–A6 | **新增 A7**（④+腕部重解算，实测 82.8°→6.7°，附 `④+wrist-repair ≡ ③` 的论证）与 **A8**（coordination-oracle，第四桶，纯软件） |
| O-28 | **§4.5 P1 行** | 现有措辞 | 替换为 **P1′**（§3.2）：交叉点是唯一主张；判定 (a) 由 G0.5、(b) 由主端点；**"若被推翻"列改为"切 cross-body admissibility framing"** |
| O-29 | **§4.5 P3 行三格** | 预测 `归因于 viewpoint variability`；检验 `移动臂锁底盘再跑一次` | 替换为 **P3′**（§3.3）：机理 = 读者限位包络覆盖率；三级检验（族级符号 + **Spearman 秩相关** + **工作空间交集核对照**） |
| O-30 | **§4.5 oracle 阶梯** | 五级四差 | 改为**六级五差**（插入 `coordination-oracle`），且 `Δ_retarget` **拆成 `Δ_limit` 与 `Δ_geom`**（实测 19.2 + 0.0 pt）；**限定只在 D/Z 两族跑**，F 族明写 anchor-oracle 不可得；**预注册负值处理** |
| O-31 | **§4.5 新增 P5 行** | — | P5（§3.4）：层④←架构、层③←限位；**已由离线实测支持**；被推翻条件 = 真机 FK 残差 >5 mm |
| O-32 | **§4.7 机器人小时预算全表**（L727–748） | 8 行，分钟列一律 1.5/2.0，合计 135–155 | **整表按 §6.6 重算**（按族计时 + 新增 G0.5 / A/A / π_d pilot 三行），合计 ≈150 h |
| O-33 | **§4.7 正文必写句** | `跨本体 trials 需要物理本体更换与复位，单位成本高于同本体` | **这句是错的，必须改写**：两个平台并行运行，跨本体 trial 单位成本与同本体相同；同时报 robot-hours 与 wall-clock（3 productive h/day/台 → 25 工作日/台） |
| O-34 | **§4.8 V-D 段** | `锁底盘对照` | 替换为**工作空间交集核对照** + 两个 writer 的条目质量统计 |
| O-35 | **§4.9 四件事** | 4 条 | **扩为 7 条**：新增 (5) 自动判据的 precision/recall 审计；(6) 初始状态配对容差与达成 IoU 直方图 + A/A 噪声地板；(7) **④层存物理单位、读出时由读者自己归一化**（防平凡混淆，必须进正文） |
| O-36 | **§5.2 人月表** | ≈10.75–11.25 PM | **重估为 16–16.5 PM**（§8.1 逐项），FTE 阈值改为 ≥2.5 / 1–1.5(MVP) / <1(不启动) |
| O-37 | **§5.3 MVP 整节** | 8 任务 × 20 成对 trial，谱系降三点 ①③④ | **整节替换为 §8.3**：confirmatory 换成门+拉链+单臂 reader；叠衣降 exploratory；保留 A7、A/A、π_d pilot、D6 |
| O-38 | **§6 gate 表整表**（L841–855） | G0–G7 | **整表替换为 §8.2**：新增 G0.5 / G0.6 / G3c；G2 拆为 G2a（9-26，门+拉链，不可延）/ G2b（11-07，叠衣）；G0 扩为 8 项 |
| O-39 | **§6「最可能烂尾的一环」整段**（L857–859） | ③层 object-anchored 在移动本体上的定义与标定 | 整段重写：新的烂尾环是**叠衣语义关键点前端**；G2a/G2b 拆分即针对它 |
| O-40 | **§7 P0 第 1 条** | `VLAC 权重可得性核实【待确认】` | **结案：可得**（MIT，327 star，2B/8B 权重公开）。改为 `VLAC 在集群侧的可达性 + 独立 venv 搭建`；并加"用 VLAC 做基座语料数据筛选（非 RL）"这一项 |
| O-41 | **§7 P0 第 4 条** | `E0 数据切分方案落锤` | **加前置条件**：必须先过 G3c（SR 窗口探针），且必须先完成家电/包实例扩充（族数 3→5） |
| O-42 | **§7 P0 第 5 条** | `启动 D12 弱配对采集` | **提前到本周**，且加：若 G0(e) 的重合度审计 ≥6 个任务，**D12 可整块省掉**（31 robot-hours） |
| O-43 | **§7 P2 第 17 条** | `openpi 源码中确认 π0 action expert 的注意力掩码与前缀 KV 结构` | **已完成**（§5.2）：注入点 = `pi0.py::sample_actions` 的 while_loop carry `x_t`，`num_steps=10`。改为可执行项：`把 while_loop 展开为 Python 循环 + 同 seed 数值一致性检查（半天），排在所有记忆库工程之前` |
| O-44 | **§7 新增 P0 第 0 条** | — | **`确认 PiperX 型号`（量臂展）**——一条如果搞错，SQ1 结论从"低风险"翻成"高风险"，而确认成本是拿把尺 |

## 9.2 `paper_outline_v1{,_zn}.md` — 建议改（P1）

| # | 位置 | 改动 |
|---|---|---|
| O-45 | §2.3 II-C | 格局图右下角新增 `Instant-Fold (2606.04269)`（无梯度读一条折叠演示的最近先例，必须主动划界） |
| O-46 | §2.4 Table I | ours 行的 body 列改为 "two bimanual platforms, different wrist topology"；R-t-S 行的 body 列补 "ALOHA-PiPER (bimanual) + OpenArm" |
| O-47 | §3.3 key 构造 | `obj-rel` 一项在可形变物上要改用语义关键点关系图；**加 D1 相机重装档**作为 key 侧的干净控制组 |
| O-48 | §3.4 边界声明英文原句 | 替换为 §2.3 的新措辞（含 GR00T RTC + bimanual change-of-coordinates） |
| O-49 | §3.6 两个 store 表 | `S_corpus` 规模 `10⁴–10⁵` 改为 **`10⁴–N_max`（明写 N_max）** |
| O-50 | §4.0 图表映射 | Fig. 5 的 caption 改为"六级五差"；新增一行"层④标定阶梯（naive / affine / linear）→ 正文 2 行 + 3 个数字" |
| O-51 | §5.1 页数 | 新增内容（P5、标定阶梯、两个主端点）会挤爆 §V 2.05 页。**建议现在就决定买 1 页（7 页）**，而不是 G6 才决定 |
| O-52 | §7 P1 第 9 条 | trials 数决定：改为 `n = 785·π_d`，并注明 R-t-S 真机 50 trials/任务（同硬件同任务）是可比锚点 |

## 9.3 `RAL2027/paper_src/root.tex` — 必改

| # | 位置（行号 / label） | 改成 |
|---|---|---|
| T-1 | **L86–87（Abstract）** | `A fixed-base Franka FR3 and a mobile manipulator both write to and read from one store, in both directions.` → `Two deployed bimanual platforms of different kinematic families---a spherical-wrist Piper and an offset-wrist PiperX, identical in DoF, payload and repeatability and differing by 6.9\% in reach---write to and read from one store, in both directions.` |
| T-2 | **L88–89（Abstract）** | `decompose the cross-body loss into key-side, retargeting and value-side terms` → `...into key-side, limit-envelope, architecture and value-side terms`（四项，见 §3.4/§6.8 修法 7） |
| T-3 | **L84（Abstract）** | 四层 value 的列举中 `object-anchored end-effector deltas` → `anchor-frame contact-point motion with an explicit $(T_{abs}, T_{rel})$ split` |
| T-4 | **L82（Abstract）** | `a second deployed robot` → `a second deployed robot of a different kinematic family` |
| T-5 | **L145（Intro ¶3 注释）** | `base frame is meaningless to a body whose base moves` → 该理由失效；改为 `joint-space content is body-private: the best fixed calibration map still leaves 7.1 cm / 17.8 deg` |
| T-6 | **L153（Intro ¶4 todo）** | `layered value + body-agnostic key + one shared readout interface` → 加 `+ a change of coordinates for bimanual entries` |
| T-7 | **L156（Intro ¶5 注释）** | `one body pair` → `two body pairs plus a single-arm reader`；并加 `the spectrum we report is a lower bound because the door and zip families are weakly coupled bimanually` |
| T-8 | **L162–172（Fig. 1 teaser）** | 两张真机实拍换成双臂 Piper / 双臂 PiperX；panel (b) 的四层内容从**我们自己的库**导出真实样例 |
| T-9 | **L482（`sec:method:readout`）** | `For same-body reads the highest-fidelity level~(4) is preferred` → **保留，但加一句**：this preference is itself an empirical claim, tested in Sec. V-B（即 G0.5 的交叉点） |
| T-10 | **L516（`sec:method:lifecycle` 注释）** | `VLAC weight [availability]` → **已核实可得**（MIT，2B/8B）；改为记录 `done_threshold` 的重标定与自测 precision/recall |
| T-11 | **L597–604（`sec:setup` 注释：PLATFORMS / TASK TIERS）** | 整块替换：平台 = 双臂 Piper / 双臂 PiperX（+ 单臂 reader）；tier = S 12 / **R 2（PiperX only, reach）** / **W 2（Piper only, wrist roll）** |
| T-12 | **L605–609（S tier 的"语言不可表达"注释）** | 三个例子替换为 L1–L4 |
| T-13 | **L613–617（仿真注释）** | LIBERO↔RoboCasa 的论据保留（它论证的是"一次改 8 个变量"），但落地路径改为同一 MuJoCo 场景内换四套官方 Piper 家族 URDF |
| T-14 | **L620–626（四件事）** | 扩为七件（见 O-35） |
| T-15 | **L628–648（Reporting protocol）** | 三条硬规则保留；**新增第 (d) 条**：every success-rate cell also prints the reader's own memoryless base SR；**新增第 (e) 条**：HR 在 rigid 与 deformable 两族上定义不同，不得 pooled |
| T-16 | **L691–702（oracle ladder 注释）** | 五级 → **六级**（插 coordination-oracle）；`D_retarget` 拆两项；加"只在 D/Z 两族跑"与"负值不画堆叠图"两句 |
| T-17 | **L716（Direction 注释）** | `Key control: lock the mobile base and re-run` → `Key control: restrict both writers' entries to the voxel intersection of the two workspaces (IoU = 0.528) and re-run` |
| T-18 | **模板** | `paper_src/` 现为 ICRA 的 `ieeeconf`；投 RA-L 需换 **`IEEEtran` 期刊格式**。换完立刻用真实字数做一次排版对账 |

## 9.4 `threat_RAM_RoboOS.md` — 必改

| # | 改动 |
|---|---|
| H-1 | **③层占位者补上 GR00T N1.7**：其 README 明文主张 relative EEF action space 是 "a key factor in the model's cross-embodiment performance"，且已参数化为 `ActionConfig(rep=RELATIVE, type=EEF)`。→ **③层不能再宣称新颖**，重新定位为"已知会迁移的那一层，纳入谱系是为了给另外三层提供标定基准（upper anchor）" |
| H-2 | **注入机制的占位者新增 GR00T N1.7 的 RTC**：`get_action_with_features()` 的采样循环里 `vel_strength` 是 `[B, horizon, action_dim]` 逐元素张量，已作为公开 steering 钩子存在（外部动作 inpaint 进中间态 + 软掩码 + 指数 ramp）。声明措辞从"沿用 Retrieve-then-Steer"扩为"沿用采样器中间态注入这一类机制，该类机制在 GR00T N1.7 的 RTC 中亦有工业实现" |
| H-3 | **③层表示的占位者补上 9 篇 point-track / flow 族**（ATM 2401.00025 / Track2Act 2405.01527 ECCV'24 / Im2Flow2Act 2407.15208 CoRL'24 / MT-π 2501.06994 / 3DFlowAction 2506.06199 / PointAction 2606.03943 / ContactFlow 2607.26579 / Point Policy 2502.20391 / P3-PO 2412.06784）；以及 kPAM 2.0 (RA-L, 2102.06279) 的 "object-centric action representation in terms of … oriented keypoints" |
| H-4 | **条目 schema 的占位者补上 RDT-1B** 的 128 维 `STATE_VEC_IDX_MAPPING`（③④按臂并列具名 + `action_mask`）。本文**直接采用**，不主张 |
| H-5 | **R-t-S 从"注入机制提供者"升级为"同硬件同任务直接前作"**（附录 D，双臂 AgileX PiPER，bimanual T-shirt folding，π0.5 42.0→50.0） |
| H-6 | **新增 Instant-Fold (2606.04269)**：可形变物操作的 in-context imitation learning，无梯度读一条折叠演示。划界：episodic/context、用完即弃、不跨本体 |
| H-7 | **GR00T EmbodimentTag 明确记为对照而非威胁**：`CategorySpecificLinear.W = 0.02*randn(num_categories, in, out)`，新本体拿到一片随机初始化的 state/action 编解码权重，**必须用该本体数据训练**。→ **GR00T 用"更新参数"解决跨本体，本文主张"不更新策略参数"。这是全文最好用的一句对照，建议在 Intro 直接引用** |
| H-8 | **跨机器人的布料操作经验迁移：查不到**（`all:"cloth manipulation" AND all:"cross-embodiment"` → **0 条**）。**这个空白是真的**，可写 |

## 9.5 venue 订正（并入 v4 §9 参考文献表）

| 文献 | v4 标注 | 订正为 | 依据 |
|---|---|---|---|
| VLAC (2509.15937) | arXiv | **ICML 2026** | README 首行挂 OpenReview `i7mfaYYLDf`；bibtex booktitle = "Forty-third International Conference on Machine Learning" |
| SRPO (2511.15605) | `arXiv，CVPR 收录未证实` | **CVPR**（保守写 CVPR，年份以官方为准） | 本地 PDF 页眉逐字 "This CVPR paper is the Open Access version… identical to the accepted version" |
| TwinVLA (2511.05275) | 未列 | **ICLR 2026 Poster** | 新增 |

**新增引用（按族）**：
- **铰接感知**：ScrewNet (ICRA'21, 2008.10518)；FlowBot3D (RSS'22, 2205.04382)；Ditto (CVPR'22 Oral, 2202.08227)；Kinematic-aware Prompting (ICRA'24, 2311.02847)
- **可形变**：Cloth Funnels (2210.09347)；SpeedFolding (IROS'22, 2208.10552)；CLASP (2507.19983 / ICRA'25 2408.08160)；BiFold (ICRA'25, 2501.16458)；MetaFold (2503.08372)；Flat'n'Fold (2409.18297)；Instant-Fold (2606.04269)；kPAM 2.0 (RA-L, 2102.06279)
- **DLO / 拉链**：mBEST (RA-L'23, 2302.09444)；BUDS (CoRL'23, 2309.01087)；2112.06442（背包拉链，纯视觉 56.7% vs +触觉 93.3%）
- **point-track / flow 跨本体**：ATM / Track2Act / Im2Flow2Act / MT-π / ContactFlow / Point Policy / P3-PO（7 篇，按族打包为 1–2 条）
- **双臂协同**：Chiacchio 1996 (DOI 10.1115/1.2802344)；Caccavale 2008 (DOI 10.1109/tmech.2008.2002816)；Extended Relative Jacobian (ISRR'19, 1905.01248)；TwinVLA (ICLR'26)
- **基座与对照**：π0 (2410.24164)；π0.5 (2504.16054)；GR00T N1 (2503.14734)；RDT-1B (ICLR'25, 2410.07864)；OpenVLA-OFT (2502.19645)；PriorVLA (2605.10925)；HELP (2607.09776)
- **任务坐标系理论**：Bruyninckx & De Schutter (IEEE T-RA 1996, DOI 10.1109/70.508440)；Berenson et al. TSR (IJRR 2011, DOI 10.1177/0278364910396389)

> **注意 §0.5 的 40 条参考文献硬预算。** 上面新增约 30 条 → **必须按族打包**（每族只单列 2–3 篇，其余合并 e.g.），或**买 1 页**（§9.2 的 O-51）。建议现在就决定买 1 页。

## 9.6 复现脚本与数据（本次一手，全部在 `/tmp/agxurdf/`）

| 文件 | 内容 | 状态 |
|---|---|---|
| `piper.urdf` / `piper_x.urdf` / `piper_h.urdf` / `piper_l.urdf` | AgileX 官方 URDF 原件（MIT） | ✅ |
| `analyze.py` | 轴线交点/平行性检测、工作空间 MC 与体素 IoU、朴素关节复制误差、限位表 | ✅ |
| `ikstudy.py` | 阻尼最小二乘 IK 可行性、可操作度/条件数分布 | ✅ |
| `taskspace.py` + `RESULTS_taskspace.txt` | 任务盒内层③/层④、双臂对照 | ⚠️ **`-- best-fit per-joint affine` 那一行是误标，必须修正**（§0.1 #3） |
| `followup.py` + `RESULTS_followup.txt` | 方向不对称 + 协同松弛阶梯 | ⚠️ 需 equal-budget 重跑（§6.4） |
| `dual_study.py` + `dual_out.txt` | 锁关节 ladder | ⚠️ **锁定角硬编码为 0，必须按 §6.2 重做 sweep** |
| **`redteam.py`**（本次） | 三档标定 retarget + 容差敏感性 | ✅ 已跑，结果见 §3.4 证据 A / C |
| **`redteam2.py`**（本次） | 限位 vs 几何归因 + 逐关节触限直方图 | ✅ 已跑，结果见 §3.4 证据 B |
| **`equalbudget.py`**（本次新写） | 双臂 equal-budget 三 arm 对照（A 独立无 float / B 独立带 float / C 协同带 float），Wilson 区间 | ⏳ **已启动但 N=400 跑不完（单核 numpy，>25 min 无结果），被超时终止。降到 N≈150 或多进程重跑。G0 那周补** |
| **`lockedsweep.py`**（本次新写） | 锁关节角 sweep（5 点 × j4/j5/j6，6-DoF 与 5-DoF 双判据） | ⏳ **待跑，需先补一个通用的 position+approach-axis IK**（`taskspace.py` 里没有；`dual_study.py` 里那个把锁定值硬编码为 0） |

**建议**：把 `/tmp/agxurdf/` 整目录移到项目仓库（例如 `RAL2027/kinematics/`）并纳入版本管理——这些脚本产出的数字要进论文，放在 `/tmp` 下随时会没。

---

# 10. 立即待办（按依赖排序，前三条是本周）

1. **【G0，成本=一把尺】~~确认 PiperX 型号~~ ✅ 已确认为官方 `piper_x`**（偏置腕 UR 型）。**剩余**：读两台固件 DH 版本 `GetPiperFirmwareVersion()`。
2. **【本周，零成本，新增最高优先】实测两台夹爪的 TCP 偏置并重跑全部运动学脚本。** 用户已确认**两台夹爪不同款**（§1.7 后果 B），而 `redteam.py` / `taskspace.py` / `followup.py` 的每一个数（82.8° / 7.10 cm / 17.8° / 80.8% / 57.3%）都建在"同款夹爪、仅安装 rpy 差 90°"这个前提上。**在重跑之前，正文不得写任何可行率数字。** 顺带把"夹爪差异单独贡献几个百分点"报成 embodiment 阶梯上的一档（这一档现在是**免费且原生**的，比 3D 打印手指自然）。
3. **【本周，零成本】从已采集的门任务轨迹反推铰链轴。** 用户确认**尚未做铰链标定**（§1.7 后果 C）。门把手轨迹是圆弧，对末端位姿序列拟合共同螺旋轴即可。多条 episode 拟合出的轴一致（残差小）则**同时证明两件事**：家电在采集期间没移动过、且轴已经拿到——存量数据直接变成③层可用、零重采。若不一致则需按场次标定或退到在线估轴（3–4 周）。
4. **【G0，成本=1 天】按 §6.2 重做锁关节角 sweep**；跑完 `equalbudget.py` 与 `lockedsweep.py`。
5. **【本周，零成本，最高优先】在存量 Piper 真实轨迹上重算 per-task 层③可行率 φ**，替换掉全部基于均匀关节采样的数字。均匀采样的任务盒位姿分布与真实家居操作（集中在把手高度、桌面、包口这少数几处）完全不同；真实分布下 φ 可能是 99%（谱系当场压平）也可能是 40%。**这是全文最关键的一个数，获取成本是零机器人小时、零 GPU。** 同时报 (a) 全局 φ、(b) **per-task φ**（P3′ 的秩相关直接需要，也是 §6.10 第四段挑变体的依据）、(c) φ 沿 episode 时间轴的分布。**与第 2 条合并做——夹爪 TCP 修正后一次算完。**
6. **【G0.5，9-05】同本体交叉点 gate**——决定四层谱系框架生死，**也决定 §6.10 第二段能不能拍**。
7. **【半天】把 `pi0.py::sample_actions` 的 `jax.lax.while_loop` 展开为 Python 循环 + 同 seed 数值一致性检查**，排在所有记忆库工程之前。
8. **【半天】JAX 训练侧实测**：跑 `uv run scripts/train.py debug_pi05` 十步。用户已确认 5090 推理可跑，但 JAX 对新架构常常推理 kernel 先于训练 kernel 就绪。
9. **【★ 第一天就要做，否则事后补拍成本 ×10】架第三方电影机位 + rollout 元数据与视频帧同步落盘。** 见 §6.10.6 的三条录制纪律。**这条不做，§6.10 第三段（harm 案例）永远拍不出来**——它完全依赖能从日志里检索出 `base 成功 & ours 失败` 的成对样本。
10. **【现在启动，与一切并行】D12 弱配对采集**（用户确认可随机启动采集，不受存量语料重合度限制）。
11. **【9 月即可开工，不依赖策略与记忆库】8 个自动判据的夹具与传感**（3 周，在关键路径上）。
12. **【指定一人，3.5 周】PiperX 侧 openpi 移植**，第 1 周 FK 一致性硬验收（<5 mm / <2°）——**这是单点故障（R9），FK 残差 >5 mm 则 §3.4 全部证据作废**。
13. **【G2a 通过后立即】arXiv 占位 P1′/P2/P3′ 的预注册预测**（R-t-S 团队抢跑风险）。
14. **把 `/tmp/agxurdf/` 移进仓库并纳入版本管理**；修正 `RESULTS_taskspace.txt` 的误标。
15. **把 §2.5 的 cross-body admissibility framing 写成一段 pre-registration 放进补充材料**，G0.5 触发即启用。
16. `PORTMEM` / `XEM` 重名检索（v4 遗留待办；**arXiv 已查零命中，仍需查 ACM/DBLP**）。
17. `paper_src/` 模板：现为 ICRA 的 `ieeeconf`（**按用户指示保留**）。若最终投 RA-L 需换 `IEEEtran` 期刊格式，换完立刻用真实字数做排版对账。

