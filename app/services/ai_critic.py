import re
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class KeywordBank:
    required_sections: List[str]
    hard_skills: List[str]
    soft_skills: List[str]
    extras: List[str]  # optional but nice to have for that domain

BANKS: Dict[str, KeywordBank] = {
    "technology": KeywordBank(
        required_sections=["Experience", "Skills", "Education"],
        hard_skills=["Python", "JavaScript", "SQL", "APIs", "Docker", "CI/CD", "AWS", "GCP", "Linux"],
        soft_skills=["collaboration", "problem solving", "communication"],
        extras=["GitHub", "projects", "hackathon", "open source"],
    ),
    "healthcare": KeywordBank(
        required_sections=["Experience", "Licenses", "Certifications", "Education"],
        hard_skills=["patient care", "EMR", "HIPAA", "triage", "medication administration", "ICD", "CPT"],
        soft_skills=["empathy", "communication", "teamwork", "attention to detail"],
        extras=["BLS", "ACLS", "RN", "CNA", "CPR"],
    ),
    "education": KeywordBank(
        required_sections=["Experience", "Certifications", "Education"],
        hard_skills=["lesson planning", "classroom management", "assessment", "IEP", "curriculum", "edtech"],
        soft_skills=["communication", "patience", "differentiation", "parent engagement"],
        extras=["state certification", "TESOL", "SPED"],
    ),
    "sales_marketing": KeywordBank(
        required_sections=["Experience", "Skills", "Education"],
        hard_skills=["CRM", "HubSpot", "Salesforce", "SEO", "SEM", "email marketing", "CAC", "LTV", "pipeline"],
        soft_skills=["negotiation", "communication", "leadership", "storytelling"],
        extras=["quota", "ARR", "MQL", "SQL (leads)", "campaigns"],
    ),
    "finance_accounting": KeywordBank(
        required_sections=["Experience", "Certifications", "Education"],
        hard_skills=["GAAP", "Excel", "forecasting", "budgeting", "P&L", "reconciliation", "audit", "QuickBooks"],
        soft_skills=["attention to detail", "communication", "problem solving"],
        extras=["CPA", "CFA", "SOX", "variance analysis"],
    ),
    "operations_hr": KeywordBank(
        required_sections=["Experience", "Skills", "Education"],
        hard_skills=["process improvement", "SOP", "onboarding", "recruiting", "HRIS", "benefits", "scheduling"],
        soft_skills=["organization", "communication", "stakeholder management"],
        extras=["Lean", "Six Sigma", "KPIs"],
    ),
    "arts_media": KeywordBank(
        required_sections=["Experience", "Portfolio", "Education"],
        hard_skills=["Adobe", "Photoshop", "Illustrator", "Premiere", "Figma", "copywriting", "storyboarding"],
        soft_skills=["creativity", "communication", "collaboration"],
        extras=["portfolio", "reel", "behance", "dribbble"],
    ),
}

FALLBACK = KeywordBank(
    required_sections=["Experience", "Skills", "Education"],
    hard_skills=[], soft_skills=[], extras=[]
)

def _has_whole(t: str, term: str) -> bool:
    """True if `term` appears as a whole token in `t` (case-insensitive)."""
    return re.search(rf"(?<![A-Za-z0-9]){re.escape(term.lower())}(?![A-Za-z0-9])", t) is not None

def detect_industry(text: str, forced: Optional[str]) -> str:
    """Whole-word detection to avoid false positives like '...ridICUlous' matching 'ICU'."""
    if forced:
        return forced
    t = text.lower()
    rules = [
        ("healthcare",        ["patient", "clinic", "hospital", "icu", "emr", "rn", "hipaa"]),
        ("education",         ["teacher", "classroom", "students", "curriculum", "lesson plan", "school"]),
        ("sales_marketing",   ["quota", "campaign", "seo", "leads", "crm", "pipeline"]),
        ("finance_accounting",["ledger", "reconciliation", "audit", "gaap", "accounts payable", "variance"]),
        ("operations_hr",     ["onboarding", "hris", "recruiting", "benefits", "scheduling", "sop"]),
        ("arts_media",        ["adobe", "photoshop", "illustrator", "premiere", "portfolio", "copywriter"]),
        ("technology",        ["github", "python", "api", "docker", "javascript", "cloud", "aws", "gcp"]),
    ]
    for label, cues in rules:
        if any(_has_whole(t, cue) for cue in cues):
            return label
    return "unknown"

def tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z\+\-/&\.\#0-9]*", text)

