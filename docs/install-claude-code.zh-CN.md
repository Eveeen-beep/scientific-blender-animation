# 在 Claude Code 中安装和使用

这份教程面向已经能够使用 Claude Code、但不熟悉 skill 或 Python 的用户。你只需下载、解压并复制完整文件夹，之后用中文描述要做的动画。Claude Code 能否实际控制 Blender，仍取决于运行环境、可用工具和权限。

**核对日期：2026-11-16。** 本文按 Claude Code 官方 Skills 格式、目录和调用方式整理；尚未在 Claude Code 产品内完成本项目的安装及 Blender 操作实测。格式兼容不代表所有执行能力都已验证。先阅读[兼容性说明](compatibility.zh-CN.md)，需要完整工作顺序时参见[新手入门](getting-started.zh-CN.md)。

## 1. 准备环境

1. 按 [Claude Code 官方安装说明](https://code.claude.com/docs/en/setup)安装、登录 Claude Code，确认能在本地项目中发送消息。本教程不替代宿主安装与账户设置。
2. 从 [Blender 官网](https://www.blender.org/download/)安装 Blender，并手动打开一次，确认默认场景能显示。已有工程优先沿用其当前 Blender 版本。
3. 建立一个自己的动画项目目录，例如“文档/Blender动画练习”，并在该目录中开始 Claude Code 会话。使用图形入口时，选择这个实际本地文件夹作为项目。
4. 按当前宿主设置授予任务所需的项目访问和命令执行权限。不要因为安装 skill 而关闭全局安全设置；组织策略仍会约束 skill 的加载与执行。

MCP 是可选项。如果 Claude Code 能调用本机 Blender，可使用 Blender 内置 Python 或 CLI；已有可用的 Blender 连接器时，也可按其能力使用。普通 Python 的 `bpy` 导入失败，不能说明 Blender 工程损坏。

## 2. 下载并解压完整 skill

1. 打开 [scientific-blender-animation 仓库](https://github.com/Eveeen-beep/scientific-blender-animation)。
2. 点击 **Code → Download ZIP**，下载后使用系统解压功能解压到普通文件夹。
3. 找到直接包含 `SKILL.md` 的一层。默认分支下载后通常叫 `scientific-blender-animation-main`；将它重命名为 `scientific-blender-animation`。
4. 确认 `SKILL.md` 同层还有 `references`、`scripts`、`assets`，复制整个 `scientific-blender-animation` 文件夹。

不要只复制 `SKILL.md`。如果解压目录内又套了一层同名目录，进入内层确认真正的 `SKILL.md` 位置后再复制。

## 3. 选择一个安装位置

[Claude Code 官方 Skills 文档](https://code.claude.com/docs/en/skills)区分个人 skill 和项目 skill。新手选下面一种即可，避免个人和项目各留一份同名副本而调用到不同版本。

### 个人安装：本机各项目可用

目标为：

```text
~/.claude/skills/scientific-blender-animation/
```

`~` 指当前用户的主目录，不是名为 `~` 的文件夹。

**Windows：**

1. 在资源管理器地址栏输入 `%USERPROFILE%`，按回车进入自己的用户主目录。
2. 新建 `.claude` 文件夹，再在其中新建 `skills`；已存在时直接使用，保留原有文件。
3. 将完整的 `scientific-blender-animation` 文件夹粘贴到 `skills` 中。
4. 进入粘贴后的目录，确认以下层级：

```text
你的用户主目录/
  .claude/
    skills/
      scientific-blender-animation/
        SKILL.md
        references/
        scripts/
        assets/
```

如果你在 WSL、容器或远程机器中运行 Claude Code，其主目录属于那个运行环境。Windows 用户主目录中的复制结果，不保证被另一个环境读取；安装位置要与实际会话环境一致。

**macOS / Linux：** 目标位于自己主目录下的 `.claude/skills`。macOS 可在 Finder 按 `Command+Shift+G` 输入 `~/.claude/skills`；点开头的文件夹可能隐藏，可按 `Command+Shift+.` 切换显示。若目录不存在，或 Finder 不允许创建点开头的名称，可先在本地 Claude Code 中发送：

```text
请只在当前本机用户主目录下创建 .claude/skills 文件夹；已有则保留，不删除、不覆盖文件。告诉我完整路径，不安装软件。
```

得到路径后，在 Finder 前往该目录并粘贴完整 skill 文件夹。Linux 也可显示隐藏文件后操作；不能新建时使用同样的中文请求。

### 项目安装：随一个动画项目使用

在自己的动画项目根目录中建立 `.claude/skills`，粘贴完整 skill：

```text
你的动画项目/
  .claude/
    skills/
      scientific-blender-animation/
        SKILL.md
        references/
        scripts/
        assets/
```

“你的动画项目”是你存 `.blend` 和输出的实际目录，不是要照抄创建的占位名称。若文件管理器不便创建点开头目录，也可先要求 Claude Code“只在当前项目创建 .claude/skills，保留已有内容”，再复制文件夹。随后从这个项目开始会话。这个仓库提供的是一个 skill 文件夹，按此路线安装无需把它当作插件市场仓库。

## 4. 确认 skill 已加载

在 Claude Code 的输入框中输入 `/`，查找 `scientific-blender-animation`，也可直接发送：

```text
/scientific-blender-animation 请确认本次加载的 skill 名称和 SKILL.md 来源路径，并说明你会如何做只读 Blender 检查。现在不要修改文件、安装软件或开始渲染。
```

本项目的调用名保持为 `/scientific-blender-animation`。它也可能在相关任务中自动被选择；第一次使用建议显式调用并确认来源。官方文档说明了 `/skill-name` 的调用方式及附带资源的用法。

如果没有出现：先核对目录层级、`SKILL.md` 文件名和项目位置，再新开本地会话。若当前版本支持 `/reload-skills`，也可刷新 skill 列表。组织策略可能限制本地 skill；不要用改名或关闭安全设置来绕过。

**加载 skill 不等于连接 Blender。** 代理成功读到规则后，还需要用实际工具确认 Blender 的版本、工程身份和场景状态。

## 5. 复制即用：最小只读 Blender 检查

在正确动画项目中发送以下提示。已有 `.blend` 时，另外提供该文件的完整路径；若只打开了未保存的新场景，要明确告诉 Claude Code。

```text
/scientific-blender-animation 请先只读检查当前本地项目和 Blender，不安装软件、不修改场景、不保存或覆盖 .blend、不启动渲染。
先识别实际可用的接入方式。若能执行 Blender，请报告版本、实际工程完整路径或“未保存的新场景”、Scene、Camera、当前帧、帧范围、fps、对象数量与几个主要对象名称。
请区分磁盘工程、后台 Blender 和当前 GUI；有未保存 GUI 修改时，不要关闭、重开或擅自保存。后台检查磁盘文件不能替代未保存的 GUI 状态。
若没有可用 Blender 执行或连接工具，请明确写“尚未连接/尚未执行”，报告已经读到什么和还缺什么，停在检查阶段。不要把列出文件名当作已连接。
```

skill 中的 `scripts/inspect_blend.py` 是供 Blender 内执行的检查脚本，代理可按[连接与恢复](../references/connection-and-recovery.md)选择合适路线。你不必自己编写 Python。代理应区分实际执行结果、历史报告和未执行项。

## 6. 开始一个简单新动画

只读检查确认可执行后，发送：

```text
/scientific-blender-animation 请在当前项目目录新建一个 Blender 示意动画：一束光从左向右照射平面样品，到达后样品短暂发光。时长约 5 秒，24 fps，中文标签，所有尺寸和时序采用明确标注的演示值。
先理清光束运动、照射和发光的因果关系，再建立新的场景和文件。请保存可编辑 .blend 与实际执行脚本，不覆盖现有工程。先输出低分辨率短预览，检查关键状态、标签和穿模，报告文件路径及实际检查范围。本轮停在短预览。不要把这个示意称作光学仿真。
```

若当前会话没有明确工作目录，先发自己的项目完整路径。后续更复杂的科研动画需要补充结构来源、运动主体、参数和允许简化范围，详见[新手入门](getting-started.zh-CN.md)。

## 7. 继续已有 Blender 项目

打开原项目目录，并向 Claude Code 提供目标 `.blend` 完整路径，然后发送：

```text
/scientific-blender-animation 请先只读恢复这个项目。优先读取 PROJECT_HANDOFF.md；若已有 CODEX_HANDOFF.md，同样兼容读取，不移动或强制重命名旧文件。请把交接记录与磁盘工程、脚本、输出及活动 Blender/渲染任务进行核对。
报告可靠基线完整路径、上次实际完成步骤、GUI 是否有未保存状态、是否已有任务运行和下一步需要的证据。本轮不要改工程、重跑成功的构建、重复启动渲染或覆盖文件。报告后停止，等我说明这次要改什么。
```

确认基线后，再给出本轮修改，如“保留结构和运动，只调灯光”。缺少 handoff 不必重做工程；先根据真实文件和场景恢复，不以最大版本号直接决定基线。

## 8. 常见问题

| 现象 | 处理方法 |
| --- | --- |
| `/scientific-blender-animation` 找不到 | 检查是否在 `.claude/skills/scientific-blender-animation/SKILL.md`；确认没有 ZIP 目录双重嵌套；确认会话使用的主目录或项目根目录。刷新或重开会话。 |
| 出现名称但行为不像本教程 | 让 Claude Code 报告来源路径，检查个人目录、项目目录是否存在不同版本的同名 skill。 |
| 缺少参考文件或脚本 | 重新复制完整目录，保留 `references`、`scripts`、`assets`，不要只安装入口文件。 |
| 说能读文件，却不能控制窗口 | 文件访问和 Blender 控制是不同能力；要求用实际工具报告工程路径、版本和场景。后台 Blender 不等于当前 GUI。 |
| `import bpy` 报错 | 通常是脚本跑在普通 Python；让代理在 Blender 内执行。skill 不要求你先在系统 Python 中安装 `bpy`。 |
| 必须先装 MCP 吗 | 不必须。先检查本机 Blender 的现有 CLI/脚本能力；需要控制当前 GUI 且缺少工具时，再选择合适连接器。 |
| 在网页聊天或云端找不到本机 skill/Blender | 本教程针对本地 Claude Code。网页、Cowork、云端会话的加载和文件访问方式不同；本机复制目录不会自动开放本机磁盘或 Blender。 |
| 执行权限被拒绝 | 按 Claude Code 的权限提示和组织规则处理；skill 不授予额外权限，也不应要求你关闭全局保护。 |
| 更新或卸载 | 备份自己的修改后替换完整 skill 文件夹；卸载时移走安装的那一份目录。不要把动画项目中的 `.blend` 和输出一起删除。 |

继续阅读：[通用入门](getting-started.zh-CN.md) · [兼容性和验证范围](compatibility.zh-CN.md) · [Claude Code 官方 Skills 文档](https://code.claude.com/docs/en/skills) · [项目首页](../README.md)
