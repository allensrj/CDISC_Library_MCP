# CDISC Library MCP

基于 [CDISC Library API](https://api.library.cdisc.org/) 的 MCP（Model Context Protocol）服务，为 AI 助手提供 SDTM、ADaM、CDASH、Controlled Terminology 等标准查询能力，MCP内部调用CDISC Library API获取CDISC数据库信息。
本项目由Allen Sun完成，非CDISC官方提供。

## 安装

```bash
pip install allensrj-cdisc-library-mcp
```

或使用 uv：

```bash
uv add allensrj-cdisc-library-mcp
```

## 配置 API Key（必填）

**本包不包含任何 API Key**，用户需自行在 [CDISC Library](https://library.cdisc.org/) 注册并获取 API Key，然后通过以下任一方式配置：

### 方式一：环境变量

```bash
export CDISC_API_KEY=你的API_KEY
allensrj-cdisc-library-mcp
```

### 方式二：`.env` 文件（推荐本地开发）

在运行目录或项目根目录创建 `.env` 文件：

```bash
CDISC_API_KEY=你的API_KEY
```

（可参考项目中的 `.env.example`，切勿将 `.env` 提交到 Git。）

## 运行

安装并配置好 `CDISC_API_KEY` 后：

```bash
allensrj-cdisc-library-mcp
```

默认使用 `stdio` 传输。若需其他传输方式，可在代码中修改 `main.py` 的 `run()` 或通过 MCP 客户端配置。

## 提供的工具概览

| 类别 | 工具示例 |
|------|----------|
| 产品列表 | `get_product_list` |
| SDTM / SEND | `get_sdtmig_class_info`, `get_sdtmig_dataset_info`, `get_sdtm_model_*`, `get_sendig_*` |
| CDASH / CDASHIG | `get_cdashig_class_info`, `get_cdashig_domain_info`, `get_cdash_model_*` |
| ADaM | `get_adam_product_info`, `get_adam_datastructure_info` |
| QRS | `get_qrs_info` |
| Controlled Terminology | `get_package_ct_info`, `get_package_ct_codelist_info`, `get_package_ct_codelist_term_info` |


## 项目结构

```
├── main.py          # 入口：注册工具、启动服务
├── config.py        # 配置：CDISC_API_KEY、常量
├── utils/           # 通用：HTTP 客户端、响应格式化
├── tools/           # 业务：sdtm, adam, terminology, general
├── pyproject.toml   # 包元数据与 allensrj-cdisc-library-mcp 入口
└── README.md
```

## License

见 [LICENSE](LICENSE) 文件。
