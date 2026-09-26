# Planmaker 아키텍처

## 현재 구현 상태

- FastAPI 애플리케이션: `app/main.py`
- Router: `app/api/health.py`의 `GET /health`
- 기존 `main.py`는 `uvicorn main:app` 실행 호환성을 위한 진입점
- 정적 대시보드 화면 (`static/`)
- `tests/test_application.py`에서 health, 대시보드, 404 응답 테스트
- `compose.yaml`에서 MySQL 8.4 개발 환경을 제공
- `app/db/`의 SQLAlchemy Base·세션 의존성 및 `alembic/` migration 기반

아래 구조에서 `app/`, `app/api/`, `app/main.py`는 구현됐다. 나머지 패키지는 기능 구현과 함께 추가하며, 아직 구현된 기능으로 간주하지 않는다.

## 목표 패키지 구조

```text
app/
├─ main.py
├─ api/             # HTTP Router
├─ schemas/         # Pydantic request/response
├─ services/        # 유스케이스와 트랜잭션
├─ repositories/    # 데이터 조회와 저장
├─ domain/          # SQLAlchemy 모델
├─ auth/            # OAuth와 서비스 인증
└─ db/              # Engine, Session, Alembic metadata
```

## 초기 도메인

```text
User 1 ── N OAuthIdentity
User 1 ── N Plan               (creator)
User N ── N PlanParticipant ── 1 Plan
User 1 ── N Notification
Plan 1 ── N PlanInvitationLink (구현 예정)
```

### User

- 서비스 사용자
- `nickname`은 고유하며 OAuth 첫 로그인 온보딩에서 설정한다.

### OAuthIdentity

- 외부 로그인 계정 연결 정보
- 지원할 제공자: `KAKAO`, `NAVER`, `GOOGLE`, `APPLE`; 초기 활성 제공자: 카카오, 네이버, Google
- `(provider, provider_user_id)`는 고유하다.

### Plan

- 친구끼리 만드는 약속
- 생성자, 제목, 내용, 시작·종료 시각, 장소, 상태를 가진다.
- 생성자는 참여자로 자동 추가한다.

### PlanParticipant

- Plan과 User의 참여 관계
- 응답 상태: `PENDING`, `ACCEPTED`, `DECLINED`
- 한 사용자는 동일 Plan에 한 번만 참여한다.

### PlanInvitationLink

- 미가입자에게 공유할 약속 초대 링크 지원 엔터티
- 무작위 원본 토큰 대신 그 해시를 저장하고, 생성 뒤 7일 후 만료한다.
- 링크 사용자는 OAuth 로그인과 닉네임 온보딩 후 참여를 확인하며, 확인 시 `ACCEPTED` 참여자로 추가된다.

### Notification

- 초대, 참여 응답, 약속 변경·취소를 사용자에게 전달하기 위한 서비스 내 알림
- 초기에는 읽음 상태를 포함한 인앱 알림으로 구현한다.

## 인증 흐름

```text
OAuth 제공자 로그인
→ FastAPI callback
→ OAuthIdentity 조회 또는 생성
→ 첫 로그인이라면 닉네임 온보딩
→ Planmaker 서버 세션 발급
```

OAuth 공급자 토큰은 서버에서만 다룬다. 로그인 상태는 불투명한 서버 세션 ID를 `HttpOnly` 쿠키에 보관해 유지하며, 운영 환경에서는 `Secure`·`SameSite=Lax`를 적용한다. 상태 변경 요청은 CSRF 토큰 검증을 거친다.

## 로컬 MySQL 실행

`.env.example`을 `.env`로 복사한 뒤 `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`에 로컬 전용 값을 설정한다. `.env`는 Git에서 제외된다.

```powershell
docker compose up -d mysql
docker compose ps
```

MySQL은 `utf8mb4`와 `utf8mb4_0900_ai_ci`로 실행되며, `planmaker_mysql_data` named volume에 데이터를 보관한다.
