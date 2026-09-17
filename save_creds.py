#!/usr/bin/env python3
"""
save_creds.py  --  one-time credential saver, the foolproof way.

Run it with:   python3 save_creds.py
It will ASK you for your API key and CRN at simple prompts, so there are
NO quotes to match and NO multi-line paste to get stuck on. Paste each value,
press Enter, done.
"""
import getpass
from qiskit_ibm_runtime import QiskitRuntimeService

print("\n--- Save IBM Quantum credentials ---")
print("Paste your NEW API key, then press Enter.")
print("(It stays hidden as you paste -- that's normal; it's still going in.)")
token = getpass.getpass("API key: ").strip()

crn = input("\nNow paste your instance CRN, then press Enter:\nCRN: ").strip()

if not token or not crn:
    print("\nOne of the values was empty -- run it again and paste both.")
    raise SystemExit(1)

QiskitRuntimeService.save_account(
    token=token,
    instance=crn,
    set_as_default=True,
    overwrite=True,
)
print("\n[OK] Credentials saved. Now run:  python3 relationship_measurement_hardware.py")
