import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import os
import time
import binascii

# Function to run a Bitcoin CLI command and return the result
def run_bitcoin_cli(command):
    try:
        result = subprocess.check_output([bitcoin_cli_path, '-datadir=' + datadir] + command)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"

# Function to check if bitcoind is running
def is_bitcoind_running():
    result = run_bitcoin_cli(['getblockchaininfo'])
    return not result.startswith("Error")

# Function to update the progress bar and estimated completion time
def update_progress(progress_bar, progress, start_time, current_block, total_blocks):
    progress_bar["value"] = progress

    current_time = int(time.time())
    elapsed_time = current_time - start_time
    if progress > 0:
        estimated_time = ((elapsed_time / progress) * (100 - progress))
        days = int(estimated_time // (24 * 3600))
        remaining_time = estimated_time % (24 * 3600)
        hours = int(remaining_time // 3600)
        remaining_time %= 3600
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)

        time_str = f"Estimated Time Remaining: {days}d {hours}h {minutes}m {seconds}s - {progress:.1f}% complete"
    else:
        time_str = "Estimated Time Remaining: calculating... - 0.0% complete"
    
    progress_label.config(text=time_str)  # Update the text label below the progress bar

# Function to search for terms in blocks
def search_blocks(progress_bar):
    global result_text
    search_start_time = int(time.time())
    search_stop_time = None
    searched_blocks = []

    # Create a folder to save hit information
    folder_name = f"search_{search_start_time}"
    os.makedirs(folder_name)

    # Write search start information to a file with 'utf-8' encoding
    with open(os.path.join(folder_name, "SearchStart.txt"), "w", encoding="utf-8") as search_start_file:
        search_start_file.write(f"Search Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(search_start_time))}\n")
        search_start_file.write(f"Program Name: Bitcoin Block Search\n")
        search_start_file.write(f"Starting Block: {start_block_entry.get()}\n")
        search_start_file.write("Search Terms:\n")
        search_start_file.write("\n".join(search_terms))

    try:
        start_block = int(start_block_entry.get())
        stop_block = run_bitcoin_cli(['getblockcount'])
        if not stop_block.startswith("Error"):
            stop_block = int(stop_block)
        else:
            result_text.insert(tk.END, "Error: Unable to get the current block height. Please check your configuration.\n")
            return

        for block_height in range(start_block, stop_block + 1):
            block_hash = run_bitcoin_cli(['getblockhash', str(block_height)]).strip()

            if block_hash:
                block_info = run_bitcoin_cli(['getblock', block_hash, '2'])
                if not block_info.startswith("Error"):
                    hits_in_block = []

                    for term_hex, term in zip(search_terms_hex, search_terms):
                        if term_hex.strip() != "":
                            if term_hex in block_info:
                                hits_in_block.append((term, block_hash))
                                searched_blocks.append(block_height)

                                # Save block content in a separate file
                                content_filename = os.path.join(folder_name, f"{block_height}_content.txt")
                                with open(content_filename, 'w', encoding='utf-8') as content_file:
                                    content_file.write(block_info)

                    result_text.insert(tk.END, f"Block Height: {block_height}, Hits Found: {len(hits_in_block)}\n")

                    if hits_in_block:
                        for hit in hits_in_block:
                            result_text.insert(tk.END, f"Term Found: {hit[0]}, Block Hash: {hit[1]}\n")
                            # Save hit information in a file
                            hit_filename = os.path.join(folder_name, f"{block_height}_hit.txt")
                            with open(hit_filename, 'a', encoding='utf-8') as hit_file:
                                hit_file.write(f"Block Height: {block_height}\n")
                                hit_file.write(f"Block Hash: {hit[1]}\n")
                                hit_file.write(f"Term Found: {hit[0]}\n")

                    # Calculate progress based on block heights
                    progress = ((block_height - start_block) / (stop_block - start_block)) * 100
                    update_progress(progress_bar, progress, search_start_time, block_height, stop_block)

        if not result_text.get("1.0", tk.END).strip():
            result_text.insert(tk.END, f"No hits found in the search.\n")

        search_stop_time = int(time.time())

    except ValueError:
        result_text.insert(tk.END, "Error: Invalid starting block height. Please enter a valid number.\n")

    # Write search stop information to a file with 'utf-8' encoding
    if search_stop_time is not None:
        with open(os.path.join(folder_name, "SearchStop.txt"), "w", encoding="utf-8") as search_stop_file:
            search_stop_file.write(f"Search Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(search_start_time))}\n")
            search_stop_file.write(f"Search Stop Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(search_stop_time))}\n")
            search_stop_file.write(f"Total Time Elapsed: {search_stop_time - search_start_time} seconds\n")
            search_stop_file.write(f"Search Range: Blocks {start_block} to {stop_block}\n")
            search_stop_file.write("Blocks with Hits:\n")
            search_stop_file.write("\n".join(map(str, searched_blocks)))

        update_progress(progress_bar, 100, search_start_time, stop_block, stop_block)

        # Read the "searchstop" text file and display its contents in the result_text widget
        search_stop_file_path = os.path.join(folder_name, "SearchStop.txt")
        with open(search_stop_file_path, "r", encoding="utf-8") as search_stop_file:
            search_stop_contents = search_stop_file.read()
            result_text.insert(tk.END, "\nSearch Stop Information:\n")
            result_text.insert(tk.END, search_stop_contents)

# Function to start the search
def start_search():
    global bitcoin_cli_path
    global datadir
    global search_terms_hex
    global search_terms
    global result_text
    global progress_label  # Define the progress_label variable

    bitcoin_cli_path = bitcoin_cli_entry.get()
    datadir = datadir_entry.get()

    # Convert search terms to hexadecimal format and keep both hex and original terms
    search_terms = search_text.get("1.0", tk.END).splitlines()
    search_terms_hex = [binascii.hexlify(term.encode()).decode() for term in search_terms]

    if not is_bitcoind_running():
        result_text.insert(tk.END, "Error: bitcoind is not running. Please start bitcoind and try again.\n")
        return

    # Hide the original GUI
    root.withdraw()

    result_window = tk.Toplevel(root)
    result_window.title("Bitcoin Search Results")

    result_text = scrolledtext.ScrolledText(result_window, wrap=tk.WORD)
    result_text.pack(fill=tk.BOTH, expand=True)

    progress_frame = ttk.Frame(result_window)
    progress_frame.pack(fill=tk.X, padx=10, pady=5)
    progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=200, mode='determinate')
    progress_bar.pack(fill=tk.X, padx=5, pady=5)

    progress_label = tk.Label(progress_frame, text="Estimated Time Remaining: calculating... - 0.0% complete")
    progress_label.pack(fill=tk.X, padx=5, pady=5)

    search_thread = threading.Thread(target=search_blocks, args=(progress_bar,))
    search_thread.start()

    # Configure the result_text widget to auto-scroll to the newest entry
    def auto_scroll():
        result_text.see(tk.END)  # Scroll to the bottom
        result_window.after(100, auto_scroll)  # Schedule the next scroll check

    auto_scroll()

