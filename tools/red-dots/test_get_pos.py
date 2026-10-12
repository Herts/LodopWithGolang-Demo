import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import cv2
import numpy as np

from get_pos import collect_images, find_dots, main, render_js


class CoordinateTests(unittest.TestCase):
    def image(self):
        image = np.full((100, 200, 3), 255, dtype=np.uint8)
        cv2.circle(image, (40, 20), 3, (0, 0, 255), -1)
        cv2.circle(image, (100, 80), 3, (0, 0, 255), -1)
        return image

    def test_centroids_scale_to_actual_image_dimensions(self):
        self.assertEqual(find_dots(self.image(), 400, 200), [(40, 80), (160, 200)])

    def test_resizing_does_not_change_page_coordinates(self):
        enlarged = cv2.resize(self.image(), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        original = find_dots(self.image(), 400, 200)
        resized = find_dots(enlarged, 400, 200)
        for first, second in zip(original, resized):
            self.assertTrue(all(abs(a - b) <= 1 for a, b in zip(first, second)))
        self.assertEqual(len(original), len(resized))

    def test_origin_marker_is_kept_and_blue_is_ignored(self):
        image = np.zeros((20, 20, 3), dtype=np.uint8)
        image[:3, :3] = (0, 0, 255)
        image[10:15, 10:15] = (255, 0, 0)
        self.assertEqual(find_dots(image, 20, 20), [(1, 1)])

    def test_noise_is_filtered(self):
        image = self.image()
        image[5, 5] = (0, 0, 255)
        self.assertEqual(len(find_dots(image)), 2)

    def test_invalid_dimensions_and_unreadable_image(self):
        for image, width in [(None, 794), (self.image(), 0)]:
            with self.assertRaises(ValueError):
                find_dots(image, width=width)

    def test_page_breaks_only_between_pages(self):
        pages = [{'dots': [[10, 20]]}, {'dots': [[30, 40]]}]
        output = render_js(pages)
        self.assertEqual(output.count('LODOP.NEWPAGE();'), 1)
        self.assertIn('LODOP.ADD_PRINT_TEXT(30, 40, 100, 20, "1");', output)

    def test_cli_directory_order_offsets_and_json(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            for name in ['02.png', '01.png']:
                self.assertTrue(cv2.imwrite(str(directory / name), self.image()))
            (directory / 'ignore.txt').write_text('not an image')
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                main([str(directory), '--width', '400', '--height', '200',
                      '--offset-y', '-7', '--offset-x', '2', '--format', 'json'])
            pages = json.loads(output.getvalue())
            self.assertTrue(pages[0]['image'].endswith('01.png'))
            self.assertEqual(pages[0]['dots'], [[33, 82], [153, 202]])

    def test_bad_or_markerless_inputs_fail_without_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            with self.assertRaises(ValueError):
                collect_images([directory / 'missing.png'])
            blank = directory / 'blank.png'
            cv2.imwrite(str(blank), np.full((20, 20, 3), 255, dtype=np.uint8))
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    main([str(blank)])
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(output.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
