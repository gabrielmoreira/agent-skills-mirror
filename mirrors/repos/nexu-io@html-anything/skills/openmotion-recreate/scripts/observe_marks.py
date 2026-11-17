"""Observe source mark size, brightness and spatial spread at selected times.

Run through vision-tools.mjs. Measurements describe thresholded image features.
The caller selects the subject, excludes overlays and interprets its mechanism.
"""

import argparse
import json
import math
from pathlib import Path

from register_motion import rectangle


def quantiles(values):
    import numpy as np

    if len(values) == 0:
        return None
    return dict(zip(['p10', 'p50', 'p90'], map(float, np.percentile(values, [10, 50, 90]))))


def observe(image, roi, excluded=(), threshold=.3, matte='black', min_area=2, max_area_fraction=.02, origin=None):
    import cv2
    import numpy as np

    x, y, width, height = roi
    if min(x, y) < 0 or min(width, height) <= 0 or x + width > image.shape[1] or y + height > image.shape[0]:
        raise ValueError('The observation region must fit inside the source frame.')
    region = image[y:y + height, x:x + width]
    strength = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    if matte == 'white':
        strength = 1 - strength
    included = np.ones((height, width), dtype=bool)
    for left, top, box_width, box_height in excluded:
        x0, x1 = max(0, left - x), max(0, min(width, left + box_width - x))
        y0, y1 = max(0, top - y), max(0, min(height, top + box_height - y))
        included[y0:y1, x0:x1] = False
    mask = (strength >= threshold) & included
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    components = []
    rejected = 0
    for label in range(1, count):
        left, top, box_width, box_height, area = map(int, stats[label])
        if area < min_area or area > width * height * max_area_fraction:
            rejected += 1
            continue
        components.append({'label': label, 'box': [x + left, y + top, box_width, box_height], 'coreAreaPx': area})
    components.sort(key=lambda component: component['coreAreaPx'])
    ys, xs = np.nonzero(mask)
    origin = origin or [x + width / 2, y + height / 2]
    radius = np.hypot(xs + x - origin[0], ys + y - origin[1])
    included_count = int(included.sum())
    if included_count == 0:
        raise ValueError('Exclusions remove the entire observation region.')
    result = {
        'status': 'observed', 'roi': roi, 'origin': origin,
        'includedPixels': included_count, 'foregroundPixels': len(xs),
        'foregroundFraction': len(xs) / included_count,
        'energy': float(strength[included].sum()),
        'meanStrength': float(strength[included].mean()),
        'foregroundStrength': quantiles(strength[mask]), 'radiusPx': quantiles(radius),
        'componentCount': count - 1, 'selectedComponentCount': len(components), 'rejectedComponentCount': rejected,
        'largestCoreAreaPx': int(stats[1:, cv2.CC_STAT_AREA].max()) if count > 1 else 0,
        'coreWidthPx': quantiles([component['box'][2] for component in components]),
        'coreHeightPx': quantiles([component['box'][3] for component in components]),
        'coreAreaPx': quantiles([component['coreAreaPx'] for component in components]),
    }
    return result, components


def export_sprites(image, components, destination, padding=8):
    import cv2
    import numpy as np

    if not components:
        return []
    indices = sorted(set(round(value) for value in np.linspace(0, len(components) - 1, min(6, len(components)))))
    results = []
    for index in indices:
        component = components[index]
        x, y, width, height = component['box']
        left, top = max(0, x - padding), max(0, y - padding)
        right, bottom = min(image.shape[1], x + width + padding), min(image.shape[0], y + height + padding)
        filename = destination / f'sprite-{len(results) + 1:02d}.png'
        crop = image[top:bottom, left:right]
        if not cv2.imwrite(str(filename), crop):
            raise OSError(f'Could not write {filename}')
        # Padding retains visible glow. Nearby marks remain visible in the crop
        # so the maker can choose a clean candidate from the contact sheet.
        results.append({**component, 'path': filename.name, 'cropBox': [left, top, right - left, bottom - top]})
    return results


