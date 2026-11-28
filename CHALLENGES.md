# Challenges

Newest first. Each one starts from the commit before it; fix it, commit, then ask for the next.

## 29. A renewal that waits for a refusal to change its mind (contracts)

`pytest -q` has one failing test: `test_api_a_contract_renewed_twice_runs_on_without_a_gap_or_an_overlap[SELL]`. A six-month contract is
renewed twice with the new `renew_contract` helper. The first renewal goes through. The second takes about five seconds to fail with
`409 overlaps contract_...`, though the helper already retries a 409. The other contract tests pass. The test has a site of its own:
Holderness Solar Farm (`1900987655178`, now on QA) has joined the pool.

Find out why and fix it at the root. Read the fake's docstring (Supply contracts), AGENTS.md (Retries and waiting), the docstring of
`_send_renewal`, and the `Renewing ...` and `POST .../contracts` log lines (which days did each renewal ask for, which contract does the
409 name, and did anything change between attempts?) before you change anything. Then ask yourself: why did the first renewal work?
Done when: the suite is green, `make check` is clean, the test still renews the same contract twice for six months and expects the same
hand-written UK dates, `renew_contract` starts the renewal on the UK day after the expiring contract's last day whatever its `end_at`
offset (an expiring contract that ends in winter, in summer, on either clock-change day, on 31 December and on 29 February 2028), a
renewal that really does overlap (a contract already starts on the renewal's first day: try it in a scratch run) fails at once with the
409 and the contract it overlaps (no wait, no `RetryError`), nothing retries an error that won't fix itself and no constant is left in
`timeouts.py` that nothing uses, and you can say in one sentence why only the second renewal was refused and where the bug lives (test,
helper, constant or factory).

## 28. A fortnight of alerts that runs out of breath (alerts)

`pytest -q` has one failing test: `test_api_a_fortnight_of_consumption_alerts_each_rule_only_on_days_above_its_own_threshold`. A site
with an EMAIL rule above 100 kWh and an SMS rule above 150 kWh is sent fourteen days of consumption, and an evaluation part-way through
fails with `401 token expired after 25 requests; log in again`. The two alert tests before it pass, and they hit the rate limit too.
The test has a site of its own: Normanton Ropeworks (`1300555145059`, now on QA) has joined the pool.

Find out why and fix it at the root. Read the fake's docstring (Everywhere, Alerts), AGENTS.md (Retries and waiting) and the
`POST .../evaluations` log lines of the failing test (how many requests did fourteen evaluations take, what did each 429 tell you, and how
long did the helper wait before sending again?) before you change anything. The 401 tells you the token ran out, not why.
Done when: the suite is green, `make check` is clean, the test sends the same fourteen days to the same two rules and still expects the
same six alerts, no evaluation is sent again before the time its 429 asked for has passed (count the 429 lines and read their
`retry after`), the wait comes from what the server said and not from a number you picked to be long enough, a rate limit that never
clears still fails within `EVALUATE_CONSUMPTION_TIMEOUT` and says which day was still rate limited (not a `RetryError`), nothing retries a
401, logs in again or hands out a second token, and you can say in one sentence why the token ran out and where the bug lives (test,
helper, fixture, constant or factory).

## 27. A bill for part of a fortnight (invoices)

`pytest -q` has one failing test: `test_api_a_month_is_billed_for_every_kwh_read_in_it`. The site sends fourteen daily reads, bills the
month they start in at the summary's total, and the invoice comes back short (on 26 November: 4874p where the test expected 17134p). The other invoice and
consumption tests pass, and nothing in billing or the summary is wrong. The test has a site of its own: Knottingley Glassworks
(`1300555134051`, now on QA) has joined the pool.

Find out why and fix it at the root. Read the fake's docstring (Consumption, Invoices), the new `DailyReadFactory`
(`resources/factories/daily_read.py`) and the `POST .../daily-reads` and `consumption-summary` log lines (how many reads went in, how many
kWh did the summary count, and which days were the reads for?) before you change anything. Then ask yourself: would this test have failed
on 2 November? Will it on 3 December?
Done when: the suite is green, `make check` is clean, the test sends the same reads, bills the same month and expects the same amount on
whatever day it runs (1 January, 29 February 2028, 30 November and 31 December included), nothing under `helpers/`, `resources/factories/`
or `tests/` reads the wall clock (`date.today()`, `datetime.now()`), a read on the day before and the day after the billed month (the
boundary) is in the run and is not billed, the expected amount still comes from the reads the test sent and the rate, not from the summary
or the invoice under test, every `DailyReadFactory.build` call still gives a fresh dict, and you can say in one sentence why the bill came up
short today and where the bug lives (test, helper, fixture or factory).

## 26. A busiest day that came second (consumption)

`pytest -q` has one failing test: `test_api_a_sites_monthly_summary_names_its_busiest_day_the_earliest_on_a_tie`. Two days in November
share the month's highest reading, and the test says the summary named the wrong one. The other consumption tests pass, and
`total_kwh` and `peak_kwh` are right. To make room for it, Castleford Dairy (`1300555123043`, already on QA) has joined the pool.

Find out who is right before you change anything: read the fake's docstring (Consumption) and the contract
(`resources/openapi/control_room_admin.json`, the consumption summary), then look at the order of the reads the test sends (put a
breakpoint before `submit_daily_reads`: which day comes first in `month_kwh`, and is that the earliest one?).
Done when: the suite is green, `make check` is clean, your expected busiest day is right whatever order the reads were built or sent in
(try the reads reversed and shuffled), for a tie of two or three days, for a tie between two weekdays and between a weekend day and a
weekday, and for a month with one clear peak, the expected value still comes from the contract and not from the summary under test,
the comparison of kWh is by value (`"95.000"` and `"95.0"` are the same reading), and you can say in one sentence why the test expected the
19th and where the bug lives (test, helper or factory).

## 25. A tender that never gets a second look (tenders)

`pytest -q` has one failing test: `test_api_a_sell_site_tender_is_priced_at_the_sell_rate[SELL]`. It fails in about a second with
`401 token expired after 25 requests; log in again`. The four other tender tests pass, and they wait for pricing too.
Start from a green suite: this branch includes your Challenge 24 fix from PR #31, so merge #31 first.

Find out why and fix it at the root. Read the fake's docstring (Everywhere, Tenders), AGENTS.md (Retries and waiting) and the failing
test's log (how many tenders did it ask for, and how many times was each one read?) before you change anything. The 401 tells you the token
ran out, not why.
Done when: the suite is green, `make check` is clean, each `get_priced_tender` call asks for exactly one tender and returns that tender
once it is priced, the SELL site is priced at the SELL rate, a tender that never prices (try Hull Test Rig in a scratch run; don't commit
it) fails within `TENDER_PRICING_TIMEOUT` with a message that names the tender and says it was still waiting for a price (not a 401, not a
`RetryError`), nothing retries a 401 or logs in again inside a helper, there is one pricing wait in `helpers/`, not two, and you can say
in one sentence why the token ran out and where the bug lives (test, helper, fixture or factory).

## 24. A credit note that went to the wrong site (invoices)

`pytest -q` has one failing test: `test_api_every_billed_month_is_charged_in_whole_pence[SELL]`. The solar farm's invoice list comes back
empty though every `bill_month` call answered 201. The `[BUY]` case passes, and so does `[SELL]` run on its own
(`pytest -k "whole_pence and SELL"`). Both cases bill the same three months.

Find out why and fix it at the root. Read the fake's docstring (Invoices) and the `POST .../invoices` log lines of both cases (which key did
each send, which invoice id came back, and whose site is that invoice on?) before you change anything.
Done when: the suite is green, `make check` is clean, the two cases pass in either order (`pytest -k whole_pence`, then with the parametrize
list reversed) and on their own, a 503 is still retried with the same key and leaves exactly one invoice for the month, two sites billed
the identical month each get their own invoice, a second run against a QA environment that keeps its data (the real one does) would not
get this run's invoices back, a month billed twice on purpose is billed twice, and you can say in one sentence why only SELL failed and
where the bug lives (test, helper or factory).