root = tk.Tk()
root.title("Bitcoin Block Search")

bitcoin_cli_label = tk.Label(root, text="Path to bitcoin-cli:")
bitcoin_cli_label.pack()

bitcoin_cli_default = "D:\\Program Files\\BitcoinCore25\\daemon\\bitcoin-cli.exe"
bitcoin_cli_entry = tk.Entry(root, width=40)
bitcoin_cli_entry.insert(0, bitcoin_cli_default)
bitcoin_cli_entry.pack()

datadir_label = tk.Label(root, text="Bitcoin Data Directory (-datadir=):")
datadir_label.pack()

datadir_default = "D:\\Program Files\\BitcoinCoreBlockchain"
datadir_entry = tk.Entry(root, width=40)
datadir_entry.insert(0, datadir_default)
datadir_entry.pack()

start_block_label = tk.Label(root, text="Starting Block Height:")
start_block_label.pack()

start_block_default = "803953"
start_block_entry = tk.Entry(root)
start_block_entry.insert(0, start_block_default)
start_block_entry.pack()

search_label = tk.Label(root, text="Enter search terms (one per line):")
search_label.pack()

default_search_terms = [
    "Bitcoin is Dead",
    "Live on Bitcoin",
    "en direct sur Bitcoin",
    "sänds live på Bitcoin",
    "in diretta su Bitcoin",
    "Live sa Bitcoin",
    "Live auf Bitcoin",
    "Ola ma ka Bitcoin",
    "Gụọ n'ụzọ Bitcoin",
    "リアルタイムでビットコイン",
    "實況比特幣",
    "实况比特币",
    "बिटकॉइन पर लाइव",
    "Прямая трансляция о Биткоине",
    "Ao vivo com Bitcoin",
    "بث مباشر حول البيتكوين",
    "실시간 비트코인 방송",
    "Canlı Bitcoin Yayını",
    "Live uitzending over Bitcoin",
    "Na żywo na temat Bitcoina",
    "Mubashara juu ya Bitcoin",
    "ถ่ายทอดสดเกี่ยวกับบิทคอยน์",
    "Ζωντανή μετάδοση για το Bitcoin",
    "Trực tiếp về Bitcoin",
    "Live despre Bitcoin",
    "Пряма трансляція про Bitcoin",
    "Élő adás a Bitcoinról",
    "Živě o Bitcoinu",
    "বিটকয়েন লাইভ",
    "Langsung tentang Bitcoin",
    "Suora lähetys Bitcoinista",
    "Live om Bitcoin",
    "Direktesendt om Bitcoin",
    "Langsung mengenai Bitcoin",
    "שידור חי על ביטקוין",
    "На живо за Биткойн"
]

search_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, width=40)
for term in default_search_terms:
    search_text.insert(tk.END, term + "\n")
search_text.pack()

start_button = tk.Button(root, text="Start Search", command=start_search)
start_button.pack()

root.mainloop()

