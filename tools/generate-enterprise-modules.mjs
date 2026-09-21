import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

const root = "/home/ubuntu/Mawasilati-Enterprise";
const domains = [
  ["journeys", "Journey", "trip planning, options, and route preference"],
  ["bookings", "Booking", "reservation lifecycle and passenger ownership"],
  ["dispatch", "Dispatch", "driver assignment and capacity coordination"],
  ["pricing", "Pricing", "fare quotes, promotions, and quote expiry"],
  ["payments", "Payment", "payment intent, confirmation, and reconciliation boundary"],
  ["tracking", "Tracking", "live location, consent, and journey room ownership"],
  ["safety", "Safety", "incident reporting, emergency actions, and audit evidence"],
];
const features = ["journey-planner", "booking-flow", "live-tracking", "driver-console", "wallet", "safety-center", "trip-history"];

async function emit(relativePath, content) {
  const target = path.join(root, relativePath);
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, content.trimStart(), "utf8");
}

for (const [domain, entity, purpose] of domains) {
  const folder = `backend/app/domain/${domain}`;
  await emit(`${folder}/__init__.py`, `"""${entity} bounded context: ${purpose}."""\nfrom .contracts import ${entity}Snapshot\nfrom .policies import requires_confirmation\n\n__all__ = ["${entity}Snapshot", "requires_confirmation"]\n`);
  await emit(`${folder}/contracts.py`, `from datetime import datetime\nfrom pydantic import BaseModel, Field\n\nclass ${entity}Snapshot(BaseModel):\n    identifier: str = Field(min_length=1, max_length=150)\n    status: str = Field(min_length=1, max_length=40)\n    user_id: int | None = None\n    correlation_id: str | None = None\n    updated_at: datetime | None = None\n\nclass ${entity}Page(BaseModel):\n    items: list[${entity}Snapshot] = Field(default_factory=list)\n    next_cursor: str | None = None\n`);
  await emit(`${folder}/commands.py`, `from dataclasses import dataclass\n\n@dataclass(frozen=True)\nclass Create${entity}:\n    actor_id: int\n    correlation_id: str\n    reason: str | None = None\n\n@dataclass(frozen=True)\nclass Change${entity}Status:\n    identifier: str\n    status: str\n    actor_id: int\n    reason: str | None = None\n`);
  await emit(`${folder}/events.py`, `from dataclasses import dataclass\nfrom datetime import datetime, timezone\n\n@dataclass(frozen=True)\nclass ${entity}Event:\n    event_type: str\n    identifier: str\n    correlation_id: str\n    occurred_at: datetime\n\n    @classmethod\n    def now(cls, event_type: str, identifier: str, correlation_id: str):\n        return cls(event_type, identifier, correlation_id, datetime.now(timezone.utc))\n`);
  await emit(`${folder}/policies.py`, `CONFIRMATION_ACTIONS = {"PAYMENT_CAPTURE", "DRIVER_ASSIGNMENT", "EMERGENCY_ESCALATION", "FARE_ADJUSTMENT"}\n\ndef requires_confirmation(action: str, risk: str = "LOW") -> bool:\n    return action.upper() in CONFIRMATION_ACTIONS or risk.upper() in {"HIGH", "CRITICAL"}\n\ndef may_share_location(consent: bool, role: str) -> bool:\n    return consent and role in {"driver", "passenger", "dispatcher"}\n`);
  await emit(`${folder}/repository.py`, `from typing import Protocol\nfrom .contracts import ${entity}Page, ${entity}Snapshot\n\nclass ${entity}Repository(Protocol):\n    def get(self, identifier: str, actor_id: int) -> ${entity}Snapshot | None: ...\n    def list_for_user(self, actor_id: int, cursor: str | None = None, limit: int = 50) -> ${entity}Page: ...\n`);
  await emit(`${folder}/service.py`, `from .contracts import ${entity}Snapshot\n\ndef display_label(snapshot: ${entity}Snapshot) -> str:\n    return f"{snapshot.identifier} · {snapshot.status}"\n\ndef is_terminal(status: str) -> bool:\n    return status.upper() in {"CANCELLED", "COMPLETED", "FAILED", "EXPIRED"}\n`);
  await emit(`${folder}/telemetry.py`, `METRIC_PREFIX = "mawasilati.${domain}"\n\ndef metric(name: str) -> str:\n    return f"{METRIC_PREFIX}.{name}"\n\ndef tags(status: str, correlation_id: str | None) -> dict[str, str]:\n    return {"status": status, "correlation_id": correlation_id or "unassigned"}\n`);
  await emit(`backend/tests/domain/test_${domain}_domain.py`, `from app.domain.${domain}.contracts import ${entity}Snapshot\nfrom app.domain.${domain}.policies import requires_confirmation\nfrom app.domain.${domain}.service import display_label, is_terminal\n\ndef test_${domain}_contract_and_policy():\n    snapshot = ${entity}Snapshot(identifier="${domain}-001", status="OPEN", correlation_id="req-${domain}")\n    assert display_label(snapshot) == "${domain}-001 · OPEN"\n    assert is_terminal("COMPLETED")\n    assert requires_confirmation("PAYMENT_CAPTURE")\n    assert not requires_confirmation("READ")\n`);
  for (const document of ["operating-model", "privacy-and-consent", "acceptance-criteria"]) {
    await emit(`docs/domains/${domain}/${document}.md`, `# ${entity}: ${document.replaceAll("-", " ")}\n\n## Responsibility\n\nThe ${entity} bounded context owns ${purpose}. Its events are correlation-aware, its commands carry an accountable actor, and external side effects require policy approval.\n\n## Safety rule\n\nLocation, payment, driver assignment, and passenger data are not shared or mutated merely because an interface requests it. The policy and ownership checks must pass first.\n\n## Acceptance signal\n\nA feature is accepted only when its domain test, API contract, and operating evidence agree.\n`);
  }
}