def compute_density(tokens: List[str], hits: List[str]) -> str:
    if not tokens:
        return "0.0% (0/0)"
    return f"{(len(hits)/len(tokens))*100:.1f}% ({len(hits)}/{len(tokens)})"

class AICritic:
    async def analyze_resume(self, resume_text: str, job_description: Optional[str] = None, industry: Optional[str] = None) -> Dict:
        detected = detect_industry(resume_text, industry)
        bank = BANKS.get(detected, FALLBACK)

        tokens = tokenize(resume_text)
        token_set = set(t.lower() for t in tokens)

        found_industry_terms = sorted({k for k in bank.hard_skills + bank.soft_skills + bank.extras if k.lower() in token_set})
        missing = sorted([k for k in bank.hard_skills if k.lower() not in token_set])

        # JD gap (if provided)
        jd_missing: List[str] = []
        if job_description:
            jd_tokens = set(t.lower() for t in tokenize(job_description))
            jd_keys = [w for w in (bank.hard_skills + bank.soft_skills) if w.lower() in jd_tokens]
            jd_missing = sorted([w for w in jd_keys if w.lower() not in token_set])

        # Sections present
        sections_present = [s for s in bank.required_sections if re.search(rf"\b{s}\b", resume_text, re.I)]
        sections_missing = [s for s in bank.required_sections if s not in sections_present]

        # Simple scoring (avoid keyword-stuffing bias)
        score = 60
        score += min(15, 3 * len(sections_present))
        score += min(10, len(found_industry_terms))
        score -= min(10, len(sections_missing) * 3)
        if jd_missing:
            score -= min(10, len(jd_missing))
        score = max(10, min(95, score))

        strengths: List[str] = []
        if sections_present:
            strengths.append(f"Includes core section(s): {', '.join(sections_present)}.")
        if found_industry_terms:
            strengths.append(f"Industry-aligned keywords present: {', '.join(found_industry_terms)}.")
        if re.search(r"\b\d{4}\b", resume_text):
            strengths.append("Dates present—timeline is reconstructable.")
        if re.search(r"\b(\d+%|\$\d+|[0-9,]+\+?)\b", resume_text):
            strengths.append("Quantified outcomes detected (numbers/percentages).")

        improvements: List[str] = []
        if sections_missing:
            improvements.append(f"Add a clear **{', '.join(sections_missing)}** section.")
        if jd_missing:
            improvements.append(f"From the job post, consider addressing: **{', '.join(jd_missing)}**.")
        if detected == "technology":
            if "github" not in token_set and "project" not in token_set:
                improvements.append("Include a Projects section with links (GitHub/portfolio) and 2–3 bullets each).")

        # Formatting heuristics
        lines = [ln for ln in resume_text.splitlines() if ln.strip()]
        bullets = sum(1 for ln in lines if re.match(r"^\s*[-•▪·]", ln))
        formatting = {
            "structure": "Mostly structured" if len(lines) > 20 else "Sparse/short — consider expanding key roles.",
            "readability": "Has bullet points" if bullets >= 5 else "Add 4–8 bullets describing impact under roles.",
            "suggestions": [
                "Lead bullets with action verbs; finish with measurable outcomes.",
                "Keep tense consistent (present for current role, past for previous).",
                "Use one consistent date format across all roles."
            ],
        }

        domain_recs = {
            "healthcare": ["List active licenses (e.g., RN, CNA) and expiration dates.", "Include EMR systems used."],
            "education": ["Call out certifications and grade levels; include assessment methods."],
            "sales_marketing": ["Show quota attainment and pipeline metrics; include CRM used."],
            "finance_accounting": ["Add GAAP/controls experience and tools; quantify savings or accuracy gains."],
            "operations_hr": ["Surface KPIs improved (throughput, cycle time, retention)."],
            "arts_media": ["Link to portfolio/reel; list tools and notable clients/projects."],
            "technology": ["Summarize tech stack and impact; link to repo/portfolio if relevant."],
            "unknown": ["Tailor the top third of your resume to the target role; mirror required skills."],
        }

        return {
            "industry": detected,
            "overall_score": score,
            "keyword_analysis": {
                "industry_keywords": found_industry_terms,
                "missing_keywords": jd_missing or missing,
                "keyword_density": compute_density(tokens, found_industry_terms),
            },
            "strengths": strengths or ["Clear and readable."],
            "areas_for_improvement": improvements or ["Tighten alignment to the target job by mirroring required skills."],
            "formatting_feedback": formatting,
            "recommendations": domain_recs.get(detected, domain_recs["unknown"]),
        }