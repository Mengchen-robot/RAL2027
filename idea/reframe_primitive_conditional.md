# 研究问题重构提案：从「聚合迁移率」到「按 primitive / 阶段条件化」

> 状态：**接在 v5 之后的重构提案**，不替代 v5。v5 的硬件、任务、训练、预算、Go/No-Go 骨架全部保留。本文只改三样东西：**主张的形态**（点 → 函数）、**分析单位**（任务 → 阶段）、**被预注册的那个预测量**。
> 日期：2026-08-24。作者复算脚本：`RAL2027/covariates/admiss.py`（本轮新建）、`absorb2.py`、`design_stage.py`、`pow_stage*.py`；运动学事实来自 `/tmp/agxurdf/`。
> 标注约定：**【复算】** = 本轮亲自跑过并复现；**【继承】** = 来自前序对抗审查，本轮未独立复现；**【待确认】** = 未查证，不得写进论文。

---

# 0. 一句话判断

**有条件采纳。**

条件是：**必须先把被预注册的那个预测量换掉。** 重构的问题表述（「跨本体记忆对哪类 primitive、长时程任务的哪个阶段更有帮助」）是对的，分析单位从任务换成阶段是免费且必要的统计红利（29 个 confirmatory 阶段 vs 4 个族），但目前的实例化——`ζ = ‖diag(1/T_y)·J·chol(Σ_e)‖_F`——**不能预注册**：我本轮复算确认，ζ 在六个 archetype 上与最朴素的标量 `−log min(T_y)` 的 **Spearman = 1.000，log-log Pearson = 0.990**【复算】，而 `T_y` 是 `absorb2.py` 第 13–20 行手打的 26 个常数。整套 SPD/cholesky/SVD/有效秩机器对排序的贡献恰好为零。以它为主端点，能被确认的命题只有「容差比误差小就失败」，这句话 Mason 1981 与 Suomalainen 2022 已经写过，不值 RA-L 版面；而且假设列表（articulated 高 / place-insert 低）在脚本之前就存在，ζ 是从待检验假设反向工程出来的，fishing 指控成立且无法 rebuttal。

**但重构可以被救，而且救法是一个更强的量，不是一个更弱的措辞。** 本轮我算出了替代品：**逐阶段的可执行性差 `Δ𝔸(k) = A₃(k) − A₄(k)`**，其中 `A_ℓ(k) = P_frames[‖diag(1/T_y)·J_k·e_ℓ‖ < 1] · (1 − abstain_ℓ(k))`。它与朴素标量的 **Spearman = −0.26（≈0）**【复算】，因为它对容差**非单调**且**会变号**：容差 12 mm 时 Δ𝔸 = +0.543 达峰，容差 ≥60 mm 时 Δ𝔸 转负（−0.19），因为层③买精度的代价是 19.2% 的 IK 弃权而层④永远可用【复算，`admiss.py`】。这正是 SQ1′ 要的那个对象——`ℓ*(π)` 本身——而不是它的代理；它做的是一个**有符号翻转的方向预测**，是最可证伪的那类；它的输入（Σ_e、abstain 率）来自已实测的运动学而非手打。

因此：**采纳重构的问题与分析单位，否决 ζ 作为主端点预测量，改用 Δ𝔸；并把主张顺序反过来——harm 侧的 key/value 解耦升为主端点，「哪些 primitive 受益」降为支撑。** 不做这三件事就在 08-31 冻结 F-ζ，冻的将是一份「我把我的假设打成 26 个数并对它做了假设检验」的文件。

---

# 1. 新问题的表述

## 1.1 SQ1″（正式表述）

> **SQ1″：跨本体读取时，最优 value 抽象层级 `ℓ*` 是操作 primitive / 任务阶段的函数吗？这个函数的形状能否在不跑机器人的前提下，由已实测的 retarget 残差、已实测的 IK 弃权率、与外源测量的阶段容差算出？**

```
ℓ*(k) = argmax_ℓ  E[ 阶段 k 的推进量 | value 层级 ℓ, reader ≠ writer ]

主张 A（存在性 / 符号翻转）：ℓ*(·) 非常数，且存在阶段使 ℓ* = ④（层④优于层③）
主张 B（可预测性）：       ℓ*(k) 的符号由离线量 Δ𝔸(k) 的符号预测
主张 C（危害的解耦）：      HR(k) > 0 且随 Δ𝔸(k) 反向变化，而与检索置信度无关
```

三条主张的强弱与可证伪性依次递增。**主张 A 是最便宜的（离线就能算出候选），主张 C 是最贵也最非平凡的。**

## 1.2 为什么它比「聚合迁移率」更值得做

三条理由，前两条是统计的，第三条是科学的。

1. **旧问题的自由度被硬件吃光了。** 旧 SQ1 押的是「存在一个 ℓ*，使同本体曲线与跨本体曲线在此交叉」——一个点估计。v5 §7-R1 已诚实写出它的死法：6-DoF 无零空间臂上同本体 FK→IK 近乎无损，`SR_same(④) − SR_same(③) ≈ 0`，交叉点消失、框架当场死亡。而这恰好是本硬件上最可能为零的量（同本体 position-only IK 可行率实测 **100.0%**）。**用一个已知会压平的量去 gate 一个关于交互的主张，是设计错误。**

2. **分析单位换成阶段是零成本的 df 三倍化。** 一条配对 episode 同时产出该任务**每一个阶段**的一次观测，所以 `n_stage` 从 12 涨到 29 **不增加任何 robot-hours**。`design_stage.py` 的 confirmatory 阶段数【复算】：C=9、B=6、D=7、E=7，合计 **29**，另加布料族 A=8 作 exploratory，总 37。主效应的有效 n 是族数（4–5），交互的有效 n 是阶段数（29）。**这不是「交互更好测」——交互从来更难测——而是「在这个设计里，主效应的 df 被任务族吃光了，交互的 df 没有，而阶段是免费的」。** 这个反驳是条件性的，条件见 §4.3（族内方差门槛、prototype 随机效应），条件一旦破，反驳整体塌回主效应的困境。

3. **它把一个赌注换成一条曲线。** 聚合迁移率若压平，论文只剩「记忆不跨本体」这一句；条件化之后，即使聚合压平，只要 `ℓ*(·)` 非常数，论文的结论就是「层级选择必须逐阶段做，不能全局做」——这是一条系统集成者能直接执行的结论，且它的证据（Δ𝔸 曲线）在跑任何机器人之前就已离线备齐。

## 1.3 非平凡性论证（哪部分是废话，哪部分不是）

必须逐条分级，并把平凡的那半主动割掉。**割不掉的部分才是论文。**

| # | 候选结论 | 平凡性判定 | 依据 |
|---|---|---|---|
| N1 | 「容差比误差小的阶段迁移差」 | **平凡，必须主动弃权** | Mason 1981（自然/人为约束分解）、Bruyninckx & De Schutter 1996（task frame formalism）、Suomalainen et al. RAS 2022 逐字：「*by leveraging compliance a robot can perform a peg-in-hole task with clearance smaller than the robot's accuracy*」【继承，全文已取】。当前 ζ 在排序上**恰好等于这句话**【复算：Spearman=1.000】 |
| N2 | 「铰接约束吸收误差」 | **作为物理事实平凡；作为策略性质非平凡** | 物理侧是教科书（Suomalainen §2.3 逐字把日常铰接物定为 1-DoF 机构）。非平凡的重述是：**一个被注入到 chunked、位置型、可能刚性伺服的生成式策略里的外体先验，是否仍能被 1-DoF 约束吸收**。双向可能（吸收 vs 变内力→abort），且先验证据自相矛盾：RAM 的 Open +17.3 > Close +10.0 > Pickup +4.5 支持，RECAP 的 Open Microwave 仅 +2.5、VLA-Pro 的 close_microwave −26.7 反对【继承】。**判据：必须与「该阶段关节力矩 p95 / abort 阈值」比值同报，否则是复述不是发现** |
| N3 | 「吸收维高 ≠ 安全」（hinge 与 zip 吸收维同为 5.00 却分居 ζ 两端） | **非平凡，但当前证据是手打的** | 反差 45× 完全来自手打的 `8°` vs `3 mm`。**T_y 实测后若反差仍在，这是「ζ 优于现成 taxonomy 标签（d_free / articulated）」的唯一证据；若不在，必须删掉这条叙事而不是调参数保住它** |
| N4 | **`ℓ*` 变号：存在阶段使层④（朴素关节复制）优于层③（任务系 retarget）** | **非平凡，且是本轮新增** | 朴素直觉是「层③处处优于层④，因为它误差小 7 倍」。变号来自层③的**弃权**：`A₃` 封顶在 `1 − 0.192 = 0.808`，而 `A₄` 在宽容差阶段趋于 1.000。容差 ≥60 mm 时 Δ𝔸 转负【复算】。这句话用「误差大所以精密任务差」**推不出来** |
| N5 | **harm rate 在高危阶段显著 > 0，且由 ζ/Δ𝔸 预测而与检索置信度无关** | **最非平凡，应升为主端点** | 朴素先验是「R-t-S 的 confidence-adaptive gating 会在没把握时弃权，最坏是无增益」。若 harm > 0，证明的是 **key 侧相似度与 value 侧可执行性解耦**——外体条目在检索侧看起来完全可用，门控看不见它执行侧不可行。直接推出设计结论：**要 executability gate，不是 similarity gate**。三条独立留痕支持：R-t-S 自己 π0 上 4/10 任务 harm（论文只字未提）、FlowRetrieval 逐字的 pick 受益 / place 受害、VLA-Pro close_microwave −26.7【继承，全部一手 PDF 核实】 |

**结论：论文的 headline 必须是 N4 + N5，不是 N1。** 当前设计把 N1 放主端点、N5 放次端点，是主张结构的排序错误。§5 给出反过来的分配。

## 1.4 必须写进正文的三条措辞纪律

1. 不写「我们提出分层表示」——GR00T N1.7 的 relative-EEF、R-t-S 的多控制空间聚合已占位。写「**层级是唯一被操纵的变量，注入路径逐字固定**」。
2. 不写「我们做了条件化分解」——RoboMME Appendix C.3 已把这个方法论做成范式（见 §5.6）。写「**我们条件化的变量是 contact-geometry tolerance，且读者 ≠ 写者**」。
3. **不写「吸收维高 ⇒ 安全」**。hinge 与 zip 吸收维同为 5.00 而 ζ 差 45×【继承，`absorb2.py`】。用二值 articulated 标签会把两者放进同一桶然后被数据打脸。

---

# 2. primitive 分类法

## 2.1 采用哪套现成分类（不自创）

**三层复合标注 N / M / B，每一层都是已发表的、可引用的，不发明任何新类。**

| 层 | 内容 | 出处（全部已取得全文并核过原话）【继承】 | 作用 |
|---|---|---|---|
| **N（Naming）** | RoboCasa 8 foundational skills（刚体家居）+ Borràs et al. 6 cloth primitives (Ex/G/R/RG/S/GM)（可形变） | RoboCasa arXiv 2406.02523，`arxiv:comment` 逐字 "RSS 2024"；Borràs, Alenyà, Torras, IEEE T-RO 2020, DOI 10.1109/tro.2020.2986921 | face validity。族 C 的三个阶段与 RoboCasa atomic task **字面同名**（`OpenSingleDoor` 描述逐字 "Open a microwave door"；`PickPlaceCounterToMicrowave` 一字不改） |
| **M（Mechanism）** | Paulius Motion Taxonomy 的 (prismatic bit, revolute bit) 二值轨迹标签 + Suomalainen 三类（environment shaping / workpiece alignment / **articulated motions**）+ GAPartNet 9 部件类 | Paulius et al., IROS 2019, DOI 10.1109/iros40897.2019.8967754；Suomalainen, Karayiannidis, Kyrki, *RAS* 156 (2022) 104224, DOI 10.1016/j.robot.2022.104224（CC-BY）；GAPartNet, CVPR 2023, DOI 10.1109/cvpr52729.2023.00684 | **维度同构**：Paulius 的 trajectory type 恰是 2-bit（平动/转动），与我们残差的 2 个分量（7.10 cm / 17.8°）可做良定义外积。所有基于动词的体系在这一步就断了 |
| **B（Bimanual）** | Krebs & Asfour 7 类 | IEEE RA-L 2022-10, DOI 10.1109/lra.2022.3196158 | `tightly coupled symmetrical` 的定义逐字含 "there is a **fixed transformation between the hands**" = 我们的 `T_rel`。双臂轴不是我们发明的 |

**负面结论（可直接写进论文防御「你为什么不用 X」）**【继承，五套均本地下载并 grep 核查】：LIBERO 四 suite 是 distribution-shift 轴不是 primitive 轴；Open X-Embodiment 的「527 skills」是 PaLM 抽的动词频次（§III 逐字），无本体论无互斥类；RLBench 通篇无 skill 分类维度；Meta-World 的组织轴是训练协议；BEHAVIOR-1K 用 BDDL 谓词描述目标状态不描述运动学。**没有任何一套现成分类法带「跨本体可迁移性」维度**——这是空白，也是贡献点（但只做了针对性检索，不能断言不存在【待确认：Paulius RSS'20 / Krebs RA-L'22 / Suomalainen RAS'22 三篇的正向引文追踪未做】）。

**唯一需要自己下定义的格子是拉链**：GAPartNet 9 类无、RoboCasa 8 类无、Borràs 6 primitives 是纯布料的。建议定义为 "articulated motion along a curved 1-DoF path with a DLO substrate"，并在论文里显式声明理由。诚实声明比硬塞进 insertion 安全。

## 2.2 ★ 关键设计变更：分类法降级为叙事，confirmatory 路径去标签化

**离散 primitive 名是 analyst degree of freedom 的唯一栖息地。**【继承·已量化】：把「抽衣」从 pick 改标 transport(drag)，ζ 移动全表 log 动态范围的 **36.9%**；「勾把手」在 pick 与 hinge 之间摇摆，移动 **72.9%**。一个人改两个标签就能重排自变量。

而 `Δ𝔸` 只需要 `(J_k, T_y(k), abstain(k))` 三个**阶段物理量**，三者都可以不经过命名获得：`J_k` 由 writer 侧 demo 的跨演示回归估计（或实测几何），`T_y(k)` 由卡尺/CAD/E2 给出，`abstain(k)` 由 `taskspace.py` 逐阶段跑 IK 得到。

> **硬规则：confirmatory 主端点不得依赖任何 primitive 名。Layer N/M/B 只用于（a）论文叙事与图表分组、（b）robustness check、（c）G0.5″-c 的族内置换零分布。**

这一条单独就把 analyst-freedom 的变体数 K 从 16 砍到 ≤4，把 FPR 从 44.4% 拉回 ~16%【继承·模拟：K=1/4/16/64 → FPR 5.5/16.4/44.4/78.1%】。

## 2.3 三个任务族的逐阶段标注表

