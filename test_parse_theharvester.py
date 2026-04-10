import sys
import os

class MockOSINTToolAgent:
    @classmethod
    def stream_command(cls, cmd, cwd, timeout=300):
        yield "Starting theHarvester..."
        yield ""
        yield "[*] Searching..."
        yield "Emails found:"
        yield "admin@example.com"
        yield "test@example.com"
        yield ""
        yield "Hosts found:"
        yield "www.example.com"
        yield "mail.example.com"
        yield ""
        yield "IPs found:"
        yield "1.1.1.1"

    @classmethod
    def run_theharvester_live(cls, domain: str, callback, current_logs, consolidated_results):
        current_section = None
        for line in cls.stream_command([], ""):
            clean = line.strip()
            if not clean: continue
            current_logs.append(f"[theHarvester] {clean}")

            # Identify sections
            if "Emails found:" in clean:
                current_section = "emails"
                continue
            elif "Hosts found:" in clean:
                current_section = "hosts"
                continue
            elif "IPs found:" in clean:
                current_section = "ips"
                continue

            # Parse based on section if the line doesn't look like standard log output
            if current_section and not clean.startswith("[*]") and not clean.startswith("[-]"):
                if current_section == "emails" and "@" in clean:
                    email = clean.split()[0]
                    node = {"type": "email", "source": "theHarvester", "value": email}
                    if node not in consolidated_results:
                        consolidated_results.append(node)
                        callback(f"[+] Email: {email}")
                elif current_section == "hosts":
                    host = clean.split()[0]
                    node = {"type": "host", "source": "theHarvester", "value": host}
                    if node not in consolidated_results:
                        consolidated_results.append(node)
                        callback(f"[+] Host: {host}")
                elif current_section == "ips":
                    ip = clean.split()[0]
                    node = {"type": "ip", "source": "theHarvester", "value": ip}
                    if node not in consolidated_results:
                        consolidated_results.append(node)
                        callback(f"[+] IP: {ip}")

        callback(f"[INFO] theHarvester finalizado.")

logs = []
results = []
def my_cb(msg):
    print("CB:", msg)

MockOSINTToolAgent.run_theharvester_live("example.com", my_cb, logs, results)
print("Results:")
for r in results:
    print(r)
