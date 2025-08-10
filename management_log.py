"""
옵시디언 관리 작업 이력 로거
Obsidian Management Activity Logger
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class LogEntry:
    """로그 엔트리 데이터 클래스"""
    """Log entry data class"""
    timestamp: str
    command: str
    status: str
    summary: Dict[str, Any]
    duration: Optional[float] = None
    error: Optional[str] = None

class ManagementLogger:
    """옵시디언 관리 작업 로거 클래스"""
    """Obsidian management activity logger class"""
    
    def __init__(self, log_dir: str = "management_logs"):
        """
        ManagementLogger 초기화
        Initialize ManagementLogger
        
        Args:
            log_dir (str): 로그 파일이 저장될 디렉토리 / Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 마크다운 로그 파일 경로
        # Markdown log file paths
        self.markdown_log = self.log_dir / "obsidian_management_history.md"
        self.json_log = self.log_dir / "management_activities.json"
        
        # 첫 실행 시 마크다운 로그 파일 초기화
        # Initialize markdown log file on first run
        if not self.markdown_log.exists():
            self._initialize_markdown_log()
    
    def _initialize_markdown_log(self):
        """
        마크다운 로그 파일 초기화
        Initialize markdown log file
        """
        initial_content = f"""# 🧠 Obsidian 관리 작업 이력
# Obsidian Management Activity History

> 자동 생성된 관리 작업 이력입니다. 수동으로 편집하지 마세요.  
> Auto-generated management activity history. Do not edit manually.

**생성 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Creation Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 요약 통계 / Summary Statistics

- **총 실행 횟수**: 0
- **마지막 실행**: -
- **Total Executions**: 0
- **Last Execution**: -

---

## 📝 상세 이력 / Detailed History

"""
        with open(self.markdown_log, 'w', encoding='utf-8') as f:
            f.write(initial_content)
    
    def log_activity(self, command: str, status: str, summary: Dict[str, Any], 
                    duration: Optional[float] = None, error: Optional[str] = None):
        """
        관리 작업 활동 로그 기록
        Log management activity
        
        Args:
            command (str): 실행된 명령어 / Executed command
            status (str): 실행 상태 (success/error) / Execution status
            summary (Dict): 작업 결과 요약 / Activity result summary
            duration (float, optional): 실행 시간 (초) / Execution time in seconds
            error (str, optional): 오류 메시지 / Error message
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 로그 엔트리 생성
        # Create log entry
        log_entry = LogEntry(
            timestamp=timestamp,
            command=command,
            status=status,
            summary=summary,
            duration=duration,
            error=error
        )
        
        # JSON 로그에 추가
        # Add to JSON log
        self._append_json_log(log_entry)
        
        # 마크다운 로그에 추가
        # Add to markdown log
        self._append_markdown_log(log_entry)
        
        # 통계 업데이트
        # Update statistics
        self._update_statistics()
    
    def _append_json_log(self, log_entry: LogEntry):
        """
        JSON 로그 파일에 엔트리 추가
        Append entry to JSON log file
        """
        logs = []
        
        # 기존 로그 읽기
        # Read existing logs
        if self.json_log.exists():
            try:
                with open(self.json_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # 새 엔트리 추가
        # Add new entry
        logs.append(asdict(log_entry))
        
        # 최근 100개 항목만 유지
        # Keep only last 100 entries
        if len(logs) > 100:
            logs = logs[-100:]
        
        # 파일에 저장
        # Save to file
        with open(self.json_log, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def _append_markdown_log(self, log_entry: LogEntry):
        """
        마크다운 로그 파일에 엔트리 추가
        Append entry to markdown log file
        """
        # 상태 이모지 매핑
        # Status emoji mapping
        status_emoji = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }
        
        emoji = status_emoji.get(log_entry.status, '📝')
        
        # 마크다운 엔트리 생성
        # Create markdown entry
        entry_md = f"""### {emoji} {log_entry.command.upper()} - {log_entry.timestamp}

**상태 / Status**: {log_entry.status.upper()}  
**실행 시간 / Duration**: {log_entry.duration:.2f}초 / {log_entry.duration:.2f}s  

**결과 요약 / Summary**:
"""
        
        # 요약 정보 추가
        # Add summary information
        for key, value in log_entry.summary.items():
            if isinstance(value, dict):
                entry_md += f"- **{key}**: {json.dumps(value, ensure_ascii=False)}\n"
            else:
                entry_md += f"- **{key}**: {value}\n"
        
        # 오류 정보 추가
        # Add error information if exists
        if log_entry.error:
            entry_md += f"\n**오류 / Error**: `{log_entry.error}`\n"
        
        entry_md += "\n---\n\n"
        
        # 파일에 추가
        # Append to file
        with open(self.markdown_log, 'a', encoding='utf-8') as f:
            f.write(entry_md)
    
    def _update_statistics(self):
        """
        마크다운 파일의 통계 섹션 업데이트
        Update statistics section in markdown file
        """
        # JSON 로그에서 통계 계산
        # Calculate statistics from JSON log
        stats = self._calculate_statistics()
        
        # 마크다운 파일 읽기
        # Read markdown file
        with open(self.markdown_log, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 통계 섹션 교체
        # Replace statistics section
        stats_section = f"""## 📊 요약 통계 / Summary Statistics