## 23. A site that was switched off before it was handed out (tenders)

`pytest -q` has one failing test: `test_api_a_buy_site_tender_starts_pending_and_is_priced_at_the_buy_rate`. Its tender is refused with a
409: the fresh pool site it claimed is inactive. Run on its own (`pytest -k starts_pending`) it passes. The new test before it,
`test_api_a_tender_for_a_deactivated_site_is_refused`, passes.

Find out why and fix it at the root. Read the fake's docstring (Sites, Tenders), AGENTS.md (Test data) and the `Claimed pool site` and
`Released pool site` lines in the log (which sites did the tender tests claim, and has any of them been claimed before?) before you change
anything.
Done when: the suite is green, `make check` is clean, the deactivation test still proves a switched-off site is refused, no pool site is
handed to two tests in one run (whatever the tests do to it, and in any test order), the suite does not run out of sites (`DataLocked`),
nothing is left in the code that could hand a site out twice, and you can say in one sentence why only the test after the deactivation
failed and where the bug lives (test, helper, fixture or data).

## 22. A tag from the site before (sites)

`pytest -q` has one failing test: `test_api_an_onboarded_site_carries_the_standard_tags_and_only_its_own[SELL]`. The solar farm comes back
tagged `cold-store` as well. The `[BUY]` case passes, and so does `[SELL]` run on its own (`pytest -k "onboarded and SELL"`).
This branch is built on `main`, not on Challenge 21 (PR #27, still open), so the suite has only today's failure.

Find out why and fix it at the root. Read the fake's docstring (Sites) and AGENTS.md (Test data factories), then look at the tags each
case's `PATCH` sends (the log names the fields, not their values: put a breakpoint in `update_site`) before you change anything.
Done when: the suite is green, `make check` is clean, the two cases pass in either order (`pytest -k onboarded`, then with the
parametrize list reversed), no payload a test changes after it is built (its tags, its email or anything else in it) shows up in the next
one or in the factory's defaults, a site tag that is already a standard tag is not added twice, `build_onboarding()` with no tags of its
own still gives exactly the standard tags, and you can say in one sentence why only the second case failed and where the bug lives (test,
helper or factory).

## 21. Six kilowatt-hours that nobody traded (hedges)

`pytest -q` has one failing test: `test_api_a_hedge_for_a_days_trade_covers_exactly_the_traded_volume[spring_clock_change]`. The day's
12.000 MWh trade comes back hedged as 12.006 MWh. The `[ordinary_day]` and `[autumn_clock_change]` cases pass with the same trade.
Start from a green suite: this branch includes PR #26 (Challenge 20) plus a commit that makes `make check` clean, so merge #26 first.

Find out why and fix it at the root. Read the fake's docstring (Hedges) and look at the CSV the test uploads (what volume is on each row,
and what do 46 of them add up to?) before you change anything.
Done when: the suite is green, `make check` is clean, your hedge adds up to exactly the traded volume for any volume to the kWh (try
10.000, 0.045 and 0.000 on each of the three days) on a day of 46, 48 or 50 periods, no two periods differ by more than 1 kWh, no period
is negative, the test still compares against the traded volume the API reports back (no `approx`, no tolerance), and you can say in one
sentence why only the spring day was off and where the bug lives (test, helper or factory).

