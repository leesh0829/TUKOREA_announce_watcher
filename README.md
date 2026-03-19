# TUKOREA announce watcher

한국공학대학교 공지 게시판을 주기적으로 확인하고, 처음 본 공지만 알리도록 설계한 Python 기반 감시기입니다.

## 이번 변경 핵심

- `kpu.kdual.net`처럼 **로그인 페이지에서 아이디/비밀번호 입력 후 버튼 클릭**이 필요한 사이트를 위해 `playwright_login_board` 어댑터를 추가했습니다.
- `eclass.tukorea.ac.kr`처럼 **홈 진입 → 안내 팝업 확인 → 우측 상단 로그인 버튼 클릭 → 로그인 폼 입력 → 과목 선택 팝업에서 원하는 과목 선택** 흐름이 필요한 사이트도 Playwright 어댑터로 처리할 수 있게 했습니다.
- eclass는 이제 단순 URL 접근이 아니라, **과목 컨텍스트 선택(`#eclass_subject_change` → `#subject_room` → `.roomGo`)**까지 설정으로 처리합니다.

## 설치

```bash
git clone <repo-url>
cd TUKOREA_announce_watcher
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m pip install playwright
playwright install chromium
```

### Windows CMD

```bat
.venv\Scripts\activate.bat
python -m pip install -e .[dev]
python -m pip install playwright
playwright install chromium
```

## 설정 및 실행

### 1) 설정 파일 만들기

```bat
copy watcher_config.example.json watcher_config.json
```

### 2) 계정 입력

`watcher_config.json`에서 로그인 필요한 사이트들의:

- `settings.username`
- `settings.password`

를 본인 값으로 바꾸고,
사용할 사이트는 `enabled: true`로 변경합니다.

### 3) eclass 과목명 확인

각 eclass 사이트는 `course_name`이 맞아야 원하는 과목 컨텍스트로 진입합니다.

예:

```json
"course_name": "데이터구조와 알고리즘(01)"
```

과목명이 다르면 팝업 목록에서 매칭되지 않으므로, 본인 실제 과목명으로 수정해야 합니다.

### 4) 1회 테스트

```bash
announce-watcher --list-sites
announce-watcher --once
```

토스트 알림만 바로 확인하려면:

```bash
announce-watcher --test-notification
```

이 명령은 DB 이력이나 실제 새 공지 여부와 무관하게 현재 `notifier` 설정으로 테스트 알림을 1회 전송합니다. Windows 토스트 팝업을 보려면 `watcher_config.json`의 `notifier.type`이 `windows_toast`여야 합니다.
처음 토스트를 보낼 때는 앱 ID 등록용 시작 메뉴 바로가기를 자동으로 생성한 뒤 알림을 띄웁니다.

### 5) 상시 실행

```bash
announce-watcher
```

## 쉬운 시작/종료

터미널을 계속 열어두지 않고 실행하려면 루트 폴더에서 아래 스크립트를 사용하면 됩니다.

### 시작

PowerShell:

```powershell
.\start-watcher.ps1
```

CMD 또는 더블클릭:

```bat
start-watcher.cmd
```

### 상태 확인

```powershell
.\status-watcher.ps1
```

### 종료

```powershell
.\stop-watcher.ps1
```

이 스크립트들은:

- 백그라운드에서 감시기를 실행합니다.
- `logs/announce_watcher.pid`에 PID를 저장합니다.
- 이미 실행 중이면 중복 실행하지 않습니다.
- 종료 시 PID 파일을 읽어 해당 감시기 프로세스를 정리합니다.

PowerShell 실행 정책 때문에 `.ps1` 실행이 막히면 `.cmd` 파일을 사용하면 됩니다.

## 로그인 흐름 반영 방식

### KDUAL (`kpu.kdual.net`)

1. 로그인 페이지 진입
2. 아이디 입력
3. 비밀번호 입력
4. 로그인 버튼 클릭

위 흐름에 맞춰 Playwright 셀렉터를 넣었습니다.

### eclass (`eclass.tukorea.ac.kr`)

1. 메인 페이지 접속
2. 접속 종료 팝업이 뜨면 확인
3. 우측 상단 로그인 버튼 클릭 (`a[href="/ilos/main/member/login_form.acl"]`)
4. 로그인 폼에서 아이디/비밀번호 입력
5. 로그인 버튼 클릭
6. 현재 과목 표시(`#subject-span`) 확인
7. 다르면 과목 펼치기(`#eclass_subject_change`) 클릭
8. 팝업(`#subject_room`)에서 원하는 과목 `.roomGo` 선택

이 흐름을 Playwright 어댑터에 반영했습니다.

## eclass 과목 컨텍스트 관련 설정

eclass 항목은 아래 설정을 사용합니다.

- `subject_change_selector`: `#eclass_subject_change`
- `subject_popup_selector`: `#subject_room`
- `current_course_selector`: `#subject-span`
- `course_item_selector`: `.roomGo`
- `course_name`: 선택할 과목명

즉, 단순히 로그인만 하는 게 아니라 **원하는 과목 컨텍스트까지 맞춘 뒤** 공지/줌 페이지를 보게 됩니다.

## 감시 대상 사이트

### 브라우저 로그인 필요

1. `https://kpu.kdual.net/BBS/Board/List/S71855C704064`
2. `https://kpu.kdual.net/BBS/Board/List/S71954C705054`
3. `https://eclass.tukorea.ac.kr/ilos/st/course/notice_list_form.acl`
4. `https://eclass.tukorea.ac.kr/ilos/st/course/zoom_list_form.acl`
5. `https://eclass.tukorea.ac.kr/ilos/st/course/notice_list_form.acl`
6. `https://eclass.tukorea.ac.kr/ilos/st/course/notice_list_form.acl`
7. `https://eclass.tukorea.ac.kr/ilos/st/course/notice_list_form.acl`

### 로그인 불필요

8. `https://contract.tukorea.ac.kr/contract/2792/subview.do`
9. `https://contract.tukorea.ac.kr/contract/3844/subview.do`

## 주의사항

1. eclass는 세션/과목 컨텍스트 구조라서 `course_name`이 매우 중요합니다.
2. 팝업 과목명 텍스트가 실제 값과 조금이라도 다르면 선택이 실패할 수 있습니다.
3. 사이트 구조가 바뀌면 셀렉터를 수정해야 합니다.
4. 처음 디버깅할 때는 `headless: false`로 두고 눈으로 브라우저 동작을 확인하는 것을 권장합니다.

## 테스트

```bash
python -m pytest -q
```
