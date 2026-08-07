import _env  # noqa: F401  # isort: skip
import unittest

from backend.common.core_layer.unigraph.module.llm_output_checks import clamp_rating, strip_json_fences


class StripJsonFencesTests(unittest.TestCase):
    def test_strips_fenced_block_markers(self):
        self.assertEqual(strip_json_fences('```json\n{"title": "报告"}\n```'), '{"title": "报告"}')

    def test_preserves_json_text_inside_payload(self):
        response = '```json\n{"title": "JSON解析技术社区", "summary": "研究json格式"}\n```'
        cleaned = strip_json_fences(response)
        self.assertIn('JSON解析技术社区', cleaned)
        self.assertIn('研究json格式', cleaned)

    def test_unfenced_response_is_trimmed(self):
        self.assertEqual(strip_json_fences('  {"a": 1}  '), '{"a": 1}')


class ClampRatingTests(unittest.TestCase):
    def test_in_range_value_passes_through(self):
        self.assertEqual(clamp_rating(7.5), 7.5)

    def test_out_of_range_values_are_clamped(self):
        self.assertEqual(clamp_rating(15), 10.0)
        self.assertEqual(clamp_rating(-3), 0.0)

    def test_numeric_string_is_accepted(self):
        self.assertEqual(clamp_rating('8.2'), 8.2)

    def test_invalid_values_become_zero(self):
        self.assertEqual(clamp_rating('high'), 0.0)
        self.assertEqual(clamp_rating(None), 0.0)
        self.assertEqual(clamp_rating(float('nan')), 0.0)


if __name__ == '__main__':
    unittest.main()
