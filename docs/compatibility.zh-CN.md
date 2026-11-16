# 平台兼容性与验证范围

文档核对日期：**2026-11-16**。本页说明同一份技能包如何被不同 agent 发现，以及现有证据能支持什么结论。安装步骤见 [Codex](install-codex.zh-CN.md)、[Claude Code](install-claude-code.zh-CN.md) 和 [Cursor](install-cursor.zh-CN.md)。第一次使用可从[新手入门](getting-started.zh-CN.md)开始。

## 先看结论

这是一份以 `SKILL.md` 为入口的科研 Blender 工作流，包含参考文档、模板和两个辅助脚本。**共享技能格式不等于共享执行环境，也不等于各平台已完成动画制作验证。**

| 平台 | 已有证据 | 可以据此判断 | 尚不能据此判断 |
|---|---|---|---|
| Codex 本地工作流 | 有科研动画项目实践，公开部分为[匿名项目复盘](../references/ring-project-retrospective.md)；本轮检查范围另列于下文 | 工作流有具体制作与恢复经验来源 | v1.2 已在所有 Codex 环境中重新完成全流程验收 |
| Claude Code | 核对官方 `SKILL.md` 格式、发现目录与调用方法 | 可按官方约定准备技能目录，作为待实测的使用入口 | 已在 Claude Code 内安装、发现或触发本技能，已连接 Blender 或完成渲染 |
| Cursor | 核对官方 `SKILL.md` 格式、发现目录与调用方法 | 可按官方约定准备技能目录，作为待实测的使用入口 | 已在 Cursor 内安装、发现或触发本技能，已连接 Blender 或完成渲染 |

Claude Code 与 Cursor **尚无本仓库的产品内实测记录**，因此这里不使用“已全面支持”“开箱即用”或“兼容性良好”作为结论。平台安装文档提供的是根据官方文档整理的操作路线，用户仍需完成本机自检。

## 把证据分开记录

| 证据层次 | 实际检查内容 | 证明范围 |
|---|---|---|
| 官方文档核对 | 技能文件格式、目录约定、调用入口 | 格式与安装说明有官方依据；不能证明本技能已被目标产品加载 |
| 技能包和普通 Python 检查 | 元数据、本地链接、脚本参数、临时 PNG 与来源凭据等 | 对应文件和脚本行为；不能证明宿主发现、权限或 Blender 连接正常 |
| Blender 最小只读自检 | 在实际 Blender 中读取版本与场景摘要，写入独立 JSON 报告 | 本次运行能执行所用 API 和读取该场景；不能证明建模、动画求值、渲染或科学性通过 |
| 宿主产品内实测 | 在指定产品和版本中安装、发现并调用技能，再取得真实 Blender 返回 | 被记录的产品、工具和具体操作可用；不能外推到其他产品或版本 |
| 项目制作与验收 | 具体工程的建模、动态、序列、视频和人工检查记录 | 该项目、版本和已登记范围；不能替代新项目验收 |

**本次 v1.2 的检查范围仅为技能包单元检查、脚本审核及 Blender 5.2 最小只读运行自检，不包含重新制作并验收一部完整科研动画。** 实际执行环境、结果与未执行项以[测试说明](../tests/README.md)中的记录为准；没有执行记录的项目不按通过处理。

Codex 的历史项目经验与本次检查是两份证据。复盘中的时长、分辨率、帧数、双语输出及历史验收状态属于原案例，不是 v1.2 的新测试结果，也不是所有新任务的默认规格。

## 官方目录与调用入口

下表中的 `~` 表示用户主目录，`<项目>` 表示正在使用的项目目录。目录下还应有完整的 `scientific-blender-animation/` 文件夹，其内直接包含 `SKILL.md`。

