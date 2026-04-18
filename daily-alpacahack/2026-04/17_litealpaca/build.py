from pathlib import Path
import base64
import hashlib
import os
import shutil


pkg_name = "litealpaca"
pkg_version = "1.0.0"
flag = os.environ["FLAG"]
root = Path("chall")
wheel_root = root / "extracted-wheel" / f"{pkg_name}-{pkg_version}-py3-none-any.whl"
dist_info = wheel_root / f"{pkg_name}-{pkg_version}.dist-info"
pkg_dir = wheel_root / pkg_name


def b64(data: str) -> str:
    return base64.b64encode(data.encode()).decode()


def record_hash(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


shutil.rmtree(root, ignore_errors=True)

payload = f'import os; os.system("echo \'{flag}\' > /tmp/flag.txt")'
pth = f'import os, subprocess, sys; subprocess.Popen([sys.executable, "-c", "import base64; exec(base64.b64decode(\'{b64(payload)}\'))"])'

write(
    root / "download.log",
    "\n".join(
        [
            f"Collecting {pkg_name}=={pkg_version}",
            f"  Using cached {pkg_name}-{pkg_version}-py3-none-any.whl",
            f"Saved ./downloads/{pkg_name}-{pkg_version}-py3-none-any.whl",
            f"Successfully downloaded {pkg_name}",
            "",
        ]
    ),
)
write(pkg_dir / "__init__.py", f'__version__ = "{pkg_version}"\n')
write(wheel_root / f"{pkg_name}_init.pth", pth + "\n")
write(
    dist_info / "METADATA",
    "\n".join(
        [
            "Metadata-Version: 2.1",
            f"Name: {pkg_name}",
            f"Version: {pkg_version}",
            "Summary: lightweight alpaca tools",
            "",
        ]
    ),
)
write(
    dist_info / "WHEEL",
    "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: litealpaca-build",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    ),
)
write(dist_info / "top_level.txt", f"{pkg_name}\n")

files = [
    wheel_root / f"{pkg_name}_init.pth",
    pkg_dir / "__init__.py",
    dist_info / "METADATA",
    dist_info / "WHEEL",
    dist_info / "top_level.txt",
]
record_lines = []
for path in files:
    rel = path.relative_to(wheel_root).as_posix()
    size = path.stat().st_size
    record_lines.append(f"{rel},sha256={record_hash(path)},{size}")
record_lines.append(f"{pkg_name}-{pkg_version}.dist-info/RECORD,,")
write(dist_info / "RECORD", "\n".join(record_lines) + "\n")