for (const feature of features) {
  const className = feature.split("-").map(word => word[0].toUpperCase() + word.slice(1)).join("");
  const folder = `frontend/lib/features/${feature}/enterprise`;
  await emit(`${folder}/${feature}_model.dart`, `class ${className}Model {\n  const ${className}Model({required this.id, required this.status, this.correlationId});\n  final String id;\n  final String status;\n  final String? correlationId;\n}\n`);
  await emit(`${folder}/${feature}_state.dart`, `class ${className}State {\n  const ${className}State({this.loading = false, this.error, this.items = const []});\n  final bool loading;\n  final String? error;\n  final List<Object> items;\n}\n`);
  await emit(`${folder}/${feature}_repository.dart`, `abstract interface class ${className}Repository {\n  Future<List<Object>> load({String? cursor});\n}\n`);
  await emit(`${folder}/${feature}_controller.dart`, `import '${feature}_state.dart';\n\nclass ${className}Controller {\n  ${className}State state = const ${className}State();\n  void beginLoad() => state = const ${className}State(loading: true);\n  void fail(String message) => state = ${className}State(error: message);\n}\n`);
  await emit(`${folder}/${feature}_policy.dart`, `bool canConfirm${className}(String action, {required bool approved}) {\n  const protected = {'payment_capture', 'driver_assignment', 'emergency_escalation'};\n  return !protected.contains(action) || approved;\n}\n`);
  await emit(`${folder}/${feature}_accessibility.dart`, `const ${feature.replaceAll("-", "_")}Labels = {\n  'loading': 'جارٍ تحميل ${feature}',\n  'empty': 'لا توجد بيانات ${feature}',\n  'retry': 'إعادة المحاولة',\n};\n`);
  await emit(`${folder}/README.md`, `# ${feature}\n\nThis module separates UI state, repository boundaries, policy checks, accessibility text, and model contracts so passenger and operator screens remain auditable as the feature grows.\n`);
}

for (const file of [
  "infrastructure/kubernetes/base/namespace.yaml", "infrastructure/kubernetes/base/api-deployment.yaml", "infrastructure/kubernetes/base/frontend-deployment.yaml", "infrastructure/kubernetes/base/api-service.yaml", "infrastructure/kubernetes/base/network-policy.yaml", "infrastructure/kubernetes/overlays/staging/kustomization.yaml", "infrastructure/kubernetes/overlays/production/kustomization.yaml", "infrastructure/observability/slo.md", "infrastructure/observability/alerts.md", "infrastructure/security/secret-rotation.md", "docs/dispatch-runbook.md", "docs/privacy-impact-assessment.md", "docs/payment-boundary.md", "docs/scaling-websocket-rooms.md"
]) {
  const title = path.basename(file).replaceAll("-", " ");
  await emit(file, file.endsWith(".yaml") ? `apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: mawasilati-${title.replace(".yaml", "").replaceAll(" ", "-")}\n  labels:\n    app.kubernetes.io/name: mawasilati\ndata:\n  managed-by: enterprise-expansion\n` : `# ${title}\n\nThis artifact defines an operational review boundary for Mawasilati. It is a safe template: production credentials, payment enablement, dispatch authority, and passenger data access require a separately approved deployment change.\n`);
}

console.log(`Generated ${domains.length} transport domains and ${features.length} Flutter feature modules.`);
