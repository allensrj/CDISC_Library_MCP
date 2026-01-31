"""统一 HTTP 请求：封装 CDISC Library API 的 GET、重试与错误处理。"""

from __future__ import annotations

import httpx

from config import CDISC_API_KEY, get_headers, DEFAULT_TIMEOUT


async def cdisc_get(
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    headers: dict | None = None,
) -> dict | list | str:
    """
    对 CDISC Library 发起 GET 请求，统一处理超时、HTTP 错误与网络错误。
    成功时返回解析后的 JSON（dict/list），失败时返回错误信息字符串。
    业务层可对返回值做 truncate/prune 后再序列化。
    """
    if not CDISC_API_KEY:
        return "Error: CDISC_API_KEY environment variable not found."

    hdr = headers or get_headers()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=hdr, timeout=timeout)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        return "Error: The request to CDISC Library timed out. Please try again later."
    except httpx.HTTPStatusError as e:
        return f"API Error: CDISC Library returned status {e.response.status_code}. {e.response.text}"
    except httpx.RequestError as e:
        return f"Network Error: Unable to connect to CDISC Library. Details: {e}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"
