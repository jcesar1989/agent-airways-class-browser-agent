"""Team 10 tool: list_seats
Team members: Julio Sepulveda, Manna Zachariah

Read-only tool. Reports which seats on the seat map are available,
unavailable, or selected. It never clicks a seat.
"""


def validate(argument):
    if type(argument) != dict:
        return False, "The argument must be a dictionary."
    
    if len(argument) != 0:
            return False, "The argument must be an empty dictionary."
   
    return True, "Argument is acceptable."


def run(page, argument, context):
    """Read the seat map and return real seat statuses.

    Returns the shared class format: {"ok": bool, "message": str, "data": dict}.
    Two possible shapes:

      Not ready: {"ok": False, "message": "The seat selection stage is not visible.", "data": {}}
      Ready:     {"ok": True, "message": "Read 30 seats.",
                  "data": {"seats": [{"seat": "1A", "status": "available"}, ...]}}

    Each seat's status is "available", "unavailable", or "selected".
    """
    # Part 0 - check the argument before touching the browser.
    # This tool takes no arguments, so anything other than {} is refused.
    # It reuses validate() so the rule lives in one place.
    is_valid, reason = validate(argument)
    if is_valid == False:
        return {"ok": False, "message": "Invalid argument: " + reason, "data": {}}

    # Part 1 - the not-ready check (our required failure behavior):
    if page.locator("#seatStage").is_visible() == False:
        return {"ok": False, "message": "The seat selection stage is not visible.", "data": {}}

    # Part 2 - read the seats:
    buttons = page.locator("#seatMap button.seat")
    seat_list = []

    for index in range(buttons.count()):
        button = buttons.nth(index)
        seat_name = button.get_attribute("data-seat")
        class_text = button.get_attribute("class")
        if class_text is None:
            class_text = ""

        if button.is_disabled():
            status = "unavailable"
        elif "selected" in class_text.split():
            status = "selected"
        else:
            status = "available"

        seat_list.append({"seat": seat_name, "status": status})

    # Part 3 - return the result in the shared format.
    # The message uses the real count, so nothing is hardcoded.
    message = "Read " + str(len(seat_list)) + " seats."
    return {"ok": True, "message": message, "data": {"seats": seat_list}}


def main():
    """Manual test harness. Not part of the tool itself.

    Runs both required tests in one session:
      Failure test: call the tool on the opening page (before any
                    flight is chosen) and expect a not-ready result.
      Success test: a human navigates to the seat map, then the tool
                    should report 1A available and 1B unavailable.
    """
    import sys
    from pathlib import Path

    # Allow "python team_tools/list_seats.py" to find browser_tools.py
    # in the repository root.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    import browser_tools

    browser_tools.start_browser()
    try:
        browser_tools.open_site()

        print("\n--- INVALID ARGUMENT TEST: a wrong argument is refused ---")
        url_before = browser_tools.page.url
        bad_argument = {"seat": "1A"}

        # 1. validate() should say False and explain why.
        is_valid, reason = validate(bad_argument)
        print("validate(" + str(bad_argument) + ") ->", is_valid, "|", reason)

        # 2. run() should refuse too, without touching the browser.
        result = run(browser_tools.page, bad_argument, {})
        print("Result:", result)

        # 3. Independent check: the page is still where it was.
        url_after = browser_tools.page.url
        print("Page URL before:", url_before, "| after:", url_after)

        if is_valid is False and result["ok"] is False and url_before == url_after:
            print("PASS: the bad argument was refused and the page did not change.")
        else:
            print("FAIL: the bad argument should have been refused.")

        print("\n--- FAILURE TEST: before reaching the seat map ---")
        result = run(browser_tools.page, {}, {})
        print("Result:", result)
        if result["ok"] is False:
            print("PASS: tool reported not-ready instead of inventing seats.")
        else:
            print("FAIL: tool should have reported not-ready.")

        print("\nNow use the browser window to search for a flight,")
        print("choose one, and continue until the seat map is visible.")
        input("Press Enter when you can see the seat map...")

        print("\n--- SUCCESS TEST: seat map visible ---")
        result = run(browser_tools.page, {}, {})
        print("Result:", result)

        statuses = {}
        for seat in result["data"].get("seats", []):
            statuses[seat["seat"]] = seat["status"]

        if result["ok"] is True and statuses.get("1A") in ("available", "selected") and statuses.get("1B") == "unavailable":
            print("PASS: 1A is choosable and 1B is unavailable, as on the demo site.")
        else:
            print("FAIL: expected 1A available and 1B unavailable. Check the output above.")

        # --- INDEPENDENT CHECK ---
        # Read the page directly, without using the tool's answer,
        # and compare what the browser shows with what the tool reported.
        print("\n--- INDEPENDENT BROWSER CHECK ---")
        page = browser_tools.page

        # 1. Count the seat buttons on the page and compare with the tool's count.
        page_count = page.locator("#seatMap button.seat").count()
        print("Seat buttons on the page:", page_count, "| Seats reported by tool:", len(statuses))
        if page_count == len(statuses):
            print("PASS: the tool reported every seat on the page.")
        else:
            print("FAIL: the tool's seat count does not match the page.")

        # 2. For 1A and 1B, read the button's disabled property straight from the page.
        for seat_name in ["1A", "1B"]:
            seat_button = page.locator('#seatMap button[data-seat="' + seat_name + '"]')
            page_disabled = seat_button.is_disabled()
            tool_status = statuses.get(seat_name)
            print(seat_name, "- page disabled:", page_disabled, "| tool says:", tool_status)

            # A seat is unavailable exactly when the page has it disabled.
            if page_disabled == (tool_status == "unavailable"):
                print("PASS:", seat_name, "matches the page.")
            else:
                print("FAIL:", seat_name, "does not match the page.")

        input("Press Enter to close the browser...")
    finally:
        browser_tools.close_browser()


if __name__ == "__main__":
    main()