约定：`P/R` = Paulius prismatic/revolute bit；`d_free` = 未被环境约束的任务系 DoF 数（由 Layer M 标签读出，零自由参数）；`proto` = `design_stage.py` 的 archetype 归属；**「Δ𝔸 预测」= 本轮 `admiss.py` 的离线符号预测（层③ vs 层④ 谁赢）**。

### 族 C：微波炉门（开 → 放入 → 关），9 阶段，confirmatory

| # | 阶段 | Layer N | Layer M | P/R | d_free | B | proto | Δ𝔸 预测 |
|---|---|---|---|---|---|---|---|---|
| C1 | 接近并勾住把手 | RoboCasa `OpenSingleDoor`（前段） | contact 0→1；GAPart `Line/Round Fixed Handle` | 1/0 | 6 | uni | pick | **③**（7.10 cm 恰在把手尺度边缘，谱系判别力最高） |
| C2 | 拉开门（转动） | RoboCasa *opening/closing doors* | **articulated motions**；GAPart `Hinge Door` | 1/1 | 1 | uni | hinge | **符号取决于实测力臂 r**（见 §3.3；r≥0.8 m → ④；r≤0.35 m → ③） |
| C3 | 松手 | Borràs (R) | contact 1→0 | 1/0 | 6 | uni | transport | ③ |
| C4 | 从台面取物 | RoboCasa pick&place | contact=1, rigid/moving | 1/0 | 5 | uni | pick | ③ |
| C5 | 运输至腔口 | pick&place | contact=0（持物自由空间） | 1/0 | 6 | uni | transport | **③（Δ𝔸 = +0.539，全表最大）** |
| C6 | 送入腔体并放置 | RoboCasa `PickPlaceCounterToMicrowave`（字面同名） | 腔壁 = 碰撞约束非引导约束 | 1/0 | 4 | uni | place | ③，但两层皆低（地板） |
| C7 | 退出腔体 | — | contact=0 | 1/0 | 6 | uni | transport | ③ |
| C8 | 推门（转动段） | RoboCasa `CloseSingleDoor` | 同 C2 | 1/1 | 1 | uni | hinge | 同 C2 |
| C9 | 卡扣咬合 | `CloseSingleDoor` 末段 | **workpiece alignment**（detent，类 peg-in-hole） | 1/0 | 3 | uni | insert | **两层皆 ≈0（地板）；harm 高危** |

### 族 B：拉链收纳包（开 → 放入 → 合），6 阶段，confirmatory

| # | 阶段 | Layer N | Layer M | P/R | d_free | B | proto | Δ𝔸 预测 |
|---|---|---|---|---|---|---|---|---|
| B1 | 左手稳定包体 | Borràs (G)+(Ex) | rigid/stationary；**environment shaping** | 1/0 | 5 | **tightly asym** | transport | ③（宽容差） |
| B2 | 定位并抓拉头 | 无现成名，最近 *insertion*；Borràs (G) | rigid/moving，无环境约束辅助 | 1/0 | **6** | tightly asym | pick | ③；**7.10 cm ≫ 拉头尺寸 → harm 高危** |
| B3 | 拉动滑块（全行程） | ★ 无现成名 → 自定义 | Suomalainen **articulated motions**，continuous=1 | **1/1** | **1** | tightly asym | zip | **③（Δ𝔸=+0.264）；但 A₄ 仅 0.057，层④崩溃** |
| B4 | 放入物体（袋口） | RoboCasa *insertion* | soft/admitting-penetrative；袋口 = 软漏斗 | 1/0 | 4 | tightly asym | place | ③，两层皆低 |
| B5 | 重抓拉头 | Borràs (RG) | 同 B2 | 1/0 | 6 | tightly asym | pick | 同 B2，harm 高危 |
| B6 | 拉合拉链 | 同 B3 | 起始段需齿列对齐，更紧 | 1/1 | 1（起始段 ~3） | tightly asym | zip | 同 B3 |

### 族 A：抽衣 → 叠 → 入篮，8 阶段，**exploratory（不进 confirmatory）**

降级理由与 v5 §8.3 的 MVP 决策一致：布不是刚体，「任务系 DoF」对它不是良定义的，A2/A4 的 `d_free ≈ 4` 是量级判断不是精确计数；且关键点感知前端 4 周未开工。

| # | 阶段 | Layer N | Layer M | d_free | B | proto |
|---|---|---|---|---|---|---|
| A1 | 接近衣堆 | pick&place 前段 | contact=0 | 6 | uni | transport |
| A2 | 从堆中抽出一件 | Borràs **Task 6 Separate from pile**；(G) | soft/manipulatee-deforming；environment shaping | ~4 | uni/loosely | pick |
| A3 | 抖开/摊平 | Borràs **1(a) Unfold in the air** / **5 Flatten**；(GM)+(S) | soft-deforming，空中无环境约束 | 6 | **tightly sym** | transport |
| A4 | 第一折（双臂） | Borràs **Task 2 Fold on table**；**(GM)**（原文举例即 "applying tension between two PP grasps"） | 桌面 + 布张力双约束 | 4 | **tightly sym** | place |
| A5 | 第二折 | 同 A4 | 对象已半刚性化，容差更紧 | 4 | tightly sym | place |
| A6 | 拾起折好的衣物 | Borràs **Task 7**；pick&place | rigid/moving（已折叠 ≈ 刚体） | 5 | uni/tightly sym | pick |
| A7 | 运输到篮 | pick&place | contact=0 | 6 | uni | transport |
| A8 | 放入篮（松手） | pick&place | 篮口 = 软漏斗，弱化的 workpiece alignment | 4 | uni | place |

## 2.4 ★ 必须新增的两类阶段（否则关键对照不可识别）

**问题（本轮复算确认）**：`design_stage.py` 的族分配里，`hinge` 只出现在 {C, D, E}，`zip` 只出现在 {B}，两者的族集合**不相交**。在 family FE 下，「同为 1-DoF 约束、hinge 安全而 zip 危险」这个对照 100% 是 B vs {C,D,E} 的族间比较，有效 cluster 数 = 2。而这个对照是 Title T3′「The Crossover Is a Function, Not a Number」的全部内容。

**修法（纯离线设计变更，0 robot-hours，必须在 F3 阶段集冻结前完成）**：

- **给刚体家电族补 zip 型阶段**：微波炉/柜门的滑动闩、抽屉族（D）的滑轨长行程拖动，都是「沿曲线 1-DoF 路径 + 窄剩余容差」。
- **给 B 族补 hinge 型阶段**：收纳包的翻盖/硬质盖板开合。
- 目标：hinge 与 zip 各自至少出现在 **2 个共同族**里。做完后必须重跑 D-optimal 与族内方差占比门槛。

**以及 matched-pair fixture（见 §4.6），这是把 Δ𝔸/ζ 与朴素预测量分开的唯一手段。**

---

# 3. 协变量与测量协议

## 3.1 先把 ζ 的问题摆平

### 3.1.1 三条本轮复算的硬事实

```
$ python3 covariates/absorb2.py  (+ 本轮追加的相关性计算)
archetype              zeta    -log min(T_y)
hinge door (theta)     0.29        1.97
transport              1.55        3.22
pick (axis-aligned)    8.67        4.83
place (6-DoF)         12.22        5.12
zip (arclength s)     13.66        5.81
insert (roll free)    31.12        6.21
Spearman(zeta, -log min Ty) = 1.000   (p = 0.0)
Pearson(log zeta, -log min Ty) = 0.990
```
【复算】

1. **ζ 的排序 ≡ 最紧容差的负对数。** SPD 张量、cholesky、SVD、有效秩、Frobenius 范数对排序贡献为零。Contribution 1 的英文 "introduces no fitted constant / no free parameters" **字面成立、实质为假**——没有 fitted，但有 **26 个 asserted constants**，而 asserted 比 fitted 更糟（fitted 至少有数据约束）。

2. **所谓「坐标图重标定不变性」是代数恒等式。** `J S⁻¹ · (S Σ Sᵀ)^{1/2}` 里 S 直接约掉，对任意胡说八道的 J 和 T_y 都成立【继承·已用随机 J/T_y 验证】。写进论文只会给审稿人「作者不理解自己的不变性检查」的把柄。**删掉。**

3. **ρ 没被消掉，它被重新打字成了 T_y 里 rad↔m 的兑换率，外加一个未声明的力臂。** `absorb2.py` 的 hinge 用 `gain = 1.0` 把一个平移分量当角度读；`θ ≈ d⊥/r` 意味着 `gain = 1/r`，`gain = 1.0` 即 **r = 1.0 m**。本轮复算：

| 力臂 r (m) | 1.0 | 0.8 | 0.35 | 0.2 | 0.12 |
|---|---|---|---|---|---|
| ζ_hinge | 0.294 | 0.367 | **0.839** | **1.468** | 2.447 |

真实微波炉把手到铰链 ≈ 0.35 m【待确认：必须卷尺实测每台家电】→ ζ_hinge 从 0.29 涨到 0.84；r = 0.2 m → 1.47，**已高于 transport 的 1.55 附近并可能翻转排序**。**全篇最非平凡的宣传语（"articulated 意外地安全"）的安全边际，由一个既没测量也没写出来的几何常数决定，且偏乐观约 3×。**【复算】

### 3.1.2 处置：ζ 降级，不删除

- **ζ 保留为描述性量**，用于论文正文说明「同一个 7.1 cm / 17.8° 残差投影到不同阶段跨两个数量级」。**这是一个离线计算结果，不是一个本实验能确认的结论，措辞必须区分**（Abstract 里 "spans two orders of magnitude" 必须写成 offline computation 而非 finding）。
- **ζ 不作主端点预测量。**
- 若仍要报 ζ 的回归，必须是预注册的头对头嵌套比较：`ΔCP ~ trivial + (ζ − proj_trivial ζ)`，只有正交残差项显著才可声称贡献；并诚实报告功效代价【继承】：corr(ζ, trivial) = 0.95 时残差项 MDE 膨胀 3.2×，0.99 时膨胀 7.1×。当前 corr = 0.99 ⇒ **不可行**。

## 3.2 ★ 替代预测量：可执行性差 Δ𝔸

### 3.2.1 定义

```
A_ℓ(k) = P_frames[ ‖ diag(1/T_y(k)) · J_k · e_ℓ ‖ < 1 ] · ( 1 − abstain_ℓ(k) )
Δ𝔸(k) = A₃(k) − A₄(k)

e_ℓ  ~ 该层 retarget 残差（层④：最优 42 参数固定标定的经验残差；层③：clipped-IK 残差）
abstain₄ = 0            （朴素关节复制永不弃权）
abstain₃(k) = 该阶段 IK 不可行帧比例   （taskspace.py 逐阶段跑，不得用全局 19.2%）
```

预测：`ℓ*(k) = ③ if Δ𝔸(k) > 0 else ④`。

### 3.2.2 为什么它不是 ζ 的改名（本轮复算）

```
$ python3 covariates/admiss.py
archetype                  A4     A3  dA=A3-A4  ell*  -logminTy
hinge door r=1.0        0.999  0.808    -0.191   (4)       1.97
hinge door r=.35        0.771  0.808    +0.037   (3)       1.97
transport               0.269  0.808    +0.539   (3)       3.22
pick (axis-aligned)     0.000  0.222    +0.222   (3)       4.83
place (6-DoF)           0.000  0.069    +0.069   (3)       5.12
zip (arclength)         0.057  0.322    +0.264   (3)       5.81
insert (roll free)      0.000  0.003    +0.003   (3)       6.21

Spearman(dA, trivial -log min Ty) = -0.257     <- 与朴素标量近乎正交

tolerance sweep, pure-position stage:
  tol(mm)     A4     A3     dA
       1   0.020  0.109  +0.089
       5   0.095  0.496  +0.400
      12   0.233  0.776  +0.543   <- 峰
      35   0.607  0.808  +0.201
      60   0.859  0.808  -0.051   <- 变号
     200   1.000  0.808  -0.192
```
【复算】

四条性质，每条都是 ζ 没有的：

1. **与朴素预测量近乎正交**（Spearman = −0.26 vs ζ 的 1.000）。fishing 指控的技术核心被结构性解除。
2. **对容差非单调（倒 U）**：极宽和极紧两端 Δ𝔸 都小，中间带最大。「紧的差」这句话**推不出倒 U**。
3. **会变号**：容差 ≥60 mm 时层④反超。这是一条方向被预先钉死、可被单次实验证伪的预测。
4. **驱动变号的量是实测的**：`abstain₃` 来自 IK 可行率（层③全位姿 80.8%），不是手打。

### 3.2.3 诚实的四条限制

| # | 限制 | 处置 |
|---|---|---|
| L1 | `Δ𝔸` 仍需要 `T_y` 的**绝对值**（阈值 1），只是不再是它的单调函数。所以 §3.3 的 T_y 外源化仍是硬前置 | 无法回避。T_y 拿不到的阶段排除出 confirmatory |
| L2 | 我用了**各向同性** Σ_e 与**全局** abstain 率作占位。真实 Σ_e 是 6×6 非各向同性经验协方差，abstain 应逐阶段 | 冻结 F 之前必须换成 `redteam.py` 的经验协方差 + `taskspace.py` 的逐阶段弃权率 |
| L3 | `insert` / `place` 两层皆 ≈0（地板）⇒ 它们对**层级对照**端点零信息 | 预注册：层级对照端点只用 `A₄ ∈ [0.05, 0.95]` 或 `A₃ ∈ [0.05, 0.95]` 的阶段；被排除的阶段数与其 T_y 分布必须报出。**但它们对 harm 端点仍有信息，不排除** |
| L4 | `A_ℓ` 是 SR 的**运动学代理**，不是 SR | 由 G2a（门+拉链各 50 episode 跨本体开环重放，v5 已排 09-26，本来就要做）在阶段级校准：报 `A_ℓ(k)` 与实测阶段完成率的秩相关。<0.5 则全部结论降级为「关于可执行性的陈述」 |

## 3.3 T_y 的外源化（最高优先级，阻塞一切）

> **硬规则：T_y 禁止手打。**

三条路径，按优先级：

1. **物理测量**，写进独立的 `covariates/Ty_measured.csv` 并单独出 sha256：卡尺/CAD 量拉头槽宽、门闩 detent 深度、篮口内径与倒角半锥角、腔壁余隙；**以及每一个 `J_k` 的非零增益所需的实测几何**：铰链轴到把手的力臂 `r`（每台家电一个数）、拉链导轨局部曲率半径、篮口漏斗半锥角。全部是分钟级测量。
2. **E2 反解**（pilot rollout 的逐阶段 logistic 边界）：`h_j^{E2} = sqrt(w₀ / (−w_j)) · h_j^{E1}`，标准化输入 + label smoothing ε=0.02，n=400 达 3% 误差，对 15–30% 标签噪声鲁棒【继承，`tol3.py`】。**必须标准化**（不标准化实测错 275 倍）、**必须 label smoothing**（否则 perfect separation → IRLS 发散成 NaN）。
3. **两者都拿不到的阶段 → 排除出 confirmatory，不许估。**

