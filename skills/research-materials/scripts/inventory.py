#!/usr/bin/env python3
"""Read-only file inventory. Paths and byte identity are not semantic judgments."""
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import stat


SKIP_NAMES = {'node_modules', '__pycache__', 'id_rsa', 'id_ed25519',
              'credentials.json', 'credentials', 'secrets.json', 'token.json'}


def inventory(root, hash_files=False):
    root = Path(root)
    if root.is_symlink():
        raise ValueError('The root must be a real directory, not a symbolic link')
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('The root must be a directory')
    files, skipped, errors = [], [], []

    def walk_error(error):
        errors.append({'path': os.path.relpath(error.filename, root),
                       'error': type(error).__name__})

    def reason(path):
        if path.is_symlink():
            return 'symbolic_link_not_followed'
        if path.name.startswith('.') or path.name in SKIP_NAMES:
            return 'hidden_or_excluded_name'
        return None

    for folder, directories, names in os.walk(root, followlinks=False, onerror=walk_error):
        directories.sort()
        for name in list(directories):
            path = Path(folder) / name
            skip = reason(path)
            if skip:
                directories.remove(name)
                skipped.append({'path': path.relative_to(root).as_posix(), 'reason': skip})
        for name in sorted(names):
            path = Path(folder) / name
            rel = path.relative_to(root).as_posix()
            skip = reason(path)
            if skip:
                skipped.append({'path': rel, 'reason': skip})
                continue
            try:
                before = path.lstat()
                if not stat.S_ISREG(before.st_mode):
                    skipped.append({'path': rel, 'reason': 'not_regular_file'})
                    continue
                item = {'path': rel, 'bytes': before.st_size, 'extension': path.suffix.lower()}
                if hash_files:
                    # Avoid following a symlink substituted between enumeration and open.
                    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
                    with os.fdopen(fd, 'rb') as stream:
                        opened = os.fstat(stream.fileno())
                        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                            raise OSError('File changed during inventory')
                        digest = hashlib.sha256()
                        for block in iter(lambda: stream.read(1024 * 1024), b''):
                            digest.update(block)
                        after = os.fstat(stream.fileno())
                    if (after.st_size, after.st_mtime_ns, after.st_ctime_ns) != (
                        before.st_size, before.st_mtime_ns, before.st_ctime_ns
                    ):
                        raise OSError('File changed during inventory')
                    item['sha256'] = digest.hexdigest()
                files.append(item)
            except OSError as error:
                errors.append({'path': rel, 'error': type(error).__name__})
    groups = defaultdict(list)
    if hash_files:
        for item in files:
            groups[item['sha256']].append(item['path'])
    return {
        'root': str(root), 'hashes_computed': hash_files,
        'file_count': len(files), 'bytes': sum(f['bytes'] for f in files),
        'files': files, 'byte_identical_groups': [v for v in groups.values() if len(v) > 1],
        'skipped': skipped, 'errors': errors,
        'note': 'No files changed. Hash equality does not authorize deletion. Content, versions, and scientific meaning were not verified.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--hash', action='store_true', help='Read file bytes and compute SHA-256')
    args = parser.parse_args()
    try:
        result = inventory(args.root, args.hash)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
