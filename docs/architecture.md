# Planmaker 아키텍처

## 현재 구현 상태

- FastAPI 애플리케이션
- `GET /health`
- 정적 대시보드 화면 (`static/`)

아래 구조는 목표 구조이며, 아직 구현된 기능으로 간주하지 않는다.

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
```

### User

- 서비스 사용자
- `nickname`은 고유하며 OAuth 첫 로그인 온보딩에서 설정한다.

### OAuthIdentity

- 외부 로그인 계정 연결 정보
- 제공자: `KAKAO`, `NAVER`, `GOOGLE`, `APPLE`
- `(provider, provider_user_id)`는 고유하다.

### Plan

- 친구끼리 만드는 약속
- 생성자, 제목, 내용, 시작·종료 시각, 장소, 상태를 가진다.
- 생성자는 참여자로 자동 추가한다.

### PlanParticipant

- Plan과 User의 참여 관계
- 응답 상태: `PENDING`, `ACCEPTED`, `DECLINED`
- 한 사용자는 동일 Plan에 한 번만 참여한다.

### Notification

- 초대, 참여 응답, 약속 변경·취소를 사용자에게 전달하기 위한 서비스 내 알림
- 초기에는 읽음 상태를 포함한 인앱 알림으로 구현한다.

## 인증 흐름

```text
OAuth 제공자 로그인
→ FastAPI callback
→ OAuthIdentity 조회 또는 생성
→ 첫 로그인이라면 닉네임 온보딩
→ Planmaker 로그인 세션 또는 토큰 발급
```

OAuth 공급자 토큰은 서버에서만 다루며, 클라이언트에는 Planmaker 인증 수단만 전달한다.
