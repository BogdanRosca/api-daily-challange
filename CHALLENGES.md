# Challenges

Newest first. Each one starts from the commit before it; fix it, commit, then ask for the next.

## 14. FIXED contracts that turn FLEX on page two (contracts)

`pytest -q` has one failing test: `test_api_a_sites_fixed_contracts_are_listed_oldest_first_across_pages`.

Find out why and fix it at the root. Read the fake's docstring (Supply contracts) and the three `GET .../contracts` log lines (which contracts came back on each page, and why is April there twice?) before you change anything.
Done when: the suite is green, `make check` is clean, your fix holds for any filter and any number of pages, and you can say in one sentence why it failed and where the bug lives (test, helper or factory).

## 13. A clean-up that fails after the test passed (alerts)

`pytest -q` reports `18 passed, 1 error`: `test_api_a_deleted_alert_rule_stops_alerting` passes, then errors in teardown.
Start from a green suite: this branch includes the Challenge 12 fix from PR #16, so merge #16 first.

Find out why and fix it at the root. Read the fake's docstring (Alerts) and the teardown's log (what did it ask for, and what was already true?) before you change anything.
Done when: the suite is green, `make check` is clean, a clean-up that meets any error other than "already gone" still fails loudly, and you can say in one sentence why the run was red when every test passed and where the bug lives (test, helper or fixture).

## 12. March runs into April (contracts)

`pytest -q` has one failing test: `test_api_back_to_back_contracts_either_side_of_the_spring_clock_change_keep_their_uk_dates`.
The November contract tests next to it pass.

Find out why and fix it at the root. Read the fake's docstring (Supply contracts) and the log line for the March contract (which dates did it store?) before you change anything.
Done when: the suite is green, `make check` is clean, your fix holds for a contract on any day of the year (not only March and April), and you can say in one sentence why it failed and where the bug lives (test, helper or factory).

## 11. Areas in the wrong order (sites)

`pytest -q` has one failing test: `test_api_a_sites_areas_are_listed_a_to_z_ignoring_case`.

Find out why and fix it at the root. Read the fake's docstring (Sites) and the failing test's output (which ids are swapped?) before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed and where the bug lives (test, helper or factory).

## 10. A token that runs out half-way through the file (tenders)

`pytest -q` has one failing test: `test_api_a_priced_tender_keeps_its_rate_when_read_again`. Run on its own (`pytest -k read_again`) it passes.

Find out why and fix it at the root. Read the fake's docstring (Everywhere) and the failing request's log before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed only in the full run and where the bug lives (test, helper or fixture).

## 9. A second change that is always out of date (sites)

`pytest -q` has one failing test: `test_api_renaming_a_site_then_tagging_it_keeps_both_changes`.

Find out why and fix it at the root. Read the fake's docstring (Sites) and the failing requests' log before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why the second change failed and where the bug lives (test, helper or fixture).
## 8. The day the clocks change (hedges)

`pytest -q` has one failing test: `test_api_a_hedge_for_each_clock_change_day_covers_every_settlement_period`.

Find out why and fix it at the root. Read the fake's docstring (Hedges) and the failing request's log before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed and where the bug lives (test, helper or factory).

## 7. A contract that should have been refused (contracts)

`pytest -q` has one failing test: `test_api_a_contract_sharing_one_day_with_an_existing_contract_is_rejected`. Run on its own (`pytest -k rejected`) it passes.

Find out why and fix it at the root. Read the fake's docstring (Supply contracts) and the passing test that runs before it before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed only in the full run and where the bug lives (test, helper or fixture).

## 6. A forecast that never arrives (forecasts)

`pytest -q` has one failing test: `test_api_a_processed_two_day_forecast_stores_both_days_with_their_totals`.

Find out why and fix it at the root. Read the fake's docstring (Forecast uploads) and the failing requests' log before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed and where the bug lives (test, helper or factory).

## 5. Two months billed, three invoices (invoices)

`pytest -q` has one failing test: `test_api_two_billed_months_give_two_invoices_with_rounded_amounts`.

Find out why and fix it at the root. Read the fake's docstring (Invoices) and the failing requests' log before you change anything.
Done when: the suite is green, `make check` is clean, and you can say in one sentence why it failed and why your retry is safe to repeat.

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
