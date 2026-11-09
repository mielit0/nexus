import sys, os
from PIL import Image, ImageStat

SRC, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)

# slug: (ratio w/h, {index: "pad" | focus_y float 0..1 | ("x", focus_x)}, [dropped indexes])
SPEC = {
    "nx-arpanet-lo":       (1.0, {1: ("x", 0.45), 3: ("x", 0.8)}, []),
    "nx-atari-burial":     (3/2, {}, []),
    "nx-baarle":           (1.0, {1: 0.75, 4: 0.7}, []),
    "nx-bibendum":         (4/5, {3: "pad"}, []),
    "nx-blood-falls":      (3/2, {1: ("x", 0.55)}, []),
    "nx-computer-space":   (1.0, {1: 0.1}, []),
    "nx-en-l-an-2000":     (3/2, {}, []),
    "nx-fairy-circles":    (3/2, {}, []),
    "nx-fallen-astronaut": (1.0, {}, []),
    "nx-first-selfie":     (3/4, {}, [2]),
    "nx-ghost-army":       (4/3, {2: "pad", 4: "pad"}, []),
    "nx-moon-trees":       (3/4, {2: 0.6}, []),
    "nx-nakagin":          (1.0, {}, []),
    "nx-pigeon-cameras":   (4/3, {4: "padk"}, []),
    "nx-pitch-drop":       (4/5, {}, []),
    "nx-trottoir-roulant": (1.0, {3: 0.4}, []),
    "nx-venus-basket":     (3/2, {}, []),
    "nx-wienermobile":     (3/2, {}, []),
    "nx-dancing-plague":   (1.0, {}, []),
    "nx-dymaxion-car":     (3/2, {4: "pad"}, []),
}

def edge_color(im):
    w, h = im.size
    strips = [im.crop((0, 0, w, 4)), im.crop((0, h - 4, w, h)), im.crop((0, 0, 4, h)), im.crop((w - 4, 0, w, h))]
    cols = [ImageStat.Stat(s).median for s in strips]
    return tuple(int(sum(c[i] for c in cols) / 4) for i in range(3))

def process(im, ratio, mode):
    W = 1080
    H = round(W / ratio)
    if mode in ("pad", "padk"):
        s = min(W / im.width, H / im.height)
        r = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        out = Image.new("RGB", (W, H), (0, 0, 0) if mode == "padk" else edge_color(im))
        out.paste(r, ((W - r.width) // 2, (H - r.height) // 2))
        return out
    fy, fx = 0.5, 0.5
    if isinstance(mode, float):
        fy = mode
    elif isinstance(mode, tuple):
        fx = mode[1]
    s = max(W / im.width, H / im.height)
    r = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l = round((r.width - W) * fx)
    t = round((r.height - H) * fy)
    return r.crop((l, t, l + W, t + H))

report = []
for slug, (ratio, modes, drop) in SPEC.items():
    files = sorted(f for f in os.listdir(SRC) if f.rsplit("-", 1)[0] == slug)
    n = 0
    for f in files:
        idx = int(f.rsplit("-", 1)[1].split(".")[0])
        if idx in drop:
            continue
        n += 1
        im = Image.open(os.path.join(SRC, f)).convert("RGB")
        out = process(im, ratio, modes.get(idx))
        name = f"{slug}-{n:02d}.jpg"
        out.save(os.path.join(DST, name), "JPEG", quality=90)
        report.append(f"{name} {out.width}x{out.height} (from {f} {im.width}x{im.height})")
print("\n".join(report))
