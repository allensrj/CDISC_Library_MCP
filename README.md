# CDISC Library MCP

基于 [CDISC Library API](https://api.library.cdisc.org/) 的 MCP（Model Context Protocol）服务，为 AI 助手提供 SDTM、ADaM、CDASH、Controlled Terminology 等标准查询能力。

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

默认使用 `streamable-http` 传输。若需其他传输方式，可在代码中修改 `main.py` 的 `run()` 或通过 MCP 客户端配置。

## 提供的工具概览

| 类别 | 工具示例 |
|------|----------|
| 产品列表 | `get_product_list` |
| SDTM / SEND | `get_sdtmig_class_info`, `get_sdtmig_dataset_info`, `get_sdtm_model_*`, `get_sendig_*` |
| CDASH / CDASHIG | `get_cdashig_class_info`, `get_cdashig_domain_info`, `get_cdash_model_*` |
| ADaM | `get_adam_product_info`, `get_adam_datastructure_info` |
| QRS | `get_qrs_info` |
| Controlled Terminology | `get_package_ct_info`, `get_package_ct_codelist_info`, `get_package_ct_codelist_term_info` |

---

## 发布到 PyPI（维护者）

### 1. 准备

- 在 [PyPI](https://pypi.org/) 注册账号（首次发布需单独注册）
- 安装构建与上传工具：`pip install build twine`

### 2. 构建

在项目根目录执行：

```bash
# 清理旧构建（可选）
rm -rf dist/

# 构建 wheel 与 sdist
python -m build
```

生成文件在 `dist/` 下（如 `cdisc_mcp-0.1.0-py3-none-any.whl`、`allensrj-cdisc-library-mcp-0.1.0.tar.gz`）。

### 3. 上传

**测试环境（推荐先测）：**

```bash
twine upload --repository testpypi dist/*
```

在 [TestPyPI](https://test.pypi.org/) 注册账号后，用 TestPyPI 的用户名和密码或 token 上传。验证安装：

```bash
pip install -i https://test.pypi.org/simple/ allensrj-cdisc-library-mcp
```

**正式 PyPI：**

```bash
twine upload dist/*
```

使用 PyPI 的用户名和密码或 [API Token](https://pypi.org/manage/account/token/)。上传成功后即可 `pip install allensrj-cdisc-library-mcp`。

### 4. 版本与元数据

- 版本号在 `pyproject.toml` 的 `[project]` 里改 `version = "0.1.0"`，每次发布前更新。
- 描述、依赖、入口点等均在 `pyproject.toml` 中维护。

---

## 在 ModelScope 托管为 MCP

将包发布到 PyPI 后，可交给 ModelScope 托管为 MCP 服务。此时：

- **API Key 由使用方提供**：ModelScope 侧一般会在「添加 MCP / 配置服务」时提供填写 **环境变量** 或 **密钥** 的入口，用户在那里填写 `CDISC_API_KEY`，由平台在运行 MCP 时注入环境变量。
- 本包只负责：安装后通过 `allensrj-cdisc-library-mcp` 启动服务，并读取环境变量 `CDISC_API_KEY`。不包含、不硬编码任何 Key。

若 ModelScope 文档中要求提供「启动命令」和「环境变量」：

- **启动命令**：`allensrj-cdisc-library-mcp`（或 `python -m main`，若平台未将 `allensrj-cdisc-library-mcp` 放在 PATH）
- **环境变量**：`CDISC_API_KEY` = 用户自己的 CDISC Library API Key

具体界面和字段名称以 ModelScope 当前文档为准。

---

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
