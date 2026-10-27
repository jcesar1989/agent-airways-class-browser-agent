# Agent Airways Part 2, Team Report

**Team label:** Team 10 (Section 06)

**Members and contributions:**

- **Julio Sepulveda (@jcesar1989):** Set up the Part 2 runner, ran Case 1 and Case 2, committed their traces and screenshots (fork PR #5), and wrote the team's Part 2 work plan. In Part 1, Julio created the fork and wrote the original `list_seats` tool.
- **Manna Zachariah (@mannameriahzachariah):** Designed and ran Case 3, wrote this report and cross-checked it against the traces. In Part 1, Manna made the TA's review fixes, including the shared `ok/message/data` format that this runner requires.

**How we checked the final submission:** Every quote below was compared with the matching JSON file in `evidence/`, and each screenshot was checked to show the stage named in its trace.

**Assigned tool:** `team_tools/list_seats.py`. It is read-only: it reports each seat as available, unavailable or selected, never clicks a seat, and only accepts the argument `{}`.

**Exact code version:** fork `jcesar1989/agent-airways-class-browser-agent`, branch `main`, commit `c34eeaf` (`c34eeaf7ab9cefebe66c2a07f25e551d1adb8106`). `list_seats.py` was last changed in `b934c94`, the same version merged into the class repository in Part 1. The tool file is also included in the ZIP.

## Case 1: Normal request

**Customer request:** "List the seats available for the selected flight." (runner default for `--case success`)

**Starting browser stage (test setup, not an AI decision):** `seat`. The runner chose DCA → BOS and flight AA101 with plain Playwright before the model started.

**Model-proposed tool call (quote from JSON trace):** Step 1: `{"action":"list_seats","argument":{}}`

**Actual tool observation (quote the important fields):** `"ok": true, "message": "Read 30 seats."`. Seats 1B, 2C, 3A, 4F and 5D are `"unavailable"`; the other 25 are `"available"`.

**Model's next response:** Step 2: `{"action":"done","argument":{"status":"success","reason":"Listed available seats for the selected flight."}}`, with `stop_reason: "success"`.

**Did the browser evidence support this response? Why?** Yes. The model chose `list_seats` itself: the runner's system prompt only lists the available actions, and the call comes from `model_reply` in the trace, not from hardcoded code. The tool returned real seat data with `ok: true`, `last_team_tool_ok` is `true`, and the final page is the seat map (`stage: "seat"`). However, the model's final reason is vague and names no seats. Case 3 tests this directly.

## Case 2: Problem request

**Customer request:** "Attempt to list seats before a flight was chosen. Report the not-ready result." (runner default for `--case failure`)

**What went wrong or was refused?** The browser stayed on the `search` stage, so there was no seat map to read.

**Tool response, or model refusal and your direct tool test:** The model proposed `{"action":"list_seats","argument":{}}`. The tool returned `{"ok": false, "message": "The seat selection stage is not visible.", "data": {}}`, with no invented seats.

**Model's next response:** `{"action":"done","argument":{"status":"not-ready","reason":"Seat selection is not available yet."}}`. `"not-ready"` is not an allowed status, so the runner recorded `stop_reason: "unable"`.

**Did it avoid an unsupported claim of success?** Yes. The model listed no seats and its reason matches the tool's observation. `last_team_tool_ok` is `false`, and the final page is still `stage: "search"`.

## Case 3: Team-designed request

**What changed from Case 1?** The same seat-map setup, but a specific question that the raw tool output does not answer directly. The model has to find 1B's status and filter row 1 from the 30-seat list, so it must use the observation's data, not just report that a call happened.

**Customer request and starting stage:** "Is seat 1B available? If not, tell me which seats in row 1 are free." Starting stage: `seat`. Run with `--label third`.

**Model proposal, tool observation, and next model response:**
- Step 1 proposal: `{"action":"list_seats","argument":{}}`
- Observation: `"ok": true, "message": "Read 30 seats."`. Row 1: 1A available, 1B unavailable, 1C, 1D, 1E and 1F available.
- Step 2 response: `{"action":"done","argument":{"status":"success","reason":"Seat 1B is unavailable. The available seats in row 1 are 1A, 1C, 1D, 1E, and 1F."}}`
- Trace: `stop_reason: "success"`, `used_team_tool: true`, `last_team_tool_ok: true`, final page `stage: "seat"`.

**What does this case demonstrate?** The model's answer is fully supported by the observation: 1B is unavailable, and the five seats it named are exactly the available row-1 seats, with none missing or invented. Unlike Case 1's generic summary, the specific question made the model state concrete facts from the tool's data, which shows the observation drives its next response.

## Reproduction

**Commands run** (repository root; Ollama running with `qwen3:8b`; use `python` instead of `python3` on Windows):

```
python3 agent_one_team_tool.py --tool list_seats --case success
python3 agent_one_team_tool.py --tool list_seats --case failure
python3 agent_one_team_tool.py --tool list_seats --case success --label third --request "Is seat 1B available? If not, tell me which seats in row 1 are free."
```

`agent_one_team_tool.py` was used unchanged from the instructor's starter.

**Files submitted:** `team_tools/list_seats.py`; `evidence/list_seats_success_agent.json` and `_final.png` (Case 1); `evidence/list_seats_failure_agent.json` and `_final.png` (Case 2); `evidence/list_seats_third_agent.json` and `_final.png` (Case 3); `REPORT.md`.

**Any failures encountered and what the team changed:** All three runs completed on the first attempt, and no code was changed for Part 2. Only the runner's fake passenger details were used.