**盲引出交叉验证（必做，成本约 2 小时人情）**：找 ≥5 位不知道本文假设的机器人研究者，各自只看该阶段的一段视频 + 一句物理描述，独立给出 `log T_y`，报 **ICC(2,k)**。**ICC < 0.6 ⇒ T_y 不是客观量 ⇒ 全部依赖它的主张降为 exploratory。**

**预注册撤回条款（写进 F 文件）**：若实测 `r` 使 `Δ𝔸(hinge) > 0`（即 ℓ* = ③ 而非 ④），则「articulated 阶段层④已足够」一条**自动撤回，且不得改写为其他方向**。本轮已给出撤回边界：**r ≈ 0.5 m 附近变号**（r=0.8 → −0.185；r=0.35 → +0.041）【复算】。

## 3.4 SO(3) 方差的正确算法（用于 E1 与 J 的估计）

**不能只报一个数，必须报切空间协方差的三个特征值；并且必须先对夹爪对称群取商。**【继承，`so3.py`，n=200/case】

```python
# 1. 对称群商化的 Karcher/Fréchet 均值（parallel-jaw: Sym = {I, Rz(π)}）
M ← R_0
repeat:
    R_i ← argmin_{S∈Sym} ‖Log(Mᵀ R_i S)‖      # 每个样本对齐到最近的对称副本
    M ← M · Exp((1/N) Σ_i Log(Mᵀ R_i))
until 收敛
# 2. 切空间坐标与协方差
ξ_i = Log(Mᵀ R_i)^∨ ∈ R³                       # rad
Σ   = (1/N) Σ ξ_i ξ_iᵀ                          # rad²  ← 这才是「姿态方差」
λ₁≥λ₂≥λ₃ = eig(Σ);  σ_j = √λ_j
# 3. 姿态临界度用【受限方向】，不是总量
PoseCrit = −log σ_min
σ²_Fréchet = tr(Σ)                              # 仅作诊断量，不作协变量
```

**两条不做就静默失败的事实**：

| 情形（真值） | Fréchet sd | **切空间特征 sd** | Euler sd |
|---|---|---|---|
| 各向同性 5° | 8.62° | [5.2, 5.0, 4.7]° | [5.1, 5.0, 4.9]° |
| **pick：roll 自由 (3,3,40)°** | **38.56°** | **[38.4, 3.0, 2.6]°** | [2.7, 2.8, 38.4]° |
| 各向同性 60° | 105.11° | [66.4, 60.5, 54.6]° | [78.9, 37.6, 81.2]°（轴序乱，不可用） |

- Fréchet 方差是**迹**不是每方向 sd（各向同性 5° 给 8.62 ≈ √3×5），当「姿态方差」报会系统偏大 √3 倍。
- **pick 行是致命的**：Fréchet 给 38.56° 会把 pick 判成「姿态不临界」，真相是 3 个方向里 2 个卡在 3°。
- **夹爪对称群商化**（真值 3° 散布、一半样本翻转 180°）：**不取商 Fréchet sd = 90.1°** 并产生虚假的 89.9° 主方向；**取商 = 5.3°**，特征 sd [3.2, 3.1, 2.8]°。**不取商则每个含抓取的阶段都被算成「姿态高度不临界」，per-primitive 分解被抹平——而抹平正是本文最怕的结果。这一行代码决定论文成败。**
- 便宜近似：Moakher (2002, DOI 10.1137/S0895479801383877) 的 projected mean `R̄ = UVᵀ` 与 Karcher mean 实测差：5° 档 **0.002°**、40° 档 0.355°、60° 档 9.485°。紧阶段可直接用闭式；**但对称群商化仍须迭代**。理论依据 Pennec, JMIV 2006, DOI 10.1007/s10851-006-6228-4。

## 3.5 成功域宽度的估计量分工

| 估计量 | 内容 | 用途 | 依据 |
|---|---|---|---|
| **E1** 演示自然散布 | `h_j = std_i(δ_{i,j}^⊥)`（阶段 k、进度百分位 φ、**投影掉切向**后） | **只用于形状/配分**，绝不用于绝对尺度 | 下界性质是构造性的。正式先例：Ureche, Umezawa, Nakamura, Billard, IEEE T-RO 2015-12, DOI 10.1109/tro.2015.2495003 |
| **E2** rollout logistic 反解 | 见 §3.3 路径 2 | **尺度（T_y）的唯一可用估计** | `tol3.py`【继承】 |
| **E3** 真机扰动 | 3 阶段 × 20 trial ≈ 1.5 robot-h，按预注册偏移网格 | **只做校准，不做测量**。E2 与 E3 的 log-半宽差 > 0.7 nats ⇒ 尺度降级为 rank-only | — |

**E1 的实测性质**【继承，`tol4.py`，60 阶段 × 40 演示】：绝对值系统性低估 **3–4 倍**（实测 h/E1 = 2.87–4.05），`×√6` 修正后仍低 ~1.6 倍；但形状恢复的 Spearman ρ：谨慎∝容差 0.98 / κ sd=0.6 nats 0.91 / **谨慎与容差统计独立（最坏）仍 0.68**——因为「成功」这个条件本身就把偏差分布截断到成功域内，**截断的形状就是 h 的形状**。这是 E1 最强的辩护，且是实测出来的。样本量宽容：n_demo = 10 已给 ρ=0.95。

**★ 一条前序审查未写、必须补的：E1 的偏倚方向沿 Δ𝔸 系统变化（differential measurement error）。** 在受约束阶段（hinge、zip 行程段），被吸收方向上的演示离散度测的是**物体的约束**不是操作员的成功域，E1 在那里几乎等于真值（bound 很紧）；在自由空间阶段（transport），E1 测的是操作员习惯，对很宽的成功域是极松的下界。于是测量误差与预测量同向，**不保证保守**。
处置：(a) 逐阶段报「6 个方向里有几个落在遥操噪声地板 `f_j` 以内」，这些方向按 **Tobit censored** 处理而不是当作真实的窄容差；(b) 预注册：**一个方向只有在失败 rollout 中存在该方向的实际偏移证据时，才允许被判为 constrained**，否则该阶段标为不可估、进 exploratory。

## 3.6 ζ / Δ𝔸 是 plug-in 估计量，必须做 errors-in-variables 校正

`Δ𝔸_k` 由 `J_k`、`T_y(k)`、`Σ_e`、`abstain(k)` 四个估计量合成，每个都有抽样误差，且误差大小逐阶段不同（演示条数不同、E1 被 censor 的方向数不同）。经典 EIV 把 β 衰减 λ 倍，异方差测量误差还让衰减本身与预测量相关。

**处置（预注册）**：对演示做 bootstrap 得到每阶段 `SE(Δ𝔸_k)`，报可靠度 `λ = Var(z)/(Var(z) + mean Var(err))`；主分析用 regression calibration 或 SIMEX 校正；最低限度声明「β 被衰减 λ 倍，报告值是下界」。**λ 很低时连续预测量的增量检验更不可能通过，应提前知道。**

## 3.7 共线诊断与去相关

**三个协变量不是三个独立量，而是同一个「阶段成功域张量」`H ∈ SPD(6)` 的三个泛函**：姿态临界度 = H 的旋转/平移**配分**；精度需求 = H 的**尺度**（log-det）；约束吸收 = H 的**形状**（各向异性 / J 的零空间维数）。共线性是结构性的，不是统计意外。

【继承，`tol2.py`，60 阶段，共享 tightness 潜变量】：

| 共享方差 | 朴素参数化 VIF | max\|r\| | 尺度/形状/配分 VIF | max\|r\| |
|---|---|---|---|---|
| 0% | [2.8, 2.8, 1.0] | 0.80 | [1.0, 1.0, 1.0] | 0.14 |
| 50% | [3.3, 3.4, 1.0] | 0.83 | [1.0, 1.0, 1.0] | 0.15 |
| **90%（现实坏情形）** | **[19.8, 18.6, 1.4]** | **0.97** | **[1.4, 1.0, 1.4]** | 0.52 |

**结论：用户初稿的朴素写法在「紧阶段处处都紧」这个完全现实的情形下 VIF ≈ 20，回归无意义；换成尺度/形状/配分参数化后 VIF ≤ 1.4。这是设计解，不是统计补丁。**

**预注册的诊断与处置阶梯（看结果前定死）**：
```
D1  报 Spearman 相关矩阵 + VIF + 缩放设计阵条件数 κ
D2  max VIF ≤ 5  且 κ ≤ 30  → 同时入模（主分析）
D3  5 < max VIF ≤ 10        → 预注册顺序的 Gram–Schmidt 残差化，
                               顺序固定 尺度 → 形状 → 配分
D4  max VIF > 10            → 放弃多元回归，只报单一预注册标量 Δ𝔸 的单变量回归
                               + 三协变量各自的边际斜率（不做联合归因）
```

**更强的解是设计端去相关**：协变量在看到任何 outcome 之前就能全部算出，所以冻结阶段集时从候选池按协变量分布选阶段、最大化标准化设计阵的 `det(RᵀR)`（D-optimal），并强制**每个协变量族内方差占比 ≥ 0.5**。这是一次纯离线、outcome-blind 的选择，完全可预注册。**注意：D-optimal 必须做在「Δ𝔸 对朴素预测量回归后的残差」上，否则只会挑出容差跨度大的阶段，把同秩问题放大。**

## 3.8 基座每阶段不确定性 u

| 方法 | 出处 | 校准（LIBERO，与 per-task SR 的 −Spearman） | 成本 |
|---|---|---|---|
| **VFD**（velocity-field disagreement，主用） | arXiv 2606.18043（2026-06-16，本地 PDF） | **0.71 ± 0.03** | M=2 即可（原文明示），每具本体多训一个 LoRA seed |
| GU | 同上 | 0.62 ± 0.00 | — |
| **Action-L2（= 多次采样成对 L2，即最直觉的做法）** | 同上 | **0.50 ± 0.13** | 最便宜 |
| Entropy / Perplexity | 同上 | 0.10 / −0.04 | 不可用 |
| **DVAC 去噪方差**（次选，单次推理、**在 π0.5 上验证**） | arXiv 2606.03847（2026-06-02） | π0.5 上 LIBERO 94.75→98.00、replanning −43.0% | 零 ensemble |

DVAC 的核心实证与我们要的因子**完全同构**（逐字）：「*clean-action estimates remain stable during predictable motion phases, but fluctuate more strongly around contact-rich or precision-sensitive operations*」；「*operating phases consistently exhibit higher average denoising variance than moving phases*」。

**三个必须处理的坑**：

1. **量纲混淆（前序审查已指出，是最基础的一个）**：DVAC 的 `V_s(k)` 是归一化动作单位下对逐维求和的**绝对**方差。若相对抖动率恒定为 c，则 `V ≈ c²‖a‖²`，chunk 位移相差 10 倍就带来 100 倍的 V。而 transport 阶段位移最大、Δ𝔸 最高；精细阶段位移最小。**纯量纲分析就会造出 corr(u, 预测量) 的伪相关。** 处置：用无量纲 `CV² = log V − 2 log‖Δa‖`，或把 chunk 按弧长归一后再算方差；**预注册证伪检查 `Spearman(u_raw, ‖Δa‖)`，> 0.6 则 u_raw 不得进模型**。
2. **u 与精度需求天然共线**（DVAC 自陈）。处置：把 u 对 (C1,C2,C3) 回归，**只用残差 `u⊥` 进主模型**；同时报 `R²(u ~ C)`——它本身就是有价值的发现（「基座的犹豫在多大程度上就是任务的精度需求」）。**预注册 `R²(u ~ C) < 0.5` 作为 γ 进入 confirmatory 的门槛**，否则 P6 直接降 exploratory 并在 F 文件里写死（避免「残差化之后 γ 不显著」被事后解释成「共线太强」）。
3. **VFD 报的 0.71 是跨 task 的校准，不是同一任务内跨 stage 的校准，两者不能互推。** γ 要成立，必须先用 split-half 在本项目 base rollout 上做一次 per-stage 校准（u 对 base CP_k 的族内秩相关）——这是 G2a 那批数据就能顺带做的。
4. **禁止用 base SR 当 u 的代理**：主 outcome 是 `Δ = SR_ours − SR_base`，解释变量含 `SR_base` 会因共享噪声制造虚假负相关（回归到均值）。必须 split-half：A 半估 `SR_base` 作解释变量、B 半算 Δ。

---

# 4. 实验设计

## 4.1 cell 定义

**分析单位 = 阶段（stage），聚类单位 = 族（family），操纵变量 = value 层级。**

| 维度 | 取值 | 说明 |
|---|---|---|
| 族（confirmatory） | C 微波炉 / B 拉链包 / D 抽屉 / E 柜门 | 4 族，29 阶段【复算：9+6+7+7】 |
| 族（exploratory） | A 叠衣 | 8 阶段，不进 confirmatory |
| arm | `base`（无记忆）/ `ours@③` / `ours@④` | **三个 arm，正是 v5 §4.3 已预算的三行** |
| 方向 | Piper→PiperX / PiperX→Piper | 配对 |
| 配对试验数 | npair = 20 每（族 × arm × 方向） | — |
| 层① | 4 任务子集，**exploratory** | 层②同 |

**★ 关键预算事实**：层级在 **episode 级**变化（一条 rollout 全程用同一层），而每条 rollout **免费产出它所有阶段的读数**。因此 per-stage 分辨率是白送的，`n_stage` 从 12 涨到 29 不增加任何 robot-hours。这是本重构相对 v5 主线最大的成本优势。

**代价必须写明**：confirmatory 只跑 ③ 与 ④ 两层，`ℓ*(k)` 由 2 层对比的符号推断，「谱系」在正文里从 4 点降为 **2 点 + 1 个 exploratory 点**。这个降级是本设计的前提，必须在 §III 显式声明。

## 4.2 统计模型（替换施工图 §4.2 与 v5 §6.8 修法 1）

### 4.2.1 主端点（co-primary 两条，gatekeeping 顺序见 §4.5）

```
E1（层级变号，对应主张 A/B）
  模型  sign( ĈP_k^{@③} − ĈP_k^{@④} )  vs  sign( Δ𝔸(k) )
  检验  族内 randomization inference：把 primitive 标签在族内置换 ≥10000 次，
        统计量 = 符号一致的阶段数
  H0    符号一致率 = 随机
  样本  只用 A₄ 或 A₃ ∈ [0.05, 0.95] 的阶段（见 §3.2.3-L3），被排除阶段必须列出

E2（危害的 key/value 解耦，对应主张 C）  ★ 本设计的 headline
  模型  logit HR_k  =  β_h · Δ𝔸̃_k  +  δ · conf_k  +  族固定效应  +  ε_k
  预测  β_h 显著（危害集中在层级不可执行的阶段）
        δ  不显著（检索置信度看不见执行侧不可行 ⇒ 解耦）
  HR_k  必须来自 stage-targeted injection 臂（见 §4.4），不得用主 rollout 的条件化定义
  H0    β_h = 0，单侧（危害随不可执行性增）
```

