import os
from dotenv import load_dotenv
from src.data_collector import DataCollector
from src.content_generator import ContentGenerator
from src.quality_reviewer import QualityReviewer
import json
from datetime import datetime

class PressAgent:
    def __init__(self):
        load_dotenv()
        self.data_collector = DataCollector()
        self.content_generator = ContentGenerator()
        self.quality_reviewer = QualityReviewer()

    def run(self):
        try:
            self.display_welcome_message()
            
            # Step 1: Data Collection
            data = self.collect_data()
            if not data:
                return
            
            # Step 2: Content Generation
            press_kit = self.generate_content(data)
            if not press_kit:
                return
            
            # Step 3: Quality Review
            review_result = self.review_content(press_kit)
            if not review_result:
                return
            
            # Step 4: Save and Export
            self.save_and_export(press_kit, review_result, data)

        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please try again or contact support if the problem persists.")

    def display_welcome_message(self):
        print("\n" + "="*50)
        print("Welcome to PressAgent - Press Kit Generator")
        print("="*50)
        print("\nThis tool will help you create a professional press kit in 4 steps:")
        print("1. Information Collection")
        print("2. Content Generation")
        print("3. Quality Review")
        print("4. Export and Save")
        print("\nLet's get started!")
        input("\nPress Enter to continue...")

    def collect_data(self):
        print("\n=== Step 1: Information Collection ===")
        
        company_info = self.data_collector.collect_company_info()
        
        print("\nPlease verify the collected information:")
        print(json.dumps(company_info, indent=2, ensure_ascii=False))
        
        if not self.confirm_input("Is this information correct?"):
            if not self.confirm_input("Would you like to start over?"):
                return None
            return self.collect_data()
        
        supp_data = self.data_collector.collect_supplementary_data(company_info['name'])
        
        if not supp_data:
            print("\n⚠️ Warning: Could not collect supplementary data.")
            if not self.confirm_input("Would you like to continue without supplementary data?"):
                return None
        
        return {
            'company_info': company_info,
            'supplementary_data': supp_data
        }

    def generate_content(self, data):
        print("\n=== Step 2: Content Generation ===")
        print("Generating press kit content...")
        
        try:
            press_kit = self.content_generator.generate_press_kit(
                data['company_info'],
                data['supplementary_data']
            )
            
            self.preview_content(press_kit)
            
            if not self.confirm_input("Are you satisfied with the generated content?"):
                if self.confirm_input("Would you like to regenerate the content?"):
                    return self.generate_content(data)
                return None
            
            return press_kit
            
        except Exception as e:
            print(f"\n❌ Error generating content: {str(e)}")
            return None

    def review_content(self, press_kit):
        print("\n=== Step 3: Quality Review ===")
        print("Analyzing press kit quality...")
        
        try:
            review_result = self.quality_reviewer.review_press_kit(press_kit)
            self.display_review_results(review_result)
            
            if not self.confirm_input("Would you like to proceed with these results?"):
                if self.confirm_input("Would you like to regenerate the content?"):
                    return self.generate_content(press_kit)
                return None
            
            return review_result
            
        except Exception as e:
            print(f"\n❌ Error during quality review: {str(e)}")
            return None

    def save_and_export(self, press_kit, review_result, original_data):
        print("\n=== Step 4: Save and Export ===")
        
        try:
            # Create timestamp and sanitize company name for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            company_name = original_data['company_info']['name'].replace(" ", "_")
            
            # Ensure output directory exists
            os.makedirs('output', exist_ok=True)

            # Prepare sanitized data for JSON
            sanitized_data = {
                'press_kit': press_kit,
                'review_result': {
                    'scores': review_result['scores'],
                    'feedback': review_result['feedback'],
                    'overall_score': review_result['overall_score'],
                    'recommendations': review_result['recommendations'],
                    'readability_analysis': {
                        k: {mk: str(mv) for mk, mv in v.items()}
                        for k, v in review_result['readability_analysis'].items()
                    }
                },
                'original_data': original_data,
                'generated_at': timestamp
            }

            # Save JSON version
            json_filename = f"output/press_kit_{company_name}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(sanitized_data, f, ensure_ascii=False, indent=2)

            # Save text version
            text_filename = f"output/press_kit_{company_name}_{timestamp}.txt"
            self.save_text_version(press_kit, review_result, text_filename)
            
            print(f"\n✅ Press kit saved successfully!")
            print(f"📄 JSON file: {json_filename}")
            print(f"📄 Text file: {text_filename}")
            
        except Exception as e:
            print(f"\n❌ Error saving files: {str(e)}")

    def preview_content(self, press_kit):
        print("\n=== Content Preview ===")
        
        print("\nPress Release Preview:")
        print("-" * 40)
        print(press_kit['press_release'][:300] + "...")
        
        print("\nCompany Overview Preview:")
        print("-" * 40)
        print(press_kit['company_overview'][:300] + "...")
        
        print("\nAlso generated:")
        print("- PR Message")
        print("- Email Draft")
        print("\nFull content will be available in the exported files.")

    def display_review_results(self, review_result):
        print("\n=== Quality Review Results ===")
        
        print(f"\nOverall Score: {review_result['overall_score']:.1f}/10")
        
        print("\nDetailed Scores:")
        for criterion, score in review_result['scores'].items():
            print(f"- {criterion.replace('_', ' ').title()}: {score}/10")
        
        print("\nRecommendations:")
        for rec in review_result['recommendations']:
            print(f"- {rec}")

    def save_text_version(self, press_kit, review_result, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write press kit content
                f.write("=== PRESS KIT ===\n\n")
                
                for section, content in press_kit.items():
                    f.write(f"=== {section.upper()} ===\n")
                    f.write(content + "\n\n")
                
                # Write review results
                f.write("=== QUALITY REVIEW ===\n")
                f.write(f"Overall Score: {review_result['overall_score']:.1f}/10\n\n")
                
                f.write("Detailed Scores:\n")
                for criterion, score in review_result['scores'].items():
                    f.write(f"- {criterion.replace('_', ' ').title()}: {score}/10\n")
                
                f.write("\nRecommendations:\n")
                for rec in review_result['recommendations']:
                    f.write(f"- {rec}\n")
                
                # Write readability analysis
                f.write("\nReadability Analysis:\n")
                for section, scores in review_result['readability_analysis'].items():
                    f.write(f"\n{section.replace('_', ' ').title()}:\n")
                    for metric, value in scores.items():
                        f.write(f"- {metric.replace('_', ' ').title()}: {value}\n")
        
        except Exception as e:
            print(f"\n❌ Error saving text file: {str(e)}")
            raise

    def confirm_input(self, message):
        return input(f"\n{message} (y/n): ").lower().strip() == 'y'

if __name__ == "__main__":
    agent = PressAgent()
    agent.run()