## 20. A tag that never catches up (sites)

`pytest -q` has one failing test: `test_api_two_people_tagging_a_site_at_once_keep_both_tags[BUY]`. It takes about two seconds to fail
with a 412, though the helper it calls already retries a 412. The Leeds Depot rename-then-tag test passes.

Find out why and fix it at the root. Read the fake's docstring (Sites) and the failing test's log (what version did each `PATCH` send,
what was current, and did anything change between attempts?) before you change anything. Compare the retry with the one in `bill_month`:
the same shape is right there and wrong here.
Done when: the suite is green, `make check` is clean, `add_site_tag` works from a site read any time before (another writer may have
changed it since), neither person's tag is lost, a tag the site already has is not added twice, a 412 that never clears fails with a
message that says what it was waiting for, a 428 is not retried, and you can say in one sentence why every retry failed the same way and
where the bug lives (test, helper or factory).

## 19. A meter that ran backwards (meters)

`pytest -q` has one failing test: `test_api_a_meters_usage_for_a_month_is_its_latest_register_minus_its_first`. November's usage
comes back as -15.625 kWh where 118.500 was expected. The two meter tests next to it pass.

Find out why and fix it at the root. Read the fake's docstring (Meters) and the failing test's log (the `Meter ... went from ... to ...`
line: which readings did the helper take as the first and the latest, and on which dates?) before you change anything.
Done when: the suite is green, `make check` is clean, your fix holds for any registers (crossing 10, 1,000 or 100,000 kWh, or staying
level), a meter with one reading has used 0 kWh, a meter with no readings fails loudly and says so instead of an `IndexError`, and you
can say in one sentence why November came out negative and where the bug lives (test, helper or factory).

