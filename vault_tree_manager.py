"""
옵시디언 볼트 트리 구조 관리자
Obsidian Vault Tree Structure Manager
"""

import os
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import SUPPORTED_EXTENSIONS, get_vault_path
from management_log import ManagementLogger

class VaultTreeEventHandler(FileSystemEventHandler):
    """볼트 파일 시스템 이벤트 핸들러"""
    """Vault file system event handler"""
    
    def __init__(self, tree_manager):
        """
        이벤트 핸들러 초기화
        Initialize event handler
        
        Args:
            tree_manager: VaultTreeManager 인스턴스
        """
        super().__init__()
        self.tree_manager = tree_manager
        self.last_update = time.time()
        self.update_delay = 2.0  # 2초 딜레이로 중복 업데이트 방지
    
    def on_any_event(self, event):
        """
        모든 파일 시스템 이벤트 처리
        Handle all file system events
        """
        # 숨김 파일이나 시스템 파일 무시
        # Ignore hidden files or system files
        if '/.obsidian' in event.src_path or '/.git' in event.src_path:
            return
        
        # 지원하는 파일 확장자만 처리
        # Process only supported file extensions
        if event.is_directory or any(event.src_path.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
            current_time = time.time()
            if current_time - self.last_update > self.update_delay:
                self.last_update = current_time
                # 딜레이 후 업데이트 (중복 방지)
                # Update after delay (prevent duplicates)
                threading.Timer(self.update_delay, self.tree_manager.update_tree_structure).start()

class VaultTreeManager:
    """옵시디언 볼트 트리 구조 관리 클래스"""
    """Obsidian vault tree structure management class"""
    
    def __init__(self, vault_path: str):
        """
        VaultTreeManager 초기화
        Initialize VaultTreeManager
        
        Args:
            vault_path (str): 옵시디언 볼트 경로 / Obsidian vault path
        """
        self.vault_path = Path(vault_path)
        # 프로젝트 폴더 내에 트리 파일 생성
        # Create tree file in project folder
        self.tree_file = Path.cwd() / "볼트구조.md"
        self.observer = None
        self.is_watching = False
        
        # 관리 로거 초기화
        # Initialize management logger
        self.management_logger = ManagementLogger()
        
        # 무시할 디렉토리/파일 패턴
        # Ignore patterns for directories/files
        self.ignore_patterns = {
            '.obsidian', '.git', '.DS_Store', '__pycache__',
            'node_modules', '.vscode', '.idea'
        }
        
        if not self.vault_path.exists():
            raise ValueError(f"볼트 경로를 찾을 수 없습니다: {vault_path}")
    
    def _should_ignore(self, path: Path) -> bool:
        """
        경로를 무시해야 하는지 확인
        Check if path should be ignored
        
        Args:
            path (Path): 확인할 경로 / Path to check
            
        Returns:
            bool: 무시해야 하면 True / True if should be ignored
        """
        for part in path.parts:
            if part in self.ignore_patterns or part.startswith('.'):
                return True
        return False
    
    def _generate_tree_structure(self, directory: Path, prefix: str = "", is_last: bool = True) -> List[str]:
        """
        디렉토리 트리 구조 생성
        Generate directory tree structure
        
        Args:
            directory (Path): 스캔할 디렉토리 / Directory to scan
            prefix (str): 트리 라인 접두사 / Tree line prefix
            is_last (bool): 마지막 항목인지 여부 / Whether it's the last item
            
        Returns:
            List[str]: 트리 구조 라인들 / Tree structure lines
        """
        lines = []
        
        try:
            # 디렉토리 내 모든 항목 가져오기
            # Get all items in directory
            items = []
            for item in directory.iterdir():
                if not self._should_ignore(item):
                    items.append(item)
            
            # 디렉토리와 파일 분리 및 정렬
            # Separate and sort directories and files
            directories = sorted([item for item in items if item.is_dir()])
            files = sorted([item for item in items if item.is_file() and 
                          any(item.name.endswith(ext) for ext in SUPPORTED_EXTENSIONS)])
            
            all_items = directories + files
            
            for i, item in enumerate(all_items):
                is_last_item = i == len(all_items) - 1
                
                # 트리 브랜치 문자 결정
                # Determine tree branch characters
                if is_last_item:
                    current_prefix = "└── "
                    next_prefix = prefix + "    "
                else:
                    current_prefix = "├── "
                    next_prefix = prefix + "│   "
                
                # 아이템 이름과 아이콘 결정
                # Determine item name and icon
                if item.is_dir():
                    icon = "📁"
                    item_name = f"{icon} **{item.name}**"
                else:
                    # 파일 확장자에 따른 아이콘
                    # Icon based on file extension
                    if item.suffix == '.md':
                        icon = "📝"
                    else:
                        icon = "📄"
                    item_name = f"{icon} {item.name}"
                
                lines.append(f"{prefix}{current_prefix}{item_name}")
                
                # 디렉토리인 경우 재귀적으로 하위 구조 생성
                # Recursively generate sub-structure for directories
                if item.is_dir():
                    sub_lines = self._generate_tree_structure(item, next_prefix, is_last_item)
                    lines.extend(sub_lines)
                    
        except PermissionError:
            lines.append(f"{prefix}├── ❌ 접근 권한 없음 / Permission Denied")
        except Exception as e:
            lines.append(f"{prefix}├── ⚠️ 오류: {str(e)} / Error: {str(e)}")
        
        return lines
    
    def _count_items(self, directory: Path) -> Dict[str, int]:
        """
        디렉토리 내 항목 수 계산
        Count items in directory
        
        Args:
            directory (Path): 스캔할 디렉토리 / Directory to scan
            
        Returns:
            Dict[str, int]: 항목 수 통계 / Item count statistics
        """
        stats = {
            'total_folders': 0,
            'total_files': 0,
            'md_files': 0,
            'other_files': 0
        }
        
        try:
            for item in directory.rglob('*'):
                if self._should_ignore(item):
                    continue
                
                if item.is_dir():
                    stats['total_folders'] += 1
                elif item.is_file():
                    stats['total_files'] += 1
                    if item.suffix == '.md':
                        stats['md_files'] += 1
                    elif any(item.name.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                        stats['other_files'] += 1
        except Exception:
            pass
        
        return stats
    
    def generate_tree_markdown(self) -> str:
        """
        마크다운 형식의 트리 구조 생성
        Generate tree structure in markdown format
        
        Returns:
            str: 마크다운 형식의 트리 구조 / Tree structure in markdown format
        """
        start_time = time.time()
        
        try:
            # 통계 정보 수집
            # Collect statistics
            stats = self._count_items(self.vault_path)
            
            # 마크다운 헤더 생성
            # Generate markdown header
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            markdown_content = f"""# 🌳 옵시디언 볼트 구조
# Obsidian Vault Structure

> **자동 생성된 볼트 트리 구조입니다.**  
> **Auto-generated vault tree structure.**

**📍 볼트 경로**: `{self.vault_path}`  
**🕒 마지막 업데이트**: {current_time}  
**📊 업데이트 유형**: 자동 감지 / Auto-detected

---

## 📈 볼트 통계 / Vault Statistics

| 항목 / Item | 개수 / Count |
|-------------|--------------|
| 📁 **총 폴더 수** / Total Folders | {stats['total_folders']} |
| 📄 **총 파일 수** / Total Files | {stats['total_files']} |
| 📝 **마크다운 파일** / Markdown Files | {stats['md_files']} |
| 📋 **기타 파일** / Other Files | {stats['other_files']} |

---

## 🌲 폴더 트리 구조 / Folder Tree Structure

```
🏠 {self.vault_path.name}
"""
            
            # 트리 구조 생성
            # Generate tree structure
            tree_lines = self._generate_tree_structure(self.vault_path)
            
            for line in tree_lines:
                markdown_content += line + "\n"
            
            markdown_content += """```

---

## 📝 업데이트 정보 / Update Information

- **자동 감지**: 파일 생성, 삭제, 이동 시 자동 업데이트
- **실시간 모니터링**: 볼트 내 변화를 실시간으로 감지
- **Auto Detection**: Automatically updates when files are created, deleted, or moved
- **Real-time Monitoring**: Detects changes in vault in real-time

---

## 🔧 관리 명령어 / Management Commands

```bash
# 트리 구조 수동 업데이트 / Manual tree update
python main.py update-tree

# 실시간 감지 시작 / Start real-time monitoring
python main.py watch-vault

# 실시간 감지 중지 / Stop real-time monitoring  
python main.py stop-watch
```

> 💡 **팁**: 이 파일은 자동으로 생성되므로 수동으로 편집하지 마세요!  
> **Tip**: This file is auto-generated, please don't edit manually!

---

*Generated by Obsidian Management System* 🤖
"""
            
            duration = time.time() - start_time
            
            # 관리 작업 로그 기록
            # Log management activity
            self.management_logger.log_activity(
                command='generate_tree',
                status='success',
                summary={
                    'vault_path': str(self.vault_path),
                    'total_folders': stats['total_folders'],
                    'total_files': stats['total_files'],
                    'md_files': stats['md_files'],
                    'tree_lines': len(tree_lines)
                },
                duration=duration
            )
            
            return markdown_content
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 오류 로그 기록
            # Log error
            self.management_logger.log_activity(
                command='generate_tree',
                status='error',
                summary={'vault_path': str(self.vault_path)},
                duration=duration,
                error=str(e)
            )
            
            raise e
    
    def update_tree_structure(self):
        """
        트리 구조 파일 업데이트
        Update tree structure file
        """
        try:
            markdown_content = self.generate_tree_markdown()
            
            # 마크다운 파일에 저장
            # Save to markdown file
            with open(self.tree_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
                
            print(f"🌳 트리 구조 업데이트 완료: {self.tree_file}")
            print(f"🌳 Tree structure updated: {self.tree_file}")
            
        except Exception as e:
            print(f"❌ 트리 구조 업데이트 실패: {str(e)}")
            print(f"❌ Tree structure update failed: {str(e)}")
    
    def start_watching(self):
        """
        파일 시스템 감시 시작
        Start file system monitoring
        """
        if self.is_watching:
            print("⚠️ 이미 감시 중입니다.")
            print("⚠️ Already watching.")
            return
        
        try:
            # 초기 트리 구조 생성
            # Generate initial tree structure
            self.update_tree_structure()
            
            # 감시자 설정
            # Setup observer
            self.observer = Observer()
            event_handler = VaultTreeEventHandler(self)
            self.observer.schedule(event_handler, str(self.vault_path), recursive=True)
            
            # 감시 시작
            # Start monitoring
            self.observer.start()
            self.is_watching = True
            
            print(f"👁️ 볼트 감시 시작: {self.vault_path}")
            print(f"👁️ Started watching vault: {self.vault_path}")
            print("📄 트리 구조 파일: 볼트구조.md")
            print("📄 Tree structure file: 볼트구조.md")
            
            # 관리 작업 로그 기록
            # Log management activity
            self.management_logger.log_activity(
                command='start_watching',
                status='success',
                summary={
                    'vault_path': str(self.vault_path),
                    'tree_file': str(self.tree_file)
                },
                duration=0.1
            )
            
        except Exception as e:
            print(f"❌ 감시 시작 실패: {str(e)}")
            print(f"❌ Failed to start watching: {str(e)}")
            
            # 오류 로그 기록
            # Log error
            self.management_logger.log_activity(
                command='start_watching',
                status='error',
                summary={'vault_path': str(self.vault_path)},
                duration=0.1,
                error=str(e)
            )
    
    def stop_watching(self):
        """
        파일 시스템 감시 중지
        Stop file system monitoring
        """
        if not self.is_watching or not self.observer:
            print("⚠️ 감시 중이 아닙니다.")
            print("⚠️ Not currently watching.")
            return
        
        try:
            self.observer.stop()
            self.observer.join()
            self.is_watching = False
            
            print("🛑 볼트 감시 중지됨")
            print("🛑 Stopped watching vault")
            
            # 관리 작업 로그 기록
            # Log management activity
            self.management_logger.log_activity(
                command='stop_watching',
                status='success',
                summary={'vault_path': str(self.vault_path)},
                duration=0.1
            )
            
        except Exception as e:
            print(f"❌ 감시 중지 실패: {str(e)}")
            print(f"❌ Failed to stop watching: {str(e)}")
            
            # 오류 로그 기록
            # Log error
            self.management_logger.log_activity(
                command='stop_watching',
                status='error',
                summary={'vault_path': str(self.vault_path)},
                duration=0.1,
                error=str(e)
            )
    
    def get_status(self) -> Dict:
        """
        감시 상태 정보 반환
        Return monitoring status information
        
        Returns:
            Dict: 상태 정보 / Status information
        """
        return {
            'is_watching': self.is_watching,
            'vault_path': str(self.vault_path),
            'tree_file': str(self.tree_file),
            'tree_file_exists': self.tree_file.exists(),
            'tree_file_size': self.tree_file.stat().st_size if self.tree_file.exists() else 0,
            'last_modified': datetime.fromtimestamp(
                self.tree_file.stat().st_mtime
            ).isoformat() if self.tree_file.exists() else None
        } 