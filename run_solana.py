import os
import subprocess

os.environ["CHAIN"] = "solana"
subprocess.run(["python3", "main.py"])
