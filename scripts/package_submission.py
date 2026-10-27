"""
Script to assemble and verify the final submission package in dist/final_submission.
Ensures clean structure, excludes large model binaries, virtualenvs, and temporary files.
"""

import os
import shutil
import sys

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(WORKSPACE_DIR, "dist", "final_submission")

INCLUDE_DIRS = [
    "app",
    "docs",
    "scripts",
    "tests"
]

INCLUDE_DATA_SUBDIRS = [
    os.path.join("data", "bankstatemently_benchmark"),
    os.path.join("data", "evaluation"),
    os.path.join("data", "raw")
]

INCLUDE_FILES = [
    ".dockerignore",
    ".env.example",
    ".gitignore",
    "Dockerfile",
    "pytest.ini",
    "README.md",
    "render.yaml",
    "requirements.txt"
]

EXCLUDE_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    "models_cache",
    "venv",
    ".venv"
}

EXCLUDE_FILE_EXTENSIONS = (
    ".safetensors",
    ".bin",
    ".pt",
    ".pyc",
    ".pyo"
)

EXCLUDE_EXACT_FILES = {
    ".env",
    ".DS_Store"
}


def should_exclude_dir(dir_name: str) -> bool:
    return dir_name in EXCLUDE_DIR_NAMES


def should_exclude_file(file_name: str) -> bool:
    if file_name in EXCLUDE_EXACT_FILES:
        return True
    if file_name.endswith(EXCLUDE_FILE_EXTENSIONS):
        return True
    return False


def copy_tree_filtered(src: str, dst: str):
    os.makedirs(dst, exist_ok=True)
    for root, dirs, files in os.walk(src):
        # Exclude directories in-place
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]
        rel_path = os.path.relpath(root, src)
        dest_dir = os.path.join(dst, rel_path) if rel_path != "." else dst
        os.makedirs(dest_dir, exist_ok=True)
        for f in files:
            if not should_exclude_file(f):
                src_file = os.path.join(root, f)
                dest_file = os.path.join(dest_dir, f)
                shutil.copy2(src_file, dest_file)


def package_submission():
    print(f"Preparing final submission directory at: {DIST_DIR}")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)

    # 1. Copy top-level directories
    for d in INCLUDE_DIRS:
        src = os.path.join(WORKSPACE_DIR, d)
        dst = os.path.join(DIST_DIR, d)
        if os.path.exists(src):
            print(f"  Copying {d}/...")
            copy_tree_filtered(src, dst)

    # 2. Copy selected data directories (excluding models_cache)
    for d in INCLUDE_DATA_SUBDIRS:
        src = os.path.join(WORKSPACE_DIR, d)
        dst = os.path.join(DIST_DIR, d)
        if os.path.exists(src):
            print(f"  Copying {d}/...")
            copy_tree_filtered(src, dst)

    # Create empty processed & raw directories with .gitkeep
    os.makedirs(os.path.join(DIST_DIR, "data", "processed"), exist_ok=True)
    with open(os.path.join(DIST_DIR, "data", "processed", ".gitkeep"), "w") as f:
        pass

    # 3. Copy top-level files
    for f in INCLUDE_FILES:
        src = os.path.join(WORKSPACE_DIR, f)
        dst = os.path.join(DIST_DIR, f)
        if os.path.exists(src):
            print(f"  Copying {f}...")
            shutil.copy2(src, dst)

    # 4. Verification of packaged contents
    total_files = 0
    total_bytes = 0
    prohibited_found = []

    for root, dirs, files in os.walk(DIST_DIR):
        for d in dirs:
            if should_exclude_dir(d):
                prohibited_found.append(os.path.join(root, d))
        for f in files:
            total_files += 1
            fpath = os.path.join(root, f)
            fsize = os.path.getsize(fpath)
            total_bytes += fsize
            if should_exclude_file(f):
                prohibited_found.append(fpath)

    print("\n------------------------------------------------------------")
    print(f"Submission Package Created Successfully:")
    print(f"  Location: {DIST_DIR}")
    print(f"  Total Files: {total_files}")
    print(f"  Total Size: {total_bytes / (1024*1024):.2f} MB")
    print(f"  Prohibited Large/Secret Files Detected: {len(prohibited_found)}")
    print("------------------------------------------------------------\n")

    if prohibited_found:
        print("ERROR: Prohibited files were packaged:")
        for p in prohibited_found:
            print("  -", p)
        sys.exit(1)


if __name__ == "__main__":
    package_submission()
