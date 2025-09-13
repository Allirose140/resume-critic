import re
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class KeywordBank:
    required_sections: List[str]
    hard_skills: List[str]
    soft_skills: List[str]
    extras: List[str]  # nice-to-haves for that domain

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
    # NEW: service/retail (fast food, cashier, barista, etc.)
    "service_retail": KeywordBank(
        required_sections=["Experience", "Skills", "Education"],
        hard_skills=[
            "customer service", "cash handling", "point of sale", "POS",
            "food safety", "sanitation", "inventory", "stocking", "scheduling"
        ],
        soft_skills=["communication", "teamwork", "time management", "reliability"],
        extras=["shift lead", "crew member", "barista", "cashier", "server"],
    ),
}

FALLBACK = KeywordBank(
    required_sections=["Experience", "Skills", "Education"],
    hard_skills=[], soft_skills=[], extras=[]
)

# ---------- detection helpers ----------
def _has_whole(t: str, term: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9]){re.escape(term.lower())}(?![A-Za-z0-9])", t) is not None

def detect_industry(text: str, forced: Optional[str]) -> str:
    """
    Vote-based detection with whole-word cues.
    Only choose an industry if it has >= 2 cue hits; otherwise 'unknown'.
    """
    if forced:
        return forced
    t = text.lower()
    rules = [
        ("service_retail",    ["cashier", "barista", "server", "crew", "shift lead", "pos", "point of sale", "fast food", "retail", "store"]),
        ("healthcare",        ["patient", "clinic", "hospital", "icu", "emr", "rn", "hipaa"]),
        ("education",         ["teacher", "classroom", "students", "curriculum", "lesson plan", "school"]),
        ("sales_marketing",   ["quota", "campaign", "seo", "leads", "crm", "pipeline"]),
        ("finance_accounting",["ledger", "reconciliation", "audit", "gaap", "accounts payable", "variance"]),
        ("operations_hr",     ["onboarding", "hris", "recruiting", "benefits", "scheduling", "sop"]),
        ("arts_media",        ["adobe", "photoshop", "illustrator", "premiere", "portfolio", "copywriter"]),
        ("technology",        ["github", "python", "api", "docker", "javascript", "cloud", "aws", "gcp"]),
    ]
    votes = {label: sum(1 for cue in cues if _has_whole(t, cue)) for label, cues in rules}
    label, score = max(votes.items(), key=lambda kv: kv[1])
    return label if score >= 2 else "unknown"

# ---------- tokenization & metrics ----------
def tokenize(text: str) -> List[str]:
    # tokens that start with a letter, may contain +-/&.#digits
    return re.findall(r"[A-Za-z][A-Za-z\+\-/&\.\#0-9]*", text)

def compute_coverage(found: List[str], universe: List[str]) -> str:
    """Coverage over the relevant universe (JD terms if provided, else none)."""
    if not universe:
        return "—"
    # de-dup case-insensitively
    u = {x.lower() for x in universe}
    f = {x.lower() for x in found if x.lower() in u}
    return f"{(len(f)/len(u))*100:.1f}% ({len(f)}/{len(u)})"

# ---------- “bad resume” heuristics ----------
BAD_TONE_PATTERNS = [
    r"\bunemploy(ed|ment)?\b",
    r"\bquit\b",
    r"\bargu(ed|ing)\b",
    r"\bboring\b",
    r"\bvideo\s*games?\b",
    r"\bmemes?\b",
    r"\bpizza\s*rolls?\b",
    r"\breddit\b",
    r"\bmom('s)?\s+basement\b",
]
UNPRO_EMAIL_LOCALPART = r"(cool|dude|420|69|swag|gamer|lol|lmao)"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

def find_email(text: str) -> Optional[str]:
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None

