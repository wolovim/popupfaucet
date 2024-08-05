import click
from rich.console import Console
from rich.prompt import Prompt
from time import sleep
from InquirerPy import prompt
import requests
from eth_account import Account

SERVER_URL = "http://localhost:5000"

console = Console()
NETWORK_CHOICES = ["Sepolia", "OP Sepolia", "Base Sepolia"]


@click.group()
def popupfaucet():
    """popupfaucet CLI"""
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
            response = requests.get(f"{SERVER_URL}/status", params={"event_code": event_code, "network": network})
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
    with console.status(
        f"Checking availability of [bold]{event_code}[/bold] on [bold]{network}[/bold] network...",
        spinner="moon",
    ):
        response = requests.get(f"{SERVER_URL}/availability", params={"event_code": event_code, "network": network})
        is_available = response.json().get("is_available")
        # Simulate
        sleep(2)
        if not is_available:
            console.print(
                f"[bold red]❌ [Error] Event code '{event_code}' is not available on the {network} network.[/bold red]"
            )
            return
        else:
            console.print(
                f"🤝 Great! [bold]'{event_code}'[/bold] is an available event code on the [bold]{network}[/bold] network!"
            )

    acct = Account.create()
    console.print(
        f"[magenta]🔗 Send testnet ether to [bold]{acct.address}[/bold].\nPress [bold]enter[/bold] once sent.[/magenta]"
    )
    input()

    with console.status(
        "[bold yellow]Waiting for confirmation...[/bold yellow]", spinner="moon"
    ):
        payload = {"pk": acct.key.hex()}
        waiting_for_confirmation = True
        while waiting_for_confirmation:
            response = requests.post(f"{SERVER_URL}/seeder-funded", json=payload)
            if response.status_code == 200:
                sleep(2)
                console.print(
                    f"[bold green]✅ Account funded![/bold green]"
                )
                waiting_for_confirmation = False
            else:
                console.print(
                    f"[bold red]❌ [Error] Haven't received it yet![/bold red]"
                )

    with console.status(
        "[bold yellow]Deploying faucet...[/bold yellow]", spinner="moon"
    ):
        payload = {"event_code": event_code, "pk": acct.key.hex()}
        response = requests.post(f"{SERVER_URL}/create-faucet", json=payload)
        if response.status_code == 200:
            sleep(2)
            console.print(
                f"[bold green]🎉 Congrats! Your popupfaucet is live on the {network} testnet![/bold green]\n\nTestnet tokens are available to claim via:\n\n`pipx install popupfaucet`\n`popupfaucet claim`"
            )
        else:
            console.print(response)
            console.print(
                f"[bold red]❌ [Error] {response}[/bold red]"
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

    with console.status(f"Checking faucet availability...", spinner="moon"):
        # Simulate
        sleep(3)
        console.print(f"[bold green]✅ Faucet has funds.[/bold green]")

    with console.status(f"Sending transaction...", spinner="moon"):
        payload = {"event_code": event_code, "address": address}
        response = requests.post(f"{SERVER_URL}/claim-faucet", json=payload)
        if response.status_code == 200:
            # Simulate
            sleep(4)
            console.print("[bold green]🎉 Congrats! Check your account![/bold green]")
        else:
            console.print(
                f"[bold red]❌ [Error] {response.status_code}: {response.reason}[/bold red]"
            )


if __name__ == "__main__":
    popupfaucet()