### 4.2.2 次端点

```
S1  ΔCP_k = P(完成阶段 k | ours) − P(完成阶段 k | base)，分母 = 全部 episode
    模型  logit(ĈP_k^{ours}) − logit(ĈP_k^{base}) ~ Δ𝔸̃_k + baseCP_k^{(A半)} + u⊥_k + 族FE
S2  P3′ 方向不对称：族内 Spearman（离线 φ 预测排序），n ≈ 29 而非 12
S3  P2′ 归因桶：per-stage oracle 阶梯（五级四差 + Δ_limit/Δ_geom 拆分 + A8 coordination-oracle 第四桶）
S4  P4′ 共享池污染：三条件 × Δ𝔸 三分位
S5  ζ 的头对头嵌套比较（§3.1.2）——**预期不可行，报出即可**
```

### 4.2.3 三条 outcome 尺度的硬规则

1. **阶段成功率不得以「到达该阶段」为分母。** 那是 post-treatment / collider conditioning：base 与 ours 到达 k 的比例不同 ⇒ 两组在 k 处不是同一总体 ⇒ 阶段级 Δ 有偏且偏向不可知。主端点用**非条件化累积推进量** `CP_k`，分母是**全部** episode，更早失败即计未完成 k。R-t-S 的「平均完成段数 1.54 → 1.94」是同型读数的现成先例。
2. **★ 但非条件化 CP 有一个前序设计未写的代价：地板压缩与假设同向。** `ΔCP_k` 的上界是 `CP_{k−1}`（base 臂）。高危阶段按定义更深、base CP 更低、两臂都贴地板、`ΔCP_k` 被压向 0——**于是「增益随不可执行性递减」可以在完全没有任何 memory 效应的情况下出现**。这不是天花板/地板效应（M2 是族级 base SR 太高/太低，用 headroom 设计处理），而是同一族内部深浅阶段之间 CP 的单调递减，headroom 不消除它。
   处置三条（全部 0 robot-hours）：(a) 主模型加入 **base CP_k 协变量，且必须来自 split-half 的 A 半**；(b) **主端点在 logit 或 arcsine 尺度上估 β**（报 odds ratio 而非 pp 差），pp 差版作 robustness；(c) 预注册限制样本敏感性分析：只用 `base CP ∈ [0.25, 0.75]` 的阶段重估，报被排除阶段数与其 Δ𝔸 分布。
3. **per-stage 读数必须连续（ordinal 进度阶梯），不得二值。**【继承，`pow2.py`】MDE 6.0 → 3.4 pp/SD。v5 §6.8 修法 4(3) 已要求为 D/Z 族预注册 ordinal 阶梯，这里给它第二个独立理由。

## 4.3 n_eff 的诚实估计（这一节是本设计最脆弱的地方）

### 4.3.1 族级 wild cluster bootstrap 在 G=4 下数学上不可用

Rademacher 权重下 G 个 cluster 只有 `2^G` 种符号模式，p 值离散化下界 `1/2^G`：**G=4 ⇒ 最小可达 p = 0.0625 > 0.05，预注册的主检验在数学上不可能拒绝原假设。** G=5 ⇒ 0.031（v5 §7-R8 那个「p ≈ 0.031 勉强显著」正是这个下界，说明团队算过一次但没把它应用到新主端点）。Webb 六点权重能缓解离散化，但 G=4 远低于文献推荐下限，restricted wild bootstrap 在 G<12 时覆盖率不可靠。

**同时存在一处内部不一致**：设计文档 §1.4 写「族级 cluster wild bootstrap」，而 `pow_stage.py` 实际用的是 `t(n−k)`。现在宣称的 MDE 4.84 pp/SD 是按后者算的；若真按前者做推断，**power 恒为 0**。

**处置（三选一，写死，并废除任何族级 bootstrap 的措辞）**：
- **(b) 推荐为主：randomization inference。** 把 primitive 标签在**族内**置换（G0.5″-c 本来就要做这件事），置换分布的支撑远大于 32，且与 outcome-blind 冻结天然兼容。
- (a) robustness：放弃族级聚类，承认识别来自 within-family stage 变异，用 family FE + stage 层 HC3 / **episode-block bootstrap**。此时 `pow_stage.py` 的 MDE 才是有效的。
- (c) 把 confirmatory 族从 4 抬到 ≥6（成本高，不推荐）。

### 4.3.2 ★ prototype 随机效应吃掉大半个 n_eff

**问题（本轮复算确认）**：`design_stage.py` 是按 prototype **查表**赋值的，29 个阶段上预测量只取 **6 个值**。因此「family FE + 预测量」在数学上是「family FE + prototype FE」的 **1-df 限制**：预测量完全落在 prototype dummy 的 span 里，5 个 prototype 自由度只用了 1 个，**剩下 4 个被当成 iid 的 stage 噪声**。只要 hinge 的 6 个阶段共享任何一个不被预测量解释的公共偏移（同一种物理，几乎必然），SE(β) 就被系统性低估。

本轮复算（family FE 残差化后，sd_stage=6 pp、sd_trial=6.1 pp、4000 次仿真）：

| τ_p (prototype 随机截距 sd) | SE(β) | MDE (2.8·SE) | **n_eff** |
|---|---|---|---|
| 0 | 1.74 | 4.86 | **24.3** |
| 2 | 1.96 | 5.48 | 19.1 |
| 4 | 2.49 | 6.98 | 11.8 |
| **6** | **3.21** | **8.98** | **7.1** |
| 8 | 3.99 | 11.16 | 4.6 |

【复算。前序审查用略不同的噪声参数化得到 τ_p=6 → n_eff 8.0，结论一致】

**这直接击穿 §1.2 的第 2 条反驳。** 「主效应 n_eff ≈ 4–5 vs 交互 n = 29」里的 29 就是 τ_p = 0 的假设值。τ_p = 6 pp 一点也不极端（stage 残差本身就假设 6 pp），此时交互的 n_eff = 7.1，与主效应的 4–5 只差 60%，整个反驳论证塌掉。

**处置（三条，全部必做）**：
1. **根因修法：`Δ𝔸(k)` 必须由该阶段自己的 `J_k`、`T_y(k)`、`abstain(k)` 逐阶段算出，不得按 prototype 查表。** 这本来就是 `admiss.py` / `absorb2.py` 的接口，`design_stage.py` 的查表只是占位。【继承·实测】只要 within-prototype 的 log 预测量标准差达到 0.6 nats（between 是 1.50 nats），`1/c` 从 4.5 回到 7.2。
2. 主模型改成 **family FE + prototype random intercept + 预测量**，并把 `τ̂_p` 作为**必报的方差分量**。
3. **预注册的 MDE 表必须按 τ_p ∈ {0, 3, 6} 三档给，宣称的 MDE 用 τ_p = 6 那档，不得用 τ_p = 0。**

### 4.3.3 连续预测量与一个二值标签几乎无法区分

本轮复算（29 个 confirmatory 阶段，family FE 残差化后）：

```
corr(log ζ, 1[hinge ∨ transport] | family FE) = −0.903   →   R² = 0.816
1/c_z  (family FE only)          = 24.62
1/c_z  (family FE + 该二值)      =  4.53
MDE 膨胀倍数                      =  2.33×    (4.84 → 11.28 pp/SD)
```
【复算】

即：高端的 pick 8.7 / place 12.2 / zip 13.7 / insert 31.1 这 3.6 倍跨度对识别**几乎零贡献**。Contribution C1 主张的是「一个跨两个数量级的定量预测量」，而本设计只有能力检验「接触临界 vs 非接触临界」这个二值。更尖锐的是 §1.4 措辞纪律第 3 条自己写了「不许用二值 articulated 标签」——**但统计上你只有能力检验那个二值。**

**处置**：
1. 把定量主张的真正检验预注册为 **nested model comparison**：`M0 = family FE + 二值低/高组`；`M1 = M0 + 连续预测量残差`。报增量 F 检验**与它的 MDE（当前 9.6–11.3 pp/SD，必须诚实写出）**。
2. 执行 §4.3.2 的逐阶段计算；若 within-prototype sd 达不到 0.6 nats，**把定量主张降级为预注册的 3 组 ordinal 主张（low/mid/high）**，并相应改写 Abstract。
3. **Δ𝔸 在这一点上比 ζ 好但不免疫**：它与二值的相关性尚未复算（阻塞在逐阶段 `J_k` 上）。**F 冻结前必须补算 `corr(Δ𝔸, 1[hinge∨transport] | family FE)`，并把它写进预注册文件。**【待补算】

### 4.3.4 「预测量能排对 primitive 顺序」这个说法的 n 是 6，不是 29

本轮复算精确置换零分布：6 个 prototype 的**单侧 5% 临界 Spearman ρ = 0.771**，最小可达 `p = 1/720 = 0.00139`（且只有顺序完全正确时取到）。**这意味着排序主张要么几乎完全命中、要么不显著，没有中间地带。** 这对论文其实有利（干净、预注册、二值化的赌注），但 **0.771 这个数必须在预注册里写出来，不能事后挑检验。**

### 4.3.5 两条本轮复算后**站在设计这边**的检查（建议主动写进论文防御）

1. **stage depth 混淆不存在**【继承·复核口径一致】：族内 `Pearson(log ζ, 相对阶段位置) = 0.013`，`Spearman = 0.020 (p = 0.92)`；把相对深度加进模型后 `1/c_z` 从 24.62 到 24.62、VIF = 1.00。审稿人一定会问「高危阶段是不是都在任务后段」，**你有现成的否定答案**。
2. **delete-one 稳健性很好**【继承】：删掉任意单个 prototype，`1/c_z` 落在 16.1–24.6、预测量跨度仍 ≥ 2.63 SD；删掉任意单个族，`1/c_z` 落在 15.5–21.8、跨度 ≥ 2.61 SD。最高杠杆的单个阶段 C9（insert，唯一一个）只承担斜率权重的 **7.1%**，前三个阶段合计 20.1%——**没有单点主导**。
3. **阶段间相关性没有想象中严重**【继承】：模拟配对 episode 生成单调 CP 的真实过程，同一族内阶段间配对 Δ_k 平均相关 **0.57**、最大 0.90，逐阶段 sd 11.9–15.2 pp（`pow_stage.py` 假设的独立 sd 是 12.2 pp）。因为 family FE 吸收了公共成分，**SE(β) 只被低估约 12%**（1.47 → 1.66）。结论：配对假设成立，"stage-level paired Δ" 不是伪配对；但 iid-t 推断要换成 **episode 层 block bootstrap（重抽 episode 而不是重抽 stage）**，并把这 12% 写进预注册 MDE。**这三条是「阶段不独立会不会毁掉配对」这个必被问到的问题的现成答案，应作为 robustness 附录直接发出去。**

## 4.4 阶段级判据与条件化偏差的处理

### 4.4.1 阶段边界的划分（与分类法解耦）

沿用 v5 §6.7 的**轨 A**：夹爪 open/close 事件 + 双臂任务系速度过零 + 固定时长上限（8 s）+ 最小片段长。**零依赖、可复现、与分类法解耦。** 轨 B 就绪后再补约束坐标里程碑（铰链角 Δθ / 弧长 Δs）作 robustness。分段规则与全部超参必须进 F 文件的 hash。

### 4.4.2 阶段内配准（不做这步后面全错）

不按时间对齐，按**任务进度变量**（θ、s、夹爪事件序号）对齐，在阶段 k 内取固定进度百分位 φ 的切片；把偏差分解为沿路径（timing）与离路径（tolerance），**只用后者**：
```
δ_i   = Log(T̄_k⁻¹ T_i(φ)) ∈ R⁶
u     = 该阶段平均运动方向的单位切向（6 维）
δ_i^⊥ = δ_i − (δ_i·u)u        # 切向散布是节奏，不是容差
```

### 4.4.3 ★ HR 的分母错误（前序审查的关键发现，必须修）

`pow_stage_hr.py` 对每个阶段都用 `N = npair × 2dir = 40` 算二项 sd；但 `HR_k = P(base 到达 k 且 ours 在 k 失败)` 的有效样本是 `40 · CP_{k−1}`。重算【继承】：

| base CP_{k−1} | 有效 sd | MDE(HR 斜率) |
|---|---|---|
| 0.90 | 6.0 pp | 3.54 |
| 0.40 | 8.9 pp | 5.16 |
| 0.25 | 11.3 pp | 6.47 |
| 0.15 | 14.6 pp | 8.31 |

而 HR 最该出现的正是 B2 抓拉头、C9 卡扣这些**深阶段**，那里 base CP 恰恰最低。**按现在的算法 HR 的 power 被系统性高估约 2 倍。**

**更根本的矛盾**：主端点用非条件化 CP 是为了躲 post-treatment conditioning，而 HR 在定义上就条件于「base 到达了 k」。**同一份预注册里两个端点用了互相矛盾的因果立场。**

**处置（三条）**：
1. **把 HR 的定义搬到 stage-targeted injection 臂上**：随机化进入阶段 k，`HR_k` 就是一个干净的、非条件化的配对失败率，**且每个阶段都有满额 npair**。这把 §4.4.4 从「识别性补强」升级为 **HR 的唯一合法来源**——也是把 E2 定为 headline 主端点的技术前提。
2. 若必须在主 rollout 上报 HR，改成非条件化联合事件 `P(base 完成 k ∧ ours 未完成 k)`，分母是全部 episode，base 到达率用 split-half 的 A 半估；重算 MDE 时逐阶段代入 `N_eff = 2·npair·ĈP_{k−1}`。
3. **预注册里必须显式写明主端点与次端点的条件化立场为何不同**，否则是可被直接指出的内部矛盾。

### 4.4.4 stage-targeted injection（把主张从相关升级为干预）

只在阶段 k 注入、其余阶段一律用 base，其他全同。此时 k 处的比较是随机化的、只对前处理变量取条件。

- **规模**：8 阶段 × 20 对 × 2 方向 = 320 rollouts ≈ **7.5 robot-h**【复算，`design_stage.py`】。
- **选哪 8 个**：Δ𝔸 谱两端各 2 个 + 中位 2 个 + **三个 mode-boundary 高危阶段中的 2 个**（C1 勾把手 / B2 抓拉头 / C9 卡扣）。理由：Kroemer, Niekum, Konidaris, JMLR 2021 §2.2 逐字「*modes also make manipulation tasks inherently discontinuous. Hence, small changes in the state can have a significant effect on the outcome*」——在 mode boundary 注入错先验会翻转 mode，代价不连续，这正是预测 harm 集中的三个格子。
- **优先级**：**优先打 harm 侧的三个 mode-boundary 阶段。这是全设计里性价比最高的 2–3 小时。**

## 4.5 多重比较处理

