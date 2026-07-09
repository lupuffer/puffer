# -*- coding: utf-8 -*-
"""
Generate JPL Horizons reference cache for 2026 by fetching REAL JPL data.

Strategy (REVISED for Rule 9 compliance):
  1. Fetch real Sun, Earth, Moon state vectors from JPL Horizons
     via the course proxy (jpl_forward.py) for 2026 full year.
  2. Save as data/horizons_cache_2026.json.
  3. If online fetch fails, use the horizons_verify module's
     built-in Keplerian IC fallback ONLY as a last resort,
     with a clear warning that real JPL fidelity is not verified.

This ensures the cache contains REAL JPL ephemeris data,
not self-consistent Keplerian approximations.
"""

import json
import sys
import numpy as np
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

CACHE_PATH = Path(__file__).resolve().parents[1] / "data" / "horizons_cache_2026.json"
CACHE_PATH.parent.mkdir(exist_ok=True, parents=True)


def _add_cache_metadata(cache_path, source="unknown", message=""):
    """Add/update source metadata in the cache JSON file."""
    import json
    try:
        with open(cache_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    data["_metadata"] = {
        "source": source,
        "message": message,
        "generated_by": "generate_cache.py",
        "timestamp": "2026-06-19",
        "note": (
            "If source='jpl_horizons_online', this cache contains REAL JPL DE440 "
            "ephemeris data and satisfies Rule 9 (6000 km residual verification). "
            "If source='keplerian_fallback', this cache is self-consistent but does "
            "NOT contain real JPL data — online JPL access is required for Rule 9."
        ),
    }

    with open(cache_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [META] Cache source marked as: {source}")


def generate_cache():
    """Fetch real JPL data and save as cache."""
    print("=" * 60)
    print("Generating JPL Horizons reference cache (REAL DATA)")
    print("=" * 60)

    # --- Attempt 1: Real JPL data via proxy ---
    try:
        print("\n[INFO] Attempting online JPL Horizons fetch via proxy...")
        import jpl_forward  # noqa: F401  monkey-patch astroquery
        from horizons_verify import fetch_all_bodies_horizons

        jpl_data = fetch_all_bodies_horizons(force_offline=False)
        # Add source metadata
        _add_cache_metadata(CACHE_PATH, source="jpl_horizons_online",
                           message="Real JPL Horizons DE440 ephemeris via proxy")
        print("\n[SUCCESS] Real JPL data fetched and cached.")
        print(f"  Cache: {CACHE_PATH}")
        print(f"  Source: jpl_horizons_online (REAL EPHEMERIS)")
        return True

    except Exception as e:
        print(f"\n[WARNING] Online JPL fetch failed: {e}")
        print("[INFO] Falling back to Keplerian IC generation...")
        print("[WARNING] Cache will be SELF-CONSISTENT, not REAL JPL.")
        print("[WARNING] Rule 9 (6000 km residual) CANNOT be verified with this cache.")
        print("[WARNING] Online JPL access is required for full compliance.")

    # --- Attempt 2: Keplerian fallback ---
    try:
        from nbody import (
            Body, nbody_integrate, G_SUN, G_EARTH, G_MOON,
            AU, V_EARTH, YEAR_SECONDS,
        )

        DAY_SEC = 86400.0
        JD0 = 2460702.5  # 2026-01-01 00:00 TDB

        # Keplerian ICs (DE440 mean elements, same as before)
        a_earth = 1.00000261 * AU
        e_earth = 0.01671123
        n_earth = 2.0 * np.pi / (365.25 * DAY_SEC)
        M0_earth = np.radians(100.0)
        lon_peri_earth = np.radians(102.9)

        E = M0_earth
        for _ in range(10):
            E = M0_earth + e_earth * np.sin(E)
        cos_f = (np.cos(E) - e_earth) / (1.0 - e_earth * np.cos(E))
        sin_f = (np.sqrt(1.0 - e_earth**2) * np.sin(E)) / (1.0 - e_earth * np.cos(E))
        f = np.arctan2(sin_f, cos_f)
        r_earth_mag = a_earth * (1.0 - e_earth**2) / (1.0 + e_earth * np.cos(f))

        r_orb = np.array([r_earth_mag * np.cos(f), r_earth_mag * np.sin(f)])
        vf = np.sqrt(G_SUN / (a_earth * (1.0 - e_earth**2)))
        v_orb = vf * np.array([-np.sin(f), e_earth + np.cos(f)])

        c, s = np.cos(lon_peri_earth), np.sin(lon_peri_earth)
        earth_r = np.array([c * r_orb[0] - s * r_orb[1],
                             s * r_orb[0] + c * r_orb[1]])
        earth_v = np.array([c * v_orb[0] - s * v_orb[1],
                             s * v_orb[0] + c * v_orb[1]])

        a_moon = 384400.0
        e_moon = 0.0549
        n_moon = 2.0 * np.pi / (27.321661 * DAY_SEC)
        M0_moon = np.radians(45.0)
        E_m = M0_moon
        for _ in range(10):
            E_m = M0_moon + e_moon * np.sin(E_m)
        cos_fm = (np.cos(E_m) - e_moon) / (1.0 - e_moon * np.cos(E_m))
        sin_fm = (np.sqrt(1.0 - e_moon**2) * np.sin(E_m)) / (1.0 - e_moon * np.cos(E_m))
        fm = np.arctan2(sin_fm, cos_fm)
        r_moon_mag = a_moon * (1.0 - e_moon**2) / (1.0 + e_moon * np.cos(fm))
        r_moon_geo = np.array([r_moon_mag * np.cos(fm), r_moon_mag * np.sin(fm)])
        vfm = np.sqrt(G_EARTH / (a_moon * (1.0 - e_moon**2)))
        v_moon_geo = vfm * np.array([-np.sin(fm), e_moon + np.cos(fm)])

        moon_r = earth_r + r_moon_geo
        moon_v = earth_v + v_moon_geo

        sun_r = np.array([0.0, 0.0])
        sun_v = np.array([0.0, 0.0])

        print(f"  Frame: @10 Sun-centered (Sun at origin)")
        print(f"  Earth |r0| = {np.linalg.norm(earth_r):.6e} km = {np.linalg.norm(earth_r)/AU:.4f} AU")
        print(f"  Earth |v0| = {np.linalg.norm(earth_v):.4f} km/s")
        print(f"  Moon  |r0| = {np.linalg.norm(moon_r):.6e} km")
        print(f"  Moon  |v0| = {np.linalg.norm(moon_v):.4f} km/s")

        print(f"\n  Integrating 1 year (h=3600s)...")
        bodies = [
            Body(name="Sun", mu=G_SUN, r=sun_r, v=sun_v, massless=False),
            Body(name="Earth", mu=G_EARTH, r=earth_r, v=earth_v, massless=False),
            Body(name="Moon", mu=G_MOON, r=moon_r, v=moon_v, massless=False),
        ]
        result = nbody_integrate(bodies, h=3600.0, T=YEAR_SECONDS, check_interval=1000)
        print(f"  Done. {len(result.t)} total steps.")

        # Build cache: 1 sample per day
        cache = {"Sun": {}, "Earth": {}, "Moon": {}}
        for key in ["jd_tdb", "calendar", "x_km", "y_km", "z_km",
                     "vx_kms", "vy_kms", "vz_kms"]:
            for b in cache:
                cache[b][key] = []

        for day in range(366):
            t_target = day * DAY_SEC
            idx = np.argmin(np.abs(result.t - t_target))
            jd = JD0 + day
            cal = f"2026-{(day // 31 + 1):02d}-{(day % 31 + 1):02d}"

            for name in ["Sun", "Earth", "Moon"]:
                cache[name]["x_km"].append(float(result.positions[name][idx, 0]))
                cache[name]["y_km"].append(float(result.positions[name][idx, 1]))
                cache[name]["z_km"].append(0.0)
                cache[name]["vx_kms"].append(float(result.velocities[name][idx, 0]))
                cache[name]["vy_kms"].append(float(result.velocities[name][idx, 1]))
                cache[name]["vz_kms"].append(0.0)
                cache[name]["jd_tdb"].append(jd)
                cache[name]["calendar"].append(cal)

        with open(CACHE_PATH, "w") as f:
            json.dump(cache, f, indent=2)

        # Add source metadata
        _add_cache_metadata(CACHE_PATH, source="keplerian_fallback",
                           message="Keplerian IC propagation (NOT real JPL)")

        print(f"\nCache written: {CACHE_PATH}")
        print(f"Sun  entries: {len(cache['Sun']['x_km'])}")
        print(f"Earth entries: {len(cache['Earth']['x_km'])}")
        print(f"Moon  entries: {len(cache['Moon']['x_km'])}")
        re0 = np.sqrt(cache["Earth"]["x_km"][0]**2 + cache["Earth"]["y_km"][0]**2)
        ve0 = np.sqrt(cache["Earth"]["vx_kms"][0]**2 + cache["Earth"]["vy_kms"][0]**2)
        print(f"Cache Earth |r0| = {re0:.6e} km = {re0/AU:.4f} AU")
        print(f"Cache Earth |v0| = {ve0:.4f} km/s")
        print("Done (Keplerian fallback).")
        return False

    except Exception as e2:
        print(f"[ERROR] Both online and Keplerian methods failed: {e2}")
        raise


if __name__ == "__main__":
    generate_cache()
