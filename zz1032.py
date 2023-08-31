import subprocess
import binascii
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading

# Replace with the actual path to your bitcoin-cli executable
BITCOIN_CLI = r"D:\Program Files\BitcoinCore25\daemon\bitcoin-cli.exe"

# Specify the data directory for Bitcoin Core
DATA_DIR = r"D:\Program Files\BitcoinCoreBlockchain"

# Specify the starting block height
START_BLOCK_HEIGHT = 803953

# Specify the text you want to search for
SEARCH_TEXTS = ["Bitcoin is Dead", "Live on Bitcoin", "Élő adás a Bitcoinról"]

hits_list = []  # Store information about hits

def get_transaction_data(txid):
    # Construct the full bitcoin-cli command with -datadir parameter
    full_command = [
        BITCOIN_CLI,
        "-datadir=" + DATA_DIR,
        "getrawtransaction",
        txid,
        "1"  # Include verbose transaction details
    ]

    # Retrieve the transaction data
    tx_info = subprocess.check_output(full_command, text=True).strip()
    return tx_info

def search_for_text_in_transactions(block_height):
    # Construct the full bitcoin-cli command with -datadir parameter
    full_command = [
        BITCOIN_CLI,
        "-datadir=" + DATA_DIR,
        "getblockhash",
        str(block_height)
    ]

    # Retrieve the block hash for the given block height
    block_hash = subprocess.check_output(full_command, text=True).strip()

    # Construct the command to retrieve the block's transactions
    full_command = [
        BITCOIN_CLI,
        "-datadir=" + DATA_DIR,
        "getblock",
        block_hash,
        "2"  # Include transactions
    ]

    # Retrieve the block's transaction data
    block_info = subprocess.check_output(full_command, text=True).strip()

    # Extract transactions from the block info
    transactions = block_info.split('"hex": "')[1:]  # Splitting transactions based on "hex" field

    # Search for the text within the transactions
    search_results = []
    for tx_number, tx_hex in enumerate(transactions, start=1):
        tx_data = binascii.unhexlify(tx_hex.split('"')[0])  # Convert hex to bytes
        for search_text in SEARCH_TEXTS:
            if search_text.encode().lower() in tx_data.lower():
                search_results.append((search_text, tx_number))

    return block_hash, search_results

def submit():
    current_block_height = int(subprocess.check_output([BITCOIN_CLI, "-datadir=" + DATA_DIR, "getblockcount"], text=True).strip())
    
    for block_height in range(START_BLOCK_HEIGHT, current_block_height + 1):
        block_hash, search_results = search_for_text_in_transactions(block_height)
        
        if search_results:
            text_widget.insert(tk.END, f"Text found in block {block_height} ({block_hash})\n")
            hits_list.append((block_height, search_results))  # Add hits to the list
            for search_text, tx_number in search_results:
                txid_command = [
                    BITCOIN_CLI,
                    "-datadir=" + DATA_DIR,
                    "getblock",
                    block_hash,
                    "2"
                ]
                txid = subprocess.check_output(txid_command, text=True).strip().split('"txid": "')[1].split('"')[0]
                tx_info = get_transaction_data(txid)
                
                text_widget.insert(tk.END, f"Found instance of '{search_text}' in transaction {tx_number} (txid: {txid})\n")
                text_widget.insert(tk.END, tx_info + '\n')
                text_widget.see(tk.END)
                text_widget.update_idletasks()

        else:
            text_widget.insert(tk.END, f"Text not found in block {block_height} ({block_hash})\n")
            text_widget.see(tk.END)
            text_widget.update_idletasks()

def start_submit_thread():
    global submit_thread
    submit_thread = threading.Thread(target=submit)
    submit_thread.start()
    check_submit_thread()

def check_submit_thread():
    if submit_thread.is_alive():
        root.after(100, check_submit_thread)
    else:
        print("Thread finished")
        print("Hits:")
        for hit in hits_list:
            print(f"Block {hit[0]}:")
            for search_text, tx_number in hit[1]:
                print(f"   {search_text} in transaction {tx_number}")

# Create the main window
root = tk.Tk()
root.title("Bitcoin Search GUI")

# Create a scrolled text widget
text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD)
text_widget.pack(fill=tk.BOTH, expand=True)

# Create a button to start the search
start_button = ttk.Button(root, text="Start Search", command=start_submit_thread)
start_button.pack()

# Start the GUI event loop
root.mainloop()
