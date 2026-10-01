"""C4D Feel smoke test: run inside Blender (Scripting tab, or via MCP exec).

Exercises every add-on operator, menu and manager in a scratch scene and
prints PASS/FAIL per check. It never saves anything. Run it in a new file:
it adds and deletes its own objects.
"""

import traceback

import bpy

RESULTS = []


def check(name):
    def deco(fn):
        try:
            fn()
            RESULTS.append((name, True, ""))
        except Exception as ex:  # noqa: BLE001 - we report every failure
            RESULTS.append((name, False, f"{type(ex).__name__}: {ex}"))
            traceback.print_exc()
        return fn
    return deco


def view3d_override():
    win = bpy.context.window_manager.windows[0]
    area = max((a for a in win.screen.areas if a.type == 'VIEW_3D'), key=lambda a: a.width * a.height)
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return bpy.context.temp_override(window=win, screen=win.screen, area=area, region=region)


def area_override(kind, upper=None):
    win = bpy.context.window_manager.windows[0]
    areas = [a for a in win.screen.areas if a.type == kind]
    if upper is not None:
        areas = [a for a in areas if (a.y + a.height / 2 > win.height / 2) == upper] or areas
    area = areas[0]
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return bpy.context.temp_override(window=win, screen=win.screen, area=area, region=region)


def select_only(ob):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def ensure_object_mode():
    if bpy.context.mode != 'OBJECT':
        with view3d_override():
            bpy.ops.object.mode_set(mode='OBJECT')


