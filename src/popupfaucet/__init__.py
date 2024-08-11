from time import sleep
import click
from rich.console import Console
from InquirerPy import prompt
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from eth_account import Account
from eth_utils import is_normalized_address

# SERVER_URL = "http://127.0.0.1:5000"
SERVER_URL = "https://popupfaucet-server-tplm.onrender.com"

console = Console()
NETWORK_CHOICES = ["Sepolia", "OP Sepolia", "Base Sepolia"]
BLOCK_EXPLORERS = {
    "Sepolia": "https://eth-sepolia.blockscout.com/tx/",
    "OP Sepolia": "https://optimism-sepolia.blockscout.com/tx/",
    "Base Sepolia": "https://base-sepolia.blockscout.com/tx/",
}

# retry GET requests
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))


@click.group()
def popupfaucet():
    """popupfaucet CLI"""
    pass


@popupfaucet.command()
def status():
    """Check the status of a faucet by its event code."""
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
            response = session.get(
                f"{SERVER_URL}/status",
                params={"event_code": event_code, "network": network},
            )
            event_exists = response.json().get("event_exists")
            if not event_exists:
                console.print(
                    f"[red]🚫 [bold]{event_code}[/bold] is not yet deployed on [bold]{network}[/bold].[/red]"
                )
                return

            remaining_eth = response.json().get("available_ether")
            console.print(
                f"[green]💰 [bold]{remaining_eth}[/bold] eth remaining in [bold]{event_code}[/bold] faucet on [bold]{network}[/bold].[/green]"
            )
        except Exception as e:
            console.print(f"[bold red]❌ Error: {str(e)}.[/bold red]")


@popupfaucet.command()
def create():
    """Create a new popupfaucet. Prompts for event code and confirmation of token sending."""
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
        try:
            response = session.get(
                f"{SERVER_URL}/availability",
                params={"event_code": event_code, "network": network},
            )
            # response.raise_for_status()
            is_available = response.json().get("is_available")
            if not is_available:
                console.print(
                    f"[bold red]❌ [Error] Event code '{event_code}' is not available on the {network} network.[/bold red]"
                )
                return
            else:
                console.print(
                    f"🤝 Great! [bold]'{event_code}'[/bold] is an available event code on the [bold]{network}[/bold] network!"
                )
        except Exception:
            console.print(f"Uh oh, something went wrong! Please try again.")
            return

    acct = Account.create()
    console.print(
        f"[magenta]🔗 Send [bold]{network}[/bold] testnet ether to:\n[bold]{acct.address}[/bold]\n\nA minimum of 0.05 testnet ether is recommended.\nYou may add more (`topup`) after successful creation.\n\nPress [bold]enter[/bold] once sent.[/magenta]"
    )
    input()

    with console.status(
        "[bold yellow]Waiting for confirmation...[/bold yellow]", spinner="moon"
    ):
        payload = {"network": network, "pk": acct.key.hex()}
        waiting_for_confirmation = True
        while waiting_for_confirmation:
            response = requests.post(f"{SERVER_URL}/seeder-funded", json=payload)
            if response.status_code == 200:
                console.print(f"[bold green]✅ Account funded![/bold green]")
                waiting_for_confirmation = False
            else:
                console.print(
                    f"[bold red]❌ [Error] Haven't received it yet![/bold red]"
                )
                sleep(5)

    with console.status(
        "[bold yellow]Deploying faucet...[/bold yellow]", spinner="moon"
    ):
        payload = {"event_code": event_code, "network": network, "pk": acct.key.hex()}
        response = requests.post(f"{SERVER_URL}/create-faucet", json=payload)
        if response.status_code == 200:
            console.print(
                f"[bold green]🎉 Congrats! Your popupfaucet is live![/bold green]\n\n"
                f"🔗 View the transaction:\n[bold]{BLOCK_EXPLORERS[network] + response.json()['tx_hash']}[/bold]\n\n"
                "Testnet tokens are available via the `popupfaucet drip` command.\n"
                f"You can share your event code, [bold]{event_code}[/bold] (on [bold]{network}[/bold])"
            )
        else:
            console.print(f"[bold red]❌ [Error] {response}[/bold red]")