## 18. A revision that never lands (forecasts)

`pytest -q` has one failing test: `test_api_a_revised_forecast_replaces_only_the_days_it_contains`. The 17th is right; the revised 18th still
shows the first upload's total. The two-day forecast test next to it passes.

Find out why and fix it at the root. Read the fake's docstring (Forecast uploads) and the log of the failing test (after the second
`POST .../forecast-uploads`, which requests did the wait send, and how many before it returned?) before you change anything.
Done when: the suite is green, `make check` is clean, your fix holds for a revision of any days (new ones, ones already there, or both), a
revision that FAILS fails at once with the server's row errors instead of passing or timing out, and you can say in one sentence why the
wait returned the old forecast and where the bug lives (test, helper or factory).

## 17. A month that ends a day early (consumption)

`pytest -q` has two failing cases of one test: `test_api_a_sites_daily_consumption_for_a_month_matches_its_monthly_summary[November]`
and `[December]`. The monthly summary they compare against is right; the weekly test next to them passes.

Find out why and fix it at the root. Read the fake's docstring (Consumption) and the `GET /consumption` log line (which dates did it ask
for, and how many daily totals came back?) before you change anything.
Done when: the suite is green, `make check` is clean, your fix holds for any month of any year (December, and February in a leap year,
included) without a hand-written calendar rule, and you can say in one sentence why every month came back short and where the bug lives
(test, helper or factory).

## 16. A handover that keeps the wrong PRIMARY (contacts)

`pytest -q` has one failing test: `test_api_each_primary_contact_handover_leaves_only_the_new_primary`. Not on every run: run the suite five
times and it will pass now and then. A green run doesn't mean it's fixed.

Find out why and fix it at the root. Read the fake's docstring (Site contacts) and the log of a failing run (which contact did each
`DELETE /contacts/...` remove, and which one had just been added?) before you change anything.
Done when: the suite is green on every run (try 20 in a row), `make check` is clean, your fix holds whatever order the list comes back in,
a handover on a site with no PRIMARY to replace, or more than one, fails loudly and says so, and you can say in one sentence why it
passed on some runs and where the bug lives (test, helper or fixture).

## 15. A credit that is a penny short (invoices)

`pytest -q` has one failing test: `test_api_every_billed_month_is_charged_in_whole_pence[SELL]`. The `[BUY]` case next to it passes, with the same three months.

Find out why and fix it at the root. Read the fake's docstring (Invoices) and the `POST .../invoices` log line for 2026-10 (what did billing charge, and what did the test expect?) before you change anything.
Done when: the suite is green, `make check` is clean, your expected amount is right for any consumption and rate on either site type (not only 0.5 kWh at 5p), and you can say in one sentence why only SELL failed and where the bug lives (test, helper or factory).

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
