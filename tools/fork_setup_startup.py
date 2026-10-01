"""Set up the fork's startup file: C4D theme + workspace (with palette row),
then save it as the startup file and preferences, and quit.

  build_c4d/bin/blender.exe --python tools/fork_setup_startup.py
"""

import bpy

STEP = {"n": 0}


def tick():
    STEP["n"] += 1
    win = bpy.context.window_manager.windows[0]
    if STEP["n"] == 1:
        bpy.ops.c4d.apply_theme()
        with bpy.context.temp_override(window=win):
            bpy.ops.c4d.setup_workspace()
        return 4.0  # layout is rebuilt over several timer ticks
    if STEP["n"] == 2:
        ws = bpy.data.workspaces.get("C4D")
        print("C4D workspace:", ws is not None, "palette:", getattr(win.screen, "show_c4d_palette", None))
        bpy.ops.wm.save_homefile()
        bpy.ops.wm.save_userpref()
        print("STARTUP_SAVED")
        bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(tick, first_interval=4.0)
