import re
from typing import Dict, Any, List, Tuple

DOMAINS_TAXONOMY = [
    "Artificial Intelligence / Machine Learning",
    "Data Science / Data Analytics",
    "Cyber Security",
    "Software Development",
    "Web Development",
    "Mobile App Development",
    "Cloud / DevOps",
    "Networking",
    "Database / SQL",
    "UI/UX Design",
    "Quality Assurance / Testing",
    "Other"
]

KEYWORD_MAP = {
    "Artificial Intelligence / Machine Learning": [
        "tensorflow", "pytorch", "keras", "machine learning", "deep learning", "computer vision",
        "nlp", "natural language processing", "scikit-learn", "sklearn", "neural network",
        "llm", "transformers", "huggingface", "opencv", "reinforcement learning", "bert", "gpt"
    ],
    "Data Science / Data Analytics": [
        "pandas", "numpy", "data analysis", "data science", "tableau", "power bi", "bi",
        "data visualization", "matplotlib", "seaborn", "statistics", "statistical modeling",
        "spark", "hadoop", "data mining", "predictive modeling", "r programming", "eda"
    ],
    "Cyber Security": [
        "kali linux", "wireshark", "siem", "network security", "penetration testing", "nmap",
        "burp suite", "owasp", "metasploit", "ethical hacking", "soc", "incident response",
        "vulnerability assessment", "cissp", "ceh", "comptia security+", "firewall", "cryptography"
    ],
    "Software Development": [
        "c++", "java", "c#", ".net", "python", "data structures", "algorithms", "oop",
        "software engineering", "design patterns", "clean code", "multithreading", "system design",
        "gof", "solid principles", "backend"
    ],
    "Web Development": [
        "react", "angular", "vue", "html", "css", "javascript", "typescript", "node.js",
        "express", "django", "fastapi", "flask", "next.js", "frontend", "full stack",
        "web applications", "rest api", "graphql", "tailwind"
    ],
    "Mobile App Development": [
        "flutter", "react native", "swift", "kotlin", "android", "ios", "xcode",
        "mobile development", "dart", "android studio", "objective-c", "mobile UI"
    ],
    "Cloud / DevOps": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins",
        "ci/cd", "cloud architecture", "helm", "devops", "cloud computing", "microservices"
    ],
    "Networking": [
        "cisco", "ccna", "ccnp", "routing", "switching", "tcp/ip", "dns", "dhcp",
        "vpn", "network administration", "bgp", "ospf", "lan/wan", "subnetting", "wireguard"
    ],
    "Database / SQL": [
        "sql", "postgresql", "mysql", "oracle", "mongodb", "database administration",
        "tsql", "pl/sql", "redis", "database design", "indexing", "etl", "query optimization"
    ],
    "UI/UX Design": [
        "figma", "sketch", "adobe xd", "ui/ux", "user research", "wireframing",
        "prototyping", "design system", "user experience", "user interface", "interaction design"
    ],
    "Quality Assurance / Testing": [
        "qa", "testing", "selenium", "cypress", "junit", "pytest", "test automation",
        "manual testing", "bug tracking", "jira", "loadrunner", "postman", "test cases"
    ]
}

