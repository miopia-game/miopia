"""Measure real pygame Surfaces. Metrics need a scene-specific expectation."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def analyze_surface(surface, stride=4, rect=None):
    import pygame
    if stride < 1:
        raise ValueError('stride must be positive')
    if rect is not None:
        roi = pygame.Rect(rect).clip(surface.get_rect())
        if roi.width <= 0 or roi.height <= 0:
            raise ValueError('ROI must intersect the Surface')
        surface = surface.subsurface(roi)
    width, height = surface.get_size()
    raw = pygame.image.tobytes(surface, 'RGB')
    samples = [tuple(surface.get_at((x, y))[:3])
               for y in range(0, height, stride) for x in range(0, width, stride)]
    colors = set(samples)
    return {'resolution': [width, height], 'sha256': hashlib.sha256(raw).hexdigest(),
            'samples': len(samples), 'unique_colors_sampled': len(colors),
            'non_black_ratio': sum(c != (0, 0, 0) for c in samples) / max(1, len(samples)),
            'uniform_sample': len(colors) <= 1}


def compare_surfaces(before, after, expect_change=False, allow_uniform=True):
    import pygame
    if before.get_size() != after.get_size():
        raise ValueError('Frames must have matching dimensions')
    a, b = pygame.image.tobytes(before, 'RGB'), pygame.image.tobytes(after, 'RGB')
    changed = sum(a[i:i+3] != b[i:i+3] for i in range(0, len(a), 3))
    stats_a, stats_b = analyze_surface(before), analyze_surface(after)
    issues = []
    if expect_change and changed == 0:
        issues.append('Expected visual change was not observed; inspect state and capture timing.')
    if not allow_uniform and stats_b['uniform_sample']:
        issues.append('Scene contract rejects a uniform sample; inspect the actual frame.')
    return {'before': stats_a, 'after': stats_b,
            'changed_pixel_ratio': changed / max(1, len(a)//3), 'issues': issues}


def assert_visual_progression(before, after, expect_change=True, allow_uniform=True):
    result = compare_surfaces(before, after, expect_change, allow_uniform)
    if result['issues']:
        raise AssertionError('; '.join(result['issues']))
    return result


def main():
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
    import pygame
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    parser.add_argument('--before', type=Path)
    parser.add_argument('--expect-change', action='store_true')
    parser.add_argument('--reject-uniform', action='store_true')
    args = parser.parse_args()
    current = pygame.image.load(str(args.image))
    if args.before:
        result = compare_surfaces(pygame.image.load(str(args.before)), current,
                                  args.expect_change, not args.reject_uniform)
    else:
        if args.expect_change:
            parser.error('--expect-change requires --before')
        result = analyze_surface(current)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get('issues') else 0


if __name__ == '__main__':
    raise SystemExit(main())
