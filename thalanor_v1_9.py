# -*- coding: utf-8 -*-
"""
THALANOR: ZATOPIONE KRONIKI
Tekstowa gra RPG – Demo Akt I: "Popiół i cisza"

Wersja: 1.9 


Autorzy: Adam Ostrowski, Arkadiusz Noiszewski
"""

import json
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# =============================================================================
# UTIL
# =============================================================================

    # Funkcja pomocnicza do bezpiecznego pobierania danych od użytkownika
    # Autor: A.O
def safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        print("\n[Wejście przerwane. Wpisz 0 aby wyjść lub kontynuuj.]")
        return ""


    # Zwraca aktualny timestamp jako string
    # Autor: A.O
def now_ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    # Oczyszcza string z białych znaków
    # Autor: A.O
def norm(raw: str) -> str:
    return (raw or "").strip()


# =============================================================================
# ITEM / INVENTORY / EQUIPMENT
# =============================================================================

@dataclass
# Klasa reprezentująca przedmiot w grze
# Autor: A.O
class Item:
    item_id: str
    name: str
    description: str
    item_type: str  # weapon, armor, helmet, consumable, misc
    damage: int = 0
    armor: int = 0
    value: int = 0
    heal: int = 0

    def __str__(self) -> str:
        parts = []
        if self.damage:
            parts.append(f"OBR: {self.damage}")
        if self.armor:
            parts.append(f"PANC: {self.armor}")
        if self.heal:
            parts.append(f"LECZY: {self.heal}")
        suffix = f" ({', '.join(parts)})" if parts else ""
        return f"{self.name}{suffix}"

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type,
            "damage": self.damage,
            "armor": self.armor,
            "value": self.value,
            "heal": self.heal,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        return cls(
            item_id=data["item_id"],
            name=data["name"],
            description=data.get("description", ""),
            item_type=data["item_type"],
            damage=data.get("damage", 0),
            armor=data.get("armor", 0),
            value=data.get("value", 0),
            heal=data.get("heal", 0),
        )


@dataclass
# Klasa zarządzająca plecakiem gracza
# Autor: A.N
class Inventory:
    max_slots: int = 20
    items: List[Item] = field(default_factory=list)

    def add_item(self, item: Item) -> bool:
        if len(self.items) >= self.max_slots:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item_id: str) -> Optional[Item]:
        for i, it in enumerate(self.items):
            if it.item_id == item_id:
                return self.items.pop(i)
        return None

    def has_item(self, item_id: str) -> bool:
        return any(it.item_id == item_id for it in self.items)

    def display(self) -> None:
        if not self.items:
            print("  (Plecak pusty)")
            return
        for i, it in enumerate(self.items, 1):
            print(f"  {i}. {it}")


@dataclass
# Klasa zarządzająca założonym ekwipunkiem (broń, zbroja, hełm)
# Autor: A.O
class Equipment:
    SLOTS = ["weapon", "armor", "helmet"]
    slots: Dict[str, Optional[Item]] = field(default_factory=lambda: {s: None for s in Equipment.SLOTS})

    def equip(self, item: Item) -> Optional[Item]:
        slot = item.item_type
        if slot not in self.slots:
            return None
        old = self.slots[slot]
        self.slots[slot] = item
        return old

    def unequip(self, slot: str) -> Optional[Item]:
        if slot not in self.slots:
            return None
        old = self.slots[slot]
        self.slots[slot] = None
        return old

    def total_damage(self) -> int:
        return sum(it.damage for it in self.slots.values() if it)

    def total_armor(self) -> int:
        return sum(it.armor for it in self.slots.values() if it)

    def display(self) -> None:
        print("  Założony ekwipunek:")
        for slot in self.SLOTS:
            it = self.slots.get(slot)
            print(f"   - {slot:8}: {it.name if it else '(pusto)'}")


# =============================================================================
# CHARACTER
# =============================================================================

@dataclass
# Klasa reprezentująca postać gracza - główny obiekt stanu gry
# Autor: A.N
class Character:
    name: str
    level: int = 1
    experience: int = 0

    strength: int = 1
    dexterity: int = 1
    intelligence: int = 1
    vitality: int = 1

    max_hp: int = 10
    max_mp: int = 10
    current_hp: int = 10
    current_mp: int = 10

    gold: int = 0
    silver: int = 0

    inventory: Inventory = field(default_factory=Inventory)
    equipment: Equipment = field(default_factory=Equipment)

    used_actions: Set[str] = field(default_factory=set)
    flags: Dict[str, Any] = field(default_factory=dict)
    reputation: int = 0
    npc_relations: Dict[str, int] = field(default_factory=dict)

    @property
    def exp_to_level(self) -> int:
        return self.level * 100

    def add_experience(self, amount: int) -> None:
        if amount <= 0:
            return
        self.experience += amount
        print(f"  +{amount} DOŚWIADCZENIA")
        while self.experience >= self.exp_to_level:
            self.experience -= self.exp_to_level
            self.level_up()

    def level_up(self) -> None:
        self.level += 1
        self.max_hp += 5
        self.max_mp += 3
        self.current_hp = self.max_hp
        self.current_mp = self.max_mp
        print()
        print("═" * 60)
        print(f"  ⭐⭐⭐ AWANS! OSIĄGNĄŁEŚ POZIOM {self.level}! ⭐⭐⭐")
        print("═" * 60)
        print("  Zyskujesz: +5 MAKS. HP, +3 MAKS. MP (pełne uleczenie)")
        print()
        print("  🎁 MASZ 2 PUNKTY STATYSTYK DO ROZDANIA!")
        print("─" * 60)
        self._distribute_stat_points(2)

    def _distribute_stat_points(self, points: int) -> None:
        """Pozwala graczowi rozdać punkty statystyk."""
        remaining = points
        while remaining > 0:
            print(f"\n  Pozostałe punkty: {remaining}")
            print(f"  Aktualne statystyki:")
            print(f"    1. SIŁA: {self.strength}")
            print(f"    2. ZRĘCZNOŚĆ: {self.dexterity}")
            print(f"    3. INTELIGENCJA: {self.intelligence}")
            print(f"    4. WITALNOŚĆ: {self.vitality}")
            print()
            
            try:
                choice = input("  Wybierz statystykę (1-4): ").strip()
                if choice == "1":
                    self.strength += 1
                    print(f"  +1 SIŁA (teraz: {self.strength})")
                    remaining -= 1
                elif choice == "2":
                    self.dexterity += 1
                    print(f"  +1 ZRĘCZNOŚĆ (teraz: {self.dexterity})")
                    remaining -= 1
                elif choice == "3":
                    self.intelligence += 1
                    print(f"  +1 INTELIGENCJA (teraz: {self.intelligence})")
                    remaining -= 1
                elif choice == "4":
                    self.vitality += 1
                    self.max_hp += 2
                    self.current_hp = min(self.max_hp, self.current_hp + 2)
                    print(f"  +1 WITALNOŚĆ (teraz: {self.vitality}), +2 MAKS. HP")
                    remaining -= 1
                else:
                    print("  Nieprawidłowy wybór. Wpisz 1, 2, 3 lub 4.")
            except (EOFError, KeyboardInterrupt):
                print("\n  Automatycznie przydzielam pozostałe punkty do SIŁY.")
                self.strength += remaining
                remaining = 0
        
        print("─" * 60)
        print("  ✅ Punkty rozdane! Kontynuujesz przygodę...")
        print("═" * 60)

    def add_money(self, gold: int = 0, silver: int = 0) -> None:
        self.gold += max(0, gold)
        self.silver += max(0, silver)
        if self.silver >= 100:
            self.gold += self.silver // 100
            self.silver = self.silver % 100
        if gold:
            print(f"  +{gold} ZŁOTA")
        if silver:
            print(f"  +{silver} SREBRA")

    def take_damage(self, amount: int) -> None:
        if amount <= 0:
            return
        armor = self.equipment.total_armor()
        actual = max(1, amount - armor)
        self.current_hp = max(0, self.current_hp - actual)
        print(f"  OTRZYMUJESZ {actual} OBRAŻEŃ (ŻYCIE: {self.current_hp}/{self.max_hp})")

    def heal(self, amount: int) -> None:
        if amount <= 0:
            return
        before = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        gained = self.current_hp - before
        if gained > 0:
            print(f"  +{gained} ŻYCIA (ŻYCIE: {self.current_hp}/{self.max_hp})")

    def check_requirement(self, req: Dict[str, Any]) -> Tuple[bool, Optional[Tuple[str, Any]]]:
        for k, v in req.items():
            if k in ("strength", "dexterity", "intelligence", "vitality", "level"):
                cur = getattr(self, k)
                if cur < int(v):
                    label = {
                        "strength": "SIŁA",
                        "dexterity": "ZRĘCZNOŚĆ",
                        "intelligence": "INTELIGENCJA",
                        "vitality": "WITALNOŚĆ",
                        "level": "POZIOM",
                    }[k]
                    return False, ("stat", (label, int(v)))
            elif k == "has_item":
                if not self.inventory.has_item(str(v)):
                    return False, ("has_item", str(v))
            elif k == "flag":
                if isinstance(v, (list, tuple)) and len(v) == 2:
                    name, expected = v[0], v[1]
                    if self.flags.get(name) != expected:
                        return False, ("flag", (name, expected))
                else:
                    name = str(v)
                    if not bool(self.flags.get(name, False)):
                        return False, ("flag", (name, True))
            elif k == "not_used":
                if str(v) in self.used_actions:
                    return False, ("not_used", str(v))
        return True, None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "level": self.level,
            "experience": self.experience,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "intelligence": self.intelligence,
            "vitality": self.vitality,
            "max_hp": self.max_hp,
            "max_mp": self.max_mp,
            "current_hp": self.current_hp,
            "current_mp": self.current_mp,
            "gold": self.gold,
            "silver": self.silver,
            "inventory": [it.to_dict() for it in self.inventory.items],
            "equipment": {slot: (it.to_dict() if it else None) for slot, it in self.equipment.slots.items()},
            "used_actions": sorted(list(self.used_actions)),
            "flags": self.flags,
            "reputation": self.reputation,
            "npc_relations": self.npc_relations,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        ch = cls(name=data.get("name", "Bohater"))
        ch.level = data.get("level", 1)
        ch.experience = data.get("experience", 0)
        ch.strength = data.get("strength", 1)
        ch.dexterity = data.get("dexterity", 1)
        ch.intelligence = data.get("intelligence", 1)
        ch.vitality = data.get("vitality", 1)
        ch.max_hp = data.get("max_hp", 10)
        ch.max_mp = data.get("max_mp", 10)
        ch.current_hp = data.get("current_hp", ch.max_hp)
        ch.current_mp = data.get("current_mp", ch.max_mp)
        ch.gold = data.get("gold", 0)
        ch.silver = data.get("silver", 0)

        inv_data = data.get("inventory", [])
        ch.inventory = Inventory()
        ch.inventory.items = [Item.from_dict(d) for d in inv_data]

        eq_data = data.get("equipment", {})
        ch.equipment = Equipment()
        for slot, it_data in eq_data.items():
            ch.equipment.slots[slot] = Item.from_dict(it_data) if it_data else None

        ch.used_actions = set(data.get("used_actions", []))
        ch.flags = data.get("flags", {}) or {}
        ch.reputation = int(data.get("reputation", 0))
        ch.npc_relations = data.get("npc_relations", {}) or {}
        return ch

# =============================================================================
# CHOICE / SCENE
# =============================================================================

EffectFn = Callable[["Game"], None]
OnEnterFn = Callable[["Game"], None]
ExitConditionFn = Callable[["Game"], Optional[str]]


