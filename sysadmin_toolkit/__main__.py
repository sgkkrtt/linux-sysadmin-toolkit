import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import sys
import tarfile
import tempfile
from datetime import datetime, timezone


def inventory():
    memory = {}
    try:
        for line in Path('/proc/meminfo').read_text().splitlines():
            key, value = line.split(':', 1)
            if key in ('MemTotal', 'MemAvailable'):
                memory[key] = int(value.strip().split()[0]) * 1024
    except FileNotFoundError:
        pass
    return {'hostname': platform.node(), 'kernel': platform.release(),
            'architecture': platform.machine(), 'cpu_count': os.cpu_count(),
            'load_average': list(os.getloadavg()), 'memory_bytes': memory}


def disk_report(path, threshold):
    usage = shutil.disk_usage(path)
    percent = (usage.total - usage.free) / usage.total * 100
    return {'path': str(Path(path).resolve()), 'total_bytes': usage.total,
            'free_bytes': usage.free, 'used_percent': round(percent, 2),
            'alert': percent >= threshold, 'threshold': threshold}


def backup(source, destination, apply=False):
    source = Path(source).resolve(strict=True)
    destination = Path(destination).resolve(strict=True)
    if not source.is_dir() or not destination.is_dir():
        raise ValueError('La source et la destination doivent être des dossiers existants.')
    if source == Path('/') or destination == source or source in destination.parents:
        raise ValueError('Source racine ou destination dans la source : opération refusée.')
    # Ne pas parcourir de liens ni archiver sockets, périphériques ou FIFO.
    entries = [source]
    for root, dirs, names in os.walk(source, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(root) / d).is_symlink())
        entries.extend(Path(root) / d for d in dirs)
        entries.extend(Path(root) / n for n in sorted(names))
    entries = [e for e in entries if stat.S_ISREG(e.lstat().st_mode) or stat.S_ISDIR(e.lstat().st_mode)]
    result = {'source': str(source), 'destination': str(destination),
              'entries': len(entries), 'mode': 'apply' if apply else 'dry-run'}
    if not apply:
        return result
    fd, name = tempfile.mkstemp(prefix='backup-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-'),
                                suffix='.tar.gz', dir=destination)
    os.close(fd)
    archive = Path(name)
    try:
        with tarfile.open(archive, 'w:gz', dereference=False) as tar:
            for entry in entries:
                # Vérifier à nouveau le type au moment de l'ajout.
                if entry.is_symlink():
                    raise ValueError('La source a changé pendant la sauvegarde.')
                tar.add(entry, arcname=str(Path(source.name) / entry.relative_to(source)), recursive=False)
        digest = hashlib.sha256()
        with archive.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        checksum = archive.with_suffix(archive.suffix + '.sha256')
        with open(checksum, 'x', opener=lambda path, flags: os.open(path, flags, 0o600)) as stream:
            stream.write(digest.hexdigest() + '  ' + archive.name + '\n')
        result.update(archive=str(archive), sha256=digest.hexdigest())
    except BaseException:
        archive.unlink(missing_ok=True)
        raise
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='Diagnostic Linux et sauvegardes locales explicites.')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('inventory', help='Inventaire en lecture seule, au format JSON')
    disk = sub.add_parser('disk', help='Contrôle de capacité')
    disk.add_argument('--path', default='/')
    disk.add_argument('--threshold', type=int, default=85)
    save = sub.add_parser('backup', help='Simulation de sauvegarde par défaut')
    save.add_argument('--source', required=True)
    save.add_argument('--destination', required=True)
    save.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.command == 'inventory':
            result = inventory()
        elif args.command == 'disk':
            if not 1 <= args.threshold <= 100:
                raise ValueError('Le seuil doit être compris entre 1 et 100.')
            result = disk_report(args.path, args.threshold)
        else:
            result = backup(args.source, args.destination, args.apply)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1 if result.get('alert') else 0
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f'Erreur : {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
