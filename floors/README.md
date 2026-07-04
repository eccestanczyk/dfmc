# Floor Assets

Art assets for battle backgrounds, parallax layers, props, and map previews.

## Structure
```
floors/
├── backgrounds/     # Battle scene backgrounds (1536x1024, boss: 1024x1024)
├── parallax/        # Seamless parallax layers per zone (2304x1024)
├── previews/        # Map preview images (empty + populated per floor)
└── props/           # Per-zone props with transparent backgrounds
    ├── grasslands/
    ├── tidal_shallows/
    └── ...
```

## Pipeline
Tracked in `codex/floor_assets.csv` and `codex/prop_assets.csv`.
Status flow: `prompt_ready` → `generated` → `approved`
