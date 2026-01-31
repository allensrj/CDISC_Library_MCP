"""CDISC 响应格式化：截断与瘦身逻辑。"""

import json

from config import MAX_RESPONSE_JSON_LENGTH, TRUNCATE_SUFFIX, TRUNCATE_SUFFIX_CT


def truncate_json_response(
    data: dict | list,
    max_length: int | None = None,
    suffix: str | None = None,
) -> str:
    """
    将 data 序列化为 JSON 字符串；若超过 max_length 则截断并追加 suffix。
    """
    max_length = max_length or MAX_RESPONSE_JSON_LENGTH
    suffix = suffix or TRUNCATE_SUFFIX
    s = json.dumps(data, ensure_ascii=False)
    if len(s) > max_length:
        return s[:max_length] + suffix
    return s


def truncate_json_string(s: str, max_length: int | None = None, suffix: str | None = None) -> str:
    """对已是 JSON 字符串的结果做长度截断。"""
    max_length = max_length or MAX_RESPONSE_JSON_LENGTH
    suffix = suffix or TRUNCATE_SUFFIX
    if len(s) > max_length:
        return s[:max_length] + suffix
    return s


# ---------- ADaM 响应瘦身 ----------


def remove_all_analysis_variables(obj):
    """删除所有 analysisVariables 里的内容（清空该层级）。"""
    if isinstance(obj, dict):
        if "analysisVariables" in obj:
            obj["analysisVariables"] = []
        for v in obj.values():
            remove_all_analysis_variables(v)
    elif isinstance(obj, list):
        for item in obj:
            remove_all_analysis_variables(item)


def remove_links_parent_refs(obj, parent_key=None):
    """只保留 analysisVariables 层级里每个元素的 _links.self，其他键删除。"""
    if isinstance(obj, dict):
        if parent_key == "analysisVariables" and "_links" in obj and isinstance(obj["_links"], dict):
            links = obj["_links"]
            obj["_links"] = {"self": links["self"]} if "self" in links else {}
        for k, v in obj.items():
            remove_links_parent_refs(v, k)
    elif isinstance(obj, list):
        for item in obj:
            remove_links_parent_refs(item, parent_key)


# ---------- CT Package 瘦身（仅保留 conceptId, submissionValue）----------


def prune_ct_codelists(raw_data: dict) -> dict:
    """仅保留 codelists 及 terms 中的 conceptId、submissionValue。"""
    minimized = []
    for cl in raw_data.get("codelists", []):
        clean_cl = {
            "conceptId": cl.get("conceptId"),
            "submissionValue": cl.get("submissionValue"),
            "terms": [],
        }
        for term in cl.get("terms", []):
            clean_cl["terms"].append({
                "conceptId": term.get("conceptId"),
                "submissionValue": term.get("submissionValue"),
            })
        minimized.append(clean_cl)
    return {"codelists": minimized}
