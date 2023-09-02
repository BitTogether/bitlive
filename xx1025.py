import subprocess
import binascii
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import os
import datetime

# Replace with the actual path to your bitcoin-cli executable
BITCOIN_CLI = r"D:\Program Files\BitcoinCore25\daemon\bitcoin-cli.exe"

# Specify the data directory for Bitcoin Core
DATA_DIR = r"D:\Program Files\BitcoinCoreBlockchain"

# Specify the starting block height
START_BLOCK_HEIGHT = 803953

# Specify the text you want to search for
SEARCH_TEXTS = ["Bitcoin is Dead", "Live on Bitcoin", "Élő adás a Bitcoinról"]

hits_list = []  # Store information about hits

def create_search_folder():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    search_folder_name = f"search_{timestamp}"
    search_folder_path = os.path.join(os.getcwd(), search_folder_name)

    os.makedirs(os.path.join(search_folder_path, "hits"))
    return search_folder_path

def extract_hex_around_search_term(tx_data, search_text):
    term_position = tx_data.lower().find(search_text.encode().lower())

    if term_position != -1:
        start_position = term_position
        end_position = term_position + len(search_text)

        while start_position > 0 and end_position < len(tx_data):
            if not tx_data[start_position - 1].isxdigit() or not tx_data[end_position].isxdigit():
                break
            start_position -= 1
            end_position += 1

        hex_around_search_term = tx_data[start_position:end_position]

        return hex_around_search_term.decode(errors='ignore')

    return None

def write_search_result(search_folder, search_text, tx_info, txid, channel_file_index):
    hits_folder = os.path.join(search_folder, "hits")
    channel_file_name = f"channel_{channel_file_index}.txt"
    channel_file_path = os.path.join(hits_folder, channel_file_name)

    try:
        hex_around_search_term = extract_hex_around_search_term(binascii.unhexlify(tx_info), search_text.encode())
    except binascii.Error as e:
        hex_around_search_term = f"Error decoding hex data: {str(e)}"

    with open(channel_file_path, "w", encoding='utf-8', errors='ignore') as channel_file:
        if hex_around_search_term:
            channel_file.write(f"Hex Data Around Search Term:\n{hex_around_search_term}\n\n")
        channel_file.write(f"Found Text: {search_text}\n")
        channel_file.write(f"Transaction Info:\n{tx_info}\n")

def get_transaction_data(txid):
    full_command = [
        BITCOIN_CLI,
        "-datadir=" + DATA_DIR,
        "getrawtransaction",
        txid,
        "1"  # Include verbose transaction details
    ]

    tx_info = subprocess.check_output(full_command, text=True).strip()
    return tx_info

def search_for_text_in_transactions(block_height, search_folder):
    full_command = [
        BITCOIN_CLI,
        "-datadir=" + DATA_DIR,
        "getblockhash",
        str(block_height)
    ]

    block_hash = subprocess.check_output(full_command, text=True).strip()

    full_command = [
        BITCOIN_CLI,
        "-datadir=" + DATA_DIR,
        "getblock",
        block_hash,
        "2"  # Include transactions
    ]

    block_info = subprocess.check_output(full_command, text=True).strip()
    transactions = block_info.split('"hex": "')[1:]

    search_results = []
    for tx_number, tx_hex in enumerate(transactions, start=1):
        tx_data = binascii.unhexlify(tx_hex.split('"')[0])
        for search_text in SEARCH_TEXTS:
            if search_text.lower().encode() in tx_data.lower():
                txid = tx_hex.split('"txid": "')[1].split('"')[0]
                tx_info = get_transaction_data(txid)
                search_results.append((search_text, txid, tx_info))

    return block_hash, search_results

def submit():
    current_block_height = int(subprocess.check_output([BITCOIN_CLI, "-datadir=" + DATA_DIR, "getblockcount"], text=True).strip())
    search_folder = create_search_folder()
    channel_file_index = 0

    # Write search terms and program info to searchstats.txt with UTF-8 encoding
    with open(os.path.join(search_folder, "searchstats.txt"), "w", encoding='utf-8') as searchstats_file:
        searchstats_file.write("Search Terms:\n")
        for search_text in SEARCH_TEXTS:
            searchstats_file.write(f"- {search_text}\n")
        searchstats_file.write(f"Program Name: {os.path.basename(__file__)}\n")
        searchstats_file.write(f"Time Run: {datetime.datetime.now()}\n")

    for block_height in range(START_BLOCK_HEIGHT, current_block_height + 1):
        block_hash, search_results = search_for_text_in_transactions(block_height, search_folder)

        if search_results:
            text_widget.insert(tk.END, f"Text found in block {block_height} ({block_hash})\n")
            hits_list.append((block_height, search_results))
            for search_text, txid, _ in search_results:
                text_widget.insert(tk.END, f"Found instance of '{search_text}' in transaction (txid: {txid})\n")
                text_widget.see(tk.END)
                text_widget.update_idletasks()
                write_search_result(search_folder, search_text, get_transaction_data(txid), txid, channel_file_index)
                channel_file_index += 1
        else:
            text_widget.insert(tk.END, f"Text not found in block {block_height} ({block_hash})\n")
            text_widget.see(tk.END)
            text_widget.update_idletasks()

        if block_height >= current_block_height:
            break

    print("Search completed")

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
            for search_text, _, _ in hit[1]:
                print(f"   {search_text}")

root = tk.Tk()
root.title("Bitcoin Search GUI")

text_widget = scrolledtext.ScrolledText(root, wrap=tk.WORD)
text_widget.pack(fill=tk.BOTH, expand=True)

start_button = ttk.Button(root, text="Start Search", command=start_submit_thread)
start_button.pack()

root.mainloop()
