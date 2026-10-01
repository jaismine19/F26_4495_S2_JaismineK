"""Download the VPD crime dataset from GeoDASH open data.

Run from the repository root:
    python scripts/00_download_data.py

Downloads the zip for all neighbourhoods and all years, extracts it to
data/raw/, and prints a brief description of the extracted files.
"""
import urllib.request
import zipfile
from pathlib import Path

URL = (
    "https://geodash.vpd.ca/opendata/crimedata_download/"
    "AllNeighbourhoods_AllYears/crimedata_csv_AllNeighbourhoods_AllYears.zip"
)
RAW_DIR = Path("data") / "raw"


def download_zip(url: str, dest: Path) -> None:
    print(f"Downloading {url}")
    print("This may take a few minutes (file is ~10 MB compressed).")
    with urllib.request.urlopen(url) as response:
        dest.write_bytes(response.read())
    print(f"Saved to {dest}")


def extract_zip(zip_path: Path, dest_dir: Path) -> None:
    print(f"Extracting {zip_path} to {dest_dir}")
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(dest_dir)
    for member in archive.namelist():
        print(f"  extracted: {member}")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "crimedata_csv_AllNeighbourhoods_AllYears.zip"
    if not zip_path.exists():
        download_zip(URL, zip_path)
    else:
        print(f"{zip_path} already exists, skipping download.")
    extract_zip(zip_path, RAW_DIR)


if __name__ == "__main__":
    main()
