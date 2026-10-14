# 对话示例

## 初始化飞书多维表格（首次）

```text
用 laowang-qiuzhi-jindu：帮我初始化秋招进度盘，并在飞书创建求职进度多维表格。
我的飞书 App ID 是 cli_xxxx，密钥已放在环境变量 FEISHU_APP_SECRET。
```

**Skill 应**：`jindu-init` → 引导/写入 `feishu-config.yaml` → `feishu_bitable.py init` → 返回飞书表链接。

## 面完更新 + 待复盘（一段话即可）

```text
用 laowang-qiuzhi-jindu：小红书社区增长产品实习今天下午三点左右业务一面刚结束，主要问了兴趣社区战略、发帖量拆解和活跃下降归因，小数指标和男性增长调性那两块我答得一般记待复盘，简历 resume-v3-xhs-community，等二面通知，周五前没动静我去官网看一下。
```

**Skill 应**：自动解析 → 改卡片 + 时间线 + 待复盘 + 待办 + 同步飞书表。怎么说见 `chat-update-prompt-guide.md`（可选联动，需另行安装）。

## 收拒信

```text
用 laowang-qiuzhi-jindu：美团 AI 产品实习刚收到拒信，简历挂了。
```

## 约面试

```text
用 laowang-qiuzhi-jindu：字节约了下周一下午3点技术面，线上。
```

## 查询

```text
用 laowang-qiuzhi-jindu：字节现在什么状态？我这周还要跟哪些事？
```

## 新投

```text
用 laowang-qiuzhi-jindu：今天投了腾讯 IEG 产品策划实习，用的 resume-v3。
```
