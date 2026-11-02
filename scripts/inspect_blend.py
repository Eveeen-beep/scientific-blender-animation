"""Blender-only read-only inventory. Never saves, renders, opens or builds a scene.

Run after loading a file via Blender CLI, then -- --output new_report.json.
This reports existing data; it does not prove evaluated animation correctness.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import bpy


def animation_summary(block):
    ad = getattr(block, 'animation_data', None)
    if ad is None:
        return None
    return {
        'action': ad.action.name if ad.action else None,
        'action_slot': getattr(getattr(ad, 'action_slot', None), 'identifier', None),
        'nla_tracks': [t.name for t in ad.nla_tracks],
        'drivers': [
            {'data_path': d.data_path, 'array_index': d.array_index,
             'type': d.driver.type, 'expression': d.driver.expression}
            for d in ad.drivers
        ],
    }


def resource(kind, block):
    raw = getattr(block, 'filepath', '')
    if not raw or raw.startswith('<builtin'):
        return None
    resolved = bpy.path.abspath(raw, library=getattr(block, 'library', None))
    return {'kind': kind, 'name': block.name, 'path': raw,
            'resolved_path': resolved, 'exists': Path(resolved).exists(),
            'relative': raw.startswith('//'),
            'packed': bool(getattr(block, 'packed_file', None)
                           or getattr(block, 'packed_files', None))}


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path,
                        help='New JSON report. Existing files are never overwritten.')
    args = parser.parse_args(argv)
    output = args.output.expanduser().resolve()
    if output.suffix.lower() != '.json':
        parser.error('Output must be a new .json report, never a .blend or asset.')
    if output.exists():
        parser.error('Report already exists; choose a new report path.')
    scene = bpy.context.scene
    r = scene.render
    resources = []
    for kind, blocks in [('image', bpy.data.images), ('font', bpy.data.fonts),
                         ('library', bpy.data.libraries), ('cache', bpy.data.cache_files),
                         ('movie', bpy.data.movieclips), ('sound', bpy.data.sounds),
                         ('text_origin', bpy.data.texts)]:
        for block in blocks:
            if kind == 'image' and block.source in {'GENERATED', 'VIEWER'}:
                continue
            item = resource(kind, block)
            if item:
                resources.append(item)
    objects = []
    for o in sorted(scene.objects, key=lambda x: x.name):
        objects.append({
            'name': o.name, 'type': o.type, 'parent': o.parent.name if o.parent else None,
            'location': list(o.location), 'rotation_mode': o.rotation_mode,
            'rotation_euler': list(o.rotation_euler), 'scale': list(o.scale),
            'matrix_world': [list(row) for row in o.matrix_world],
            'dimensions': list(o.dimensions), 'hide_render': o.hide_render,
            'constraints': [{'name': c.name, 'type': c.type,
                             'target': getattr(getattr(c, 'target', None), 'name', None)}
                            for c in o.constraints],
            'modifiers': [{'name': m.name, 'type': m.type} for m in o.modifiers],
            'animation': animation_summary(o),
            'data_animation': animation_summary(o.data) if o.data else None,
            'shape_key_animation': animation_summary(getattr(o.data, 'shape_keys', None)) if o.data else None,
        })
    fps = r.fps / r.fps_base
    report = {
        'mode': 'inventory_only_no_save_no_render', 'process_id': os.getpid(),
        'blender_version': bpy.app.version_string, 'binary': bpy.app.binary_path,
        'background': bpy.app.background, 'file': bpy.data.filepath,
        'saved_file_version': list(bpy.data.version), 'is_dirty': bpy.data.is_dirty,
        'scene': scene.name, 'camera': scene.camera.name if scene.camera else None,
        'current_frame': scene.frame_current, 'subframe': scene.frame_subframe,
        'frame_range': [scene.frame_start, scene.frame_end], 'frame_step': scene.frame_step,
        'fps_numerator': r.fps, 'fps_base': r.fps_base, 'effective_fps': fps,
        'duration_seconds_if_step_one': (scene.frame_end - scene.frame_start + 1) / fps,
        'unit_system': scene.unit_settings.system, 'unit_scale': scene.unit_settings.scale_length,
        'engine': r.engine, 'resolution': [r.resolution_x, r.resolution_y],
        'resolution_percentage': r.resolution_percentage,
        'pixel_aspect': [r.pixel_aspect_x, r.pixel_aspect_y], 'output_path': r.filepath,
        'color_management': {'view_transform': scene.view_settings.view_transform,
                             'look': scene.view_settings.look,
                             'exposure': scene.view_settings.exposure,
                             'gamma': scene.view_settings.gamma},
        'autoexec_fail': getattr(bpy.app, 'autoexec_fail', None),
        'autoexec_fail_message': getattr(bpy.app, 'autoexec_fail_message', None),
        'object_count': len(objects), 'material_count': len(bpy.data.materials),
        'objects': objects, 'resources': resources,
        'limitations': ['No frame sweep, mesh fingerprint, pixel check or physical validation.',
                        'Python auto-execution may be disabled; transforms are not proof of working drivers.',
                        'Text file paths can be historical metadata; missing path does not prove missing embedded code.'],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print('READ_ONLY_INVENTORY_WRITTEN', str(output), flush=True)


if __name__ == '__main__':
    main()
