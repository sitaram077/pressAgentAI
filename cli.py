import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
import json
import os
from main import PressAgent

app = typer.Typer()
console = Console()

@app.command()
def main():
    """Main function to run the press kit generator"""
    try:
        # Initialize PressAgent
        press_agent = PressAgent()
        
        # Display welcome message
        display_welcome()
        
        # Collect information with enhanced display
        console.print("\n[bold green]=== Step 1: Information Collection ===[/bold green]")
        data = collect_information(press_agent)
        if not data:
            return

        # Generate content
        console.print("\n[bold green]=== Step 2: Content Generation ===[/bold green]")
        press_kit = generate_content(press_agent, data)
        if not press_kit:
            return

        # Review content
        console.print("\n[bold green]=== Step 3: Quality Review ===[/bold green]")
        review_result = review_content(press_agent, press_kit)
        if not review_result:
            return

        # Export content
        console.print("\n[bold green]=== Step 4: Export ===[/bold green]")
        export_content(press_kit, review_result, data)

    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

def display_welcome():
    """Display enhanced welcome message"""
    welcome_text = """
    [bold cyan]PressAgent - Professional Press Kit Generator[/bold cyan]
    
    Generate comprehensive press kits with:
    ✨ Company Information
    📰 News Articles
    📊 Market Analysis
    📝 Quality Review
    """
    console.print(Panel(welcome_text, subtitle="v1.0"))

def collect_information(press_agent):
    """Collect information with enhanced display"""
    try:
        # Use Rich's Prompt for better input handling
        company_info = {
            'name': Prompt.ask("[cyan]Company Name"),
            'industry': Prompt.ask("[cyan]Industry"),
            'flagship_products': Prompt.ask("[cyan]Flagship Products/Services (comma-separated)").split(','),
            'achievements': Prompt.ask("[cyan]Major Achievements (comma-separated)").split(','),
            'brand_attributes': Prompt.ask("[cyan]Brand Attributes (comma-separated)").split(','),
            'year_founded': Prompt.ask("[cyan]Year Founded"),
            'company_size': Prompt.ask("[cyan]Company Size")
        }

        # Press release details
        console.print("\n[yellow]Press Release Details[/yellow]")
        press_release_info = {
            'topic': Prompt.ask("[cyan]Press Release Topic"),
            'target_media': Prompt.ask("[cyan]Target Media"),
            'target_audience': Prompt.ask("[cyan]Target Audience"),
            'tone': Prompt.ask("[cyan]Desired Tone (professional/casual/formal)"),
            'key_message': Prompt.ask("[cyan]Key Message"),
            'call_to_action': Prompt.ask("[cyan]Call to Action")
        }

        combined_info = {**company_info, **press_release_info}

        # Display collected information
        console.print("\n[yellow]Collected Information:[/yellow]")
        console.print(json.dumps(combined_info, indent=2))

        if not Prompt.ask("\nIs this information correct?", choices=["y", "n"]) == "y":
            return None

        # Collect supplementary data
        with console.status("[cyan]Collecting news articles..."):
            supp_data = press_agent.data_collector.collect_supplementary_data(company_info['name'])

        return {
            'company_info': combined_info,
            'supplementary_data': supp_data
        }

    except Exception as e:
        console.print(f"[bold red]Error collecting information: {str(e)}[/bold red]")
        return None

def generate_content(press_agent, data):
    """Generate content with enhanced display"""
    try:
        with console.status("[cyan]Generating press kit content..."):
            press_kit = press_agent.content_generator.generate_press_kit(
                data['company_info'],
                data['supplementary_data']
            )

        # Preview content
        console.print("\n[yellow]Content Preview:[/yellow]")
        console.print(Panel(press_kit['press_release'][:300] + "..."))

        if not Prompt.ask("\nAre you satisfied with the generated content?", choices=["y", "n"]) == "y":
            return None

        return press_kit

    except Exception as e:
        console.print(f"[bold red]Error generating content: {str(e)}[/bold red]")
        return None

def review_content(press_agent, press_kit):
    """Review content with enhanced display"""
    try:
        with console.status("[cyan]Analyzing press kit quality..."):
            review_result = press_agent.quality_reviewer.review_press_kit(press_kit)

        # Display review results
        console.print("\n[yellow]Quality Review Results:[/yellow]")
        table = Table()
        table.add_column("Metric")
        table.add_column("Score")
        
        for criterion, score in review_result['scores'].items():
            table.add_row(criterion.replace('_', ' ').title(), f"{score:.1f}/10")
        
        console.print(table)

        if not Prompt.ask("\nWould you like to proceed with these results?", choices=["y", "n"]) == "y":
            return None

        return review_result

    except Exception as e:
        console.print(f"[bold red]Error reviewing content: {str(e)}[/bold red]")
        return None

def export_content(press_kit, review_result, data):
    """Export content with enhanced display"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name = data['company_info']['name'].replace(" ", "_")
        base_path = f"output/press_kit_{company_name}_{timestamp}"

        os.makedirs('output', exist_ok=True)

        # Export files
        with console.status("[cyan]Exporting files..."):
            # JSON export
            json_path = f"{base_path}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'press_kit': press_kit,
                    'review_result': review_result,
                    'data': data
                }, f, ensure_ascii=False, indent=2)

            # Text export
            text_path = f"{base_path}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write("=== PRESS KIT ===\n\n")
                for section, content in press_kit.items():
                    f.write(f"=== {section.upper()} ===\n")
                    f.write(content + "\n\n")

        # Display export summary
        table = Table(title="Exported Files")
        table.add_column("Format", style="cyan")
        table.add_column("Path", style="green")
        table.add_row("JSON", json_path)
        table.add_row("Text", text_path)
        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error during export: {str(e)}[/bold red]")

if __name__ == "__main__":
    app()