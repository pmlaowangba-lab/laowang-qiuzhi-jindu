# laowang-qiuzhi-jindu

## 从 GitHub 安装（豆包工作）

GitHub 用户：`pmlaowangba-lab`；仓库：`pmlaowangba-lab/laowang-qiuzhi-jindu`。

把下面整段发送给电脑版豆包工作的 Agent：

```text
请从 GitHub 用户 pmlaowangba-lab 的仓库 laowang-qiuzhi-jindu 安装 Skill。
仓库地址：https://github.com/pmlaowangba-lab/laowang-qiuzhi-jindu
请先读取仓库根目录 SKILL.md，下载完整技能目录（包括 scripts、references、assets 和 agents 等文件，若存在），安装到当前工作区 .agents/skills/laowang-qiuzhi-jindu/。
安装后检查 SKILL.md 的 name 与依赖文件，尝试识别并调用技能，返回实际安装路径和识别结果。若不能识别，请说明需要配置的技能目录或刷新步骤，不要仅以下载成功宣称安装完成。
```

也可手动安装：

```bash
git clone https://github.com/pmlaowangba-lab/laowang-qiuzhi-jindu.git .agents/skills/laowang-qiuzhi-jindu
```

Python 脚本需 Python 3 与 PyYAML；若缺少 PyYAML，请在项目虚拟环境中安装。技能能否出现在界面列表，取决于客户端版本和技能目录设置，需在目标客户端实际检查。
飞书功能还需用户自己的应用、权限和凭据；本地功能不需要飞书。个人数据写入 workspace，不提交 GitHub。


**面试全周期进度** Skill（对话驱动）：随口报进展 → 自动更新时间线、待办、待复盘 → **可选同步飞书多维表格**。

> 别名说明：`job-application-copilot` 在套件里对应 **laowang-toudi-desk**（网申填表），不是本 Skill。进度跟踪用 **laowang-qiuzhi-jindu**。

## 核心模式

- `feishu-bitable-init` — 一键创建飞书进度多维表格
- `chat-update` — 用自然语言更新（默认，自动同步飞书）
- `jindu-query` — 查状态
- `card-new` — 登记新投
- `follow-up-sync` / `review-queue` / `dashboard-refresh`

## 安装

```text
帮我把 laowang-qiuzhi-jindu 安装到 .agents/skills/
```

## 数据

- 本地：`workspace/<season>/cards/*.yaml` + `progress-dashboard.md`
- 飞书：`feishu-config.yaml` 里的多维表格（投递主表 / 时间线 / 待复盘）

飞书接入见 [references/feishu-bitable-setup.md](references/feishu-bitable-setup.md)

## 套件

`求职Skill套件-README.md`（可选联动，需另行安装）
