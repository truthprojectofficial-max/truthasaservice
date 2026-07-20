from pathlib import Path
root = Path(r"C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight")
for sub in ["02_Technical/src"]:
    d = root / sub
    for p in sorted(d.rglob("*.py")):
        rel = p.relative_to(root)
        print(f"{p.stat().st_size:7d}  {rel}")