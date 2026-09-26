# 설계 결정 기록

## 2026-09-26 — 프로젝트 기준

- 개발 저장소는 `planmaker-app`이다.
- 백엔드는 Python/FastAPI로 개발한다.
- 현재 정적 화면은 FastAPI가 제공한다.

## 2026-09-26 — 초기 도메인

- `User`, `OAuthIdentity`, `Plan`, `PlanParticipant`, `Notification`으로 시작한다.
- Availability, 예약, AI 코스 추천, 실제 푸시 알림은 초기 구현 범위에 넣지 않는다.

## 2026-09-26 — 로그인

- 로그인 제공자는 카카오, 네이버, Google, Apple이다.
- 첫 OAuth 로그인 시 Bakii 닉네임 입력을 필수로 한다.
- 닉네임은 서비스 내에서 고유하다.
- OAuth 계정은 `OAuthIdentity`로 분리하고 공급자 고유 사용자 ID로 식별한다.
- 이메일·비밀번호 로그인은 초기 범위에 넣지 않는다.

## 2026-09-26 — 시간과 알림

- 날짜·시간은 UTC로 저장하고 `Asia/Seoul` 기준으로 표시한다.
- 초기 알림은 인앱 알림 목록이다.
- Android/iOS 푸시 알림은 기본 약속 흐름 이후에 추가한다.
