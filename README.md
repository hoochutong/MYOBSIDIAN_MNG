# 🧠 Obsidian Note Manager

옵시디언 노트를 체계적으로 관리하고 정리하는 Python 기반 도구입니다.  
A Python-based tool for systematically managing and organizing Obsidian notes.

## ✨ 주요 기능 / Main Features

- 📊 **볼트 상태 분석**: 노트 수, PARA 폴더 구조 등 전반적인 상태 확인
- 🧹 **노트 정리**: 자동화된 노트 분류 및 정리
- 💾 **백업 기능**: 안전한 볼트 백업 생성
- 📈 **상세 분석**: 노트별 메타데이터, 링크, 태그 분석
- 🎯 **PARA 메소드 지원**: Projects, Areas, Resources, Archive 구조 최적화
- 🌳 **실시간 트리 구조**: 볼트 폴더 구조를 마크다운으로 자동 생성 및 실시간 업데이트
- 👁️ **파일 변화 감지**: 노트 생성/삭제/이동 시 자동으로 트리 구조 업데이트
- 📝 **자동 로깅**: 모든 관리 작업을 마크다운으로 자동 기록

## 🚀 설치 및 설정 / Installation & Setup

### 1. 의존성 설치 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. 볼트 경로 설정 / Configure Vault Path

`config.py` 파일에서 옵시디언 볼트 경로를 확인/수정하세요:

```python
OBSIDIAN_VAULT_PATH = "/Users/alliej/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second Brain"
```

## 📖 사용법 / Usage

### 기본 명령어 / Basic Commands

```bash
# 볼트 상태 확인 / Check vault status
python main.py status

# 노트 정리 실행 / Execute note organization  
python main.py organize

# 백업 생성 / Create backup
python main.py backup

# 전체 노트 분석 / Analyze all notes
python main.py analyze

# 특정 PARA 폴더만 분석 / Analyze specific PARA folder
python main.py analyze --folder projects
python main.py analyze --folder areas
python main.py analyze --folder resources
python main.py analyze --folder archive
```

### 🌳 트리 구조 관리 / Tree Structure Management

```bash
# 트리 구조 수동 업데이트 / Manual tree update
python main.py update-tree

# 실시간 감지 시작 / Start real-time monitoring
python main.py watch-vault

# 실시간 감지 중지 / Stop real-time monitoring
python main.py stop-watch

# 트리 구조 상태 확인 / Check tree structure status
python main.py tree-status

# 트리 구조 파일 열기 / Open tree structure file
python main.py open-tree
```

### 📝 로그 관리 / Log Management

```bash
# 최근 관리 활동 조회 / View recent management activities
python main.py logs

# 특정 개수만 조회 / View specific number of activities
python main.py logs --limit 5

# 관리 리포트 생성 / Generate management report
python main.py report

# 로그 파일 열기 / Open log file
python main.py open-logs
```

### 도움말 / Help

```bash
python main.py --help
```

## 📁 PARA 메소드 지원 / PARA Method Support

이 도구는 다음과 같은 PARA 메소드 폴더 구조를 지원합니다:

- **10-Projects**: 진행 중인 프로젝트
- **20-Areas**: 지속적인 관심 영역  
- **30-Resources**: 참고 자료
- **40-Archive**: 보관된 항목

## 🔧 설정 파일 / Configuration Files

### config.py
- 볼트 경로 설정
- PARA 폴더 구조 정의
- 백업 및 로깅 설정

### requirements.txt
- 필요한 Python 패키지 목록
- 마크다운 처리, CLI, 파일 모니터링 등

## 📋 지원하는 파일 형식 / Supported File Formats

- `.md` (Markdown)
- `.txt` (Text)

## 🛠️ 주요 구성 요소 / Main Components

### ObsidianManager 클래스
- 볼트 상태 분석
- 노트 파일 처리
- 백업 생성
- 메타데이터 추출

### VaultTreeManager 클래스
- 실시간 볼트 트리 구조 관리
- 파일 시스템 변화 감지 (`watchdog` 사용)
- 자동 마크다운 트리 생성
- 한글 파일명 지원 (`볼트구조.md`)

### ManagementLogger 클래스
- 모든 관리 작업 자동 로깅
- JSON 및 마크다운 이중 기록
- 활동 분석 및 리포트 생성

### CLI 인터페이스
- 직관적인 명령행 도구
- Rich 라이브러리 기반 예쁜 출력
- 상세한 도움말 및 오류 메시지

## 📊 분석 기능 / Analysis Features

- **기본 통계**: 노트 수, 단어 수, 문자 수
- **메타데이터 분석**: 제목, 태그, 생성/수정 날짜
- **링크 분석**: 내부 링크 및 외부 링크 추출
- **구조 분석**: 헤딩 구조 및 계층 분석

## 💾 백업 기능 / Backup Features

- 자동 타임스탬프 기반 백업
- 볼트 전체 복사 (`.obsidian` 폴더 제외)
- 백업 메타데이터 저장
- 안전한 증분 백업

## 🔍 로깅 / Logging

모든 작업은 다음 위치에 로그로 기록됩니다:
- **기본 로그**: `obsidian_manager.log`
- **관리 로그**: `management_logs/obsidian_management_history.md`
- **활동 데이터**: `management_logs/management_activities.json`
- **콘솔**: 실시간 상태 출력

## 🎯 자동화된 기능들 / Automated Features

- **자동 트리 업데이트**: 파일 생성/삭제/이동 시 `볼트구조.md` 자동 업데이트
- **실시간 감지**: `watchdog` 라이브러리를 통한 실시간 파일 시스템 모니터링
- **자동 로깅**: 모든 관리 작업이 JSON과 마크다운 양 형태로 자동 기록
- **중복 방지**: 2초 딜레이로 중복 업데이트 방지 시스템
- **한글 지원**: 트리 구조 파일을 한글명(`볼트구조.md`)으로 생성

## ⚠️ 주의사항 / Important Notes

1. 백업을 정기적으로 생성하여 데이터 손실을 방지하세요
2. 볼트 경로가 정확한지 확인하세요
3. iCloud 동기화 중인 볼트의 경우 네트워크 상태를 확인하세요

## 🤝 기여 / Contributing

버그 리포트나 기능 제안은 언제든 환영합니다!  
Bug reports and feature suggestions are always welcome!

## 📄 라이선스 / License

MIT License 