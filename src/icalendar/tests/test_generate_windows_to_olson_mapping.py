import io
import json
import runpy
from pathlib import Path
from urllib import request

CLDR_SHA = "0123456789abcdef0123456789abcdef01234567"
COMMITS_URL = (
    "https://api.github.com/repos/unicode-org/cldr/commits"
    "?path=common/supplemental/windowsZones.xml&sha=main&per_page=1"
)
RAW_URL = (
    "https://raw.githubusercontent.com/unicode-org/cldr/"
    f"{CLDR_SHA}/common/supplemental/windowsZones.xml"
)


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class Output(io.StringIO):
    def close(self):
        """Keep generated content available after the writer context exits."""


def test_generator_pins_mapping_to_latest_cldr_commit(monkeypatch):
    """The generated mapping and its version use the same CLDR commit."""
    requested_urls = []

    def urlopen(url):
        requested_urls.append(url)
        if url == COMMITS_URL:
            return Response(json.dumps([{"sha": CLDR_SHA}]).encode())
        if url == RAW_URL:
            return Response(
                b"<supplementalData><windowsZones><mapTimezones>"
                b'<mapZone other="Test Standard Time" territory="001" '
                b'type="Etc/Test"/>'
                b"</mapTimezones></windowsZones></supplementalData>"
            )
        raise AssertionError(f"Unexpected URL: {url}")

    output = Output()

    def open_output(_path, _mode):
        return output

    monkeypatch.setattr(request, "urlopen", urlopen)
    monkeypatch.setattr(Path, "open", open_output)

    generator = Path(__file__).parents[3] / "generate_windows_to_olson_mapping.py"
    runpy.run_path(str(generator), run_name="__main__")

    generated = output.getvalue()
    assert requested_urls == [COMMITS_URL, RAW_URL]
    assert f'version = "{CLDR_SHA}"' in generated
    assert '"Test Standard Time": "Etc/Test"' in generated


def test_generator_serializes_cldr_version_as_a_string(monkeypatch):
    """The source version cannot inject executable Python into the output."""
    malicious_sha = '"; injected = True; version = "'
    malicious_raw_url = (
        "https://raw.githubusercontent.com/unicode-org/cldr/"
        f"{malicious_sha}/common/supplemental/windowsZones.xml"
    )

    def urlopen(url):
        if url == COMMITS_URL:
            return Response(json.dumps([{"sha": malicious_sha}]).encode())
        if url == malicious_raw_url:
            return Response(b"<supplementalData />")
        raise AssertionError(f"Unexpected URL: {url}")

    output = Output()

    monkeypatch.setattr(request, "urlopen", urlopen)
    monkeypatch.setattr(Path, "open", lambda _path, _mode: output)

    generator = Path(__file__).parents[3] / "generate_windows_to_olson_mapping.py"
    runpy.run_path(str(generator), run_name="__main__")

    generated = output.getvalue()
    namespace = {}
    exec(generated, namespace)  # noqa: S102
    assert namespace["version"] == malicious_sha
    assert "injected" not in namespace
