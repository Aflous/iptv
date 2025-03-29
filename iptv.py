#!/usr/bin/env -S uv run --require-virtualenv=false
# /// script
# requires-python = ">=3.7"
# dependencies = [
#     "typer",
#     "pandas",
#     "httpx",
#     "python-dotenv",
# ]
# ///

"""M3U downloader and filter script."""

import os
import re
from pathlib import Path

import httpx
import pandas as pd
import typer
from dotenv import load_dotenv

load_dotenv()

PLAYLIST_FILE = "playlist.m3u"

app = typer.Typer()


def download_m3u(output_file: str = PLAYLIST_FILE) -> None:
    """Download M3U playlist file using credentials from env."""
    params = {
        "username": os.getenv("USER"),
        "password": os.getenv("PWD"),
        "type": "m3u_plus",
        "output": "ts",
    }
    try:
        response = httpx.get("http://ultra-vip.net/get.php", params=params, timeout=10)
        response.raise_for_status()
        with Path(output_file).open("wb") as f:
            f.write(response.content)
        typer.echo(f"M3U file downloaded and saved to {output_file}")
    except httpx.HTTPStatusError as e:
        typer.echo(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:  # noqa: BLE001
        typer.echo(f"Download failed: {e}")


def read_m3u(file_path: str) -> list[str]:
    """Read M3U file and return lines."""
    try:
        with Path(file_path).open(encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        typer.echo(f"File {file_path} not found.")
        raise


def parse_m3u(lines: list[str]) -> pd.DataFrame:
    """Parse M3U lines into a DataFrame."""
    tvg_name, tvg_logo, group_title, urls = [], [], [], []
    i = 0
    if lines and lines[0].strip().upper().startswith("#EXTM3U"):
        i = 1
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            name_match = re.search(r'tvg-name="([^"]+)"', line)
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            group_match = re.search(r'group-title="([^"]+)"', line)
            url_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
            tvg_name.append(name_match.group(1) if name_match else "")
            tvg_logo.append(logo_match.group(1) if logo_match else "")
            group_title.append(group_match.group(1) if group_match else "")
            urls.append(url_line)
            i += 2
        else:
            i += 1
    return pd.DataFrame(
        {
            "tvg_name": tvg_name,
            "tvg_logo": tvg_logo,
            "group_title": group_title,
            "url": urls,
        },
    )


def filter_dataframe(frame: pd.DataFrame, tokens: list[str]) -> pd.DataFrame:
    """Filter DataFrame by presence of tokens in tvg_name."""
    mask = pd.Series(data=True, index=frame.index)
    for token in tokens:
        mask &= frame["tvg_name"].str.contains(token, regex=False, case=False, na=False)
    return frame[mask]


def save_filtered_m3u(frame: pd.DataFrame, output_file: str) -> None:
    """Save filtered DataFrame to a new M3U file."""
    with Path(output_file).open("w", encoding="utf-8") as file:
        file.write("#EXTM3U\n")
        for _, row in frame.iterrows():
            file.write(
                f'#EXTINF:-1 tvg-name="{row["tvg_name"]}" tvg-logo="{row["tvg_logo"]}" '
                f'group-title="{row["group_title"]}",{row["tvg_name"]}\n{row["url"]}\n',
            )


def generate_output_filename(tokens: list[str]) -> str:
    """Generate output file name based on tokens."""
    filename = "_".join(token.strip().lower() for token in tokens if token.strip())
    if not filename:
        filename = "filtered"
    return f"{filename}.m3u"


@app.command()
def download(output_file: str = PLAYLIST_FILE) -> None:
    """Download M3U file from IPTV server."""
    download_m3u(output_file)


@app.command()
def filter(
    tokens: list[str],
    input_file: str = PLAYLIST_FILE,
    output_file: str | None = None,
) -> None:
    """Filter M3U file entries based on keywords."""
    lines = read_m3u(input_file)
    dataframe = parse_m3u(lines)
    filtered_df = filter_dataframe(dataframe, tokens)
    hit_count = len(filtered_df)

    if hit_count == 0:
        typer.echo("No hits found. No file was saved.")
        return

    typer.echo(f"{hit_count} hit{'s' if hit_count != 1 else ''} found.")

    if output_file is None:
        output_file = generate_output_filename(tokens)
    save_filtered_m3u(filtered_df, output_file)
    typer.echo(f"Filtered M3U file saved to {output_file}")


if __name__ == "__main__":
    app()
