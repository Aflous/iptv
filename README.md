# M3U Playlist CLI

A simple Typer-based CLI to **download** and **filter** IPTV M3U playlists.

## Setup

1. Install [`uv`](https://github.com/astral-sh/uv) if not already installed:

    ```bash
    pip install uv
    ```

2. Create a `.env` file in the same directory with your IPTV credentials:

    ```env
    USER=your_username
    PWD=your_password
    ```

## Usage

No need to install dependencies — `uv` handles everything via the shebang.

### Download M3U

```bash
uv run iptv.py download
```

Downloads the playlist to `playlist.m3u`.

### Filter Playlist

```bash
uv run iptv.py filter-streams --tokens "action" "sports"
```

Filters entries containing **both** `"action"` and `"sports"` in their title. Saves output to `filtered.m3u`.

You can optionally specify input/output files:

```bash
uv run iptv.py filter-streams --tokens "news" --input-file custom.m3u --output-file news_only.m3u
```

## Notes

- The `playlist.m3u` filename is used by default for both download and filter.
- Filtering is **case-insensitive**.

---

Built with ❤️ using [Typer](https://typer.tiangolo.com/) and [uv](https://github.com/astral-sh/uv).
