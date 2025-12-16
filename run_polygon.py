import os
import subprocess

os.environ["CHAIN"] = "polygon"
subprocess.run(["python3", "main.py"])
