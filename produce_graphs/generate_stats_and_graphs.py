import requests
import matplotlib.pyplot as plt
from collections import Counter

ONIONOO_URL = "https://onionoo.torproject.org/details?type=relay"

FOURTEEN_EYES = {
    "US","UK","CA","AU","NZ",
    "DK","FR","NL","NO","DE",
    "BE","IT","ES","SE"
}

def fetch_relays():
    print("[*] Fetching relay data from Onionoo…")
    r = requests.get(
        ONIONOO_URL,
        headers={"User-Agent": "Tor-Research/1.0"},
        timeout=20
    )
    r.raise_for_status()
    return r.json()["relays"]

def plot_top15_countries(relays):
    countries = [r.get("country", "??").upper() for r in relays]
    counts = Counter(countries)
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    top15 = sorted_items[:15]
    other = sum(v for _, v in sorted_items[15:])

    labels = [c for c, _ in top15] + ["Other"]
    values = [v for _, v in top15] + [other]

    plt.figure(figsize=(12, 6))
    plt.bar(labels, values)
    plt.title("Geographic Distribution of Tor Relays (Top 15 Countries)")
    plt.xlabel("Country")
    plt.ylabel("Number of Relays")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("tor_top15_countries.png", dpi=300)
    plt.close()

    print("[+] Saved tor_top15_countries.png")

def compute_selection_probabilities(relays):
    guard_14 = guard_non14 = 0.0
    middle_14 = middle_non14 = 0.0

    for r in relays:
        cc = r.get("country", "").upper()
        gp = r.get("guard_probability", 0.0)
        mp = r.get("middle_probability", 0.0)

        if cc in FOURTEEN_EYES:
            guard_14 += gp
            middle_14 += mp
        else:
            guard_non14 += gp
            middle_non14 += mp

    return {
        "guard": (guard_14, guard_non14),
        "middle": (middle_14, middle_non14)
    }

def plot_selection_probabilities(probs):
    labels = ["14-Eyes", "Non-14-Eyes"]
    x = range(len(labels))
    width = 0.35

    guard_vals = [probs["guard"][0]*100, probs["guard"][1]*100]
    middle_vals = [probs["middle"][0]*100, probs["middle"][1]*100]

    plt.figure(figsize=(7,5))
    plt.bar([i - width/2 for i in x], guard_vals, width, label="Entry Guards")
    plt.bar([i + width/2 for i in x], middle_vals, width, label="Middle Relays")

    plt.ylabel("Selection Probability (%)")
    plt.title("Relay Selection Probability by Jurisdiction (14-Eyes vs Others)")
    plt.xticks(x, labels)
    plt.legend()
    plt.tight_layout()
    plt.savefig("tor_14eyes_selection_probability.png", dpi=300)
    plt.close()

    print("[+] Saved tor_14eyes_selection_probability.png")

    print("\n=== 14-EYES HOSTING PROBABILITY ===")
    print(f"Entry Guards:")
    print(f"  14-Eyes:     {guard_vals[0]:.2f}%")
    print(f"  Non-14-Eyes: {guard_vals[1]:.2f}%")
    print(f"\nMiddle Relays:")
    print(f"  14-Eyes:     {middle_vals[0]:.2f}%")
    print(f"  Non-14-Eyes: {middle_vals[1]:.2f}%")

def main():
    relays = fetch_relays()
    plot_top15_countries(relays)
    probs = compute_selection_probabilities(relays)
    plot_selection_probabilities(probs)

if __name__ == "__main__":
    main()
