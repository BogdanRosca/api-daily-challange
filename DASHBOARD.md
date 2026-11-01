# Progress dashboard

https://claude.ai/artifact/4ov8cGvrt49doqbkTBHQjK

Updated by the daily task. Data lives in two uploaded files, referenced by the `challenges` and `lessons` datasets:

- `challenges.json`: one row per challenge (`number`, `issued_on`, `domain`, `title`, `branch`, `status` solved/open/missed, `solved_on`, `pr_number`, `pr_url`).
- `lessons.json`: one row per lesson (`id`, `challenge`, `learned_on`, `category`, `lesson`, `fix`).

Each morning: mark yesterday's challenge solved (merged PR) or missed, add lessons from its PR review, add today's as `open`.
Upload the new file as an asset, then update the dataset's `source.url` and `updated`.
