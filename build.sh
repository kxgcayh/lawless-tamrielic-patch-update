#!/usr/bin/env bash
# Build both plugins in both variants from YOUR copies of the original plugins and package the FOMOD zip.
# Inputs (put them in inputs/, see BUILDING.md):
#   Bandit War - Tamrielic Distribution.esp           Lawless Patch FOMOD 2.1.0 (Nexus mod 88080, file 473986)
#   Bandit War Expanded - Tamrielic Distribution.esp  Lawless Patch FOMOD 2.1.0
#   Tamrielic Distribution.esp                        Tamrielic Distribution 1.4.1, "00 Core"
#   Tamrielic Distribution - Netch Leather Armor.esp  Tamrielic Distribution 1.4.1, "01 CreationClub"
#   Tamrielic Distribution - Dead Man's Dread.esp     Tamrielic Distribution 1.4.1, "01 CreationClub"
#   Tamrielic Distribution - AA Silver.esp            Tamrielic Distribution 1.4.1, "01 CreationClub"
# Output: dist/Lawless - Tamrielic Distribution Patch Update (FOMOD).zip
# Needs: dotnet, python3, and the Spriggit.Yaml.Skyrim 0.41.0 translation DLL (SPRIGGIT_DLL or auto-detected).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
ROOT="$PWD"
INPUTS="${INPUTS:-$ROOT/inputs}"
BUILD="$ROOT/build"
DIST="$ROOT/dist"
ZIP="$DIST/Lawless - Tamrielic Distribution Patch Update (FOMOD).zip"
GAME=(-g SkyrimSE -p Spriggit.Yaml.Skyrim -v 0.41.0)
# rules key|plugin file name
PLUGINS=("bandit-war|Bandit War - Tamrielic Distribution.esp"
         "bandit-war-expanded|Bandit War Expanded - Tamrielic Distribution.esp")
TD="Tamrielic Distribution.esp"
# module key|plugin file name (the 1.4.1 Creation Club modules)
MODULES=("netch|Tamrielic Distribution - Netch Leather Armor.esp"
         "dmd|Tamrielic Distribution - Dead Man's Dread.esp"
         "silver|Tamrielic Distribution - AA Silver.esp")

find_dll() {
  if [ -n "${SPRIGGIT_DLL:-}" ]; then echo "$SPRIGGIT_DLL"; return; fi
  local dir base
  for dir in "${TMPDIR:-}" /tmp; do
    [ -n "$dir" ] || continue
    base="$dir/Spriggit/Translations/Spriggit.Yaml.Skyrim/0.41.0"
    [ -d "$base" ] || continue
    find "$base" -name Spriggit.Yaml.Skyrim.dll | head -n 1
  done | head -n 1
}
DLL="$(find_dll || true)"
if [ -z "$DLL" ] || [ ! -f "$DLL" ]; then
  echo "Spriggit.Yaml.Skyrim.dll 0.41.0 not found. See BUILDING.md ('Spriggit'), or set SPRIGGIT_DLL." >&2
  exit 1
fi

for f in "$TD" "${PLUGINS[0]#*|}" "${PLUGINS[1]#*|}" "${MODULES[0]#*|}" "${MODULES[1]#*|}" "${MODULES[2]#*|}"; do
  [ -f "$INPUTS/$f" ] || { echo "missing input: $INPUTS/$f (see BUILDING.md)" >&2; exit 1; }
done
(cd "$INPUTS" && python3 -I - "$ROOT/patch/inputs.sha256" <<'PY'
import hashlib, sys
for line in open(sys.argv[1]):
    want, name = line.split(None, 1); name = name.strip()
    got = hashlib.sha256(open(name, "rb").read()).hexdigest()
    if got != want:
        print(f"warning: {name} differs from the version this patch was written for", file=sys.stderr)
PY
)

rm -rf "$BUILD"
mkdir -p "$BUILD/orig" "$BUILD/yaml" "$BUILD/package/creation-club" "$BUILD/package/vanilla" "$DIST"

spriggit() { dotnet "$DLL" "$@" | grep -E "Unhandled|rror" || true; }

echo "serializing the original plugins"
mkdir -p "$BUILD/orig/td"
spriggit serialize -i "$INPUTS/$TD" -o "$BUILD/orig/td" "${GAME[@]}"
for entry in "${PLUGINS[@]}"; do
  key="${entry%%|*}"; plugin="${entry#*|}"
  mkdir -p "$BUILD/orig/$key"
  spriggit serialize -i "$INPUTS/$plugin" -o "$BUILD/orig/$key" "${GAME[@]}"
done
for entry in "${MODULES[@]}"; do
  key="${entry%%|*}"; plugin="${entry#*|}"
  mkdir -p "$BUILD/orig/modules/$key"
  spriggit serialize -i "$INPUTS/$plugin" -o "$BUILD/orig/modules/$key" "${GAME[@]}"
done

for entry in "${PLUGINS[@]}"; do
  key="${entry%%|*}"; plugin="${entry#*|}"
  for mode in creation-club vanilla; do
    python3 -I tools/apply_patch.py "$key" "$mode" "$BUILD/orig/$key" "$BUILD/orig/td" "$BUILD/orig/modules" "$BUILD/yaml/${mode%%-*}-$key"
  done
  spriggit deserialize -i "$BUILD/yaml/creation-$key" -o "$BUILD/package/creation-club/$plugin"
  spriggit deserialize -i "$BUILD/yaml/vanilla-$key" -o "$BUILD/package/vanilla/$plugin"
done

for variant in creation-club vanilla; do
  for entry in "${PLUGINS[@]}"; do
    [ -s "$BUILD/package/$variant/${entry#*|}" ] || { echo "deserialize produced no $variant/${entry#*|}" >&2; exit 1; }
  done
done

# A vanilla plugin must carry no Creation Club master.
if grep -l -a -E "ccbgs|ccmtys" "$BUILD"/package/vanilla/*.esp; then
  echo "vanilla variant still references Creation Club content" >&2
  exit 1
fi

cp fomod-src/README.txt "$BUILD/package/"
mkdir -p "$BUILD/package/fomod"
cp fomod-src/info.xml fomod-src/ModuleConfig.xml "$BUILD/package/fomod/"
python3 -I tools/package.py "$BUILD/package" "$ZIP"
