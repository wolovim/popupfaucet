import click
from rich.console import Console
from rich.prompt import Prompt
from time import sleep
from InquirerPy import prompt
import requests

SERVER_URL = "http://localhost:5000"

console = Console()
NETWORK_CHOICES = ["Sepolia", "OP Sepolia", "Base Sepolia"]


@click.group()
def popupfaucet():
    """Popup Faucet CLI"""
    pass


@popupfaucet.command()
def status():
    """Check the status of an event by its event code."""
    questions = [
        {
            "type": "list",
            "name": "network",
            "message": "Select the network:",
            "choices": NETWORK_CHOICES,
        },
        {
            "type": "input",
            "name": "event_code",
            "message": "Event code?",
            "validate": lambda x: x != "",
        },
    ]
    answers = prompt(questions)
    network = answers["network"]
    event_code = answers["event_code"]

    with console.status(
        f"Checking status of [bold]{event_code}[/bold] on [bold]{network}[/bold] testnet...",
        spinner="moon",
    ):
        try:
            response = requests.get(f"{SERVER_URL}/status", params={"key": event_code})
            sleep(3)
            response.raise_for_status()  # Raise an exception for HTTP errors
            remaining_eth = response.json().get("available_ether")
            console.print(
                f"[green]💰 [bold]{remaining_eth}[/bold] eth remaining in [bold]{event_code}[/bold] faucet on [bold]{network}[/bold].[/green]"
            )
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]❌ Error: {str(e)}.[/bold red]")


@popupfaucet.command()
def create():
    """Create a new popup faucet event. Prompts for event code and confirmation of token sending."""
    questions = [
        {
            "type": "list",
            "name": "network",
            "message": "Select the network:",
            "choices": NETWORK_CHOICES,
        },
        {
            "type": "input",
            "name": "event_code",
            "message": "Event code?",
            "validate": lambda x: x != "",
        },
    ]
    answers = prompt(questions)
    network = answers["network"]
    event_code = answers["event_code"]
    if not event_code:
        console.print("[bold red]❌ Invalid: Event code is required.[/bold red]")
    else:
        with console.status(
            f"Checking availability of [bold]{event_code}[/bold] on [bold]{network}[/bold] network...",
            spinner="moon",
        ):
            # Simulate
            sleep(2)

        console.print(
            f"🤝 Great! [bold]'{event_code}'[/bold] is an available event code on the [bold]{network}[/bold] network!"
        )
        console.print(
            "[magenta]🔗 Send tokens to [bold]0xaBc123[/bold]. Press [bold]enter[/bold] once sent.[/magenta]"
        )
        input()

        with console.status(
            "[bold yellow]Waiting for confirmation...[/bold yellow]", spinner="moon"
        ):
            # Simulate
            sleep(2)

        console.print(
            f"[bold green]🎉 Congrats! Your popupfaucet is live on the {network} testnet![/bold green]\n\nTestnet tokens are available to claim via:\n\n`pipx install popupfaucet`\n`popupfaucet claim {event_code}`"
        )


@popupfaucet.command()
def claim():
    """Claim tokens from an event by its event code."""
    questions = [
        {
            "type": "list",
            "name": "network",
            "message": "Select the network:",
            "choices": NETWORK_CHOICES,
        },
        {
            "type": "input",
            "name": "event_code",
            "message": "Event code?",
            "validate": lambda x: x != "",
        },
        {
            "type": "input",
            "name": "address",
            "message": "Address to receive testnet ether?",
            "validate": lambda x: x != "",
        },
    ]
    answers = prompt(questions)
    network = answers["network"]
    event_code = answers["event_code"]
    address = answers["address"]
    if not address:
        console.print("[bold red]❌ Invalid: Address is required.[/bold red]")
    else:
        with console.status(f"Checking faucet availability...", spinner="moon"):
            # Simulate
            sleep(3)
        console.print(f"[bold green]✅ Faucet has funds.[/bold green]")

        with console.status(f"Sending transaction...", spinner="moon"):
            # Simulate
            sleep(4)
        console.print("[bold green]🎉 Congrats! Check your account![/bold green]")


if __name__ == "__main__":
    popupfaucet()
