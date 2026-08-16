import pytest
from backend.ai.fallback_engine import (
    extract_candidate_heuristic,
    classify_domain_heuristic,
    evaluate_screening_heuristic
)

def test_cyber_security_classification():
    cv_text = """
    Penetration Tester & Security Specialist
    Skills: Kali Linux, Wireshark, Nmap, Burp Suite, OWASP, Metasploit, SIEM, Incident Response.
    Certifications: CEH, CompTIA Security+.
    Experience: 4 years as Cyber Security Analyst conducting penetration testing.
    """
    extracted = extract_candidate_heuristic(cv_text)
    domain_res = classify_domain_heuristic(extracted, cv_text)
    screening_res = evaluate_screening_heuristic(extracted, domain_res)

    assert domain_res["primary_domain"] == "Cyber Security"
    assert domain_res["confidence"] >= 75.0
    assert len(domain_res["evidence"]) > 0
    assert screening_res["score"] >= 70
    assert screening_res["recommendation"] in ["Strong Match", "Potential Match"]


def test_aiml_classification():
    cv_text = """
    Machine Learning Engineer
    Skills: Python, TensorFlow, PyTorch, Pandas, Scikit-learn, Computer Vision, Deep Learning, NLP.
    Experience: 3 years training neural networks and LLMs at AI Dynamics.
    Education: MS in Artificial Intelligence.
    """
    extracted = extract_candidate_heuristic(cv_text)
    domain_res = classify_domain_heuristic(extracted, cv_text)

    assert domain_res["primary_domain"] == "Artificial Intelligence / Machine Learning"
    assert domain_res["confidence"] >= 75.0


def test_web_dev_classification():
    cv_text = """
    Full Stack Developer
    Skills: React, Next.js, Node.js, TypeScript, HTML, CSS, Express, MongoDB.
    Experience: 3 years building web applications.
    """
    extracted = extract_candidate_heuristic(cv_text)
    domain_res = classify_domain_heuristic(extracted, cv_text)

    assert domain_res["primary_domain"] == "Web Development"


def test_incomplete_cv_handling():
    cv_text = "John Doe\nCandidate Resume."
    extracted = extract_candidate_heuristic(cv_text)
    assert extracted["email"] == "Not Provided"
    assert extracted["phone"] == "Not Provided"

    domain_res = classify_domain_heuristic(extracted, cv_text)
    assert domain_res["primary_domain"] in ["Other", "Software Development"]
