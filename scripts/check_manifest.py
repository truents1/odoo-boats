#!/usr/bin/env python3
import ast, sys, os, traceback

search_paths = [
    "/mnt/extra-addons/custom",
    "/mnt/extra-addons/third-party",
    "/var/lib/odoo/.local/share/Odoo/addons/17.0",
    "/usr/lib/python3/dist-packages/odoo/addons",
]

def check_manifest(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            src = f.read()
        # emulate Odoo load_manifest behaviour: ast.literal_eval on whole file
        ast.literal_eval(src)
        return True, None
    except Exception as e:
        return False, e

bad = []
for base in search_paths:
    if not os.path.isdir(base): continue
    for root, _, files in os.walk(base):
        for name in files:
            if name in ("__manifest__.py", "__openerp__.py"):
                p = os.path.join(root, name)
                ok, err = check_manifest(p)
                if not ok:
                    bad.append((p, err))
for p, err in bad:
    print("BAD:", p)
    print("ERROR:", repr(err))
    tb = traceback.format_exception_only(type(err), err)
    print("DETAIL:", "".join(tb))
if not bad:
    print("No manifest parse errors found.")
