import subprocess
import os
import sys

def run_theharvester(domain):
    project_root = os.path.dirname(os.path.abspath(__file__))
    harvester_dir = os.path.join(project_root, "theHarvester")
    cmd = [sys.executable, "-m", "theHarvester", "-d", domain, "-b", "all"]
    try:
        process = subprocess.Popen(
            cmd, cwd=harvester_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="ignore"
        )
        for line in process.stdout:
            print(line, end="")
        process.wait()
    except Exception as e:
        print(f"Error: {e}")

run_theharvester("example.com")
