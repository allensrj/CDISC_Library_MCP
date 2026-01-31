"""显式提供 Name/Version，避免部分环境下 pyproject.toml 元数据未写入 wheel/sdist。"""
from setuptools import setup

setup(
    name="allensrj-cdisc-library-mcp",
    version="0.1.0",
)
