import json
import unittest
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_generate():
    spec = importlib.util.spec_from_file_location("generate", ROOT / "generate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenerateSecurityTests(unittest.TestCase):
    def test_archive_json_is_safe_inside_script_tag(self):
        generate = load_generate()
        payload = '</script><img src=x onerror="alert(1)">'

        encoded = generate.json_for_script([["2026-05-03", payload, "1", payload]])

        self.assertNotIn("</script><img", encoded.lower())
        self.assertEqual(json.loads(encoded), [["2026-05-03", payload, "1", payload]])

    def test_issues_pagination_escapes_archive_metadata_before_inner_html(self):
        generate = load_generate()
        payload = '<img src=x onerror="alert(1)">'

        html = generate.build_issues_html([("2026-05-03", payload, "1", payload)])

        self.assertIn("function escHtml", html)
        self.assertIn("${escHtml(headline || '暂无摘要')}", html)
        self.assertIn('const summaryHtml = summary ? `<p class="date-summary">${escHtml(summary)}</p>` : \'\';', html)


class BakeryAssetFetchSecurityTests(unittest.TestCase):
    def test_rejects_path_traversal_asset_filenames(self):
        script = (ROOT / "scripts" / "fetch-bakery-assets.mjs").read_text(
            encoding="utf-8"
        )
        self.assertIn("function assertSafeAssetFilename(filename)", script)
        self.assertIn('assertSafeAssetFilename(filename);', script)
        self.assertIn('filename.includes("/")', script)
        self.assertIn('filename.includes("\\\\")', script)
        self.assertIn('filename === "."', script)
        self.assertIn('filename === ".."', script)


if __name__ == "__main__":
    unittest.main()
