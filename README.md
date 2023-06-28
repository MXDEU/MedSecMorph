# MedSec biometrischer Matcher

Programm zum Matching von biometrischen Morphs und ihren Originalen.

## Vorraussetzungen

- CMake
- C++ Compiler
- Python3
- Python Modul `face-biometric-recognition` (https://pypi.org/project/face-biometric-recognition/)
  - (setzt Dlib als Bibliothek vorraus)

Hinweis: die originalen Bilder stammen aus der London Face DB. Erwartet wird ein bestimmtes Format
des Dateinamen: `{3-stellige Nummer; mit führenden Nullen}_003.jpg`. Die Morphbilder müssen wiefolgt
benannt sein: `{Programm}-{Nummer des ersten Originals}_{Nummer des zweiten Originals}.jpg`. Diese
liegen jeweil in einem `morph-{Ersteller}` Ordner. Nach dieser Struktur wird beim automatisierten
Modus gesucht; der Modus erwartet die Originale im `images` Ordner.

Dateistruktur (Beispiel):
- images
  - 001_003.jpg
  - 010_003.jpg
- morphs-name
  - gimp-001_010.jpg
  - squirlz-001_010.jpg
- verify.py

## Verwendung

Parameter:
- `a`: führt den automatisierten Modus aus
- `t <float>`: setzt den Schwellwert des Matchers: [0, 1]
- `MORPH`: Morphbild (Pfad relativ zur Ausführung)
- `REAL...`: 1+ originale Bilder (Pfad relativ zur Ausführung)

Sypnose: `python3 verify.py -at [t] MORPH REAL...`
Bei der automatisierten Ausführung müssen die Parameter `REAL` und `MORPH` nicht angegeben werden.

### Manueller Modus

Gibt pro angegebenes Original `True` oder `False` aus, wenn es aus Sicht des Matchers
biometrisch identisch ist. Zusätzlich kann der Schwellwert angegeben werden.

Beispiel: `python3 verify.py -t 0.5 morphs-amelie/gimp-001_002.jpg images/001_03.jpg images/002_03.jpg images/003_03.jpg`

### Automatisierter Modus

Führt alle Ordner mit Präfix `morph-` aus und vergleicht alle Morphs mit ihren Originalen.
Am Ende werden Metriken wie MAR und FAR zu dem gesamten Datensatz, als auch gruppiert nach
Ersteller (Morphordner) und Programm, erstellt.

Verwendung: `python3 verify.py -a -t 0.5`