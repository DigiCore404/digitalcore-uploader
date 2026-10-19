# DigitalCore Uploader changelog

## 3.3.1 · 2026-10-19

- Keep the expanded changelog in update instructions readable with a dark background and contrasting text. Upload behaviour is unchanged.

## 3.3.0 · 2026-10-19

- Add visible coloured Rules buttons, a removal-rule overview and + New Rule. Support multiple named rules per client, preserve existing rules and apply only the first matching enabled rule.
- Add a per-client qBittorrent category for confirmed uploads delivered through the API, including web, CLI and Import. Source downloads, existing torrents and watch-folder delivery keep their current category handling.
- Put the editable site torrent title above category selection and keep each Manuals panel separate, including client controls.
- Refresh browser asset versions on release so updated interfaces load without stale cached files.
- Render the Changelog page and update instructions with version headings and readable bullet lists.
- Fit Clients columns to the full available width, preserving user proportions and adapting when the window changes.
- Use smaller monospace text and horizontal scrolling in the filters.json editor to keep long category rules readable.
- Group the torrent information modal into readable sections, use full-width paths and hashes, and align tracker hosts, status badges and peer counts.
- Add a tracker-host filter to Clients, combined with client, state and search filters across the full paginated list. Private announce paths and passkeys are not shown.
- Add resizable Clients torrent columns, remembered per browser across refreshes and sorting, with per-column and full-width reset controls.
- Add per-torrent actions in Clients and the torrent information dialog, tracker hostnames, seed time and connected/swarm peer counts.
- Add optional completed-torrent removal rules per client, with a read-only preview, explicit data handling and removal history. Rules are disabled by default; shared or unknown content paths are skipped for automatic data removal.
- Allow a separate site post title in uploads, Library, Import, drafts and CLI (--title), preserving the torrent payload and seeding paths.
- Convert fetched metadata descriptions from HTML to readable text with paragraph breaks, and separate the metadata source link from the comparison button.

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
