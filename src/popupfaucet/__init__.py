import click
from rich.console import Console
from rich.prompt import Prompt
import time

console = Console()

@click.group()
def popupfaucet():
    """Popup Faucet CLI"""
    pass

@popupfaucet.command()
@click.argument('eventcode', required=False)
def status(eventcode):
    """Check the status of an event by its event code."""
    if not eventcode:
        console.print("[bold red]❌ Invalid: Event code is required.[/bold red]")
    else:
        # Simulate
        remaining_eth = 0.456
        console.print(f"[bold green]💰 {remaining_eth} eth remaining[/bold green]")

@popupfaucet.command()
@click.option('--network', type=click.Choice(['OP Sepolia', 'Base Sepolia'], case_sensitive=False), prompt=True, help="Select the network.")
def create(network):
    """Create a new popup faucet event. Prompts for event code and confirmation of token sending."""
    event_code = Prompt.ask("[bold yellow]Event code?[/bold yellow]")
    if not event_code:
        console.print("[bold red]❌ Invalid: Event code is required.[/bold red]")
    else:
        with console.status(f"Checking availability of [bold]{event_code}[/bold] on [bold]{network}[/bold] network...", spinner="moon"):
            # Simulate
            time.sleep(2)

        console.print(f"🤝 Great! [bold]'{event_code}'[/bold] is an available event code on the [bold]{network}[/bold] network!")
        console.print("[magenta]🔗 Send tokens to [bold]0xaBc123[/bold]. Press [bold]enter[/bold] once sent.[/magenta]")
        input()

        with console.status("[bold yellow]Waiting for confirmation...[/bold yellow]", spinner="moon"):
            # Simulate
            time.sleep(2)

        console.print(f"[bold green]🎉 Congrats! Your popupfaucet is live on the {network} testnet![/bold green]\n\nTestnet tokens are available to claim via:\n\n`pipx install popupfaucet`\n`popupfaucet claim {event_code}`")

@popupfaucet.command()
@click.argument('eventcode', required=False)
def claim(eventcode):
    """Claim tokens from an event by its event code."""
    if not eventcode:
        console.print("[bold red]❌ Invalid: Event code is required.[/bold red]")
    else:
        address = Prompt.ask("[bold yellow]🔗 Address to receive testnet ether?[/bold yellow]")
        if not address:
            console.print("[bold red]❌ Invalid: Address is required.[/bold red]")
        else:
            # Simulate
            with console.status(f"Sending transaction...", spinner="moon"):
                time.sleep(4)
            console.print("[bold green]🎉 Congrats! Check your account![/bold green]")

if __name__ == '__main__':
    popupfaucet()
