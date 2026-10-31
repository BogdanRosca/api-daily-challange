# API daily challenge

A pytest API suite laid out like tem's automation repo, running against an in-process stand-in for the Control Room
QA environment. Every day it gets a new problem: a failing test, a test that's green for the wrong reason, a helper
that breaks under load. Fix it at the root, commit, and the suite grows from there.

## Setup

```
make install     # python3.14 -m venv .venv && pip install -r requirements.txt
make test        # pytest -q
make check       # ruff, ruff format --check, pyright
```

## Today's challenge

See the top entry in [CHALLENGES.md](CHALLENGES.md). The rules are the interview's: no reruns, no sleeps, no blanket
xfail, don't edit the fake, and follow [AGENTS.md](AGENTS.md).

## Layout

| Path | Role | Edit? |
|---|---|---|
| `tests/api/` | the tests, one file per domain | yes |
| `tests/conftest.py` | root fixtures: credentials, auth, API client, test-data allocation | yes |
| `helpers/` | domain helpers: API calls that check status, polling, building upload files | yes |
| `resources/factories/`, `resources/models/` | payload builders and models | yes |
| `resources/enums/`, `resources/constants/` | shared values (`timeouts.py` for every wait) | yes |
| `resources/utils/`, `resources/data/` | ConfigManager, DataManager and the site pool (`site_data.json`, `fixed_sites.json`) | yes |
| `resources/config/config_qa.ini` | credentials, never in code | yes |
| `resources/openapi/control_room_admin.json` | the contract, as deployed on QA | read |
| `resources/dependencies/control_room_fake.py` | the environment, standing in for the generated API client. Its docstring lists the behaviours tests have to live with. | **no** |
| `scripts/api.py` | call the environment directly | — |

## Calling the API directly

```
python scripts/api.py GET /sites/1300123456718
python scripts/api.py POST /sites/1300123456718/contacts '{"name": "Ada", "email": "ada@example.com", "role": "PRIMARY"}' \
    --then GET /sites/1300123456718/contacts
python scripts/api.py PATCH /sites/1300123456718 '{"tags": ["cold-store"]}' --if-match 1001
python scripts/api.py GET '/consumption?from_date=2026-11-01&to_date=2026-12-01'
```

Each run starts from a clean environment (like each pytest run); chain calls with `--then`. Headers: `--if-match`,
`--idempotency-key`.

## The API (one environment, every domain from the tem challenges)

| Domain | Endpoints | What bites |
|---|---|---|
| auth | `POST /auth/login` | a token is good for 25 requests |
| settings | `GET/PATCH /settings` | environment-wide: change, then put it back |
| sites | `GET /sites`, `GET/PATCH /sites/{mpan}`, `POST …/deactivation`, `POST/GET …/areas` | If-Match versions (412/428), opaque version numbers, case-insensitive sort |
| tenders | `POST /sites/{mpan}/tenders`, `GET /tenders/{id}` | async pricing; Hull Test Rig never prices; inactive site → 409 |
| hedges | `POST /hedges` (CSV), `GET /hedges/{id}` | 46/48/50 settlement periods (Europe/London clock changes) |
| invoices | `POST/GET /sites/{mpan}/invoices` | first POST per site → 503 but stored; Idempotency-Key; ROUND_HALF_UP; SELL is negative |
| forecasts | `POST /sites/{mpan}/forecast-uploads`, `GET /forecast-uploads/{id}`, `GET …/forecast` | async QUEUED → PROCESSING → PROCESSED/FAILED; Hull → 423 |
| contracts | `POST/GET /sites/{mpan}/contracts` | UK dates from offset instants; overlaps → 409; 3 per page, filters on every page |
| contacts | `POST/GET /sites/{mpan}/contacts`, `PUT/PATCH/DELETE /contacts/{id}` | PUT clears what you leave out; unordered list; last PRIMARY can't go |
| consumption | `POST …/daily-reads`, `GET /consumption`, `GET …/consumption-summary` | half-open `[from, to)`; other customers' data without `mpan_core`; decimal strings |
| alerts | `POST …/alert-rules`, `GET/DELETE /alert-rules/{id}`, `POST …/evaluations`, `GET …/alerts` | strictly above threshold; 429 + `retry_after` (6/s env-wide); 2 per page |
| meters | `POST/GET /sites/{mpan}/meters`, `POST/GET /meters/{id}/readings` | 5 per page (last page has items); registers only go up; unique serials |

## Sites on QA

Pool (`site_data.json`, one per test): six BUY (`1300123456718`, `1300123456824`, `1300555012349`, `1300555023457`,
`1300555034565`, `1300555045673`) and three SELL (`1900987654312`, `1900987654429`, `1900987654536`).
Not in the pool on purpose: Leeds Depot `1300777000119` (fixed, shared), Hull Test Rig `1300999000222` (manual QA
only), and Drax Battery Store `1900111222333` (another customer, with reads already on QA).
