#!/usr/bin/env python3
"""Check .si domain availability via the Arnes (register.si) website lookup.

Prints one line per domain. Exits 2 if any domain is free, so a scheduler
can treat "free" as the alert condition.
"""
import os, re, sys, time, urllib.parse, urllib.request

HOME = "https://www.register.si/en/"
AJAX = "https://www.register.si/wp-admin/admin-ajax.php"
UA = {"User-Agent": "Mozilla/5.0 (si-watch; personal availability check)"}


def fetch(url, data=None):
    req = urllib.request.Request(url, data=data, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def nonce():
    m = re.search(r'nonce":"([a-f0-9]+)', fetch(HOME))
    if not m:
        raise RuntimeError("no nonce on register.si homepage")
    return m.group(1)


def status(domain, n):
    body = urllib.parse.urlencode(
        {"_ajax_nonce": n, "action": "get_domain_status", "domain": domain}
    ).encode()
    text = re.sub(r"<[^>]+>", " ", fetch(AJAX, body))
    if "je prosta" in text:
        return "FREE"
    if "registrirana" in text:
        return "registered"
    if "rezervirana" in text:
        return "reserved"
    return "unknown"


def main():
    domains = (os.environ.get("SI_DOMAINS") or " ".join(sys.argv[1:])).split()
    domains = [d if d.endswith(".si") else d + ".si" for d in domains]
    # In GitHub Actions the logs are public, so only free names are printed there.
    quiet = os.environ.get("GITHUB_ACTIONS") == "true"
    try:
        n = nonce()
    except Exception as e:
        print(f"::warning::register.si lookup unavailable: {e}", flush=True)
        return
    free, unknown = [], 0
    for d in domains:
        try:
            s = status(d, n)
        except Exception:
            s = "unknown"
        if s == "unknown":
            unknown += 1
        if not quiet:
            print(f"{d}: {s}", flush=True)
        if s == "FREE":
            free.append(d)
        time.sleep(1)
    if unknown:
        print(f"::warning::{unknown} of {len(domains)} lookups gave no answer", flush=True)
    if free:
        for d in free:
            print(f"::error title=.si domain FREE::{d} is free. Register it now.", flush=True)
        sys.exit(2)
    print(f"Checked {len(domains)} domains: none free.", flush=True)


if __name__ == "__main__":
    main()