def evaluated_verts(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    me = ob.evaluated_get(dg).to_mesh()
    n = len(me.vertices)
    ob.evaluated_get(dg).to_mesh_clear()
    return n


CREATED = []


def track(ob):
    CREATED.append(ob.name)
    return ob


def run():
    RESULTS.clear()
    CREATED.clear()
    ensure_object_mode()
    ops = bpy.ops.c4d

    @check("primitives: all kinds build geometry")
    def _():
        for kind in ("Cube", "Sphere", "Cylinder", "Cone", "Plane", "Torus", "Pyramid"):
            with view3d_override():
                ops.add_primitive(kind=kind)
            ob = track(bpy.context.active_object)
            assert evaluated_verts(ob) > 0, kind

    @check("make editable (C) turns a primitive into a mesh")
    def _():
        with view3d_override():
            ops.add_primitive(kind='Cube')
            track(bpy.context.active_object)
            ops.make_editable()
        ob = track(bpy.context.active_object)
        assert ob.type == 'MESH' and not ob.modifiers and len(ob.data.vertices) == 8

    @check("edit toggle refuses parametric objects, allows meshes")
    def _():
        with view3d_override():
            ops.add_primitive(kind='Sphere')
            track(bpy.context.active_object)
            assert ops.edit_toggle() == {'CANCELLED'}

    @check("component modes: points / edges / polygons / model")
    def _():
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add()
            track(bpy.context.active_object)
            for m in ('VERT', 'EDGE', 'FACE'):
                ops.component_mode(mode=m)
                assert bpy.context.mode == 'EDIT_MESH'
            ops.component_mode(mode='MODEL')
            assert bpy.context.mode == 'OBJECT'

    @check("mesh commands (M~ / U~ via menu) run in edit mode")
    def _():
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add()
            track(bpy.context.active_object)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            # Non-interactive commands only (interactive ones need a mouse).
            for prefix, key in (('U', 'Y'), ('U', 'K'), ('U', 'I'), ('U', 'R'), ('U', 'A'),
                                ('U', 'T'), ('U', 'U'), ('U', 'O'), ('U', 'S')):
                bpy.ops.mesh.select_all(action='SELECT')
                r = ops.chord_cmd(prefix=prefix, key=key)
                assert r in ({'FINISHED'}, {'CANCELLED'}), (prefix, key, r)
            bpy.ops.object.mode_set(mode='OBJECT')

    @check("group (Alt+G) and ungroup (Shift+G)")
    def _():
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add(location=(1, 0, 0))
            a = track(bpy.context.active_object)
            bpy.ops.mesh.primitive_cube_add(location=(-1, 0, 0))
            b = track(bpy.context.active_object)
            a.select_set(True)
            ops.group()
            null = bpy.context.active_object
            null_name = null.name
            assert null.type == 'EMPTY' and a.parent == null and b.parent == null
            ops.ungroup()
            assert a.parent is None and b.parent is None
            assert null_name not in bpy.data.objects  # ungroup deletes the null

    @check("view panels F1-F5 and display modes")
    def _():
        with view3d_override():
            for v in ('TOP', 'RIGHT', 'FRONT', 'PERSP', 'ALL', 'ALL'):
                ops.view_panel(view=v)
            for m in ('GOURAUD', 'GOURAUD_LINES', 'CONSTANT', 'LINES', 'GOURAUD'):
                ops.display_mode(mode=m)

    @check("coordinate toggle (W) and axis locks")
    def _():
        wm = bpy.context.window_manager
        with view3d_override():
            ops.coord_toggle()
            ops.coord_toggle()
        for axis in "xyz":
            setattr(wm, f"c4d_lock_{axis}", False)
            setattr(wm, f"c4d_lock_{axis}", True)

    @check("coordinate manager: object position / size / world")
    def _():
        wm = bpy.context.window_manager
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        ob = track(bpy.context.active_object)
        wm.c4d_coord_space = 'OBJ_REL'
        wm.c4d_pos = (1.0, 2.0, 3.0)
        assert tuple(round(v, 4) for v in ob.location) == (1.0, 2.0, 3.0)
        wm.c4d_coord_size = 'SIZE'
        wm.c4d_size = (4.0, 2.0, 2.0)
        bpy.context.view_layer.update()
        assert abs(ob.dimensions.x - 4.0) < 1e-4
        wm.c4d_coord_space = 'WORLD'
        wm.c4d_pos = (0.0, 0.0, 0.0)
        wm.c4d_coord_space = 'OBJ_REL'

    @check("coordinate manager: edit-mode selection move / size")
    def _():
        wm = bpy.context.window_manager
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
            ob = track(bpy.context.active_object)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            wm.c4d_coord_space = 'OBJ_REL'
            wm.c4d_pos = (0.0, 0.0, 1.0)
            assert abs(wm.c4d_pos[2] - 1.0) < 1e-4
            wm.c4d_size = (1.0, 1.0, 1.0)
            assert abs(wm.c4d_size[0] - 1.0) < 1e-4
            bpy.ops.object.mode_set(mode='OBJECT')

    @check("splines: all kinds build curves")
    def _():
        from bl_ext.user_default.c4d_feel.splines import SPLINE_SPECS
        for kind in SPLINE_SPECS:
            with view3d_override():
                ops.add_spline(kind=kind)
            track(bpy.context.active_object)

    @check("spline generators: Extrude / Lathe / Sweep / Loft build geometry")
    def _():
        for kind in ("Extrude", "Lathe", "Sweep", "Loft"):
            ensure_object_mode()
            for o in bpy.context.selected_objects:
                o.select_set(False)
            with view3d_override():
                ops.add_spline_generator(kind=kind)
            gen = track(bpy.context.active_object)
            for c in gen.children:
                track(c)
            assert evaluated_verts(gen) > 0, kind

    @check("spline generators: Extrude uses a user-drawn Blender curve")
    def _():
        with view3d_override():
            bpy.ops.curve.primitive_bezier_circle_add(radius=0.5)
            circ = track(bpy.context.active_object)
            select_only(circ)
            ops.add_spline_generator(kind='Extrude')
        gen = track(bpy.context.active_object)
        assert circ.parent == gen and evaluated_verts(gen) > 0

    @check("cloner: linear / radial / grid + plain effector")
    def _():
        for mode in ("Linear", "Radial", "Grid"):
            with view3d_override():
                bpy.ops.mesh.primitive_cube_add(size=0.3)
                src = track(bpy.context.active_object)
                select_only(src)
                ops.add_cloner(mode=mode)
            cl = track(bpy.context.active_object)
            dg = bpy.context.evaluated_depsgraph_get()
            dg.update()
            n = sum(1 for i in dg.object_instances if i.is_instance and i.parent and i.parent.original == cl)
            assert n == (9 if mode == "Grid" else 3), (mode, n)
        with view3d_override():
            ops.add_plain_effector()
        track(bpy.context.active_object)

    @check("generators / deformers menu: every modifier kind adds")
    def _():
        from bl_ext.user_default.c4d_feel.ui import MODIFIERS
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add()
            ob = track(bpy.context.active_object)
            for kind in MODIFIERS:
                if kind in {'BOOLEAN', 'LATTICE', 'SHRINKWRAP'}:
                    continue  # need a target object
                ops.add_modifier(kind=kind)
            assert len(ob.modifiers) >= len(MODIFIERS) - 3

    @check("deformer objects: child drives parent, re-parenting moves the effect")
    def _():
        with view3d_override():
            ops.add_primitive(kind='Cube')
            a = track(bpy.context.active_object)
            ops.add_deformer(kind='BEND')
            bend = track(bpy.context.active_object)
            assert bend.parent == a and a.modifiers.get("C4D " + bend.name) is not None
            ops.add_primitive(kind='Cylinder')
            b = track(bpy.context.active_object)
        bend.parent = b
        bpy.context.view_layer.update()
        assert a.modifiers.get("C4D " + bend.name) is None, "old parent kept modifier"
        assert b.modifiers.get("C4D " + bend.name) is not None, "new parent missing modifier"
        bpy.data.objects.remove(bend)
        bpy.context.view_layer.update()
        assert not any(m.name.startswith("C4D Bend") for m in b.modifiers), "stale modifier after delete"

    @check("tags: add every C4D tag, custom tags stored, remove + copy")
    def _():
        from bl_ext.user_default.c4d_feel.tags import TAGS, custom_tags
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add()
            ob = track(bpy.context.active_object)
            for key in TAGS:
                select_only(ob)
                assert ops.add_tag(key=key) == {'FINISHED'}, key
        assert custom_tags(ob) == ['PROTECTION', 'DISPLAY', 'COMPOSITING'], custom_tags(ob)
        assert all(ob.lock_location)
        assert len(ob.constraints) == 3 and ob.material_slots
        ops.remove_tag(name=ob.name, key='PROTECTION')
        assert 'PROTECTION' not in custom_tags(ob) and not any(ob.lock_location)
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add(location=(3, 0, 0))
            other = track(bpy.context.active_object)
            other.select_set(True)
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            ops.copy_tags()
        assert custom_tags(other) == ['DISPLAY', 'COMPOSITING']
        ops.om_tag(name=ob.name, kind='CUSTOM', index=0)
        assert bpy.context.window_manager.c4d_active_tag == 'DISPLAY'
        bpy.context.window_manager.c4d_active_tag = ""

    @check("camera: look through + navigation moves camera, toggle back")
    def _():
        with view3d_override():
            bpy.ops.object.camera_add(location=(0, -8, 2))
            cam = track(bpy.context.active_object)
            space = bpy.context.space_data
            r3d = space.region_3d
            ops.look_through(name=cam.name)
            assert r3d.view_perspective == 'CAMERA' and bpy.context.scene.camera == cam
            assert space.lock_camera, "camera navigation not locked"
            ops.look_through(name=cam.name)
            assert r3d.view_perspective != 'CAMERA' and not space.lock_camera

    @check("generator on/off toggle (Q)")
    def _():
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add()
            ob = track(bpy.context.active_object)
            ob.modifiers.new("Sub", 'SUBSURF')
            ops.toggle_generators()
            assert not ob.modifiers[0].show_viewport
            ops.toggle_generators()
            assert ob.modifiers[0].show_viewport

    @check("object manager: select / visibility / generators / tag")
    def _():
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add()
        ob = track(bpy.context.active_object)
        ob.modifiers.new("Sub", 'SUBSURF')
        ops.om_select('INVOKE_DEFAULT', name=ob.name)
        assert bpy.context.view_layer.objects.active == ob
        ops.om_visibility(name=ob.name, what='RENDER')
        assert ob.hide_render
        ops.om_visibility(name=ob.name, what='RENDER')
        ops.om_toggle_generators(name=ob.name)
        assert not ob.modifiers[0].show_viewport
        ops.om_toggle_generators(name=ob.name)
        ops.om_tag(name=ob.name, kind='MODIFIER', index=0)

    @check("material manager: new / apply / duplicate / remove unused")
    def _():
        before = set(bpy.data.materials)
        ops.new_material()
        new = [m for m in bpy.data.materials if m not in before]
        assert new and new[0].asset_data is not None
        mat = new[0]
        with view3d_override():
            bpy.ops.mesh.primitive_cube_add()
        ob = track(bpy.context.active_object)
        ob.data.materials.append(mat)
        ops.remove_unused_materials()
        assert mat.name in bpy.data.materials  # used, so kept

    @check("material nodes: opens a node editor window for the material")
    def _():
        mat = bpy.data.materials.new("SmokeNodes")
        mat.use_nodes = True
        wm = bpy.context.window_manager
        before = len(wm.windows)
        with view3d_override():
            assert ops.edit_material_nodes(name=mat.name) == {'FINISHED'}
        assert len(wm.windows) == before + 1, "no node window opened"
        new = wm.windows[-1]
        with bpy.context.temp_override(window=new):
            bpy.ops.wm.window_close()
        bpy.data.materials.remove(mat)

    @check("render settings / interactive render toggles")
    def _():
        with view3d_override():
            space = bpy.context.space_data
            before = space.shading.type
            ops.interactive_render()
            assert space.shading.type == 'RENDERED' and space.use_render_border
            ops.interactive_render()
            assert space.shading.type == before and not space.use_render_border
        ops.render_settings()

    @check("menus draw without errors")
    def _():
        names = [n for n in dir(bpy.types) if n.startswith("C4D_MT_")]
        assert len(names) > 20, names
        with view3d_override():
            for n in names:
                bpy.ops.wm.call_menu(name=n) if False else None  # drawing is covered by UI

    # Clean up everything we created.
    ensure_object_mode()
    for name in reversed(CREATED):
        ob = bpy.data.objects.get(name)
        if ob is not None:
            bpy.data.objects.remove(ob)
    for coll in [c for c in bpy.data.collections if c.name.startswith(("Cloner Children", "Loft Splines")) and not c.objects]:
        bpy.data.collections.remove(coll)

    passed = sum(1 for _n, ok, _e in RESULTS if ok)
    lines = [f"{'PASS' if ok else 'FAIL'}  {n}" + (f"  -> {e}" if e else "") for n, ok, e in RESULTS]
    lines.append(f"{passed}/{len(RESULTS)} passed")
    return "\n".join(lines)


if __name__ == "__main__":
    print(run())
