from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [
    ROOT / "shizi" / "index.html",
    ROOT / "shizi" / "404.html",
    ROOT / "shizi" / "404" / "index.html",
]
WEBPACK_RUNTIME = ROOT / "shizi" / "bakery-assets" / "static" / "chunks" / "webpack-1ed4c2217ac2d2f6.js"


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.asset_urls = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value and "bakery-assets/" in value:
                self.asset_urls.append(value)


def main():
    for html_file in HTML_FILES:
        parser = AssetParser()
        parser.feed(html_file.read_text(encoding="utf-8"))

        assert parser.asset_urls, f"{html_file} should reference bakery assets"

        for asset_url in parser.asset_urls:
            resolved_path = urlparse(urljoin("https://lava7397.com/shizi", asset_url)).path

            assert resolved_path.startswith("/shizi/bakery-assets/"), (
                f"{asset_url} resolves to {resolved_path} when the page URL is /shizi"
            )
            assert (ROOT / resolved_path.lstrip("/")).exists(), (
                f"{resolved_path} should exist on disk"
            )

    runtime = WEBPACK_RUNTIME.read_text(encoding="utf-8")
    assert 'r.p="/shizi/bakery-assets/"' in runtime, (
        "webpack runtime should load dynamic chunks from /shizi at the bare /shizi URL"
    )


if __name__ == "__main__":
    main()