def score_red_flags(text: str) -> int:
    t = text.lower()
    penalty = 0
    hits = sum(1 for p in BAD_TONE_PATTERNS if re.search(p, t))
    penalty -= min(30, hits * 8)  # up to -30
    em = find_email(t)
    if em:
        local = em.split("@")[0]
        if re.search(UNPRO_EMAIL_LOCALPART, local):
            penalty -= 10
    tokens = tokenize(text)
    if len(tokens) < 180:
        penalty -= 10
    bullets = sum(1 for ln in text.splitlines() if re.match(r"^\s*[-•▪·]", ln))
    if bullets < 3:
        penalty -= 8
    return penalty

# ---------- main critic ----------
class AICritic:
    async def analyze_resume(self, resume_text: str, job_description: Optional[str] = None, industry: Optional[str] = None) -> Dict:
        detected = detect_industry(resume_text, industry)
        bank = BANKS.get(detected, FALLBACK)

        tokens = tokenize(resume_text)
        token_set = set(t.lower() for t in tokens)

        found_industry_terms = sorted({k for k in bank.hard_skills + bank.soft_skills + bank.extras if k.lower() in token_set})

        # JD-aware universe for coverage/suggestions
        jd_keys: List[str] = []
        if job_description:
            jd_tokens = set(t.lower() for t in tokenize(job_description))
            jd_keys = [w for w in (bank.hard_skills + bank.soft_skills) if w.lower() in jd_tokens]

        # Suggested keywords:
        # - If JD provided: show missing JD-aligned keywords (concrete, non-buzzwordy).
        # - If NO JD: show nothing (avoid generic noise).
        suggested = []
        if job_description:
            suggested = sorted([w for w in jd_keys if w.lower() not in token_set])

        # Sections present/missing
        sections_present = [s for s in bank.required_sections if re.search(rf"\b{s}\b", resume_text, re.I)]
        sections_missing = [s for s in bank.required_sections if s not in sections_present]

        # ---------- scoring ----------
        score = 40
        score += min(12, 4 * len(sections_present))        # up to +12
        score += min(8, len(found_industry_terms))         # up to +8
        score -= min(15, 5 * len(sections_missing))        # up to -15
        if job_description and suggested:
            score -= min(10, len(suggested))               # up to -10
        score += score_red_flags(resume_text)              # 0 to -30
        score = max(5, min(95, score))

        # ---------- narratives ----------
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
        if suggested:
            improvements.append(f"From the job post, consider addressing: **{', '.join(suggested)}**.")

        # Tech: repo/portfolio nag only if truly absent
        repo_markers = {"github", "portfolio", "repo", "repository", "project", "projects"}
        if detected == "technology" and not (token_set & repo_markers):
            improvements.append("Include a Projects section with links (GitHub/portfolio) and 2–3 bullets each).")

        # Professionalism nudges
        if re.search(r"\bunemploy(ed|ment)?\b", resume_text, re.I):
            improvements.append("Replace 'Unemployed' with a neutral gap explanation (e.g., education, caregiving, self-study).")
        em = find_email(resume_text)
        if em and re.search(UNPRO_EMAIL_LOCALPART, em.split("@")[0]):
            improvements.append("Use a professional email (firstname.lastname@provider).")
        if any(re.search(p, resume_text, re.I) for p in BAD_TONE_PATTERNS):
            improvements.append("Remove casual/jokey lines; use professional, achievement-focused language.")

        # formatting heuristics
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

        # Coverage universe: JD if present; else none (we show '—' rather than misleading %)
        coverage_universe = jd_keys if job_description else []
        keyword_coverage = compute_coverage(found_industry_terms, coverage_universe)

        domain_recs = {
            "service_retail": ["Quantify customer throughput, order accuracy, and cash-handling; note POS systems."],
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
                "suggested_keywords": suggested,         # JD-driven only
                "keyword_coverage": keyword_coverage,    # over JD universe (or '—')
            },
            "strengths": strengths or ["Clear and readable."],
            "areas_for_improvement": improvements or ["Tighten alignment to the target job by mirroring required skills."],
            "formatting_feedback": formatting,
            "recommendations": domain_recs.get(detected, domain_recs["unknown"]),
        }