当前至少有 5 个 confirmatory 检验跑在同一批 29 个阶段上：E1 层级变号、E2 HR 斜率、S1 ΔCP 斜率、S2 P3′ 族内 Spearman、u⊥ 的 γ。前序设计只给了 Bonferroni α = 0.025 × 2，不够；而这些检验之间高度相关（同一批 Δ_k），裸 Bonferroni 又过保守。

**预注册固定顺序的 gatekeeping 层级（与 F 文件一起冻结并出 sha256）**：
```
Gate 1   E1（层级变号，randomization inference）        α = 0.05
           ↓ 通过才允许
Gate 2   E2（HR 斜率 β_h，单侧）                        α = 0.05
           ↓ 通过才允许
Gate 3   S1（ΔCP 斜率，logit 尺度）                     α = 0.05
           ↓ 通过才允许
Gate 4   S3（per-stage oracle 归因）                    α = 0.05
S2（P3′）与 γ（u⊥）明确降为 secondary，标注 exploratory-confirmatory 混合，不进 Abstract
S5（ζ 嵌套比较）纯 exploratory，报出即可
```

顺序理由：E1 是唯一一个不依赖 T_y 绝对值的符号检验（最稳健）；E2 是唯一一个先验方向明确且反直觉的（最有信息量）；S1 是最容易被指为平凡的（最后）。

## 4.6 ★ matched-pair fixture：唯一能把预测量与平凡预测量分开的实验操作

**问题**：当前阶段集里不存在任何一对 stage 能让预测量与 `−log min T_y` 分开。等 rollout 跑完再去找 disagreeing pair 就是 post-hoc，正好坐实 fishing。**必须在冻结阶段集之前用硬件操作制造出来。**

**设计：固定容差，只变约束结构。** 每对里朴素预测量在对内是常数，Δ𝔸 在对内不同；主张改为**对内 contrast**（自动吸收族效应、物体、光照）。至少造 4 对，全部是几小时的激光切割 / 3D 打印 / 夹具活：

| 对 | A 侧（有约束结构） | B 侧（无约束结构） | 保持恒定 |
|---|---|---|---|
| P1 | 篮口**有倒角漏斗** | 篮口**无倒角直壁** | 开口内径完全相同 |
| P2 | 同一块门板**装铰链** | 同一块门板**自由放置于摩擦垫上** | 同一把手、同一目标角度公差 |
| P3 | 抽屉**带滑轨** | **无轨托盘** | 同一横向余隙 |
| P4 | 拉链**带导向槽** | **裸齿列** | 同一 3 mm 槽宽 |

**预注册命题**：`对内 ΔCP 差 ≠ 0`，方向由 Δ𝔸 指定。

**这一条如果成立，论文的结论就不再是「紧的差」，而是「同样紧、有约束结构的不差」——这才是唯一非平凡的、且本文独有的命题。** 它也天然是族内的，顺带解决 §4.7 的族内方差门槛。

**预算**：4 对 × 2 侧 × 20 配对 × 2 方向 = 640 rollouts。按 `design_stage.py` 的 1.75–2.5 min/rollout ≈ **19–27 robot-h**。这是本重构最大的单笔新增成本，必须与 §4.8 一起权衡。**若预算不够，砍到 2 对（P2 门 + P4 拉链，对应 hinge/zip 的关键对照）≈ 10–13 robot-h。**

## 4.7 设计可行性门槛（硬 gate，不是建议）

**族内方差占比 ≥ 0.5。**【继承，`pow2.py`】若预测量本质是族的属性（族内方差 10%），MDE 炸到 **18 pp/SD**——那就是 v5 §6.8 修法 4 的 `n_eff ≈ 4` 问题改头换面重演。

当前实测【复算，`design_stage.py`】：
```
[logzeta] confirmatory: within-family share = 0.879  between = 0.121  sd = 1.496
[absorb]  confirmatory: within-family share = 0.995  between = 0.005  sd = 2.110
```
**族内方差占比 0.879，远超 0.5，门槛通过。** 但注意这是**按 prototype 查表**算出来的；换成逐阶段计算后必须重算。**Δ𝔸 的族内方差占比尚未算，F 冻结前必须补。**【待补算】

**族定义必须在 F 文件里锁死，不能等 G0.5″-d 再决定**——族定义本身是 analyst degree of freedom（任务族 4 族 vs 物体实例 7 族），且直接决定 β 的 SE。**锁死顺序：先锁族定义 → 再算族内方差占比 → 不达 0.5 则用 §4.6 的 matched-pair 补阶段（天然族内），而不是重新划族。**

**族的推荐定义**：维持 v5 的**任务族**（C/B/D/E），不改为物体实例。理由：物体实例把 n_cluster 从 4 抬到 7 看似有益，但每个实例至少要 5 个阶段才有族内 df，本设计的实例阶段数不够；且 §4.3.1 已把主推断换成 randomization inference，cluster 数不再是 p 值下界的瓶颈。

## 4.8 机器人小时预算更新

`design_stage.py` 的现有算式【复算，全部输出逐行核对】：

| 项 | robot-h |
|---|---|
| 主端点 400 rollouts（npair=20） | 30.4（其中刚体 confirmatory 19.4，布料 exploratory 11.0） |
| stage-targeted injection（8 阶段 × 20 对 × 2） | 7.5 |
| level sweep ①+④（P→X only） | 7.3 |
| A/A + π_d pilot | 7.3 |
| 7 个 control arm | 19.4 |
| R-t-S 同本体 ×2 | 5.5 |
| D6 单臂 reader | 5.5 |
| G0.5 / E5 / ER | 2.3 / 4.2 / 4.8 |
| **EVAL 小计** | **94.2** |
| D12 采集（360 episode） | 29.3 |
| **合计** | **123.5**（v5 baseline 150） |

**本重构的增量**：

| 新增项 | robot-h | 可否砍 |
|---|---|---|
| **matched-pair fixture（4 对全量）** | +19～27 | 可砍到 2 对 = +10～13 |
| E3 扰动校准（3 阶段 × 20 trial） | +1.5 | 不可砍（E2 的唯一校准） |
| G0.5″ 全部四条判据 | **0**（纯离线） | — |
| Δ𝔸 / T_y 的物理测量 | **0 robot-h**（卡尺 + CAD，约 4 人时） | 不可砍 |
| 盲引 T_y 交叉验证（≥5 人） | **0 robot-h**（约 2 小时人情） | 不可砍 |
| 人类基线实验（见 §6.4） | **0 robot-h**（约 1 小时人情） | 可砍但强烈建议做 |

**新总计：123.5 + 21 ≈ 144.5 robot-h（全量）或 123.5 + 12 ≈ 135.5（砍半），仍在 v5 baseline 150 之内。**

**可以砍的**：布料族 exploratory 主端点 11.0 h 若预算紧张可延后（与 v5 §8.3 把叠衣降 exploratory 的 MVP 决策一致），正好抵掉 matched-pair 全量的成本。

---

# 5. 对主张结构的影响

## 5.1 新 SQ 结构

| 旧 | 新 | 变化 |
|---|---|---|
| SQ1：存在一个 ℓ*，使两条曲线在此交叉 | **SQ1″**（§1.1）：ℓ* 是阶段的函数吗？形状能否离线算出？ | 点估计 → 有符号翻转的函数 |
| SQ2：跨本体检索瓶颈在 key 侧还是 value 侧？（记账题） | **SQ2′：primitive 条件化到底住在哪一侧？**（机理证伪题） | Δ𝔸 的构造**完全是 value 侧的**。若交互主要出现在 `Δ_retarget`/`Δ_value` 两桶 ⇒ 机理确证；**若主要出现在 `Δ_key` 桶 ⇒ Δ𝔸 是错的，即使它在 outcome 上相关。** 这是一个真正能杀死 C1 的检验，旧 SQ2 没有这个能力。执行：v5 §3.4 的 oracle 阶梯**逐阶段重算**，零增量成本 |
| SQ3：共享池有无串扰？ | **SQ3′：共享池净效应是否也是阶段的函数，且与 SQ1″ 同向？** | 污染应集中在「检索侧看起来完全可用、执行侧不可用」的阶段。若成立，SQ3′ 就是 SQ1″ 交互在另一个 outcome 上的**独立重复**，成本为零（表本来就要跑，只是加一列分组） |

## 5.2 预测汇总表（替换 v5 §3.6）

| # | 预测 | 检验 | 何时判定 | 被推翻 → 论文形态 |
|---|---|---|---|---|
| **P1″** | `ℓ*(k)` 非常数且符号由 Δ𝔸(k) 预测；宽容差阶段层④反超 | G0.5″ 离线 + 主端点 E1 | **G0.5″，0 robot-h** | 切 Fallback A（§6.5） |
| **P7′（升为 headline）** | HR > 0 且随 Δ𝔸 反向；**由 Δ𝔸 预测而检索置信度不预测**（key/value 解耦） | 主端点 E2（stage-targeted 臂） | G6 | 「记忆无害」是更好的工程结果，但削弱 C4；或「门控已部分捕获可执行性」（δ 显著），两支都可发表 |
| **P2′** | 交互住在 value 侧，不在 key 侧 | per-stage oracle 阶梯 | G5 | Δ𝔸 机理被证伪 → C1 撤回，C2 保留 |
| **P8（新，matched-pair）** | 容差固定时，**有约束结构侧优于无约束结构侧** | §4.6 对内 contrast | G6 | 「约束结构在容差之外无独立效应」——这直接把 C1 打回平凡，必须诚实报 |
| **P3′** | 方向不对称由离线 φ 预测逐阶段排序 | 族内 Spearman，n≈29 | G6 | 报 no asymmetry at this power |
| **P4′** | 共享池污染集中在低 Δ𝔸 阶段 | 三条件 × Δ𝔸 三分位 | G6 | 「此规模下未观测到阶段相关的串扰」 |
| **P5** | 层④←架构、层③←限位 | 已离线成立 | 已成立（待 FK 验收） | FK 残差 >5 mm → 全盘作废 |
| **P6** | 增益 ∝ u⊥；基座已确定的阶段无增益 | γ，门槛 `R²(u~C) < 0.5` | G6 | 双因子退化单因子，不伤 P1″ |

## 5.3 G0.5 gate 的离线版本：G0.5″（0 robot-hours）

### 5.3.1 为什么旧 gate 必须废

旧判据 `SR_same(④) − SR_same(③) ≥ 10 pp` 赌的是**主效应**，而它恰好是本硬件上最可能为零的量（同本体 position-only IK 可行率实测 100.0%）。

### 5.3.2 可计算对象（全部输入今天已具备）

对存量 Piper 语料的每个阶段 k、每帧 i、每层 ℓ ∈ {③,④}：
```
e₄(k,i) = Log( FK_reader(A·q_i + b)⁻¹ · T_task(i) )              # 最优固定线性标定残差（A,b 已拟合）
e₃(k,i) = Log( FK_reader(IK_clip(T_task(i)))⁻¹ · T_task(i) )     # IK 失败 → abstain
z_ℓ(k,i) = ‖ diag(1/T_y(k)) · J_k · e_ℓ(k,i) ‖
A_ℓ(k)   = mean_i 1[ z_ℓ(k,i) < 1 ] · (1 − abstain_ℓ(k))
Δ𝔸(k)    = A₃(k) − A₄(k)
```
脚本：`/tmp/agxurdf/redteam.py`（A,b 与残差）、`redteam2.py`（限位归因）、`taskspace.py`（层③可行率与逐阶段弃权）、`RAL2027/covariates/admiss.py`（本轮新建）。**零机器人小时，零新硬件依赖。**

### 5.3.3 冻结顺序（反 fishing 的全部内容）

| 时点 | 冻结物 | sha256 |
|---|---|---|
| **≤ 08-28** | `Ty_measured.csv` + 每个 `J_k` 的实测几何（力臂 r、曲率半径、半锥角）+ 盲引 ICC 报告 | 单独 |
| **08-31** | **F 文件**：阶段定义与切分规则（含全部超参）、族定义、三层标注表（**仅用于叙事**）、`Δ𝔸(k)` 与 `ζ(k)` 的先验数值、P1″/P7′/P8 方向表、gatekeeping 顺序、MDE 表（τ_p 三档）、撤回条款、**留出族指定** | 单独 |
| **09-05** | 才计算 `A_ℓ` 与 G0.5″ 四判据 | — |
| **09-08** | **arXiv 占位**，v1 附录**全文塞入 F 文件** | 外部时间戳 |

**F 文件的 hash 必须覆盖变体空间而非一个点**：标签表 + 裁决人姓名 + `Ty_measured.csv` + 分段脚本及其全部超参 + 一句「**本文件不存在第二版本，任何修订以新 hash 追加发布并在正文列出 diff**」。

### 5.3.4 四条判据（预注册，看 A_ℓ 之前冻结）

| 判据 | 内容 | 通过线 |
|---|---|---|
| **a — 异质性（唯一 KILL 条款）** | `range_k Δ𝔸(k) ≥ 0.40`，**且至少 1 个阶段 Δ𝔸 < 0**（层④反超，即符号翻转真实存在），且 ≥2 个阶段 Δ𝔸 ≥ 0.30 | 三条同时满足 |
| **b — 可预测性** | **族内** Spearman `ρ(Δ𝔸(k), A₄(k)) ` 与 `ρ(Δ𝔸(k), −log min T_y(k))` 同时报；**要求后者 \|ρ\| ≤ 0.4**（证明不是朴素预测量的改名） | 必须用族内秩，不得用 pooled |
| **c — 反同义反复（离线 A/A）** | 把 primitive 标签**在族内**随机置换 ≥1000 次重算判据 b 的统计量；观测值须落在置换零分布 >95 百分位 | 不过 = Δ𝔸 只是「族」的改名 |
| **d — 设计可行性** | 冻结阶段集上 `Δ𝔸` 的**族内方差占比 ≥ 0.5**；且 `corr(Δ𝔸, 1[hinge∨transport] \| family FE)` 的 `R² ≤ 0.5`（§4.3.3）；不足则以 D-optimal（做在残差上）增删阶段 + §4.6 matched-pair 补 | 必须在 G3b 的 E0 切分冻结之前完成 |

### 5.3.5 判定树

| 结果 | 动作 |
|---|---|
| a,b,c,d 全过 | 主线成立。**09-08 立即 arXiv 占位**（比 v5 定的 G2a 后早 3 周，且占的正是抢跑防御最需要的那块） |
| **a 不过** | **条件化框架当场死亡。不要花任何机器人小时跑 level sweep。** 直接切 Fallback A（§6.5） |
| a 过、b 不过（Δ𝔸 与朴素量高度相关） | **C1 撤回并降 exploratory，C2 保留。** 论文变成「分解很陡，但我们的先验预测量不比『哪个阶段最紧』强」。必须找 post-hoc 预测量并**在留出族上预注册重测**（留出族在 08-31 就要指定） |
| b 过、c 不过 | Δ𝔸 是族的改名。不得报 ρ；C1 改写为「族级而非阶段级的条件化」，效力回落 n_eff ≈ 4 |
| d 不过 | **冻结前修设计，不是修统计**（加 matched-pair 阶段） |

