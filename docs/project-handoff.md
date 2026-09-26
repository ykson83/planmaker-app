# Planmaker 개발 인수인계

> 이 문서는 다른 Codex 세션 또는 개발자가 현재 상태에서 개발을 이어가기 위한 기준 문서다.
> 작성일: 2026-09-26

## 1. 프로젝트 목표

Planmaker(Bakii)는 친구끼리 약속을 만들고, 참여자를 초대하며, 약속 관련 알림을 받는 웹 서비스다.

- 첫 단계는 반응형 웹으로 제공한다.
- Android/iOS에서는 우선 모바일 브라우저로 사용할 수 있어야 한다.
- 이후 필요하면 Flutter 또는 React Native 앱이 동일한 API를 사용하도록 확장한다.
- 추후 AI API로 장소·코스 추천을 추가할 수 있으나, 초기 구현 범위에는 넣지 않는다.

## 2. 원본 기획 문서의 핵심

`bakii_notion.md`는 Python/FastAPI 백엔드 학습과 서비스 구현을 함께 다룬 5단계 로드맵이다. 파일의 일부 한글 인코딩이 깨져 보일 수 있으므로, 아래 요약을 기준으로 사용한다.

1. FastAPI와 Pydantic으로 User/Plan 기본 API를 만든다.
2. SQLAlchemy 2.x와 MySQL을 연결하고 관계를 매핑한다.
3. Service, Transaction, 검증, pytest를 추가한다.
4. LLM Structured Output으로 자연어 약속 생성·검색을 추가한다.
5. Agent, Docker, 전체 테스트를 추가한다.

현재 프로젝트는 **1~3단계의 기본 약속 서비스**를 먼저 완성한다. AI, Agent, Docker는 기본 흐름이 안정된 뒤 별도 작업으로 진행한다.

## 3. 현재 구현 상태

### 구현됨

- Python 3.14 가상환경: `venv/`
- FastAPI: `main.py`
- `GET /health` → `{"status":"ok"}`
- `GET /` → 정적 대시보드 화면
- 정적 화면: `static/index.html`, `static/bakii.css`, `static/bakii.js`
- 화면에는 다가오는 약속, 초대, 알림 패널, 약속 생성 모달의 시안이 있다.

### 아직 구현되지 않음

- DB와 SQLAlchemy 모델
- Alembic migration
- 회원·OAuth 로그인 처리
- 서비스 자체 인증 세션 또는 토큰
- User, Plan, PlanParticipant, Notification API
- 실제 약속 저장·참여·알림
- 실제 푸시 알림
- AI 코스 추천

정적 화면의 약속 데이터와 모달 동작은 현재 시연용이다. 실제 API와 연결되어 있지 않다.

## 4. 확정된 기술과 구조

### 기술

- Python 3.14
- FastAPI
- Pydantic
- 향후 SQLAlchemy 2.x + MySQL
- 향후 Alembic
- pytest

목표 코드 구조:

```text
app/
├─ main.py
├─ api/             # HTTP Router
├─ schemas/         # Pydantic request/response 모델
├─ services/        # 유스케이스와 트랜잭션
├─ repositories/    # 데이터 조회와 저장
├─ domain/          # SQLAlchemy 모델
├─ auth/            # OAuth와 서비스 인증
└─ db/              # Engine, Session, Alembic metadata
tests/
```

Router는 HTTP 입출력, Service는 유스케이스·트랜잭션, Repository는 영속성 조회를 담당한다. API schema와 ORM 모델을 직접 공유하지 않는다.

## 5. 확정된 도메인 설계

```text
User 1 ── N OAuthIdentity
User 1 ── N Plan               (creator)
User N ── N PlanParticipant ── 1 Plan
User 1 ── N Notification
```

### User

서비스 사용자다.

- `id`
- `nickname` — 서비스 내 고유값, 첫 OAuth 로그인 시 필수 입력
- `created_at`, `updated_at`

### OAuthIdentity

외부 로그인 계정 연결 정보다.

- `id`
- `user_id`
- `provider` — `KAKAO`, `NAVER`, `GOOGLE`, `APPLE`
- `provider_user_id` — OAuth 공급자가 제공하는 변경되지 않는 고유 사용자 ID
- `created_at`
- `UNIQUE(provider, provider_user_id)`

공급자가 제공하는 이메일이나 닉네임은 계정 식별자로 사용하지 않는다. 하나의 User는 여러 OAuthIdentity를 연결할 수 있다.

### Plan

친구끼리 만드는 약속이다.

- `id`
- `creator_id`
- `title`
- `content` — 선택
- `starts_at`, `ends_at`
- `location` — 선택
- `status` — 초기 후보: `SCHEDULED`, `CANCELED`
- `created_at`, `updated_at`

`starts_at < ends_at`을 서비스 검증과 DB 제약으로 보장한다.

### PlanParticipant

약속과 참여자의 관계다.

- `id`
- `plan_id`
- `user_id`
- `response_status` — `PENDING`, `ACCEPTED`, `DECLINED`
- `created_at`, `updated_at`
- `UNIQUE(plan_id, user_id)`

Plan 생성자는 PlanParticipant에 자동 추가한다. Owner/Guest를 User 또는 PlanParticipant의 고정 role 컬럼으로 만들지 않는다.

### Notification

초대, 참여 응답, 약속 변경·취소를 위한 인앱 알림이다.

- `id`
- `user_id`
- `plan_id` — 선택
- `type`
- `message`
- `read_at` — 읽지 않음은 `NULL`
- `created_at`

초기에는 인앱 목록만 구현한다. Android/iOS 푸시 알림과 기기 토큰 관리는 이후 범위다.

