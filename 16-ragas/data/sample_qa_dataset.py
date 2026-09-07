qa_dataset = [{
        "case_id": "baseline",
        "user_input": "Why my absence timesheet wasn't created successfully in date 26.06.2026?",
        "retrieved_contexts": ["If the timesheet was closed for that date, absences can still be added, but they’ll be created only on open days, so closed days won’t reflect the absence. Also, ensure you can save the absence (e.g., comment required may block saving) and that the contract type/department are authorized for that absence type.",
                          "According to HR Policy employee should provide detailed description absence during working period"],
        "response": "You are not able to create absence timesheet because you need provide detailed info about your missing",
        "reference": "Unfortunately, the absence timesheet wasn't created because a detailed description of the absence was missing"
    },
    {
        "case_id": "hallucination",
        "user_input": "I can't create new employee, how to fix it?",
        "retrieved_contexts": ["User with standard tariff plan is not able to create more than 5 employees"],
        "response": "You are not able to create new employee after 29.06.2027",
        "reference": "You are not able to create new employee because you have created 5 employees, this is your limit according to your tariff plan"
    },
    {
        "case_id": "bad_retrieval",
        "user_input": "I requested 2 hours today for absence, as a result it wasn't applied in app, how to fix it?",
        "retrieved_contexts": ["According to our policy you have only 15 vacations, 2 days requested by you exceeds your vacation limit"],
        "response": "I don't know",
        "reference": "According our policy employee can take absence per day no more than 1 hour"
    },
    {
        "case_id": "off_topic_generation",
        "user_input": "Incorrectly generated automatic shifts for employee on a week",
        "retrieved_contexts": ["Generation of automatic shifts depends on selected employee and role of it"],
        "response": "Automatic shift generation works based on user and role. Make sure you've selected correct user.",
        "reference": "After correctly selected employee you should be able to generate automatic shifts"
    },
    {
        "case_id": "fully_broken",
        "user_input": "I'm not able to generate financial report for last month",
        "retrieved_contexts": ["For creation new schedule you need to click on button Create Schedule - fill date and add schedule time"],
        "response": "Generation report is possible only for last three days",
        "reference": "You are not able to generate report for last month because you don't have any data for this period"
    }
]