# Mawasilati Security Report

Generated: 2026-08-23T10:35:50Z

| Control | Status | Evidence |
|---|---|---|
| Dependency audit | findings_or_failure | pip-audit.json |
| Python SAST | passed | bandit.json |
| OWASP SAST | passed | semgrep.json |
| Secret scan | passed_heuristic | secret-heuristic.json (fallback) |

Review raw evidence and remediate open dependency findings before a production cutover.
