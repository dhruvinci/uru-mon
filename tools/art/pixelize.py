"""Turns large AI-generated "pixel-art style" images into real low-resolution sprites.

Steps: alpha-crop to the subject, pad to the target aspect, box-downscale, hard alpha, palette-quantize,
and re-outline with a dark edge so silhouettes stay crisp at native size.

Usage (library): pixelize(img, size=(64, 64), colors=24) -> Image
CLI: python3 tools/art/pixelize.py <in.png> <out.png> [W H] [colors]
"""
import sys

import numpy as np
from PIL import Image

OUTLINE = (42, 34, 48, 255)


def remove_flat_background(img, tol=28):
    """If the image has no real transparency, flood-fill the border colour to transparent."""
    img = img.convert("RGBA")
    a = np.array(img)
    if (a[:, :, 3] < 250).mean() > 0.05:
        return img
    h, w = a.shape[:2]
    corner = a[0, 0, :3].astype(int)
    diff = np.abs(a[:, :, :3].astype(int) - corner).sum(axis=2) <= tol
    mask = np.zeros((h, w), bool)
    stack = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    while stack:
        y, x = stack.pop()
        if y < 0 or x < 0 or y >= h or x >= w or mask[y, x] or not diff[y, x]:
            continue
        mask[y, x] = True
        stack.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    a[mask, 3] = 0
    return Image.fromarray(a)


def crop_to_subject(img, threshold=40):
    a = np.array(img)
    ys, xs = np.where(a[:, :, 3] > threshold)
    if len(xs) == 0:
        return img
    return img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def fit_canvas(img, size, margin, anchor_bottom):
    tw, th = size
    inner_w, inner_h = tw - 2 * margin, th - 2 * margin
    w, h = img.size
    scale = min(inner_w / w, inner_h / h)
    # work at 8x the target so the box downscale averages cleanly
    big = (max(1, round(w * scale * 8)), max(1, round(h * scale * 8)))
    img = img.resize(big, Image.LANCZOS)
    canvas = Image.new("RGBA", (tw * 8, th * 8), (0, 0, 0, 0))
    x = (tw * 8 - big[0]) // 2
    y = (th * 8 - big[1] - margin * 8) if anchor_bottom else (th * 8 - big[1]) // 2
    canvas.alpha_composite(img, (x, y))
    return canvas


def box_down(img, size):
    a = np.array(img).astype(np.float64)
    tw, th = size
    a = a.reshape(th, a.shape[0] // th, tw, a.shape[1] // tw, 4)
    alpha = a[..., 3:4]
    weight = alpha.sum(axis=(1, 3))
    rgb = (a[..., :3] * alpha).sum(axis=(1, 3)) / np.maximum(weight, 1e-6)
    out_a = alpha.mean(axis=(1, 3))
    return np.concatenate([rgb, out_a], axis=2)


def quantize(arr, colors):
    rgb = np.clip(arr[..., :3], 0, 255).astype(np.uint8)
    solid = arr[..., 3] >= 110
    img = Image.fromarray(rgb, "RGB")
    pal_img = img.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE)
    q = np.array(pal_img.convert("RGB"))
    out = np.zeros(arr.shape[:2] + (4,), np.uint8)
    out[..., :3] = q
    out[..., 3] = np.where(solid, 255, 0)
    return out


def outline(out):
    """Give every opaque pixel that touches transparency on its outer edge a dark outline pixel next to it."""
    h, w = out.shape[:2]
    solid = out[..., 3] > 0
    grown = solid.copy()
    grown[1:, :] |= solid[:-1, :]
    grown[:-1, :] |= solid[1:, :]
    grown[:, 1:] |= solid[:, :-1]
    grown[:, :-1] |= solid[:, 1:]
    edge = grown & ~solid
    out[edge] = OUTLINE
    return out


def darken_existing_edges(out, amount=0.55):
    """Darken the outermost ring of the subject so the AI's soft outline becomes a crisp line."""
    solid = out[..., 3] > 0
    inner = solid.copy()
    inner[1:, :] &= solid[:-1, :]
    inner[:-1, :] &= solid[1:, :]
    inner[:, 1:] &= solid[:, :-1]
    inner[:, :-1] &= solid[:, 1:]
    ring = solid & ~inner
    rgb = out[..., :3].astype(np.float64)
    lum = rgb.mean(axis=2)
    dark = ring & (lum > 70)
    rgb[dark] = rgb[dark] * amount + np.array(OUTLINE[:3]) * (1 - amount)
    out[..., :3] = rgb.astype(np.uint8)
    return out


def pixelize(img, size=(64, 64), colors=24, margin=1, anchor_bottom=True, add_outline=False):
    img = remove_flat_background(img)
    img = crop_to_subject(img)
    big = fit_canvas(img, size, margin, anchor_bottom)
    arr = box_down(big, size)
    out = quantize(arr, colors)
    out = darken_existing_edges(out)
    if add_outline:
        out = outline(out)
    return Image.fromarray(out, "RGBA")


def smooth(img, size, margin=4, anchor_bottom=True):
    """High-resolution version framed exactly like pixelize() at size / 4: same crop, margin and anchor, but a smooth
    downscale with no palette reduction. Used for the large battle sprites."""
    img = remove_flat_background(img)
    img = crop_to_subject(img)
    big = fit_canvas(img, size, margin, anchor_bottom)
    return big.resize(size, Image.LANCZOS)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 64
    h = int(sys.argv[4]) if len(sys.argv) > 4 else w
    c = int(sys.argv[5]) if len(sys.argv) > 5 else 24
    pixelize(Image.open(src), (w, h), c).save(dst)
