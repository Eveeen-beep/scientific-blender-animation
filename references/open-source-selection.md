# Blender 开源项目选型与研究快照

核查日期：**2026-11-02**。范围是 9 个 GitHub 代表项目，另补 2 个 Blender 官方生产工具；不是 GitHub 全量调查。以维护者仓库、许可文件、发行说明、源码/示例和官方文档为依据，不按 stars 排名。

**本轮没有安装或执行这些项目；以下兼容性是上游声明/源码观察，不是本机 Blender 5.2 实测通过。** 固定 tag/commit 是取证锚点，不是永远推荐的安装版本。主分支条目未取得固定 SHA 时明确标注，实际采用前重新核查版本及许可。

## 按任务选择，而不是按热度装插件

| 任务缺口 | 先采用的方法 | 候选与采用等级 |
|---|---|---|
| 连接 Blender、读场景、局部自动化 | 现有连接或原生 bpy | MCP for Blender：可选桥接，不是必需品 |
| 装置、路径、截面、复杂参数几何 | 原生 Curve/GN/bpy，模块化接口 | Sverchok：复杂几何时隔离试用 |
| 蜂窝、晶格、多孔/曲面单元 | 载体＋组件＋分布场，先小样 | Tissue：领域可选 |
| 分子/蛋白/MD/密度轨迹 | 原数据→属性/时间→显示样式 | MolecularNodes：领域优先候选 |
| CFD/温度等 VTK 结果 | 科学处理链→缓存几何/体数据→显示 | BVTKNodes：版本敏感，先隔离；也可用已验证 VTK/ParaView 导出 |
| 复杂程序化运动 | 公共时间输入、阶段/插值分离 | Animation Nodes：优先借鉴，已有 AN 工程再评估迁移 |
| 合成训练数据、多相机、深度/标签 | 数据、相机、输出通道分层 | BlenderProc / BlenderSynth：专项候选，非普通汇报片默认框架 |
| HDRI/纹理与资产复用 | 记录来源、许可、尺度、分辨率 | Poly Haven Assets：素材/管理方法可用，插件可选 |
| 长序列、多机器渲染 | 冻结输入、任务依赖、状态与补帧 | Flamenco：有调度需求才部署 |
| 多人/多镜头资产制作 | 数据所有权、试验/发布分层 | Blender Studio Pipeline：先借鉴，不照搬整套平台 |

上述采用等级是本工作流根据任务匹配与接入成本的判断，不是各项目的官方评价。

## 项目证据与可吸收部分

### 1. MCP for Blender：连接与受控读写

