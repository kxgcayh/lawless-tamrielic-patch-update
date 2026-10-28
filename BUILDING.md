# Building from source

Back to [README.md](README.md). The technical notes are in [NOTES.md](NOTES.md).


This repository contains no plugin data from other mods. It holds only the changes (`patch/`) and the
tools. You supply the original plugins; Spriggit extracts them on your machine and the build applies the
changes and writes the new plugins.

## Platforms

Tested: macOS (arm64) only. Expected to work, but not run:

- **Linux:** needs `bash`, `python3`, `find`, `grep` and the .NET 10 SDK.
- **Windows:** run `bash build.sh` from WSL or Git Bash; `cmd` and PowerShell do not work. Make sure `python3` exists
  (Git Bash often only has `python`) and set `SPRIGGIT_DLL`, because the automatic DLL lookup only checks `$TMPDIR` and `/tmp`.
  `.gitattributes` keeps `build.sh` on LF line endings, which bash needs.

## What you need

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

## Spriggit

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

## Run

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
BUILDING.md               How to build from source
NOTES.md                  Technical notes and the full record mapping
inputs/                   Your copies of the original plugins (not tracked)
build/, dist/             Generated (not tracked)
```
