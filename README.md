# The Daily Sum — Tuesday, 24 November 2026 in one image

[![Competition](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![Rank](https://make.fun/badge/news-image-20261124/fadliferdian74-lgtm/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![Reward](https://make.fun/badge/news-image-20261124/fadliferdian74-lgtm/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

A newspaper front page that sums up the world news of **Tuesday,
24 November 2026** in a single 1024×1024 image: 25 stories from every
region and beat — the Gaza strike and the Hormuz mine hits, Singapore's
upgraded forecast and Anthropic's slide below its IPO price, the
Democrats' 259-seat House majority, the first foreign astronaut bound
for China's space station, and Galatasaray's win over Aston Villa.

Every story prints its headline, a short summary and the names of its
sources beneath it; each story is backed by at least two credible
sources (see [SOURCES.md](SOURCES.md)). Colour appears only in the
masthead band; the body of the page is black and white.

## How it is built

- `stories.py` — the 25 stories: headline, summary and source names.
- `render.py` — draws the page deterministically with Pillow: composed
  at 2048×2048, downscaled with Lanczos to 1024×1024, saved as a JPEG
  (quality 93, 4:4:4 chroma) in the file `entry.png`. Repeated renders
  are byte-identical.
- `entry.png` — the rendered front page (JPEG bytes, as the competition
  allows; the file name stays `entry.png`).
- `main.py` — the competition entry point: copies `entry.png` to
  `/output/entry.png` (or to `$MAKEFUN_OUTPUT_DIR` when set), byte for
  byte, using only the Python standard library.

## Run it

```sh
python3 main.py            # writes /output/entry.png
python3 render.py          # re-renders entry.png from stories.py
```

## License

MIT — see [LICENSE](LICENSE).
