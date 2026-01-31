"""CDISC Library MCP 配置：环境变量与常量。"""

import os
from dotenv import load_dotenv

load_dotenv()

# API
CDISC_API_KEY = os.getenv("CDISC_API_KEY")
CDISC_API_BASE = "https://api.library.cdisc.org/api/mdr"

# 请求
DEFAULT_TIMEOUT = 15.0
CT_TIMEOUT = 30.0

# 响应
MAX_RESPONSE_JSON_LENGTH = 130_000
TRUNCATE_SUFFIX = "... The data is too long, please shorten the request."
TRUNCATE_SUFFIX_CT = "\n... [Truncated]"


def get_headers():
    """返回 CDISC API 请求头（需在调用前确保 CDISC_API_KEY 已配置）。"""
    return {
        "Cache-Control": "no-cache",
        "api-key": CDISC_API_KEY or "",
        "Accept": "application/json",
    }