def write_sheet(panels, destination):
    import cv2
    import numpy as np

    if not panels:
        destination.unlink(missing_ok=True)
        return
    columns = min(4, len(panels))
    cell_width, cell_height = 360, 390
    sheet = np.full((math.ceil(len(panels) / columns) * cell_height, columns * cell_width, 3), 238, np.uint8)
    for index, (label, image) in enumerate(panels):
        scale = min((cell_width - 16) / image.shape[1], (cell_height - 44) / image.shape[0])
        size = (max(1, round(image.shape[1] * scale)), max(1, round(image.shape[0] * scale)))
        view = cv2.resize(image, size, interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_NEAREST)
        left = index % columns * cell_width + (cell_width - size[0]) // 2
        top = index // columns * cell_height
        cv2.putText(sheet, label, (index % columns * cell_width + 8, top + 25), cv2.FONT_HERSHEY_SIMPLEX, .48, (25, 25, 25), 1, cv2.LINE_AA)
        sheet[top + 36:top + 36 + size[1], left:left + size[0]] = view
    if not cv2.imwrite(str(destination), sheet):
        raise OSError(f'Could not write {destination}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--times', required=True, help='Comma-separated source times in seconds.')
    parser.add_argument('--roi', type=rectangle)
    parser.add_argument('--exclude', type=rectangle, action='append', default=[])
    parser.add_argument('--threshold', type=float, default=.3, help='Foreground strength from 0 to 1.')
    parser.add_argument('--matte', choices=['black', 'white'], default='black')
    parser.add_argument('--min-area', type=int, default=2)
    parser.add_argument('--max-area-fraction', type=float, default=.02)
    parser.add_argument('--origin', help='Fixed full-frame x,y for spatial spread.')
    parser.add_argument('--sprites-at', type=float, help='Also extract representative source sprite candidates at this time.')
    parser.add_argument('--padding', type=int, default=8, help='Source pixels around sprite cores.')
    parser.add_argument('--out', type=Path, required=True, help='Working observation directory outside the editable project.')
    args = parser.parse_args()
    import cv2
    import numpy as np

    try:
        times = sorted(set(float(value) for value in args.times.split(',')))
        origin = [float(value) for value in args.origin.split(',')] if args.origin else None
    except ValueError:
        parser.error('Times and origin must contain numbers.')
    if not times or not np.isfinite(times).all() or times[0] < 0:
        parser.error('Use finite nonnegative source times.')
    if origin is not None and (len(origin) != 2 or not np.isfinite(origin).all()):
        parser.error('Origin must contain two finite coordinates.')
    if not 0 < args.threshold <= 1 or args.min_area < 1 or not 0 < args.max_area_fraction <= 1 or args.padding < 0:
        parser.error('Use threshold and area fraction in (0, 1], positive minimum area and nonnegative padding.')
    if args.sprites_at is not None and (not np.isfinite(args.sprites_at) or args.sprites_at < 0):
        parser.error('Sprite time must be finite and nonnegative.')
    capture = cv2.VideoCapture(str(args.video))
    if not capture.isOpened():
        parser.error('The reference video could not be opened.')
    fps = capture.get(cv2.CAP_PROP_FPS)
    width, height = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not np.isfinite(fps) or fps <= 0 or min(width, height) <= 0:
        capture.release()
        parser.error('The video has no usable frame geometry or rate.')
    roi = args.roi or [0, 0, width, height]
    args.out.mkdir(parents=True, exist_ok=True)
    report = {'video': str(args.video.resolve()), 'fps': fps, 'width': width, 'height': height,
              'threshold': args.threshold, 'matte': args.matte, 'excluded': args.exclude,
              'minAreaPx': args.min_area, 'maxAreaFraction': args.max_area_fraction,
              'samples': [], 'sprites': [], 'status': 'incomplete',
              'limits': 'Core sizes depend on the declared threshold and component filter. Padding includes surrounding source pixels and can contain neighboring marks. Radius is image-space extent around the fixed origin, not tracked particle speed. Energy includes all unexcluded material, including connected structures rejected by the size filter. Samples describe selected decoded frames, not continuous event coverage.'}
    filename = args.out / 'observations.json'
    filename.write_text(json.dumps(report, indent=2) + '\n')
    panels = []
    requested = sorted(set(times + ([args.sprites_at] if args.sprites_at is not None else [])))
    try:
        for time in requested:
            capture.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
            ok, image = capture.read()
            if not ok:
                raise ValueError(f'Could not decode a source frame at {time}s.')
            actual = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if not np.isfinite(actual) or abs(actual - time) > 1 / fps + 1e-6:
                raise ValueError(f'Decoded timestamp {actual}s does not cover requested {time}s.')
            sample, components = observe(image, roi, args.exclude, args.threshold, args.matte, args.min_area, args.max_area_fraction, origin)
            sample.update(requestedTime=time, decodedTime=actual)
            if time in times:
                report['samples'].append(sample)
                x, y, region_width, region_height = roi
                panels.append((f'{actual:.3f}s cores={len(components)}', image[y:y + region_height, x:x + region_width]))
            if time == args.sprites_at:
                report['sprites'] = export_sprites(image, components, args.out, args.padding)
                report['spriteTime'] = actual
        write_sheet(panels, args.out / 'source-samples.jpg')
        sprite_panels = [(f"{item['path']} core={item['box'][2]}x{item['box'][3]}", cv2.imread(str(args.out / item['path']))) for item in report['sprites']]
        write_sheet(sprite_panels, args.out / 'sprite-candidates.jpg')
        report['status'] = 'observed'
    except (ValueError, OSError, cv2.error) as error:
        report['error'] = str(error)
    finally:
        capture.release()
        filename.write_text(json.dumps(report, indent=2) + '\n')
    summary = {'report': str(filename), 'status': report['status'], 'samples': report['samples'], 'sprites': report['sprites']}
    print(json.dumps(summary))
    return 0 if report['status'] == 'observed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
