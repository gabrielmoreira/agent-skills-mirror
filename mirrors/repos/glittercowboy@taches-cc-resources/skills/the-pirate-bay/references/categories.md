# Category Reference

<category_codes>

**Top-level categories:**

| Code | Name | CLI alias |
|------|------|-----------|
| 0 | All | `all` |
| 100 | Audio | `audio` |
| 200 | Video | `video` |
| 300 | Applications | `apps`, `applications` |
| 400 | Games | `games` |
| 500 | Porn | `porn` |
| 600 | Other | `other` |

**Audio (100):**

| Code | Name | CLI alias |
|------|------|-----------|
| 101 | Music | `music` |
| 102 | Audio Books | `audiobooks` |
| 103 | Sound Clips | `sound-clips` |
| 104 | FLAC | `flac` |
| 199 | Other | — |

**Video (200):**

| Code | Name | CLI alias |
|------|------|-----------|
| 201 | Movies | `movies` |
| 202 | Movies DVDR | `movies-dvdr` |
| 203 | Music Videos | `music-videos` |
| 204 | Movie Clips | `movie-clips` |
| 205 | TV Shows | `tv-shows`, `tv` |
| 206 | Handheld | — |
| 207 | HD Movies | `hd-movies` |
| 208 | HD TV Shows | `hd-tv` |
| 209 | 3D | `3d` |
| 210 | CAM/TS | `cam-ts` |
| 211 | UHD/4K Movies | `uhd-movies`, `4k-movies` |
| 212 | UHD/4K TV Shows | `uhd-tv`, `4k-tv` |
| 299 | Other | — |

**Applications (300):**

| Code | Name | CLI alias |
|------|------|-----------|
| 301 | Windows | `windows` |
| 302 | Mac | `mac` |
| 303 | UNIX | `unix` |
| 304 | Handheld | — |
| 305 | iOS | `ios` |
| 306 | Android | `android` |
| 399 | Other OS | — |

**Games (400):**

| Code | Name | CLI alias |
|------|------|-----------|
| 401 | PC | `pc-games` |
| 402 | Mac | `mac-games` |
| 403 | PSx | `psx` |
| 404 | XBOX360 | `xbox` |
| 405 | Wii | `wii` |
| 406 | Handheld | — |
| 407 | iOS | — |
| 408 | Android | `android-games` |
| 499 | Other | — |

**Porn (500):**

| Code | Name |
|------|------|
| 501 | Movies |
| 502 | Movies DVDR |
| 503 | Pictures |
| 504 | Games |
| 505 | HD Movies |
| 506 | Movie Clips |
| 507 | UHD/4K |
| 599 | Other |

**Other (600):**

| Code | Name | CLI alias |
|------|------|-----------|
| 601 | E-books | `ebooks`, `e-books` |
| 602 | Comics | `comics` |
| 603 | Pictures | `pictures` |
| 604 | Covers | — |
| 605 | Physibles | — |
| 699 | Other | — |

</category_codes>

<usage_notes>

- Use top-level codes (100, 200, etc.) to search across all subcategories
- Use specific codes (207, 208, etc.) for precise filtering
- The CLI tool accepts friendly aliases (`video`, `hd-movies`, `tv`, etc.)
- The API accepts only numeric codes
- For top100 precompiled JSONs, use the numeric code as the slug: `data_top100_207.json`

</usage_notes>
