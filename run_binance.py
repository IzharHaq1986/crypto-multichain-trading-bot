import os
import subprocess

os.environ["CHAIN"] = "binance"
subprocess.run(["python3", "main.py"])
