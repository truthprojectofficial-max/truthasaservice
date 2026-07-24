import sys, json
sys.path.insert(0, ".")
from src.io import vault_io

contacts_dir = "contacts"
files = ["operator.json", "roles.json", "vendors.json", "legal.json", "emergency.json"]
for f in files:
    path = f"{contacts_dir}/{f}"
    data = json.load(open(path))
    data["sealed_to_chain"] = True
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
    block = vault_io.append_block("CONTACT_SEALED_" + f.replace(".json","").upper(), {
        "fix_id": "contact-registry",
        "file": path,
        "contact_data": data,
        "operator": "Justin Barnett",
    })
    print("Sealed " + f + " -> block " + str(block["index"]))