def extract_candidate_heuristic(text: str) -> Dict[str, Any]:
    """Heuristic extraction of candidate details from raw CV text."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Candidate Name (Usually in top 3 lines)
    name = "Not Provided"
    for line in lines[:5]:
        if not re.search(r'@|http|phone|resume|cv|curriculum|email|page', line, re.IGNORECASE):
            if len(line.split()) in [2, 3, 4] and re.match(r'^[A-Za-z\s\.\'-]+$', line):
                name = line.strip()
                break
                
    # Email regex
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    email = email_match.group(0) if email_match else "Not Provided"
    
    # Phone regex
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else "Not Provided"
    
    # Location regex heuristically
    loc_match = re.search(r'(?:Location|Address|Based in|City)[:\s]+([A-Za-z\s,]+)', text, re.IGNORECASE)
    location = loc_match.group(1).strip() if loc_match else "Not Provided"
    
    # Extract skills
    all_known = []
    for domain_skills in KEYWORD_MAP.values():
        all_known.extend(domain_skills)
    found_skills = set()
    text_lower = text.lower()
    for item in set(all_known):
        if re.search(r'\b' + re.escape(item) + r'\b', text_lower):
            found_skills.add(item.title())
            
    skills_list = list(found_skills)
    
    # Programming languages & Frameworks breakdown
    prog_langs = [s for s in skills_list if s.lower() in ["python", "java", "c++", "c#", "javascript", "typescript", "kotlin", "swift", "dart", "r programming", "sql", "html", "css"]]
    tools = [s for s in skills_list if s not in prog_langs]
    
    # Years of experience extraction
    exp_years = 0.0
    exp_match = re.search(r'(\d+(?:\.\d+)?)\+?\s*(?:years|yrs)\s*(?:of)?\s*experience', text, re.IGNORECASE)
    if exp_match:
        try:
            exp_years = float(exp_match.group(1))
        except ValueError:
            exp_years = 1.0
    elif len(text) > 1000:
        exp_years = 2.0
        
    # Education heuristic
    education = []
    edu_matches = re.findall(r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.Tech|M\.Tech|Diploma|BSc|MSc)[^\n,]*', text, re.IGNORECASE)
    for edu in edu_matches[:3]:
        education.append({
            "degree": edu.strip(),
            "institution": "Universities / Recognized Institute",
            "field_of_study": "Relevant Major",
            "year": "Graduated"
        })
    if not education:
        education.append({
            "degree": "Degree Program",
            "institution": "Academic Institute",
            "field_of_study": "Computer Science / Relevant",
            "year": "Not Provided"
        })

    # Experience heuristic
    work_exp = []
    exp_sections = re.findall(r'(?:Senior|Lead|Junior|Principal)?\s*(?:Software Engineer|Developer|Analyst|Consultant|Architect|Specialist|Manager|Intern)[^\n]*', text, re.IGNORECASE)
    for role in exp_sections[:3]:
        work_exp.append({
            "company": "Tech Company / Organization",
            "role": role.strip(),
            "duration": "Relevant Experience Period",
            "description": f"Worked as {role.strip()} utilizing core domain technologies."
        })
        
    # Projects heuristic
    projects = []
    proj_matches = re.findall(r'(?:Project|Built|Developed|Created)[:\s]+([^\n]+)', text, re.IGNORECASE)
    for p in proj_matches[:2]:
        projects.append({
            "title": p.strip(),
            "description": f"Implemented project featuring {p.strip()}",
            "technologies": ", ".join(skills_list[:3]) if skills_list else "Relevant Stack"
        })
        
    # Certifications heuristic
    certifications = []
    cert_matches = re.findall(r'(AWS Certified|Certified|CISSP|CEH|CCNA|CompTIA|Google Professional|Azure Administrator)[^\n]*', text, re.IGNORECASE)
    for c in cert_matches[:3]:
        certifications.append({
            "title": c.strip(),
            "issuer": "Industry Certifying Authority"
        })
        
    return {
        "candidate_name": name,
        "email": email,
        "phone": phone,
        "location": location,
        "education": education,
        "skills": skills_list,
        "programming_languages": prog_langs,
        "frameworks_tools": tools,
        "work_experience": work_exp,
        "internships": [],
        "projects": projects,
        "certifications": certifications,
        "years_of_experience": exp_years
    }


def classify_domain_heuristic(extracted_info: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """Scores candidate against all 12 domains based on skills, text, projects, and certifications."""
    text_lower = raw_text.lower()
    domain_scores: Dict[str, float] = {d: 0.0 for d in DOMAINS_TAXONOMY}
    evidence_map: Dict[str, List[str]] = {d: [] for d in DOMAINS_TAXONOMY}
    
    # Match keywords
    for domain, keywords in KEYWORD_MAP.items():
        matched = []
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                matched.append(kw)
        score = len(matched) * 15.0
        if matched:
            domain_scores[domain] += score
            evidence_map[domain].append(f"Matching technical skills: {', '.join([m.title() for m in matched[:5]])}")

    # Check extracted profile fields for extra domain cues
    exp_years = extracted_info.get("years_of_experience", 0.0)
    for domain in DOMAINS_TAXONOMY:
        if domain_scores[domain] > 0 and exp_years > 0:
            domain_scores[domain] += min(exp_years * 5.0, 20.0)
            
    # Check certifications
    for cert in extracted_info.get("certifications", []):
        cert_str = (cert.get("title", "") if isinstance(cert, dict) else str(cert)).lower()
        if "security" in cert_str or "ceh" in cert_str or "cissp" in cert_str:
            domain_scores["Cyber Security"] += 25.0
            evidence_map["Cyber Security"].append(f"Industry certification: {cert_str.title()}")
        if "aws" in cert_str or "azure" in cert_str or "cloud" in cert_str:
            domain_scores["Cloud / DevOps"] += 25.0
            evidence_map["Cloud / DevOps"].append(f"Cloud certification: {cert_str.title()}")

    # Sort domains by score
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    
    top_domain, top_score = sorted_domains[0]
    
    if top_score == 0:
        top_domain = "Other"
        primary_conf = 50.0
        evidence = ["General professional background extracted from CV."]
        secondaries = [
            {"domain": "Software Development", "confidence": 40.0},
            {"domain": "Web Development", "confidence": 35.0}
        ]
    else:
        # Normalize primary confidence between 70% and 98%
        primary_conf = min(85.0 + (top_score * 0.25), 98.0)
        evidence = evidence_map[top_domain] if evidence_map[top_domain] else ["Strong technical alignment with domain competencies."]
        
        secondaries = []
        for d_name, d_score in sorted_domains[1:3]:
            if d_score > 0:
                conf = min(40.0 + (d_score * 0.2), primary_conf - 10.0)
            else:
                conf = 30.0
            secondaries.append({"domain": d_name, "confidence": round(conf, 1)})
            
    return {
        "primary_domain": top_domain,
        "confidence": round(primary_conf, 1),
        "secondary_domains": secondaries,
        "evidence": evidence
    }


def evaluate_screening_heuristic(extracted_info: Dict[str, Any], domain_info: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates objective preliminary 0-100 screening score and HR recommendation."""
    skills_count = len(extracted_info.get("skills", []))
    exp_years = extracted_info.get("years_of_experience", 0.0)
    projects_count = len(extracted_info.get("projects", []))
    certs_count = len(extracted_info.get("certifications", []))
    domain_conf = domain_info.get("confidence", 50.0)

    # Component scores (0-100)
    skill_score = min(skills_count * 12 + 20, 100)
    exp_score = min(exp_years * 20 + 30, 100)
    proj_cert_score = min((projects_count + certs_count) * 20 + 30, 100)
    alignment_score = domain_conf

    # Weighted overall score
    overall_score = int(
        (skill_score * 0.35) +
        (exp_score * 0.25) +
        (proj_cert_score * 0.20) +
        (alignment_score * 0.20)
    )
    overall_score = max(min(overall_score, 98), 35)

    if overall_score >= 80:
        recommendation = "Strong Match"
        summary = (
            f"The candidate demonstrates strong technical mastery in {domain_info.get('primary_domain')}, "
            f"supported by {skills_count} verified skills, relevant practical experience, and domain alignment."
        )
    elif overall_score >= 65:
        recommendation = "Potential Match"
        summary = (
            f"The candidate shows good alignment with {domain_info.get('primary_domain')} with solid core skills, "
            "making them a viable candidate for further technical assessment."
        )
    elif overall_score >= 50:
        recommendation = "Needs HR Review"
        summary = (
            f"The candidate has partial alignment with {domain_info.get('primary_domain')}. "
            "Further manual review of specific project outcomes or work experience is recommended."
        )
    else:
        recommendation = "Low Match"
        summary = (
            f"The candidate shows limited alignment with the core requirements of {domain_info.get('primary_domain')}."
        )

    return {
        "score": overall_score,
        "recommendation": recommendation,
        "summary": summary,
        "score_breakdown": {
            "skill_relevance": skill_score,
            "experience_relevance": exp_score,
            "projects_certifications": proj_cert_score,
            "domain_alignment": alignment_score
        }
    }
