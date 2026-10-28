# Lawless - Tamrielic Distribution Patch Update

Replacement for two plugins of the Lawless Patch FOMOD (v2.1.0, for "Lawless - A Bandit Overhaul") so
they load with Tamrielic Distribution 2.0 and later:

- `Bandit War - Tamrielic Distribution.esp`
- `Bandit War Expanded - Tamrielic Distribution.esp`

Skyrim Special Edition and Anniversary Edition. Not tested on VR.

## The problem

Both original plugins master `Tamrielic Distribution.esp`. Tamrielic Distribution 2.0 replaced it with
`Tamrielic Distribution.esl` and deleted the proxy records the originals pointed at (FormIDs `0x00087D`
to `0x0009C0`, 23 of them are referenced). The game reports a missing master. Changing the master from
`.esp` to `.esl` does not help: the referenced records no longer exist in the new file, so the references
resolve to nothing.

In Tamrielic Distribution 1.x each proxy was a leveled list that defaulted to a vanilla item; the
Tamrielic Distribution Creation Club modules overrode it with the Creation Club item. The original patches
therefore needed no Creation Club content. Version 2.0 has no proxy layer, so reaching a Creation Club
item now means mastering its plugin directly.

## Variants

The release is a FOMOD with one choice. Both variants contain the same two plugins under the same names,
and neither depends on Tamrielic Distribution.

| Variant | Extra masters | Result |
|---|---|---|
| Vanilla | none | Reavers, pirates and sailors get the vanilla items the 1.x proxies defaulted to |
| Creation Club | `ccbgssse041-netchleather.esl`, `ccbgssse031-advcyrus.esm`, `ccbgssse056-ba_silver.esl` | Netch Leather for Solstheim Reavers, Dead Man's Dread for pirates and sailors, Silver armor for Atar |

The installer preselects Creation Club when all three files are active, and Vanilla otherwise. The three
Creation Club files are part of the Anniversary Edition bundle.

The item-by-item mapping and the technical details are in [NOTES.md](NOTES.md).

## Install

Install the FOMOD zip with Mod Organizer 2 or Vortex and let it overwrite the Lawless patch files.

## Build from source

This repository contains no plugin data from other mods. It holds only the changes (`patch/`) and the
tools. You supply the original plugins; Spriggit extracts them on your machine and the build applies the
changes and writes the new plugins.

### What you need

Download these yourself and put the six plugin files in `inputs/` (create the folder):

