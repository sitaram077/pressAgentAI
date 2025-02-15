import requests
from dotenv import load_dotenv
import os
import json

class ContentGenerator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        # Using Mistral model
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _validate_company_info(self, company_info):
        """Validate and set default values for company information"""
        default_info = {
            'name': '',
            'industry': '',
            'flagship_products': [],
            'achievements': [],
            'brand_attributes': [],
            'topic': '',
            'target_audience': '',
            'tone': 'professional',
            'key_message': '',
            'call_to_action': ''
        }
        
        validated_info = default_info.copy()
        validated_info.update(company_info)
        
        if isinstance(validated_info['flagship_products'], str):
            validated_info['flagship_products'] = [validated_info['flagship_products']]
        if isinstance(validated_info['achievements'], str):
            validated_info['achievements'] = [validated_info['achievements']]
        if isinstance(validated_info['brand_attributes'], str):
            validated_info['brand_attributes'] = [validated_info['brand_attributes']]
            
        return validated_info

    def _generate_content(self, prompt):
        try:
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {
                    "max_length": 1000,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            
            if response.status_code == 200:
                return response.json()[0]['generated_text']
            else:
                print(f"Error from Hugging Face API: {response.text}")
                raise Exception("Failed to generate content")
                
        except Exception as e:
            print(f"Error in content generation: {str(e)}")
            raise

    def generate_press_kit(self, company_info, supplementary_data):
        try:
            company_info = self._validate_company_info(company_info)
            
            return {
                'press_release': self.generate_press_release(company_info, supplementary_data),
                'company_overview': self.generate_company_overview(company_info),
                'pr_message': self.generate_pr_message(company_info),
                'email_draft': self.generate_email_draft(company_info)
            }
        except Exception as e:
            print(f"Error in generate_press_kit: {str(e)}")
            raise

    def generate_press_release(self, company_info, supplementary_data):
        prompt = f"""
        Act as a professional PR writer and create a press release with the following information:
        
        Company: {company_info['name']}
        Industry: {company_info['industry']}
        Products/Services: {', '.join(company_info['flagship_products'])}
        Achievements: {', '.join(company_info['achievements'])}
        Topic: {company_info.get('topic', '')}
        
        Format the press release with:
        1. Headline
        2. Dateline
        3. Introduction
        4. Body with details
        5. Quotes
        6. Contact information
        
        Make it professional and newsworthy.
        """
        return self._generate_content(prompt)

    def generate_company_overview(self, company_info):
        prompt = f"""
        Create a comprehensive company overview with these details:
        
        Company: {company_info['name']}
        Industry: {company_info['industry']}
        Products/Services: {', '.join(company_info['flagship_products'])}
        Achievements: {', '.join(company_info['achievements'])}
        Brand Values: {', '.join(company_info['brand_attributes'])}
        
        Include:
        1. Company background
        2. Industry position
        3. Key products/services description
        4. Major achievements
        5. Brand values and mission
        
        Make it professional and engaging.
        """
        return self._generate_content(prompt)

    def generate_pr_message(self, company_info):
        prompt = f"""
        Create a concise PR message with these details:
        
        Company: {company_info['name']}
        Topic: {company_info.get('topic', '')}
        Target Audience: {company_info.get('target_audience', '')}
        Tone: {company_info.get('tone', 'professional')}
        Key Message: {company_info.get('key_message', '')}
        
        Make it impactful and suitable for the target audience.
        """
        return self._generate_content(prompt)

    def generate_email_draft(self, company_info):
        prompt = f"""
        Create a media outreach email with these details:
        
        Company: {company_info['name']}
        Topic: {company_info.get('topic', '')}
        Call to Action: {company_info.get('call_to_action', '')}
        
        Include:
        1. Compelling subject line
        2. Brief introduction
        3. Key points about the news
        4. Clear call to action
        
        Make it professional and engaging for media recipients.
        """
        return self._generate_content(prompt)