# services/ai_critic.py
import re, os, time, random
from datetime import datetime
from typing import Dict, Any, List, Optional

class AICritic:
    """
    Industry-aware resume critic.
    - Autodetects industry (or accepts it explicitly).
    - Uses per-industry keyword banks.
    - Gates tech-only advice behind industry == "technology".
    """
    def __init__(self):
        # Flip to False when you wire a real model
        self.use_mock = True

        # Per-industry keyword banks (extend as needed)
        self.industry_profiles = {
            "technology": {
                "keywords": [
                    "python","javascript","java","c++","c#","php","ruby","go","rust","swift",
                    "html","css","react","angular","vue","node","express","django","flask",
                    "sql","mysql","postgresql","mongodb","redis","sqlite",
                    "git","docker","kubernetes","aws","azure","gcp","jenkins","terraform",
                    "api","rest","graphql","microservices","devops","ci/cd","agile","scrum","github","gitlab"
                ],
                "sections_optional": ["Projects","Publications"],
                "hard_requirements": ["Experience","Education","Skills"],
                "role_markers": ["software","developer","engineer","data","machine learning","devops","full-stack"]
            },
            "healthcare": {
                "keywords": [
                    "patient care","clinical","charting","emr","ehr","epic","cerner","triage",
                    "hipaa","care plans","icu","med-surg","vitals","phlebotomy","medication administration",
                    "cpt","icd-10","diagnostic","treatment","nursing","rn","lpn","bcls","acls"
                ],
                "sections_optional": ["Certifications","Licensure"],
                "hard_requirements": ["Experience","Education","Skills"],
                "role_markers": ["nurse","rn","lpn","medical assistant","therapist","clinic","hospital"]
            },
            "education": {
                "keywords": [
                    "curriculum","lesson planning","classroom management","iep","assessment","differentiation",
                    "student engagement","parent communication","grading","standards","pedagogy","edtech"
                ],
                "sections_optional": ["Certifications","Licensure"],
                "hard_requirements": ["Experience","Education","Skills"],
                "role_markers": ["teacher","educator","instructor","tutor","school","classroom"]
            },
            "sales_marketing": {
                "keywords": [
                    "pipeline","crm","salesforce","prospecting","quota","negotiation","closing rate",
                    "roi","seo","sem","campaign","brand","go-to-market","lead generation","kpi","conversion"
                ],
                "sections_optional": ["Certifications","Awards"],
                "hard_requirements": ["Experience","Education","Skills"],
                "role_markers": ["sales","account executive","business development","marketing","brand"]
            },
            "finance_accounting": {
                "keywords": [
                    "gaap","reconciliation","ap/ar","forecasting","budgeting","variance analysis","audit",
                    "financial modeling","excel","sap","netsuite","quickbooks","p&l","balance sheet","sox"
                ],
                "sections_optional": ["Certifications"],
                "hard_requirements": ["Experience","Education","Skills"],
                "role_markers": ["accountant","financial analyst","controller","bookkeeper","audit"]
            },
            "operations_hr": {
                "keywords": [
                    "process improvement","sop","cross-functional","logistics","procurement","inventory",
                    "onboarding","recruiting","talent acquisition","compliance","policy","kpis","sla"
                ],
                "sections_optional": ["Certifications"],
                "hard_requirements": ["Experience","Education","Skills"],
                "role_markers": ["operations","office manager","hr","people","talent"]
            },
            "arts_media": {
                "keywords": [
                    "portfolio","storytelling","copywriting","adobe","photoshop","illustrator","premiere",
                    "brand voice","content strategy","editing","layout","typography","social media"
                ],
                "sections_optional": ["Portfolio","Projects"],
                "hard_requirements": ["Experience","Education","Skills"],
                "role_markers": ["designer","writer","editor","videographer","photographer","artist"]
            }
        }
        self.default_industry = "technology"

    async def analyze_resume(self, resume_text: str, job_description: Optional[str] = None, industry: Optional[str] = None) -> Dict[str, Any]:
        detected_industry = self._detect_industry(resume_text, job_description, industry)
        analysis = self._analyze_content(resume_text, detected_industry)
        score = self._calculate_dynamic_score(analysis)

        strengths = self._generate_strengths(analysis)
        improvements = self._generate_improvements(analysis)
        recommendations = self._generate_recommendations(analysis)

        return {
            "overall_score": score,
            "industry": detected_industry,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "keyword_analysis": {
                "industry_keywords": analysis['found_keywords'],
                "missing_keywords": analysis['missing_keywords'],
                "keyword_density": analysis['keyword_density']
            },
            "formatting_feedback": {
                "structure": analysis['structure_feedback'],
                "readability": analysis['readability_feedback'],
                "suggestions": analysis['format_suggestions']
            },
            "recommendations": recommendations
        }

    def _detect_industry(self, resume_text: str, job_description: Optional[str], explicit: Optional[str]) -> str:
        text = f"{resume_text}\n{job_description or ''}".lower()

        if explicit and explicit.lower() in self.industry_profiles:
            return explicit.lower()

        best, best_score = self.default_industry, -1
        for name, prof in self.industry_profiles.items():
            score = 0
            for marker in prof["role_markers"]:
                if marker in text:
                    score += 3
            for kw in prof["keywords"]:
                if kw in text:
                    score += 1
            if score > best_score:
                best, best_score = name, score

        return best if best_score > 0 else self.default_industry

    def _analyze_content(self, resume_text: str, industry: str) -> Dict[str, Any]:
        text_lower = resume_text.lower()
        words = resume_text.split()
        lines = [l.strip() for l in resume_text.split('\\n') if l.strip()]

        word_count = len(words)
        line_count = len(lines)

        has_email = bool(re.search(r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b', resume_text))
        has_phone = bool(re.search(r'(\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4})', resume_text))
        has_linked = 'linkedin' in text_lower
        has_github = 'github' in text_lower  # only rewarded for tech later

        prof = self.industry_profiles[industry]
        found_keywords = [kw.title() for kw in prof["keywords"] if kw in text_lower][:12]
        missing = [kw.title() for kw in prof["keywords"] if kw not in text_lower][:6]

        sections_found = []
        if any(w in text_lower for w in ['experience','employment','work history']): sections_found.append('Experience')
        if any(w in text_lower for w in ['education','degree','university','college']): sections_found.append('Education')
        if any(w in text_lower for w in ['skill','skills','technical','competencies']): sections_found.append('Skills')
        if any(w in text_lower for w in ['certification','certifications','license','licensure']): sections_found.append('Certifications')
        if any(w in text_lower for w in ['project','projects','portfolio']): sections_found.append('Projects')

        achievements_with_numbers = len(re.findall(r'\\d+%|\\$\\d+|€\\d+|£\\d+|\\d{4}\\+|\\d+x|improved|reduced|increased|decreased', text_lower))
        keyword_density = 'Excellent' if len(found_keywords) > 10 else 'Good' if len(found_keywords) > 5 else 'Needs Improvement'

        return {
            'industry': industry,
            'word_count': word_count,
            'line_count': line_count,
            'has_email': has_email,
            'has_phone': has_phone,
            'has_linkedin': has_linked,
            'has_github': has_github,
            'found_keywords': found_keywords,
            'missing_keywords': missing,
            'keyword_density': keyword_density,
            'sections_found': sections_found,
            'achievements_with_numbers': achievements_with_numbers,
            'structure_feedback': f"Contains {len(sections_found)} key sections: {', '.join(sections_found)}" if sections_found else "Basic structure detected",
            'readability_feedback': f"Good length with {word_count} words" if 250 <= word_count <= 600 else f"Consider adjusting length (currently {word_count} words)",
            'format_suggestions': self._get_format_suggestions(word_count, sections_found, achievements_with_numbers, industry)
        }

    def _calculate_dynamic_score(self, a: Dict[str, Any]) -> int:
        base = 70
        if 250 <= a['word_count'] <= 600: base += 5
        elif a['word_count'] < 200: base -= 10
        elif a['word_count'] > 800: base -= 5

        if a['has_email']: base += 5
        if a['has_phone']: base += 5
        if a['has_linkedin']: base += 3
        if a['industry'] == "technology" and a['has_github']: base += 3

        kc = len(a['found_keywords'])
        if kc > 10: base += 8
        elif kc > 5: base += 4
        elif kc < 2: base -= 4

        sc = len(a['sections_found'])
        if sc >= 4: base += 8
        elif sc >= 3: base += 5
        elif sc < 2: base -= 8

        if a['achievements_with_numbers'] > 2: base += 8
        elif a['achievements_with_numbers'] > 0: base += 4
        else: base -= 4

        base += random.randint(-5, 5)
        return max(60, min(95, base))

    def _generate_strengths(self, a: Dict[str, Any]) -> List[str]:
        s = []
        if a['word_count'] >= 250:
            s.append(f"Substantive detail with {a['word_count']} words shows scope and depth")
        if a['has_email'] and a['has_phone']:
            s.append("Complete contact information makes you easy to reach")
        if len(a['found_keywords']) > 5:
            s.append(f"Uses {len(a['found_keywords'])}+ relevant {a['industry']} keywords (e.g., {', '.join(a['found_keywords'][:3])})")
        if len(a['sections_found']) >= 3:
            s.append(f"Clear structure with key sections: {', '.join(a['sections_found'])}")
        if a['achievements_with_numbers'] > 0:
            s.append("Quantified outcomes help demonstrate impact")
        s.append(f"Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        return s[:4] if len(s) >= 4 else (s + ["Professional presentation", "Relevant experience shown"])[:4]

    def _generate_improvements(self, a: Dict[str, Any]) -> List[str]:
        out = []
        if a['word_count'] < 250:
            out.append(f"Expand content—{a['word_count']} words is light for screening context")
        elif a['word_count'] > 700:
            out.append(f"Condense to improve scannability—{a['word_count']} words is long for first pass")

        if not a['has_email']: out.append("Add a professional email")
        if not a['has_phone']: out.append("Include a phone number")
        if len(a['found_keywords']) < 5: out.append(f"Add more {a['industry']} keywords to match role language")
        if a['achievements_with_numbers'] == 0: out.append("Quantify outcomes (%, $, time saved, counts)")

        if a['industry'] == "technology" and 'Projects' not in a['sections_found']:
            out.append("Add a Projects section for hands-on work")
        if a['industry'] == "healthcare" and 'Certifications' not in a['sections_found']:
            out.append("Surface licensure/certifications (e.g., RN, ACLS) prominently")
        if a['industry'] == "education" and 'Certifications' not in a['sections_found']:
            out.append("List teaching credentials and relevant endorsements")
        if a['industry'] == "sales_marketing" and a['achievements_with_numbers'] < 2:
            out.append("Show pipeline, conversion, or quota metrics")

        return out[:4] if out else ["Add specific, role-aligned examples"]

    def _generate_recommendations(self, a: Dict[str, Any]) -> List[str]:
        rec = []
        if a['missing_keywords']:
            rec.append(f"Consider adding: {', '.join(a['missing_keywords'][:5])}")
        if a['achievements_with_numbers'] < 2:
            rec.append("Add more metrics (e.g., “Raised retention by 12%”, “Managed 30-bed unit”, “Cut costs by $75k”)")

        prof = self.industry_profiles[a['industry']]
        missing_sections = [s for s in prof["hard_requirements"] if s not in a['sections_found']]
        if missing_sections:
            rec.append(f"Add core sections: {', '.join(missing_sections)}")

        rec.append("Tailor examples to the target job description(s)")
        rec.append(f"Re-run analysis after edits: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return rec[:4]

    def _get_format_suggestions(self, word_count: int, sections: List[str], achievements: int, industry: str) -> List[str]:
        s = []
        if word_count > 600: s.append("Use bullets for scanability")
        if achievements == 0: s.append("Start bullets with strong verbs (Led, Improved, Reduced)")
        if len(sections) < 3: s.append("Add clear section headers")
        if industry in ("healthcare","education"): s.append("Place certifications/licensure near the top")
        return s or ["Ensure consistent formatting"]
