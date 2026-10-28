"""Build the Spriggit tree of one patch plugin from a serialized original Lawless plugin.

usage: apply_patch.py <rules-key> <creation-club|vanilla> <original-tree> <td-core-tree> <modules-dir> <output-tree>

Every FormKey that comes from another mod is read from the user's own serialized copies:
  <original-tree>  the Lawless plugin to patch
  <td-core-tree>   Tamrielic Distribution 1.4.1 core plugin: record defaults (vanilla items), Jaree-Ra package
  <modules-dir>    netch/, dmd/, silver/: the 1.4.1 Creation Club modules, which override a proxy record with the
                   Creation Club item
patch/rules.json holds only the decisions.
"""
import glob, json, os, re, shutil, sys

key, mode, orig, td, modules, out = sys.argv[1:7]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rule = json.load(open(os.path.join(root, "patch", "rules.json")))[key]
cc_mode = mode == "creation-club"
if mode not in ("creation-club", "vanilla"):
    sys.exit("apply_patch: mode must be creation-club or vanilla")

CC_REF = re.compile(r"\b[0-9A-F]{6}:cc[\w.\-]+\.es[lm]\b")
VANILLA_REF = re.compile(r"\b[0-9A-F]{6}:(?:Skyrim|Update|Dragonborn)\.esm\b")


def fail(msg):
    sys.exit(f"apply_patch: {key}: {msg}")


def record(tree, formid):
    # A module also has its own records with colliding FormIDs; the file name suffix is the record's origin plugin.
    hit = glob.glob(os.path.join(tree, "*", f"* - {formid}_Tamrielic Distribution.esp.yaml"))
    if len(hit) != 1:
        fail(f"expected one record {formid} in {tree}, found {len(hit)}")
    return open(hit[0], encoding="utf-8").read()


def single(pattern, text, what):
    found = set(pattern.findall(text))
    if len(found) != 1:
        fail(f"{what}: expected exactly one reference, found {sorted(found)}")
    return found.pop()


def cc_item(mod, proxy):
    """The Creation Club item a 1.4.1 module puts into a proxy record."""
    return single(CC_REF, record(os.path.join(modules, mod), proxy), f"module {mod} record {proxy}")


def vanilla_item(proxy):
    """The vanilla item the 1.4.1 core plugin gives the same proxy record by default."""
    over = rule.get("vanilla_override", {})
    if proxy in over:
        return over[proxy]
    return single(VANILLA_REF, record(td, proxy), f"core record {proxy}")


def resolve(value, proxy):
    if isinstance(value, str):
        return value
    return cc_item(value["cc_from"], proxy) if cc_mode else vanilla_item(proxy)


shutil.copytree(orig, out)

# 1. FormKey substitution, one pass so a replacement is never rewritten again.
subs = {old: resolve(new, old.split(":")[0]) for old, new in rule["substitutions"].items()}
pat = re.compile("|".join(re.escape(k) for k in sorted(subs, key=len, reverse=True)))
hits = 0
for dp, _, fns in os.walk(out):
    for fn in fns:
        if fn == "RecordData.yaml" or not fn.endswith(".yaml"):
            continue
        p = os.path.join(dp, fn)
        t = open(p, encoding="utf-8").read()
        t2, n = pat.subn(lambda m: subs[m.group(0)], t)
        hits += n
        if n:
            open(p, "w", encoding="utf-8").write(t2)
if hits != rule["expected_substitutions"]:
    fail(f"made {hits} substitutions, expected {rule['expected_substitutions']}. "
         "The input plugin is not the Lawless Patch FOMOD 2.1.0 version this patch was written for.")

# 2. Masters: the Tamrielic Distribution slot becomes the new masters, in place (none for vanilla).
rd = os.path.join(out, "RecordData.yaml")
t = open(rd, encoding="utf-8").read()
old = f"  - Master: {rule['master_replace']['remove']}\n    FileSize: 0\n"
if old not in t:
    fail(f"master {rule['master_replace']['remove']} not found in RecordData.yaml")
masters = rule["master_replace"]["insert"] if cc_mode else []
open(rd, "w", encoding="utf-8").write(t.replace(old, "".join(f"  - Master: {m}\n    FileSize: 0\n" for m in masters)))

# 3. New outfit records. Items come from the modules (or the core defaults for vanilla).
for o in rule["new_outfits"]:
    items = [resolve(i, i["proxy"]) if isinstance(i, dict) else i for i in o["items"]]
    fid, modkey = o["formkey"].split(":", 1)
    os.makedirs(os.path.join(out, "Outfits"), exist_ok=True)
    body = f"FormKey: {o['formkey']}\nEditorID: {o['editor_id']}\nItems:\n" + "".join(f"- {i}\n" for i in items)
    open(os.path.join(out, "Outfits", f"{o['editor_id']} - {fid}_{modkey}.yaml"), "w", encoding="utf-8").write(body)

# 4. Records taken from the user's own Tamrielic Distribution 1.4.1, renamed into this plugin.
for imp in rule["import_from_td"]:
    lines = record(td, imp["source_formid"]).split("\n")
    if not (lines[0].startswith("FormKey: ") and lines[1].startswith("EditorID: ")):
        fail(f"unexpected layout in TD record {imp['source_formid']}")
    lines[0] = f"FormKey: {imp['new_formkey']}"
    lines[1] = f"EditorID: {imp['new_editor_id']}"
    fid, modkey = imp["new_formkey"].split(":", 1)
    dest = os.path.join(out, imp["folder"])
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, f"{imp['new_editor_id']} - {fid}_{modkey}.yaml"), "w", encoding="utf-8").write("\n".join(lines))

# 5. Nothing may still point at the old master, and a vanilla tree must not name a Creation Club file.
bad = re.compile(r":Tamrielic Distribution\.es[pl]" + ("" if cc_mode else r"|:cc[\w.\-]+\.es[lm]"))
left = [p for p in glob.glob(os.path.join(out, "**", "*.yaml"), recursive=True)
        if bad.search(open(p, encoding="utf-8").read())]
if left:
    fail(f"{len(left)} file(s) still reference a removed master, e.g. {left[0]}")
print(f"{key} [{mode}]: {hits} substitutions, {len(rule['new_outfits'])} outfits")