## 6. 로그인과 OAuth 결정

초기 로그인 제공자:

- 카카오
- 네이버
- Google
- Apple

공통 흐름:

```text
로그인 버튼
→ OAuth 공급자 인가 화면
→ FastAPI callback에서 인가 코드 검증·토큰 교환
→ OAuthIdentity 조회 또는 생성
→ 신규 User면 닉네임 온보딩
→ Planmaker 자체 로그인 세션 또는 토큰 발급
```

OAuth 공급자 토큰, Client Secret, Apple private key는 서버에서만 처리한다. 클라이언트에 공급자 토큰이나 비밀값을 전달하지 않는다.

`.env.example`에는 다음 설정 키가 준비되어 있다.

```text
APP_BASE_URL
KAKAO_CLIENT_ID / KAKAO_CLIENT_SECRET
NAVER_CLIENT_ID / NAVER_CLIENT_SECRET
GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
APPLE_CLIENT_ID / APPLE_TEAM_ID / APPLE_KEY_ID / APPLE_PRIVATE_KEY
```

실제 값은 `.env` 또는 배포 환경의 Secret Store에만 저장하며 절대 커밋하지 않는다.

## 7. 시간 정책

- DB에는 UTC 기준 시간을 저장한다.
- 초기 화면과 사용자 입력은 `Asia/Seoul` 기준으로 처리한다.
- 문자열 비교가 아니라 `datetime`, timezone-aware 값, `timedelta` 등 명시적인 시간 타입을 사용한다.

## 8. API 구현 순서

아래 순서로 진행한다.

1. `app/` 및 `tests/` 패키지 구조를 만들고 기존 `main.py`를 이동·정리한다.
2. SQLAlchemy, MySQL, Alembic을 설정한다.
3. User와 OAuthIdentity migration·repository·service를 구현한다.
4. OAuth callback 및 첫 로그인 닉네임 온보딩 API를 구현한다.
5. 서비스 자체 인증 방식(세션 또는 access/refresh token)을 확정하고 보호된 API 의존성을 구현한다.
6. Plan과 PlanParticipant 생성·조회·초대·응답 API를 구현한다.
7. Notification 생성·목록·읽음 처리 API를 구현한다.
8. 정적 화면을 실제 API에 연결한다.
9. 정상·실패 경로 테스트와 Docker 개발 환경을 추가한다.

초기 API 후보는 아래와 같으나, HTTP 경로·모델은 구현 시작 시 `docs/api-contract.md`에 확정한다.

```text
GET  /health
GET  /auth/{provider}/login
GET  /auth/{provider}/callback
POST /auth/onboarding/nickname
GET  /me
POST /auth/logout

POST /plans
GET  /plans
GET  /plans/{plan_id}
PATCH /plans/{plan_id}
POST /plans/{plan_id}/participants
PATCH /plans/{plan_id}/participants/me

GET   /notifications
PATCH /notifications/{notification_id}/read
```

## 9. 테스트 기준

새 도메인 기능은 정상 경로와 실패 경로를 모두 테스트한다.

- 닉네임 중복
- 같은 OAuth 계정의 중복 가입 방지
- OAuth 완료 전 닉네임 미설정 사용자 차단
- 종료 시각이 시작 시각보다 빠르거나 같은 약속 거부
- 존재하지 않는 참여자 초대 거부
- 동일 약속 중복 참여 거부
- 취소된 약속 변경·참여 정책
- 알림의 소유자 외 읽음 처리 거부

현재 시각에 의존하는 테스트는 고정 시각 또는 주입 가능한 Clock을 사용한다.

## 10. 아직 사용자 결정이 필요한 사항

다음은 구현 전에 또는 구현 중 결정이 필요하다.

1. **서비스 인증 방식**: 웹 HttpOnly 세션/쿠키 중심으로 할지, access/refresh token 중심으로 할지
2. **OAuth 활성화 순서**: 카카오·네이버부터 실제 연결하고 Google·Apple은 설정값 확보 후 활성화할지
3. **Apple 개발자 설정**: Apple Developer 계정·서비스 ID·키 발급 준비 여부
4. **MySQL 개발 환경**: 로컬 MySQL을 사용할지 Docker Compose로 시작할지
5. **닉네임 정책**: 길이, 허용 문자, 변경 가능 여부
6. **친구 초대 방식**: 가입 사용자 닉네임 검색부터 시작할지, 초대 링크도 초기 범위에 넣을지
7. **약속 수정 권한과 취소 규칙**: 생성자만 수정·취소 가능한지, 참여자에게 어떤 알림을 보내는지

## 11. Git 상태와 실행 방법

- 기본 브랜치: `main`
- 최초 커밋: `21714fe chore: initialize planmaker app`
- 원격 저장소는 아직 연결되지 않았다.
- 다음 세션 시작 전 `AGENTS.md`와 이 문서, `docs/decisions.md`를 먼저 읽는다.

로컬 실행:

```powershell
cd D:\toy_project\planmaker-app
.\venv\Scripts\uvicorn.exe main:app --reload
```

확인 주소:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## 12. 반드시 지킬 규칙

- 작업은 `planmaker-app`에서만 한다.
- 현재 구현되지 않은 기능을 구현되었다고 문서화하지 않는다.
- `.env`, `venv/`, OAuth 비밀값, DB 비밀번호를 Git에 추가하지 않는다.
- 새 기능의 API·DB 계약이 바뀌면 `docs/api-contract.md`와 `docs/decisions.md`를 함께 갱신한다.
- 기존 변경을 덮어쓰지 말고, 기능 단위로 테스트 후 커밋한다.
