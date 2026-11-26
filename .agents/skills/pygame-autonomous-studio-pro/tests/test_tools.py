import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from invariant_auditor import audit_source, audit_project
from visual_probe import analyze_surface, compare_surfaces, assert_visual_progression
import pygame


class AuditorTests(unittest.TestCase):
    def test_qualifies_pygame_alias_and_portuguese_render_name(self):
        issues = audit_source('import pygame as pg\ndef desenhar():\n pg.image.load("a.png")\n', 'demo.py')
        self.assertEqual([x['code'] for x in issues], ['ASSET_IN_FRAME'])
        self.assertEqual(issues[0]['line'], 3)

    def test_unrelated_load_and_frect_do_not_imply_bug(self):
        text = 'import pygame\ndef update(cache):\n cache.load()\n return pygame.FRect(0,0,1,1)\n'
        self.assertEqual(audit_source(text, 'demo.py'), [])

    def test_sleep_alias_inside_update(self):
        issues = audit_source('from time import sleep as wait\ndef update(dt):\n wait(.1)\n', 'demo.py')
        self.assertEqual(issues[0]['code'], 'BLOCKING_SLEEP')

    def test_constructor_preload_loop_is_not_a_frame_load(self):
        text = 'import pygame\nclass Audio:\n def __init__(self, files):\n  for path in files:\n   pygame.mixer.Sound(path)\n'
        self.assertEqual(audit_source(text, 'audio.py'), [])

    def test_scans_source_and_skips_embedded_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'src').mkdir(); (root/'distribuicao').mkdir()
            (root/'src/a.py').write_text('def broken(:\n', encoding='utf-8')
            (root/'distribuicao/ignore.py').write_text('def broken(:\n', encoding='utf-8')
            issues = audit_project(root)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0]['code'], 'SYNTAX_ERROR')


class VisualTests(unittest.TestCase):
    def test_dark_or_static_scene_is_not_automatically_a_bug(self):
        scene = pygame.Surface((24, 16)); scene.fill((0, 0, 0))
        stats = analyze_surface(scene)
        self.assertTrue(stats['uniform_sample'])
        self.assertEqual(compare_surfaces(scene, scene)['issues'], [])

    def test_visible_region_changes_and_snapshot_is_independent(self):
        frame = pygame.Surface((24, 16)); frame.fill((2, 3, 4))
        before = frame.copy(); frame.fill((100, 2, 7), pygame.Rect(4, 4, 8, 8))
        result = assert_visual_progression(before, frame)
        self.assertGreater(result['changed_pixel_ratio'], 0)
        self.assertNotEqual(result['before']['sha256'], result['after']['sha256'])

    def test_expected_motion_cannot_pass_with_identical_frames(self):
        scene = pygame.Surface((24, 16)); scene.fill((30, 40, 50))
        with self.assertRaises(AssertionError):
            assert_visual_progression(scene.copy(), scene)

    def test_invalid_stride_and_dimensions_are_explicit(self):
        scene = pygame.Surface((24, 16))
        with self.assertRaises(ValueError): analyze_surface(scene, stride=0)
        with self.assertRaises(ValueError): compare_surfaces(scene, pygame.Surface((12, 8)))


if __name__ == '__main__':
    unittest.main()