@dataclass
# Klasa reprezentująca wybór gracza w scenie
# Autor: A.O
class Choice:
    text: str
    next_scene: Optional[str]
    requirements: Dict[str, Any] = field(default_factory=dict)
    effects: List[EffectFn] = field(default_factory=list)
    one_time_id: Optional[str] = None
    hidden_if_unavailable: bool = False

    def is_done(self, game: "Game") -> bool:
        return bool(self.one_time_id) and (self.one_time_id in game.character.used_actions)

    def is_available(self, game: "Game") -> bool:
        if self.is_done(game):
            return False
        ok, _ = game.character.check_requirement(self.requirements)
        return ok

    def block_reason(self, game: "Game") -> Optional[str]:
        ok, reason = game.character.check_requirement(self.requirements)
        if ok or not reason:
            return None

        kind, data = reason
        if kind == "stat":
            label, val = data
            return f"WYMAGANA {label} {val}"
        if kind == "flag":
            return "NAJPIERW WYKONAJ WCZEŚNIEJSZE DZIAŁANIA"
        if kind == "has_item":
            return f"WYMAGANY PRZEDMIOT: {data}"
        if kind == "not_used":
            return "TO JUŻ ZOSTAŁO ZROBIONE"
        return "ZABLOKOWANE"

    def display(self, idx: int, game: "Game") -> None:
        if self.is_done(game):
            print(f"  V. {self.text} [ZROBIONE]")
            return

        if not self.is_available(game):
            reason = self.block_reason(game)
            print(f"  X. {self.text} [{reason}]")
            return

        print(f"  {idx}. {self.text}")

    def apply(self, game: "Game") -> None:
        if self.one_time_id:
            game.character.used_actions.add(self.one_time_id)
        for fn in self.effects:
            fn(game)


@dataclass
# Klasa reprezentująca scenę (lokację) w grze
# Autor: A.N
class Scene:
    scene_id: str
    title: str
    narration: str
    choices: List[Choice] = field(default_factory=list)
    explore_mode: bool = False
    subscenes: List[str] = field(default_factory=list)
    on_enter: Optional[OnEnterFn] = None
    exit_condition: Optional[ExitConditionFn] = None
    objective: Optional[str] = None

    def enter(self, game: "Game") -> None:
        if self.on_enter:
            self.on_enter(game)

    def check_exit(self, game: "Game") -> Optional[str]:
        if self.exit_condition:
            return self.exit_condition(game)
        return None

    def display(self, game: "Game") -> List[Tuple[int, Choice]]:
        ch = game.character
        weapon = ch.equipment.slots.get("weapon")
        weapon_name = weapon.name if weapon else "BRAK"

        # Statystyki zawsze na górze - czytelny pasek
        print("\n" + "═" * 80)
        print(f"  ❤️  ŻYCIE: {ch.current_hp}/{ch.max_hp}  |  ⭐ POZIOM: {ch.level}  |  📊 EXP: {ch.experience}/{ch.exp_to_level}")
        print(f"  💪 SIŁ: {ch.strength}  |  🏃 ZRĘ: {ch.dexterity}  |  🧠 INT: {ch.intelligence}  |  🛡️  WIT: {ch.vitality}")
        print(f"  💰 SREBRO: {ch.silver}  |  🪙  ZŁOTO: {ch.gold}  |  ⚔️  BROŃ: {weapon_name}")
        print("═" * 80)
        
        # Tytuł sceny
        print(f"\n  📍 {self.title}")
        print("─" * 80)
        
        # Narracja
        print(self.narration)

        if self.objective:
            print()
            print("┄" * 80)
            print(f"  >>> CEL: {self.objective} <<<")
            print("┄" * 80)

        # Separator przed wyborami
        print()
        print("─" * 80)
        print("  DOSTĘPNE AKCJE:")
        print("─" * 80)

        shown: List[Tuple[int, Choice]] = []
        idx = 1
        for c in self.choices:
            if c.hidden_if_unavailable and not c.is_available(game):
                continue
            shown.append((idx, c))
            c.display(idx, game)
            idx += 1

        print("─" * 80)
        print("Wpisz NUMER opcji lub 'menu'. | [O] = opcjonalne | [F] = fabularne")
        print("Legenda: X = zablokowane, V = zrobione (jednorazowe).")
        return shown


# =============================================================================
# SAVE MANAGER
# =============================================================================

# Klasa odpowiedzialna za zapis i odczyt gry z plików JSON
# Autor: A.N - Klasa zarządzająca zapisami gry
class SaveManager:
    SLOT_COUNT = 4
    SLOT_FILES = [f"thalanor_save_slot{i}.json" for i in range(1, SLOT_COUNT + 1)]

    @classmethod
    def slot_info(cls, idx: int) -> Optional[dict]:
        path = cls.SLOT_FILES[idx]
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @classmethod
    def save(cls, idx: int, ch: Character, scene_id: str) -> None:
        data = {
            "timestamp": now_ts(),
            "scene": scene_id,
            "character": ch.to_dict(),
        }
        with open(cls.SLOT_FILES[idx], "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Zapisano grę.")

    @classmethod
    def load(cls, idx: int) -> Tuple[Optional[Character], Optional[str]]:
        try:
            with open(cls.SLOT_FILES[idx], "r", encoding="utf-8") as f:
                data = json.load(f)
            return Character.from_dict(data["character"]), data["scene"]
        except Exception:
            return None, None
# =============================================================================
# GAME
# =============================================================================

