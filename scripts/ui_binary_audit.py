#!/usr/bin/env python3
"""Read-only, hash-gated bytecode inventory of the MTR 4.1.0-beta.2 renderer.

Does not execute Minecraft, instantiate mod classes or touch game data.
The JSON contains only normalized class names, method-reference checks, and counts.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

EXPECTED_SHA256 = "5da075f7d63daea89da17348ace0959a0c216cbaf14a322d063a64bec44aae94"
CLASSES = (
    "org.mtr.render.MainRenderer",
    "org.mtr.render.RenderVehicles",
    "org.mtr.render.RenderRails",
    "org.mtr.render.RenderLifts",
    "org.mtr.render.WorkerThread",
    "org.mtr.client.DynamicTextureCache",
    "org.mtr.model.ModelLoaderBase",
    "org.mtr.model.NewOptimizedModel",
    "org.mtr.model.NewOptimizedModelGroup",
    "org.mtr.model.ObjModelLoader",
    "org.mtr.model.BlockbenchModelLoader",
    "org.mtr.model.BuiltVehicleModelHolder",
    "org.mtr.resource.VehicleResource",
    "org.mtr.client.CustomResourceLoader",
    "org.mtr.render.MoreRenderLayers",
)
# Exact bytecode references. These are structural facts, not runtime timings.
CHECKS = {
    "main_calls_vehicles": ("org.mtr.render.MainRenderer", "Method org/mtr/render/RenderVehicles.render:"),
    "main_calls_rails": ("org.mtr.render.MainRenderer", "Method org/mtr/render/RenderRails.render:"),
    "main_calls_passengers": ("org.mtr.render.MainRenderer", "Method org/mtr/render/RenderPassengers.render:"),
    "main_ticks_texture_cache": ("org.mtr.render.MainRenderer", "Method org/mtr/client/DynamicTextureCache.tick:"),
    "vehicles_distance_check": ("org.mtr.render.RenderVehicles", "Method org/mtr/tool/CullingHelper.getDistanceFromCamera:"),
    "vehicles_new_random": ("org.mtr.render.RenderVehicles", "Method java/util/Random.\"<init>\":"),
    "vehicles_new_remote_player": ("org.mtr.render.RenderVehicles", "class net/minecraft/class_745"),
    "rails_box_distance_check": ("org.mtr.render.RenderRails", "Method org/mtr/tool/CullingHelper.getDistanceFromCameraToBox:"),
    "lifts_request_occlusion": ("org.mtr.render.RenderLifts", "Method org/mtr/render/WorkerThread.scheduleLifts:"),
    "worker_has_vehicle_occlusion_api": ("org.mtr.render.WorkerThread", "scheduleVehicles("),
    "worker_has_texture_queue_api": ("org.mtr.render.WorkerThread", "scheduleDynamicTextures("),
    "texture_dispatches_worker": ("org.mtr.client.DynamicTextureCache", "Method org/mtr/render/WorkerThread.scheduleDynamicTextures:"),
    "texture_creates_dynamic_texture": ("org.mtr.client.DynamicTextureCache", "class net/minecraft/class_1043"),
    "models_have_vertex_buffer_upload": ("org.mtr.model.NewOptimizedModel", "Method net/minecraft/class_291.method_1352:"),
    "models_have_vertex_buffer_draw": ("org.mtr.model.NewOptimizedModel", "Method net/minecraft/class_291.method_35665:"),
    "obj_parser_async": ("org.mtr.model.ObjModelLoader", "java/util/concurrent/ExecutorService.submit:"),
}
def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def audit(jar, javap):
    digest = sha256(jar)
    if digest != EXPECTED_SHA256:
        raise ValueError(f"JAR digest mismatch: {digest}; expected {EXPECTED_SHA256}")
    bytecode = {}
    results = {}
    for cls in CLASSES:
        p = subprocess.run(
            [str(javap), "-c", "-p", "-classpath", str(jar), cls],
            check=True, capture_output=True, text=True, timeout=60,
        )
        bytecode[cls] = p.stdout
        results[cls] = {
            "bytecode_instruction_lines": len(re.findall(r"(?m)^\s+\d+:\s+\w+", p.stdout)),
            "method_declarations_approx": len(re.findall(r"(?m)^  (?:public|private|protected|static).*\);$", p.stdout)),
        }
    checks = {name: {"present": needle in bytecode[cls], "class": cls, "searched_text": needle}
              for name, (cls, needle) in CHECKS.items()}
    # A zero means this limited class's javap text has no such reference.
    evidence_counts = {
        "vehicles_distance_helper_references": bytecode["org.mtr.render.RenderVehicles"].count("Method org/mtr/tool/CullingHelper.getDistanceFromCamera:"),
        "vehicles_frustum_token_references": len(re.findall("frustum|Frustum|class_4604", bytecode["org.mtr.render.RenderVehicles"])),
        "vehicles_random_constructor_references": bytecode["org.mtr.render.RenderVehicles"].count('Method java/util/Random."<init>":'),
        "model_vertex_draw_method_references": bytecode["org.mtr.model.NewOptimizedModel"].count("Method net/minecraft/class_291.method_35665:"),
        "model_vertex_upload_method_references": bytecode["org.mtr.model.NewOptimizedModel"].count("Method net/minecraft/class_291.method_1352:"),
        "worker_vehicle_culling_call_references_in_renderer": bytecode["org.mtr.render.RenderVehicles"].count("WorkerThread.scheduleVehicles:"),
    }
    return {
        "release_sha256": digest,
        "method": "JDK 21 javap -c -p on the exact distributed JAR; no client executed",
        "interpretation": "STATIC BYTECODE COUNTS ONLY. Not draw calls per frame, GPU operations, CPU time, FPS or proven source provenance.",
        "class_inventory": results,
        "structural_checks": checks,
        "static_reference_counts": evidence_counts,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--jdk", type=Path, required=True, help="directory containing bin/javap")
    parser.add_argument("--output", type=Path, default=Path("audits/ui-binary-evidence.json"))
    args = parser.parse_args()
    report = audit(args.jar.resolve(), (args.jdk / "bin/javap").resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"sha256": report["release_sha256"],
                      "classes": len(report["class_inventory"]),
                      "checks_passed": sum(v["present"] for v in report["structural_checks"].values()),
                      "checks_total": len(report["structural_checks"]),
                      "static_counts": report["static_reference_counts"]}, indent=2))
    if not all(v["present"] for v in report["structural_checks"].values()):
        raise SystemExit("Some expected structural references absent: inspect JSON (no claim of a failed runtime test).")

if __name__ == "__main__":
    main()
