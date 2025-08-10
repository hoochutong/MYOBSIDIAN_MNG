#!/usr/bin/env python3
"""
Obsidian 노트 관리 시스템 메인 모듈
Main module for Obsidian note management system
"""

import click
import logging
import signal
import sys
from rich.console import Console
from rich.table import Table
from pathlib import Path

from config import get_vault_path, PARA_FOLDERS, LOG_FILE, LOG_LEVEL
from obsidian_manager import ObsidianManager
from vault_tree_manager import VaultTreeManager

# 콘솔 및 로깅 설정
# Console and logging setup
console = Console()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 전역 변수로 트리 매니저 저장
# Store tree manager as global variable
tree_manager = None

def signal_handler(sig, frame):
    """시그널 핸들러 - 프로그램 종료 시 감시 중지"""
    """Signal handler - stop monitoring when program exits"""
    global tree_manager
    if tree_manager and tree_manager.is_watching:
        console.print("\n🛑 [yellow]프로그램 종료 중... 볼트 감시를 중지합니다.[/yellow]")
        console.print("🛑 [yellow]Exiting program... Stopping vault monitoring.[/yellow]")
        tree_manager.stop_watching()
    sys.exit(0)

# 시그널 핸들러 등록
# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """옵시디언 노트 관리 시스템"""
    """Obsidian Note Management System"""
    pass

@cli.command()
def status():
    """볼트 상태 확인"""
    """Check vault status"""
    console.print("🔍 [bold blue]옵시디언 볼트 상태 확인 중...[/bold blue]")
    console.print("🔍 [bold blue]Checking Obsidian vault status...[/bold blue]")
    
    vault_path = get_vault_path()
    if not vault_path:
        console.print("❌ [bold red]볼트를 찾을 수 없습니다![/bold red]")
        console.print("❌ [bold red]Vault not found![/bold red]")
        return
    
    manager = ObsidianManager(vault_path)
    status_info = manager.get_vault_status()
    
    # 상태 테이블 생성
    # Create status table
    table = Table(title="📊 Obsidian Vault Status")
    table.add_column("항목 / Item", style="cyan")
    table.add_column("값 / Value", style="green")
    
    table.add_row("볼트 경로 / Vault Path", vault_path)
    table.add_row("총 노트 수 / Total Notes", str(status_info['total_notes']))
    table.add_row("PARA 폴더 수 / PARA Folders", str(status_info['para_folders']))
    
    console.print(table)

@cli.command()
def organize():
    """노트 정리 실행"""
    """Execute note organization"""
    console.print("🧹 [bold green]노트 정리를 시작합니다...[/bold green]")
    console.print("🧹 [bold green]Starting note organization...[/bold green]")
    
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    manager = ObsidianManager(vault_path)
    result = manager.organize_notes()
    
    if result['success']:
        console.print(f"✅ [bold green]정리 완료! {result['processed']}개 노트 처리됨[/bold green]")
        console.print(f"✅ [bold green]Organization complete! {result['processed']} notes processed[/bold green]")
    else:
        console.print(f"❌ [bold red]정리 실패: {result['error']}[/bold red]")
        console.print(f"❌ [bold red]Organization failed: {result['error']}[/bold red]")

@cli.command()
def backup():
    """노트 백업 생성"""
    """Create note backup"""
    console.print("💾 [bold yellow]백업을 생성합니다...[/bold yellow]")
    console.print("💾 [bold yellow]Creating backup...[/bold yellow]")
    
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    manager = ObsidianManager(vault_path)
    backup_path = manager.create_backup()
    
    if backup_path:
        console.print(f"✅ [bold green]백업 완료: {backup_path}[/bold green]")
        console.print(f"✅ [bold green]Backup complete: {backup_path}[/bold green]")
    else:
        console.print("❌ [bold red]백업 실패[/bold red]")
        console.print("❌ [bold red]Backup failed[/bold red]")

@cli.command()
@click.option('--folder', type=click.Choice(['projects', 'areas', 'resources', 'archive']), 
              help='특정 PARA 폴더만 분석 / Analyze specific PARA folder only')
def analyze(folder):
    """노트 분석 실행"""
    """Execute note analysis"""
    console.print("📈 [bold magenta]노트 분석을 시작합니다...[/bold magenta]")
    console.print("📈 [bold magenta]Starting note analysis...[/bold magenta]")
    
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    manager = ObsidianManager(vault_path)
    analysis = manager.analyze_notes(folder)
    
    # 분석 결과 표시
    # Display analysis results
    table = Table(title="📊 Note Analysis Results")
    table.add_column("메트릭 / Metric", style="cyan")
    table.add_column("값 / Value", style="green")
    
    for metric, value in analysis.items():
        table.add_row(str(metric), str(value))
    
    console.print(table)

