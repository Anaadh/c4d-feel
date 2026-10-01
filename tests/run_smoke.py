"""Launch helper: open Blender with the C4D workspace, run the smoke test,
write results to tests/smoke_result.txt and quit. Never saves the file.

  blender --factory-startup? no: uses the user's startup so the C4D layout exists.
  "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --python tests/run_smoke.py
"""

import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "smoke_result.txt")


def go():
    try:
        ns = {"__name__": "smoke"}
        with open(os.path.join(HERE, "smoke_test.py"), encoding="utf-8") as f:
            exec(f.read(), ns)
        result = ns["run"]()
    except Exception as ex:  # noqa: BLE001
        import traceback
        result = "CRASH " + traceback.format_exc()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(result)
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(go, first_interval=4.0)
