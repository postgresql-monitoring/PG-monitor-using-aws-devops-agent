"""Create an archive containing only the documented skill files."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "postgres-investigation"
FILES = ("SKILL.md", "references/tool-reference.md")


def main():
    output = ROOT / "build" / "postgres-investigation.zip"
    output.parent.mkdir(exist_ok=True)
    for name in FILES:
        if not (SKILL / name).is_file():
            raise FileNotFoundError(name)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(SKILL / name, arcname=name)
    print(output)


if __name__ == "__main__":
    main()
