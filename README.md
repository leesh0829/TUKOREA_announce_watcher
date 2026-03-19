# TUKOREA announce watcher

한국공학대학교 공지 게시판을 주기적으로 확인하고, 처음 본 공지만 알리도록 설계한 Python 기반 감시기입니다.

## 이번 변경 핵심

- `kpu.kdual.net`처럼 **로그인 페이지에서 아이디/비밀번호 입력 후 버튼 클릭**이 필요한 사이트를 위해 `playwright_login_board` 어댑터를 추가했습니다.
- `eclass.tukorea.ac.kr`처럼 **홈 진입 → 안내 팝업 확인 → 우측 상단 로그인 버튼 클릭 → 로그인 폼 입력** 흐름이 필요한 사이트도 같은 Playwright 어댑터로 처리할 수 있게 설정 예시를 넣었습니다.
- 기존의 단순 폼 POST용 `authenticated_tukorea_board`는 그대로 남겨 두되, KDUAL/eclass 예제는 브라우저 클릭 흐름 기준으로 바꿨습니다.

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

> 로그인 필요한 사이트를 쓰려면 Playwright와 Chromium 설치가 필요합니다.

## 설정 및 실행

### 1) 설정 파일 만들기

```bat
copy watcher_config.example.json watcher_config.json
```

### 2) 계정 입력

`watcher_config.json`에서 로그인 필요한 사이트들의 아래 값을 바꿉니다.

- `settings.username`
- `settings.password`

그리고 사용할 사이트는 `enabled: true`로 바꿉니다.

### 3) 1회 테스트

```bash
announce-watcher --list-sites
announce-watcher --once
```

### 4) 상시 실행

```bash
announce-watcher
```

## 로그인 흐름 반영 방식

### KDUAL (`kpu.kdual.net`)

사용자 설명대로:

1. 로그인 페이지 진입
2. 아이디 입력
3. 비밀번호 입력
4. 로그인 버튼 클릭

흐름으로 처리하도록 Playwright 설정을 넣었습니다.

예제 설정은 `input[type="text"]`, `input[type="password"]`, 그리고 "로그인" 텍스트가 있는 버튼/submit을 사용하도록 되어 있습니다.

### eclass (`eclass.tukorea.ac.kr`)

사용자 설명대로:

1. 메인 페이지 접속
2. 접속 종료 팝업이 뜨면 확인
3. 우측 상단 로그인 버튼 클릭 (`a[href="/ilos/main/member/login_form.acl"]`)
4. 로그인 폼에서 아이디/비밀번호 입력
5. 로그인 버튼 클릭

흐름으로 맞췄습니다.

Playwright 어댑터는 페이지의 JS dialog를 자동으로 accept 하도록 되어 있어서, 설명하신 "확인" 팝업 흐름을 반영할 수 있습니다.

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

## 설정 파일에서 확인할 항목

- `adapter_type`
  - `tukorea_board`: 로그인 없는 게시판
  - `authenticated_tukorea_board`: 단순 폼 POST 로그인
  - `playwright_login_board`: 브라우저 클릭 로그인 흐름
- `login_button_selector`: eclass처럼 로그인 버튼을 먼저 눌러야 할 때 사용
- `username_selector`, `password_selector`, `submit_selector`: 실제 로그인 폼 셀렉터
- `headless`: 브라우저를 숨길지 여부

## 주의사항

1. KDUAL/eclass는 브라우저 흐름이 있는 사이트라서 현재는 Playwright 방식이 더 적합합니다.
2. 사이트 HTML이 바뀌면 셀렉터(`username_selector`, `password_selector`, `submit_selector`)를 수정해야 할 수 있습니다.
3. eclass의 동일 URL 공지들은 실제로는 과목 컨텍스트가 세션 상태에 묶여 있을 수 있어서, 과목별 파라미터가 더 필요할 수 있습니다.
4. Playwright 트러블슈팅이 필요하면 우선 `headless: false`로 바꿔서 눈으로 로그인 과정을 확인하는 게 좋습니다.

## 테스트

```bash
python -m pytest -q
```
