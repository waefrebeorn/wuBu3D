import json, pathlib, subprocess, sys
sys.path.insert(0, '/opt/data/work/wubu3d')
import wubu3d as W

def run(spec_path, label):
    spec = W.load_spec(pathlib.Path(spec_path))
    data = W.build_raster_scene(spec, 1)
    out = {}
    for tag, args in (("cull", []), ("nocull", ["--no-cull"])):
        d = pathlib.Path(f"/opt/data/work/wubu3d/out/cull_cmp/{label}_{tag}")
        d.mkdir(parents=True, exist_ok=True)
        r = subprocess.run([str(W.RASTER_BIN), str(d) + "/"] + args, input=data, capture_output=True)
        line = [l for l in r.stderr.decode().splitlines() if l.startswith("wuburaster:")][-1]
        print(f"{label:14s} {tag:7s} {line}")
        out[tag] = line
    return out

run("/opt/data/work/wubu3d/specs/demo_moves.json", "moves")
run("/opt/data/work/wubu3d/specs/demo_oit.json", "oit")

# heavy variant: 400 towers to push the triangle count up
spec = json.loads(pathlib.Path("/opt/data/work/wubu3d/specs/demo_moves.json").read_text())
spec["name"] = "demo_heavy"
spec["props"]["towers"] = 400
spec["props"]["rocks"] = 120
pathlib.Path("/opt/data/work/wubu3d/specs/demo_heavy.json").write_text(json.dumps(spec, indent=1))
run("/opt/data/work/wubu3d/specs/demo_heavy.json", "heavy")
