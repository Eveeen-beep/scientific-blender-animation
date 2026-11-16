# 在 Codex 中安装和使用

这份教程适合第一次安装 skill、希望用中文指令制作 Blender 科研动画的用户。安装过程可以用资源管理器或 Finder 完成，不要求自己编写 Python。Codex 会按任务编写或调用脚本；实际操作仍取决于本地 Blender、工具连接和宿主权限。

**核对日期：2026-11-16。** 本项目有 Codex 本地项目实践；这里的新安装目录依据当前官方文档整理，尚未完成新版 Codex 在全部平台上的端到端验证。跨产品边界见[兼容性说明](compatibility.zh-CN.md)，完整工作顺序见[新手入门](getting-started.zh-CN.md)。

## 1. 准备环境

1. 准备一个已安装、已登录且能打开本地项目的 Codex 环境。宿主的安装和登录按 [Codex 官方入口](https://developers.openai.com/codex/)完成；本教程从“能在 Codex 中发消息”开始。
2. 从 [Blender 官网](https://www.blender.org/download/)安装适合自己系统的 Blender，先手动打开一次，确认能看到默认场景。记下版本；不必为了安装 skill 更换已有工程使用的版本。
3. 在自己的文件夹中新建一个动画项目目录，例如“文档/Blender动画练习”。在 Codex 中打开或选择这个目录，让它成为本次工作的本地项目。
4. 确认 Codex 可以读取该目录，并可按宿主规则申请或使用执行命令、写项目文件的权限。skill 不会绕过这些限制，也不自动获得 Blender 控制能力。

不必先安装 MCP。已有合适连接器时可以使用；没有连接器时，也可由宿主通过本机 Blender 执行脚本或命令。只装普通 Python 不能代替 Blender，`bpy` 通常要在 Blender 自带的 Python 环境中运行。

## 2. 下载完整 skill 文件夹

1. 打开 [scientific-blender-animation 仓库](https://github.com/Eveeen-beep/scientific-blender-animation)。
2. 点击绿色 **Code** 按钮，再点击 **Download ZIP**。
3. 在下载目录找到 ZIP，使用“全部解压缩”或系统解压工具解压。不要直接在压缩包预览中复制单个文件。
4. 找到**直接包含 `SKILL.md`** 的那一层文件夹。默认分支下载的名称通常是 `scientific-blender-animation-main`；将这一层重命名为 `scientific-blender-animation`。
5. 检查同一层至少还有 `references`、`scripts`、`assets`，随后复制**整个文件夹**。不要只复制 `SKILL.md`，也不要把所有文件散放到 `skills` 目录。

解压工具有时会额外套一层同名文件夹。安装后正确关系是 `skills/scientific-blender-animation/SKILL.md`，中间不应再出现一层 `scientific-blender-animation-main`。

## 3. 放入 Codex 的 skill 目录

### 个人安装：本机多个项目可用

当前官方本地个人目录为：

```text
~/.agents/skills/scientific-blender-animation/
```

这里的 `~` 表示**当前用户的主目录**，不是要求创建一个名为 `~` 的文件夹。[Codex 官方 Skills 文档](https://learn.chatgpt.com/docs/build-skills)说明了个人和仓库目录的发现规则。

**Windows：**

1. 打开资源管理器，在地址栏输入 `%USERPROFILE%` 并按回车。这会进入你自己的用户文件夹。
2. 在其中新建 `.agents` 文件夹，再进入它新建 `skills`。已有这些文件夹时直接使用，保留原有内容。
3. 把上一步复制的整个 `scientific-blender-animation` 文件夹粘贴到 `skills` 内。
4. 进入该文件夹，确认可直接看到 `SKILL.md`、`references`、`scripts`、`assets`。

最终层级应为：

```text
你的用户主目录/
  .agents/
    skills/
      scientific-blender-animation/
        SKILL.md
        references/
        scripts/
        assets/
```

**macOS / Linux：** 在主目录下准备 `.agents/skills`，再粘贴整个 skill 文件夹。macOS 可在 Finder 按 `Command+Shift+G`，输入 `~/.agents/skills`；以点开头的目录可能被隐藏，可按 `Command+Shift+.` 切换显示。若目录不存在，或 Finder 不允许创建点开头的名称，可先在本地 Codex 中发送下面的普通中文请求，不需要自己写命令：

```text
请只在当前本机用户主目录下创建 .agents/skills 文件夹；已有则保留，不删除、不覆盖任何文件。完成后告诉我完整路径。现在不要安装软件。
```

得到实际路径后，用 Finder 前往该目录并粘贴。Linux 文件管理器也通常提供“显示隐藏文件”选项；无法新建时可采用同样的中文请求。

有些旧安装使用 `~/.codex/skills`，也可能已被本机配置识别。如果现有 skill 已正常出现，不必为本教程迁移或删除它；先让 Codex 报告实际加载路径。新安装优先采用当前官方的 `~/.agents/skills`，避免同时留两份同名副本导致版本混淆。

### 项目安装：只随某个项目使用

也可在动画项目根目录建立 `.agents/skills`，粘贴完整文件夹：

```text
你的动画项目/
  .agents/
    skills/
      scientific-blender-animation/
        SKILL.md
        references/
        scripts/
        assets/
```

“你的动画项目”指你准备存放 `.blend`、脚本和输出的实际文件夹，不是需要照字面新建的目录。个人安装和项目安装选择一种即可。仓库内的发现范围受 Codex 当前工作目录和仓库边界影响；若没有识别，先在包含 `.agents` 的项目根目录开始会话。

### 可选：让 Codex 的安装器处理 GitHub 下载

若当前环境已有 `$skill-installer`，可在 Codex 中发送：

```text
$skill-installer 请从 https://github.com/Eveeen-beep/scientific-blender-animation 安装 scientific-blender-animation。它的 SKILL.md 位于仓库根目录，请按根目录 skill 处理，保留 references、scripts 和 assets。完成后告诉我实际安装路径。
```

这是手动复制的替代路线，不必重复安装。安装器的联网、写入和实际目标目录遵守当前宿主设置；安装成功后仍需核对加载路径。[官方文档](https://learn.chatgpt.com/docs/build-skills)支持用安装器从其它仓库下载 skill。

## 4. 确认 skill 已加载

在动画项目中打开一个新会话。在支持 skill 选择的输入框中输入 `$scientific-blender-animation`，选择对应项，再发送：

```text
$scientific-blender-animation 请先确认本次实际加载的 skill 名称和 SKILL.md 路径，再概述你会如何进行只读 Blender 检查。现在不要修改文件、安装软件或启动渲染。
```

能选到名称、且代理能够报告实际 skill 路径和规则，才说明加载可用。名称应保持为 `scientific-blender-animation`。只有普通对话中复述这个名字，不能单独证明加载成功。若输入框没有选择入口，可以直接要求 Codex 使用同名 skill，并让它报告来源；仍找不到时重启 Codex 后再检查目录。

**加载成功与 Blender 连接成功是两个检查。** 能读 `SKILL.md` 或列出磁盘文件，不代表已连接到你打开的 Blender 窗口。

## 5. 复制即用：先做最小只读检查

先在 Codex 中打开自己的动画项目目录，再复制下面整段。已有 `.blend` 时把它的完整路径另发给 Codex；没有旧工程也可以从当前空白场景开始。

```text
$scientific-blender-animation 请先做最小只读环境检查，不安装软件、不修改场景、不保存或覆盖 .blend、不启动渲染。
确认当前项目目录和实际可用的 Blender 接入方式；若能执行 Blender，只读报告版本、实际工程完整路径或“未保存的新场景”、Scene、Camera、当前帧、帧范围、fps、对象数量及几个主要对象名称。
请区分：读取磁盘上的工程、连接当前 GUI、只读取到文件名。GUI 若有未保存修改，不要关闭、重开或擅自保存；后台读取磁盘不能代表 GUI 的未保存状态。
如果只能读取文件，或找不到可执行 Blender，请明确写“尚未连接/尚未执行”，列出缺少的能力并停在检查阶段，不虚构检查结果。
```

正确结果应包含实际读取证据，或准确说明缺少哪一步。仓库自带的 `scripts/inspect_blend.py` 可由代理在 Blender 内用于检查；你不必手动改脚本。它的报告可以作为检查产物，但不会保存工程或开始渲染。更详细的接入方式见[连接与恢复](../references/connection-and-recovery.md)。

## 6. 开始一个简单新动画

只读检查通过后，可以发送下面的需求。先在 Codex 打开准备好的项目目录；若宿主没有明确工作目录，先发送项目完整路径。

```text
$scientific-blender-animation 在当前项目目录制作一个新的 Blender 示意动画：一束光从左向右照射平面样品，光束到达后样品短暂发光。总长约 5 秒，24 fps，使用演示参数，中文标签。先明确光束、样品和发光状态之间的关系。
请使用新的场景和文件，不覆盖已有工程；把可继续编辑的 .blend 和实际执行脚本存入项目，先制作低分辨率短预览并检查运动、标签和穿模，完成后给出文件路径及已检查范围。本轮停在短预览，不做高分辨率全片输出。说明这是机理示意，不是光学数值仿真。
```

这段提示已经限定了本轮交付与停止点。复杂装置需要你补充结构、依据和希望观众理解的因果关系；不要用一段模糊需求替代科研参数来源。

## 7. 恢复已有工程

在 Codex 中打开原项目，提供要继续的 `.blend` 完整路径，再发送：

```text
$scientific-blender-animation 请恢复当前项目，先读取 PROJECT_HANDOFF.md；若已有 CODEX_HANDOFF.md，也读取并兼容使用，不要为了改名移动或重命名它。核对记录与磁盘上的 .blend、脚本、输出和活动 Blender/渲染任务是否一致。
本轮先只读报告：可靠基线的完整路径、上次实际完成的步骤、未保存状态、是否有任务仍在运行，以及下一步缺少的证据。不要重跑已成功的构建，不要启动第二个相同渲染，不要覆盖原工程。报告后停下，等我给出这次的具体修改。
```

后续可以直接说明“只改灯光”“只改 80–120 帧的光束位置”等范围。没有 handoff 时先以磁盘和实际场景证据恢复；文件名里最大的版本号不自动等于可靠基线。

## 8. 常见问题

| 现象 | 处理方法 |
| --- | --- |
| 找不到 skill | 检查 `SKILL.md` 是否就在 `scientific-blender-animation` 内；检查有没有多套一层 ZIP 目录；确认个人目录是当前运行 Codex 环境的主目录。必要时重启 Codex。 |
| 同名 skill 出现多次 | 让 Codex 报告每份来源路径和版本，再选择要用的副本。先保留现有可用配置，不盲目覆盖或删除。 |
| `references` 或脚本不存在 | 重新复制完整 skill 文件夹。只放 `SKILL.md` 不足以使用附带参考和工具。 |
| “能读工程”，但 Blender 没反应 | 先问清读的是磁盘文件、后台实例还是当前 GUI；要求返回实际文件路径、版本、Scene 和帧。读取文件名不等于连接 Blender。 |
| 报 `No module named bpy` | 检查脚本是否被普通 Python 执行。让代理使用 Blender 内置 Python 或 Blender CLI；不要因此认定工程损坏。 |
| 没有 MCP | MCP 是可选接入方式。让代理先检查是否可调用本机 Blender；确需新增连接时再按该连接器官方说明配置。 |
| 使用网页或云端 Codex，找不到本机文件 | 云端会话的文件系统和工具环境与本机不同。本机复制 skill、安装 Blender，并不自动赋予云端访问本机磁盘或窗口的能力。使用具备本机执行能力的环境，或单独配置受支持的连接。 |
| 读写或执行被拒绝 | 按宿主显示的权限流程处理，确认路径正确；skill 不会提升权限。无需为此关闭全局安全设置。 |
| 想更新或卸载 | 更新前备份自定义内容，再替换同名完整文件夹；卸载时移走对应 skill 文件夹即可。动画项目及 `.blend` 存在项目目录中，应另外保留。 |

继续阅读：[通用入门](getting-started.zh-CN.md) · [兼容性和验证范围](compatibility.zh-CN.md) · [项目首页](../README.md)