### 5.3.6 两条必须自己先说的残余风险

1. **`A_ℓ` 是 SR 的运动学代理**（见 §3.2.3-L4），由 G2a 阶段级校准，秩相关 <0.5 则全部结论降级为「关于可执行性的陈述」。
2. **单点故障未变**：`A_ℓ` 全部建在 URDF FK 上。v5 §1.6 #2 的 FK 一致性硬验收（20 构型 <5 mm / <2°）不过 ⇒ G0.5″ 连同 P5 全部作废。**这条必须排在 G0.5″ 之前而不是同一天（提前到 08-28 之前）。**

## 5.4 Contribution 四条（英文成稿，替换施工图 §0.4）

> **1) A pre-computed, sign-flipping prediction of which abstraction level a persistent action memory should be read at, stage by stage, when the reader is a different body.**
> The best fixed joint-space calibration between our two bimanual platforms leaves a median residual of 7.1 cm and 17.8°. Whether that residual matters is not a property of the residual: projected through a stage's measured outcome tolerances and its measured contact geometry, and set against the abstain rate that a task-space retarget pays for its precision, it predicts that the naive joint-space copy is the *better* readout on wide-tolerance stages and the *worse* one on a narrow track. The prediction changes sign, is computed from measured quantities rather than asserted ones, and is frozen with a hash, together with its retraction conditions, before any success rate exists.

> **2) A per-stage account of what a foreign memory does — including where it does harm — under one fixed injection path, with the harm measured interventionally.**
> Compositional household tasks are scored stage by stage on a non-conditional cumulative-progress scale, so that no stage-level quantity is conditioned on having reached that stage. Harm is not read off the main rollouts, where it would be so conditioned; it is measured on a stage-targeted arm in which injection is applied at one stage while every other stage falls back to the memoryless base. We report, per stage, whether the retrieval confidence that gates injection can see the executability that determines the outcome.

> **3) A persistent store of executable action content that two deployed bodies write to and read from in both directions, with no gradient reaching either policy after deployment.**
> Each body's base policy is fine-tuned once, before deployment, on tasks disjoint from the memory-evaluation tasks; nothing is updated when the store is admitted or when it grows. Abstraction level is the only variable we manipulate: every level is decoded into the reader's own action space and injected at the same point of the same frozen flow-matching sampler. We further admit a third, previously unseen reader and report its admission cost in paired episodes and GPU-minutes, alongside the cost of a per-body target-side fine-tune on the same pair.

> **4) A fixture-controlled separation of two explanations that are otherwise confounded: tolerance and constraint structure.**
> Every claim of the form "tight stages transfer worse" is already implied by the task-frame decomposition of contact. We therefore build matched pairs in which the clearance is held fixed by construction and only the constraint structure changes — a chamfered versus a straight-walled opening, the same door panel hinged versus free, the same slider with and without a guide channel — and pre-register the within-pair contrast. An oracle ladder attributes the same-body-to-cross-body gap to retrieval, retargeting and value inexecutability, with the retargeting term split into a joint-limit and a geometric component, per stage and without post-hoc human labelling.

> **We explicitly do not claim**: the intermediate-state injection into a flow-matching sampler, the confidence-adaptive guidance strength, the abstain-on-low-confidence fallback, or the component-aware aggregation of retrieved chunks — all adopted unchanged from Retrieve-then-Steer once an entry has been decoded into the reader's action space; **nor the stage-resolved reporting format for long-horizon tasks, which that work introduced**; **nor the practice of regrouping tasks by functional characteristics to explain why a memory design helps unevenly, which RoboMME established under a single embodiment**; **nor the qualitative relation that tighter clearances transfer worse, which follows from the natural/artificial constraint decomposition of contact**; nor any of the manipulation taxonomies whose labels we use; nor gradient-free growth of a retrieval pool, demonstrated by RECAP; nor entry-level revocability, demonstrated by CLARE.

**相对旧四条的四处结构性变化**：① 删除「我们提出分层表示」的卖点（GR00T N1.7 relative-EEF 与 R-t-S 多控制空间聚合已占位），改挂「层级是唯一被操纵的变量 + 注入路径逐字固定」；② C1 从「跨 100 倍的定量预测」改为「**会变号**的符号预测」——后者可测，前者不可测（§4.3.3）；③ C4 从纯 oracle 阶梯改为 **fixture-controlled 分离**，这是唯一能割掉平凡性的那一刀；④ do-not-claim 新增三条主动弃权（RoboMME 方法论、R-t-S 阶段评分格式、**「紧的差」这一定性关系本身**）。**主动弃权比被指出便宜一个量级。**

## 5.5 Title / Abstract / 叙事

### 5.5.1 Title 候选

| # | 候选 | 何时用 |
|---|---|---|
| **T-A（推荐）** | **When Does a Foreign Body's Action Memory Help, and When Does It Hurt? A Per-Stage Measurement Under a Frozen VLA** | 主端点 E2（harm 解耦）显著。与新的 headline 排序一致 |
| T-B | Which Readout Level Survives a Change of Body? A Sign-Flipping, Pre-Computed Answer, Stage by Stage | E1（层级变号）显著而 E2 不显著 |
| T-C（保守） | Primitive-Conditioned Cross-Body Readout of a Persistent Action Memory for Frozen VLA Policies | rebuttal 后改名的退路，最不可攻击 |
| T-D（Fallback A 绑定） | Per-Stage Level Routing for Cross-Body Action Memory: An Admissibility Study | G0.5″-a 不过 |
| T-E（Fallback B 绑定） | Does Cross-Body Action Memory Transfer Unevenly? A Pre-Registered Null at 9 pp Resolution | 零结果专用。**标题必须带分辨率数字**，且数字必须是 τ_p=6 那档（≈9 pp），不得用 4.8 |

**绑定规则**（沿用 v5 §8.2 G6）：Title / Abstract / Intro ¶5 预注册句 / Contribution 1 **四处绑定，不可只改一个**。

### 5.5.2 Abstract（约 215 词，替换施工图 §0.2）

> A robot that improves during deployment must put what it learned somewhere, and a persistent store of successful action chunks has already been shown to help the frozen vision–language–action policy that wrote it. What has not been shown is such a store of *executable action content*, written by a robot *during its own deployment*, read by a *second deployed robot of a different kinematic family* with *no further update to its policy*. The best fixed joint-space calibration between our two bimanual platforms leaves a median residual of 7.1 cm and 17.8°, and the useful question is not how much of that survives on average but where in a long-horizon task it survives at all. Reading the memory in the task frame costs an abstain whenever the reader's inverse kinematics fails; reading it as raw joint angles never abstains but pays the full residual. We compute, before any evaluation and from measured tolerances and measured contact geometry rather than asserted ones, which of the two wins at each stage — a prediction that changes sign — and we freeze it, with its retraction conditions, under a hash. We then report per-stage gain and per-stage harm on compositional household tasks, measure harm on a stage-targeted arm so that it is not conditioned on having reached the stage, and separate tolerance from constraint structure with matched fixtures in which the clearance is held fixed by construction. Every number is reported with the injection rate that conditions it.

**红线自检**：无 first/novel/unexplored/fill-the-gap；四个限定词齐全；injection rate 出现；主动交出 7.1 cm / 17.8° 而非只报 82.8°；**不出现 "spans two orders of magnitude"**（那是离线计算不是 finding，且已知不可测）。

### 5.5.3 叙事一句话（英文，替换 v5 §2.4）

> Retrieval-augmented frozen VLAs now work, and a persistent store of successful chunks has already been shown to help a frozen $\pi_{0.5}$ fold shirts on a bimanual AgileX PiPER — read by the same body that wrote it. When the reader is a different body, the question stops being *how much* of the memory survives and becomes *which reading of it* survives, and *where*. Our spherical-wrist Piper and our offset-wrist PiperX are identical in degrees of freedom, payload and repeatability, and differ by 6.9 % in reach; the best fixed joint-space calibration between them leaves 7.1 cm and 17.8°. Reading an entry in the task frame costs an abstain wherever the reader's kinematics cannot reach; reading it as joint angles never abstains but pays that residual in full. Which trade wins is a property of the stage, not of the pair of robots — and on a wide-tolerance transfer the naive reading wins. We compute that ranking from measured geometry, freeze it with its retraction conditions, and only then run anything. Then two deployed bodies write to and read from one store in both directions, with no policy gradient, and we report per-stage gain, per-stage harm, and the injection rate that conditions both.

**新增的两句是全段最重要的**：「Which trade wins is a property of the stage」把主张从数量换成结构；「We compute that ranking ... and only then run anything」同时承担 novelty 与反 fishing。

## 5.6 与 RoboMME 的对齐声明

### 5.6.1 写法（英文，进 §II-C 或 §IV 开头）

> Our task suite is, in the taxonomy of [RoboMME], primarily *procedural* memory with a *temporal* component, since a compositional task carries both a motion pattern to be reproduced and an ordering of sub-goals. That work also establishes the analysis pattern we follow: when its four cognitive memory types did not account for task-level differences, it regrouped tasks by functional characteristics and found that no single memory design wins everywhere, with sign reversals across groups. We adopt that pattern rather than re-derive it. What differs is the conditioning variable and the setting. [RoboMME] conditions the effect of a *memory design* on *history-reasoning demand*, under a single 7-DoF embodiment and a single backbone — boundaries it states explicitly. We condition the effect of a *reader change* on *contact geometry*, and we take our labels from published manipulation taxonomies rather than introducing new ones. The two axes are crossed, not nested: each of our stages is reported with its functional group under [RoboMME] alongside its geometric label, and we pre-register the check that our predictor retains rank agreement *within* a single functional group. Stages in which the object itself reduces the task frame to one degree of freedom — a hinged door, a zipper track — have no counterpart among those functional groups; they are where our prediction is most exposed, and where it is most informative.

### 5.6.2 三个使它既对齐又不被吃掉的机制

1. **主动弃权方法论**。承认「按功能特征重新分组」是它的招式并显式引用（Appendix C.3 / Table 13-14）。**这一步删掉了「你重新发明了他们的动作」这一刀。** 剩下的 novelty 只能落在自变量上——那正是我们独有的。
2. **★ 交叉而非嵌套的实证检验（最强的一件）**：每个阶段**同时**标注 RoboMME 功能类别与 Δ𝔸，然后**预注册：在单一功能组内部，Δ𝔸 的族内秩相关仍然成立**。若在同一个 Motion-Centric 组里 Δ𝔸 仍变号且仍预测，**我们的轴在数学上就不是他们的轴的改名**。这条检验便宜、离线可做、且决定性。**没有这一条，「正交」只是一句形容词。**
3. **盲区用建设性语气**。写 "have no counterpart among those functional groups"（覆盖互补），不写 "they missed it"；并立刻自曝这正是我们最暴露的地方（articulated 的先验证据混合：RAM 的 O +17.3 > C +10.0 > P +4.5 支持；RECAP 的 Open Microwave 仅 +2.5、VLA-Pro 的 close_microwave −26.7 反对）。**证据混合是好事——说明这是真正未定的可证伪预测。**

**rebuttal 备答（一句，进模板）**：
> *RoboMME conditions the gain on history-reasoning demand under a single embodiment; we condition it on contact geometry under a change of reader. The independent variables do not intersect, that work names single-embodiment as its boundary, and we report the within-functional-group rank test that shows our axis is not a relabelling of theirs.*

### 5.6.3 引用纪律

RoboMME 的数值（Table 14 分组 delta：symbolic 在 Motion-Centric **−5.34** 而在 Event-Salient **+39.12**，跨类极差 34–58 点）是 pdftotext 按 layout 重抽的【继承】；**定稿前须人工核对表格原图**。**【待确认】RoboMME 的 ICML'26 收录状态未从 arXiv comment 字段核实，只能写 arXiv preprint。**

## 5.7 对 Retrieve-then-Steer 的划界措辞（英文，替换 v5 §2.3 后半 + 施工图 §3.4 对应句）

> We adopt from [R-t-S], unchanged, the intermediate-state initialisation of the flow sampler, the confidence-adaptive guidance strength, the abstain-and-fall-back rule, and the component-aware aggregation of retrieved chunks; we also adopt its stage-resolved reporting format, in which a long-horizon task is scored by how far it advanced rather than only by terminal success. That work is not merely the source of our injection path: it is a direct predecessor on our own hardware. It reports bimanual T-shirt folding on two 6-DoF AgileX PiPER arms with a frozen $\pi_{0.5}$, improving 42.0 %→50.0 % in domain and 36.0 %→46.0 % out of domain, at 50 trials per cell, and it reports sequential test-tube placement stage by stage, raising the average completed length from 1.54 to 1.94. We note — as a property of experimental design rather than of the method, and one that applies equally to every single-task cell of our own tables — that a single task at 50 trials per cell cannot by itself localise *where within the task* an improvement was produced, and that the four stages of the test-tube task are four repetitions of one pick-and-place primitive, so that the completed-length score measures progress rather than which primitive benefited. This is why we power on stages rather than on tasks, why our stages are heterogeneous by construction, and why our harm measurements are made on a separately randomised arm. Two further boundaries are stated by that work itself: its two platforms are complementary testbeds, each writing and reading its own memory, and its stated limitations name a change in **robot calibration** as a condition under which stored priors may become less informative or even misleading. That condition is our operating point.

**三条措辞纪律（写进 §II 写作红线）**：

1. **绝不把 p 值当武器。** 前序稿里的「Fisher exact 给 p = 0.55 / 0.42」应**删除**——攻击一篇未定稿预印本的显著性会立刻反噬，而同样的算术对我们自己的每一个 single-task cell 都成立。改成上面的定性表述即可，力度不减而风险归零。
2. **同质阶段 vs 异质阶段是真正的分野，必须比任何统计话术更靠前地讲。**
3. **把它的 limitation 变成我们的 premise**，逐字引用 "robot calibration" 那一句。这是全篇最省力的一处生态位论证。同型弹药：Dejavu 的 future work 逐字承认 experience bank 绑定单一 domain/embodiment 且点名 negative transfer，应并列引用。

**baseline 表脚注（必补）**：R-t-S 的 component-aware aggregation 明文允许 `Δp` 是 end-effector position increments **或 joint-angle increments**，并声称支持 EE 位姿控制、关节空间控制与不同夹爪参数化。→ **本文层③改成「锚点系下接触点运动」后仍能原样喂进其聚合式，统一读出接口不受影响。** 这句要写在方法节，它是「注入路径逐字固定」这一 C3 主张的技术前提。

**【待确认】R-t-S 的 venue 为 preprint 态（arXiv 2605.10094v2）；42.0→50.0 等数字定稿前需人工核对表格原图。**

---

# 6. 风险

## 6.1 风险 #1：fishing expedition 指控

