# PRD — Mawasilati (Multimodal Transport Platform, Egypt)

## 1. نظرة عامة
منصة نقل متعددة الوسائط: مصادقة JWT حقيقية، تخطيط/حجز/تتبع رحلات على PostgreSQL، مدفوعات، بحث مسارات، تتبع سائقين لحظي عبر WebSocket، مساعد AI.

## 2. المستخدمون
- راكب (تسجيل، تخطيط، حجز، تتبع، دفع)
- سائق (موقع لحظي، طلبات، heatmap)
- مشغّل (مقاييس، إسناد)

## 3. الميزات الأساسية (قابلة للاختبار)
1. تسجيل/دخول/تجديد/خروج JWT + ملف المستخدم (`POST /api/v1/auth/register|/login|/refresh|/logout`, `GET /api/v1/auth/me|/profile`)
2. تخطيط رحلة وخيارات وحجز وتتبع وسجل (`POST /api/v1/trip/plan|/book`, `GET /api/v1/trip/options|/track/{trip_id}|/history`)
3. بحث مسارات ومحطات وبيانات لحظية (`GET /api/v1/routes/search|/{route_id}/stops|/realtime`)
4. دفع: بدء/تأكيد/سجل (`POST /api/v1/payment/initiate|/confirm`, `GET /api/v1/payment/history`)
5. مساعد AI ومحلل رحلات (`POST /api/v1/ai/chat|/parse-trip`)
6. سائق: موقع وheatmap وطلبات (`POST /api/v1/driver/location`, `GET /api/v1/driver/heatmap|/requests`)
7. إسناد سائق لرحلة (`POST /api/v1/dispatch/trips/{trip_id}/assign/{driver_id}`)
8. تتبع لحظي WebSocket (`/ws/trip/{trip_id}?role=driver|passenger&token=<jwt>`، بث `{"type":"location",...}`، رفض 4401 للتوكن/الدور غير الصالح)
9. صحة/جاهزية ومقاييس (`GET /health`, `GET /api/v1/health`, `GET /ready`, `GET /api/v1/operations/metrics`)

## 4. API endpoints الحقيقية (من الكود فقط)
- البادئة: `/api/v1` (`api_v1_prefix='/api/v1'`)؛ الراوترات: `/auth|/trip|/routes|/payment|/ai|/driver|/dispatch|/operations` كما أعلاه
- الجذر: `GET /health`, `GET /api/v1/health`, `GET /ready`
- WebSocket: `ws(s)://<host>/ws/trip/{trip_id}` (خارج بادئة `/api/v1`)

## 5. بيانات الدخول/الإعداد للاختبار
- `cp ../.env.example ../.env` ثم `docker compose up -d postgres redis` وتشغيل `uvicorn app.main:app --reload` من `backend/` (افتراضي `ENVIRONMENT=development` ينشئ الجداول تلقائيا؛ للإنتاج Alembic)
- الاختبارات: `cd backend && python -m pytest`؛ لا مستخدمين مزروعين — أنشئ عبر `POST /api/v1/auth/register` واستخدم `access_token` في `Authorization: Bearer` وWS

## 6. خارج النطاق (mocked/simulated)
- بوابات الدفع (Instapay/Visa) تسجّل صفوفا حقيقية لكن دون نداء حي؛ محلل AI regex عربي (لا Gemini/Dify)؛ لا Firebase push؛ لا `google_maps_flutter`؛ مدير WS in-memory لنسخة واحدة (يلزم Redis pub/sub للتوسع).
