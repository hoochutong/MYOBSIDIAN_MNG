"""
유틸리티 함수 모음
Utility functions collection
"""

import os
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

def sanitize_filename(filename: str) -> str:
    """
    파일명에서 특수문자 제거 및 정리
    Remove special characters from filename and clean it
    
    Args:
        filename (str): 원본 파일명 / Original filename
        
    Returns:
        str: 정리된 파일명 / Cleaned filename
    """
    # 특수문자를 언더스코어로 변경
    # Replace special characters with underscore
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 연속된 언더스코어 제거
    # Remove consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # 앞뒤 공백 및 점 제거
    # Remove leading/trailing spaces and dots
    cleaned = cleaned.strip(' .')
    
    return cleaned

def extract_obsidian_tags(content: str) -> List[str]:
    """
    옵시디언 노트에서 태그 추출
    Extract tags from Obsidian note
    
    Args:
        content (str): 노트 내용 / Note content
        
    Returns:
        List[str]: 태그 목록 / List of tags
    """
    tags = []
    
    # #태그 형식 추출
    # Extract #tag format
    hashtag_pattern = r'#([a-zA-Z0-9가-힣_\-/]+)'
    hashtags = re.findall(hashtag_pattern, content)
    tags.extend(hashtags)
    
    # YAML frontmatter에서 태그 추출 (기본적으로 frontmatter 라이브러리에서 처리)
    # Extract tags from YAML frontmatter (handled by frontmatter library)
    
    return list(set(tags))  # 중복 제거

def extract_wikilinks(content: str) -> List[Dict[str, str]]:
    """
    위키링크 [[링크]] 형식 추출
    Extract wikilinks [[link]] format
    
    Args:
        content (str): 노트 내용 / Note content
        
    Returns:
        List[Dict]: 링크 정보 목록 / List of link information
    """
    links = []
    
    # [[링크명|표시명]] 또는 [[링크명]] 형식
    # [[linkname|displayname]] or [[linkname]] format
    wikilink_pattern = r'\[\[([^\]|]+)(\|([^\]]+))?\]\]'
    matches = re.findall(wikilink_pattern, content)
    
    for match in matches:
        link_name = match[0].strip()
        display_name = match[2].strip() if match[2] else link_name
        
        links.append({
            'link': link_name,
            'display': display_name,
            'type': 'wikilink'
        })
    
    return links

def calculate_file_hash(file_path: Path) -> str:
    """
    파일의 MD5 해시 계산
    Calculate MD5 hash of file
    
    Args:
        file_path (Path): 파일 경로 / File path
        
    Returns:
        str: MD5 해시 값 / MD5 hash value
    """
    hash_md5 = hashlib.md5()
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""

