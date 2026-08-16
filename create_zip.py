"""
create_zip.py — Packages the entire AI Recruitment System project into a zip file.
"""

import os
import zipfile

PROJECT_DIR = os.path.dirname(__file__)
ZIP_FILENAME = os.path.join(PROJECT_DIR, "ai_recruitment_system_complete.zip")

EXCLUDE_DIRS = [".pytest_cache", "__pycache__", ".git"]
EXCLUDE_FILES = ["ai_recruitment_system_complete.zip", ".DS_Store"]

def package_project():
    with zipfile.ZipFile(ZIP_FILENAME, 'w', zipfile.ZIP_DEFLATED) as ziph:
        for root, dirs, files in os.walk(PROJECT_DIR):
            # Modify dirs in-place to skip excluded folders
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file in EXCLUDE_FILES or file.endswith(".pyc"):
                    continue
                
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, PROJECT_DIR)
                arcname = os.path.join("ai-recruitment-system", rel_path)
                
                ziph.write(abs_path, arcname)
                print(f"Added: {rel_path}")

    print(f"\n✓ Successfully created zip package: {ZIP_FILENAME}")
    print(f"Size: {os.path.getsize(ZIP_FILENAME)} bytes")

if __name__ == "__main__":
    package_project()
