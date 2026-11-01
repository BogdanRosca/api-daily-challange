# Challenges

Newest first. Each one starts from the commit before it; fix it, commit, then ask for the next.

## 2. A week of alerts that stops half-way (alerts)

`pytest -q` has one failing test: `test_api_a_week_of_consumption_alerts_only_on_days_above_the_threshold`.

Find out why and fix it at the root. Read the fake's docstring (Alerts) before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed and why your wait is safe to retry.

## 1. A contact update that loses details (contacts)

`pytest -q` has one failing test: `test_api_changing_a_contacts_email_keeps_their_other_details`.

Find out why and fix it at the root. Read the fake's docstring and the contract before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed.
