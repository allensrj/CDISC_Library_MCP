"""
CDISC Library MCP 入口：仅负责注册工具与启动服务。

业务逻辑在 tools/ 中按标准分块（sdtm / adam / terminology / general），
通用 HTTP 与格式化逻辑在 utils/ 与 config 中。
"""

import config  # noqa: F401 - 加载环境变量
from mcp.server.fastmcp import FastMCP

from tools import sdtm, adam, terminology, general

mcp = FastMCP("CDISC Library")


# Product List
mcp.tool()(general.get_product_list)

# SDTM / SEND
mcp.tool()(sdtm.get_sdtmig_class_info)
mcp.tool()(sdtm.get_sdtmig_dataset_info)
mcp.tool()(sdtm.get_sdtm_model_class_info)
mcp.tool()(sdtm.get_sdtm_model_dataset_info)
mcp.tool()(sdtm.get_sendig_class_info)
mcp.tool()(sdtm.get_sendig_dataset_info)

# CDASH / CDASHIG
mcp.tool()(general.get_cdashig_class_info)
mcp.tool()(general.get_cdashig_domain_info)
mcp.tool()(general.get_cdashig_scenarios_info)
mcp.tool()(general.get_cdash_model_class_info)
mcp.tool()(general.get_cdash_model_domain_info)

# ADaM
mcp.tool()(adam.get_adam_product_info)
mcp.tool()(adam.get_adam_datastructure_info)

# QRS
mcp.tool()(general.get_qrs_info)

# Controlled Terminology
mcp.tool()(terminology.get_package_ct_info)
mcp.tool()(terminology.get_package_ct_codelist_info)
mcp.tool()(terminology.get_package_ct_codelist_term_info)


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    """Generate a greeting prompt"""
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."


def run():
    """供 PyPI 安装后的命令行入口 `allensrj-cdisc-library-mcp` 调用。"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
