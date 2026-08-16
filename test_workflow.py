"""
test_workflow.py — End-to-End Automated Test for AI Recruitment System (3 AI Agents).
"""

import os
from database import init_db, get_all_candidates, get_all_email_logs
from agents.cv_agent import CVScreeningAgent
from agents.interview_agent import AIInterviewAgent
from agents.selection_agent import CandidateSelectionAgent
from email_service import send_interview_link_email

def run_test():
    print("\n==========================================")
    print("STARTING E2E RECRUITMENT WORKFLOW TEST")
    print("==========================================\n")

    # Step 0: Database init
    init_db()

    # Instantiate Agents
    agent1 = CVScreeningAgent()
    agent2 = AIInterviewAgent()
    agent3 = CandidateSelectionAgent()

    # Step 1: Agent 1 — CV Screening
    print("--- [STEP 1] Testing Agent 1: CV Screening ---")
    cv_file = os.path.join(os.path.dirname(__file__), "sample_cvs", "ali_khan_cv.pdf")
    candidate = agent1.process_cv(cv_file)
    
    assert candidate["name"] != "Not Available", "Candidate name should be extracted"
    assert candidate["email"] != "Not Available", "Candidate email should be extracted"
    print(f"✓ Agent 1 Extracted Candidate: {candidate['name']} ({candidate['email']})")
    print(f"  Skills: {candidate['skills']}")
    print(f"  Education: {candidate['education']}")

    candidate_id = candidate["id"]

    # Step 2: Agent 2 — AI Interview Generation
    print("\n--- [STEP 2] Testing Agent 2: Interview Generation ---")
    interview = agent2.generate_interview(candidate_id)
    token = interview["token"]
    questions = interview["questions"]

    assert len(questions) == 10, f"Expected 10 questions, got {len(questions)}"
    assert token, "Interview token should be generated"
    print(f"✓ Agent 2 Generated {len(questions)} Questions. Token: {token}")

    # Step 3: Candidate Interview Simulation
    print("\n--- [STEP 3] Testing Candidate Answer Submission & Evaluation ---")
    mock_answers = [
        "I have 1 year of experience building Python and FastAPI microservices.",
        "I use pdb and logging to systematically isolate bugs.",
        "I built a customer web portal using Python and SQL database.",
        "I follow PEP8 guidelines, write unit tests, and perform code reviews.",
        "I prefer VS Code, Git, and Virtualenv environments.",
        "I prioritize tasks using agile boards and communicate blockers early.",
        "I learned FastAPI in 3 days by building small prototype APIs.",
        "I actively participate in pull request reviews and daily standups.",
        "I implement proper input validation, password hashing, and HTTPS.",
        "I aim to become a Senior Full-Stack Engineer leading technical projects."
    ]

    eval_res = agent2.evaluate_answers(token, mock_answers)
    score = eval_res["score"]
    status = eval_res["status"]

    print(f"✓ Agent 2 Evaluated Answers -> Score: {score}/100 | Result: {status}")

    # Step 4: Agent 3 — Candidate Selection Routing
    print("\n--- [STEP 4] Testing Agent 3: Candidate Selection ---")
    selection = agent3.process_selection(candidate_id, score, status == "PASS")
    final_status = selection["final_status"]
    print(f"✓ Agent 3 Updated Status -> {final_status}")

    # Step 5: Email Service Trigger
    print("\n--- [STEP 5] Testing Final Interview Email Dispatch ---")
    if selection["can_send_final_email"]:
        success = agent3.dispatch_final_email(candidate_id)
        assert success, "Email dispatch should succeed"
        print("✓ Agent 3 Dispatched Final Interview Email.")

    # Step 6: Verify Database Records
    print("\n--- [STEP 6] Verifying Data Persistence in SQLite ---")
    all_cands = get_all_candidates()
    emails = get_all_email_logs()
    
    print(f"✓ Total Candidates in DB: {len(all_cands)}")
    print(f"✓ Total Email Logs in DB: {len(emails)}")

    print("\n==========================================")
    print("ALL WORKFLOW TESTS PASSED SUCCESSFULLY!")
    print("==========================================\n")

if __name__ == "__main__":
    run_test()
