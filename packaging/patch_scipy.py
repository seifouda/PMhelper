"""
Patch scipy.stats._distn_infrastructure for PyInstaller compatibility.

Fixes: NameError: name 'obj' is not defined

The bug: scipy does `for obj in ...: exec('del '+obj); del obj`
but when PyInstaller freezes the module, the _doc_ variables don't exist,
the loop never runs, 'obj' is never assigned, and `del obj` fails.

Fix: Insert `obj = None` before the for-loop so `del obj` always works.
"""
import os
import sys


def patch_scipy():
    try:
        import scipy.stats._distn_infrastructure as m
    except NameError:
        # Already broken in this interpreter - find the file manually
        import scipy
        scipy_dir = os.path.dirname(scipy.__file__)
        filepath = os.path.join(scipy_dir, 'stats', '_distn_infrastructure.py')
    else:
        filepath = m.__file__

    if not filepath.endswith('.py'):
        # Maybe it's a .pyc - find the .py
        filepath = filepath.replace('.pyc', '.py')

    if not os.path.isfile(filepath):
        print(f"ERROR: Cannot find {filepath}")
        return False

    print(f"File: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    marker = "# PyInstaller fix v2"
    if marker in content:
        print("Already patched (v2).")
        return True

    # Remove any previous v1 patch
    content = content.replace("obj = None  # PyInstaller fix\n", "")

    # The problematic block:
    #   for obj in [s for s in dir() if s.startswith('_doc_')]:
    #       exec('del ' + obj)
    #   del obj
    # Replace with a try/except guarded version
    old_block = (
        "for obj in [s for s in dir() if s.startswith('_doc_')]:\n"
        "    exec('del ' + obj)\n"
        "del obj"
    )
    new_block = (
        "# PyInstaller fix v2\n"
        "try:\n"
        "    for obj in [s for s in dir() if s.startswith('_doc_')]:\n"
        "        exec('del ' + obj)\n"
        "    del obj\n"
        "except NameError:\n"
        "    pass"
    )
    if old_block not in content:
        print("Target block not found - scipy version may not need this patch.")
        return True

    patched = content.replace(old_block, new_block)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(patched)

    print("PATCHED successfully.")

    # Delete cached .pyc files
    cache_dir = os.path.join(os.path.dirname(filepath), '__pycache__')
    if os.path.isdir(cache_dir):
        for fname in os.listdir(cache_dir):
            if '_distn_infrastructure' in fname:
                os.remove(os.path.join(cache_dir, fname))
                print(f"  Deleted cache: {fname}")

    return True


if __name__ == '__main__':
    success = patch_scipy()
    sys.exit(0 if success else 1)
