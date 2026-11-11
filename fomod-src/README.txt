Lawless - Tamrielic Distribution Patch Update
=============================================

Replaces two plugins from "Lawless - A Bandit Overhaul - Lawless Patch FOMOD" (v2.1.0):

  Bandit War - Tamrielic Distribution.esp
  Bandit War Expanded - Tamrielic Distribution.esp

Why
---
Both originals master "Tamrielic Distribution.esp". Tamrielic Distribution 2.0 and later
replaced it with "Tamrielic Distribution.esl" and deleted the proxy records the originals
pointed at (FormIDs 0x00087D to 0x0009C0), so the game reports a missing master. Renaming the
master does not help: the 23 referenced records no longer exist in the new file.

Install
-------
Install this archive in Mod Organizer 2 and let it overwrite the Lawless patch files. Pick one
variant in the installer. Both variants contain the same two plugins under the same names.

Variants
--------
Vanilla (no Creation Club)
  Masters: Skyrim.esm, Dragonborn.esm, Bandit War.esp.
  Uses the vanilla items that Tamrielic Distribution 1.x proxies fell back to when no
  Creation Club module was installed. Works without the Anniversary Edition content.

Creation Club
  Additional masters: ccbgssse041-netchleather.esl (Netch Leather), ccbgssse031-advcyrus.esm
  (Dead Man's Dread), ccbgssse056-ba_silver.esl (Alternative Armors - Silver).
  Solstheim Reavers get Netch Leather armor, pirates and sailors get Dead Man's Dread clothing,
  Atar gets Silver armor. A missing file produces a missing-master error.

The installer preselects the Creation Club variant when all three files are active in your
load order, and the vanilla variant otherwise.

Neither variant depends on Tamrielic Distribution itself.

Vanilla item mapping (taken from the Tamrielic Distribution 1.4.1 proxy defaults)
---------------------------------------------------------------------------------
  Netch shields                    -> 013914 Skyrim.esm
  Netch cuirass                    -> 013911
  Boiled / shadowed cuirasses      -> 03619E
  Netch gauntlets / shadowed       -> 013912 / 013921
  Netch helmet and boiled helmet   -> 013913
  Shadowed helmets                 -> 013922
  Netch boots / shadowed           -> 013910 / 013920
  Boatswain clothes and shoes      -> 04223C / 04223D
  Scrub clothes                    -> 080697 (footwraps 07BC15 unchanged)
  Captain clothes / boots          -> 0F8715 / 0CEE82
  Silver outfit boots / cuirass / gauntlets -> 01395B / 01395C / 01395D

One deliberate deviation: the 1.4.1 proxy for the shadowed boiled helmet pointed at the
shield 013914, which looks like an upstream mistake. The vanilla variant uses the helmet 013922.

Verification and limits
-----------------------
Both vanilla plugins were built from Spriggit YAML and re-serialized: no differences other than
line order within a file. Neither plugin contains a Creation Club master (binary scan).
Item distribution has not been tested in game.

Credits and permissions
-----------------------
Based on the Lawless Patch FOMOD for "Lawless - A Bandit Overhaul" by Ooreeoo (Nexus mod 88080, free use with credit)
and on Tamrielic Distribution by Tate Taylor, Nexus user TateTaylorOH (Nexus mod 71372, use with credit, not in sold
files). Credit both authors if you reuse this. This patch is free and must stay free: do not sell it or put it behind a paywall.
