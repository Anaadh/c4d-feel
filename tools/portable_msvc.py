"""Fetch a portable (no-install, no-admin) MSVC toolset from Microsoft's
Visual Studio package feed, for building the Blender fork when the installed
Visual Studio is too old and can't be updated without an admin prompt.

Usage:  python portable_msvc.py <dest_dir> [min_version]
Downloads only Microsoft-hosted packages listed in the official VS channel
manifest (https://aka.ms/vs/17/release/channel). The Windows SDK already
installed on the machine is reused.
"""

import hashlib
import io
import json
import os
import sys
import urllib.request
import zipfile

CHANNEL = "https://aka.ms/vs/17/release/channel"


def get(url):
    with urllib.request.urlopen(url) as r:
        return r.read()


def version_key(v):
    return tuple(int(p) for p in v.split("."))


def main():
    dest = os.path.abspath(sys.argv[1])
    min_ver = sys.argv[2] if len(sys.argv) > 2 else "14.44"
    os.makedirs(dest, exist_ok=True)

    channel = json.loads(get(CHANNEL))
    vs_item = next(i for i in channel["channelItems"] if i["id"] == "Microsoft.VisualStudio.Manifests.VisualStudio")
    manifest = json.loads(get(vs_item["payloads"][0]["url"]))
    packages = {}
    for p in manifest["packages"]:
        packages.setdefault(p["id"].lower(), []).append(p)

    # Pick the newest MSVC toolset >= min_ver.
    prefix = "microsoft.vc."
    suffix = ".tools.hostx64.targetx64.base"
    candidates = {pid[len(prefix):-len(suffix)] for pid in packages
                  if pid.startswith(prefix) and pid.endswith(suffix)}
    # Skip non-numeric ids such as "premium".
    candidates = {v for v in candidates if all(part.isdigit() for part in v.split("."))}
    versions = sorted(candidates, key=version_key)
    versions = [v for v in versions if version_key(v) >= version_key(min_ver)]
    if not versions:
        sys.exit(f"No MSVC toolset >= {min_ver} in the channel")
    ver = versions[-1]
    print("MSVC toolset:", ver, flush=True)

    wanted = [
        f"microsoft.vc.{ver}.tools.hostx64.targetx64.base",
        f"microsoft.vc.{ver}.tools.hostx64.targetx64.res.base",
        f"microsoft.vc.{ver}.crt.headers.base",
        f"microsoft.vc.{ver}.crt.x64.desktop.base",
        f"microsoft.vc.{ver}.crt.x64.store.base",
        f"microsoft.vc.{ver}.crt.redist.x64.base",
        f"microsoft.vc.{ver}.atl.headers.base",
        f"microsoft.vc.{ver}.atl.x64.base",
        f"microsoft.vc.{ver}.openmp.x64.base" if f"microsoft.vc.{ver}.openmp.x64.base" in packages else None,
        f"microsoft.vc.{ver}.asan.headers.base",
    ]
    for pid in filter(None, wanted):
        if pid not in packages:
            print("  (missing, skipped)", pid, flush=True)
            continue
        pkg = next((p for p in packages[pid] if p.get("language") in (None, "neutral", "en-US")), packages[pid][0])
        for payload in pkg.get("payloads", []):
            data = get(payload["url"])
            sha = payload.get("sha256")
            if sha and hashlib.sha256(data).hexdigest().lower() != sha.lower():
                sys.exit(f"Checksum mismatch for {payload['fileName']}")
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for name in z.namelist():
                    if not name.startswith("Contents/"):
                        continue
                    out = os.path.join(dest, name[len("Contents/"):].replace("/", os.sep))
                    if name.endswith("/"):
                        continue
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    with open(out, "wb") as f:
                        f.write(z.read(name))
            print("  ok", pid, f"{len(data) // 1024} KB", flush=True)

    tools = os.path.join(dest, "VC", "Tools", "MSVC")
    print("installed:", os.listdir(tools) if os.path.isdir(tools) else "?", flush=True)


if __name__ == "__main__":
    main()
