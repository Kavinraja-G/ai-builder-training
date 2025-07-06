import os
import sys
import re
from typing import List, Optional
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

from agents.research_agent import ResearchAgent
from utils.logger import logger, setup_logger
from ira_cli.config import settings

console = Console()


def clean_response(response):
    """Clean and format the agent response."""
    if isinstance(response, dict) and "output" in response:
        answer = response["output"]
    else:
        answer = str(response)

    # Remove markdown code blocks if present
    answer = re.sub(r'^```\w*\n', '', answer)
    answer = re.sub(r'\n```$', '', answer)

    return answer.strip()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--log-file', help='Log file path')
def cli(verbose: bool, log_file: Optional[str]):
    """Internal Research Agent - AI-powered document research and analysis."""
    # Set up logging - quiet by default, verbose only when requested
    log_level = "DEBUG" if verbose else "ERROR"
    setup_logger(level=log_level, log_file=log_file)

    if verbose:
        console.print("[yellow]Verbose logging enabled[/yellow]")


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force recreate vector store')
def init(force: bool):
    """Initialize the research agent and vector store."""
    try:
        console.print("[bold blue]Initializing Research Agent...[/bold blue]")

        agent = ResearchAgent()
        agent.initialize_agent(force_recreate=force)

        # Get vector store info
        info = agent.get_vector_store_info()

        table = Table(title="Vector Store Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        for key, value in info.items():
            table.add_row(key, str(value))

        console.print(table)
        console.print("[bold green]✓ Research Agent initialized successfully![/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error initializing agent: {e}[/bold red]")
        logger.error(f"Initialization error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('question', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
def query(question: Optional[str], interactive: bool):
    """Query the research agent with a question."""
    try:
        agent = ResearchAgent()
        agent.initialize_agent()

        if interactive:
            run_interactive_mode(agent)
        elif question:
            response = agent.query(question)
            answer = clean_response(response)
            console.print(Panel(answer, title="[bold blue]Answer[/bold blue]"))
        else:
            console.print("[red]Please provide a question or use --interactive mode[/red]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        logger.error(f"Query error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('file_paths', nargs=-1, required=True)
def add_docs(file_paths: List[str]):
    """Add new documents to the vector store."""
    try:
        console.print("[bold blue]Adding documents to vector store...[/bold blue]")

        agent = ResearchAgent()
        agent.initialize_agent()
        agent.add_documents(file_paths)

        console.print(f"[bold green]✓ Successfully added {len(file_paths)} document(s)[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error adding documents: {e}[/bold red]")
        logger.error(f"Add documents error: {e}")
        sys.exit(1)


@cli.command()
def info():
    """Show information about the current setup."""
    try:
        agent = ResearchAgent()
        agent.initialize_agent()

        info = agent.get_vector_store_info()

        table = Table(title="System Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        # Add configuration info
        table.add_row("Model", settings.model_name)
        table.add_row("Temperature", str(settings.temperature))
        table.add_row("Chunk Size", str(settings.chunk_size))
        table.add_row("Chunk Overlap", str(settings.chunk_overlap))
        table.add_row("Documents Path", settings.docs_path)
        table.add_row("Vector Store Path", settings.vector_store_path)

        # Add vector store info
        for key, value in info.items():
            table.add_row(key, str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error getting info: {e}[/bold red]")
        logger.error(f"Info error: {e}")
        sys.exit(1)


@cli.command()
@click.argument('query_text')
@click.option('--limit', '-k', default=4, help='Number of results to return')
def search(query_text: str, limit: int):
    """Search for relevant documents in the vector store."""
    try:
        agent = ResearchAgent()
        agent.initialize_agent()

        results = agent.search_documents(query_text, k=limit)

        if results:
            console.print(f"[bold blue]Found {len(results)} relevant documents:[/bold blue]")
            for i, result in enumerate(results, 1):
                console.print(Panel(
                    result[:500] + "..." if len(result) > 500 else result,
                    title=f"[bold cyan]Document {i}[/bold cyan]"
                ))
        else:
            console.print("[yellow]No relevant documents found.[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error searching documents: {e}[/bold red]")
        logger.error(f"Search error: {e}")
        sys.exit(1)


def run_interactive_mode(agent: ResearchAgent):
    """Run the agent in interactive mode."""
    console.print(Panel(
        "[bold blue]Interactive Research Agent[/bold blue]\n"
        "Type your questions and press Enter. Type 'quit' or 'exit' to stop.",
        title="Welcome"
    ))

    while True:
        try:
            question = Prompt.ask("\n[bold cyan]Question[/bold cyan]")

            if question.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not question.strip():
                continue

            console.print("[dim]Processing...[/dim]")
            response = agent.query(question)
            answer = clean_response(response)
            console.print(Panel(answer, title="[bold blue]Answer[/bold blue]"))

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            logger.error(f"Interactive mode error: {e}")


@cli.command()
def setup():
    """Interactive setup for API keys and configuration."""
    console.print(Panel(
        "[bold blue]Internal Research Agent Setup[/bold blue]\n"
        "This will help you configure the required API keys.",
        title="Setup"
    ))

    # Check for existing .env file
    env_file = Path(".env")
    if env_file.exists():
        if not Confirm.ask("A .env file already exists. Overwrite it?"):
            console.print("[yellow]Setup cancelled.[/yellow]")
            return

    # Get API keys
    gemini_key = Prompt.ask("Enter your Google Gemini API Key", password=True)
    tavily_key = Prompt.ask("Enter your Tavily API Key", password=True)

    # Create .env file
    env_content = f"""# Internal Research Agent Configuration
GEMINI_API_KEY={gemini_key}
TAVILY_API_KEY={tavily_key}

# Optional Configuration
MODEL_NAME=gemini-2.0-flash
TEMPERATURE=0.0
MAX_RETRIES=2
CHUNK_SIZE=500
CHUNK_OVERLAP=100
DOCS_PATH=hr_docs
VECTOR_STORE_PATH=./chroma_db
MAX_SEARCH_RESULTS=5
"""

    try:
        with open(".env", "w") as f:
            f.write(env_content)

        console.print("[bold green]✓ Configuration saved to .env file[/bold green]")
        console.print("[yellow]Note: Make sure to add .env to your .gitignore file[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error saving configuration: {e}[/bold red]")


if __name__ == '__main__':
    cli()