# AGENTS.md

The repo's coding rules, as in the tem challenges. They apply to everything under `helpers/`, `resources/`,
`scripts/` and `tests/`.

## Code

- Type hints on every function signature.
- No new module-level variables or constants. A value used by one class is a private class attribute. Shared
  values live in a constants module (`resources/constants/`) or an enums module (`resources/enums/`).
- Specific names. Never `item`, `result`, `data`, `entry`, `response` or `error` on their own: say which one.
- Private helpers start with `_`. Keep shared helpers general and name any non-trivial predicate.
- Log with f-strings: no `%s`, no `print`, no ticket IDs in log messages. `logging.info` for readable
  "Checking X" lines, `logging.debug` for raw payloads.
- Inline `#` comments are one line, never stacked.

## Retries and waiting

- tenacity is for eventual consistency and transient failures only. Retry the condition that is eventually true,
  never an error that won't fix itself. A 401 means the token is no longer valid: fix how tokens are made, don't
  retry around it.
- Bound every wait with a timeout from `resources/constants/timeouts.py`. When a wait gives up, the failure must say
  what it was waiting for, not a wrapper exception.
- No `sleep`. Let tenacity do the waiting.

## Test data factories

- Factories (`resources/factories/`) build a fresh payload on every call. Nothing a test does to one payload may
  leak into the next.

## Fixtures

- A fixture that cleans up yields what it made; the cleanup goes after `yield`, in teardown.
- Use the narrowest scope that works. Session scope is for things that never change or run out during a run.
- A fixture that changes an environment-wide setting puts it back in teardown.

## Tests

- Every test asserts something. Tests check product behaviour end to end: no tests that a query parameter
  filters, no write-then-read-back echoes, no assertions a helper has already made.
- An assertion inside a loop proves nothing if the loop can run zero times.
- Test the boundary the contract defines, not only the comfortable middle.
- Class-based tests with domain markers. Register every marker in `pytest.ini`.
- Every test carries `@qase.id(...)` in the real repo (stripped here).
- Keep test-only constants in the test.

## Test data

- "Use data nothing else can touch." Pool sites come from `DataManager` (`resources/data/site_data.json`); a test
  never shares a site with another test. Named, shared sites live in `resources/data/fixed_sites.json`.
- Credentials come from `resources/config/config_<env>.ini` through `ConfigManager` and the `credentials` fixture.
  Never in code.

## Before you push

- `make check`: ruff (line length 150), ruff format, pyright.
- When a fix doesn't hold, say so.
