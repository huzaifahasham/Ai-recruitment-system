"""
agents/selection_agent.py — Agent 3: Candidate Selection Agent

Role:
1. Receive interview evaluation result from Agent 2.
2. Identify PASS vs FAIL candidates.
3. Update candidate status in database & HR dashboard:
   - PASS -> 'Passed — Final Interview'
   - FAIL -> 'Failed — Not Selected'
4. Provide action to dispatch Final Interview Invitation email for PASS candidates.
"""

from database import get_candidate_by_id, update_candidate_status
from email_service import send_final_interview_email


class CandidateSelectionAgent:
    """Agent 3: Responsible for final candidate selection and status routing."""

    def process_selection(self, candidate_id: int, score: int, is_pass: bool) -> dict:
        """Processes selection decision based on interview score."""
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate ID {candidate_id} not found.")

        if is_pass or score >= 60:
            final_status = "Passed — Final Interview"
        else:
            final_status = "Failed — Not Selected"

        # Update candidate status in database
        update_candidate_status(candidate_id, final_status)

        print(f"[Agent 3] Candidate {candidate['name']} (ID: {candidate_id}) -> Final Status: {final_status}")

        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate["name"],
            "score": score,
            "final_status": final_status,
            "can_send_final_email": (final_status == "Passed — Final Interview")
        }

    def dispatch_final_email(self, candidate_id: int) -> bool:
        """Dispatches the Final Interview Invitation email to passed candidates."""
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate ID {candidate_id} not found.")

        status = candidate.get("status", "")
        if "Passed" not in status:
            raise ValueError("Final interview email can only be sent to passed candidates.")

        success = send_final_interview_email(candidate_id, candidate["name"], candidate["email"])
        print(f"[Agent 3] Dispatched final interview email for Candidate {candidate['name']}")
        return success
