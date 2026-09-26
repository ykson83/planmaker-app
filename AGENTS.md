# Planmaker 개발 규칙

## 작업 범위

- 모든 개발은 이 저장소(`planmaker-app`)에서 진행한다.
- 현재 구현된 것은 FastAPI `/health`와 정적 화면뿐이다. 구현되지 않은 기능을 완료된 것으로 문서화하지 않는다.
- 사용자 요청이 없는 리팩터링, 패키지 추가, 외부 서비스 설정은 하지 않는다.

## 기술 기준

- Python 3.14 가상환경(`venv`)과 FastAPI를 사용한다.
- 영속성은 SQLAlchemy 2.x와 MySQL을 사용할 예정이며, 스키마 변경은 Alembic migration으로 관리한다.
- API 계층은 Router, Service, Repository, Schema(Pydantic)를 분리한다.
- API 응답에 ORM Entity나 OAuth 공급자 토큰을 직접 노출하지 않는다.

## 도메인 규칙

- 초기 도메인은 User, OAuthIdentity, Plan, PlanParticipant, Notification이다.
- User의 닉네임은 서비스 내에서 고유하며 첫 OAuth 로그인 시 반드시 설정한다.
- OAuth 제공자는 KAKAO, NAVER, GOOGLE, APPLE이다.
- 계정 식별은 `(provider, provider_user_id)` 복합 UNIQUE 제약을 사용한다. 공급자 이메일·닉네임은 식별자로 사용하지 않는다.
- Plan 생성자는 PlanParticipant에 자동 참여한다. `(plan_id, user_id)`는 UNIQUE 제약으로 중복 참여를 막는다.
- 시간은 UTC로 저장하고 화면에서는 `Asia/Seoul` 기준으로 표시한다. `starts_at < ends_at`을 검증한다.
- Owner/Guest 같은 고정 role 컬럼은 User나 PlanParticipant에 추가하지 않는다.

## 보안과 설정

- `.env`, OAuth Client Secret, Apple private key, DB 비밀번호는 절대 커밋하지 않는다.
- 실제 비밀값은 로컬 `.env` 또는 배포 환경의 비밀값 저장소에만 둔다. `.env.example`에는 키 이름만 유지한다.
- OAuth 인가 코드 교환과 공급자 토큰 검증은 서버에서만 처리한다.
- 서비스는 자체 인증 토큰 또는 안전한 세션으로 로그인 상태를 관리한다.

## 품질과 Git

- 새 기능에는 정상·실패 경로 테스트를 함께 추가한다.
- 시간 의존 테스트는 고정 시각 또는 주입 가능한 Clock을 사용한다.
- API·DB 계약 변경 시 `docs/api-contract.md`, `docs/decisions.md`를 함께 갱신한다.
- 기능 단위로 커밋하며, 기존 사용자 변경을 덮어쓰지 않는다.

## 응답 방식

- 작업 결과는 구현 내용, 테스트 결과, 남은 결정 사항만 간결하게 보고한다.
- 범위가 불명확하거나 외부 계정·비밀값이 필요한 경우, 임의로 진행하지 말고 필요한 정보를 요청한다.
