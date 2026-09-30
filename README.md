# C4D Feel

A Blender 5.2 extension that makes Blender look and work like Cinema 4D R24, without removing any Blender features.

## Install

1. Build the zip (see below), or grab `dist/c4d_feel-<version>.zip`.
2. In Blender, go to Edit > Preferences > Get Extensions > the ▾ menu > Install from Disk, and pick the zip.
3. In the add-on preferences, click **Create C4D Workspace**, then **Apply C4D Theme**.

## What it does

- **Hotkeys:** C4D R24 keys, including Alt/1/2/3 navigation, E/R/T tools, and the M~/U~/K~/N~ two-key commands (a HUD shows the second keys). There's a V pie menu, and all of it can be switched off in the preferences.
- **Layout:** a "C4D" workspace with:
  - the C4D menu bar and command palette;
  - a mode palette on top of Blender's toolbar;
  - an Object Manager (custom, or Blender's Outliner on its own tab);
  - an Attribute Manager with Basic/Coord./Object tabs;
  - a Material Manager and Coordinate Manager;
  - the timeline.
- **Parametric objects:** primitives (Cube, Sphere, Cylinder, Cone, Plane, Torus, Pyramid) and splines (Circle, Rectangle, Star, Arc, Helix). Press C to make them editable.
- **Generators:** Extrude, Lathe, Sweep and Loft, which work on child splines. Also a Cloner (Linear/Radial/Grid) with Random and Plain effectors.
- **Theme:** R24 colours.

Every other workspace keeps stock Blender.

## Develop

- Regenerate icons: `python tools/make_icons.py`
- Build the zip: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" --command extension build --source-dir c4d_feel --output-dir dist`

The icons are original artwork. No Maxon assets are included.
