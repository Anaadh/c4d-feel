"""Copy the C4D Feel add-on into the Blender fork as a bundled core add-on.

Usage:  python tools/sync_to_fork.py [fork_dir]
Default fork dir: ~/blender-fork. The add-on repo stays the source of truth;
run this before building the fork.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "c4d_feel")
fork = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/blender-fork")
DST = os.path.join(fork, "scripts", "addons_core", "c4d_feel")

if os.path.isdir(DST):
    shutil.rmtree(DST)
shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.stackdump", "blender_manifest.toml"))
print("synced", os.path.abspath(SRC), "->", DST)