- **총 실행 횟수**: {stats['total_executions']}
- **마지막 실행**: {stats['last_execution']}
- **성공률**: {stats['success_rate']:.1f}%
- **평균 실행 시간**: {stats['avg_duration']:.2f}초
- **Total Executions**: {stats['total_executions']}
- **Last Execution**: {stats['last_execution']}
- **Success Rate**: {stats['success_rate']:.1f}%
- **Average Duration**: {stats['avg_duration']:.2f}s

**명령어별 실행 횟수 / Command Execution Count**:
"""
        
        for cmd, count in stats['command_counts'].items():
            stats_section += f"- **{cmd}**: {count}회 / {count} times\n"
        
        stats_section += "\n---\n\n## 📝 상세 이력 / Detailed History\n\n"
        
        # 통계 섹션 교체
        # Replace statistics section
        import re
        pattern = r'## 📊 요약 통계.*?## 📝 상세 이력 / Detailed History\n\n'
        content = re.sub(pattern, stats_section, content, flags=re.DOTALL)
        
        # 파일에 저장
        # Save to file
        with open(self.markdown_log, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """
        로그 통계 계산
        Calculate log statistics
        
        Returns:
            Dict: 통계 정보 / Statistics information
        """
        stats = {
            'total_executions': 0,
            'last_execution': '-',
            'success_rate': 0.0,
            'avg_duration': 0.0,
            'command_counts': {}
        }
        
        if not self.json_log.exists():
            return stats
        
        try:
            with open(self.json_log, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if not logs:
                return stats
            
            # 기본 통계
            # Basic statistics
            stats['total_executions'] = len(logs)
            stats['last_execution'] = logs[-1]['timestamp']
            
            # 성공률
            # Success rate
            success_count = sum(1 for log in logs if log['status'] == 'success')
            stats['success_rate'] = (success_count / len(logs)) * 100
            
            # 평균 실행 시간
            # Average duration
            durations = [log['duration'] for log in logs if log['duration'] is not None]
            if durations:
                stats['avg_duration'] = sum(durations) / len(durations)
            
            # 명령어별 횟수
            # Command counts
            for log in logs:
                cmd = log['command']
                stats['command_counts'][cmd] = stats['command_counts'].get(cmd, 0) + 1
            
        except Exception as e:
            print(f"통계 계산 중 오류: {e}")
        
        return stats
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """
        최근 활동 목록 반환
        Return recent activities list
        
        Args:
            limit (int): 반환할 항목 수 / Number of items to return
            
        Returns:
            List[Dict]: 최근 활동 목록 / Recent activities list
        """
        if not self.json_log.exists():
            return []
        
        try:
            with open(self.json_log, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            return logs[-limit:] if logs else []
        except:
            return []
    
    def export_report(self, output_path: Optional[str] = None) -> str:
        """
        관리 리포트 내보내기
        Export management report
        
        Args:
            output_path (str, optional): 출력 파일 경로 / Output file path
            
        Returns:
            str: 리포트 파일 경로 / Report file path
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.log_dir / f"management_report_{timestamp}.md"
        
        stats = self._calculate_statistics()
        recent_activities = self.get_recent_activities(20)
        
        report_content = f"""# 📊 Obsidian 관리 리포트
# Obsidian Management Report

**생성 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 핵심 지표 / Key Metrics

- **총 관리 작업**: {stats['total_executions']}회
- **성공률**: {stats['success_rate']:.1f}%
- **평균 실행 시간**: {stats['avg_duration']:.2f}초
- **마지막 관리**: {stats['last_execution']}

## 📈 명령어 사용 현황 / Command Usage

"""
        
        for cmd, count in stats['command_counts'].items():
            percentage = (count / stats['total_executions']) * 100 if stats['total_executions'] > 0 else 0
            report_content += f"- **{cmd}**: {count}회 ({percentage:.1f}%)\n"
        
        report_content += f"""

## 🕒 최근 활동 ({len(recent_activities)}개)

"""
        
        for activity in reversed(recent_activities):
            status_emoji = {'success': '✅', 'error': '❌', 'warning': '⚠️'}.get(activity['status'], '📝')
            report_content += f"- {status_emoji} **{activity['command']}** - {activity['timestamp']}\n"
        
        # 파일에 저장
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(output_path) 