# bitlive
Thank you for checking out Bitlive!, you may inscribe your main channel link on bitcoin using this tool for less than $3 worth of bitcoin: https://bitliveprototype.tiiny.site/.  

Bitlive's protocol is platform agnostic: creators on platforms like youtube, twitch, twitter spaces, kick, or any other platform you might currently be using to reach a live audience or post video content.  If you ever move, you can reinscribe your ordinal and your audience can use bitcoin to follow along and continue supporting creators with bitcoin in the event of platform demonetization.

DM us for assistance in getting your channel on bitcoin: http://www.x.com/@liveonbitcoin or @onchainfossils on twitter. We'd love to help you get your channel on bitcoin or you may use the channel maker tool above to create your Bitlive channel ordinal as a text inscription using any inscription service.

Once your channel is created, our indexer can detect your channel on the bitcoin blockchain so they can be updated on our website bitlive.live or made available to any person using the Bitlive! indexer.  We monitor your link for you to go live or post new content.  Our goal is to grow the indexer into a dapp that lets people enjoy their favorite creators directly without interference from censors or platforms by leveraging the decentralized nature of bitcoin.  

Bitlive channels consist of 3 lines:
1:  "Live on Bitcoin" used as a protocol identifier on line 1 so channels can advertise that they are sources of live video or other content on bitcoin's blockchain in human readable format.  This means you don't have to use ordinals if you like stamps or some other protocol better, Bitlive will pick up your channel anywhere on the bitcoin blockchain as long as an identifier can be found by the indexer.  This identifier is available in 30-some languages at the time of writing on our channel maker tool and the indexer catalogs them all successfully.
2.  Proof of Identification is used on line 2 so that the creator of a channel can prove to users that they created the ordinal.  Our channel maker tool gives users the option of a short aes 256 cbc key and iv as proof but a user can also use their nostr signature here instead to prove their identity via nostr.  Bitlive is encryption agnostic utilizing security thru obscurity and users may feel free to use any scheme to prove identity to their audiences using line 2.  Take a screenshot of your key and IV when you make your channel if you are using the channel maker tool and confused by this part. Just know that the secret key and iv can be used later to prove you are the person who knows the secret written on line 2 similar to a password.  Bitcoin is a cypherpunk community and doing this makes you one of us.
3.  Your Channel Here!  Put a link to your current live, video, or podcast platform here to be broadcast to the world on bitcoin.  This is VERY public and cannot be removed once inscribed, reinscription allows you to change this link but does not remove previous entries.

To use or test the python indexer: install python on windows with a bitcoin core node and point the -datadir= to the place your copy of the blockchain is stored and the path to your cli client.  Tested on the latest bitcoin core (version 25 at writing).  Bitlive's indexer starts at block 803953 and does not run at a high speed, the indexer is meant to be run continuously although that is disabled in this windows release.  Pip can probably help you find the following dependencies is necessary:

import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import os
import time
import binascii
