"""
agents/interview_agent.py — Agent 2: AI Interview Agent

Role:
1. Read candidate CV details.
2. Generate 10 tailored interview questions using LLM AI.
3. Create unique interview link & token.
4. Evaluate submitted answers, calculate score out of 100.
5. Determine PASS (Score >= 60) or FAIL (Score < 60).
"""

import uuid
from llm_service import call_llm_json
from database import (
    get_candidate_by_id,
    create_interview,
    get_interview_by_token,
    update_interview_submission,
    update_candidate_status
)


class AIInterviewAgent:
    """Agent 2: Responsible for interview question generation and answer evaluation."""

    def generate_interview(self, candidate_id: int) -> dict:
        """Generates 10 interview questions based on candidate CV and creates unique interview token."""
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate ID {candidate_id} not found.")

        skills = candidate.get("skills", "General Skills")
        education = candidate.get("education", "Education")
        experience = candidate.get("experience", "Experience")

        system_prompt = (
            "You are Agent 2 — AI Interview Agent in an AI Recruitment System. "
            "Generate exactly 10 interview questions tailored to the candidate's skills, education, and experience. "
            "Return JSON format with key 'questions', which is a list of 10 clear, professional questions."
        )
        user_prompt = (
            f"Candidate Profile:\n"
            f"- Name: {candidate.get('name')}\n"
            f"- Skills: {skills}\n"
            f"- Education: {education}\n"
            f"- Experience: {experience}\n\n"
            "Generate 10 relevant technical and situational questions."
        )

        ai_result = call_llm_json(system_prompt, user_prompt)
        questions = []
        if ai_result and isinstance(ai_result, dict) and "questions" in ai_result:
            questions = ai_result["questions"]

        # Fallback question set if AI key unavailable
        if len(questions) < 10:
            questions = self._default_questions(skills)

        # Ensure exactly 10 questions
        questions = questions[:10]

        # Generate unique token
        token = str(uuid.uuid4())

        # Save interview to database
        interview_id = create_interview(candidate_id, token, questions)

        # Update candidate status
        update_candidate_status(candidate_id, "Interview Generated")

        print(f"[Agent 2] Generated 10 questions for Candidate {candidate['name']} (Token: {token})")

        return {
            "interview_id": interview_id,
            "candidate_id": candidate_id,
            "token": token,
            "questions": questions
        }

    def evaluate_answers(self, token: str, user_answers: list) -> dict:
        """Evaluates candidate answers, calculates score out of 100, determines PASS/FAIL."""
        interview = get_interview_by_token(token)
        if not interview:
            raise ValueError("Invalid interview link or token.")

        if interview.get("status") == "Completed":
            raise ValueError("This interview has already been submitted.")

        questions = interview.get("questions", [])
        
        # Structure Q&A for evaluation
        qa_pairs = []
        for i, q in enumerate(questions):
            ans = user_answers[i] if i < len(user_answers) else "No answer provided"
            qa_pairs.append({"question": q, "answer": ans})

        system_prompt = (
            "You are Agent 2 — AI Interview Agent evaluating candidate responses. "
            "Score the overall performance from 0 to 100 based on accuracy, depth, and clarity of answers. "
            "Return JSON with key 'score' (integer 0-100) and 'feedback' (brief summary string)."
        )
        user_prompt = f"Candidate interview Q&A list:\n\n" + "\n".join(
            [f"Q{idx+1}: {pair['question']}\nA: {pair['answer']}" for idx, pair in enumerate(qa_pairs)]
        )

        ai_result = call_llm_json(system_prompt, user_prompt)
        score = 70
        feedback = "Solid demonstration of core concepts."

        if ai_result and isinstance(ai_result, dict):
            score = int(ai_result.get("score", 70))
            feedback = str(ai_result.get("feedback", "Completed interview."))
        else:
            # Rule-based score calculation fallback
            total_words = sum([len(ans.split()) for ans in user_answers])
            if total_words > 100:
                score = 80
                feedback = "Detailed and articulate responses provided across all questions."
            elif total_words > 40:
                score = 65
                feedback = "Good effort, provided reasonable responses to most questions."
            else:
                score = 45
                feedback = "Answers were too brief or incomplete."

        # Cap score 0 to 100
        score = max(0, min(100, score))

        # PASS / FAIL Rule (Passing score >= 60)
        outcome_status = "PASS" if score >= 60 else "FAIL"

        # Update interview record
        update_interview_submission(token, user_answers, score, outcome_status, feedback)

        print(f"[Agent 2] Evaluated Interview Token {token} -> Score: {score}/100 ({outcome_status})")

        return {
            "candidate_id": interview["candidate_id"],
            "token": token,
            "score": score,
            "status": outcome_status,
            "feedback": feedback
        }

    def _default_questions(self, skills: str) -> list:
        """Returns 10 default interview questions for fallback."""
        return [
            f"1. Could you describe your experience working with {skills}?",
            "2. How do you approach debugging or solving a complex technical issue?",
            "3. Can you explain a major project you worked on recently and your role in it?",
            "4. How do you ensure your code is clean, maintainable, and well-tested?",
            "5. What tools and environments do you prefer for development?",
            "6. How do you handle tight deadlines or changing project requirements?",
            "7. Describe a situation where you had to learn a new tool or language quickly.",
            "8. How do you collaborate with team members during code reviews and planning?",
            "9. What is your understanding of security and optimization best practices?",
            "10. Where do you see yourself professionally in the next 2-3 years?"
        ]
