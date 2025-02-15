import requests
from dotenv import load_dotenv
import os
from textstat import textstat

class QualityReviewer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.criteria = [
            'content_consistency',
            'writing_style',
            'readability',
            'seo_optimization'
        ]

    def review_press_kit(self, press_kit):
        scores = {}
        feedback = {}
        readability_scores = {}

        # Check readability for each section
        for section, content in press_kit.items():
            readability_scores[section] = self._check_readability(content)

        # Evaluate each criterion
        for criterion in self.criteria:
            score, feedback_text = self.evaluate_criterion(press_kit, criterion, readability_scores)
            scores[criterion] = score
            feedback[criterion] = feedback_text

        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)

        # Generate recommendations
        recommendations = self.generate_recommendations(feedback, readability_scores)

        return {
            'scores': scores,
            'feedback': feedback,
            'overall_score': overall_score,
            'recommendations': recommendations,
            'readability_analysis': readability_scores
        }

    def _check_readability(self, text):
        """Calculate readability scores using textstat"""
        return {
            'flesch_reading_ease': textstat.flesch_reading_ease(text),
            'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
            'gunning_fog': textstat.gunning_fog(text),
            'smog_index': textstat.smog_index(text),
            'automated_readability_index': textstat.automated_readability_index(text),
            'coleman_liau_index': textstat.coleman_liau_index(text)
        }

    def evaluate_criterion(self, press_kit, criterion, readability_scores):
        prompt = self._create_evaluation_prompt(press_kit, criterion, readability_scores)
        response = self._get_evaluation(prompt)
        return self._parse_evaluation(response)

    def _create_evaluation_prompt(self, press_kit, criterion, readability_scores):
        return f"""
        Evaluate the following press kit content for {criterion}.
        Consider these readability metrics:

        Press Release Readability:
        - Flesch Reading Ease: {readability_scores['press_release']['flesch_reading_ease']}
        - Flesch-Kincaid Grade: {readability_scores['press_release']['flesch_kincaid_grade']}
        
        Content to evaluate:
        Press Release:
        {press_kit['press_release'][:500]}...

        Company Overview:
        {press_kit['company_overview'][:500]}...

        Provide a score out of 10 and detailed feedback.
        Format response as:
        Score: X/10
        Feedback: Your detailed feedback here
        """

    def _get_evaluation(self, prompt):
        try:
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return response.json()[0]['generated_text']
            else:
                raise Exception(f"API Error: {response.text}")

        except Exception as e:
            print(f"Error in evaluation: {str(e)}")
            raise

    def _parse_evaluation(self, response):
        try:
            lines = response.split('\n')
            score_line = next(line for line in lines if line.startswith('Score:'))
            score = float(score_line.split(':')[1].strip().split('/')[0])
            feedback = '\n'.join(line for line in lines if line.startswith('Feedback:')).replace('Feedback:', '').strip()
            return score, feedback
        except Exception as e:
            print(f"Error parsing evaluation: {str(e)}")
            return 5.0, "Error parsing evaluation response"

    def generate_recommendations(self, feedback, readability_scores):
        recommendations = []

        # Add readability recommendations
        for section, scores in readability_scores.items():
            flesch_score = scores['flesch_reading_ease']
            if flesch_score < 60:
                recommendations.append(f"Improve readability in {section}: Current Flesch score is {flesch_score:.1f}. Consider using simpler language.")
            elif flesch_score > 80:
                recommendations.append(f"Consider more professional language in {section}: Current Flesch score is {flesch_score:.1f}.")

        # Add content recommendations from feedback
        for criterion, feedback_text in feedback.items():
            if 'improve' in feedback_text.lower() or 'consider' in feedback_text.lower():
                recommendations.append(f"{criterion.replace('_', ' ').title()}: {feedback_text}")

        return recommendations