### 6.1.1 指控的最强形式（按当前实例化，它**成立**）

> 「ζ 是把已有假设用线性代数洗了一遍。假设列表（articulated 高 / place-insert 低）在脚本之前就存在；ζ 的排序与作者手打的 26 个 T_y 常数的最小值完全同秩（Spearman = 1.000）；SPD 张量、cholesky、SVD、有效秩、Frobenius 范数对排序的贡献恰好为零。你预注册的那个量本身就是你要检验的假设。」

**这个指控不需要任何「作者偷看结果」的动机假设**，只需要打开补充材料的脚本跑两分钟——我本轮就是这么做的。**不改就冻结，C1 当场死亡且无法 rebuttal。**

### 6.1.2 处置（六条，全部在 F 冻结前可完成）

| # | 处置 | 效果 | 成本 |
|---|---|---|---|
| R1 | **T_y 外源化**（物理测量 → `Ty_measured.csv` 单独 hash；拿不到的阶段排除，不许估） | 把「我自己打的数」变成可审计的测量 | 4 人时 |
| R2 | **盲引 ICC 交叉验证**（≥5 位不知假设的研究者独立给 log T_y，报 ICC(2,k)，<0.6 则降 exploratory） | 把主观性变成一个可报的数 | 2 小时人情 |
| R3 | **换预测量：ζ → Δ𝔸**（与朴素量 Spearman −0.26，非单调，会变号） | **结构性解除指控**：被检验的命题不再是「紧的差」 | 已完成（`admiss.py`） |
| R4 | **confirmatory 路径去标签化**（主端点不依赖任何 primitive 名，分类法只用于叙事与 robustness） | K 从 16 降到 ≤4，FPR 从 44.4% 拉回 ~16%【继承】 | 0 |
| R5 | **matched-pair fixture**（容差固定、只变约束结构，对内 contrast） | 把「紧的差」这一平凡命题**从设计上排除掉**，而不是靠措辞 | 10–27 robot-h |
| R6 | **F 文件与 arXiv 占位绑定发布**（外部时间戳 >> 自 hash），hash 覆盖变体空间而非一个点 | 把「作者自己 hash 自己」变成第三方时间戳 | 0 |

### 6.1.3 必须主动交出的六张自曝表（比等审稿人算出来便宜一个量级）

全部脚本已就绪，直接进补充材料：
1. `ζ` vs `−log min T_y`：Spearman = **1.000**，log-log Pearson = **0.990**【复算】
2. 随机 J、T_y 下 ζ 的「坐标图不变性」逐位不变 → **它是代数恒等式，证明不了任何东西**【继承】
3. `ζ_hinge` 对力臂 r 的敏感曲线：r = 1.0/0.8/0.35/0.2/0.12 m → 0.294/0.367/0.839/1.468/2.447【复算】
4. analyst-freedom FPR 表：K = 1/4/16/64 → 5.5/16.4/44.4/78.1%【继承】
5. R² 表：β = 3/5/8/12 pp/SD → partial R² = 0.057/0.144/0.301/0.492【继承】
6. router 捕获率表：R² = 0.05/0.14/0.30/0.50 → 吃到 oracle 增益的 5.5/23.7/44.2/63.2%【继承】

### 6.1.4 **无解项（诚实标注）**

- **机器人领域没有 registered-report 机制。** `abs:"pre-registered" AND cat:cs.RO` 在 arXiv 全库只有 **9 条**【继承】。作者自己 hash 自己的文件，证据力接近于零；arXiv 时间戳是能拿到的最强外部锚，但它锁不住「冻结前在变体空间里游走」。**这一条无解，只能靠 R4（去标签化）把变体空间本身缩小，并在论文里诚实说明「我们没有可抄的模板，格式是自定的」。**
- **outcome-blind ≠ prediction-blind。** 作者知道自己希望哪些格子高哪些低。**无解。** 唯一的缓解是 R5：让预测的方向由 fixture 的物理构造决定，而不是由标注决定。

## 6.2 风险 #2：n_eff 过小

### 6.2.1 三个独立的 n_eff 杀手（全部本轮复算）

| # | 杀手 | 量级 | 处置 | 残余 |
|---|---|---|---|---|
| K1 | **族级 wild cluster bootstrap 在 G=4 下 min p = 0.0625** | power 恒为 0 | 换 randomization inference（§4.3.1） | 已解决 |
| K2 | **prototype 随机截距**：τ_p = 6 pp ⇒ n_eff 从 24.3 掉到 **7.1**，MDE 从 4.86 涨到 **8.98** | 击穿「交互 n=29」的反驳 | 逐阶段计算预测量（§4.3.2） | **部分**：τ_p 是否 <6 pp 要等真实数据，**必须按 τ_p ∈ {0,3,6} 三档报 MDE，宣称值用 τ_p=6** |
| K3 | **连续量与二值标签 R² = 0.816**，条件于二值后 `1/c` 从 24.62 → 4.53，MDE 膨胀 **2.33×** | 定量主张不可证伪 | 降级为符号/三分位主张 + 嵌套比较（§4.3.3） | **未解**：Δ𝔸 与二值的相关性尚未算【待补算】 |

### 6.2.2 诚实的 MDE 声明（写进论文与 F 文件）

```
主端点 S1（ΔCP 斜率），29 阶段、npair=20、ordinal 读数、episode-block bootstrap：
  τ_p = 0 →  MDE = 4.9 pp/SD   （乐观，不得对外宣称）
  τ_p = 3 →  MDE = 6.2 pp/SD
  τ_p = 6 →  MDE = 9.0 pp/SD   ← 对外宣称用这一档
  加 12% 阶段相关修正后 ≈ 10.1 pp/SD
  条件于二值标签的增量检验：MDE ≈ 21–23 pp/SD  ← 事实上不可行，报出即可
主端点 E2（HR 斜率），stage-targeted 臂，每阶段满额 npair：
  base CP 不再进分母 ⇒ MDE ≈ 3.5 pp（相对主 rollout 上的 8.3 pp 是 2.4× 改善）
```

**这直接决定 Title T-E 的数字必须是 9 pp 而不是 4.8 pp。**

### 6.2.3 **无解项（诚实标注）**

- **partial R² 被设计钉死在 ~0.14。** β = 5 pp/SD（正是 MDE 目标）配残差 12.2 pp ⇒ partial R² = 0.144；β = 3 ⇒ 0.057【继承】。**即「完全成功的 confirmatory 结果」长得和「几乎没关系」一模一样。这是设计的必然产物，不是运气。**
  处置：**现在就把 R² = 0.14 写出来先手拆弹**；在 F 文件里**禁止把 R² 或 variance-explained 用作任何成败判据**；改报三个可用量——(a) Δ𝔸 三分位间的 ΔCP 差（β=5 时顶/底三分位差 11.0 pp，对照组内 sd 12.2 pp），(b) **Δ𝔸-router 相对 best fixed layer 的实测增益，且强制同时报 oracle routing 上界**（R²=0.14 时 router 只吃到 oracle 增益的 23.7%；不报上界的 router 数字是虚报），(c) 符号一致率。
- **交互效应的统计效力严格低于主效应，这是一般规律，我们不推翻它。** 我们只主张「在本设计里主效应的 df 被族吃光而阶段是免费的」，这个反驳**是条件性的**，条件是 §4.7 的族内方差门槛与 §4.3.2 的 τ_p。**τ_p ≥ 8 pp 时反驳完全失效（n_eff = 4.6 ≈ 主效应的 4–5）。这一条无解，只能在真实数据上量出 τ_p 后诚实报告。**

## 6.3 风险 #3：交互为零的四条**非统计**原因

统计效力只是一半。交互也可能因为真实机理而为零：

| # | 机理 | 离线/廉价预检 | 处置 |
|---|---|---|---|
| **M1** | **基座失败以感知/语义为主**（没抓对物体、根本没尝试），运动学残差从不成为 binding constraint | 存量 rollout 的 **per-stage first-fault 分布**：若「未尝试/错物体」占比 > 50%，Δ𝔸 不可能预测任何东西 | **属于预 gate，在 G0.5″ 同批做（0 robot-h）；不过则整个 value 侧条件化无对象** |
| M2 | 天花板/地板截断：base SR ≈ 0 或 ≈ 100 的阶段无法显示增益差 | pilot 测每族 base SR | 沿用 v5 §6.8 修法 1：D 族强制制造 headroom（开合角随机、本体位置 ±8 cm / ±10° yaw、加干扰物），把每变体压进 25–65% |
| **M3** | **柔顺预算不足导致符号反转**：刚性位置伺服下铰接段不吸收残差而产生内力 → Δ𝔸 最高的一档变成最先 abort 的一档 | v5 §6.9 已有力矩 abort 判据；**并报「该阶段力矩 p95 / abort 阈值」** | **主端点预注册为两侧检验**，符号作为机理的次级主张。**反号是可归因的结果，不是意外，但它杀死预注册的方向**——必须现在就把两侧检验与力矩协变量写进 F 文件 |
| M4 | 注入门控把高危阶段整体弃权掉（IR→0），交互被门控吃掉 | 每阶段并报 IR | 沿用施工图 §4.6 硬规则：每层同时报 `gated` 与 `forced` 两列，**P1″ 建在 forced 列上** |

**M3 是最诚实也最危险的一条：它不是「没有交互」，是「交互反号」。** 反号仍可发表（且是关于柔顺预算的有用发现），但必须**先说**。

**【待确认，最高优先级，非文献问题】** π0.5 输出的是位置型 action chunk；若 Piper/PiperX 的执行层是刚性位置伺服且不可背驱，则 C2/C8/B3/B6 这些 1-DoF 阶段不会「吸收」17.8° 的非切向分量，而会把它变成内力 → 卡死/脱手。这与 v5 §1.6 待确认 #3（是否有腕部力/力矩或触觉通道）是同一件事，**必须在冻结 F 之前实测，不能靠文献推断。** 若无力通道，需现在决定：(i) 把主张改成两侧检验 + 力矩 gating 协变量，还是 (ii) 把铰接族整体降为 exploratory。

## 6.4 风险 #4：平凡性指控（「这不就是常识吗」）

§1.3 已给出四级分级。**处置的关键动作是一个 0 robot-hour 的实验：人类基线。**

> 给 ≥10 位不知假设的机器人研究者看 20 对阶段视频，强制二选一「哪个阶段的跨本体记忆增益更大」，**在跑 rollout 之前收齐**。

- 若人类准确率 ≈ 预测量准确率 ⇒ **C1 必须重写为「我们**测量**了这个函数」而非「我们**预测**了它」**。这仍是合法贡献（无人测过），但措辞必须诚实。
- 若预测量显著优于人类 ⇒ triviality 指控被**定量**击退。

**成本：1 小时人情。收益：把最难反驳的口头指控变成一张表。强烈建议做。**

## 6.5 三层退路

排序：**主线（E1 + E2 显著）> Fallback A（router / admissibility）> Fallback B（calibrated null）**。v5 §2.5 原文被 A 完全吸收，不再单列。

### 6.5.1 Fallback A：per-stage level routing，outcome 换成 admissibility

主端点从「成功率」整体换成「**可执行性**」：某条被解码到读者动作空间的条目，在该阶段是否 (i) IK 可行、(ii) 在力矩包络内、(iii) 落在成功域内。

**为什么这一层能活下来**：
- **每一帧都是一次观测**（n ~ 10⁵ 而非 10² 条 trial），完全绕开 π_d、天花板/地板、感知噪声、配对可复现性（v5 §7-R3 的可形变物问题在这里字面消失），也绕开 §4.3.2 的 τ_p。
- 主张变成**系统主张**：`一个基于 Δ𝔸 的 per-stage router 在 matched injection rate 下，admissibility 优于任何固定层级`。这对系统集成者有直接价值，且与 v5 §2.5 的「不更新参数的拒绝准则」是同一件事——注入必须在采样器中间态上生效（低置信度不注入、部分维度不注入），天然需要冻结策略 + 注入机制，**不会被「用最近邻策略就能证」打掉**。
- 增量成本 ≈ 0（复用 D1–D4 档位与已采 rollout）。

**必须诚实标注的弱点**：Δ𝔸 的输入之一就是 IK 可行性与残差，而 admissibility 的输入也是它们——**有同义反复的嫌疑**。破解：把**容差项**单独拿出来做**嵌套模型比较**（`feasibility-only` vs `feasibility + tolerance`），可证伪的内容是「容差项在可行性项之外还携带信息」。**若嵌套比较不显著，这一层也只是描述性的——这正是它是 fallback 而不是主线的原因，必须在补充材料里逐字写出来。**

**★ 但本轮有一个新的正面理由把 A 从「退路」升级为「并行交付物」**：R² = 0.14 时 router 只吃到 oracle 增益的 23.7%【继承】。**报了 oracle 上界，即使 R² 低，「逐阶段路由存在 X pp 的可得增益、当前预测量吃到其中 24%」仍是一条完整、诚实、可发表的系统结论。**

### 6.5.2 Fallback B：calibrated null

若 Δ𝔸 与所有替代预测量都不显著，论文变成**有信息量的零结果**——**但只在 MDE 足够小时才有信息量**：

> 「以预注册的 MDE = 9 pp/SD、以一个在离线上会变号的先验预测量 Δ𝔸，我们在 29 个异质阶段上未检出阶段条件化。因此在此本体对与此任务族上，**聚合数字就是答案，层级选择可以全局做，不必逐阶段做。**」

**这条只有当 §6.2.2 的 MDE 达成才成立。** 因此把设计做到「即使零结果也是结果」不是保险，是必须——它把 MDE 从技术参数变成**可发表性的前置条件**。

### 6.5.3 分支联动改写（现在就写好，不等 G6）

| 分支 | Title | Abstract | Contribution 1 | Intro ¶5 |
|---|---|---|---|---|
| E1+E2 全过 | T-A | §5.5.2 原稿 | §5.4 C1 原稿 | 「we compute ... and freeze it」 |
| E1 过、E2 不过 | T-B | 删 harm 句 | 保留符号预测 | 同上 |
| **b 过、c 不过**（Δ𝔸 = 族的改名） | T-C | 「family-level」替换「stage-level」 | **C1 撤回，改为「我们测量了族级条件化」** | 删预注册句的 novelty 语气 |
| a 不过 | T-D | 换 admissibility 口径 | 换 router 主张 | 重写 |
| 全不显著、MDE 达成 | T-E | 零结果口径，**标题带 9 pp** | 换 calibrated null | 重写 |





---

# 7. 补丁清单

按依赖排序。每行：文件 · 章节 · 改成什么 · 阻塞谁。

## 7.1 阻塞级（必须在 2026-08-31 F 冻结前完成）

