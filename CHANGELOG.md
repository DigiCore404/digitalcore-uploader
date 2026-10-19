# DigitalCore Uploader changelog

## 3.2.1 · 2026-10-19

- Restore consistent spacing between all Manuals panels on desktop and small screens.

## 3.2.0 · 2026-10-19

- Add persistent upload drafts and a local screenshot, contact-sheet, MediaInfo and description preview without publishing or creating a torrent.
- Add a choice between a linked release folder and a native single-file torrent. Posted titles exclude the file extension; the payload filename is preserved.
- Keep file selection, review and CLI dry-run free of media-folder or link creation.
- Add confirmed torrent delivery to a configured qBittorrent client, visible delivery results and retries without republishing.
- Add Account preference, Anonymous and Named publication settings; stop if the account preference cannot be read.
- Stop uploads when required screenshots cannot be generated, including when no eligible video is found.
- Add Back navigation for visited folders, workspace pages, upload steps, details and dialogs.
- Add a Changelog menu and the complete changelog to update instructions.

## Earlier changes

The entries below preserve the complete change record of this uploader repository. Cosmetic label punctuation changes are excluded.

- 2026-10-17 · DigitalCore Uploader
- 2026-10-17 · Fix login background and use DigitalCore uploader names
- 2026-10-17 · Match DirtyBytes login panel layout in DigitalCore colours
- 2026-10-17 · Support single-file releases with configurable hardlinks or softlinks
- 2026-10-17 · Link upload descriptions to the new DigitalCore uploader
- 2026-10-17 · Restore original CLI metadata and upload capabilities while preserving the web workflow
- 2026-10-17 · Fix end-to-end QA findings across web, Docker CLI and native setup
- 2026-10-17 · Add one-time workspace login recovery and Docker README screenshots
- 2026-10-17 · Show workspace screenshots in the main README
- 2026-10-17 · Expand README galleries with settings and metadata screenshots
- 2026-10-17 · Fix upload failure recovery, duplicate seeding and UNRAR handling
- 2026-10-18 · Add per-video screenshot mode for packs in web and CLI
- 2026-10-18 · Default to all pack videos and one video for other releases
- 2026-10-18 · Add web release notifications, update instructions and ImgBB support
- 2026-10-18 · Keep ImgBB endpoint and setup help consistent (v3.1.0)
- 2026-10-18 · Fix update panel text contrast for the site theme (v3.1.1)
- 2026-10-18 · Update installation guides to use published latest Docker images
- 2026-10-18 · Organize uploader settings and document direct Compose installation (v3.1.2)
- 2026-10-18 · Add library upload actions, category rules editor and API checks
- 2026-10-18 · Document native FUSE and archive tool requirements
- 2026-10-18 · Keep screenshot publication tests on isolated image host fixture (v3.1.3)
- 2026-10-18 · Document Library uploads and automatic category rules
- 2026-10-18 · Restrict uploader metadata to supported DigitalCore fields (v3.1.4)
- 2026-10-18 · Center uploader descriptions and remove empty template sections (v3.1.5)
- 2026-10-19 · Reuse existing torrents through Import and CLI without rehash fallback (v3.1.6)