@popupfaucet.command()
def topup():
    """Add funds to a popupfaucet. Prompts for an event code and confirmation of token sending."""
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
    acct = Account.create()

    with console.status(
        f"Checking availability of [bold]{event_code}[/bold] on [bold]{network}[/bold] network...",
        spinner="moon",
    ):
        try:
            response = session.get(
                f"{SERVER_URL}/status",
                params={"event_code": event_code, "network": network},
            )

            # response.raise_for_status()
            faucet_exists = response.json().get("event_exists")
            if not faucet_exists:
                console.print(
                    f"[bold red]❌ [Error] Event code '{event_code}' does not exist on the {network} network.[/bold red]"
                )
                return
            else:
                console.print(
                    f"🤝 Great! [bold]'{event_code}'[/bold] was found on the [bold]{network}[/bold] network!"
                )
        except Exception:
            console.print(f"Uh oh, something went wrong! Please try again.")
            return

    console.print(
        f"[magenta]🔗 Send [bold]{network}[/bold] testnet ether to:\n[bold]{acct.address}[/bold]\nA minimum of 0.005 testnet ether is recommended.\nPress [bold]enter[/bold] once sent.[/magenta]"
    )
    input()

    with console.status(
        "[bold yellow]Waiting for confirmation...[/bold yellow]", spinner="moon"
    ):
        payload = {"pk": acct.key.hex(), "network": network}
        waiting_for_confirmation = True
        while waiting_for_confirmation:
            response = requests.post(f"{SERVER_URL}/seeder-funded", json=payload)
            if response.status_code == 200:
                console.print(f"[bold green]✅ Account funded![/bold green]")
                waiting_for_confirmation = False
            else:
                console.print(
                    f"[bold red]❌ [Error] Haven't received it yet![/bold red]"
                )
                sleep(5)

    with console.status(
        "[bold yellow]Sending funds to faucet...[/bold yellow]", spinner="moon"
    ):
        payload = {"event_code": event_code, "network": network, "pk": acct.key.hex()}
        response = requests.post(f"{SERVER_URL}/top-up", json=payload)
        if response.status_code == 200:
            console.print(
                f"[bold green]🎉 Congrats! Your popupfaucet has been topped up![/bold green]\n\n"
                f"[bold green]🔗 View the transaction: {BLOCK_EXPLORERS[network] + response.json()["tx_hash"]}[/bold green]\n\n"
                "Testnet tokens are available to drip via:\n\n`pipx install popupfaucet`\n`popupfaucet drip`"
            )
        else:
            console.print(response)
            console.print(f"[bold red]❌ [Error] {response}[/bold red]")


@popupfaucet.command()
def drip():
    """Claim tokens from a faucet by its event code."""
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
            "validate": lambda x: is_normalized_address(x.lower()),
        },
    ]
    answers = prompt(questions)
    network = answers["network"]
    event_code = answers["event_code"]
    address = answers["address"]

    with console.status(f"Checking faucet availability...", spinner="moon"):
        response = session.get(
            f"{SERVER_URL}/status",
            params={"event_code": event_code, "network": network},
        )
        available_ether = response.json().get("available_ether")
        if available_ether == 0:
            console.print(
                f"[red]❌ No funds found in faucet [bold]'{event_code}'[/bold] on {network}.[/red]"
            )
            return
        console.print(f"[bold green]✅ Faucet has funds.[/bold green]")

    with console.status(f"Sending transaction...", spinner="moon"):
        payload = {"event_code": event_code, "network": network, "address": address}
        response = requests.post(f"{SERVER_URL}/claim-faucet", json=payload)
        if response.status_code == 200:
            tx_hash = response.json()["tx_hash"]
            console.print(
                "[bold green]🎉 Congrats! Check your account![/bold green]"
                f"[bold green]🔗 View the transaction: {BLOCK_EXPLORERS[network] + response.json()["tx_hash"]}[/bold green]\n\n"
                )
        else:
            console.print(f"[bold red]❌ [Error] {response}[/bold red]")


if __name__ == "__main__":
    popupfaucet()