@cli.command()
@click.option('--limit', default=10, help='표시할 최근 활동 수 / Number of recent activities to show')
def logs(limit):
    """관리 작업 로그 조회"""
    """View management activity logs"""
    console.print("📋 [bold blue]관리 작업 이력을 조회합니다...[/bold blue]")
    console.print("📋 [bold blue]Retrieving management activity history...[/bold blue]")
    
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    manager = ObsidianManager(vault_path)
    summary = manager.get_management_summary()
    
    # 최근 활동 테이블 생성
    # Create recent activities table
    table = Table(title=f"📝 최근 {limit}개 관리 활동 / Recent {limit} Management Activities")
    table.add_column("시간 / Time", style="cyan")
    table.add_column("명령어 / Command", style="yellow")
    table.add_column("상태 / Status", style="green")
    table.add_column("요약 / Summary", style="white")
    
    recent_activities = summary['recent_activities'][-limit:]
    
    for activity in reversed(recent_activities):
        # 상태 이모지
        # Status emoji
        status_emoji = {
            'success': '✅ SUCCESS',
            'error': '❌ ERROR',
            'warning': '⚠️ WARNING'
        }.get(activity['status'], '📝 INFO')
        
        # 요약 정보를 간단히 표시
        # Display summary briefly
        summary_text = []
        for key, value in activity['summary'].items():
            if key in ['total_notes', 'processed_notes', 'note_count']:
                summary_text.append(f"{key}: {value}")
        
        summary_str = ", ".join(summary_text[:3])  # 최대 3개 항목만
        if len(summary_str) > 50:
            summary_str = summary_str[:50] + "..."
        
        table.add_row(
            activity['timestamp'],
            activity['command'].upper(),
            status_emoji,
            summary_str
        )
    
    console.print(table)
    
    # 로그 파일 경로 안내
    # Log file path information
    console.print(f"\n📄 [bold]상세 로그 파일 / Detailed log file[/bold]: {summary['log_file_path']}")

@cli.command()
@click.option('--output', help='출력 파일 경로 / Output file path')
def report(output):
    """관리 리포트 생성"""
    """Generate management report"""
    console.print("📊 [bold blue]관리 리포트를 생성합니다...[/bold blue]")
    console.print("📊 [bold blue]Generating management report...[/bold blue]")
    
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    manager = ObsidianManager(vault_path)
    report_path = manager.management_logger.export_report(output)
    
    console.print(f"✅ [bold green]리포트 생성 완료: {report_path}[/bold green]")
    console.print(f"✅ [bold green]Report generated: {report_path}[/bold green]")

@cli.command()
def open_logs():
    """관리 로그 파일 열기"""
    """Open management log file"""
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    manager = ObsidianManager(vault_path)
    log_path = manager.management_logger.markdown_log
    
    if log_path.exists():
        console.print(f"📄 [bold blue]로그 파일 경로: {log_path}[/bold blue]")
        console.print(f"📄 [bold blue]Log file path: {log_path}[/bold blue]")
        
        # macOS에서 파일 열기
        # Open file on macOS
        import subprocess
        try:
            subprocess.run(['open', str(log_path)])
            console.print("✅ [bold green]로그 파일을 열었습니다[/bold green]")
            console.print("✅ [bold green]Log file opened[/bold green]")
        except Exception as e:
            console.print(f"⚠️ [bold yellow]파일을 직접 여세요: {log_path}[/bold yellow]")
            console.print(f"⚠️ [bold yellow]Please open the file manually: {log_path}[/bold yellow]")
    else:
        console.print("❌ [bold red]로그 파일이 없습니다[/bold red]")
        console.print("❌ [bold red]Log file not found[/bold red]")

@cli.command('update-tree')
def update_tree():
    """볼트 트리 구조 수동 업데이트"""
    """Manually update vault tree structure"""
    console.print("🌳 [bold green]볼트 트리 구조를 업데이트합니다...[/bold green]")
    console.print("🌳 [bold green]Updating vault tree structure...[/bold green]")
    
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    try:
        tree_manager = VaultTreeManager(vault_path)
        tree_manager.update_tree_structure()
        
        console.print("✅ [bold green]트리 구조 업데이트 완료![/bold green]")
        console.print("✅ [bold green]Tree structure update complete![/bold green]")
        console.print(f"📄 [bold blue]파일 위치: {tree_manager.tree_file}[/bold blue]")
        console.print(f"📄 [bold blue]File location: {tree_manager.tree_file}[/bold blue]")
        
    except Exception as e:
        console.print(f"❌ [bold red]트리 구조 업데이트 실패: {str(e)}[/bold red]")
        console.print(f"❌ [bold red]Tree structure update failed: {str(e)}[/bold red]")