| 平台 | 用户级目录 | 项目级目录 | 显式调用方式 | 官方依据 |
|---|---|---|---|---|
| Codex | `~/.agents/skills/` | `<项目>/.agents/skills/` | 在支持的技能选择器选择技能，或输入 `$scientific-blender-animation` | [Build skills](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code | `~/.claude/skills/` | `<项目>/.claude/skills/` | 输入 `/scientific-blender-animation` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Cursor | `~/.cursor/skills/`；官方也列出 `~/.agents/skills/` | `<项目>/.cursor/skills/` 或 `<项目>/.agents/skills/` | 在 Agent 聊天中输入 `/` 并选择技能 | [Cursor Agent Skills](https://cursor.com/docs/skills) |

技能主体采用 [Agent Skills 规范](https://agentskills.io/specification)中的 YAML frontmatter 与 Markdown 正文，参考文件、模板和脚本通过相对路径保留在包内。安装时复制完整目录；只复制 `SKILL.md` 会丢失工作流引用的材料。

`agents/openai.yaml` 是 OpenAI 宿主使用的可选元数据；本仓库用它提供显示名称、简介与默认提示词。它不是通用 Blender 连接配置。Claude Code、Cursor 等其他宿主可忽略此文件，不能据此推定它们采用相同 UI、调用策略或工具配置。依据见 [OpenAI 技能文档](https://learn.chatgpt.com/docs/build-skills)。

上表针对本地使用。远程、云端、容器和受组织策略管理的环境可能具有独立目录与权限；本机放入文件不等于远程环境已经收到技能或能够访问本机 Blender。

## 真正执行任务需要什么

| 组件或能力 | 要求 |
|---|---|
| Agent 的文件工具 | 能读取技能与项目材料，能在指定项目目录保存脚本、报告和交接记录 |
| Agent 的命令执行能力 | 能运行当前任务所需的本地程序；仅能聊天的环境无法直接完成建模与渲染 |
| Blender 执行通路 | 可用的 Blender 自带 Python `bpy` / CLI，或已配置且能实际调用的 Blender 连接器 / MCP；选可用的一条即可 |
| 普通 Python + Pillow | 运行 `scripts/sequence_audit.py` 审核 PNG 时需要；Blender 工程摘要由 Blender 内的 `bpy` 执行 |
| FFmpeg | 选用；需要视频编码、解码或检测时按任务配置，也可使用经验证的 Blender VSE 路线 |
| 其他领域插件、素材与服务 | 按具体缺口选择、记录版本与许可，并在独立小样中验证 |

能读写文件并不代表能控制 Blender；能列出 MCP 名称也不代表连接成功。只读握手应实际返回 Blender 版本、目标工程完整路径（或明确的新建未保存场景）、Scene、Camera、当前帧、时间轴和对象摘要。

普通 Python 环境没有 `bpy` 通常是执行位置不对；应由 Blender 的 Python 运行工程检查脚本。不要为了通过检查，在系统 Python 中随意安装同名包。文件工具、命令权限、Blender 和连接服务需要分别检查。

本技能包**不包含 Blender 软件、agent 产品或 API 账号、外部插件、科研数据、模型素材和最终动画**，也不提供点击一次就能自动完成任意科研动画的程序。技能指导 agent 组织工作，实际输出仍取决于研究材料、执行工具和逐阶段检查。

## 操作系统与 Blender 版本的边界

普通 Python 单元检查若在 Windows 和 Ubuntu 的 CI 中运行，仅说明登记的脚本检查在对应 CI 环境中的结果。**这不等于 Blender 在 Windows / Linux 均已连接、建模或渲染通过。** 应查看实际运行记录，而不是由 CI 配置文件推定通过。

一次 Blender 5.2 最小只读自检也不构成其他 Blender 版本、macOS、不同 GPU / 驱动、全部引擎或第三方插件的兼容性保证。实际项目须记录 Blender 完整版本、操作系统、引擎和必要外部组件，并检查真实工程的代表状态。

`inspect_blend.py` 不保存工程、不渲染、不扫描整段动画。使用 `--disable-autoexec` 读取时，依赖 Python 的驱动或处理器还可能被禁用；摘要成功不能证明动态求值正确。`sequence_audit.py` 检查 PNG 结构与用户提供的来源凭据，不能独立证明来源真实性或视觉、科学性通过。详见[连接与恢复](../references/connection-and-recovery.md)及[渲染与交付](../references/render-and-delivery.md)。

## 换 agent 或恢复项目

新项目默认使用 `PROJECT_HANDOFF.md` 记录可靠工程、已执行脚本、已完成检查、待做工作和下一步。已有项目若使用 `CODEX_HANDOFF.md`，继续沿用该文件，并把路径告诉接手的 agent；不必为了换平台另建一份相互冲突的交接记录。

接手时先只读核对磁盘文件、活动渲染、日志与交接内容。脚本“已写好”、脚本“已执行成功”、工程“已保存”和画面“已审核”分别记录；换 agent 不会自动补齐缺失证据。完整恢复提示见[新手入门](getting-started.zh-CN.md)。
