# Brook Farm Replay

Interactive viewer for the Brook Farm AI commune simulation. Watch 30 rounds of five AI agents trying to build utopia — and failing.

**Live:** [menggg22.github.io/utopia/replay.html](https://menggg22.github.io/utopia/replay.html)

## Files

| File | What it does |
|------|-------------|
| `replay.html` | Web viewer — step through rounds, read conversations, watch morale decline |
| `replay.py` | Terminal viewer — ASCII animated playback in your shell |
| `make_replay_data.py` | Generates `replay_data.json` from simulation run directories |
| `replay_data.json` | Generated data file (not committed — generate it yourself) |

## Usage

### Web viewer

```bash
# Generate data from runs
python make_replay_data.py ../runs/v3_run_*/

# Serve locally (fetch doesn't work with file://)
python -m http.server 8000
# Open http://localhost:8000/replay.html
```

### Adding a narrative summary for a run

Each run can have a closing summary shown on the finale screen. To add one, edit `make_replay_data.py` and add an entry to the `SUMMARIES` dict:

```python
SUMMARIES = {
    "run_0":       "Nobody left. All five stayed...",  # keyed by exp_name + seed for baselines
    "no_hawthorne": "Without the skeptic...",           # keyed by exp_name for counterfactuals
}
```

For baseline runs (`name = "run"` or `"baseline"`), the key is `run_{seed}` (e.g. `run_0`, `run_42`).
For counterfactuals, the key is the experiment name (e.g. `no_hawthorne`, `no_sophia`).

Write it like a closing film card — short sentences, no numbers in parentheses. Then regenerate:

```bash
python make_replay_data.py ../runs/v3_*/
```

### Terminal viewer

```bash
python replay.py ../runs/v3_run_20260403_135520/
python replay.py ../runs/v3_run_20260403_135520/ --speed 3  # seconds between rounds
```

## Deploying to the blog

```bash
# Generate fresh data
python make_replay_data.py ../runs/v3_*

# Copy to blog repo
cp replay.html replay_data.json /path/to/menggg22.github.io/utopia/

# Commit and push blog repo
```

## Single-run vs multi-run

With one run in `replay_data.json`, the viewer goes straight to the story — no run selector. With multiple runs, a home screen appears with run cards to choose from.
