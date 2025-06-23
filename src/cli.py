import click
import pandas as pd
from tabulate import tabulate
from pathlib import Path
from .survey_analyzer import SurveyAnalyzer

analyzer = None
current_subset = None


def get_analyzer():
    global analyzer
    if analyzer is None:
        data_path = Path(__file__).parent.parent / 'data' / 'so_2024_raw.xlsx'
        if not data_path.exists():
            click.echo(f"Error: Data file not found at {data_path}")
            click.echo("Please ensure so_2024_raw.xlsx is in the data/ directory")
            return None
        analyzer = SurveyAnalyzer(str(data_path))
    return analyzer


@click.group()
def cli():
    """Stack Overflow Survey Data Analysis Tool"""
    pass


@cli.command()
@click.option('--limit', '-l', default=20, help='Number of questions to display')
def structure(limit):
    """Display the survey structure (list of questions)"""
    analyzer = get_analyzer()
    if not analyzer:
        return
    
    df = analyzer.display_survey_structure(limit)
    click.echo(f"\nSurvey Structure ({len(analyzer.questions)} total questions):\n")
    click.echo(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    
    if limit < len(analyzer.questions):
        click.echo(f"\nShowing {limit} of {len(analyzer.questions)} questions. Use --limit to see more.")


@cli.command()
@click.argument('keyword')
@click.option('--in-options', '-o', is_flag=True, help='Search in answer options instead of questions')
@click.option('--question', '-q', help='Specific question to search options in')
def search(keyword, in_options, question):
    """Search for specific questions or options"""
    analyzer = get_analyzer()
    if not analyzer:
        return
    
    if in_options:
        if not question:
            click.echo("Error: --question is required when searching in options")
            return
        
        try:
            options = analyzer.search_options(question, keyword)
            click.echo(f"\nOptions matching '{keyword}' in question '{question}':")
            for i, opt in enumerate(options, 1):
                click.echo(f"  {i}. {opt}")
            
            if not options:
                click.echo("  No matching options found.")
        except ValueError as e:
            click.echo(f"Error: {e}")
    else:
        questions = analyzer.search_questions(keyword)
        click.echo(f"\nQuestions matching '{keyword}':")
        for i, q in enumerate(questions, 1):
            q_info = analyzer.questions[q]
            click.echo(f"  {i}. {q}")
            click.echo(f"     Type: {q_info['type']}, Responses: {q_info['response_count']}")
        
        if not questions:
            click.echo("  No matching questions found.")


@cli.command()
@click.argument('question')
@click.argument('option')
@click.option('--save', '-s', is_flag=True, help='Save this subset for future operations')
def subset(question, option, save):
    """Create a subset of respondents based on question+option"""
    global current_subset
    analyzer = get_analyzer()
    if not analyzer:
        return
    
    try:
        subset_df = analyzer.create_subset(question, option)
        subset_size = len(subset_df)
        total_size = len(analyzer.df)
        
        click.echo(f"\nCreated subset: {subset_size} respondents ({subset_size/total_size*100:.1f}% of total)")
        click.echo(f"Filter: {question} = '{option}'")
        
        if save:
            current_subset = subset_df
            click.echo("\nSubset saved for future operations. Use --subset flag in distribution command.")
        
    except ValueError as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument('question')
@click.option('--top', '-t', default=10, help='Number of top options to display')
@click.option('--subset', '-s', is_flag=True, help='Use saved subset instead of full data')
def distribution(question, top, subset):
    """Display distribution of answers for a question"""
    global current_subset
    analyzer = get_analyzer()
    if not analyzer:
        return
    
    if subset and current_subset is None:
        click.echo("Error: No subset saved. Create a subset first using the 'subset' command with --save flag.")
        return
    
    try:
        data_to_use = current_subset if subset else None
        df_dist = analyzer.display_distribution(question, data_to_use, top)
        
        data_desc = "saved subset" if subset else "full dataset"
        total_responses = (data_to_use[question].notna().sum() if subset 
                         else analyzer.df[question].notna().sum())
        
        click.echo(f"\nDistribution for '{question}' ({data_desc}):")
        click.echo(f"Total responses: {total_responses}")
        click.echo(f"Question type: {analyzer.question_types.get(question, 'Unknown')}\n")
        
        click.echo(tabulate(df_dist, headers='keys', tablefmt='grid', showindex=False))
        
    except ValueError as e:
        click.echo(f"Error: {e}")


@cli.command()
def repl():
    """Start interactive REPL mode"""
    analyzer = get_analyzer()
    if not analyzer:
        return
    
    click.echo("\nStack Overflow Survey Analyzer - Interactive Mode")
    click.echo("Type 'help' for available commands, 'exit' to quit\n")
    
    commands = {
        'help': 'Show available commands',
        'structure [limit]': 'Display survey structure',
        'search <keyword>': 'Search questions',
        'search-options <question> <keyword>': 'Search options in a question',
        'subset <question> <option>': 'Create and save subset',
        'dist <question> [top_n]': 'Show distribution',
        'dist-subset <question> [top_n]': 'Show distribution for saved subset',
        'clear-subset': 'Clear saved subset',
        'exit': 'Exit REPL'
    }
    
    global current_subset
    
    while True:
        try:
            cmd = click.prompt('survey>', prompt_suffix=' ')
            
            if cmd.strip() == 'exit':
                break
            
            elif cmd.strip() == 'help':
                click.echo("\nAvailable commands:")
                for cmd_name, desc in commands.items():
                    click.echo(f"  {cmd_name:<30} - {desc}")
            
            elif cmd.startswith('structure'):
                parts = cmd.split()
                limit = int(parts[1]) if len(parts) > 1 else 20
                df = analyzer.display_survey_structure(limit)
                click.echo(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
            
            elif cmd.startswith('search-options'):
                parts = cmd.split(maxsplit=2)
                if len(parts) < 3:
                    click.echo("Usage: search-options <question> <keyword>")
                    continue
                question = parts[1]
                keyword = parts[2]
                options = analyzer.search_options(question, keyword)
                for opt in options:
                    click.echo(f"  - {opt}")
            
            elif cmd.startswith('search'):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    click.echo("Usage: search <keyword>")
                    continue
                keyword = parts[1]
                questions = analyzer.search_questions(keyword)
                for q in questions:
                    click.echo(f"  - {q}")
            
            elif cmd.startswith('subset'):
                parts = cmd.split(maxsplit=2)
                if len(parts) < 3:
                    click.echo("Usage: subset <question> <option>")
                    continue
                question = parts[1]
                option = parts[2]
                current_subset = analyzer.create_subset(question, option)
                click.echo(f"Subset created: {len(current_subset)} respondents")
            
            elif cmd.startswith('dist-subset'):
                if current_subset is None:
                    click.echo("No subset saved. Create one first with 'subset' command.")
                    continue
                parts = cmd.split()
                question = parts[1] if len(parts) > 1 else None
                if not question:
                    click.echo("Usage: dist-subset <question> [top_n]")
                    continue
                top = int(parts[2]) if len(parts) > 2 else 10
                df_dist = analyzer.display_distribution(question, current_subset, top)
                click.echo(tabulate(df_dist, headers='keys', tablefmt='grid', showindex=False))
            
            elif cmd.startswith('dist'):
                parts = cmd.split()
                question = parts[1] if len(parts) > 1 else None
                if not question:
                    click.echo("Usage: dist <question> [top_n]")
                    continue
                top = int(parts[2]) if len(parts) > 2 else 10
                df_dist = analyzer.display_distribution(question, None, top)
                click.echo(tabulate(df_dist, headers='keys', tablefmt='grid', showindex=False))
            
            elif cmd.strip() == 'clear-subset':
                current_subset = None
                click.echo("Subset cleared.")
            
            else:
                click.echo(f"Unknown command: {cmd}. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            click.echo("\nUse 'exit' to quit.")
            continue
        except Exception as e:
            click.echo(f"Error: {e}")
    
    click.echo("\nGoodbye!")


def main():
    cli()


if __name__ == '__main__':
    main()