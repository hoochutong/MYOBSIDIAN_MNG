"""
ObsidianManager - 옵시디언 노트 관리 핵심 클래스
Core class for Obsidian note management
"""

import os
import shutil
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter
import markdown
from config import PARA_FOLDERS, BACKUP_DIR, SUPPORTED_EXTENSIONS
from management_log import ManagementLogger

class ObsidianManager:
    """옵시디언 볼트 관리 클래스"""
    """Obsidian vault management class"""
    
    def __init__(self, vault_path: str):
        """
        ObsidianManager 초기화
        Initialize ObsidianManager
        
        Args:
            vault_path (str): 옵시디언 볼트 경로 / Obsidian vault path
        """
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(__name__)
        
        # 관리 작업 로거 초기화
        # Initialize management activity logger
        self.management_logger = ManagementLogger()
        
        if not self.vault_path.exists():
            raise ValueError(f"볼트 경로를 찾을 수 없습니다: {vault_path}")
            
        self.logger.info(f"ObsidianManager 초기화 완료: {vault_path}")
    
    def get_vault_status(self) -> Dict:
        """
        볼트 상태 정보 반환
        Return vault status information
        
        Returns:
            Dict: 볼트 상태 정보 / Vault status information
        """
        start_time = time.time()
        
        try:
            status = {
                'total_notes': 0,
                'para_folders': 0,
                'last_modified': None,
                'folder_stats': {}
            }
            
            # 전체 마크다운 파일 수 계산
            # Count total markdown files
            for ext in SUPPORTED_EXTENSIONS:
                status['total_notes'] += len(list(self.vault_path.rglob(f'*{ext}')))
            
            # PARA 폴더 존재 여부 확인
            # Check PARA folder existence
            for folder_key, folder_name in PARA_FOLDERS.items():
                folder_path = self.vault_path / folder_name
                if folder_path.exists():
                    status['para_folders'] += 1
                    # 각 폴더별 노트 수 계산
                    # Count notes in each folder
                    folder_notes = 0
                    for ext in SUPPORTED_EXTENSIONS:
                        folder_notes += len(list(folder_path.rglob(f'*{ext}')))
                    status['folder_stats'][folder_key] = folder_notes
            
            # 최근 수정 시간 확인
            # Check last modification time
            try:
                status['last_modified'] = datetime.fromtimestamp(
                    self.vault_path.stat().st_mtime
                ).isoformat()
            except:
                status['last_modified'] = "Unknown"
            
            duration = time.time() - start_time
            
            # 관리 작업 로그 기록
            # Log management activity
            self.management_logger.log_activity(
                command='status',
                status='success',
                summary={
                    'vault_path': str(self.vault_path),
                    'total_notes': status['total_notes'],
                    'para_folders': status['para_folders'],
                    'folder_stats': status['folder_stats']
                },
                duration=duration
            )
            
            self.logger.info("볼트 상태 확인 완료")
            return status
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 오류 로그 기록
            # Log error
            self.management_logger.log_activity(
                command='status',
                status='error',
                summary={'vault_path': str(self.vault_path)},
                duration=duration,
                error=str(e)
            )
            
            self.logger.error(f"볼트 상태 확인 실패: {str(e)}")
            return {'error': str(e)}
    
    def get_notes_list(self, folder: Optional[str] = None) -> List[Path]:
        """
        노트 파일 목록 반환
        Return list of note files
        
        Args:
            folder (str, optional): 특정 PARA 폴더 지정 / Specific PARA folder
            
        Returns:
            List[Path]: 노트 파일 경로 목록 / List of note file paths
        """
        notes = []
        
        if folder and folder in PARA_FOLDERS:
            search_path = self.vault_path / PARA_FOLDERS[folder]
        else:
            search_path = self.vault_path
        
        if not search_path.exists():
            self.logger.warning(f"검색 경로가 존재하지 않습니다: {search_path}")
            return notes
        
        for ext in SUPPORTED_EXTENSIONS:
            notes.extend(search_path.rglob(f'*{ext}'))
        
        return sorted(notes)
    
    def analyze_note(self, note_path: Path) -> Dict:
        """
        개별 노트 분석
        Analyze individual note
        
        Args:
            note_path (Path): 노트 파일 경로 / Note file path
            
        Returns:
            Dict: 노트 분석 결과 / Note analysis results
        """
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            analysis = {
                'path': str(note_path),
                'title': post.metadata.get('title', note_path.stem),
                'tags': post.metadata.get('tags', []),
                'created': post.metadata.get('created'),
                'modified': post.metadata.get('modified'),
                'word_count': len(post.content.split()),
                'char_count': len(post.content),
                'has_frontmatter': bool(post.metadata),
                'links': self._extract_links(post.content),
                'headings': self._extract_headings(post.content)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"노트 분석 실패 {note_path}: {str(e)}")
            return {'error': str(e), 'path': str(note_path)}
    
    def _extract_links(self, content: str) -> List[str]:
        """마크다운 링크 추출"""
        """Extract markdown links"""
        import re
        links = re.findall(r'\[\[([^\]]+)\]\]', content)  # Obsidian 링크
        links.extend(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))  # 마크다운 링크
        return links
    
    def _extract_headings(self, content: str) -> List[str]:
        """마크다운 헤딩 추출"""
        """Extract markdown headings"""
        import re
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        return headings
    
    def organize_notes(self) -> Dict:
        """
        노트 정리 실행
        Execute note organization
        
        Returns:
            Dict: 정리 결과 / Organization results
        """
        start_time = time.time()
        
        try:
            processed = 0
            results = {
                'success': True,
                'processed': 0,
                'errors': [],
                'moved': [],
                'updated': []
            }
            
            notes = self.get_notes_list()
            
            for note_path in notes:
                try:
                    # 노트 분석 및 필요시 이동/업데이트
                    # Analyze note and move/update if needed
                    analysis = self.analyze_note(note_path)
                    
                    # 여기에 구체적인 정리 로직 추가 가능
                    # Add specific organization logic here
                    
                    processed += 1
                    
                except Exception as e:
                    results['errors'].append({
                        'file': str(note_path),
                        'error': str(e)
                    })
            
            results['processed'] = processed
            duration = time.time() - start_time
            
            # 관리 작업 로그 기록
            # Log management activity
            self.management_logger.log_activity(
                command='organize',
                status='success',
                summary={
                    'processed_notes': processed,
                    'total_notes': len(notes),
                    'errors_count': len(results['errors']),
                    'moved_count': len(results['moved']),
                    'updated_count': len(results['updated'])
                },
                duration=duration
            )
            
            self.logger.info(f"노트 정리 완료: {processed}개 처리됨")
            
            return results
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 오류 로그 기록
            # Log error
            self.management_logger.log_activity(
                command='organize',
                status='error',
                summary={'vault_path': str(self.vault_path)},
                duration=duration,
                error=str(e)
            )
            
            self.logger.error(f"노트 정리 실패: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_backup(self) -> Optional[str]:
        """
        볼트 백업 생성
        Create vault backup
        
        Returns:
            str: 백업 파일 경로 / Backup file path
        """
        start_time = time.time()
        
        try:
            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"obsidian_backup_{timestamp}"
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            
            # 볼트 전체 복사
            # Copy entire vault
            shutil.copytree(self.vault_path, backup_path, 
                           ignore=shutil.ignore_patterns('*.tmp', '.obsidian'))
            
            # 백업 정보 저장
            # Save backup info
            notes_count = len(self.get_notes_list())
            backup_info = {
                'timestamp': timestamp,
                'vault_path': str(self.vault_path),
                'backup_path': backup_path,
                'note_count': notes_count
            }
            
            with open(os.path.join(backup_path, 'backup_info.json'), 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            duration = time.time() - start_time
            
            # 관리 작업 로그 기록
            # Log management activity
            self.management_logger.log_activity(
                command='backup',
                status='success',
                summary={
                    'backup_path': backup_path,
                    'note_count': notes_count,
                    'timestamp': timestamp,
                    'backup_size_mb': self._get_directory_size(backup_path) / (1024*1024)
                },
                duration=duration
            )
            
            self.logger.info(f"백업 생성 완료: {backup_path}")
            return backup_path
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 오류 로그 기록
            # Log error
            self.management_logger.log_activity(
                command='backup',
                status='error',
                summary={'vault_path': str(self.vault_path)},
                duration=duration,
                error=str(e)
            )
            
            self.logger.error(f"백업 생성 실패: {str(e)}")
            return None
    
    def _get_directory_size(self, directory: str) -> int:
        """디렉토리 크기 계산"""
        """Calculate directory size"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size
    
    def analyze_notes(self, folder: Optional[str] = None) -> Dict:
        """
        노트 분석 실행
        Execute note analysis
        
        Args:
            folder (str, optional): 특정 폴더만 분석 / Analyze specific folder only
            
        Returns:
            Dict: 분석 결과 / Analysis results
        """
        start_time = time.time()
        
        try:
            notes = self.get_notes_list(folder)
            
            analysis = {
                'total_notes': len(notes),
                'total_words': 0,
                'total_chars': 0,
                'notes_with_tags': 0,
                'notes_with_frontmatter': 0,
                'average_word_count': 0,
                'common_tags': {},
                'folder_distribution': {},
                'analysis_errors': 0
            }
            
            for note_path in notes:
                note_analysis = self.analyze_note(note_path)
                
                if 'error' not in note_analysis:
                    analysis['total_words'] += note_analysis.get('word_count', 0)
                    analysis['total_chars'] += note_analysis.get('char_count', 0)
                    
                    if note_analysis.get('tags'):
                        analysis['notes_with_tags'] += 1
                        for tag in note_analysis['tags']:
                            analysis['common_tags'][tag] = analysis['common_tags'].get(tag, 0) + 1
                    
                    if note_analysis.get('has_frontmatter'):
                        analysis['notes_with_frontmatter'] += 1
                else:
                    analysis['analysis_errors'] += 1
            
            if analysis['total_notes'] > 0:
                analysis['average_word_count'] = analysis['total_words'] // analysis['total_notes']
            
            duration = time.time() - start_time
            
            # 상위 10개 태그만 로그에 포함
            # Include only top 10 tags in log
            top_tags = dict(sorted(analysis['common_tags'].items(), key=lambda x: x[1], reverse=True)[:10])
            
            # 관리 작업 로그 기록
            # Log management activity
            self.management_logger.log_activity(
                command='analyze',
                status='success',
                summary={
                    'analyzed_folder': folder or 'all',
                    'total_notes': analysis['total_notes'],
                    'total_words': analysis['total_words'],
                    'notes_with_tags': analysis['notes_with_tags'],
                    'notes_with_frontmatter': analysis['notes_with_frontmatter'],
                    'average_word_count': analysis['average_word_count'],
                    'analysis_errors': analysis['analysis_errors'],
                    'top_tags': top_tags
                },
                duration=duration
            )
            
            self.logger.info("노트 분석 완료")
            return analysis
            
        except Exception as e:
            duration = time.time() - start_time
            
            # 오류 로그 기록
            # Log error
            self.management_logger.log_activity(
                command='analyze',
                status='error',
                summary={
                    'analyzed_folder': folder or 'all',
                    'vault_path': str(self.vault_path)
                },
                duration=duration,
                error=str(e)
            )
            
            self.logger.error(f"노트 분석 실패: {str(e)}")
            return {'error': str(e)}
    
    def get_management_summary(self) -> Dict:
        """
        관리 작업 요약 정보 반환
        Return management activity summary
        
        Returns:
            Dict: 관리 작업 요약 / Management activity summary
        """
        recent_activities = self.management_logger.get_recent_activities(10)
        
        return {
            'recent_activities': recent_activities,
            'log_file_path': str(self.management_logger.markdown_log)
        } 