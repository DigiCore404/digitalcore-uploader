# DigitalCore Uploader

Upload to DigitalCore through your browser or the command line. Includes metadata
lookup with TMDB, TVmaze and IGDB, automatic screenshots, MediaInfo, DigitalCore's
image host and qBittorrent integration.

## Screenshots

The empty upload workspace:

![Empty upload workspace](docs/images/workspace-empty.jpg)

Built-in installation and seeding guide:

![Built-in manuals and folder mapping](docs/images/manuals.jpg)

### Settings & automation

![Uploader settings and image host](docs/images/settings.jpg)

### Screenshots & thumbnail sheets

![Screenshot and MTN configuration](docs/images/screenshot-settings.jpg)

In **Settings → Screenshots & thumbnail sheets → Videos to capture**, choose
**Automatic** (default: all videos for pack categories, one for other releases),
**One video**, or **All videos (packs / site rips)**. All videos processes
every main video, including subfolders, with separate screenshot counts and an
optional MTN contact sheet for each video. Samples and extras are skipped when
main videos exist. Use the MTN engine for contact sheets; FFmpeg creates separate
screenshots only. These settings apply to browser uploads, imports and CLI uploads.

For CLI configuration:

```ini
[MediaTools]
SCREENSHOT_VIDEO_MODE = auto
SCREENSHOT_ENGINE = mtn
SCREENSHOT_SHEET = true
SCREENSHOT_SINGLES = 3
```

For packs, this creates one sheet and three separate screenshots per video;
other release categories use one video. With required
screenshots enabled, a failed video stops publication; disabling that option
allows partial previews and logs the failed videos.

### Metadata search

![Empty metadata search](docs/images/metadata-search.jpg)

## Install

For Docker or Synology, you need Linux x86_64 and Docker Compose (Container Manager
on Synology).

```bash
git clone https://github.com/DigiCore404/digitalcore-uploader.git
cd digitalcore-uploader
docker build --target release -t digitalcore-uploader:local .
bash setup.sh --media /srv/media --image digitalcore-uploader:local --bind 0.0.0.0
```

Replace `/srv/media` with your media folder. When running as root, also pass your
normal account's `--uid` and `--gid`.

Open `http://<server-ip>:6080` and sign in with the login shown during installation.

[Docker and Synology setup](README-docker.md) · [Linux seedbox setup](SEEDBOX-INSTALL.md)

## Upload

1. Add your DigitalCore API key and personal announce URL in **Settings**.
2. Connect qBittorrent in **Clients** if you want to import torrents.
3. Choose **New upload** or **Import torrent**, fill in the release details and review before uploading.

DigitalCore's image host is ready to use. TVmaze works without a key; TMDB and
IGDB can be enabled in Settings with your own credentials.

Keep seeding after uploading. Folder and seeding instructions are available in
**Manuals** inside the uploader.

## Command line

The CLI, download-completion callback and folder watcher remain available.
For a native Linux installation, upload a release with:

```bash
bash start.sh upload /srv/media/My.Release --cat 6
```

Browser and CLI uploads appear together in **Activity**, with their progress,
logs and results. Use the same installation and persistent data folder.

For a single file, select it in the content browser. The uploader creates a release
folder beside it and adds a link. Choose **Hardlink** or **Softlink** in
**Settings → Single-file uploads**. Hardlinks require the same filesystem;
softlinks require the original file to stay accessible. No file data is copied.
The seeding client must see both the release folder and original media through
the same library mapping. The media mount needs write access to create the folder.

## Updates and image hosts

**Settings → Uploader updates** checks for new stable releases automatically.
When a newer version exists, a banner links to release notes and update steps for
Docker Compose, a Git checkout, or a seedbox package. **Check for updates** checks
again; configuration, credentials and upload history remain on your own server.
New Docker installations follow `latest`; an existing pinned image must be
changed to `latest` in its existing Compose project to follow stable releases.
Older installations need one manual update to gain this notification feature.

Choose **ImgBB** in Settings and enter your ImgBB API key in **Image host API key**.
This applies to browser images, folder images and screenshots from web or CLI.
For CLI configuration:

```ini
[ImageHost]
PROVIDER = imgbb
API_KEY =
```

Fill API_KEY privately with your ImgBB key. To use the site's own image host,
select it in Settings; no separate image-host key is needed.
