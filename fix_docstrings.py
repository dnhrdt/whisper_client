#!/usr/bin/env python3
"""Docstring-Fixer für WhisperClient.

Dieses Skript behebt automatisch häufige Docstring-Probleme in Python-Dateien:
- D205: Fehlende Leerzeile zwischen Zusammenfassung und Beschreibung
- D400: Erste Zeile sollte mit einem Punkt enden
- D401: Erste Zeile sollte im Imperativ-Modus sein

Version: 1.0
Timestamp: 2025-04-20 19:00 CET

"""

import os
import re
import sys
from typing import List, Tuple


def find_python_files(directory: str) -> List[str]:
    """Finde alle Python-Dateien in einem Verzeichnis und seinen
    Unterverzeichnissen.

    Args:
        directory: Das zu durchsuchende Verzeichnis

    Returns:
        Eine Liste mit den Pfaden aller gefundenen Python-Dateien

    """
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def fix_docstring_d205(content: str) -> str:
    """
    Behebe D205: Füge eine Leerzeile zwischen Zusammenfassung und Beschreibung ein.

    Args:
        content: Der Dateiinhalt

    Returns:
        Der korrigierte Dateiinhalt
    """
    # Regulärer Ausdruck für Docstrings mit fehlender Leerzeile
    pattern = r'("""|\'\'\')([^\n]*)\n([^\n])'

    # Ersetze durch Docstring mit Leerzeile
    return re.sub(pattern, r"\1\2\n\n\3", content)


def fix_docstring_d400(content: str) -> str:
    """
    Behebe D400: Stelle sicher, dass die erste Zeile mit einem Punkt endet.

    Args:
        content: Der Dateiinhalt

    Returns:
        Der korrigierte Dateiinhalt
    """
    # Regulärer Ausdruck für Docstrings, deren erste Zeile nicht mit einem Punkt endet
    pattern = r'("""|\'\'\')([^\n.]*)\n'

    # Ersetze durch Docstring mit Punkt am Ende der ersten Zeile
    return re.sub(pattern, r"\1\2.\n", content)


def fix_docstring_d401(content: str) -> str:
    """
    Behebe D401: Stelle sicher, dass die erste Zeile im Imperativ-Modus ist.

    Args:
        content: Der Dateiinhalt

    Returns:
        Der korrigierte Dateiinhalt
    """
    # Diese Funktion ist komplexer und erfordert NLP-Fähigkeiten
    # Hier implementieren wir eine vereinfachte Version, die häufige Muster erkennt

    # Muster für häufige nicht-imperative Verben am Anfang von Docstrings
    patterns = [
        (r'("""|\'\'\')([^\n]*?)Returns ', r"\1Return "),
        (r'("""|\'\'\')([^\n]*?)Gets ', r"\1Get "),
        (r'("""|\'\'\')([^\n]*?)Sets ', r"\1Set "),
        (r'("""|\'\'\')([^\n]*?)Checks ', r"\1Check "),
        (r'("""|\'\'\')([^\n]*?)Creates ', r"\1Create "),
        (r'("""|\'\'\')([^\n]*?)Updates ', r"\1Update "),
        (r'("""|\'\'\')([^\n]*?)Deletes ', r"\1Delete "),
        (r'("""|\'\'\')([^\n]*?)Handles ', r"\1Handle "),
        (r'("""|\'\'\')([^\n]*?)Processes ', r"\1Process "),
        (r'("""|\'\'\')([^\n]*?)Validates ', r"\1Validate "),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def process_file(file_path: str, dry_run: bool = False) -> Tuple[bool, List[str]]:
    """Verarbeite eine Datei und behebe Docstring-Probleme.

    Args:
        file_path: Der Pfad zur zu verarbeitenden Datei
        dry_run: Wenn True, werden keine Änderungen geschrieben

    Returns:
        Ein Tupel mit einem Boolean, der angibt, ob Änderungen vorgenommen wurden,
        und einer Liste von Strings mit Beschreibungen der vorgenommenen Änderungen

    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        original_content = content
        changes = []

        # Behebe D205
        new_content = fix_docstring_d205(content)
        if new_content != content:
            content = new_content
            changes.append("D205: Leerzeile zwischen Zusammenfassung und Beschreibung hinzugefügt")

        # Behebe D400
        new_content = fix_docstring_d400(content)
        if new_content != content:
            content = new_content
            changes.append("D400: Punkt am Ende der ersten Zeile hinzugefügt")

        # Behebe D401
        new_content = fix_docstring_d401(content)
        if new_content != content:
            content = new_content
            changes.append("D401: Erste Zeile in Imperativ-Modus geändert")

        # Schreibe die Änderungen, wenn welche vorgenommen wurden und kein Dry-Run
        if content != original_content and not dry_run:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

        return content != original_content, changes

    except Exception as e:
        print(f"Fehler bei der Verarbeitung von {file_path}: {e}")
        return False, []


def main():
    """Hauptfunktion des Skripts.

    Verarbeitet alle Python-Dateien in den angegebenen Verzeichnissen
    und behebt Docstring-Probleme.

    """
    # Standardverzeichnisse
    directories = ["src", "tests", "tools"]

    # Kommandozeilenargumente verarbeiten
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("Dry-Run-Modus: Es werden keine Änderungen geschrieben.")

    # Verzeichnisse aus Kommandozeilenargumenten
    custom_dirs = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if custom_dirs:
        directories = custom_dirs

    # Statistiken
    total_files = 0
    changed_files = 0
    total_changes = 0

    # Verarbeite alle Dateien
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Verzeichnis {directory} existiert nicht. Überspringe.")
            continue

        python_files = find_python_files(directory)
        total_files += len(python_files)

        for file_path in python_files:
            changed, changes = process_file(file_path, dry_run)
            if changed:
                changed_files += 1
                total_changes += len(changes)
                print(f"Datei {file_path}:")
                for change in changes:
                    print(f"  - {change}")

    # Zusammenfassung ausgeben
    print("\nZusammenfassung:")
    print(f"  - {total_files} Dateien verarbeitet")
    print(f"  - {changed_files} Dateien geändert")
    print(f"  - {total_changes} Änderungen vorgenommen")

    if dry_run:
        print(
            "\nDies war ein Dry-Run. Führen Sie das Skript ohne --dry-run aus, um die Änderungen zu schreiben."
        )


if __name__ == "__main__":
    main()
