# 在 Cursor 中安装和使用

这份教程使用“下载 ZIP、复制完整 skill 文件夹”的方式，把本项目提供给 Cursor Agent。无需自己写 Python；随后用中文描述动画，由 Agent 按当前环境能力处理脚本和 Blender 操作。

**核对日期：2026-11-16。** 本文按 Cursor 官方 Skills 格式、目录和调用规则整理，尚未在 Cursor 产品内完成本项目的安装和 Blender 操作实测。支持同一种 skill 格式，不代表已验证所有功能。详细边界见[兼容性说明](compatibility.zh-CN.md)，通用流程见[新手入门](getting-started.zh-CN.md)。

## 1. 准备环境

1. 从 [Cursor 官网](https://cursor.com/downloads)安装并登录 Cursor，确认能够使用本地项目中的 Agent 聊天。本教程从宿主已可使用开始。
2. 从 [Blender 官网](https://www.blender.org/download/)安装 Blender，先手动打开确认默认场景可用。已有项目优先沿用其工程所需版本。
3. 新建自己的动画项目目录，例如“文档/Blender动画练习”，在 Cursor 中使用 **Open Folder / 打开文件夹**打开它。
4. 使用具备文件和执行工具的 Agent 入口。命令执行、项目写入和连接工具仍按 Cursor 当前权限与组织设置处理。

建议第一次在本机项目中尝试。本地 skill 文件、Blender 安装和 GUI 不会自动出现在 Cloud Agent、远程 SSH 或其它远端运行环境中。MCP 可选：可先检查 Agent 是否能通过本机 Blender 的内置 Python/CLI 执行任务。

## 2. 下载并解压

1. 打开 [scientific-blender-animation 仓库](https://github.com/Eveeen-beep/scientific-blender-animation)。
2. 点击 **Code → Download ZIP**，下载后使用系统工具解压。
3. 找到直接包含 `SKILL.md` 的文件夹。默认分支下载后通常叫 `scientific-blender-animation-main`；将这一层重命名为 `scientific-blender-animation`。
4. 检查 `SKILL.md` 同层存在 `references`、`scripts`、`assets`，复制整个文件夹。

如果解压工具额外套了一层目录，只复制真正包含 `SKILL.md` 的那一层。不要只复制 `SKILL.md`，也不要把它单独改名后扔进项目根目录。

## 3. 安装到项目或个人目录

[Cursor 官方 Skills 文档](https://cursor.com/docs/skills)列出了项目与个人目录。本教程推荐先按项目安装，便于明确 skill 用于哪个动画项目。

### 项目安装：推荐第一次使用

在 Cursor 左侧文件列表中，于打开的动画项目根目录新建 `.cursor` 文件夹，再在其中新建 `skills`，把完整 `scientific-blender-animation` 文件夹粘贴进去：

```text
你的动画项目/
  .cursor/
    skills/
      scientific-blender-animation/
        SKILL.md
        references/
        scripts/
        assets/
```

“你的动画项目”指你准备存 `.blend` 和输出的实际目录，不是要照字面创建的名称。也可使用项目内的 `.agents/skills/scientific-blender-animation/`；两条路线选一种即可，避免重复安装相同 skill。

Windows 可直接在资源管理器中进入项目目录并创建这些文件夹。macOS 的点开头目录可能隐藏，可在 Finder 按 `Command+Shift+.` 显示它们。

### 个人安装：本机多个项目可用

个人目录可使用：

```text
~/.cursor/skills/scientific-blender-animation/
```

`~` 是当前用户的主目录，不是名为 `~` 的目录。

**Windows：**

1. 打开资源管理器，在地址栏输入 `%USERPROFILE%` 并回车。
2. 建立 `.cursor` 文件夹，并在其中建立 `skills`；已有时直接使用，保留原内容。
3. 粘贴整个 skill 文件夹，使 `SKILL.md` 位于 `.cursor/skills/scientific-blender-animation/` 内。

**macOS / Linux：** 目标位于当前用户主目录下的 `.cursor/skills`。macOS 可在 Finder 按 `Command+Shift+G` 输入 `~/.cursor/skills`。若目录不存在，或 Finder 不允许创建点开头的名称，可先在本地 Cursor Agent 中发送：

```text
请只在当前本机用户主目录下创建 .cursor/skills 文件夹；已有则保留，不删除、不覆盖文件。告诉我完整路径，不安装软件。
```

得到路径后，在 Finder 前往该目录并粘贴完整 skill 文件夹。Linux 也可显示隐藏文件后操作；不能新建时使用同样的中文请求。

Cursor 当前也支持个人 `~/.agents/skills`，并读取部分其它工具的兼容目录。第一次安装无需复制到所有目录；已有同名 skill 时，先确认来源，避免把旧版和新版混用。

### 为什么不使用 “From GitHub Repository” 一键导入

当前 Cursor 的 **From GitHub Repository** 路线用于从市场导入插件，要求仓库提供 `.cursor-plugin/marketplace.json`。本仓库目前提供直接 skill 文件夹，没有这一插件市场清单，因此这里使用完整文件夹复制；不要把仓库 URL 粘贴进去后就当作已安装。这个限制依据 [Cursor 官方仓库安装说明](https://cursor.com/docs/skills)。

## 4. 确认 skill 被发现和加载

安装后重新打开项目或开始新的 Agent 会话，在 Agent 输入框输入 `/`，搜索 `scientific-blender-animation`，选择它并发送：

```text
/scientific-blender-animation 请确认本次加载的 skill 名称与 SKILL.md 来源路径，并概述只读 Blender 检查方法。现在不要修改文件、安装软件或启动渲染。
```

本项目调用名保持为 `/scientific-blender-animation`。Cursor 也可以按上下文自动使用 skill；第一次建议显式选中，并让 Agent 报告来源路径。按当前官方说明，手动选择的 skill 附着到这一条消息；新手可在后续关键请求中再次选择它，避免依赖会话记忆。

找不到时先核对目录、文件名、解压嵌套和当前打开的项目，再重开 Cursor。能在磁盘读到 `SKILL.md` 不等于已经被 Agent 发现；也不等于 Blender 已连接。

## 5. 复制即用：先做最小只读检查

在正确的动画项目中发送以下提示。若要检查已有工程，另发 `.blend` 的完整路径；若 Blender 是未保存的新场景，也直接说明。

```text
/scientific-blender-animation 先只读检查本地项目和可用 Blender 环境。不安装软件、不修改场景、不保存或覆盖 .blend、不启动渲染。
请说明实际可用的接入方式；若能执行 Blender，报告版本、工程完整路径或“未保存的新场景”、Scene、Camera、当前帧、帧范围、fps、对象数量和几个主要对象名称。
请明确区分磁盘文件、后台实例和当前 GUI。GUI 若有未保存修改，不要关闭、重开或擅自保存；后台读盘结果不能代表未保存的 GUI 状态。
如果当前 Agent 只能读取文件，或找不到 Blender 执行/连接工具，请写“尚未连接/尚未执行”，列出实际读到什么和缺少什么，停在检查阶段。不要凭文件名或进程存在宣称已连接。
```

仓库的 `scripts/inspect_blend.py` 可由 Agent 在 Blender 内只读执行；你无需自己写代码。它用于生成检查报告，不保存工程、不启动渲染。检查证据和接入路线详见[连接与恢复](../references/connection-and-recovery.md)。

## 6. 制作一个简单新动画

检查确认可以执行 Blender 后，在 Agent 中再次选中 skill 并发送：

```text
/scientific-blender-animation 请在当前项目制作一个新的 Blender 示意动画：一束光从左向右照射平面样品，到达后样品短暂发光。约 5 秒，24 fps，中文标签，尺寸和时序使用清楚注明的演示值。
先明确光束运动、照射和发光之间的关系，再使用新的场景和文件实现。请保存可编辑的 .blend 与实际执行脚本，不覆盖已有工程。先做低分辨率短预览，检查关键状态、标签和穿模，报告文件完整路径与已检查范围。本轮停在短预览；说明这是机理示意，不是光学数值仿真。
```

如果项目目录不明确，先提供自己的实际路径。复杂动画还需说明装置结构、参数来源、谁在运动和允许的示意简化；可按[通用入门](getting-started.zh-CN.md)补充需求。

## 7. 恢复已有工程

用 Cursor 打开原项目目录，提供目标 `.blend` 完整路径，再发送：

```text
/scientific-blender-animation 请先只读恢复当前项目。先读 PROJECT_HANDOFF.md；若已有 CODEX_HANDOFF.md，同样兼容读取，不为改名而移动或重命名旧文件。请核对交接记录、磁盘工程、脚本、输出以及活动 Blender/渲染任务。
报告可靠基线完整路径、实际完成步骤、是否有未保存 GUI 状态、是否已有任务仍运行，以及下一步缺少的证据。不要改工程、重跑成功的构建、重复启动渲染或覆盖原文件。报告后停止，等我说明本轮具体修改。
```

随后说明允许的改动，例如“保留结构与运动，只调材质”。缺少交接文件时，以实际工程和输出核对为准，不根据文件名最大版本号直接重建。

## 8. 常见问题

| 现象 | 处理方法 |
| --- | --- |
| `/` 菜单找不到 skill | 检查是否打开了正确项目，`SKILL.md` 是否直接位于 `.cursor/skills/scientific-blender-animation/` 或所选安装目录内；排除 ZIP 双重嵌套，再重开项目或 Cursor。 |
| 提示缺少 `marketplace.json` | 这是插件市场导入要求。本仓库按直接 skill 路线使用，改用上面的完整文件夹复制步骤。 |
| 同一个名称有多份 | 让 Agent 报告来源路径，检查个人目录、项目目录及兼容目录中的副本，确认要用的版本。 |
| 能加载规则，却找不到脚本/模板 | 检查是否只复制了 `SKILL.md`；重新复制整个 skill 文件夹，保留 `references`、`scripts`、`assets`。 |
| 文件能读，但 Blender 窗口没有变化 | 读取文件、执行后台 Blender、控制当前 GUI 是不同能力。先要求真实只读握手结果；不要以窗口是否变化判断只读检查成功与否。 |
| `No module named bpy` | 让 Agent 检查是否错用了普通 Python。`bpy` 通常应在 Blender Python 或 Blender CLI 中执行。 |
| 没有 MCP 是否不能用 | MCP 可选。先检查本机 Blender CLI/脚本路线；需要控制当前打开 GUI 且缺少工具时，再按选定连接器说明配置。 |
| Cloud Agent/远程会话无法访问本机工程 | 远端有自己的文件系统和执行环境；个人目录中的 skill、本地 Blender 和窗口不会自动传过去。确认 skill、工程和 Blender 是否都位于实际执行环境。 |
| 权限受限 | 按 Cursor 的项目、工具和组织权限处理；skill 不会自动增加能力，不要通过关闭全局保护解决。 |
| 更新、卸载怎么做 | 更新前备份自定义内容，再替换完整 skill 目录；卸载时移走安装的那份目录即可。另行保留动画项目、`.blend` 和输出。 |

继续阅读：[通用入门](getting-started.zh-CN.md) · [兼容性和验证范围](compatibility.zh-CN.md) · [Cursor 官方 Skills 文档](https://cursor.com/docs/skills) · [项目首页](../README.md)
