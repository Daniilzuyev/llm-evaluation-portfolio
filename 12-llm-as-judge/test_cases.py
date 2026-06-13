"""
Test cases for summarization judge.

Each case represents a real customer support ticket and a generated summary
that exhibits a specific failure mode (or, for case 1, no failure).

Expected scores guide what the judge SHOULD output — actual judge output
will be validated against these in tests/test_judge.py.
"""
ORIGINAL_TICKET = """
Subject: Cannot export shift schedule to Excel

Hi support team,

I've been trying to export our weekly shift schedule from the dashboard
for the past 3 days but every time I click "Export to Excel" the page
just freezes. I'm using Chrome on Windows 11. I've tried clearing cache
and using incognito mode but the problem persists. This is blocking our
weekly payroll process — we need this fixed urgently. My company has
50+ employees so doing this manually is not an option.

Account: company_a_workspace
User: john.doe@company-a.com
""".strip()

TEST_CASES = [
    {
        "id": "TC-01-good",
        "category": "good",
        "original_text": ORIGINAL_TICKET,
        "summary": (
            "User reports Export to Excel button freezes the page on "
            "Chrome/Windows 11 after multiple attempts (cache clear, incognito). "
            "Blocks weekly payroll for 50+ employees. Urgent. "
            "Account: company_a_workspace."
        ),
        "expected_score_min": 4,
        "expected_score_max": 5,
        "notes": "Faithful, complete, concise"
    },
    {
        "id": "TC-02-hallucinated",
        "category": "hallucinated",
        "original_text": ORIGINAL_TICKET,
        "summary": "User reports Export to Excel button freezes. Issue happened after update browser till version 143.3",
        "expected_score_min": 1,
        "expected_score_max": 2,
        "notes": "Adds invented browser version v143.3 as cause"
    },
    {
        "id": "TC-03-incomplete",
        "category": "incomplete",
        "original_text": ORIGINAL_TICKET,
        "summary": "User reports Export to Excel button freezes on Chrome/Windows 11.",
        "expected_score_min": 2,
        "expected_score_max": 3,
        "notes": "Omits urgency, payroll impact, scale, troubleshooting steps"
    },
    {
        "id": "TC-04-verbose",
        "category": "verbose",
        "original_text": ORIGINAL_TICKET,
        "summary": "It appears that the user, who is a customer of the platform, is currently experiencing a technical issue wherein the Export to Excel functionality is not working as expected. Specifically, when the user attempts to click the Export to Excel button, the page appears to freeze. It should be noted that this issue has been persisting for the past 3 days. The user is using Chrome browser on Windows 11 operating system.",
        "expected_score_min": 2,
        "expected_score_max": 3,
        "notes": "Faithful and complete but uses filler phrases throughout"
    },
    {
        "id": "TC-05-wrong-facts",
        "category": "wrong-facts",
        "original_text": ORIGINAL_TICKET,
        "summary": "User reports Export to PDF button freezes on Firefox/macOS for the past 1 day. Affects 5 employees. Account: company_b_workspace.",
        "expected_score_min": 1,
        "expected_score_max": 2,
        "notes": "Wrong facts: PDF->Excel, Firefox->Chrome, 5->50+ employees"
    },

]