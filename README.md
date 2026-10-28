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

See [BUILDING.md](BUILDING.md) for building the plugins yourself (Spriggit, the input files, `build.sh`) and for changing the patch.

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
