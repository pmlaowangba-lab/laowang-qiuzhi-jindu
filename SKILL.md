---
name: laowang-qiuzhi-jindu
description: 老王工作区原创求职进度 Skill（面试全周期进度）。用自然语言对话更新多家投递的状态、时间线、面试考点与待复盘队列；支持一键初始化飞书多维表格并在每次对话后自动同步；支持查询「某公司现在到哪一步」、生成跟进行动清单。适用于秋招并行多厂、面完随手记账、测评笔试面试阶段不混淆。与 laowang-boss-sync 岗位池、laowang-toudi-desk 网申可联动。别名 job-application-copilot 仅指投递台，本 Skill 管进度。不擅自编造投递结果。
---

# 老王求职进度（laowang-qiuzhi-jindu）

秋招同时开 5 家厂，最怕的不是忙，是**状态记混**：测评做完以为过了、二面完不知道下一步干嘛。本 Skill 用**对话当输入**，帮你维护一张动态进度盘。

## 能力地图

| 模式 | 代号 | 你怎么说 | Skill 做什么 |
|------|------|----------|--------------|
| 初始化 | `jindu-init` | 「建求职进度盘」 | 建 `workspace/<season>/` 骨架 |
| **飞书表初始化** | `feishu-bitable-init` | 「生成飞书求职进度多维表格」 | 调飞书 API 建表 + 写 `feishu-config.yaml` |
| **对话更新** | `chat-update` | 「快手今天二面完了，问了指标归因…」 | 解析 → 改本地卡片 → 同步飞书表 → 待办/待复盘 |
| 查询 | `jindu-query` | 「字节现在什么状态？」 | 读卡片 + 时间线摘要 |
| 登记新投 | `card-new` | 「刚投了美团 AI 产品实习」 | 新建投递卡片 + 主表一行 |
| 跟进行动 | `follow-up-sync` | 「帮我列这周要干嘛」 | 刷新 `follow-up.md` 优先级队列 |
| 复盘队列 | `review-queue` | 「把今天答不好的题记待复盘」 | 维护 `review-queue.md` |
| 总览刷新 | `dashboard-refresh` | 「刷新进度总览」 | 从各卡片重算 `progress-dashboard.md` |

**不做**：未经用户确认把「做完测评」写成「通过」；编造 Offer/拒信；自动改 boss-sync 岗位池里的「已投」（除非用户明确说已投）。

## 数据落点

```text
workspace/2027-fall/
├── progress-dashboard.md      # 一眼总览（多厂并行）
├── master-pipeline.md         # 主表（与 boss-sync 字段对齐）
├── follow-up.md               # 待办 + 截止日期
├── review-queue.md            # 待复盘考点
├── cards/                     # 每家公司+岗位一张卡
│   └── kuaishou-pm-intern.yaml
├── timeline/                  # 可选：按日合并日志
├── feishu-config.yaml         # 飞书 app_token / 表 ID（gitignore，含密钥）
└── audit/                     # 对话更新审计
```

卡片用 **YAML**（机器好改），总览用 **Markdown**（人好读）。已配置飞书时，**投递主表 / 时间线 / 待复盘** 三张多维表格与本地同步。

## 路由规则

1. 用户随口报进展、面完、收邮件、约面试 → **`chat-update`**（默认路由）
2. 用户说「建飞书进度表」「生成多维表格」→ **`feishu-bitable-init`**（需先有 `jindu-init` + 飞书应用凭证）
3. 用户问状态 → `jindu-query`
4. 用户说「新投了一家」→ `card-new`，可接 `chat-update` 补细节
5. 用户要待办清单 → `follow-up-sync`
6. 用户专门记错题/薄弱考点 → `review-queue`（也常由 `chat-update` 顺带触发）

执行前按需读取：

- 飞书接入：[references/feishu-bitable-setup.md](references/feishu-bitable-setup.md)
- **提示词与关键信息**：[references/chat-update-prompt-guide.md](references/chat-update-prompt-guide.md)
- 对话解析：[references/chat-update-guide.md](references/chat-update-guide.md)
- 阶段定义：[references/stage-definitions.md](references/stage-definitions.md)
- 卡片结构：[references/card-schema.md](references/card-schema.md)
- 复盘队列：[references/review-queue-rules.md](references/review-queue-rules.md)
- 总览模板：[assets/progress-dashboard-template.md](assets/progress-dashboard-template.md)

## 模式：chat-update（核心）

### 用户怎么说都行

示例（**一段话**口述即可，Skill 自动解析更新，见 [chat-update-prompt-guide.md](references/chat-update-prompt-guide.md)）：

```text
用 laowang-qiuzhi-jindu：小红书社区增长产品实习今天下午业务一面刚结束，问了发帖量拆解和活跃下降归因，小数指标那块答得虚记待复盘，等二面通知，周五前没消息我去官网看一下。
```

```text
美团刚收到拒信，简历挂。
```

```text
字节约了下周一下午 3 点技术面，线上。
```

### Agent 处理步骤

