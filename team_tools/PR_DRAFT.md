## Assigned issue

Team 10 assignment: Identify free and unavailable seats (`list_seats`) — no GitHub issue was created for this team; assigned via the class handout.

## Capability being added

Team 10: `list_seats` — a read-only tool in `team_tools/list_seats.py` that reads the seat map and reports each seat's real status (available, unavailable, or selected). It never chooses a seat.

## Model action format

Example JSON proposal and what arguments are allowed:

```json
{"action": "list_seats", "argument": {}}
```

The only allowed argument is an empty dictionary `{}`. The tool takes no inputs.

## How Python validates it

`validate()` rejects any proposal before a browser action runs if the argument is not a dictionary or is not empty (e.g. `{"seat": "1A"}` is refused). `run()` re-checks the same rule, and also returns a not-ready result (`ok: false`) if the seat-selection stage (`#seatStage`) is not visible, instead of inventing seats.

## What the browser actually returned

The tool reads `#seatMap button.seat`, using each button's `data-seat` attribute and `disabled` property. On the demo site's seat map it returned all 30 seats, with 1A available and 1B unavailable, matching the page. An independent check in `team_tests/test_list_seats.py` re-read the seat count and the `disabled` property for 1A and 1B straight from the page and confirmed the tool's answers; the full trace is in `team_tests/test_results.txt`.

## How to run the tests

From the repository folder:

```
pip install -r requirements.txt
python -m playwright install chromium
python3 team_tests/test_list_seats.py
```

The test opens Agent Airways in a Playwright browser and runs the invalid-argument and not-ready tests on the opening page. When it pauses, use that same Playwright window to search for a flight (e.g. DCA → BOS, any date), click **Choose AA101**, then press Enter to run the success test and the independent browser check. `python3 tests.py` runs the 9 existing offline checks.

## Tests and evidence

- [x] Ran `python tests.py` — all 9 offline checks passed
- [x] Demonstrated a normal case — seat map visible: 30 seats read, 1A available, 1B unavailable
- [x] Demonstrated an error or edge case — ran before reaching the seat map (not-ready result) and with an invalid argument (refused, page untouched)
- [x] Recorded trace evidence — `team_tests/test_results.txt`
- [x] Did not add personal information, credentials, or real payment activity
- [x] Kept the implementation understandable and narrow

## Team participation

- **Julio Sepulveda (@jcesar1989):** Forked the class repository and created the `Branch_Julio` working branch. Manually explored the Agent Airways site in the browser to inspect the seat map's HTML structure (`#seatMap`, `button.seat`, `data-seat`, `disabled`). Wrote the initial `list_seats.py` — `validate()`, the not-ready check, and the seat-reading loop — and ran the manual browser tests.
- **Manna Zachariah (@mannameriahzachariah):** Created her own `Branch_Manna` branch and made the review fixes requested by the TA: restored `practice_dropdown.py` to the original class version, converted the tool to the shared `ok/message/data` return format, and made `run()` refuse invalid arguments before touching the browser. Added the invalid-argument test and the independent browser check (seat count, 1A and 1B read directly from the page), moved the tests into `team_tests/test_list_seats.py` as requested in review, re-ran all tests and `tests.py`, and updated the recorded results.

## Known limitations

The tool only reads the seat map; it cannot select a seat (by design). It assumes the demo site's structure (`#seatStage`, `#seatMap button.seat`, `data-seat`) and would need updating if the site changed. It reports a seat as "selected" only via the `selected` CSS class, and it has no retry logic if the page is mid-transition.
