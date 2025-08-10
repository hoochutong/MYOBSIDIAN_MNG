"""
옵시디언 노트 관리 시스템 설정
Configuration for Obsidian note management system
"""

import os
from pathlib import Path

# 옵시디언 볼트 기본 경로 (메모리 정보 기반)
# Default Obsidian vault path (based on memory information)
OBSIDIAN_VAULT_PATH = "/Users/alliej/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second Brain"

# PARA 메소드 기반 폴더 구조
# PARA method folder structure
PARA_FOLDERS = {
    "projects": "10-Projects",
    "areas": "20-Areas", 
    "resources": "30-Resources",
    "archive": "40-Archive"
}

# 지원하는 파일 확장자
# Supported file extensions
SUPPORTED_EXTENSIONS = ['.md', '.txt']

# 백업 설정
# Backup settings  
BACKUP_ENABLED = True
BACKUP_DIR = os.path.join(os.getcwd(), "backups")

# 로그 설정
# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = "obsidian_manager.log"

def get_vault_path():
    """볼트 경로 반환 (존재 여부 확인)"""
    """Return vault path (check if exists)"""
    vault_path = Path(OBSIDIAN_VAULT_PATH)
    if vault_path.exists():
        return str(vault_path)
    else:
        print(f"⚠️  볼트 경로를 찾을 수 없습니다: {OBSIDIAN_VAULT_PATH}")
        print(f"⚠️  Vault path not found: {OBSIDIAN_VAULT_PATH}")
        return None

def get_para_folder_path(folder_type):
    """PARA 폴더 경로 반환"""
    """Return PARA folder path"""
    vault_path = get_vault_path()
    if vault_path and folder_type in PARA_FOLDERS:
        return os.path.join(vault_path, PARA_FOLDERS[folder_type])
    return None 