- [仓库](https://github.com/ahujasid/mcp-for-blender)，原 `ahujasid/blender-mcp`；第三方项目。固定源码 `992233bb258975a05eec8b5691465c50c2831e34`（2026-10-29），[pyproject](https://github.com/ahujasid/mcp-for-blender/blob/992233bb258975a05eec8b5691465c50c2831e34/pyproject.toml) 为2.2.6、Python>=3.10；[MIT许可](https://github.com/ahujasid/mcp-for-blender/blob/992233bb258975a05eec8b5691465c50c2831e34/LICENSE)。[addon](https://github.com/ahujasid/mcp-for-blender/blob/992233bb258975a05eec8b5691465c50c2831e34/addon.py) 最低 Blender3.0 声明不等于5.2全功能验证；该交互服务器不在 `-b` 中启动。
- 学习：连接适配与创作代码分离；读取状态→小操作→读回/视觉核验。已有稳定 bpy/CLI 不必换成 MCP。
- 所选源码的[条款](https://github.com/ahujasid/mcp-for-blender/blob/992233bb258975a05eec8b5691465c50c2831e34/TERMS_AND_CONDITIONS.md)中内容遥测为 opt-in，最小使用统计另行处理，`DISABLE_TELEMETRY=true` 可关闭全部遥测；旧搜索摘要“默认开启”不适用于这个快照。[SAFE_MODE 源码](https://github.com/ahujasid/mcp-for-blender/blob/992233bb258975a05eec8b5691465c50c2831e34/src/blender_mcp/safe_mode.py)明确不是 Blender 沙箱。接入时核查所选版本的执行、socket和数据外发边界。

### 2. BlenderProc：模块化生成与科学诊断输出

- [仓库](https://github.com/DLR-RM/BlenderProc)，[GPLv3](https://github.com/DLR-RM/BlenderProc/blob/main/LICENSE)；源码锚点 `76bd8b82ee19489843578ff045298642197bf883`（2026-01-07）。[安装实现](https://github.com/DLR-RM/BlenderProc/blob/76bd8b82ee19489843578ff045298642197bf883/blenderproc/python/utility/InstallUtility.py)默认选择 Blender4.2.1；支持自定义路径不证明5.2兼容。
- 阅读[基本示例](https://github.com/DLR-RM/BlenderProc/blob/76bd8b82ee19489843578ff045298642197bf883/examples/basics/basic/main.py)：输入、导入、相机位姿、渲染、写出分离。可学相机坐标、标注/深度与画面分离、受控批处理；训练数据随机化不应混入冻结的科研叙事。
- **接入边界**：[Initializer](https://github.com/DLR-RM/BlenderProc/blob/76bd8b82ee19489843578ff045298642197bf883/blenderproc/python/utility/Initializer.py) 的 `init(clean_up_scene=True)` 默认清场并设置 Cycles；关闭清场也仍会重设其他属性。不要在稳定 Eevee 工程直接运行示例初始化。先借鉴组织方式，实际依赖仅在独立项目/副本测试。

### 3. MolecularNodes：科学数据和视觉表示分离

- [仓库](https://github.com/BradyAJohnston/MolecularNodes)，[v520.0.0 / 69711f5](https://github.com/BradyAJohnston/MolecularNodes/releases/tag/v520.0.0)。[该tag配置](https://github.com/BradyAJohnston/MolecularNodes/blob/v520.0.0/pyproject.toml)对应 Python3.13、bpy5.2；[许可](https://github.com/BradyAJohnston/MolecularNodes/blob/main/LICENSE)为GPL-3.0-or-later。核查时 main 配置520.3.0；README入口描述>=4.2不能替代具体发行要求。
- 阅读[分子对象实现](https://github.com/BradyAJohnston/MolecularNodes/blob/main/molecularnodes/entities/molecule/base.py)：原始拓扑/轨迹、帧管理、selection属性和GN样式分层。该发行还改变了内部显示尺度，升级应核对单位。实现按引擎能力选球体表示，可借鉴为“保持引擎，检查等价表示”，而不是偷偷切换引擎。
- 适合分子、MD、蛋白与EM题材；不作为工程装置默认依赖。插件运行和原模拟有效性是两项检查，导入数据的许可也独立记录。

### 4. Sverchok：路径、截面与姿态解耦

- [仓库](https://github.com/nortikin/sverchok)，[v1.4.0 / dd435d7](https://github.com/nortikin/sverchok/releases/tag/v1.4.0)声明 Blender3.6–5.1，[tag许可](https://github.com/nortikin/sverchok/blob/v1.4.0/LICENSE)GPLv3；本次未确认5.2实测。
- [NURBS Sweep文档](https://github.com/nortikin/sverchok/blob/master/docs/nodes/surface/nurbs_sweep.rst)及[实现](https://github.com/nortikin/sverchok/blob/master/nodes/surface/nurbs_sweep.py)把截面、路径和姿态算法分开；零曲率、拐点与闭环处可能翻转或扭转。吸收其接口组织和姿态审核，而非只看轨迹中心线。
- 复杂参数曲面可选；简单环道继续原生方式。SciPy、geomdl、FreeCAD等依赖只在实际节点需要时考虑。

### 5. Tissue：载体与重复单元

- [仓库](https://github.com/alessandro-zomparelli/tissue)，[v0-3-75 / d2e8393](https://github.com/alessandro-zomparelli/tissue/releases/tag/v0-3-75)；[tag manifest](https://github.com/alessandro-zomparelli/tissue/blob/v0-3-75/blender_manifest.toml)最低4.5、GPL-2.0-or-later。发布者列出的加载测试为4.5.10和5.1。核查时开发分支0.3.76 manifest为GPL-3.0-or-later，不能混用版本许可信息。
- 阅读[tessellate_numpy](https://github.com/alessandro-zomparelli/tissue/blob/master/tessellate_numpy.py)：生成器、组件、厚度、法向、权重和seed独立。适合多孔材料/晶格/曲面重复单元；可借鉴“载体＋组件＋分布场”的原生模块。
- 生成不等于可制造或力学验证。[配置](https://github.com/alessandro-zomparelli/tissue/blob/master/config.py)涉及可选加速依赖；不为加速未经检查重装共享 Blender Python。

### 6. BVTKNodes：科学场数据到展示的桥接

- [仓库](https://github.com/tkeskita/BVtkNodes)，[GPLv3](https://github.com/tkeskita/BVtkNodes/blob/master/LICENSE)；未取得本次固定发行锚点。[官方文档](https://github.com/tkeskita/BVtkNodes/blob/master/docs/BVTKNodes.rst)列 Blender4.2/3.6与VTK9.2.6；[元数据](https://github.com/tkeskita/BVtkNodes/blob/master/__init__.py)0.11、最低3.3、Experimental。维护者明确提示版本敏感及崩溃风险。
- 文档 head.vti 示例：Reader→ContourFilter→VTK To Blender Mesh，配合Time Selector。可借鉴字段/阈值/时间过滤与Blender样式分离，记录科学处理链。
- 当前5.2工程不直接加入。确需VTK数据先隔离验证，或使用已验证的VTK/ParaView转换路径；转换后仍查单位、字段与时间，不默认转换保真。

### 7. Animation Nodes：时间、插值与模块分开

- [仓库](https://github.com/JacquesLucke/animation_nodes)，[GPL-3.0-or-later](https://github.com/JacquesLucke/animation_nodes/blob/master/license.txt)。[v2.3发行](https://github.com/JacquesLucke/animation_nodes/releases)面向4.2 LTS；[提交记录](https://github.com/JacquesLucke/animation_nodes/commits)含5.0 API更新及2026维护，不能称已停更，但也不能据此宣称5.2稳定构建已验证。
- 阅读[time_info](https://github.com/JacquesLucke/animation_nodes/blob/master/animation_nodes/nodes/animation/time_info.py)：从Scene读实际帧与fps/fps_base。吸收统一时间输入、delay/repeat、插值、falloff和子程序组合。
- 新科研任务可用原生Keyframe/GN/bpy实现该模式；已有AN工程须检查其编译组件与Blender/Python版本，不原地升级。

### 8. BlenderSynth：同场景多视图与诊断通道

- [仓库](https://github.com/OllieBoyne/BlenderSynth)，[MIT](https://github.com/OllieBoyne/BlenderSynth/blob/main/LICENSE)。[官方文档](https://www.ollieboyne.com/BlenderSynth/)声明支持Blender3/4、Beta；5.2未验证。[PyPI](https://pypi.org/project/blendersynth/)0.3.3与核查时[setup.py](https://github.com/OllieBoyne/BlenderSynth/blob/main/setup.py)0.3.2不同，实际采用固定发布包/commit，不混合判断。
- 阅读[快速开始](https://www.ollieboyne.com/BlenderSynth/python/quickstart.html)与[多视图示例](https://www.ollieboyne.com/BlenderSynth/python/multiview_rendering.html)：同场景相机列表、RGB、法线AOV及标注分别组织。可借鉴诊断输出/遮挡mask，不改变beauty画面。
- 需要合成数据才考虑完整框架；示例Cycles/多进程配置不能直接覆盖用户冻结设置。深度/法线等数值通道不要套显示色彩变换。

### 9. Poly Haven Assets：按需资产库与来源记录

- [仓库](https://github.com/Poly-Haven/polyhavenassets)，[插件GPLv3](https://github.com/Poly-Haven/polyhavenassets/blob/main/LICENSE)；[元数据](https://github.com/Poly-Haven/polyhavenassets/blob/main/__init__.py)1.2.3、最低4.5，本次是未固定SHA的主分支快照，不是5.2实测。
- 阅读[获取实现](https://github.com/Poly-Haven/polyhavenassets/blob/main/operators/pull_from_polyhaven.py)：资产库路径检查、类别/catalog、按需获取和进度。学习来源ID、真实尺度、纹理分辨率与依赖管理；不默认下载整库。
- [资产CC0说明及API项目](https://github.com/Poly-Haven/Public-API)与[在线服务条款](https://github.com/Poly-Haven/Public-API/blob/master/ToS.md)是独立层次，不能把资产许可套到插件/API服务或其他素材。关键科研结构仍以研究数据为准。

### 10. Flamenco：有依赖的渲染任务

- 官方补充源：[源码](https://projects.blender.org/studio/flamenco)，非GitHub主托管，GPL-3.0-or-later。源码锚点`76806d0d6a08fa70d02a4933220f4fbce59864c5`；[插件元数据](https://projects.blender.org/studio/flamenco/src/commit/76806d0d6a08fa70d02a4933220f4fbce59864c5/addon/flamenco/__init__.py)最低3.1，主分支3.10-beta2明确非稳定；不应当作生产默认。
- 阅读[simple_blender_render.js](https://projects.blender.org/studio/flamenco/src/commit/76806d0d6a08fa70d02a4933220f4fbce59864c5/internal/manager/job_compilers/scripts/simple_blender_render.js)和[任务文档](https://flamenco.blender.org/usage/job-types/builtin/)：分块渲染→全部任务完成依赖→FFmpeg。吸收任务图、独立状态与恢复。
- 不覆盖已有文件仍不足以证明PNG有效/同源；保留本skill的完整解码与provenance门槛。有状态模拟先缓存，worker环境/路径一致后才可分发。单机短片不必部署农场。

### 11. Blender Studio Pipeline：数据归属与发布

- 官方补充源：[工具站](https://studio.blender.org/tools/)、[源码入口](https://projects.blender.org/studio/blender-studio-pipeline)。本次源码站访问受限，依据官方文档，**不声称已审源码**。[总览](https://studio.blender.org/tools/pipeline-overview/introduction)说明GPLv2或更高，实际子组件还需逐项确认；没有统一5.2适配保证。
- 阅读[Asset Pipeline](https://studio.blender.org/tools/addons/asset_pipeline)：task layers区分model/rig/shading所有权，发布分Sandbox/Staged/Active。科研短片可采用“设备/机理/展示/语言/输出”改动边界与试验/冻结版区分。
- 不把整套团队平台加进单人工作流；跨镜头/多人确有共享需求时再考虑linked assets/overrides，并验证依赖可交付。

## 实际引入前的最小门槛

1. 记录目标任务缺口与为什么原生方法不足；“源码值得学习”不自动意味着“必须安装”。
2. 固定所用版本/哈希，核对release、manifest、安装代码及依赖；声明、源码观察、本机测试分别记录。矛盾未澄清就写未核验，不宣称支持。
3. 看清初始化/示例是否清场、改引擎、替换World/相机、下载外部内容、安装依赖或执行任意代码。不要以调研为由运行一键安装/示例。
4. 实际采用时先隔离最小样例：单位/字段正确→保存重开→代表帧/短动态→重现与缓存→冻结内容保持。只测试本项目需要的能力，不把一个成功立方体当成全功能通过。
5. 区分创作期与渲染期依赖，保留可编辑源与派生缓存/导出关系；填写[外部组件采用记录](../assets/EXTERNAL_COMPONENT_RECORD.md)。新项目的Blender版本由任务决定，不为不兼容插件原地降级稳定工程。

具体实施模式见[可复用方法](open-source-patterns.md)。该研究快照只负责选型，后续使用时重新核查变化部分。