| File in `inputs/` | Where it comes from |
|---|---|
| `Bandit War - Tamrielic Distribution.esp` | [Lawless Patch FOMOD 2.1.0](https://www.nexusmods.com/skyrimspecialedition/mods/88080?tab=files&file_id=473986) (optional file, file ID 473986) of "Lawless - A Bandit Overhaul", folder `Tamrielic Distribution/` in the archive |
| `Bandit War Expanded - Tamrielic Distribution.esp` | the same archive, folder `Tamrielic Distribution - Expanded/` |
| `Tamrielic Distribution.esp` | Tamrielic Distribution **1.4.1**, `00 Core/` in the old-version download on the [Nexus page](https://www.nexusmods.com/skyrimspecialedition/mods/71372) |
| `Tamrielic Distribution - Netch Leather Armor.esp` | the same 1.4.1 download, `01 CreationClub/` |
| `Tamrielic Distribution - Dead Man's Dread.esp` | the same, `01 CreationClub/` |
| `Tamrielic Distribution - AA Silver.esp` | the same, `01 CreationClub/` |

The Tamrielic Distribution 1.4.1 plugins are the source of every item FormKey the patch uses: the core plugin
gives the vanilla default of each proxy record and the Jaree-Ra AI package, and each Creation Club module
overrides a proxy with the Creation Club item. Nothing from them is stored in this repository.
`patch/inputs.sha256` lists the file hashes this patch was written against. A different hash only prints a
warning; different content stops the build (see below).

Tools: the .NET 10 SDK, Python 3, `bash`, and Spriggit 0.41.0 (see below, most Skyrim users do not have it).

### Spriggit

[Spriggit](https://github.com/Mutagen-Modding/Spriggit) is a command line tool from the Mutagen project
that converts a Skyrim plugin (`.esp`, `.esm`, `.esl`) into a folder of readable YAML files and back. It is
a modding developer tool, not part of a normal Skyrim install, and **you only need it to rebuild the patch**.
To just use the patch, install the FOMOD zip and skip this section.

Install (needs the .NET 10 SDK, `dotnet --version` must print 10 or higher):

```
dotnet tool install --global Spriggit.CLI --version 0.41.0
```

Spriggit then downloads the Skyrim serializer package `Spriggit.Yaml.Skyrim` 0.41.0 the first time it
converts a plugin. The build calls that package's DLL directly. It looks in
`<temp>/Spriggit/Translations/Spriggit.Yaml.Skyrim/0.41.0/`; if you keep it elsewhere, point `SPRIGGIT_DLL`
at `Spriggit.Yaml.Skyrim.dll`. To fill the folder, serialize any plugin once:

```
spriggit serialize --InputPath "inputs/Tamrielic Distribution.esp" --OutputPath some-empty-folder --GameRelease SkyrimSE --PackageName Spriggit.Yaml.Skyrim --PackageVersion 0.41.0
```

The CLI prints its version with a nonzero exit status; that is normal. On macOS the CLI itself crashes during
a conversion (`kernel32.dll` cannot be loaded by a dependency's process tracker), so there the DLL has to
come from the package download described below.

`dotnet restore` rejects `Spriggit.Yaml.Skyrim` (it is a tool-type package). Instead download
`https://api.nuget.org/v3-flatcontainer/spriggit.yaml.skyrim/0.41.0/spriggit.yaml.skyrim.0.41.0.nupkg`, unzip it
(a `.nupkg` is a zip) and set `SPRIGGIT_DLL` to `tools/net10.0/any/Spriggit.Yaml.Skyrim.dll` inside it. With that DLL
`bash build.sh` ran to the end on macOS (arm64, .NET 10.0.402); only the CLI crashes there.

These steps are untested on a machine that has never run Spriggit.

### Run

```
bash build.sh
```

Output: `dist/Lawless - Tamrielic Distribution Patch Update (FOMOD).zip`. Intermediate files are in `build/`.

What the script does:

1. Serializes the three input plugins to YAML with Spriggit.
2. `tools/apply_patch.py` runs twice per Lawless plugin, once per variant, using the decisions in
   `patch/rules.json`:
   - it rewrites each reference to a Tamrielic Distribution proxy record. Creation Club variant: to the item
     the 1.4.1 module overrides that proxy with. Vanilla variant: to the item the 1.4.1 core plugin gives the
     proxy by default;
   - it swaps the Tamrielic Distribution master for the Creation Club masters (none for vanilla);
   - it writes the new outfit records, with items read the same way;
   - it copies the Jaree-Ra package out of the core plugin under a new FormKey and EditorID.
3. Deserializes both variants to `.esp` files, fails if a vanilla plugin still names a Creation Club
   master, validates the FOMOD XML and zips the package.

The build refuses to continue if a Lawless plugin yields a different number of substitutions than
`patch/rules.json` expects (43 and 80), or if any reference to the old Tamrielic Distribution master is left.
That is the guard against building from a different version of the Lawless patch.

The result is deterministic: the same inputs give byte-identical plugins.

## Changing the patch

- Which proxy maps to which module, the new outfits and their FormKeys, and the one vanilla override:
  `patch/rules.json`.
- After a build, re-serialize a built plugin with `-g SkyrimSE -p Spriggit.Yaml.Skyrim -v 0.41.0` and compare.
  Spriggit drops unknown YAML fields silently, and item order inside a record can differ, so compare with
  lines sorted.

## Repository layout

```
patch/rules.json          Decisions: proxy-to-module mapping, new outfits, masters, expected counts
patch/inputs.sha256       Hashes of the input plugins this was written against
tools/apply_patch.py      Applies the rules to serialized plugins, per variant
tools/package.py          FOMOD XML check and zip
fomod-src/                FOMOD info.xml, ModuleConfig.xml, README.txt shipped in the zip
build.sh                  Build and package
tests/                    Unit test of apply_patch.py (python3 -m unittest discover tests)
NOTES.md                  Technical notes and the full record mapping
inputs/                   Your copies of the original plugins (not tracked)
build/, dist/             Generated (not tracked)
```

## Verification status

- Built from the original plugins, the four output plugins are byte-identical to the ones first built by hand
  from edited YAML.
- Built plugins re-serialize to the source YAML apart from line order within a file.
- A binary scan finds no Creation Club master in the vanilla plugins.
- Item distribution has not been tested in game.

## Credits and permissions

The patch changes plugins from the Lawless Patch FOMOD for "Lawless - A Bandit Overhaul" so that they work
with Tamrielic Distribution by Tate Taylor. This repository does not contain those plugins or any record
copied from them. The built
FOMOD zip does contain modified plugins, so check the Lawless and Tamrielic Distribution permissions before you
distribute that zip. No Creation Club assets are included; the Creation Club variant references them by
FormKey only.

No license is set for the repository yet.