def format_file_size(size_bytes: int) -> str:
    """
    바이트를 읽기 쉬운 형식으로 변환
    Convert bytes to human readable format
    
    Args:
        size_bytes (int): 바이트 크기 / Size in bytes
        
    Returns:
        str: 형식화된 크기 / Formatted size
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def get_creation_date(file_path: Path) -> Optional[datetime]:
    """
    파일 생성 날짜 반환
    Return file creation date
    
    Args:
        file_path (Path): 파일 경로 / File path
        
    Returns:
        datetime: 생성 날짜 / Creation date
    """
    try:
        stat = file_path.stat()
        # macOS에서는 st_birthtime, 다른 OS에서는 st_ctime 사용
        # Use st_birthtime on macOS, st_ctime on other OS
        if hasattr(stat, 'st_birthtime'):
            return datetime.fromtimestamp(stat.st_birthtime)
        else:
            return datetime.fromtimestamp(stat.st_ctime)
    except Exception:
        return None

def is_duplicate_content(file1: Path, file2: Path) -> bool:
    """
    두 파일의 내용이 동일한지 확인
    Check if two files have identical content
    
    Args:
        file1 (Path): 첫 번째 파일 / First file
        file2 (Path): 두 번째 파일 / Second file
        
    Returns:
        bool: 동일 여부 / Whether identical
    """
    try:
        return calculate_file_hash(file1) == calculate_file_hash(file2)
    except Exception:
        return False

def find_broken_links(vault_path: Path, note_content: str, note_path: Path) -> List[str]:
    """
    깨진 링크 찾기
    Find broken links
    
    Args:
        vault_path (Path): 볼트 경로 / Vault path
        note_content (str): 노트 내용 / Note content
        note_path (Path): 현재 노트 경로 / Current note path
        
    Returns:
        List[str]: 깨진 링크 목록 / List of broken links
    """
    broken_links = []
    links = extract_wikilinks(note_content)
    
    for link_info in links:
        link_name = link_info['link']
        
        # .md 확장자 추가하여 검색
        # Search with .md extension added
        possible_paths = [
            vault_path / f"{link_name}.md",
            vault_path / link_name,
            note_path.parent / f"{link_name}.md",
            note_path.parent / link_name
        ]
        
        # 모든 가능한 경로 확인
        # Check all possible paths
        link_exists = any(path.exists() for path in possible_paths)
        
        if not link_exists:
            broken_links.append(link_name)
    
    return broken_links

def create_note_template(title: str, tags: List[str] = None, template_type: str = "basic") -> str:
    """
    노트 템플릿 생성
    Create note template
    
    Args:
        title (str): 노트 제목 / Note title
        tags (List[str]): 태그 목록 / List of tags
        template_type (str): 템플릿 유형 / Template type
        
    Returns:
        str: 템플릿 내용 / Template content
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M")
    
    tags = tags or []
    tags_str = ", ".join(f'"{tag}"' for tag in tags) if tags else ""
    
    templates = {
        "basic": f"""---
title: "{title}"
created: "{time_str}"
tags: [{tags_str}]
---

# {title}

## 개요 / Overview

## 내용 / Content

## 관련 링크 / Related Links

## 참고 사항 / Notes

""",
        
        "project": f"""---
title: "{title}"
created: "{time_str}"
tags: [{tags_str}, "project"]
status: "진행중"
priority: "보통"
due_date: ""
---

# 📋 {title}

## 🎯 프로젝트 목표 / Project Goals

## 📅 일정 / Timeline
- 시작일: {date_str}
- 마감일: 
- 현재 상태: 진행중

## ✅ 할 일 목록 / Todo List
- [ ] 

## 📝 진행 상황 / Progress Notes

## 🔗 관련 자료 / Related Resources

## 📊 결과 / Results

""",
        
        "meeting": f"""---
title: "{title}"
created: "{time_str}"
tags: [{tags_str}, "meeting"]
date: "{date_str}"
attendees: []
---

# 🤝 {title}

## 📅 회의 정보 / Meeting Info
- 날짜: {date_str}
- 참석자: 
- 장소: 

## 📋 안건 / Agenda
1. 

## 📝 회의 내용 / Meeting Notes

## ✅ 액션 아이템 / Action Items
- [ ] 

## 🔗 관련 자료 / Related Materials

"""
    }
    
    return templates.get(template_type, templates["basic"])

def validate_frontmatter(content: str) -> Tuple[bool, List[str]]:
    """
    Frontmatter 유효성 검사
    Validate frontmatter
    
    Args:
        content (str): 노트 내용 / Note content
        
    Returns:
        Tuple[bool, List[str]]: (유효성, 오류 목록) / (validity, error list)
    """
    errors = []
    
    if not content.startswith('---'):
        return True, []  # frontmatter가 없는 경우는 유효
    
    try:
        import frontmatter
        post = frontmatter.loads(content)
        
        # 필수 필드 확인
        # Check required fields
        if 'title' not in post.metadata:
            errors.append("title 필드가 없습니다")
        
        # 날짜 형식 확인
        # Check date format
        date_fields = ['created', 'modified', 'due_date']
        for field in date_fields:
            if field in post.metadata:
                date_value = post.metadata[field]
                if isinstance(date_value, str) and date_value:
                    try:
                        datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                    except ValueError:
                        errors.append(f"{field} 날짜 형식이 올바르지 않습니다")
        
    except Exception as e:
        errors.append(f"frontmatter 파싱 오류: {str(e)}")
    
    return len(errors) == 0, errors 