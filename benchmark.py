import timeit

setup_code = """
alias = "user_alias"
email = "test@example.com"
telefono = "+1234567890"
extra_seeds = ["seed1", "seed2@test.com", "seed3"] * 10
recursive_targets = [
    {"type": "email", "value": "recurse1@test.com"},
    {"type": "phone", "value": "+0987654321"},
    {"type": "social", "value": "http://social.com/recurseuser"}
] * 10
real_names = ["Real Name 1", "Real Name 2"] * 5
"""

test_code_original = """
osint_username_targets = []
osint_email_targets = []
osint_phone_targets = []

if alias: osint_username_targets.append(alias)
if email:
    osint_email_targets.append(email)
    osint_username_targets.append(email.split("@")[0])
if telefono: osint_phone_targets.append(telefono)

for seed in extra_seeds:
    if "@" in seed: osint_email_targets.append(seed)
    elif seed.startswith("+") or (seed.isdigit() and len(seed) > 8): osint_phone_targets.append(seed)
    else: osint_username_targets.append(seed)

for rt in recursive_targets:
    if rt["type"] == "email": osint_email_targets.append(rt["value"])
    elif rt["type"] == "phone": osint_phone_targets.append(rt["value"])
    elif rt["type"] in ("social", "username"):
        val = rt["value"]
        if val.startswith("http"):
            username = val.rstrip("/").split("/")[-1]
            if username and len(username) > 2: osint_username_targets.append(username)
        else:
            osint_username_targets.append(val)

osint_username_targets = list(set(osint_username_targets))
osint_email_targets = list(set(osint_email_targets))
osint_phone_targets = list(set(osint_phone_targets))

for name in real_names:
    if name not in osint_username_targets:
        osint_username_targets.append(name)

osint_username_targets = list(set(osint_username_targets))
osint_email_targets = list(set(osint_email_targets))
osint_phone_targets = list(set(osint_phone_targets))
"""

test_code_optimized = """
osint_username_targets = set()
osint_email_targets = set()
osint_phone_targets = set()

if alias: osint_username_targets.add(alias)
if email:
    osint_email_targets.add(email)
    osint_username_targets.add(email.split("@")[0])
if telefono: osint_phone_targets.add(telefono)

for seed in extra_seeds:
    if "@" in seed: osint_email_targets.add(seed)
    elif seed.startswith("+") or (seed.isdigit() and len(seed) > 8): osint_phone_targets.add(seed)
    else: osint_username_targets.add(seed)

for rt in recursive_targets:
    if rt["type"] == "email": osint_email_targets.add(rt["value"])
    elif rt["type"] == "phone": osint_phone_targets.add(rt["value"])
    elif rt["type"] in ("social", "username"):
        val = rt["value"]
        if val.startswith("http"):
            username = val.rstrip("/").split("/")[-1]
            if username and len(username) > 2: osint_username_targets.add(username)
        else:
            osint_username_targets.add(val)

for name in real_names:
    osint_username_targets.add(name)

osint_username_targets = list(osint_username_targets)
osint_email_targets = list(osint_email_targets)
osint_phone_targets = list(osint_phone_targets)
"""

print("Original:")
t1 = timeit.timeit(test_code_original, setup=setup_code, number=100000)
print(f"{t1:.6f} seconds")

print("Optimized:")
t2 = timeit.timeit(test_code_optimized, setup=setup_code, number=100000)
print(f"{t2:.6f} seconds")

improvement = (t1 - t2) / t1 * 100
print(f"Improvement: {improvement:.2f}%")
