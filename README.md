# qylg_ai_service

一个基于 FastAPI 的 AI 服务，当前提供两类能力：

- 商品查询语义解析：把自然语言购买需求转换成结构化查询条件
- 定制商品需求抽取：从用户描述中提取定制下单所需字段

项目通过兼容 OpenAI SDK 的大模型接口完成推理，适合接在电商、礼品、定制商品等业务场景后面作为 AI 能力层。

## 功能概览

### 1. 商品查询解析

接口会将用户输入的自然语言查询解析为结构化字段，例如：

- 商品类型：`mass` / `custom`
- 关键词：`keyword`
- 用途：`purpose`
- 价格区间：`price_min` / `price_max`
- 尺寸范围：`size_range`
- 制作时间：`make_time`

适合用于搜索前置解析、筛选条件补全、查询改写等场景。

### 2. 定制商品字段抽取

接口会结合候选项列表，从用户描述中抽取或匹配：

- 用途
- 风格
- 材质
- 预算区间
- 颜色
- 纹样
- 尺寸
- 备注
- AI 补充说明

适合用于定制订单预填、智能客服辅助录单、表单自动补全等场景。

## 项目结构

```text
qylg_ai_service/
├─ api/                     # 路由层
├─ core/                    # 配置、异常等基础能力
├─ schemas/                 # 请求/响应模型
├─ services/                # 业务服务与大模型调用
├─ utils/                   # JSON 提取、结果清洗等工具函数
├─ main.py                  # FastAPI 应用入口
├─ .env                     # 本地环境变量
└─ test_main.http           # 简单接口调试文件
```

## 技术栈

- Python 3.13（仓库中存在 `cpython-313` 缓存文件）
- FastAPI
- Pydantic
- OpenAI Python SDK
- python-dotenv
- Uvicorn

## 环境变量

项目启动前需要准备 `.env` 文件，示例：

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
APP_NAME=ai-service
APP_PORT=9000
APP_ENV=dev
```

字段说明：

- `LLM_API_KEY`：大模型服务密钥
- `LLM_BASE_URL`：兼容 OpenAI SDK 的服务地址
- `LLM_MODEL`：实际调用的模型名称
- `APP_NAME`：服务名称
- `APP_PORT`：启动端口
- `APP_ENV`：运行环境标识

建议不要提交真实密钥到代码仓库。

## 安装与启动

### 1. 创建虚拟环境

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 2. 安装依赖

当前仓库未包含 `requirements.txt`，可先按项目实际 import 安装最小依赖：

```bash
pip install fastapi uvicorn openai python-dotenv pydantic
```

### 3. 启动服务

```bash
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

如果希望和 `.env` 中配置保持一致，可以把端口改成 `APP_PORT` 对应的值。

## 接口说明

### 健康检查

`GET /health`

响应示例：

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "service": "ai-service",
    "env": "dev"
  }
}
```

### 1. 商品查询解析

`POST /api/parse/product-query`

请求体：

```json
{
  "text": "想买一个送女生的中式木质摆件，预算 200 以内"
}
```

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "type": "mass",
    "keyword": "木质中式摆件",
    "title": null,
    "purpose": "送礼",
    "price_min": null,
    "price_max": 200,
    "size_range": "小型摆件",
    "make_time": null,
    "sort_by": "recommend",
    "status": 1
  }
}
```

### 2. 定制商品字段抽取

`POST /api/ai/custom-product`

请求体：

```json
{
  "text": "想做一个送朋友的中式风格定制摆件，预算 300 以内，偏木质，颜色想要红色和金色",
  "purposeList": ["送礼", "自用", "乔迁"],
  "styleList": ["中式", "现代", "极简"],
  "materialList": ["木质", "陶瓷", "金属"],
  "budgetRangeList": ["100以内", "100-300", "300-500"],
  "colorList": ["红色", "金色", "黑色"],
  "patternList": ["祥云", "花鸟", "山水"]
}
```

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "purpose": "送礼",
    "style": "中式",
    "material": "木质",
    "budgetRange": "100-300",
    "size": null,
    "remark": null,
    "colors": ["红色", "金色"],
    "patterns": [],
    "aiRemark": "适合作为中式礼品定制方向"
  }
}
```

## 运行机制

- 路由层负责接收参数并返回统一响应结构
- 服务层负责构造 Prompt、调用大模型接口、解析返回结果
- 工具层负责从模型输出中提取 JSON，并做字段归一化和候选项校验
- 异常会统一转换为标准 JSON 响应


## 调试入口

服务启动后可访问：

- Swagger UI: `http://127.0.0.1:9000/docs`
- OpenAPI JSON: `http://127.0.0.1:9000/openapi.json`
- Health Check: `http://127.0.0.1:9000/health`

