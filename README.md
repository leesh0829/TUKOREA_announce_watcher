# TUKOREA announce watcher

공지사항을 백그라운드에서 주기적으로 확인하고, 처음 본 공지만 알리도록 설계한 Python 기반 감시기 스켈레톤입니다.

## 지금 상태에서 되는 것

- 등록된 사이트 어댑터를 주기적으로 실행합니다.
- 이미 본 공지는 SQLite DB에 저장해서 중복 알림을 막습니다.
- 기본값 기준으로 **첫 실행은 기존 공지를 기준선(baseline)으로만 저장하고 알리지 않습니다.**
- 두 번째 실행부터 새로 추가된 공지만 콘솔에 `[NEW] ...` 형태로 출력합니다.

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

테스트 의존성 없이 실행만 하려면:

```bash
python -m pip install -e .
```

> Windows에서 `announce-watcher`가 인식되지 않으면, 가상환경이 활성화되지 않았거나 설치가 아직 안 된 경우가 많습니다. 그럴 때는 먼저 위 설치 명령을 다시 실행하고, 당장 확인만 할 거면 `python -m announce_watcher.app`로 실행하면 됩니다.

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

## 첫 실행 알림 동작

기본값에서는 **첫 실행 때 기존 글이 있더라도 알림을 보내지 않습니다.**
첫 실행은 현재 목록을 DB에 저장해서 "여기까지는 이미 본 것"으로 기준선만 잡습니다.

즉:

1. 첫 실행 → 기존 글 저장만 하고 알림 없음
2. 이후 실행 → 그 뒤에 새로 생긴 글만 알림

만약 어떤 사이트는 첫 실행부터 알림을 받고 싶다면 `SiteConfig`에서 `notify_on_first_run=True`로 켤 수 있습니다.

```python
SiteConfig(
    name="sample-static",
    interval_seconds=60,
    enabled=True,
    login_mode="none",
    notify_on_first_run=False,
    settings={"base_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do"},
)
```

## 샘플 어댑터 링크에 `/welcome-notice`가 붙던 이유

기존 샘플 어댑터는 예시용 상세 페이지 경로를 강제로 뒤에 붙이도록 되어 있었습니다.
그래서 `base_url`만 실제 공지 URL로 바꿔도 `/welcome-notice`가 추가된 이상한 링크가 만들어졌습니다.

이제는 기본 동작이 아래처럼 바뀌었습니다.

- `settings["base_url"]`만 주면 그 URL 자체를 알림 링크로 사용
- 필요할 때만 `settings["notice_path"]`를 따로 넣어서 상세 경로를 붙임

예:

```python
settings={
    "base_url": "https://contract.tukorea.ac.kr/contract/2792/subview.do",
}
```

위처럼 넣으면 알림 링크도 그대로 `https://contract.tukorea.ac.kr/contract/2792/subview.do`가 됩니다.

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
    notify_on_first_run=False,
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