@cli.command('watch-vault')
def watch_vault():
    """볼트 실시간 감시 시작"""
    """Start real-time vault monitoring"""
    console.print("👁️ [bold green]볼트 실시간 감시를 시작합니다...[/bold green]")
    console.print("👁️ [bold green]Starting real-time vault monitoring...[/bold green]")
    
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    global tree_manager
    
    try:
        tree_manager = VaultTreeManager(vault_path)
        tree_manager.start_watching()
        
        console.print("✅ [bold green]실시간 감시 시작됨![/bold green]")
        console.print("✅ [bold green]Real-time monitoring started![/bold green]")
        console.print("🔄 [bold yellow]파일 변화를 감지하면 자동으로 트리 구조가 업데이트됩니다.[/bold yellow]")
        console.print("🔄 [bold yellow]Tree structure will auto-update when file changes are detected.[/bold yellow]")
        console.print("⌨️ [bold blue]Ctrl+C를 눌러 감시를 중지할 수 있습니다.[/bold blue]")
        console.print("⌨️ [bold blue]Press Ctrl+C to stop monitoring.[/bold blue]")
        
        # 무한 대기 (감시 중)
        # Infinite wait (while monitoring)
        try:
            while tree_manager.is_watching:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n🛑 [yellow]사용자가 감시를 중지했습니다.[/yellow]")
            console.print("🛑 [yellow]User stopped monitoring.[/yellow]")
            tree_manager.stop_watching()
            
    except Exception as e:
        console.print(f"❌ [bold red]실시간 감시 시작 실패: {str(e)}[/bold red]")
        console.print(f"❌ [bold red]Failed to start real-time monitoring: {str(e)}[/bold red]")

@cli.command('stop-watch')
def stop_watch():
    """볼트 실시간 감시 중지"""
    """Stop real-time vault monitoring"""
    console.print("🛑 [bold yellow]볼트 실시간 감시를 중지합니다...[/bold yellow]")
    console.print("🛑 [bold yellow]Stopping real-time vault monitoring...[/bold yellow]")
    
    global tree_manager
    
    if tree_manager:
        tree_manager.stop_watching()
        console.print("✅ [bold green]실시간 감시 중지됨![/bold green]")
        console.print("✅ [bold green]Real-time monitoring stopped![/bold green]")
    else:
        console.print("⚠️ [bold yellow]실행 중인 감시가 없습니다.[/bold yellow]")
        console.print("⚠️ [bold yellow]No active monitoring found.[/bold yellow]")

@cli.command('tree-status')
def tree_status():
    """트리 구조 감시 상태 확인"""
    """Check tree structure monitoring status"""
    console.print("📊 [bold blue]트리 구조 감시 상태를 확인합니다...[/bold blue]")
    console.print("📊 [bold blue]Checking tree structure monitoring status...[/bold blue]")
    
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    try:
        tree_manager = VaultTreeManager(vault_path)
        status = tree_manager.get_status()
        
        # 상태 테이블 생성
        # Create status table
        table = Table(title="🌳 Tree Structure Monitoring Status")
        table.add_column("항목 / Item", style="cyan")
        table.add_column("값 / Value", style="green")
        
        table.add_row("감시 상태 / Monitoring Status", 
                     "🟢 실행 중 / Running" if status['is_watching'] else "🔴 중지됨 / Stopped")
        table.add_row("볼트 경로 / Vault Path", status['vault_path'])
        table.add_row("트리 파일 / Tree File", status['tree_file'])
        table.add_row("파일 존재 / File Exists", 
                     "✅ Yes" if status['tree_file_exists'] else "❌ No")
        
        if status['tree_file_exists']:
            table.add_row("파일 크기 / File Size", f"{status['tree_file_size']} bytes")
            table.add_row("마지막 수정 / Last Modified", status['last_modified'])
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ [bold red]상태 확인 실패: {str(e)}[/bold red]")
        console.print(f"❌ [bold red]Status check failed: {str(e)}[/bold red]")

@cli.command('open-tree')
def open_tree():
    """볼트 트리 구조 파일 열기"""
    """Open vault tree structure file"""
    vault_path = get_vault_path()
    if not vault_path:
        return
    
    tree_manager = VaultTreeManager(vault_path)
    tree_file = tree_manager.tree_file
    
    if tree_file.exists():
        console.print(f"📄 [bold blue]트리 파일 경로: {tree_file}[/bold blue]")
        console.print(f"📄 [bold blue]Tree file path: {tree_file}[/bold blue]")
        
        # macOS에서 파일 열기
        # Open file on macOS
        import subprocess
        try:
            subprocess.run(['open', str(tree_file)])
            console.print("✅ [bold green]트리 구조 파일을 열었습니다[/bold green]")
            console.print("✅ [bold green]Tree structure file opened[/bold green]")
        except Exception as e:
            console.print(f"⚠️ [bold yellow]파일을 직접 여세요: {tree_file}[/bold yellow]")
            console.print(f"⚠️ [bold yellow]Please open the file manually: {tree_file}[/bold yellow]")
    else:
        console.print("❌ [bold red]트리 구조 파일이 없습니다. 먼저 생성해주세요.[/bold red]")
        console.print("❌ [bold red]Tree structure file not found. Please generate it first.[/bold red]")
        console.print("💡 [bold blue]실행: python main.py update-tree[/bold blue]")
        console.print("💡 [bold blue]Run: python main.py update-tree[/bold blue]")

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n👋 [bold yellow]프로그램이 중단되었습니다.[/bold yellow]")
        console.print("\n👋 [bold yellow]Program interrupted.[/bold yellow]")
    except Exception as e:
        console.print(f"\n❌ [bold red]오류 발생: {str(e)}[/bold red]")
        console.print(f"\n❌ [bold red]Error occurred: {str(e)}[/bold red]")
        logging.error(f"Unexpected error: {str(e)}", exc_info=True) 