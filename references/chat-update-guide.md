# 对话更新解析（chat-update）

用户**一段话**口述即可，Skill 自动抽取字段；怎么说见 **[chat-update-prompt-guide.md](chat-update-prompt-guide.md)**。

## 意图分类

| 意图 | 触发词示例 | 动作 |
|------|------------|------|
| 阶段推进 | 投了、交卷、面完、约面、OC、offer、挂了、拒信 | 改 `current_stage` + timeline |
| 预约 | 约了、通知、明天下午 | 写 `scheduled_*`，阶段→面试中 |
| 考点记录 | 问了、考了、主要考察 | timeline.note + 可选 review-queue |
| 薄弱登记 | 答不好、卡壳、不会、复盘 | review-queue |
| 待办 | 截止、记得、要交 | follow-up.md |
| 查询 | 什么状态、到哪了 | 转 `jindu-query` |

## 实体抽取

| 字段 | 规则 |
|------|------|
| company | 简称映射：快手/KS、字节/ByteDance、美团/Meituan |
| role | 产品实习、后端、运营… 无则沿用卡片或追问 |
| when | 默认今天；解析「昨天下午」「下周一下午3点」 |
| round | 一面/二面/业务面/HR面/终面 |
| source | 默认 `用户口述`；用户说邮件/短信则改 |

## 模糊匹配

1. 仅说公司名 → 若只有 1 张卡，用该卡
2. 多张卡 → 问：「是 {A岗位} 还是 {B岗位}？」
3. 全新公司 → 提议 `card-new`

## 禁止自动推断

| 用户说 | 不能写成 |
|--------|----------|
| 做完测评 | 测评通过 |
| 面完挺顺 | 稳了 / 已过 |
| 很久没消息 | 默拒（除非用户说拒信） |
| HR 口头说不错 | Offer |

## 飞书同步（chat-update 第 9 步）

若 `workspace/<season>/feishu-config.yaml` 中已有 `app_token`：

1. 本地改完 `cards/`、`follow-up.md`、`review-queue.md` 后
2. 组装 `update.json`（含 `card_id`、`stage`、`timeline_entry`、`review_items`）
3. 执行 `scripts/feishu_bitable.py apply-update`
4. 失败时：本地进度仍有效，回复里说明飞书同步失败原因，不阻断记账

无飞书配置时跳过，仅维护本地。

## 回复模板（给用户）

```markdown
记下了：**{公司}-{岗位}** 现为 **{阶段}**。
- 时间线：{一句话}
- 待复盘：{有则列，无则写「无」}
- 飞书表：{有则附 app_url，无则省略}
- 建议你：{一条具体下一步}
```
