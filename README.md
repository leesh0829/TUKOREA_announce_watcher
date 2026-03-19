# TUKOREA announce watcher

한국공학대학교 공지 게시판을 주기적으로 확인하고, 처음 본 공지만 알리도록 설계한 Python 기반 감시기입니다.

## 현재 구현된 단계

- TUKOREA K2Web 게시판용 HTTP 어댑터 포함
- 로그인 필요한 사이트용 **세션 로그인 어댑터 뼈대** 포함
- 여러 게시판을 **JSON 설정 파일**로 관리 가능
- SQLite 중복 방지 저장소 포함
- **Windows 토스트 알림** 지원
- **로그 파일 로테이션** 및 요청 **재시도 정책** 지원
- **시작프로그램 등록/해제** 지원
- **트레이 모드 엔트리포인트** 포함(옵션 패키지 필요)

## 요구 사항

- Python 3.11 이상
- 인터넷 연결
- Windows 토스트/시작프로그램은 Windows 환경
- `venv` 사용 가능 환경

## 설치

```bash
git clone <repo-url>
cd TUKOREA_announce_watcher
python -m venv .venv
```

### macOS / Linux

```bash
source .venv/bin/activate
python -m pip install -e .[dev]
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

### Windows CMD

```bat
.venv\Scripts\activate.bat
python -m pip install -e .[dev]
```

## 설정 파일 만들기

```bash
announce-watcher --write-example-config
```

또는 `watcher_config.example.json`을 복사해서 `watcher_config.json`으로 사용하면 됩니다.

## 주요 기능

### 1) Windows 토스트 알림

설정 파일에서 아래처럼 켜면 됩니다.

```json
"notifier": {
  "type": "windows_toast",
  "enabled": true
}
```

현재 구현은 콘솔 출력 + Windows PowerShell 기반 토스트를 함께 사용합니다. Windows가 아닌 환경에서는 토스트는 건너뛰고 로그만 남깁니다.

### 2) 로그 파일 / 로테이션

```json
"logging": {
  "path": "logs/announce_watcher.log",
  "level": "INFO",
  "max_bytes": 1048576,
  "backup_count": 3
}
```

- 로그 파일은 자동 생성됩니다.
- 크기가 커지면 회전(rotating)됩니다.
- 콘솔에도 같이 출력됩니다.

### 3) 재시도 정책

사이트별 `settings`에 아래 값을 둘 수 있습니다.

```json
"settings": {
  "board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do",
  "timeout_seconds": 20,
  "retries": 2,
  "retry_backoff_seconds": 2
}
```

실패 시 점진적으로 대기 후 재시도합니다.

### 4) 로그인 필요한 사이트 어댑터

`authenticated_tukorea_board` 어댑터를 추가했습니다.

예:

```json
{
  "name": "secure-example-board",
  "enabled": true,
  "login_mode": "session",
  "adapter_type": "authenticated_tukorea_board",
  "interval_seconds": 300,
  "settings": {
    "login_url": "https://example.com/login",
    "username": "your-id",
    "password": "your-password",
    "username_field": "username",
    "password_field": "password",
    "extra_login_fields": {},
    "board_url": "https://example.com/protected-board"
  }
}
```

이 어댑터는 폼 로그인 후 쿠키 세션을 유지하면서 보호된 게시판을 읽는 구조입니다.

### 5) 시작프로그램 연동

설치:

```bash
announce-watcher --install-startup
```

제거:

```bash
announce-watcher --uninstall-startup
```

Windows Startup 폴더에 `.cmd` 런처를 생성/삭제합니다.

### 6) 트레이 앱 모드

```bash
announce-watcher --tray
```

트레이 모드는 선택 기능이며 `pystray`, `Pillow` 설치가 필요합니다.
현재는 최소 트레이 엔트리포인트까지 구현되어 있습니다.

## 실행 예시

### 1회 체크

```bash
announce-watcher --once
```

### 활성 사이트 목록 확인

```bash
announce-watcher --list-sites
```

### 계속 감시

```bash
announce-watcher
```

## 첫 실행 알림 정책

기본값에서는 **첫 실행은 기존 글을 기준선으로만 저장하고 알리지 않습니다.**
그 다음부터 새로 올라온 공지만 알림합니다.

## 설정 파일 예시

전체 예시는 `watcher_config.example.json`에 들어 있습니다.

핵심 필드:

- `db_path`: SQLite 경로
- `logging`: 로그 파일 설정
- `notifier`: 알림 방식
- `startup`: 시작프로그램 관련 기본값
- `sites`: 감시 대상 목록
- `sites[].adapter_type`: `tukorea_board` 또는 `authenticated_tukorea_board`

## 테스트

```bash
python -m pytest -q
```

## 현재 상태에서 남아 있는 현실적인 후속 작업

이번 변경으로 요청하신 4가지는 모두 코드 경로에 반영했습니다. 다만 실사용 완성도를 더 끌어올리려면 이후에는 아래를 추가하면 좋습니다.

1. 토스트 클릭 시 브라우저 열기 액션
2. 트레이 메뉴(일시정지/즉시 확인/종료)
3. 로그인 어댑터별 사이트 맞춤 파서
4. 암호 평문 저장 대신 OS 자격 증명 저장소 연동
