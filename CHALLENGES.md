# Challenges

Newest first. Each one starts from the commit before it; fix it, commit, then ask for the next.

## 4. A week that adds up to 2,605 kWh (consumption)

`pytest -q` has one failing test: `test_api_a_sites_weekly_consumption_adds_up_the_days_in_the_week_only`.

Find out why and fix it at the root. Read the fake's docstring (Consumption) and the failing request's log before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed and where the bug lives (test, helper or factory).

## 3. Seven meters, one serial number (meters)

`pytest -q` has one failing test: `test_api_a_sites_meters_are_listed_in_registration_order_across_pages`.

Find out why and fix it at the root. Read the fake's docstring (Meters) and the failing request's log before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed and where the bug lives (test, helper or factory).

## 2. A week of alerts that stops half-way (alerts)

`pytest -q` has one failing test: `test_api_a_week_of_consumption_alerts_only_on_days_above_the_threshold`.

Find out why and fix it at the root. Read the fake's docstring (Alerts) before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed and why your wait is safe to retry.

## 1. A contact update that loses details (contacts)

`pytest -q` has one failing test: `test_api_changing_a_contacts_email_keeps_their_other_details`.

Find out why and fix it at the root. Read the fake's docstring and the contract before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed.
