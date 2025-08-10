#!/usr/bin/env python3
"""
설치 스크립트
Installation script for Obsidian Note Manager
"""

from setuptools import setup, find_packages

# README 파일 읽기
# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# requirements.txt에서 의존성 읽기
# Read dependencies from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="obsidian-note-manager",
    version="1.0.0",
    author="Allie J",
    author_email="",
    description="옵시디언 노트를 체계적으로 관리하고 정리하는 Python 기반 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "obsidian-manager=main:cli",
        ],
    },
    keywords="obsidian, notes, markdown, para, productivity, knowledge-management",
    project_urls={
        "Bug Reports": "",
        "Source": "",
    },
) 