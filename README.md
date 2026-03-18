# TUKOREA announce watcher

공지사항을 백그라운드에서 주기적으로 확인하고, 처음 본 공지만 알리도록 설계한 Python 기반 감시기 스켈레톤입니다.

## 지금 상태에서 되는 것

- 샘플 사이트 어댑터 1개를 주기적으로 실행합니다.
- 이미 본 공지는 SQLite DB에 저장해서 중복 알림을 막습니다.
- 새 공지가 감지되면 콘솔에 `[NEW] ...` 형태로 출력합니다.

## 요구 사항

- Python 3.11 이상
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

### 3) 패키지 설치

개발용 테스트 의존성까지 같이 설치하려면:

```bash
pip install -e .[dev]
```

테스트 의존성 없이 실행만 하려면:

```bash
pip install -e .
```

## 실행 방법

설치가 끝났으면 아래 둘 중 하나로 실행하면 됩니다.

### 방법 A: 모듈로 실행

```bash
python -m announce_watcher.app
```

### 방법 B: 콘솔 명령으로 실행

```bash
announce-watcher
```

실행되면 현재 등록된 어댑터를 즉시 한 번 체크하고, 그 다음부터는 `interval_seconds` 간격으로 계속 확인합니다.

현재 기본 설정은 `announce_watcher/config.py`에 들어 있는 샘플 사이트 1개이며, 첫 실행 시 새 공지가 있으면 아래처럼 출력됩니다.

```text
[NEW] sample-static: Sample notice -> https://example.com/notices/welcome-notice
```

## 종료 방법

터미널에서 `Ctrl + C`를 누르면 스케줄러가 종료됩니다.

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
- `announce_watcher/sites/`: 사이트별 어댑터 구현 위치

## 설정 바꾸는 방법

기본 샘플 사이트 설정은 `announce_watcher/config.py`의 `build_site_adapters()`에서 관리합니다.

예를 들어 체크 주기를 바꾸려면 `interval_seconds` 값을 수정하면 됩니다.

```python
SiteConfig(
    name="sample-static",
    interval_seconds=300,
    enabled=True,
    login_mode="none",
    settings={"base_url": "https://example.com/notices"},
)
```

## 실제 사이트를 붙이려면

1. `announce_watcher/sites/` 아래에 새 어댑터 파일을 만듭니다.
2. `SiteAdapter`를 상속하고 `fetch_notices()`를 구현합니다.
3. 공지마다 고유한 `notice_key`를 안정적으로 만들도록 합니다.
4. `announce_watcher/config.py`에서 어댑터를 등록합니다.
5. Windows 토스트 알림이 필요하면 `ConsoleNotifier`를 실제 notifier 구현으로 교체합니다.

## 참고

- 로컬 DB 파일은 기본적으로 `watcher.db`로 생성됩니다.
- 현재는 샘플 구현이라 실제 크롤링/로그인 처리는 들어 있지 않습니다.
- 로그인 필요한 사이트는 추후 사이트 어댑터에서 세션/브라우저 자동화를 추가하는 방식으로 확장하면 됩니다.
