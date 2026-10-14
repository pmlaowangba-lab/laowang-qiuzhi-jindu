# 飞书多维表格接入（feishu-bitable-init）

`laowang-qiuzhi-jindu` 的**进度真相源**仍是本地 `cards/*.yaml`；飞书表是**可视化进度盘 + 多端查看**，对话更新后双向以本地为准、自动同步飞书。

## 适用场景

- 豆包工作 / Cursor 里随口报进展，自动改飞书表
- 手机飞书 App 随时看「现在几家到哪一步」
- 和 HR / 导师共享进度（只开飞书表权限，不暴露本地 workspace）

## 复用 obsidian-wx 已有飞书应用（推荐）

若已在 Obsidian 插件 **obsidian-wx** 配过飞书（`data.json` 里有 `feishuAppId`），无需新建应用：

```bash
python scripts/feishu_bitable.py import-obsidian-wx --workspace workspace/2027-fall
```

会从 ``.obsidian/plugins/obsidian-wx/data.json``（可选联动，需另行安装） 读取 `feishuAppId`，写入 `feishu-config.yaml`。

**注意**：

- `feishuAppSecret` 在 Obsidian 里通常进 **SecretStorage**，脚本读不到明文。需在本机执行一次 `export FEISHU_APP_SECRET=...`（可从火山 `wx-proxy` 的 `client-config.json` 复制，或 Obsidian 设置里查看后导出）。
- obsidian-wx 当前用于**飞书知识库发文**（wiki），求职进度表还需在同一应用上额外开通下面 bitable 权限。

## 前置：飞书自建应用（无 obsidian-wx 时）

1. 打开 [飞书开放平台](https://open.feishu.cn/app) → 创建**企业自建应用**
2. **权限**（应用身份 `tenant_access_token`）至少开通：
   - `bitable:app`（查看、编辑和管理多维表格）
   - `base:app:create`（创建多维表格，仅 init 时需要）
3. 发布版本并**安装到企业**
4. 记录 **App ID**、**App Secret**

密钥只放 `workspace/<season>/feishu-config.yaml` 或环境变量 `FEISHU_APP_SECRET`，不进 Skill 正文与 Git。

## 一次性初始化

```bash
# 1. 建本地进度盘
python scripts/bootstrap_workspace.py --season 2027-fall

# 2. 复制配置模板
cp assets/feishu-config.example.yaml workspace/2027-fall/feishu-config.yaml
# 编辑 app_id；app_secret 写文件或 export FEISHU_APP_SECRET=...

# 3. 测连通
python scripts/feishu_bitable.py ping --workspace workspace/2027-fall

# 4. 创建飞书多维表格（三张表：投递主表 / 进度时间线 / 待复盘队列）
python scripts/feishu_bitable.py init --workspace workspace/2027-fall --title "秋招求职进度-2027"
```

成功后终端会打印 `app_url`，点开即为飞书多维表格。`feishu-config.yaml` 会自动写入 `app_token`、`tables.*`。

## 表结构

| 数据表 | 用途 |
|--------|------|
| 投递主表 | 每家公司+岗位一行：阶段、轮次、下一动作、考点、card_id |
| 进度时间线 | 每次进展一条，关联投递主表 |
| 待复盘队列 | 面完答不好的考点 |

阶段枚举与本地一致：`意向 → 已投 → 测评中 → 笔试中 → 面试中 → OC/谈薪 → Offer → 拒信 → 放弃`

## 对话更新（日常）

用户**一段话**说完即可（见 [chat-update-prompt-guide.md](chat-update-prompt-guide.md)）：

```text
用 laowang-qiuzhi-jindu：小红书社区增长产品实习今天下午业务一面刚结束，问了发帖量拆解和活跃下降归因，小数指标答得虚记待复盘，等二面通知，周五前没消息我去官网看一下。
```

Agent 流程：

1. 按 [chat-update-guide.md](chat-update-guide.md) 更新本地 `cards/`、`follow-up.md`、`review-queue.md`
2. 若存在 `feishu-config.yaml` 且 `app_token` 已配置 → 调用：

```bash
python scripts/feishu_bitable.py apply-update \
  --workspace workspace/2027-fall \
  --payload /tmp/update.json
```

3. 回复里附上飞书表链接（`app_url`）和本次变更摘要

`update.json` 形状见 [card-schema.md](card-schema.md#chat-update-payload)。

## 仅同步某张本地卡片

```bash
python scripts/feishu_bitable.py sync-card \
  --workspace workspace/2027-fall \
  --card workspace/2027-fall/cards/kuaishou-pm-intern.yaml
```

## 故障排查

| 现象 | 处理 |
|------|------|
| `99991663` 无权限 | 检查应用是否安装到企业、权限是否发布 |
| `app_token` 为空 | 先跑 `init`，不要手填 table_id |
| 关联投递列空 | 先确保主表有对应 `card_id` 行 |
| 飞书改了、本地没改 | 以本地 `cards/` 为准，用 `sync-card` 覆盖飞书 |

## 与 job-application-copilot 的区别

| 旧名 / 技能 | 职责 |
|-------------|------|
| `job-application-copilot` → `laowang-toudi-desk` | 网申填表、字段库、简历快照 |
| **`laowang-qiuzhi-jindu`** | **面试全周期进度、时间线、待复盘**（含飞书同步） |

公众号「面试全周期进度」段落应调用 **`laowang-qiuzhi-jindu`**，不是 `job-application-copilot`。