1. **解析实体**：公司、岗位（模糊则用最接近的卡片或追问）、事件类型、时间、考点、情绪/薄弱点。
2. **Read** 对应 `cards/*.yaml`；无卡则先 `card-new` 或询问是否新建。
3. **映射阶段**：按 [stage-definitions.md](references/stage-definitions.md)，禁止跳级臆测（做完测评 ≠ 通过）。
4. **追加 timeline** 条目（时间、阶段、来源=用户口述、note）。
5. **更新** `current_stage`、`interview_round`（若适用）、`next_action`。
6. **待复盘**：薄弱考点写入 `review-queue.md`（去重，附公司+日期+题旨）。
7. **待办**：生成/勾选 `follow-up.md`（如「24h 内感谢信」「周五前完成测评」）。
8. **同步** `master-pipeline.md` 对应行 + `dashboard-refresh`。
9. **飞书同步**（若 `feishu-config.yaml` 已 init）：写 `update.json` 后执行：

```bash
python scripts/feishu_bitable.py apply-update \
  --workspace workspace/<season> \
  --payload /tmp/update.json
```

10. **写审计** `audit/chat-update-<timestamp>.md`（用户原话 + 改了什么 + 是否已同步飞书）。
11. **回复确认**：用 3–5 行说清「记下了什么、当前阶段、你下一步该干嘛」；有飞书则附 `app_url`。

信息不足时**只问 1 个关键问题**（如「是快手主站还是电商线？」），不要问卷。

### 可选脚本校验

```bash
python scripts/apply_update.py \
  --workspace workspace/2027-fall \
  --payload /tmp/update.json
```

`update.json` 形状见 [references/card-schema.md](references/card-schema.md#chat-update-payload)。

## 模式：feishu-bitable-init

### 目标

在飞书创建**求职进度多维表格**（投递主表 + 进度时间线 + 待复盘队列），后续 `chat-update` 自动写入。

### 流程

1. 确认已完成 `jindu-init`。
2. 引导用户配置飞书自建应用（见 [feishu-bitable-setup.md](references/feishu-bitable-setup.md)）。
3. **已有 obsidian-wx 飞书配置时**，优先：

```bash
python scripts/feishu_bitable.py --workspace workspace/<season> import-obsidian-wx
```

否则复制 [assets/feishu-config.example.yaml](assets/feishu-config.example.yaml) → `feishu-config.yaml`，填入 `app_id`；`app_secret` 走环境变量或本地文件。

4. 执行：

```bash
python scripts/feishu_bitable.py ping --workspace workspace/<season>
python scripts/feishu_bitable.py init --workspace workspace/<season> --title "秋招求职进度-<赛季>"
```

5. 把返回的 **`app_url`** 发给用户收藏；后续所有 `chat-update` 默认同步该表。

未配置飞书时，`chat-update` 仅写本地，不报错。

## 模式：jindu-query

输出：

- 当前阶段 + 最近 3 条时间线
- 用的哪版简历（`resume_snapshot_id`）
- 待办里与它相关的项
- 待复盘里与它相关的考点

## 模式：card-new

必填：公司、岗位。可选：渠道、投递日、简历版本、boss-sync 的 `job_id` 链接。

## 阶段枚举（互斥）

```text
意向 → 已投 → 测评中 → 笔试中 → 面试中 → OC/谈薪 → Offer → 拒信 → 放弃
```

子状态（面试中）：`round: 一面|二面|HR|终面` + `scheduled_at` / `completed_at`

详见 [stage-definitions.md](references/stage-definitions.md)。

## 与其他 Skill 的分工

| Skill | 分工 |
|-------|------|
| `laowang-boss-sync`（可选联动，需另行安装） | 岗位从哪来（BOSS 池） |
| `laowang-toudi-desk`（可选联动，需另行安装） | 网申填表、字段库、附件 |
| [laowang-qiuzhi-jindu](SKILL.md) | **对话更新进度**、时间线、待办、待复盘 |
| `laowang-mianshi-lian`（可选联动，需另行安装） | 面试工作册编排 |
| `laowang-mianshi-fu`（可选联动，需另行安装） | 面后复盘写入工作册 B/C |
| `laowang-mianshi-mo`（可选联动，需另行安装） | 模拟压测 |

`laowang-toudi-desk` 的 `pipeline-update` 可改调本 Skill 的 `chat-update`，避免两套进度打架；以本 Skill 的 `cards/` 为进度**唯一真相源**。

## 完成报告（chat-update 后）

```markdown
## 进度更新确认
- 公司/岗位：…
- 阶段：… → …
- 时间线：新增 1 条
- 待复盘：+1（漏斗归因）
- 你的下一步：…
```

## 质量门槛

- [ ] 用户原话与写入字段一致，无臆测结果
- [ ] 测评/笔试未确认通过前不升级阶段
- [ ] 主表、总览、卡片三者一致
- [ ] 待复盘条目可追溯到具体面试 note
- [ ] 回复里明确下一步动作
