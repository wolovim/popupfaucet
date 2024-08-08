# popupfaucet

Ethereum testnet faucet CLI

### What

Ephemeral faucets with shareable code phrases via an easy-to-use CLI app.

Network support for: OP Sepolia, Base Sepolia, Sepolia.

### Why

Motivation originated with wanting a pain-free way to get workshop participants some testnet ether to participate with interactive components of the workshop.

Current options leave something to be desired:

1. Ask users to navigate to and use a 3rd-party faucet
    - cons: external point of failure, sales pitches, hoops (account creation/PoW), exhausted daily limits
2. Create and pre-seed wallets then distribute, e.g., print and hand out
    - cons: physical/in-person only, manual process
3. Collect addresses, then use a script to distribute eth
    - cons: if manual, interruptions with latecomers; if automated, one more thing to run and maintain

`popupfaucet` introduces one more option: pre-seeding a faucet accessible to anyone that can install a Python package and is aware of your code phrase.

### How

1. `pipx install popupfaucet`
1. `popupfaucet create`
    1. Select a network
    1. Choose a unique "event code"
    1. Send testnet ether to the address provided
    1. ✨ voila ✨
1. `popupfaucet status` to view available funds in your faucet
1. `popupfaucet claim` to receive testnet funds from a faucet
    1. Select the network
    1. Enter the event code
    1. Enter the address to receive the testnet ether
    1. ✨ enjoy ✨