# Główna klasa gry - zarządza pętlą rozgrywki i scenami
# Autorzy: A.O + A.N - Główna klasa gry (silnik rozgrywki)
class Game:
    INTRO_TEXT = (
        "Budzisz się w starej chacie na skraju lasu.\n"
        "Twoja przeszłość wydaje się być rozmazana.\n\n"
        "Czujesz tylko ból, zapach dymu i ciszę, która przychodzi po rzezi.\n"
        "Przypominasz sobie o tym, że coś złego wydarzyło się w twojej rodzinnej wiosce.\n"
        "Ale jedno pytanie wisi w powietrzu bez odpowiedzi: dlaczego i gdzie jestem?\n\n"
        "Każdy wybór ma cenę. Czasem to słowa, nie stal, decydują o tym kto doczeka świtu."
    )

    DEFAULT_NAMES = ["Kaelen", "Rhodan", "Mirel", "Syrien", "Aragorn", "Fila", "Filavandrel", "Cahir", "Desmond"]

    def __init__(self):
        self.character: Optional[Character] = None
        self.current_scene_id: str = "prolog_instincts"
        self.scenes: Dict[str, Scene] = {}
        self.items_db: Dict[str, Item] = {}
        self.running: bool = True

        self._create_items()
        self._create_scenes()

    # -------------------------
    # Items
    # -------------------------
    def _create_items(self) -> None:
        self.items_db = {
            "bandage": Item(
                "bandage", "Prowizoryczny bandaż",
                "Kawałek materiału, który może uratować życie.", "consumable",
                value=3, heal=2
            ),
            "primitive_stick": Item(
                "primitive_stick", "Prymitywny kij",
                "Krzywy, twardy kij. Prymitywny, ale lepszy niż gołe pięści.", "weapon",
                damage=3, value=8
            ),
            "silver_knife": Item(
                "silver_knife", "Srebrny nóż",
                "Pięknie zdobiony nóż ze szczerego srebra. Symbole na rękojeści są nieznane.", "weapon",
                damage=5, value=50
            ),
        }

    # -------------------------
    # Slots UI
    # -------------------------
    def _print_slots(self) -> None:
        print("\n--- SLOTY ZAPISU (1–4) ---")
        for i in range(SaveManager.SLOT_COUNT):
            info = SaveManager.slot_info(i)
            if not info:
                print(f"  {i+1}. (PUSTO)")
            else:
                ts = info.get("timestamp", "brak daty")
                scene = info.get("scene", "?")
                name = (info.get("character", {}) or {}).get("name", "Bohater")
                lvl = (info.get("character", {}) or {}).get("level", 1)
                print(f"  {i+1}. {name} (POZIOM {lvl}) | scena: {scene} | zapis: {ts}")
        print()

    def _choose_slot(self, prompt: str) -> Optional[int]:
        self._print_slots()
        raw = safe_input(prompt)
        if raw is None:
            return None
        raw = raw.strip()
        if raw == "":
            return None
        try:
            n = int(raw)
            if 1 <= n <= SaveManager.SLOT_COUNT:
                return n - 1
        except ValueError:
            pass
        print("Nieprawidłowy slot.")
        return None

    # -------------------------
    # Menus
    # -------------------------
        # Autor metody: A.O
    def main_menu(self) -> bool:
        while True:
            print("\n" + "=" * 80)
            print("  THALANOR: ZATOPIONE KRONIKI — DEMO (AKT I)")
            print("=" * 80)
            print(self.INTRO_TEXT)
            print("\n--- MENU ---")
            print("  1. Nowa gra")
            print("  2. Wczytaj grę")
            print("  0. Wyjście\n")

            c = safe_input("Wybierz: ")
            if c is None:
                continue
            c = c.strip()

            if c == "1":
                self.create_character()
                self.current_scene_id = "prolog_instincts"
                return True

            if c == "2":
                slot = self._choose_slot("Wybierz numer slotu do wczytania (1-4) lub Enter aby wrócić: ")
                if slot is None:
                    continue
                ch, sid = SaveManager.load(slot)
                if ch and sid:
                    self.character = ch
                    self.current_scene_id = sid
                    return True
                print("Ten slot jest pusty albo zapis uszkodzony.")
                continue

            if c == "0":
                return False

            print("Nieprawidłowy wybór! - spróbuj ponownie")

    def game_menu(self) -> None:
        while True:
            print("\n--- MENU GRY ---")
            print("  1. Statystyki")
            print("  2. Ekwipunek")
            print("  3. Plecak")
            print("  4. Zapisz grę (wybór slotu)")
            print("  5. Nowa gra")
            print("  0. Powrót")
            c = safe_input("Wybierz: ")
            if c is None:
                continue
            c = c.strip()

            if c == "1":
                self.character_stats_screen()
            elif c == "2":
                self.equipment_menu()
            elif c == "3":
                print("\n--- PLECAK ---")
                self.character.inventory.display()
            elif c == "4":
                slot = self._choose_slot("Zapisz w slocie (1-4) lub Enter aby anulować: ")
                if slot is None:
                    continue
                SaveManager.save(slot, self.character, self.current_scene_id)
            elif c == "5":
                ans = safe_input("Czy na pewno chcesz rozpocząć nową grę? (t/n): ")
                if ans is None:
                    continue
                ans = ans.strip().lower()
                if ans == "t":
                    self.create_character()
                    self.current_scene_id = "prolog_instincts"
                    return
            elif c == "0" or c == "":
                return

    def character_stats_screen(self) -> None:
        ch = self.character
        print("\n" + "=" * 80)
        print(f"  {ch.name} — POZIOM {ch.level}")
        print("=" * 80)
        print(f"  DOŚWIADCZENIE: {ch.experience}/{ch.exp_to_level} (do poziomu {ch.level+1})")
        print(f"  ŻYCIE: {ch.current_hp}/{ch.max_hp}")
        print("-" * 80)
        print(f"  SIŁA: {ch.strength}")
        print(f"  ZRĘCZNOŚĆ: {ch.dexterity}")
        print(f"  INTELIGENCJA: {ch.intelligence}")
        print(f"  WITALNOŚĆ: {ch.vitality}")
        print("-" * 80)
        print(f"  ZŁOTO: {ch.gold} | SREBRO: {ch.silver}")
        print(f"  OBRAŻENIA (z broni): {ch.equipment.total_damage()} | PANCERZ: {ch.equipment.total_armor()}")
        print("=" * 80)

    def equipment_menu(self) -> None:
        ch = self.character
        print("\n--- EKWIPUNEK ---")
        ch.equipment.display()
        print("\n  1. Załóż przedmiot z plecaka")
        print("  2. Zdejmij przedmiot")
        print("  0. Powrót")
        c = safe_input("Wybierz: ")
        if c is None:
            return
        c = c.strip()

        if c == "1":
            print("\n--- PLECAK ---")
            ch.inventory.display()
            if not ch.inventory.items:
                return
            raw = safe_input("Numer przedmiotu do założenia: ")
            if raw is None:
                return
            raw = raw.strip()
            if raw == "":
                return
            try:
                n = int(raw)
                if 1 <= n <= len(ch.inventory.items):
                    it = ch.inventory.items[n - 1]
                    if it.item_type not in Equipment.SLOTS:
                        print("Tego nie da się założyć.")
                        return
                    ch.inventory.items.remove(it)
                    old = ch.equipment.equip(it)
                    print(f"Założono: {it.name}")
                    if old:
                        ch.inventory.add_item(old)
                        print(f"Zdjęto: {old.name}")
            except ValueError:
                return

        elif c == "2":
            slot = safe_input("Slot (weapon/armor/helmet): ")
            if slot is None:
                return
            slot = slot.strip().lower()
            it = ch.equipment.unequip(slot)
            if it:
                ch.inventory.add_item(it)
                print(f"Zdjęto: {it.name}")

    # -------------------------
    # Character creation
    # -------------------------
    def create_character(self) -> None:
        while True:
            raw = safe_input("\nNadaj imię swojego bohatera (Enter = wybór losowy): ")
            if raw is None:
                continue
            raw = raw.strip()
            if raw:
                name = raw
                break

            candidate = random.choice(self.DEFAULT_NAMES)
            confirm = safe_input(f"Chcesz, żebym nadał imię: {candidate}? (t/n): ")
            if confirm is None:
                continue
            confirm = confirm.strip().lower()
            if confirm == "t":
                name = candidate
                break

        self.character = Character(name=name)
        # pełne HP na start (potem prolog ustawi 3/ max)
        self.character.current_hp = self.character.max_hp
        self.character.flags = {}
        self.character.used_actions = set()

    # -------------------------
    # Engine
    # -------------------------
    def play_scene(self) -> None:
        scene = self.scenes.get(self.current_scene_id)
        if not scene:
            print(f"[BŁĄD] Brak sceny: {self.current_scene_id}. Powrót do prologu.")
            self.current_scene_id = "prolog_instincts"
            return

        scene.enter(self)

        nxt = scene.check_exit(self)
        if nxt:
            self.current_scene_id = nxt
            return

        options = scene.display(self)

        while True:
            raw = safe_input("\nTwój wybór: ")
            if raw is None:
                continue
            raw = raw.strip()

            # PUSTE / SPACJE => nie wyłączamy gry
            if raw == "":
                print("Podaj numer opcji albo wpisz 'menu'.")
                continue

            low = raw.lower()
            if low == "menu":
                self.game_menu()
                options = scene.display(self)
                continue

            try:
                n = int(raw)
            except ValueError:
                print("Podaj numer opcji albo wpisz 'menu'.")
                continue

            chosen = None
            for idx, c in options:
                if idx == n:
                    chosen = c
                    break
            if not chosen:
                print("Nieprawidłowy wybór.")
                continue

            if not chosen.is_available(self):
                if chosen.is_done(self):
                    print("To już zostało zrobione.")
                else:
                    print("Ta opcja jest zablokowana.")
                continue

            chosen.apply(self)
            if chosen.next_scene is not None:
                self.current_scene_id = chosen.next_scene
            break

        # Autor metody: A.O
    def run(self) -> None:
        if not self.main_menu():
            print("\nDo zobaczenia!")
            return

        while self.running:
            self.play_scene()

            if self.character.current_hp <= 0:
                print()
                print("═" * 60)
                print("  💀💀💀 NIE ŻYJESZ 💀💀💀")
                print("═" * 60)
                print()
                print("  Twoja historia dobiegła końca...")
                print("  Ciemność pochłania wszystko. Ból ustępuje miejsca nicości.")
                print()
                print("═" * 60)
                print()
                ans = safe_input("Chcesz wczytać zapisaną grę? (t/n): ")
                if ans and ans.strip().lower() == "t":
                    slot = self._choose_slot("Wybierz slot do wczytania (1-4) lub Enter aby wrócić do menu: ")
                    if slot is not None:
                        ch, sid = SaveManager.load(slot)
                        if ch and sid:
                            self.character = ch
                            self.current_scene_id = sid
                            continue
                    # Jeśli nie wczytano - wróć do menu głównego
                    if self.main_menu():
                        continue
                break

            if self.character.flags.get("act1_completed", False):
                print("\n*** KONIEC WERSJI DEMONSTRACYJNEJ (AKT I) ***")
                print("Dalsze prace trwają. W przyszłości możliwym będzie utworzenie gry na silniku graficznym PyEngine.\n")
                print("Autorzy: Adam Ostrowski, Arkadiusz Noiszewski\n")
                ans = safe_input("Czy na pewno chcesz wyjść z gry? (t/n): ")
                if ans and ans.strip().lower() == "t":
                    break
                if not self.main_menu():
                    break

        print("Dziękujemy za grę!")

    # =============================================================================
    # FX helpers
    # =============================================================================

        # Autor fabryk efektów: A.N
    def fx_add_exp(self, amt: int) -> EffectFn:
        def _fn(game: "Game"):
            game.character.add_experience(amt)
        return _fn

    def fx_add_hp(self, amt: int) -> EffectFn:
        def _fn(game: "Game"):
            if amt >= 0:
                game.character.heal(amt)
            else:
                game.character.take_damage(-amt)
        return _fn

    def fx_add_silver(self, amt: int) -> EffectFn:
        def _fn(game: "Game"):
            game.character.add_money(silver=amt)
        return _fn

    def fx_add_silver_rng(self, lo: int, hi: int) -> EffectFn:
        def _fn(game: "Game"):
            s = random.randint(lo, hi)
            game.character.add_money(silver=s)
        return _fn

    def fx_flag(self, key: str, value: Any = True) -> EffectFn:
        def _fn(game: "Game"):
            game.character.flags[key] = value
        return _fn

    # Autor: A.O - Helper do wyświetlania tekstu po wyborze
    def fx_print(self, text: str) -> EffectFn:
        def _fn(game: "Game"):
            print("\n" + text + "\n")
        return _fn

    def fx_stat(self, stat: str, delta: int, cap: Optional[int] = None) -> EffectFn:
        def _fn(game: "Game"):
            ch = game.character
            cur = getattr(ch, stat)
            newv = cur + delta
            if cap is not None:
                newv = min(newv, cap)
            setattr(ch, stat, newv)

            label = {
                "strength": "SIŁA",
                "dexterity": "ZRĘCZNOŚĆ",
                "intelligence": "INTELIGENCJA",
                "vitality": "WITALNOŚĆ",
            }.get(stat, stat.upper())

            sign = "+" if delta > 0 else ""
            print(f"  {sign}{delta} {label}")

            if stat == "vitality" and delta > 0:
                ch.max_hp += 2 * delta
                ch.current_hp = min(ch.max_hp, ch.current_hp + 2 * delta)
                print(f"  +{2 * delta} do MAKS. ŻYCIA (teraz {ch.max_hp})")
        return _fn

    def fx_add_item(self, item_id: str) -> EffectFn:
        def _fn(game: "Game"):
            it = game.items_db[item_id]
            ok = game.character.inventory.add_item(Item.from_dict(it.to_dict()))
            if ok:
                print(f"  OTRZYMUJESZ: {it.name}")
            else:
                print("  Plecak jest pełny — nie możesz tego zabrać.")
        return _fn

    def fx_equip_first_weapon_if_any(self) -> EffectFn:
        def _fn(game: "Game"):
            ch = game.character
            for it in list(ch.inventory.items):
                if it.item_type == "weapon":
                    ch.inventory.items.remove(it)
                    old = ch.equipment.equip(it)
                    print(f"  Zakładasz broń: {it.name}")
                    if old:
                        ch.inventory.add_item(old)
                    return
            print("  Nie masz broni do założenia.")
        return _fn

    def _fx_clear_directions(self, except_key: str) -> EffectFn:
        def _fn(game: "Game"):
            for k in ("direction_forest", "direction_hills", "direction_swamp"):
                game.character.flags[k] = (k == except_key)
        return _fn

    def _fx_bandage_or_int_heal(self) -> EffectFn:
        def _fn(game: "Game"):
            ch = game.character
            if ch.inventory.has_item("bandage"):
                ch.inventory.remove_item("bandage")
                ch.heal(2)
                print("  Zużyto bandaż.")
                return
            if ch.intelligence >= 2:
                ch.heal(1)
                print("  Opatrujesz rany najlepiej jak potrafisz.")
                return
            print("  Nie masz bandaża ani wiedzy, by to zrobić skutecznie.")
        return _fn

    def _fx_share_item_and_rep(self, item_id: str, exp: int) -> EffectFn:
        def _fn(game: "Game"):
            it = game.character.inventory.remove_item(item_id)
            if not it:
                print("  Nie masz tego przedmiotu.")
                return
            game.character.add_experience(exp)
            print("  Dzielisz się zasobami. Ktoś to zapamięta.")
        return _fn

    def _fx_fight_damage(self, base_dmg: int) -> EffectFn:
        def _fn(game: "Game"):
            ch = game.character
            dmg = base_dmg
            if ch.flags.get("fight_advantage", False):
                dmg = max(1, base_dmg - 1)
            ch.take_damage(dmg)
        return _fn

    def _fx_final_defend(self) -> EffectFn:
        def _fn(game: "Game"):
            game.character.take_damage(2)
            game.character.add_experience(20)
            game.character.flags["act1_protector"] = True
        return _fn

    # -------------------------
    # Nowe helpery dla fabuły leśnej
    # -------------------------
    
    def _fx_pay_silver(self, amount: int) -> EffectFn:
        """Płaci srebrem jeśli gracz ma wystarczająco."""
        def _fn(game: "Game"):
            ch = game.character
            if ch.silver >= amount:
                ch.silver -= amount
                print(f"  Płacisz {amount} SREBRA.")
            else:
                print(f"  Nie masz wystarczająco srebra!")
        return _fn

    def _fx_mglak_escape_roll(self, stat: str, success_msg: str, fail_msg: str) -> EffectFn:
        """Rzut na statystykę podczas ucieczki przed Mglakiem."""
        def _fn(game: "Game"):
            import random
            ch = game.character
            stat_val = getattr(ch, stat, 1)
            # Szansa = 30% + 15% za każdy punkt statystyki powyżej 1
            chance = 30 + (stat_val - 1) * 15
            roll = random.randint(1, 100)
            
            if roll <= chance:
                print(f"  ✓ {success_msg}")
                ch.add_experience(5)
            else:
                print(f"  ✗ {fail_msg}")
                ch.take_damage(1)
        return _fn

    def _fx_mglak_final_escape(self) -> EffectFn:
        """Ostatni segment ucieczki przed Mglakiem."""
        def _fn(game: "Game"):
            import random
            ch = game.character
            # Zawsze udaje się uciec, ale możesz oberwać
            roll = random.randint(1, 100)
            if roll <= 50:
                print("  Wypadasz z mgły na trakt! Udało się!")
                ch.add_experience(10)
            else:
                print("  Lodowate pazury drasnęły twoje plecy, ale UCIEKŁEŚ!")
                ch.take_damage(1)
                ch.add_experience(10)
        return _fn

    def _fx_werewolf_attack_roll(self, stat: str, success_msg: str, fail_msg: str) -> EffectFn:
        """Rzut na statystykę podczas walki z wilkołakiem."""
        def _fn(game: "Game"):
            import random
            ch = game.character
            stat_val = getattr(ch, stat, 1)
            chance = 30 + (stat_val - 1) * 20
            roll = random.randint(1, 100)
            
            if roll <= chance:
                print(f"  ✓ {success_msg}")
                ch.add_experience(10)
            else:
                print(f"  ✗ {fail_msg}")
                ch.take_damage(2)
        return _fn

    def _fx_werewolf_final_roll(self) -> EffectFn:
        """Ostatni segment walki z wilkołakiem."""
        def _fn(game: "Game"):
            import random
            ch = game.character
            roll = random.randint(1, 100)
            if roll <= 60:
                print("  Świt! Pierwsz promienie słońca przebijają przez drzewa!")
                print("  Bestia wyje i cofa się w las!")
                ch.add_experience(20)
            else:
                print("  Bestia trafia cię ostatni raz zanim nadchodzi świt!")
                ch.take_damage(2)
                ch.add_experience(15)
        return _fn

    # =============================================================================
    # Scenes
    # =============================================================================

    def _create_scenes(self) -> None:
        # PROLOG: 2 z 4 (blokada po 2 wybranych)
        self.scenes["prolog_instincts"] = Scene(
            scene_id="prolog_instincts",
            title="PROLOG — Wybór talentów startowych",
            narration=(
                "Zanim wraca ból, pojawia się jedyna jasna myśl:\n"
                "musisz przypomnieć sobie to, w czym byłeś najlepszy.\n\n"
                "Masz 2 PUNKTY STATYSTYK do rozdania.\n"
                "Możesz wybrać tę samą statystykę dwa razy lub dwie różne.\n"
                "Gdy rozdasz oba punkty — rozpoczniesz właściwą grę."
            ),
            objective="Rozdaj 2 punkty statystyk.",
            explore_mode=True,
            on_enter=self._on_enter_instincts,
            choices=[
                Choice("[O] SIŁA +1 — lepsze akcje siłowe", "prolog_instincts",
                       effects=[self._fx_pick_stat("strength")]),
                Choice("[O] ZRĘCZNOŚĆ +1 — lepsze skradanie i refleks", "prolog_instincts",
                       effects=[self._fx_pick_stat("dexterity")]),
                Choice("[O] INTELIGENCJA +1 — lepsza analiza i tropy", "prolog_instincts",
                       effects=[self._fx_pick_stat("intelligence")]),
                Choice("[O] WITALNOŚĆ +1 — większa wytrzymałość (+2 HP)", "prolog_instincts",
                       effects=[self._fx_pick_stat("vitality")]),
                Choice("[F] ✅ Zakończ wybór i rozpocznij grę", "prolog_wake_up",
                       requirements={"flag": ("picks_done", True)}),
            ],
        )

        # SCENA 1
        self.scenes["prolog_wake_up"] = Scene(
            scene_id="prolog_wake_up",
            title="1. Przebudzenie",
            narration=(
                "Ból wyrywa cię z ciemności.\n\n"
                "Oddychasz płytko - czujesz jakbyś miał złamane żebra. Każdy ruch pali jak ogień pod skórą.\n"
                "Leżysz na słomianym łożu w starej chacie. W kominku tli się ogień.\n\n"
                "Nie pamiętasz nic. Czujesz kompletny mętlik w głowie.\n"
                "Co wydarzyło się w mojej rodzinnej wiosce? Dlaczego tu jestem? - KIM JA JESTEM?\n\n"
                "Jesteś ciężko ranny. (ŻYCIE: 3 / maks.)\n\n"
                "Na stole leży sakiewka i zwinięty pergamin.\n"
                "Za oknem: noc."
            ),
            objective="Rozejrzyj się i ustal, gdzie jesteś oraz czy jesteś sam.",
            explore_mode=True,
            subscenes=["prolog_table", "prolog_bed", "prolog_window"],
            on_enter=self._on_enter_prolog_wake_up,
            exit_condition=self._exit_prolog_wake_up,
            choices=[
                Choice("[O] Podejdź do okna i wyjrzyj", "prolog_window",
                       one_time_id="look_window", effects=[self.fx_flag("visited_window", True)]),
                Choice("[O] Połóż się na słomianym łożu", "prolog_bed", one_time_id="lie_down"),
                Choice("[F] Podejdź do stołu", "prolog_table"),
                Choice("[O] Ogrzej się przy kominku (+1 ŻYCIA)", "prolog_wake_up",
                       one_time_id="fireplace_warmth", effects=[self.fx_add_hp(+1)]),
                Choice("[O] Sprawdź swoje rany", "prolog_wake_up",
                       requirements={"intelligence": 2}, one_time_id="examine_wounds",
                       effects=[self.fx_add_exp(10), self.fx_stat("intelligence", +0)]),
                Choice("[F] Nasłuchuj otoczenia", "prolog_wake_up",
                       requirements={"dexterity": 2}, one_time_id="listen_night",
                       effects=[self.fx_stat("dexterity", +0), self.fx_flag("heard_snoring", True)]),
            ],
        )

        self.scenes["prolog_window"] = Scene(
            scene_id="prolog_window",
            title="Podscena — Okno",
            narration=(
                "Podchodzisz do okna.\n\n"
                "Widzisz ciemny las. Drzewa ustawione są w rząd czarnych kolumn.\n"
                "W oddali majaczy łuna — jakby pożar już dawno wygasł, ale popiół jeszcze unosi się w powietrzu.\n\n"
                "Cisza jest nienaturalna. Odczuwasz strach.\n"
                "Nawet nocne ptaki wydają się milczeć."
            ),
            explore_mode=True,
            choices=[Choice("[F] Wróć do łóżka", "prolog_wake_up")],
        )

        self.scenes["prolog_table"] = Scene(
            scene_id="prolog_table",
            title="Podscena — Stół",
            narration="Drewniany stół jest porysowany i stary. Leży na nim sakiewka oraz pergamin.",
            objective="Możesz tu znaleźć drobne zasoby i jakiś kawałek papieru.",
            explore_mode=True,
            choices=[
                Choice("[O] Sprawdź sakiewkę", "prolog_table",
                       one_time_id="take_pouch",
                       effects=[self.fx_add_silver_rng(5, 15), self.fx_flag("table_interacted", True)]),
                Choice("[O] Przeczytaj pergamin", "prolog_table",
                       requirements={"intelligence": 2}, one_time_id="read_parchment",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_print(
                               "Nie wiem dlaczego próbowałeś ratować tego człowieka.\n\n"
                               "Doskonale wiem, że nie posiadasz wielu środków a przez niego zmarnujesz ich jeszcze więcej...\n"
                               "Ale nie mogę zostawić Ciebie samego w tej sytuacji... Masz to moje ostatnie oszczędności.\n\n"
                               "Jeśli po przebudzeniu ten ktoś wbije Ci nóż w plecy, nawet mnie to nie zdziwi.\n"
                               "Weź go chociaż zwiąż do tego łoża.\n"
                               "K."
                           ),
                           self.fx_flag("note_warning", True),
                           self.fx_flag("table_interacted", True)
                       ]),
                Choice("[F] Wróć", "prolog_wake_up"),
            ],
        )

        self.scenes["prolog_bed"] = Scene(
            scene_id="prolog_bed",
            title="Podscena — Łoże",
            narration=(
                "Próbujesz się uspokoić i zebrać chaotyczne myśli.\n\n"
                "Sen nie przychodzi.\n"
                "Nie możesz zasnąć.\n"
                "Ból trzyma cię przy życiu i przy świadomości."
            ),
            explore_mode=True,
            choices=[Choice("[F] Wróć", "prolog_wake_up")],
        )

        # SCENA 2
        self.scenes["prolog_old_man_intro"] = Scene(
            scene_id="prolog_old_man_intro",
            title="2. Ktoś tu jest",
            narration=(
                "Drzwi chaty skrzypią.\n\n"
                "— Spokojnie… — mówi ktoś łagodnym głosem.\n"
                "Wchodzi stary mężczyzna z lampą w prawej dłoni.\n\n"
                "— Obudziłeś się w końcu. Znalazłem cię przy spalonych ruinach."
            ),
            objective="Zdecyduj, czy mu ufasz i dowiedz się, co wie.",
            explore_mode=True,
            subscenes=["old_man_questions", "old_man_decision"],
            on_enter=self._on_enter_scene2_dynamic,
            choices=[
                Choice("„[O] Kim jesteś?”", "old_man_questions",
                       one_time_id="ask_who",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_print(
                               "— Jestem tylko starcem, którego zainteresował los młodego człowieka,\n"
                               "który ledwo dychał po starciu z tymi nędznymi orkami."
                           ),
                           self.fx_flag("visited_old_man_questions", True)
                       ]),
                Choice("„[O] Dlaczego mi pomogłeś?”", "old_man_questions",
                       one_time_id="ask_why_help",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_print(
                               "— Sam tego nie wiem. Nie potrafiłem przejść obok cudzego nieszczęścia obojętnie."
                           )
                       ]),
                Choice("[O] Milcz i obserwuj go uważnie", "old_man_questions",
                       requirements={"intelligence": 2}, one_time_id="observe_oldman",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_print(
                               "Starasz się przyjrzeć starszemu mężczyźnie.\n"
                               "Widzisz zmarszczki na jego czole. Ubrany jest w lekkie szaty.\n"
                               "Przy pasie ma alchemiczny przybornik.\n"
                               "Dostrzegasz też krucze ziele i mniszek — typowe do leczenia ran."
                           )
                       ]),
                Choice("[O] Cofnij się instynktownie", "old_man_questions",
                       requirements={"dexterity": 2}, one_time_id="step_back",
                       effects=[
                           self.fx_stat("dexterity", +1),
                           self.fx_add_hp(-1),
                           self.fx_print(
                               "Nieufnie cofasz się do tyłu pod ścianę — pomimo tego, że wiesz,\n"
                               "że i tak nic by to nie dało ze względu na twój stan zdrowia.\n"
                               "Staruszek patrząc na ciebie wydaje się zażenowany, ale również w pełni podziwu,\n"
                               "że pomimo rozległych ran starasz się zachować rozwagę."
                           )
                       ]),
                Choice("[F] Podejmij decyzję co zrobić dalej", "old_man_decision"),
            ],
        )

        self.scenes["old_man_questions"] = Scene(
            scene_id="old_man_questions",
            title="Podscena — Pytania",
            narration=(
                "Starzec mówi oszczędnie. Wydaje ci się, że nie do końca ci ufa.\n"
                "Nie daje ci to pewności, prawdopodobnie sam do końca nie wie dlaczego Ci pomógł"
            ),
            explore_mode=True,
            choices=[
                Choice("„[O] Co stało się z wioską w której mnie znalazłeś?”", "old_man_questions",
                       one_time_id="ask_village",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_print(
                               "— Wioska została doszczętnie zniszczona… wielu ludzi tam poległo.\n"
                               "Część z ładniejszych kobiet została porwana przez te cholerne orki."
                           ),
                           self.fx_flag("knows_orcs", True)
                       ]),
                Choice("„[O] Dlaczego nie zabili akurat mnie?”", "old_man_questions",
                       requirements={"intelligence": 2}, one_time_id="ask_survival",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_print(
                               "— Nie wiem dlaczego nie zginąłeś, jednakże prawdopodobnie sam Arros nad tobą czuwał."
                           ),
                           self.fx_flag("hint_survival", True)
                       ]),
                Choice("„[O] Jak długo już tu leżę?”", "old_man_questions",
                       one_time_id="ask_time",
                       effects=[
                           self.fx_add_exp(20),
                           self.fx_print(
                               "— Znalazłem cię 4 dni temu, od tamtej pory walczyłem z gorączką która pochłonęła twoje ciało…\n"
                               "Wywar z piekielników zdecydowanie złagodził objawy gorączki, a zioła lecznicze lekko poprawiły stan twoich ran."
                           )
                       ]),
                Choice("[F] Wróć", "prolog_old_man_intro"),
            ],
        )

        self.scenes["old_man_decision"] = Scene(
            scene_id="old_man_decision",
            title="Podscena — Decyzja",
            narration=(
                "— Dzień będzie za niedługo świtał. Jeśli zostaniesz, złapiesz oddech, a ja w tym czasie cię opatrzę.\n"
                "Jeśli odejdziesz… las może nie być dla ciebie łaskawy w tym stanie.\n\n"
                "— Decyzja jednak należy tylko do ciebie."
            ),
            explore_mode=True,
            choices=[
                Choice(
                    "[F] Zostanę tu jeszcze chwilę, jednak nie chciałbym Panu przeszkadzać...",
                    "act1_dawn_safe",
                    one_time_id="stay_choice",
                    effects=[
                        self.fx_flag("stayed_with_old_man", True),
                        self.fx_print(
                            "— Spokojnie, nie przeszkadzasz…\n"
                            "Właściwie to cieszę się, że w końcu się obudziłeś…\n"
                            "Powoli zaczynałem tracić nadzieję, że jeszcze otworzysz oczy."
                        ),
                    ],
                ),
                Choice(
                    "[F] Muszę iść dalej, muszę odnaleźć wspomnienia które utraciłem...",
                    "act1_dawn_departure",
                    one_time_id="leave_choice",
                    effects=[
                        self.fx_flag("left_early", True),
                        self.fx_print(
                            "— Rób jak uważasz jednakże twoje rany mogą doprowadzić Cię do śmierci…\n"
                            "Daj mi chociaż zmienić Ci bandaże na nowe."
                        ),
                        self.fx_add_hp(+1),
                    ],
                ),
            ],
        )

        # SCENA 3A
        self.scenes["act1_dawn_safe"] = Scene(
            scene_id="act1_dawn_safe",
            title="3. Świt nad popiołem",
            narration=(
                "Świt przychodzi powoli. Starzec wymienił stare bandaże na nowe oraz obmył moje rany.\n"
                "W chacie pachnie ziołami i dymem. Starzec podaje ci czarny, gorzki wywar.\n"
                "— To pomoże. Chociaż trochę.\n"
                "Ale najpierw musisz to wypić."
            ),
            objective="Zbierz siły i rusz na trakt.",
            explore_mode=True,
            subscenes=["old_man_directions"],
            choices=[
                Choice(
                    "[O] Wypij wywar (+3 ŻYCIA)",
                    "act1_dawn_safe",
                    one_time_id="drink_brew",
                    effects=[
                        self.fx_add_hp(3),
                        self.fx_add_exp(10),
                        self.fx_print(
                            "Ugh… śmierdzi obrzydliwie i smakuje jeszcze gorzej…\n"
                            "Ale czujesz, że rozgrzewający wywar zaczyna oddziaływać pozytywnie na twój organizm."
                        ),
                    ],
                ),
                Choice(
                    "[O] Zapytaj dokąd iść dalej",
                    "old_man_directions",
                    one_time_id="ask_directions",
                    effects=[
                        self.fx_add_exp(10),
                        self.fx_print(
                            "— Czy mógłbyś powiedzieć mi dokąd mogę dojść po wyjściu z twojej chaty?\n"
                            "— Trakt biegnie na wschód, staraj się unikać ciszy i pod żadnym pozorem nie podchodź\n"
                            "do porzuconych wozów lub ludzi wołających o pomoc."
                        ),
                    ],
                ),
                Choice(
                    "[O] Pomóż przygotować chatę",
                    "act1_dawn_safe",
                    requirements={"strength": 2},
                    one_time_id="help_cabin",
                    effects=[
                        self.fx_add_exp(20),
                        self.fx_stat("strength", +1),
                        self.fx_print(
                            "— W takim razie w ramach tego co dla mnie zrobiłeś, pozwól mi proszę chociaż\n"
                            "posprzątać po sobie... Wiem, że to niewiele ale chciałbym chociaż w taki sposób okazać Ci swoją wdzięczność."
                        ),
                    ],
                ),
                Choice(
                    "[F] Wyrusz na trakt",
                    "act1_forest_road",
                    effects=[
                        self.fx_print(
                            "— Dziękuję Ci za pomoc, jednakże muszę wyruszać aby powrócić do rodzinnej wioski...\n"
                            "Myślę że tam mogę dowiedzieć się czegoś więcej o moich wspomnieniach.\n"
                            "— Żegnaj przyjacielu, pamiętaj, że zawsze będziesz u mnie mile widziany."
                        ),
                    ],
                ),
            ],
        )

        self.scenes["old_man_directions"] = Scene(
            scene_id="old_man_directions",
            title="Podscena — Wskazówki starca",
            narration=(
                "Starzec kreśli palcem w popiele na stole.\n\n"
                "— Trakt biegnie na wschód. Jeśli chcesz przeżyć, trzymaj się go,\n"
                "ale staraj się nie ufać ciszy. W tym lesie obudziło się coś prastarego...\n"
                "Wyczuwam tą siłę nawet z tego miejsca.\n\n"
                "— W okolicy kręcą się szajki bandytów i to coś złowrogiego...\n"
                "Możliwe, że to pewnego rodzaju klątwa...\n\n"
                "— Jeśli zobaczysz porzucone wozy, nie dotykaj ich jeśli nie musisz.\n"
                "POD ŻADNYM POZOREM NIE ZBLIŻAJ SIĘ DO LUDZI KTÓRZY MOGLIBY WOŁAĆ O POMOC!\n"
                "To bardzo niebezpieczne... Ja sprawdziłem praktycznie całą drogę\n"
                "i nie znalazłem nikogo żywego poza tobą...\n\n"
                "Starzec patrzy ci prosto w oczy.\n\n"
                "— Jeśli poczujesz się zagrożony, pojawi się ta grobowa cisza\n"
                "i poczujesz lodowatą obecność... UCIEKAJ.\n"
                "On już rozpoczął swoje łowy...\n\n"
                "Dlatego lepiej powinieneś tu zostać."
            ),
            explore_mode=True,
            choices=[
                Choice("[O] Wróć", "act1_dawn_safe",
                       effects=[self.fx_flag("warned_by_old_man", True)]),
            ],
        )

        # SCENA 3B
        self.scenes["act1_dawn_departure"] = Scene(
            scene_id="act1_dawn_departure",
            title="3. Świt nad popiołem",
            narration=(
                "Wychodzisz przed świtem.\n"
                "Las połyka cię natychmiast.\n"
                "Jesteś sam."
            ),
            objective="Dotrzyj do traktu, nie tracąc resztek sił.",
            explore_mode=True,
            choices=[
                Choice("[O] Ruszaj ostrożnie (-1 ŻYCIA)", "act1_dawn_departure",
                       one_time_id="depart_careful", effects=[self.fx_add_hp(-1), self.fx_add_exp(5)]),
                Choice("[O] Ukryj się i obserwuj", "act1_dawn_departure",
                       requirements={"dexterity": 2}, one_time_id="hide_observe",
                       effects=[self.fx_add_exp(5), self.fx_stat("dexterity", +1)]),
                Choice("[O] Uspokój oddech", "act1_dawn_departure",
                       requirements={"intelligence": 2}, one_time_id="calm_breath",
                       effects=[self.fx_add_exp(5), self.fx_add_hp(+1)]),
                Choice("[F] Dotrzyj do traktu", "act1_forest_road"),
            ],
        )

        # =============================================================================
        # AKT I - NOWA FABUŁA LEŚNA
        # =============================================================================

        # SCENA 4 - Początek wędrówki przez las
        self.scenes["act1_forest_road"] = Scene(
            scene_id="act1_forest_road",
            title="4. Trakt przez las",
            narration=(
                "Opuszczasz chatę starca i ruszasz na wschód, zgodnie z jego wskazówkami.\n\n"
                "Las otacza cię ze wszystkich stron. Wysokie dęby i sosny tworzą gęsty baldachim,\n"
                "przez który z trudem przebijają się promienie słońca. Pod stopami chrzęszczą\n"
                "suche liście i połamane gałązki.\n\n"
                "Między drzewami dostrzegasz resztki zniszczonych wozów - ich drewno jest poczerniałe,\n"
                "jakby ktoś próbował je spalić. W powietrzu unosi się lekki zapach dymu i czegoś...\n"
                "słodkawego. Niepokojącego.\n\n"
                "Idziesz już jakiś czas, gdy nagle słyszysz coś w oddali..."
            ),
            objective="Podążaj traktem na wschód i bądź czujny.",
            explore_mode=True,
            choices=[
                Choice("[O] Rozejrzyj się uważnie po okolicy", "act1_forest_road",
                       one_time_id="forest_look_around",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_print(
                               "Przystajesz i rozglądasz się. Las wydaje się martwy - nie słychać ptaków,\n"
                               "nie widać zwierząt. Tylko cisza i odległy szum wiatru w koronach drzew.\n"
                               "Dostrzegasz ślady na ziemi - coś dużego przechodziło tędy niedawno."
                           )
                       ]),
                Choice("[O] Zbadaj zniszczony wóz przy trakcie", "act1_forest_road",
                       one_time_id="forest_check_wagon",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_add_item("bandage"),
                           self.fx_print(
                               "Podchodzisz ostrożnie do wraku wozu. Wśród szczątków znajdujesz\n"
                               "kawałek czystego płótna - przyda się jako prowizoryczny bandaż.\n"
                               "Na drewnie widać ślady pazurów... i coś co wygląda jak ludzkie zadrapania.\n"
                               "Ktoś desperacko próbował się wydostać."
                           )
                       ]),
                Choice("[F] Idź dalej traktem", "act1_forest_voices",
                       effects=[self.fx_add_exp(5)]),
            ],
        )

        # SCENA 5 - Głosy w lesie
        self.scenes["act1_forest_voices"] = Scene(
            scene_id="act1_forest_voices",
            title="5. Głosy w lesie",
            narration=(
                "Idziesz dalej, gdy nagle słyszysz to wyraźnie...\n\n"
                "— POMOCY! PROSZĘ, NIECH KTOŚ MI POMOŻE!\n\n"
                "To głos kobiety, dochodzący gdzieś z głębi lasu, na lewo od traktu.\n"
                "Brzmi rozpaczliwie, pełen strachu i bólu.\n\n"
                "— BŁAGAM! JESTEM RANNA! NIE MOGĘ SIĘ RUSZYĆ!\n\n"
                "Słowa starca wracają do ciebie: 'POD ŻADNYM POZOREM NIE ZBLIŻAJ SIĘ\n"
                "DO LUDZI KTÓRZY MOGLIBY WOŁAĆ O POMOC'..."
            ),
            objective="Zdecyduj, czy zareagujesz na wołanie.",
            explore_mode=True,
            on_enter=self._on_enter_forest_voices,
            choices=[
                Choice("[F] Zlekceważ głosy i idź dalej", "act1_bandit_camp",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_flag("ignored_voices", True),
                           self.fx_print(
                               "Zaciskasz zęby i zmuszasz się do ignorowania wołania.\n"
                               "Starzec ostrzegał cię... Musisz mu zaufać.\n"
                               "Idziesz dalej, a głosy powoli cichną za tobą."
                           )
                       ]),
                Choice("[O] Nasłuchuj uważnie dźwięków", "act1_forest_voices",
                       requirements={"intelligence": 3},
                       one_time_id="listen_voices",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_flag("listened_carefully", True),
                           self.fx_print(
                               "Zamykasz oczy i nasłuchujesz...\n"
                               "Coś jest nie tak. Głos jest... zbyt perfekcyjny. Zbyt czysty.\n"
                               "I powtarza się w dokładnie tych samych odstępach czasu.\n"
                               "To nie jest człowiek. To coś, co NAŚLADUJE człowieka."
                           )
                       ]),
                Choice("[F] Sprawdź co się dzieje", "mglak_trap_enter",
                       effects=[
                           self.fx_flag("went_to_voices", True),
                           self.fx_print(
                               "Nie możesz zostawić kogoś w potrzebie...\n"
                               "Schodzisz z traktu i zagłębiasz się w las."
                           )
                       ]),
            ],
        )

        # SCENA - Pułapka Mglaka (wejście)
        self.scenes["mglak_trap_enter"] = Scene(
            scene_id="mglak_trap_enter",
            title="Pułapka",
            narration="",
            objective="Przetrwaj!",
            explore_mode=False,
            on_enter=self._on_enter_mglak_trap,
            choices=[
                Choice("[F] Uciekaj natychmiast!", "mglak_escape_1",
                       effects=[self.fx_add_exp(5)]),
            ],
        )

        # SCENA - Ucieczka przed Mglakiem (1)
        self.scenes["mglak_escape_1"] = Scene(
            scene_id="mglak_escape_1",
            title="Ucieczka — Segment 1",
            narration=(
                "Biegniesz ile sił w nogach! Mgła gęstnieje wokół ciebie.\n\n"
                "Za sobą słyszysz... syczenie? Charczenie? Coś się zbliża!\n\n"
                "Przed tobą rozwidlenie - możesz skoczyć przez przewrócony pień\n"
                "albo przebiec przez gęste zarośla!"
            ),
            objective="Wybierz drogę ucieczki!",
            explore_mode=False,
            choices=[
                Choice("[F] Przeskocz przez pień!", "mglak_escape_2",
                       effects=[self._fx_mglak_escape_roll("dexterity", "Udało się! Przeskakujesz zgrabnie.", "Potykasz się! Coś drasnęło twoje plecy!")]),
                Choice("[F] Przebiegnij przez zarośla!", "mglak_escape_2",
                       effects=[self._fx_mglak_escape_roll("strength", "Przedzierasz się przez chaszcze!", "Kolce rozdzierają ci skórę!")]),
            ],
        )

        # SCENA - Ucieczka przed Mglakiem (2)
        self.scenes["mglak_escape_2"] = Scene(
            scene_id="mglak_escape_2",
            title="Ucieczka — Segment 2",
            narration=(
                "Nie zwalniasz! Serce wali ci jak oszalałe!\n\n"
                "Mgła jest wszędzie - ledwo widzisz na metr przed siebie.\n"
                "Ale... czy tam jest światło? Tak! Widzisz przebłyski słońca!\n\n"
                "Tylko czy to prawdziwa droga, czy kolejna pułapka?\n"
                "Z drugiej strony słyszysz szum wody - może strumień?"
            ),
            objective="Wybierz drogę!",
            explore_mode=False,
            choices=[
                Choice("[F] Biegnij w stronę światła!", "mglak_escape_3",
                       effects=[self._fx_mglak_escape_roll("intelligence", "Intuicja cię nie zawiodła!", "To była iluzja! Tracisz orientację!")]),
                Choice("[F] Biegnij do strumienia!", "mglak_escape_3",
                       effects=[self._fx_mglak_escape_roll("vitality", "Woda spowalnia istotę!", "Zimna woda szokuje twoje ciało!")]),
            ],
        )

        # SCENA - Ucieczka przed Mglakiem (3)
        self.scenes["mglak_escape_3"] = Scene(
            scene_id="mglak_escape_3",
            title="Ucieczka — Segment 3",
            narration=(
                "Jeszcze trochę! Mgła zaczyna rzednąć!\n\n"
                "Widzisz trakt! Jesteś prawie na miejscu!\n"
                "Ale istota jest tuż za tobą - czujesz lodowaty oddech na karku!\n\n"
                "Ostatni zryw!"
            ),
            objective="Ostatnia szansa!",
            explore_mode=False,
            choices=[
                Choice("[F] Rzuć się do przodu z całych sił!", "mglak_escape_end",
                       effects=[self._fx_mglak_final_escape()]),
            ],
        )

        # SCENA - Koniec ucieczki przed Mglakiem
        self.scenes["mglak_escape_end"] = Scene(
            scene_id="mglak_escape_end",
            title="Koniec ucieczki",
            narration="",
            objective="Odetchnij...",
            explore_mode=True,
            on_enter=self._on_enter_mglak_escape_end,
            choices=[
                Choice("[F] Idź dalej, nie oglądając się za siebie", "act1_bandit_camp",
                       effects=[
                           self.fx_flag("escaped_mglak", True),
                           self.fx_add_exp(15)
                       ]),
            ],
        )

        # SCENA 6 - Opuszczony obóz bandytów
        self.scenes["act1_bandit_camp"] = Scene(
            scene_id="act1_bandit_camp",
            title="6. Opuszczony obóz",
            narration=(
                "Po dłuższym marszu dostrzegasz coś między drzewami.\n\n"
                "To pozostałości obozu - wygasłe ognisko, porzucone namioty,\n"
                "porozrzucane przedmioty. Wszystko wskazuje na to, że ludzie\n"
                "opuścili to miejsce w wielkim pośpiechu.\n\n"
                "Na ziemi leżą resztki jedzenia, butelki, a także...\n"
                "Czy to broń? Ktoś zostawił tutaj sporo rzeczy."
            ),
            objective="Przeszukaj obóz lub idź dalej.",
            explore_mode=True,
            choices=[
                Choice("[O] Przeszukaj namioty", "act1_bandit_camp",
                       one_time_id="search_tents",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_add_silver(8),
                           self.fx_print(
                               "W namiotach znajdujesz trochę srebra i prowiantu.\n"
                               "Bandyci musieli bardzo się spieszyć, skoro to zostawili."
                           )
                       ]),
                Choice("[O] Podkradnij się do skrzyni przy ognisku", "act1_bandit_camp",
                       requirements={"dexterity": 3},
                       one_time_id="steal_silver_knife",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_add_item("silver_knife"),
                           self.fx_print(
                               "Twoja zręczność pozwala ci cicho otworzyć skrzynię.\n"
                               "W środku znajdujesz SREBRNY NÓŻ! Pięknie zdobiony,\n"
                               "z symbolami których nie rozpoznajesz. Może się przydać..."
                           )
                       ]),
                Choice("[O] Zbierz pozostałe jedzenie (+2 HP)", "act1_bandit_camp",
                       one_time_id="camp_food",
                       effects=[
                           self.fx_add_hp(2),
                           self.fx_add_exp(5),
                           self.fx_print(
                               "Znajdujesz trochę suszonego mięsa i chleba.\n"
                               "Nie jest świeże, ale jedzenie to jedzenie."
                           )
                       ]),
                Choice("[F] Opuść obóz i idź dalej", "act1_healing_spot",
                       effects=[self.fx_add_exp(5)]),
            ],
        )

        # SCENA 7 - Miejsce odpoczynku (jagody/zioła)
        self.scenes["act1_healing_spot"] = Scene(
            scene_id="act1_healing_spot",
            title="7. Polana przy strumieniu",
            narration=(
                "Trakt prowadzi cię do małej polany przy strumieniu.\n\n"
                "To dobre miejsce na krótki odpoczynek. Strumień jest czysty,\n"
                "a na brzegu rosną jakieś krzewy z ciemnymi jagodami.\n"
                "Widzisz też żółte kwiaty - wyglądają na lecznicze zioła."
            ),
            objective="Odpręż się i uzupełnij siły.",
            explore_mode=True,
            choices=[
                Choice("[O] Zjedz jagody z krzaków (+2 HP)", "act1_healing_spot",
                       one_time_id="eat_berries",
                       effects=[
                           self.fx_add_hp(2),
                           self.fx_add_exp(5),
                           self.fx_print(
                               "Jagody są słodkie i soczyste. Czujesz, jak energia\n"
                               "wraca do twojego zmęczonego ciała."
                           )
                       ]),
                Choice("[O] Użyj ziół do opatrzenia ran (+3 HP)", "act1_healing_spot",
                       requirements={"intelligence": 3},
                       one_time_id="use_herbs",
                       effects=[
                           self.fx_add_hp(3),
                           self.fx_add_exp(10),
                           self.fx_print(
                               "Twoja wiedza pozwala ci rozpoznać lecznicze właściwości ziół.\n"
                               "Przygotowujesz prowizoryczny okład, który łagodzi ból ran."
                           )
                       ]),
                Choice("[O] Napij się wody ze strumienia (+1 HP)", "act1_healing_spot",
                       one_time_id="drink_water",
                       effects=[
                           self.fx_add_hp(1),
                           self.fx_add_exp(5),
                           self.fx_print(
                               "Zimna, czysta woda orzeźwia cię. Czujesz się trochę lepiej."
                           )
                       ]),
                Choice("[F] Ruszaj dalej", "act1_bandits_wagon",
                       effects=[self.fx_add_exp(5)]),
            ],
        )

        # SCENA 8 - Bandyci przy wozie
        self.scenes["act1_bandits_wagon"] = Scene(
            scene_id="act1_bandits_wagon",
            title="8. Spotkanie na trakcie",
            narration=(
                "Idąc dalej, słyszysz głosy. Tym razem to prawdziwe głosy - męskie, szorstkie.\n\n"
                "Za zakrętem widzisz dwóch mężczyzn grzebiących w zniszczonym wozie.\n"
                "Są uzbrojeni - jeden ma miecz, drugi topór. Na ich twarzach widać blizny.\n\n"
                "— Hej, patrz! Mamy gościa! — jeden z nich cię zauważył.\n\n"
                "Drugi odwraca się i mierzy cię wzrokiem.\n"
                "— No no... Samotny wędrowiec. Co tutaj robisz, przyjacielu?"
            ),
            objective="Zdecyduj, jak rozegrać to spotkanie.",
            explore_mode=True,
            choices=[
                Choice("[O] „Tylko przechodzę. Nie chcę kłopotów.", "act1_bandits_talk",
                       one_time_id="bandits_peaceful",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_print(
                               "— Kłopotów? My też nie chcemy kłopotów... — mówi pierwszy,\n"
                               "ale w jego głosie słychać sarkazm."
                           )
                       ]),
                Choice("[O] Obserwuj ich uważnie, nie odpowiadaj", "act1_bandits_talk",
                       requirements={"intelligence": 2},
                       one_time_id="bandits_observe",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_flag("observed_bandits", True),
                           self.fx_print(
                               "Nie odpowiadasz. Obserwujesz ich ruchy.\n"
                               "Pierwszy jest nerwowy - ciągle zerka w las.\n"
                               "Drugi jest spokojniejszy, ale trzyma rękę na mieczu.\n"
                               "Coś ich niepokoi..."
                           )
                       ]),
                Choice("[F] Spróbuj ich wyminąć i uciec", "act1_bandits_flee",
                       requirements={"dexterity": 3},
                       effects=[
                           self.fx_add_exp(15),
                           self.fx_print(
                               "Wykorzystujesz moment nieuwagi i rzucasz się do ucieczki!\n"
                               "Słyszysz za sobą przekleństwa, ale nikt cię nie goni.\n"
                               "Widocznie mają ważniejsze sprawy..."
                           )
                       ]),
            ],
        )

        # SCENA - Rozmowa z bandytami
        self.scenes["act1_bandits_talk"] = Scene(
            scene_id="act1_bandits_talk",
            title="Rozmowa z bandytami",
            narration=(
                "Bandyci podchodzą bliżej. Nie wyglądają na przyjaźnie nastawionych,\n"
                "ale też nie atakują od razu.\n\n"
                "— Widzisz, przyjacielu — zaczyna ten z mieczem — mamy tu mały problem.\n"
                "Obóz musieliśmy porzucić, bo... coś tam chodziło po nocy.\n"
                "A teraz szukamy czegokolwiek wartościowego.\n\n"
                "— Może masz coś dla nas? — pyta drugi, kręcąc toporem."
            ),
            objective="Zdecyduj, co zrobisz.",
            explore_mode=True,
            on_enter=self._on_enter_forest_voices,
            choices=[
                Choice("[F] Daj im trochę srebra (płacisz 5 SREBRA)", "act1_bandits_flee",
                       requirements={"flag": ("has_silver_5", True)},
                       one_time_id="pay_bandits",
                       effects=[
                           self._fx_pay_silver(5),
                           self.fx_add_exp(5),
                           self.fx_print(
                               "Wrzucasz im kilka monet. Pierwszy łapie je w locie.\n"
                               "— Mądry człowiek. Idź sobie.\n"
                               "Odchodzą, nie oglądając się za siebie."
                           )
                       ]),
                Choice("[F] Powiedz im o istocie w lesie", "act1_bandits_flee",
                       requirements={"flag": ("escaped_mglak", True)},
                       one_time_id="warn_bandits",
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_print(
                               "— Jeśli chcecie rady... uciekajcie z tego lasu.\n"
                               "Jest tu coś... we mgle. Ledwo uszedłem z życiem.\n\n"
                               "Ich twarze bledną. Wymieniają spojrzenia.\n"
                               "— Mglak... — szepcze jeden. — Cholera. Idziemy stąd.\n"
                               "Odchodzą szybkim krokiem, nie patrząc na ciebie."
                           )
                       ]),
                Choice("[F] Zaatakuj ich z zaskoczenia!", "act1_bandits_fight",
                       requirements={"strength": 3},
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_flag("fought_bandits", True)
                       ]),
                Choice("[F] Uciekaj!", "act1_bandits_flee",
                       effects=[
                           self.fx_add_hp(-1),
                           self.fx_add_exp(5),
                           self.fx_print(
                               "Rzucasz się do ucieczki! Jeden z nich próbuje cię złapać,\n"
                               "drapiąc twoje ramię, ale udaje ci się wyrwać!"
                           )
                       ]),
            ],
        )

        # SCENA - Walka z bandytami
        self.scenes["act1_bandits_fight"] = Scene(
            scene_id="act1_bandits_fight",
            title="Walka z bandytami",
            narration=(
                "Rzucasz się na nich z całych sił!\n\n"
                "Udaje ci się zaskoczyć pierwszego - twój cios trafia go w szczękę\n"
                "i pada na ziemię. Drugi zamachuje się toporem, ale jest za wolny!\n\n"
                "Wykorzystujesz moment i uderzasz go w brzuch. Zgina się w pół.\n"
                "— Dość! Dość! — krzyczy pierwszy, leżąc na ziemi.\n"
                "— Bierz co chcesz, tylko nas nie zabijaj!"
            ),
            objective="Zdecyduj, co zrobisz z pokonanymi.",
            explore_mode=True,
            choices=[
                Choice("[O] Zabierz ich sakiewki", "act1_bandits_flee",
                       one_time_id="loot_bandits",
                       effects=[
                           self.fx_add_silver(15),
                           self.fx_add_exp(10),
                           self.fx_print(
                               "Zabierasz ich pieniądze. Nie próbują się sprzeciwiać."
                           )
                       ]),
                Choice("[F] Zostaw ich i odejdź", "act1_bandits_flee",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_print(
                               "— Macie szczęście, że nie jestem mordercą.\n"
                               "Odchodzisz, zostawiając ich na ziemi."
                           )
                       ]),
            ],
        )

        # SCENA - Po bandytach
        self.scenes["act1_bandits_flee"] = Scene(
            scene_id="act1_bandits_flee",
            title="Po spotkaniu",
            narration=(
                "Zostawiasz bandytów za sobą i idziesz dalej.\n\n"
                "Słońce powoli zaczyna zachodzić. Musisz znaleźć miejsce na nocleg,\n"
                "zanim zrobi się całkowicie ciemno. W tym lesie nie chcesz\n"
                "być złapany przez noc bez ognia..."
            ),
            objective="Znajdź miejsce na obóz.",
            explore_mode=True,
            choices=[
                Choice("[F] Szukaj miejsca na obóz", "act1_night_camp",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_print(
                               "Znajdujesz niewielką polanę osłoniętą skałami.\n"
                               "To dobre miejsce - łatwo się bronić i można rozpalić ogień."
                           )
                       ]),
            ],
        )

        # SCENA 9 - Nocny obóz
        self.scenes["act1_night_camp"] = Scene(
            scene_id="act1_night_camp",
            title="9. Nocny obóz",
            narration=(
                "Rozpalasz ognisko. Płomienie tańczą, rzucając cienie na okoliczne drzewa.\n\n"
                "Noc jest cicha. Zbyt cicha. Nawet wiatr ucichł.\n\n"
                "Siadasz przy ogniu, wpatrując się w ciemność między drzewami.\n"
                "Musisz przetrwać do świtu. To nie powinno być trudne...\n\n"
                "Mijają godziny. Zmęczenie daje o sobie znać.\n"
                "Oczy same ci się zamykają...\n\n"
                "Słyszysz jak coś wolnym krokiem zbliża się do Ciebie z oddali."
            ),
            objective="Przetrwaj noc.",
            explore_mode=True,
            choices=[
                Choice("[O] Dorzuć drewna do ognia", "act1_night_camp",
                       one_time_id="add_wood",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_flag("fire_strong", True),
                           self.fx_print(
                               "Dorzucasz więcej gałęzi. Ogień bucha jasnym płomieniem.\n"
                               "W oddali zaczynasz słyszeć warczenie."
                           )
                       ]),
                Choice("[O] Przygotuj pochodnię", "act1_night_camp",
                       one_time_id="make_torch",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_flag("has_torch", True),
                           self.fx_print(
                               "Z gałęzi i kawałka tkaniny robisz prowizoryczną pochodnię.\n"
                               "Ona na pewno pozwoli mi rozświetlić chociaż trochę tej przeklętej ciemności"
                               "Pozwoli mi też na uderzenie potencjalnego celu.\n"
                           )
                       ]),
                Choice("[F] Czekaj i obserwuj ciemność", "act1_werewolf_appears",
                       effects=[self.fx_add_exp(10)]),
            ],
        )

        # SCENA 10 - Wilkołak się pojawia
        self.scenes["act1_werewolf_appears"] = Scene(
            scene_id="act1_werewolf_appears",
            title="10. Bestia z ciemności",
            narration=(
                "Widzisz TO.\n\n"
                "Z ciemności wyłania się masywna sylwetka. Stoi na dwóch nogach,\n"
                "ale jej kształt nie jest ludzki. Pokryte futrem ciało, wydłużony pysk,\n"
                "żółte oczy błyszczące w świetle ognia...\n\n"
                "WILKOŁAK.\n\n"
                "Bestia warczy, obnażając kły. Zbliża się powoli, ale ogień\n"
                "trzyma ją na dystans. Widać, że się go boi.\n\n"
                "Ale jest też głodna. I zdesperowana."
            ),
            objective="Przetrwaj do świtu!",
            explore_mode=False,
            on_enter=self._on_enter_werewolf,
            choices=[
                Choice("[F] Pomachaj pochodnią!", "werewolf_fight_1",
                       requirements={"flag": ("has_torch", True)},
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_flag("used_torch", True),
                           self.fx_print(
                               "Chwytasz pochodnię i wymachujesz nią przed sobą!\n"
                               "Bestia cofa się, sycząc z wściekłości!"
                           )
                       ]),
                Choice("[F] Rzuć w niego płonącą gałąź!", "werewolf_fight_1",
                       requirements={"flag": ("fire_strong", True)},
                       effects=[
                           self.fx_add_exp(10),
                           self.fx_print(
                               "Chwytasz płonącą gałąź z ogniska i rzucasz w bestię!\n"
                               "Trafiona, wyje z bólu i cofa się na moment!"
                           )
                       ]),
                Choice("[F] Użyj srebrnego noża!", "werewolf_fight_silver",
                       requirements={"has_item": "silver_knife"},
                       effects=[
                           self.fx_add_exp(15),
                           self.fx_flag("used_silver_knife", True)
                       ]),
                Choice("[F] Stój nieruchomo i nie prowokuj!", "werewolf_fight_1",
                       effects=[
                           self.fx_add_exp(5),
                           self.fx_print(
                               "Stoisz nieruchomo, nie spuszczając wzroku z bestii.\n"
                               "Wilkołak kręci się niespokojnie, ale nie atakuje... jeszcze."
                           )
                       ]),
            ],
        )

        # SCENA - Walka z wilkołakiem (ze srebrnym nożem)
        self.scenes["werewolf_fight_silver"] = Scene(
            scene_id="werewolf_fight_silver",
            title="Srebrne ostrze",
            narration=(
                "Wyciągasz srebrny nóż. W świetle ognia błyszczy on dziwnym blaskiem.\n\n"
                "Bestia SYCZY na widok srebra. Cofa się, ale nadal warczy.\n\n"
                "Gdy rzuca się na ciebie, zamachasz nożem!\n"
                "Ostrze przecina jej ramię - bestia WYJE z bólu!\n\n"
                "Krew - ciemna, prawie czarna - spływa po jej futrze.\n"
                "Wilkołak cofa się, trzymając ranę. Patrzy na ciebie z nienawiścią...\n"
                "I znika w ciemności."
            ),
            objective="Przetrwałeś!",
            explore_mode=True,
            choices=[
                Choice("[F] Czekaj do świtu", "act1_dawn_ending",
                       effects=[
                           self.fx_flag("wounded_werewolf", True),
                           self.fx_add_exp(20)
                       ]),
            ],
        )

        # SCENA - Walka z wilkołakiem (1)
        self.scenes["werewolf_fight_1"] = Scene(
            scene_id="werewolf_fight_1",
            title="Starcie z bestią",
            narration=(
                "Bestia nie ustępuje! Krąży wokół ogniska, szukając okazji do ataku.\n\n"
                "Nagle rzuca się! Musisz zareagować!"
            ),
            objective="Broń się!",
            explore_mode=False,
            choices=[
                Choice("[F] Odskocz w bok!", "werewolf_fight_2",
                       effects=[self._fx_werewolf_attack_roll("dexterity", "Unikasz pazurów!", "Pazury rozdzierają ci ramię!")]),
                Choice("[F] Zasłoń się rękami!", "werewolf_fight_2",
                       effects=[self._fx_werewolf_attack_roll("vitality", "Blokujesz atak!", "Ból jest nie do zniesienia!")]),
                Choice("[F] Kopnij ją w pysk!", "werewolf_fight_2",
                       effects=[self._fx_werewolf_attack_roll("strength", "Trafiony! Bestia się zatacza!", "Chybiasz i tracisz równowagę!")]),
            ],
        )

        # SCENA - Walka z wilkołakiem (2)
        self.scenes["werewolf_fight_2"] = Scene(
            scene_id="werewolf_fight_2",
            title="Walka trwa",
            narration=(
                "Bestia jest wściekła! Atakuje ponownie!\n\n"
                "Ale... czy niebo się rozjaśnia? Czy to świt?"
            ),
            objective="Jeszcze chwila!",
            explore_mode=False,
            choices=[
                Choice("[F] Unikaj i czekaj na świt!", "act1_dawn_ending",
                       effects=[self._fx_werewolf_final_roll()]),
            ],
        )

        # SCENA - Zakończenie Aktu I
        self.scenes["act1_dawn_ending"] = Scene(
            scene_id="act1_dawn_ending",
            title="Świt",
            narration="",
            objective="Koniec Aktu I.",
            explore_mode=True,
            on_enter=self._on_enter_dawn_ending,
            choices=[
                Choice("[F] Zakończ Akt I", "act2_start",
                       effects=[self.fx_flag("act1_completed", True)]),
            ],
        )

        # SCENA - Akt II placeholder
        self.scenes["act2_start"] = Scene(
            scene_id="act2_start",
            title="Akt II — (placeholder)",
            narration=(
                "To koniec pierwszego aktu gry THALANOR: ZATOPIONE KRONIKI.\n\n"
                "Dziękujemy za grę!\n"
                "Dalszy rozwój fabuły jest w trakcie tworzenia."
                "Planujemy wprowadzić tą grę na silnik PyEngine uwzględniając kwestie UI oraz dźwięku.\n\n"
            ),
            objective="Koniec wersji Demonstracyjnej.",
            choices=[Choice("[F] Zakończ grę", None, effects=[self.fx_flag("act1_completed", True)])],
        )

    # =============================================================================
    # Hooks / dynamic
    # =============================================================================

        # Autor hooków: A.N
    def _on_enter_instincts(self, game: "Game") -> None:
        ch = game.character
        # Licznik rozdanych punktów
        picks_count = ch.flags.get("stat_picks_count", 0)
        ch.flags["picks_done"] = (picks_count >= 2)
        
        # Blokuj wybory statystyk po rozdaniu 2 punktów
        stat_choices = ["SIŁA", "ZRĘCZNOŚĆ", "INTELIGENCJA", "WITALNOŚĆ"]
        for c in self.scenes["prolog_instincts"].choices:
            for stat_name in stat_choices:
                if stat_name in c.text and "[O]" in c.text:
                    if picks_count >= 2:
                        c.requirements = {"flag": ("picks_done", False)}
                    else:
                        c.requirements = {}
                    break
    
    def _fx_pick_stat(self, stat: str) -> EffectFn:
        """Helper do wyboru statystyki na starcie - bez limitu."""
        def _fn(game: "Game"):
            ch = game.character
            picks_count = ch.flags.get("stat_picks_count", 0)
            if picks_count >= 2:
                print("  Już rozdałeś wszystkie punkty!")
                return
            
            # Zwiększ statystykę
            cur = getattr(ch, stat)
            setattr(ch, stat, cur + 1)
            
            label = {
                "strength": "SIŁA",
                "dexterity": "ZRĘCZNOŚĆ",
                "intelligence": "INTELIGENCJA",
                "vitality": "WITALNOŚĆ",
            }.get(stat, stat.upper())
            
            print(f"  +1 {label} (teraz: {getattr(ch, stat)})")
            
            # Witalność daje też HP
            if stat == "vitality":
                ch.max_hp += 2
                ch.current_hp = ch.max_hp
                print(f"  +2 MAKS. ŻYCIA (teraz: {ch.max_hp})")
            
            # Zwiększ licznik
            ch.flags["stat_picks_count"] = picks_count + 1
            remaining = 2 - (picks_count + 1)
            if remaining > 0:
                print(f"  Pozostałe punkty do rozdania: {remaining}")
            else:
                print("  ✅ Rozdałeś wszystkie punkty! Możesz rozpocząć grę.")
        return _fn

        # Autor hooków: A.N
    def _on_enter_prolog_wake_up(self, game: "Game") -> None:
        ch = game.character
        if "entered_prolog_wake_up" in ch.used_actions:
            return
        ch.used_actions.add("entered_prolog_wake_up")

        ch.current_hp = min(ch.max_hp, 3)
        ch.gold = 0
        ch.silver = 0
        ch.inventory.items = []
        ch.equipment = Equipment()

        ch.flags.setdefault("table_interacted", False)
        ch.flags.setdefault("heard_snoring", False)
        ch.flags.setdefault("visited_window", False)

        # Autor hooków: A.N
    def _exit_prolog_wake_up(self, game: "Game") -> Optional[str]:
        ch = game.character
        if ch.flags.get("heard_snoring", False):
            return "prolog_old_man_intro"
        if ch.flags.get("table_interacted", False):
            return "prolog_old_man_intro"
        return None

        # Autor hooków: A.N
    def _on_enter_scene2_dynamic(self, game: "Game") -> None:
        # tu ewentualnie możesz dopiąć dynamiczne teksty Adam
        pass

        # Autor hooków: A.N
    def _on_enter_first_path(self, game: "Game") -> None:
        ch = game.character
        if ch.flags.get("direction_forest"):
            self.scenes["act1_first_path"].narration = (
                "Las szybko gęstnieje. Światło znika między koronami.\n"
                "Tu łatwo się ukryć — i łatwo zgubić drogę."
            )
        elif ch.flags.get("direction_hills"):
            self.scenes["act1_first_path"].narration = (
                "Ziemia twardnieje. Masz lepszy widok, ale sam jesteś bardziej widoczny.\n"
                "Wzgórza nie wybaczają błędów."
            )
        else:
            self.scenes["act1_first_path"].narration = (
                "Mgła wisi nisko. Każdy krok wciąga buty w miękką ziemię.\n"
                "Mokradła są ciche w sposób, który budzi niepokój."
            )

        # Autor hooków: A.N
    def _on_enter_fight_intro(self, game: "Game") -> None:
        ch = game.character
        if ch.flags.get("fight_advantage", False) and "fight_advantage_applied" not in ch.used_actions:
            ch.used_actions.add("fight_advantage_applied")
            ch.heal(1)

        # Autor hooków: A.N
    def _on_enter_finale(self, game: "Game") -> None:
        choice = game.character.flags.get("act1_final_choice", "defend")
        base = (
            "Ogień trzaska głośniej.\n"
            "Cienie wokół ogniska poruszają się nie od wiatru, lecz od czegoś, co krąży poza światłem.\n"
            "To nie są orkowie.\n"
            "Coś nowego — coś, co poluje inaczej.\n"
        )
        if choice == "defend":
            self.scenes["act1_finale"].narration = base + "\nZostajesz. Bronisz ognia."
        elif choice == "flee":
            self.scenes["act1_finale"].narration = base + "\nOdwracasz się. Uciekasz w ciemność."
        else:
            self.scenes["act1_finale"].narration = base + "\nRuszysz pierwszy — by odciągnąć zagrożenie."

    # -------------------------
    # Nowe hooki dla fabuły leśnej - A.O + A.N
    # -------------------------

    def _on_enter_forest_voices(self, game: "Game") -> None:
        """Dynamiczna narracja dla sceny z głosami - zależy od ostrzeżenia starca."""
        ch = game.character
        if ch.flags.get("warned_by_old_man", False):
            # Gracz został ostrzeżony przez starca
            extra = "\n\n(Pamiętasz ostrzeżenie starca: nie zbliżaj się do ludzi wołających o pomoc...)"
            self.scenes["act1_forest_voices"].narration = (
                "Idziesz dalej, gdy nagle słyszysz to wyraźnie...\n\n"
                "— POMOCY! PROSZĘ, NIECH KTOŚ MI POMOŻE!\n\n"
                "To głos kobiety, dochodzący gdzieś z głębi lasu, na lewo od traktu.\n"
                "Brzmi rozpaczliwie, pełen strachu i bólu.\n\n"
                "— BŁAGAM! JESTEM RANNA! NIE MOGĘ SIĘ RUSZYĆ!\n\n"
                "Słowa starca wracają do ciebie: 'POD ŻADNYM POZOREM NIE ZBLIŻAJ SIĘ\n"
                "DO LUDZI KTÓRZY MOGLIBY WOŁAĆ O POMOC'...\n\n"
                "Ale... a jeśli to naprawdę ktoś potrzebujący pomocy?"
                + extra
            )
        #Arek tu jest sprawdzenie czy masz wiecej srebra niz 5
        ch.flags["has_silver_5"] = (ch.silver >= 5)

    def _on_enter_mglak_trap(self, game: "Game") -> None:
        """Narracja pułapki Mglaka - zależy od tego czy gracz wiedział o niebezpieczeństwie."""
        ch = game.character
        warned = ch.flags.get("warned_by_old_man", False)
        listened = ch.flags.get("listened_carefully", False)
        
        if warned:
            # Gracz WIEDZIAŁ że to pułapka
            narration = (
                "Schodzisz z traktu i zagłębiasz się w las...\n\n"
                "Głos prowadzi cię coraz dalej. I nagle... cisza.\n\n"
                "Starzec OSTRZEGAŁ cię. Wiedziałeś, że to pułapka.\n"
                "A mimo to tu jesteś. Jakim trzeba być KRETYNEM...\n\n"
                "Mgła zaczyna gęstnieć wokół ciebie. Lodowata. Nienaturalna.\n"
                "Z jej głębin wyłania się COŚ. Blade, wychudzone, z oczami\n"
                "jak dwa martwe księżyce...\n\n"
                "MGLAK.\n\n"
                "Starzec miał rację. A ty jesteś idiotą."
            )
        elif listened:
            # Gracz nasłuchiwał, więc wiedział że to pułapka
            narration = (
                "Mimo że WIEDZIAŁEŚ, że to nie jest człowiek...\n"
                "Mimo że twoja intuicja KRZYCZAŁA, żebyś uciekał...\n"
                "Mimo wszystko - tu jesteś.\n\n"
                "Głos cichnie. Mgła gęstnieje.\n"
                "Z jej głębin wyłania się COŚ. Blade, wychudzone...\n\n"
                "MGLAK. Wampir mgły. Istota polująca na głupców.\n"
                "Takich jak ty."
            )
        else:
            # Gracz nie wiedział - ścieżka 3B (wyszedł wcześniej od starca)
            narration = (
                "Schodzisz z traktu, kierując się głosem kobiety.\n\n"
                "Las gęstnieje. Światło słoneczne z trudem przebija się przez korony.\n"
                "Głos się oddala... a potem nagle cichnie.\n\n"
                "Coś jest nie tak. Powietrze staje się lodowate.\n"
                "Mgła zaczyna się zbierać wokół twoich stóp...\n\n"
                "I wtedy TO widzisz. Wyłania się z mgły jak koszmar.\n"
                "Blade ciało, wychudzone, z oczami jak martwe księżyce.\n"
                "To nie był człowiek. To PUŁAPKA.\n\n"
                "MGLAK. I jesteś jego ofiarą."
            )
        
        self.scenes["mglak_trap_enter"].narration = narration

    def _on_enter_mglak_escape_end(self, game: "Game") -> None:
        """Narracja po ucieczce przed Mglakiem."""
        ch = game.character
        if ch.current_hp <= 2:
            narration = (
                "Wypadasz z mgły na trakt, dysząc ciężko.\n\n"
                "Jesteś ranny. Bardzo ranny. Ledwo żyjesz.\n"
                "Ale ŻYJESZ.\n\n"
                "Za tobą mgła powoli się rozwiewa. Mglak odpuścił...\n"
                "Na razie.\n\n"
                "To była lekcja. Bolesna lekcja. Już nigdy nie zignorujesz ostrzeżeń."
            )
        else:
            narration = (
                "Wypadasz z mgły na trakt, dysząc ciężko.\n\n"
                "Udało się. Uciekłeś przed tą istotą.\n"
                "Twoje serce wali jak oszalałe, ale jesteś cały.\n\n"
                "Za tobą mgła się rozwiewa. Mglak zniknął.\n\n"
                "Idziesz dalej, nie oglądając się za siebie."
            )
        
        self.scenes["mglak_escape_end"].narration = narration

    def _on_enter_werewolf(self, game: "Game") -> None:
        """Przygotowanie do walki z wilkołakiem."""
        ch = game.character
        # Sprawdź czy gracz ma srebrny nóż
        has_silver = ch.inventory.has_item("silver_knife")
        ch.flags["has_silver_weapon"] = has_silver

    def _on_enter_dawn_ending(self, game: "Game") -> None:
        """Zakończenie Aktu I - zależne od wyboru ze srebrnym nożem."""
        ch = game.character
        wounded_werewolf = ch.flags.get("wounded_werewolf", False)
        
        if wounded_werewolf:
            narration = (
                "Świt.\n\n"
                "Pierwsze promienie słońca przebijają przez korony drzew.\n"
                "Tam, gdzie zniknęła bestia, widzisz ruch...\n\n"
                "To nie wilkołak. To... kobieta?\n\n"
                "Młoda, piękna, naga. Leży skulona na ziemi, trzymając się za ramię.\n"
                "Krwawi. W tym samym miejscu, gdzie trafiłeś bestię srebrnym nożem.\n\n"
                "Jej oczy są pełne bólu i... wstydu?\n"
                "— P-proszę... — szepcze. — Nie chciałam...\n\n"
                "Zdejmujesz swoje łachmany i okrywasz nimi drżącą kobietę.\n"
                "Cokolwiek się stało... ona nie jest winna.\n\n"
                "Klątwa. To musi być jakaś klątwa.\n\n"
                "Patrzysz na nią, a potem na wschodzące słońce.\n"
                "Ten las kryje więcej tajemnic, niż się spodziewałeś..."
            )
        else:
            narration = (
                "Świt.\n\n"
                "Pierwsze promienie słońca przebijają przez korony drzew.\n"
                "Bestia wyje ostatni raz i znika w lesie.\n\n"
                "Przetrwałeś.\n\n"
                "Gasisz resztki ogniska i zbierasz swoje rzeczy.\n"
                "Ta noc była... koszmarem. Ale żyjesz.\n\n"
                "Gdzieś w oddali słyszysz jeszcze wycie - ludzkie czy zwierzęce?\n"
                "Nie wiesz. I nie chcesz wiedzieć.\n\n"
                "Ruszasz dalej na wschód. Słońce ogrzewa twoje zmęczone ciało.\n"
                "Koniec Aktu I."
            )
        
        self.scenes["act1_dawn_ending"].narration = narration


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    random.seed()
    try:
        Game().run()
    except Exception as e:
        import traceback
        print("\n*** WYSTĄPIŁ BŁĄD ***\n")
        traceback.print_exc()
        input("\nNaciśnij Enter, aby zamknąć...")

