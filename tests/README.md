# 测试方法与实际验证记录

## 普通 Python 检查

在仓库根目录、独立 Python 环境中运行：

```sh
python -m pip install Pillow PyYAML
python -m unittest discover -s tests -v
```

测试在临时目录创建小型 PNG 和凭据，不读取用户科研工程。检查范围包括：缺帧/坏帧/尺寸、暗帧建议、可信来源复用条件、报告覆盖保护、输入内容保持、skill 元数据和所有 Markdown 本地链接。外部网页链接不由这组单元测试请求。

`test_inspect_blend_arguments.py` 使用故意不可操作的 `bpy` 替身，确认错误输出目标在接触场景前被拒绝。它不运行真实 Blender，也不能证明动画求值或渲染成功。

## 可选的真实 Blender 最小检查

让 agent 把下列路径替换成本机真实可执行文件；不必让新手手动输入命令：

```text
python tests/blender_runtime_smoke.py --blender "Blender可执行文件完整路径" --report "./reports/blender_smoke.json"
```

`--report` 必须是尚不存在的 `.json` 文件。该工具在可自动清理的独立临时目录内启动 factory 场景，保存带关键帧的测试 `.blend`，再用仓库的 `inspect_blend.py` 读取它；检查报告和源文件 SHA256 保持性。它不打开用户工程，不渲染、不安装插件，也不安装或操控 Claude Code/Cursor。退出时清理自有临时场景，只保留指定报告。

## v1.2.0 发布前实测（2026-11-16）

| 检查 | 实际环境/结果 | 不证明什么 |
|---|---|---|
| Python 单元检查 | Windows，本次独立环境 Python 3.12.14、Pillow 13.0.0、PyYAML 6.0.3；**21 项全部通过** | 不证明三个宿主安装成功或科研机理正确 |
| Skill 元数据验证 | 当前本地验证器通过；使用 `name`、`description`、`metadata` 这一保守公共字段集合 | 不替代各宿主发现/触发检查 |
| 真实 Blender 最小检查 | Windows，**Blender 5.2.0 LTS**；真实 JSON 库存报告、时间轴/分辨率、关键帧动画入口符合测试场景，源 `.blend` SHA256 不变 | 未渲染；未扫描全部帧；未验证生产动画 |
| 引擎记录 | 测试场景报告 `BLENDER_EEVEE`，只记录未渲染 | 不构成 Eevee 渲染性能或 GPU 验证 |
| Claude Code / Cursor | 仅官方文档核对与技能包静态审查 | **未在两个产品内安装、发现、触发、连接 Blender 或渲染** |
| macOS / Linux Blender | 本轮未运行 | 不能从可移植 Python 或 CI 配置外推出 Blender 跨系统运行结果 |

首次普通运行环境缺少 PyYAML，之后在独立环境安装声明的开发依赖再完整重跑通过。元数据检查也曾拒绝某可选字段，现已采用更保守的公共字段集合；没有修改宿主验证器来绕过检查。

匿名化结果见 [validation_1.2.0.json](validation_1.2.0.json)。Codex 的历史完整项目经验见[案例复盘](../references/ring-project-retrospective.md)，不算本轮 v1.2 的全流程重验收。

[GitHub Actions](https://github.com/Eveeen-beep/scientific-blender-animation/actions) 配置为 Windows/Ubuntu + Python 3.11 的普通脚本检查，结果以对应 commit 的实际运行页面为准。**CI 不运行 Blender，也不在 Claude Code/Cursor 中安装技能。**

新增平台实测时请按[贡献指南](../CONTRIBUTING.md)记录宿主版本、系统、工具路线、可公开样例、命令/步骤、结果及未执行项；不要只把表格文字改成“通过”。
