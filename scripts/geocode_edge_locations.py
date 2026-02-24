import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {path}")


def _extract_location_names(locations: dict) -> list[str]:
    names = []
    for raw in locations.keys():
        if not isinstance(raw, str):
            continue
        cleaned = raw.split("(")[0].strip()
        cleaned = cleaned.replace("*", "")
        cleaned = cleaned.split(",")[0].strip()
        if cleaned:
            names.append(cleaned)
    return sorted(set(names))


def _geocode_open_meteo(query: str) -> tuple[float, float] | None:
    url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode(
        {
            "name": query,
            "count": 1,
            "language": "en",
            "format": "json",
        }
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "faas-bench-geodis/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        print(f"Geocode failed for '{query}'")
        return None
    results = data.get("results") or []
    if not results:
        print(f"No geocode results for '{query}'")
        return None
    return float(results[0]["latitude"]), float(results[0]["longitude"])


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    config_path = base_dir / "config" / "geodis_provider_config.json"
    output_path = base_dir / "config" / "edge_location_coordinates.json"

    config = _load_json(config_path)
    existing = _load_json(output_path)
    print(f"Loaded config: {config_path}")
    print(f"Loaded existing coordinates: {output_path} ({len(existing)} providers)")

    providers = {
        "cloudflare": config.get("cloudflare-locations", {}),
        "fastly": config.get("fastly-locations", {}),
        "deno": config.get("deno-locations", {}),
    }

    updated = dict(existing)
    for provider, locations in providers.items():
        provider_map = updated.get(provider, {})
        if not isinstance(provider_map, dict):
            provider_map = {}

        names = _extract_location_names(locations)
        print(f"Provider '{provider}': {len(names)} locations ({len(provider_map)} already geocoded)")
        for name in names:
            if name in provider_map:
                continue
            print(f"  Geocoding '{name}'...")
            coords = _geocode_open_meteo(name)
            if coords is None:
                provider_map[name] = None
                print(f"  -> No coords")
            else:
                provider_map[name] = {"lat": coords[0], "lon": coords[1]}
                print(f"  -> {coords[0]:.5f}, {coords[1]:.5f}")
            time.sleep(1.0)

        updated[provider] = provider_map

    _save_json(output_path, updated)
    print(f"Done. Total providers: {len(updated)}")


if __name__ == "__main__":
    main()
