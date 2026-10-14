# 投递卡片结构

文件：`cards/<card_id>.yaml`  
`card_id` = `{公司拼音}-{岗位关键词}`，如 `kuaishou-pm-intern`

```yaml
card_id: kuaishou-pm-intern
company: 快手
role: 社区产品实习
city: 北京
channel: 官网
job_url: ""
job_pool_ref: ""              # laowang-boss-sync job_id
resume_snapshot_id: ""
current_stage: 面试中
interview:
  round: 二面
  status: completed
  completed_at: 2026-09-19T14:00:00+08:00
  focus_topics: [指标归因, 漏斗分析]
next_action: 等结果；补强漏斗题进 mianshi-zhu
timeline:
  - at: 2026-09-10
    stage: 已投
    source: 用户口述
    note: 网申提交
  - at: 2026-09-19T14:00:00+08:00
    stage: 面试中
    source: 用户口述
    note: 二面完成，考察指标归因；漏斗题薄弱
updated_at: 2026-09-19
```

## chat-update-payload（脚本用）

```json
{
  "card_id": "kuaishou-pm-intern",
  "user_quote": "快手今天下午二面完了…",
  "stage": "面试中",
  "timeline_entry": {
    "at": "2026-09-19T14:00:00+08:00",
    "stage": "面试中",
    "source": "用户口述",
    "note": "二面完成，考察指标归因"
  },
  "interview_patch": { "round": "二面", "status": "completed" },
  "review_items": ["漏斗分析-快手二面"],
  "follow_up_items": []
}
```
