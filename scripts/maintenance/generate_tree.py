from pathlib import Path
root=Path(__file__).resolve().parents[2]
ignore={".git","node_modules",".venv","__pycache__"}
lines=["# Repository Treeview","", "```text"]
def walk(path, prefix=""):
    items=[p for p in sorted(path.iterdir(), key=lambda p:(not p.is_dir(),p.name.lower())) if p.name not in ignore]
    for i,p in enumerate(items):
        last=i==len(items)-1
        branch="└── " if last else "├── "
        lines.append(prefix+branch+p.name+("/" if p.is_dir() else ""))
        if p.is_dir():
            walk(p,prefix+("    " if last else "│   "))
walk(root)
lines.append("```")
(root/"TREEVIEW.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(root/"TREEVIEW.md")
