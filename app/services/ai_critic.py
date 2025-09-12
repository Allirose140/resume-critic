import openai
from typing import Dict, Any, List
import os
import random
import time
import re
from datetime import datetime


class AICritic:
    def __init__(self):
        # You'll need to set your OpenAI API key
        # For now, we'll create a mock version
        self.use_mock = True  # Set to False when you have an API key

        # Technical keywords to look for
        self.tech_keywords = {
            'languages': ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node', 'express', 'django', 'flask'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite'],
            'tools': ['git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'terraform'],
            'concepts': ['api', 'rest', 'graphql', 'microservices', 'devops', 'ci/cd', 'agile', 'scrum']
        }

    async def analyze_resume(self, resume_text: str, job_description: str = None) -> Dict[str, Any]:
        """Analyze resume using AI and provide detailed feedback"""
        if self.use_mock:
            return self._dynamic_mock_analysis(resume_text)
        else:
            return await self._openai_analysis(resume_text, job_description)

    def _dynamic_mock_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Dynamic mock AI analysis that changes based on actual content"""

        # Use current timestamp and content hash to ensure uniqueness
        timestamp_seed = int(time.time())
        content_hash = hash(resume_text.lower())
        random.seed(timestamp_seed + content_hash)

        # Analyze the actual resume content
        analysis_results = self._analyze_content(resume_text)

        # Generate dynamic score based on content quality
        score = self._calculate_dynamic_score(analysis_results)

        # Generate context-aware feedback
        strengths = self._generate_strengths(analysis_results)
        improvements = self._generate_improvements(analysis_results)
        recommendations = self._generate_recommendations(analysis_results)

        return {
            "overall_score": score,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "keyword_analysis": {
                "technical_keywords": analysis_results['found_keywords'],
                "missing_keywords": analysis_results['missing_keywords'],
                "keyword_density": analysis_results['keyword_density']
            },
            "formatting_feedback": {
                "structure": analysis_results['structure_feedback'],
                "readability": analysis_results['readability_feedback'],
                "suggestions": analysis_results['format_suggestions']
            },
            "recommendations": recommendations
        }

    def _analyze_content(self, resume_text: str) -> Dict[str, Any]:
        """Analyze the actual resume content for meaningful insights"""
        text_lower = resume_text.lower()
        words = resume_text.split()
        lines = [line.strip() for line in resume_text.split('\n') if line.strip()]

        # Basic metrics
        word_count = len(words)
        line_count = len(lines)
        char_count = len(resume_text)

        # Contact information detection
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text))
        has_phone = bool(re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', resume_text))
        has_linkedin = 'linkedin' in text_lower
        has_github = 'github' in text_lower

        # Find technical keywords
        found_keywords = []
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword.title())

        # Suggest missing important keywords
        important_missing = []
        if 'git' not in text_lower: important_missing.append('Git')
        if 'api' not in text_lower: important_missing.append('API')
        if 'sql' not in text_lower and 'database' not in text_lower: important_missing.append('SQL')
        if 'agile' not in text_lower and 'scrum' not in text_lower: important_missing.append('Agile')

        # Analyze structure
        sections_found = []
        if any(word in text_lower for word in ['experience', 'work', 'employment']): sections_found.append('Experience')
        if any(word in text_lower for word in ['education', 'degree', 'university', 'college']): sections_found.append(
            'Education')
        if any(word in text_lower for word in ['project', 'projects']): sections_found.append('Projects')
        if any(word in text_lower for word in ['skill', 'skills', 'technical']): sections_found.append('Skills')

        # Detect achievements with numbers
        achievements_with_numbers = len(
            re.findall(r'\d+%|\d+x|\d+\+|increased.*\d+|improved.*\d+|reduced.*\d+', text_lower))

        return {
            'word_count': word_count,
            'line_count': line_count,
            'has_email': has_email,
            'has_phone': has_phone,
            'has_linkedin': has_linkedin,
            'has_github': has_github,
            'found_keywords': found_keywords[:8],  # Limit to top 8
            'missing_keywords': important_missing[:4],  # Limit to top 4
            'keyword_density': 'Excellent' if len(found_keywords) > 10 else 'Good' if len(
                found_keywords) > 5 else 'Needs Improvement',
            'sections_found': sections_found,
            'achievements_with_numbers': achievements_with_numbers,
            'structure_feedback': f"Contains {len(sections_found)} key sections: {', '.join(sections_found)}" if sections_found else "Basic structure detected",
            'readability_feedback': f"Good length with {word_count} words" if 250 <= word_count <= 600 else f"Consider adjusting length (currently {word_count} words)",
            'format_suggestions': self._get_format_suggestions(word_count, sections_found, achievements_with_numbers)
        }

    def _calculate_dynamic_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate a dynamic score based on actual resume content"""
        base_score = 70

        # Word count scoring
        if 250 <= analysis['word_count'] <= 600:
            base_score += 5
        elif analysis['word_count'] < 200:
            base_score -= 10
        elif analysis['word_count'] > 800:
            base_score -= 5

        # Contact information
        if analysis['has_email']: base_score += 5
        if analysis['has_phone']: base_score += 5
        if analysis['has_linkedin']: base_score += 3
        if analysis['has_github']: base_score += 3

        # Technical keywords
        keyword_count = len(analysis['found_keywords'])
        if keyword_count > 8:
            base_score += 10
        elif keyword_count > 4:
            base_score += 5
        elif keyword_count < 2:
            base_score -= 5

        # Structure
        section_count = len(analysis['sections_found'])
        if section_count >= 4:
            base_score += 8
        elif section_count >= 3:
            base_score += 5
        elif section_count < 2:
            base_score -= 10

        # Quantified achievements
        if analysis['achievements_with_numbers'] > 2:
            base_score += 8
        elif analysis['achievements_with_numbers'] > 0:
            base_score += 4
        else:
            base_score -= 5

        # Add some randomness for variety (±5 points)
        base_score += random.randint(-5, 5)

        return max(60, min(95, base_score))

    def _generate_strengths(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate strengths based on actual content analysis"""
        strengths = []

        if analysis['word_count'] >= 250:
            strengths.append(
                f"Well-detailed resume with {analysis['word_count']} words showing comprehensive experience")

        if analysis['has_email'] and analysis['has_phone']:
            strengths.append("Complete contact information makes you easy to reach")

        if len(analysis['found_keywords']) > 5:
            strengths.append(
                f"Strong technical vocabulary with {len(analysis['found_keywords'])} relevant keywords: {', '.join(analysis['found_keywords'][:3])}")

        if len(analysis['sections_found']) >= 3:
            strengths.append(f"Well-organized structure with clear sections: {', '.join(analysis['sections_found'])}")

        if analysis['achievements_with_numbers'] > 0:
            strengths.append(
                f"Includes {analysis['achievements_with_numbers']} quantified achievement(s) - great for demonstrating impact")

        if analysis['has_github']:
            strengths.append("GitHub profile included - shows commitment to code sharing and collaboration")

        # Add timestamp-based unique strength
        strengths.append(
            f"Analysis completed on {datetime.now().strftime('%Y-%m-%d at %H:%M')} - fresh perspective provided")

        # Ensure we have at least 4 strengths
        generic_strengths = [
            "Professional presentation and clear formatting",
            "Demonstrates relevant experience in the field",
            "Good use of industry-appropriate terminology",
            "Shows progression and growth in career/education"
        ]

        while len(strengths) < 4:
            strengths.append(generic_strengths[len(strengths) % len(generic_strengths)])

        return strengths[:4]  # Return top 4

    def _generate_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on actual content"""
        improvements = []

        if analysis['word_count'] < 250:
            improvements.append(
                f"Expand content - current {analysis['word_count']} words is quite brief for a comprehensive resume")
        elif analysis['word_count'] > 700:
            improvements.append(
                f"Consider condensing - {analysis['word_count']} words may be too lengthy for initial screening")

        if not analysis['has_email']:
            improvements.append("Add a professional email address to contact information")

        if not analysis['has_phone']:
            improvements.append("Include a phone number for direct contact")

        if len(analysis['found_keywords']) < 5:
            improvements.append("Increase technical keywords to improve ATS (Applicant Tracking System) compatibility")

        if analysis['achievements_with_numbers'] == 0:
            improvements.append(
                "Add quantified achievements (percentages, dollar amounts, timeframes) to demonstrate impact")

        if not analysis['has_linkedin']:
            improvements.append("Consider adding LinkedIn profile to showcase professional network")

        if 'Projects' not in analysis['sections_found']:
            improvements.append("Add a projects section to showcase hands-on technical experience")

        # Always include at least one improvement
        if not improvements:
            improvements.append("Consider adding more specific examples of your technical accomplishments")

        return improvements[:4]  # Return top 4

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on content analysis"""
        recommendations = []

        # Content-specific recommendations
        if len(analysis['missing_keywords']) > 0:
            recommendations.append(
                f"Consider adding these relevant keywords: {', '.join(analysis['missing_keywords'])}")

        if analysis['achievements_with_numbers'] < 2:
            recommendations.append(
                "Add more metrics: 'Improved performance by 25%', 'Managed team of 5', 'Completed project 2 weeks ahead of schedule'")

        # Structure recommendations
        if len(analysis['sections_found']) < 4:
            missing_sections = set(['Experience', 'Education', 'Projects', 'Skills']) - set(analysis['sections_found'])
            if missing_sections:
                recommendations.append(f"Consider adding these sections: {', '.join(list(missing_sections)[:2])}")

        # Always include actionable advice
        recommendations.append("Tailor keywords and examples to match specific job descriptions you're applying for")

        # Add timestamp for uniqueness
        recommendations.append(
            f"Last analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - re-analyze after making changes")

        return recommendations[:4]

    def _get_format_suggestions(self, word_count: int, sections: List[str], achievements: int) -> List[str]:
        """Get formatting suggestions based on content analysis"""
        suggestions = []

        if word_count > 600:
            suggestions.append("Use bullet points to make content more scannable")

        if achievements == 0:
            suggestions.append("Use bullet points starting with action verbs (Developed, Implemented, Achieved)")

        if len(sections) < 3:
            suggestions.append("Add clear section headers to improve organization")

        suggestions.append("Ensure consistent formatting throughout document")

        return suggestions

    async def _openai_analysis(self, resume_text: str, job_description: str = None) -> Dict[str, Any]:
        """Real OpenAI analysis (when API key is available)"""
        # This would contain the actual OpenAI API call
        # You can implement this later when you have an API key
        try:
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            prompt = f"""
            Analyze this resume and provide detailed feedback in JSON format:

            Resume text: {resume_text}

            Please provide:
            1. Overall score (60-95)
            2. List of strengths (3-4 items)
            3. Areas for improvement (3-4 items)
            4. Technical keywords found
            5. Missing important keywords
            6. Specific recommendations

            Focus on content quality, ATS optimization, and professional presentation.
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            # Parse and return the response
            # This would need proper JSON parsing
            return {"status": "OpenAI analysis would go here"}

        except Exception as e:
            # Fall back to mock analysis if OpenAI fails
            return self._dynamic_mock_analysis(resume_text)