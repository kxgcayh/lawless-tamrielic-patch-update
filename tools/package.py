"""usage: package.py <package-dir> <output.zip>  -- validate the FOMOD XML and zip the package."""
import os, sys, zipfile
from xml.dom import minidom

pkg, out = sys.argv[1:3]
for x in ("info.xml", "ModuleConfig.xml"):
    minidom.parse(os.path.join(pkg, "fomod", x))

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for top in ("fomod", "vanilla", "creation-club", "README.txt"):
        p = os.path.join(pkg, top)
        paths = [p] if os.path.isfile(p) else sorted(os.path.join(d, f) for d, _, fs in os.walk(p) for f in fs)
        for f in paths:
            z.write(f, os.path.relpath(f, pkg).replace(os.sep, "/"))
    for i in z.infolist():
        print(f"{i.file_size:>8}  {i.filename}")
print("built:", out)
