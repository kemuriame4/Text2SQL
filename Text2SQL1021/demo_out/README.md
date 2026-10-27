# MiniMax CLI (mmx) 能力演示报告

环境：`mmx 1.0.25` / Node CLI / region = `cn` / base_url = `https://api.minimaxi.com`
认证：API key 持久化在 `~/.mmx/config.json`（`mmx auth status` 显示 `method: api-key, source: config.json`）
所有产物由 `mmx_demo.sh` 生成（`FORCE=1 bash mmx_demo.sh` 可重跑，已存在的产物默认跳过以免重复消耗额度）。

---

## 1. 文本对话 —— text2sql 场景生成 SQL

```bash
mmx text chat --non-interactive --quiet --output json \
  --system "你是一名数据平台工程师，只输出可执行的 MySQL SQL，不要解释。" \
  --message "user:表 orders(id, user_id, pay_amount, status, created_at) 中 status=1 表示已支付，写出统计 2024 年第二季度已支付订单总金额的 SQL。" \
  --model MiniMax-M3
```

输出（`text/chat_text2sql.json`）：

```sql
SELECT SUM(pay_amount) AS total_paid_amount
FROM orders
WHERE status = 1
  AND created_at >= '2024-04-01 00:00:00'
  AND created_at < '2024-07-01 00:00:00';
```

半开区间 `>= 上季度初 AND < 下季度初` 是正确写法，季度边界无缝隙、无重复。

## 2. 工具调用（Tool Use）

```bash
mmx text chat --non-interactive --output json \
  --system "你可以调用 get_sales_metric 工具获取销售额指标定义。" \
  --message "user:帮我查一下第二季度GMV的口径" \
  --tool '{"name":"get_sales_metric",...}'
```

响应体是 Anthropic 风格信封：`content` 数组里同时出现 `text` 和 `tool_use` 块，
`tool_use.input = {"metric_name": "GMV"}`，`stop_reason = "tool_use"`。
→ 智能体循环（模型 → 调工具 → 回填结果 → 继续生成）可以直接在这套结构上写。
产物：`text/chat_tool_call.json`

## 3. 图像生成

```bash
mmx image generate --non-interactive --quiet \
  --prompts "Flat vector illustration ... absolutely no text or letters anywhere ..." \
  --n 2 --aspect-ratio 16:9 --out-dir demo_out/images --out-prefix text2sql_arch_v2
```

产物：`images/text2sql_arch_v2_001.jpg`、`_002.jpg`（16:9，蓝紫渐变，纯插画无文字）。

**踩坑**：`image-01` 对中文文字渲染不可靠。第一版 prompt 要求"中文标签"，
出来的是 `MHFRI bocadatle`、`Qdrant` 这类乱码英文；改成"绝对不要任何文字"的插画描述后正常。
→ 需要带文字的图，走"让模型画图 + 叠字"或在图生成后再用代码加文字。

## 4. 语音合成（带字幕）

```bash
mmx speech synthesize --non-interactive --quiet \
  --text "本项目是自然语言转SQL。..." \
  --voice "Chinese (Mandarin)_News_Anchor" --text-normalization --subtitles \
  --format mp3 --out demo_out/audio/project_intro.mp3
```

产物：`audio/project_intro.mp3`（218 KB，13.7 s）+ `audio/project_intro.srt`（自动字幕时间轴）。
中文场景用 `Chinese (Mandarin)_*` 系列音色；`mmx speech voices` 可列出全部音色。

## 5. 视频生成

```bash
mmx video generate --non-interactive --quiet --model MiniMax-H3 \
  --prompts "数据分析师在屏幕上用自然语言提问 ..." \
  --duration 6 --ratio 16:9 --download demo_out/video/text2sql_pipeline.mp4
```

产物：`video/text2sql_pipeline.mp4`（3.5 MB，6 s，16:9）。
**耗时约 5 分钟**，建议 `--async` 拿 taskId 后用 `mmx video task get --task-id` 轮询，别在前台等。

## 6. 联网搜索

```bash
mmx search query --non-interactive --quiet --output json --q "text2sql 元数据 知识库 RAG 检索 实践"
```

产物：`search/search_result.json`，`organic[]` 里是 `{title, link, snippet}`。
底层 `/v1/coding_plan/search` **单次最多 10 条且不支持分页**，想看别的结果只能改 query。

## 7. 图像理解（VLM）

```bash
mmx vision describe --non-interactive --quiet --output json \
  --image demo_out/images/text2sql_arch_v2_001.jpg \
  --prompts "这张图里有哪些组件？数据流向是怎样的？"
```

产物：`vision/describe_arch.json`。本地图片自动 base64 编码上传；也可以用 `--file-id` 跳过编码。

## 8. 额度与工具 Schema

```bash
mmx quota show --output json          # meta/quota.json —— 5 小时/周额度、剩余百分比
mmx config export-schema              # meta/tool_schemas.json —— 13 个工具的 JSON Schema
```

`config export-schema` 导出的是 Anthropic/OpenAI 兼容的 tool schema，
可直接注册进 LangChain / 自建 agent 框架，命令名如 `mmx_text_chat`、`mmx_image_generate`。

---

## 关键结论（对后续接 LangChain 有用）

| 项目 | 结论 |
|---|---|
| OpenAI 兼容 Chat | `https://api.minimaxi.com/v1/chat/completions` ✅ 可用，模型 `MiniMax-M3 / M2.7 / M2.7-highspeed / M3.1-Flash` |
| 模型列表 | `GET https://api.minimaxi.com/v1/models` ✅ |
| Embedding | `POST https://api.minimaxi.com/v1/embeddings`，模型 `embo-01`，**维度 1536**；参数是 `texts`（不是 `input`）+ `type`(`db` 入库 / `query` 检索)；返回 `{"vectors": [[...]]}` ✅ |
| Rerank | `/v1/rerank` 在 `api.minimaxi.com` 和 `api.minimax.io` 都 **404**，当前 key 走不通，重排需另找方案 |
| Anthropic 兼容 | `https://api.minimax.io/anthropic/v1/messages` 存在，但对 CN 区域 key 返回 **401**（key 绑区域） |
| `--quiet` 行为不一致 | `text chat --quiet --output json` 会退化成**纯文本**（丢 JSON 外壳）；`vision/search/image --quiet --output json` 仍输出 JSON。**要完整响应体就别加 `--quiet`** |

## 一条命令跑全部演示

```bash
bash mmx_demo.sh            # 跳过已存在产物
FORCE=1 bash mmx_demo.sh   # 全部重跑（会消耗额度）
```
