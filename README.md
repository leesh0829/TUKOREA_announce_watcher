# TUKOREA announce watcher

한국공학대학교 공지 게시판을 주기적으로 확인하고, 처음 본 공지만 알리도록 설계한 Python 기반 감시기입니다.

## 현재 구현된 단계

- TUKOREA K2Web 게시판용 HTTP 어댑터가 기본 포함되어 있습니다.
- 여러 게시판을 **JSON 설정 파일**로 관리할 수 있습니다.
- 이미 본 공지는 SQLite DB에 저장해서 중복 알림을 막습니다.
- 첫 실행은 기존 게시물을 기준선으로만 저장하고 알리지 않습니다.
- `--once`, `--list-sites`, `--write-example-config` 같은 실행 옵션을 지원합니다.

## 요구 사항

- Python 3.11 이상
- 인터넷 연결
- `venv` 사용 가능 환경

## 처음 세팅하는 방법

### 1) 저장소 받기

```bash
git clone <repo-url>
cd TUKOREA_announce_watcher
```

### 2) 가상환경 만들기

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Windows CMD

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

### 3) 패키지 설치

개발용 테스트 의존성까지 같이 설치하려면:

```bash
python -m pip install -e .[dev]
```

실행만 하려면:

```bash
python -m pip install -e .
```

## 설정 파일 준비

예제 설정 파일을 만들려면:

```bash
announce-watcher --write-example-config
```

또는 저장소에 들어 있는 `watcher_config.example.json`을 복사해서 `watcher_config.json`으로 써도 됩니다.

```bash
cp watcher_config.example.json watcher_config.json
```

Windows CMD에서는:

```bat
copy watcher_config.example.json watcher_config.json
```

## 실행 방법

### 1회만 체크하고 종료

```bash
announce-watcher --once
```

또는:

```bash
python -m announce_watcher.app --once
```

### 등록된 사이트 목록만 보기

```bash
announce-watcher --list-sites
```

### 백그라운드처럼 계속 감시하기

```bash
announce-watcher
```

실행되면 시작 시 한 번 체크한 뒤, 각 사이트의 `interval_seconds` 주기로 계속 확인합니다.

## 첫 실행 알림 동작

기본값에서는 **첫 실행 때 기존 글이 있더라도 알림을 보내지 않습니다.**
첫 실행은 현재 목록을 DB에 저장해서 "여기까지는 이미 본 것"으로 기준선만 잡습니다.

즉:

1. 첫 실행 → 기존 글 저장만 하고 알림 없음
2. 이후 실행 → 그 뒤에 새로 생긴 글만 알림

원하면 사이트별로 `notify_on_first_run=true`를 설정 파일에 넣어 첫 실행 알림을 켤 수 있습니다.

## 설정 파일 형식

`watcher_config.json` 예시는 아래처럼 생겼습니다.

```json
{
  "db_path": "watcher.db",
  "sites": [
    {
      "name": "tukorea-contract-notices",
      "interval_seconds": 300,
      "enabled": true,
      "login_mode": "none",
      "notify_on_first_run": false,
      "adapter_type": "tukorea_board",
      "settings": {
        "board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do",
        "timeout_seconds": 20
      }
    }
  ]
}
```

설정 항목:

- `db_path`: SQLite DB 경로
- `sites`: 감시 대상 목록
- `name`: 사이트 식별자
- `interval_seconds`: 체크 주기(초)
- `enabled`: 활성화 여부
- `notify_on_first_run`: 첫 실행 알림 여부
- `adapter_type`: 현재는 `tukorea_board` 지원
- `settings.board_url`: 감시할 게시판 목록 URL
- `settings.timeout_seconds`: HTTP 타임아웃

## 여러 게시판 추가 예시

```json
{
  "db_path": "watcher.db",
  "sites": [
    {
      "name": "contract-notices",
      "interval_seconds": 300,
      "enabled": true,
      "adapter_type": "tukorea_board",
      "settings": {
        "board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do"
      }
    },
    {
      "name": "another-board",
      "interval_seconds": 600,
      "enabled": true,
      "adapter_type": "tukorea_board",
      "settings": {
        "board_url": "https://example.tukorea.ac.kr/example/1234/subview.do"
      }
    }
  ]
}
```

## CLI 옵션

- `--config <path>`: 설정 파일 경로 지정
- `--db-path <path>`: SQLite DB 경로 강제 override
- `--once`: 한 번만 실행 후 종료
- `--list-sites`: 활성 사이트 목록 출력 후 종료
- `--write-example-config`: 예제 설정 파일 생성 후 종료

## 테스트 방법

```bash
python -m pytest -q
```

## 파일 구조

- `announce_watcher/app.py`: CLI 및 스케줄러 시작점
- `announce_watcher/config.py`: 설정 로드/예제 설정 생성/어댑터 빌드
- `announce_watcher/engine.py`: 공지 비교, 저장, 알림 호출
- `announce_watcher/storage.py`: SQLite 저장소
- `announce_watcher/notifier.py`: 알림 인터페이스 및 콘솔 구현
- `announce_watcher/sites/tukorea_board.py`: TUKOREA 게시판 파서/HTTP 어댑터
- `watcher_config.example.json`: 시작용 예제 설정 파일

## 다음 개발 후보

1. Windows 토스트 알림 붙이기
2. 설정 UI 또는 트레이 앱 추가
3. 로그인 필요한 사이트용 별도 어댑터 추가
4. 에러 로그 파일 저장 및 재시도 정책 추가
