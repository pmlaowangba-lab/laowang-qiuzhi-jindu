# 阶段定义

## 主阶段（current_stage，互斥）

```text
意向 → 已投 → 测评中 → 笔试中 → 面试中 → OC/谈薪 → Offer → 拒信 → 放弃
```

| 阶段 | 进入条件 |
|------|----------|
| 意向 | 在 boss-sync 池里，未正式投递 |
| 已投 | 用户确认网申/投递已提交 |
| 测评中 | 收到测评链接或正在做 |
| 笔试中 | 收到笔试通知或已开考 |
| 面试中 | 任何一轮面试预约或进行中 |
| OC/谈薪 | 口头/书面 OC，未最终签字 |
| Offer | 用户确认接受意向或已签 |
| 拒信 | 用户确认被拒或明确默拒 |
| 放弃 | 用户主动不继续 |

## 面试子状态（stage=面试中 时）

```yaml
interview:
  round: 二面
  status: completed    # scheduled | completed | cancelled
  scheduled_at: 2026-09-22T15:00:00+08:00
  completed_at: 2026-09-19T14:00:00+08:00
  format: 线上
  focus_topics: [指标归因, 漏斗分析]
```

## 易混（必须写进 note）

- 做完测评 → 仍 `测评中`，note 写「已提交待结果」
- 通知二面 → `面试中`，round=二面，status=scheduled
