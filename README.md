# TUKOREA announce watcher

한국공학대학교 공지 게시판을 주기적으로 확인하고, 처음 본 공지만 알리도록 설계한 Python 기반 감시기입니다.

## 현재 구현된 단계

- TUKOREA K2Web 게시판용 HTTP 어댑터가 기본 포함되어 있습니다.
- 기본 대상은 `https://contract.tukorea.ac.kr/contract/2792/subview.do` 게시판입니다.
- 이미 본 공지는 SQLite DB에 저장해서 중복 알림을 막습니다.
- 첫 실행은 기존 게시물을 기준선으로만 저장하고 알리지 않습니다.
- 두 번째 실행부터 새로 올라온 공지만 콘솔에 `[NEW] ...` 형태로 출력합니다.

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

> Windows에서 `announce-watcher`가 인식되지 않으면, 가상환경이 활성화되지 않았거나 설치가 아직 안 된 경우가 많습니다. 그럴 때는 먼저 위 설치 명령을 다시 실행하고, 당장 확인만 할 거면 `python -m announce_watcher.app`로 실행하면 됩니다.

## 실행 방법

### 방법 A: 모듈로 실행

```bash
python -m announce_watcher.app
```

### 방법 B: 콘솔 명령으로 실행

```bash
announce-watcher
```

실행되면 현재 등록된 게시판을 즉시 한 번 체크하고, 그 다음부터는 `interval_seconds` 간격으로 계속 확인합니다.

## 첫 실행 알림 동작

기본값에서는 **첫 실행 때 기존 글이 있더라도 알림을 보내지 않습니다.**
첫 실행은 현재 목록을 DB에 저장해서 "여기까지는 이미 본 것"으로 기준선만 잡습니다.

즉:

1. 첫 실행 → 기존 글 저장만 하고 알림 없음
2. 이후 실행 → 그 뒤에 새로 생긴 글만 알림

원하면 `SiteConfig(notify_on_first_run=True)`로 사이트별 첫 실행 알림을 켤 수 있습니다.

## 현재 기본 감시 대상

기본 설정은 `announce_watcher/config.py`에 있고, 현재는 아래 게시판을 감시합니다.

- `https://contract.tukorea.ac.kr/contract/2792/subview.do`

이 URL은 실제 게시판 목록 페이지이며, 어댑터가 목록에서 각 공지의 상세 URL을 자동으로 파싱합니다.

## 설정 바꾸는 방법

기본 사이트 설정은 `announce_watcher/config.py`의 `build_site_adapters()`에서 관리합니다.

예:

```python
SiteConfig(
    name="tukorea-contract-notices",
    interval_seconds=300,
    enabled=True,
    login_mode="none",
    notify_on_first_run=False,
    settings={
        "board_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do",
        "timeout_seconds": 20,
    },
)
```

- `interval_seconds`: 몇 초마다 확인할지
- `board_url`: 감시할 게시판 목록 URL
- `timeout_seconds`: HTTP 요청 타임아웃

## 테스트 방법

```bash
python -m pytest -q
```

## 파일 구조

- `announce_watcher/app.py`: 스케줄러 시작점
- `announce_watcher/config.py`: 감시 대상 사이트 등록
- `announce_watcher/engine.py`: 공지 비교, 저장, 알림 호출
- `announce_watcher/storage.py`: SQLite 저장소
- `announce_watcher/notifier.py`: 알림 인터페이스 및 콘솔 구현
- `announce_watcher/sites/tukorea_board.py`: TUKOREA 게시판 파서/HTTP 어댑터

## 다음 단계로 확장하려면

1. 다른 게시판 URL을 `config.py`에 추가해서 다중 감시 지원
2. 콘솔 출력 대신 Windows 토스트 알림 구현
3. 필요시 로그인/세션 기반 게시판용 별도 어댑터 추가
4. 설정 파일 분리(JSON/YAML/.env)
