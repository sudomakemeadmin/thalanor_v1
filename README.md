<div align="center">

# ⚔️ THALANOR: ZATOPIONE KRONIKI

### *Tekstowa gra RPG — Dark Fantasy*

**Wersja 1.9** · Demo — Akt I: „Popiół i cisza"

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/Licencja-MIT-green)
![Status](https://img.shields.io/badge/Status-Demo%20Akt%20I-orange)
![Lines](https://img.shields.io/badge/Linie%20kodu-2449-informational)

```
Budzisz się w starej chacie na skraju lasu.
Twoja przeszłość wydaje się być rozmazana.
Czujesz tylko ból, zapach dymu i ciszę, która przychodzi po rzezi.
```

</div>

---

> 🇬🇧 **[English version below](#-thalanor-sunken-chronicles)**

---

## 🇵🇱 Wersja Polska

### 📖 O grze

**Thalanor: Zatopione Kroniki** to konsolowa gra RPG osadzona w mrocznym świecie dark fantasy. Gracz wciela się w postać, która budzi się pozbawiona wspomnień po zagładzie rodzinnej wioski. Każdy wybór ma konsekwencje — otwiera lub zamyka ścieżki fabularne, zmienia narrację i wpływa na zakończenie.

Gra powstała jako projekt zaliczeniowy z **Programowania Obiektowego** na uczelni wyższej.

### 🎮 Mechaniki

| Mechanika | Opis |
|---|---|
| 🧠 **4 statystyki** | Siła, Zręczność, Inteligencja, Witalność — wpływają na dostępne wybory |
| ⚔️ **Walka** | Probabilistyczny system oparty na rzutach statystykowych |
| 🎒 **Ekwipunek** | Plecak (20 slotów) + 3 sloty założonego ekwipunku (broń/zbroja/hełm) |
| 💰 **Ekonomia** | Dwuwalutowy system: srebro i złoto |
| 🔀 **Rozgałęzienia** | Wybory wpływają na narrację — dynamiczne teksty zależne od ścieżki gracza |
| 💾 **Zapis/Odczyt** | 4 sloty zapisu w formacie JSON |
| 🔁 **Tryb eksploracji** | Wykonuj akcje opcjonalne przed przejściem dalej w fabule |
| ⬆️ **Levelowanie** | System doświadczenia z awansami i ręcznym rozdawaniem punktów |

### 🗺️ Fabuła (bez spoilerów)

Akt I prowadzi gracza przez:
- Przebudzenie w chacie tajemniczego starca
- Odkrywanie prawdy o zniszczonej wiosce
- Wędrówkę przez niebezpieczny las pełen pułapek
- Spotkania z postaciami — od pomocnych po wrogich
- Walkę z pradawnymi istotami
- Odkrycie tajemnicy, która zmienia wszystko

> *„Każdy wybór ma cenę. Czasem to słowa, nie stal, decydują o tym kto doczeka świtu."*

### 🚀 Uruchomienie

#### Opcja 1 — Gotowy plik `.exe` (Windows, bez instalacji)

1. Pobierz `thalanor_v1_9.exe` z repozytorium
2. Uruchom — gra startuje od razu, Python nie jest wymagany

> **Uwaga:** Windows Defender może wyświetlić ostrzeżenie przy pierwszym uruchomieniu — to normalne przy nieznanym pliku .exe. Kliknij „Więcej informacji" → „Uruchom mimo to".

#### Opcja 2 — Uruchomienie z kodu źródłowego (Python)

**Wymagania:** Python 3.10+, brak dodatkowych zależności

```bash
# Sklonuj repozytorium
git clone https://github.com/sudomakemeadmin/thalanor.git
cd thalanor

# Uruchom grę
python thalanor_v1_9.py
```

> **Uwaga:** Gra korzysta z emoji w terminalu. Dla najlepszego efektu zalecany jest terminal wspierający Unicode (Windows Terminal, iTerm2, nowoczesne terminale Linux).

### 📁 Struktura projektu

```
thalanor/
├── thalanor_v1_9.py           # Kod źródłowy gry
├── thalanor_v1_9.exe          # Skompilowana wersja (Windows)
├── README.md                  # Ten plik
├── thalanor_save_slot1.json   # Slot zapisu 1 (generowany w trakcie gry)
├── thalanor_save_slot2.json   # Slot zapisu 2
├── thalanor_save_slot3.json   # Slot zapisu 3
└── thalanor_save_slot4.json   # Slot zapisu 4
```

### 🏗️ Architektura

Gra oparta jest na **9 klasach** z jasnym podziałem odpowiedzialności:

```
Game (silnik rozgrywki)
 ├── Character (postać gracza)
 │    ├── Inventory (plecak)
 │    │    └── Item (przedmiot)
 │    └── Equipment (założony ekwipunek)
 │         └── Item (przedmiot)
 ├── Scene (scena / lokacja)
 │    └── Choice (wybór gracza)
 └── SaveManager (zapis / odczyt)
```

Zastosowane wzorce: **Command** (fabryki efektów), **Observer** (hooki scen), **State** (flagi fabularne), **Serializer** (JSON save/load).

### 🛣️ Roadmap

- [x] Silnik gry z systemem scen i wyborów
- [x] System statystyk, ekwipunku i walki
- [x] Dynamiczna narracja (hooki)
- [x] Zapis / odczyt (4 sloty JSON)
- [x] Akt I — kompletna fabuła z rozgałęzieniami
- [ ] Interfejs graficzny (Tkinter / PyEngine)
- [ ] Muzyka i efekty dźwiękowe
- [ ] Akt II — kontynuacja fabuły
- [ ] System handlu z NPC

### 👥 Autorzy

| Autor | Zakres |
|---|---|
| **Adam Ostrowski** | Item, Equipment, Choice, menu główne, silnik gry, fabuła |
| **Arkadiusz Noiszewski** | Inventory, Character, Scene, SaveManager, fabryki efektów, hooki |

### 📄 Licencja

Projekt udostępniony na licencji MIT — szczegóły w pliku `LICENSE`.

---
---

<div align="center">

## 🇬🇧 THALANOR: SUNKEN CHRONICLES

### *Text-based RPG — Dark Fantasy*

</div>

### 📖 About

**Thalanor: Sunken Chronicles** is a console-based text RPG set in a dark fantasy world. The player takes on the role of a character who awakens with no memories after the destruction of their home village. Every choice matters — decisions open or close story paths, alter narration dynamically, and shape the ending.

Built as a university project for an **Object-Oriented Programming** course.

### 🎮 Features

- **4 core stats** (Strength, Dexterity, Intelligence, Vitality) that gate story choices
- **Probabilistic combat** based on stat rolls
- **Inventory & equipment** system (20-slot backpack + 3 gear slots)
- **Dual-currency economy** (silver & gold)
- **Branching narrative** with dynamically adapted text based on player decisions
- **Save/Load** system with 4 JSON slots
- **Exploration mode** — perform optional actions before advancing the story
- **Leveling system** with manual stat point distribution

### 🚀 Quick Start

**Option 1 — Windows `.exe` (no installation needed):**
Download `thalanor_v1_9.exe` from the repository and run it.

**Option 2 — From source (Python 3.10+):**
```bash
git clone https://github.com/sudomakemeadmin/thalanor.git
cd thalanor
python thalanor_v1_9.py
```

No external dependencies required.

> **Note:** The game is written entirely in Polish. An English localization is not currently planned but may be considered in the future.

### 🏗️ Architecture

9 classes built around composition and the Command pattern:

| Class | Role |
|---|---|
| `Game` | Main engine — scene loop, menus, effect factories, hooks |
| `Character` | Player state — stats, HP, inventory, flags, serialization |
| `Scene` | Location with narrative, choices, enter hooks, exit conditions |
| `Choice` | Player option with requirements, effects, one-time tracking |
| `Item` | Game object with type, stats, serialization |
| `Inventory` | Backpack with 20-slot limit |
| `Equipment` | 3 gear slots (weapon / armor / helmet) |
| `SaveManager` | JSON save/load with 4 slots |

### 👥 Authors

- **Adam Ostrowski** — Item, Equipment, Choice, main menu, game engine, story
- **Arkadiusz Noiszewski** — Inventory, Character, Scene, SaveManager, effect factories, hooks

### 📄 License

MIT

---

<div align="center">

*Każdy wybór ma cenę. / Every choice has a price.*

⚔️

</div>