| # | 文件 · 位置 | 动作 | 阻塞谁 |
|---|---|---|---|
| **1** | `v5` §1.6 #2 / §8.2 G0.6 | **FK 一致性硬验收（20 构型 <5 mm / <2°）提前到 08-28 之前**，不得与 G0.5″ 同日 | 一切。不过则 G0.5″ 连同 P5 全部作废 |
| **2** | `v5` §1.6 #3 | **腕部力/力矩或触觉通道的实测**提前到 F 冻结之前；无力通道则在 F 里写死二选一（两侧检验+力矩协变量 / 铰接族降 exploratory） | M3 反号风险、H1 方向 |
| **3** | 新建 `RAL2027/covariates/Ty_measured.csv` + 单独 sha256 | 每阶段 T_y 的**物理测量**（卡尺/CAD：拉头槽宽、detent 深度、篮口内径与倒角、腔壁余隙）+ 每个 `J_k` 非零增益的**实测几何**（铰链力臂 r、导轨曲率半径、漏斗半锥角）+ 盲引 ICC(2,k) 报告 | Δ𝔸 全部数值 |
| **4** | `RAL2027/covariates/design_stage.py` | **删除 prototype 查表赋值**，改为逐阶段调用 `admiss.py:dA(J_k, Ty_k, abstain_k)`；`Σ_e` 换成 `redteam.py` 的经验 6×6 协方差（不再各向同性）；`abstain₃` 换成 `taskspace.py` 的逐阶段弃权率（不再用全局 19.2%） | §4.3.2 的 τ_p 问题、§4.7 的族内方差 |
| **5** | `RAL2027/covariates/absorb2.py` | 保留但**加注释声明其局限**：hinge 的 `gain=1.0` 等价于未声明的 1.0 m 力臂；ζ 与 `−log min T_y` 同秩。**该脚本不再产出主端点预测量** | 反 fishing 自曝表 |
| **6** | 新建 `RAL2027/prereg/F.md` + sha256（08-31） | 阶段定义与切分规则（含全部超参）、**族定义（任务族 C/B/D/E，锁死）**、三层 N/M/B 标注表（**声明仅用于叙事**）、`Δ𝔸(k)` 与 `ζ(k)` 数值、P1″/P7′/P8/P2′/P3′/P4′/P6 方向表、**gatekeeping 顺序**、**MDE 表（τ_p ∈ {0,3,6} 三档）**、撤回条款（力臂 r 使 Δ𝔸(hinge)>0 则撤回）、留出族指定、「本文件不存在第二版本」声明 | G0.5″ |
| **7** | `v5` §8.2 Go/No-Go 表 | 插入 **F 冻结行（08-31）**；**G0.5 行整行替换为 G0.5″**（§5.3.4 四判据 + §5.3.5 判定树，0 robot-h）；**新增预 gate M1**（per-stage first-fault 分布，占比>50% 则 value 侧条件化无对象） | 09-05 |
| **8** | 施工图 §4.2「主端点」整节 | 替换为 §4.2 的 co-primary 双端点（E1 层级变号 / E2 harm 解耦）+ 次端点 S1–S5；**分析单位改阶段，聚类改族，推断改 randomization inference** | G3b 切分冻结 |

## 7.2 设计级（G3b / E0 切分冻结前，2026-10-17 之前）

| # | 文件 · 位置 | 动作 | 阻塞谁 |
|---|---|---|---|
| 9 | `v5` §6.3 任务分层 | **新增 matched-pair fixture 四对**（篮口倒角/直壁、门板铰链/自由、抽屉滑轨/无轨、拉链导槽/裸齿），预算 +19～27 robot-h（砍半版 P2+P4 = +10～13） | P8、割掉平凡性 |
| 10 | `v5` §6.3 / `design_stage.py` 的 `fam` 表 | **给刚体家电族补 zip 型阶段**（滑动闩 / 抽屉滑轨长行程）、**给 B 族补 hinge 型阶段**（包体翻盖），使 hinge 与 zip 各自出现在 ≥2 个共同族 | hinge-vs-zip 对照的可识别性（当前有效 cluster = 2） |
| 11 | `v5` §6.3 拉链族 | Z 族族内 Δ𝔸 方差可能过不了 0.5 门槛；由 #10 的 hinge 阶段补齐。**不达标不得重新划族，只能补阶段** | §4.7 硬 gate |
| 12 | `v5` §6.6 预算表 | 更新为 §4.8：EVAL 94.2 + matched-pair 19～27 + E3 1.5 = **≈123（砍半）～144.5（全量）robot-h**，仍在 baseline 150 内；布料 exploratory 11.0 h 可延后抵账 | 排期 |
| 13 | `v5` §6.6 / 新增 arm | **stage-targeted injection 从「识别性补强」升为 HR 的唯一合法来源**：8 阶段 × 20 对 × 2 方向 = 7.5 robot-h；选阶段规则写进 F（谱两端各 2 + 中位 2 + mode-boundary 高危 2） | 主端点 E2 |
| 14 | 施工图 §4.6 指标定义式 | 追加 `CP_k`（非条件化累积推进）、`dA_k`、`u_perp_k`、`HR_k`（**stage-targeted 口径**）四行；原有 SR/Delta/IR/AR/HR/TR 六行中 HR 一行重写 | 全表执行 |
| 15 | 施工图 §4.0 表图映射 | Fig. 4 改为 **per-stage ΔCP vs Δ𝔸 散点 + 族内回归线 + 符号翻转带**（按 Δ𝔸 排序，不按任务名）；新增 Fig. 4b = matched-pair 对内 contrast；Fig. 5 oracle 阶梯改 per-stage | G6 |
| 16 | 施工图 §4.5 P1–P4 检验方式表 | 整表替换为 §5.2 的八行预测汇总表 | — |
| 17 | `v5` §6.8 修法 1 | 主端点从「刚体/可形变两个 Bonferroni 端点」改为 §4.5 的**固定顺序 gatekeeping**；刚体/可形变的拆分下沉为 family 固定效应 | 多重比较预算 |
| 18 | `v5` §6.7 轨 A | 保留不动，但**分段脚本与全部超参必须进 F 的 hash** | 反 fishing |

## 7.3 写作级（09-08 arXiv 占位之前）

| # | 文件 · 位置 | 动作 |
|---|---|---|
| 19 | 施工图 §0.1 Title 表（T1/T2/T3 + 决策规则） | 替换为 §5.5.1 的 T-A～T-E 五候选与新决策规则；**T-E 的分辨率数字必须是 9 pp（τ_p=6 档），不得用 4.8** |
| 20 | 施工图 §0.2 Abstract（约 195 词） | 替换为 §5.5.2 新稿（约 215 词）。**删除任何 "spans two orders of magnitude" 措辞** |
| 21 | 施工图 §0.3 故事线第 2、3 句 | 替换为 §5.5.3 一句话叙事的对应展开 |
| 22 | 施工图 §0.4 四条 Contribution + do-not-claim 段 | 整体替换为 §5.4。**do-not-claim 新增三条弃权：RoboMME 方法论、R-t-S 阶段评分格式、「紧的差」这一定性关系本身** |
| 23 | `v5` §2.4 叙事一句话 | 替换为 §5.5.3 |
| 24 | `v5` §2.3 后半 + 施工图 §3.4 对应句 | 替换为 §5.7 的英文边界声明。**删除 Fisher exact p=0.55/0.42 那句**（p 值不得当武器） |
| 25 | `v5` §2.5 fallback framing | 被 §6.5.1 Fallback A 完全吸收并升级为 level-router + 并行交付物；其下新增 Fallback B（calibrated null） |
| 26 | `v5` §3.1 SQ1/SQ2/SQ3 整节 | 替换为 §5.1 的 SQ1″/SQ2′/SQ3′ |
| 27 | `v5` §3.2 P1′ | 替换为 P1″（ℓ* 是阶段的函数且会变号） |
| 28 | `v5` §3.6 预测汇总表 | 替换为 §5.2 八行表（新增 P7′ 升 headline、P8 matched-pair） |
| 29 | `v5` §7-R1（交叉点不存在）、§7-R4（谱系压平） | 两节合并替换为 §6.2 + §6.3（含「交互比主效应更难测」的反向论证及其**条件性**反驳） |
| 30 | `v5` §8.3 MVP 12 条 | 第 4 条「P1′ + G0.5 交叉点 gate」替换为「**P1″ + G0.5″ 四判据 + stage-targeted 8×20 + matched-pair 砍半版 2 对**」 |
| 31 | `threat_RAM_RoboOS.md` | **新增登记 arXiv 2605.30695**（*Primitive Subspaces Mediate Few-Shot Transfer in VLAs*, 2026-05-29, OpenVLA + π0.5 + REASSEMBLE；primitive 训练 m=3 达微调上界 78% vs flat 需 m=10；子空间消融 −32 pp）。**非跨本体、非冻结+记忆，不抢主线，但证明「按 primitive 切分解释迁移」已是活跃可发表框架，必须登记。** 它还报告了 chunked policy 评测中 single-step action-range gate 的 family-wise inflation 坑，与本文自动判据审计相关 |

## 7.4 root.tex 补丁（LaTeX 正文，按行号）

| # | root.tex 位置 | 动作 |
|---|---|---|
| 32 | `\section{Introduction}` (L101) ¶5 | 预注册句改为「we compute that ranking from measured geometry, freeze it with its retraction conditions, and only then run anything」；删除任何「first / novel / unexplored」 |
| 33 | `\subsection{Memory Written As Explicit Entries}` (L260) | 插入 §5.6.1 的 RoboMME 对齐段（英文成稿）与 §5.7 的 R-t-S 边界段（英文成稿），替换现有对应措辞 |
| 34 | `\subsection{Readout: One Interface, Four Levels}` (L463) | 标题改为 **Readout: One Interface, Two Confirmatory Levels**；正文显式声明「confirmatory 只跑 ③ 与 ④，①② 为 exploratory」；补 R-t-S component-aware aggregation 允许 joint-angle increments 的脚注（§5.7 末） |
| 35 | `\section{Experimental Setup}` (L592) | 加入 stage 定义与切分规则、matched-pair fixture 描述、stage-targeted arm 描述、**「主端点与次端点的条件化立场为何不同」的显式说明**（§4.4.3-3） |
| 36 | `\subsection{The Transferability Spectrum}` (L672) | 整节重写为 per-stage 版：Fig. 4 散点 + 符号翻转带；**明确写出「我们只能检验符号与三分位，不能检验连续尺度」及其 MDE** |
| 37 | `\subsection{Sharing, Scale, and Harm}` (L722) | harm 部分前置并扩写为主端点 E2；报 `β_h` 与 `δ`（检索置信度）二者，写出 key/value 解耦的双支结论 |
| 38 | `\subsection{Where the Loss Goes}` (L684) | oracle 阶梯改 per-stage；加 `Δ_limit`/`Δ_geom` 拆分与 A8 coordination-oracle 第四桶 |
| 39 | `\section{Conclusions and Limitations}` (L798) | 新增三条 limitation：(a) partial R² ≈ 0.14 是设计的必然产物；(b) `A_ℓ` 是运动学代理，秩相关校准见 G2a；(c) 约束吸收依赖柔顺预算，力矩 p95/abort 比值并报 |
| 40 | `paper_src/refs.bib` | 新增：RoboCasa (RSS 2024)、Borràs T-RO 2020、Paulius IROS 2019 + RSS 2020、Suomalainen RAS 2022、Krebs & Asfour RA-L 2022、GAPartNet CVPR 2023、Kroemer JMLR 2021、Mason TSMC 1981、Bruyninckx & De Schutter T-RA 1996、Ureche T-RO 2015、Moakher SIMAX 2002、Pennec JMIV 2006、Park JMD 1995、VFD (2606.18043)、DVAC (2606.03847)、扰动式 (2606.20754)、Primitive Subspaces (2605.30695)。**所有 DOI 已 Crossref 核实【继承】；arXiv preprint 一律标 preprint，不得写 venue（RoboMME 的 ICML 26、R-t-S 的 venue 均【待确认】）** |

## 7.5 明确**不动**的部分（防止修订过度）

- v5 §1.1–1.5 硬件与数据条件、§4.7 条目 schema（RDT-1B 128 维布局）、§5.1–5.9 基座与训练方案（π0.5 + LoRA + openpi-agilex）、§5.6 写入门控（VLAC）、§5.8 三份切分与硬规则、§6.2 embodiment-distance 阶梯 D1–D6、§6.9 力矩 abort 判据：**全部保留，本重构不触碰**。
- 施工图 §0.5 页数预算表、§1.0 写作红线、§2.4 Table I、§3.1–3.3 方法节结构、§3.9 工程清单：**保留**。
- P5（层④←架构、层③←限位）与其三条一手证据：**保留不动**，它是全文唯一已成立的定量结论。

---

## 附：本提案引用的一手复算清单（可复现）

| 断言 | 脚本 | 本轮状态 |
|---|---|---|
| ζ vs −log min T_y：Spearman 1.000 / log-log Pearson 0.990 | `covariates/absorb2.py` + 追加相关计算 | **复算** |
| ζ_hinge 对力臂 r：1.0/0.8/0.35/0.2/0.12 m → 0.294/0.367/0.839/1.468/2.447 | `covariates/admiss.py` | **复算** |
| Δ𝔸 与朴素量 Spearman = −0.257；倒 U 峰在 12 mm（+0.543）；≥60 mm 变号（−0.051→−0.192） | `covariates/admiss.py`（本轮新建） | **复算** |
| confirmatory 阶段数 29（C9+B6+D7+E7），族内 log ζ 方差占比 0.879 | `covariates/design_stage.py` | **复算** |
| corr(log ζ, 二值 \| family FE) = −0.903，R²=0.816；1/c 24.62→4.53；MDE 膨胀 2.33× | 本轮追加计算 | **复算** |
| prototype 随机截距：τ_p=0/2/4/6/8 → n_eff 24.3/19.1/11.8/7.1/4.6 | 本轮追加仿真（4000 次） | **复算** |
| n=6 精确置换：单侧 5% 临界 Spearman = 0.771，min p = 1/720 | 本轮追加（720 全排列） | **复算** |
| G=4 wild cluster bootstrap min p = 1/2⁴ = 0.0625 | 解析 | **复算** |
| E1 形状恢复 ρ 0.98/0.95/0.91/0.83/0.68；E2 n=400 达 3% 误差 | `tol3.py` `tol4.py` `tol5.py` | 继承 |
| SO(3)：不取商 90.1° vs 取商 5.3°；Fréchet vs 切空间特征谱 | `so3.py` | 继承 |
| twist-PCA 有效秩对 ρ 敏感（free 档 2.82→0.01） | `absorb.py` | 继承 |
| MDE 表 6.0/3.4/2.2/18.0 pp/SD；R² 表；router 捕获率表；analyst-freedom FPR 表 | `pow2.py` + 前序审查 | 继承 |
| 层④标定阶梯 82.8°/52.4°/17.8°；层③限位归因 80.8%→100.0%；双臂 77.6%/93.6% | `/tmp/agxurdf/redteam.py` `redteam2.py` `taskspace.py` | v5 已有 |
