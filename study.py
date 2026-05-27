import json
import random
import os
import sys

# --- POMOCNÉ FUNKCE ---

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_json_files():
    return [f for f in os.listdir('.') if f.endswith('.json')]

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_next_id(data):
    """Vrátí o 1 vyšší ID než je maximum v datech."""
    if not data:
        return 1
    return max((item.get('id', 0) for item in data), default=0) + 1

# --- STATISTIKA ---

def show_statistics(data):
    """Spočítá a vypíše statistiku známek."""
    if not data:
        return

    counts = {i: 0 for i in range(1, 6)}
    
    for item in data:
        s = item.get('score', 1) 
        if 1 <= s <= 5:
            counts[s] += 1
    
    print("\n📊 STAV ZNALOSTÍ:")
    labels = ["Nové / Neumím", "S chybami", "Ujde to", "Vím", "Perfektní"]
    for i in range(1, 6):
        count = counts[i]
        print(f"   [{i}] {labels[i-1]:<13}: {count}")

# --- LOGIKA VÝBĚRU OTÁZEK ---

def get_weighted_question(data):
    """Původní logika: Vybírá váženě (čím horší známka, tím větší šance)."""
    if not data: return None
    # Váha: (6 - skóre)^2. Tedy skóre 1 má váhu 25, skóre 5 má váhu 1.
    weights = [(6 - item.get('score', 1)) ** 2 for item in data]
    return random.choices(data, weights=weights, k=1)[0]

def get_hardest_question(data):
    """Nová logika: Vybírá náhodně pouze z otázek s nejnižším skóre."""
    if not data: return None
    
    # 1. Najdeme nejmenší skóre, které se v datech vyskytuje
    min_score = min(item.get('score', 1) for item in data)
    
    # 2. Vyfiltrujeme jen ty otázky, které mají toto nejnižší skóre
    candidates = [item for item in data if item.get('score', 1) == min_score]
    
    # 3. Vybereme náhodnou z nich
    return random.choice(candidates)

def choose_subject():
    files = get_json_files()
    if not files:
        print("❌ Žádné soubory .json! Vytvoř třeba 'grafy.json'.")
        sys.exit()

    print("\n📚 DOSTUPNÉ PŘEDMĚTY:")
    for i, f in enumerate(files):
        print(f"[{i + 1}] {f.replace('.json', '')}")

    while True:
        choice = input("\nVyber číslo (nebo 'q'): ")
        if choice.lower() == 'q': sys.exit()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(files): return files[idx]
        except ValueError: pass
        print("⚠️ Neplatná volba.")

# --- IMPORT JSON ---

def add_questions_json(data, filename):
    clear_screen()
    print(f"--- IMPORT JSON: {filename} ---")
    print("Vlož JSON (objekt nebo seznam). Ukonči zadáním 'END' na nový řádek.")
    print("-" * 60)

    lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    
    raw_text = "\n".join(lines).strip()
    if not raw_text: return

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"\n❌ Chyba JSONu: {e}")
        input("Enter pro návrat...")
        return

    if isinstance(parsed, dict): new_items = [parsed]
    elif isinstance(parsed, list): new_items = parsed
    else: return

    count = 0
    for item in new_items:
        if not all(k in item for k in ["topic", "question", "answer"]):
            continue
        new_id = get_next_id(data)
        data.append({
            "id": new_id,
            "topic": item["topic"],
            "question": item["question"],
            "answer": item["answer"],
            "score": 1
        })
        count += 1

    if count > 0:
        save_data(data, filename)
        print(f"\n✅ Úspěšně přidáno {count} otázek!")
    else:
        print("\n⚠️ Žádné platné otázky.")
    input("Zmáčkni Enter...")

# --- ZKOUŠENÍ ---

def run_quiz_mode(data, filename, mode='weighted'):
    if not data:
        print("❌ Žádné otázky.")
        input("Enter..."); return

    while True:
        clear_screen()
        
        # Výběr otázky podle módu
        if mode == 'hardest':
            card = get_hardest_question(data)
            mode_label = "NEJTĚŽŠÍ (Hardcore)"
        else:
            card = get_weighted_question(data)
            mode_label = "VÁŽENÝ VÝBĚR (Standard)"
        
        print(f"\n[Předmět: {filename.replace('.json', '')} | Mód: {mode_label}]")
        print(f"[Téma: {card.get('topic', 'Obecné')} | Aktuální známka: {card.get('score', 1)}]")
        print("=" * 60)
        print(f"OTÁZKA: {card['question']}")
        print("=" * 60)
        
        cmd = input("\n(Enter=Odpověď, q=Menu, x=Konec)")
        if cmd.lower() == 'x': sys.exit()
        if cmd.lower() == 'q': return

        print("-" * 60)
        print(f"ODPOVĚĎ: {card['answer']}")
        print("-" * 60)
        
        while True:
            try:
                r = int(input("\nZnámka (1=Neumím ... 5=Easy): "))
                if 1 <= r <= 5: break
            except ValueError: pass
        
        card['score'] = r
        save_data(data, filename)
        print("Uloženo!")

# --- MENU ---

def main():
    while True:
        clear_screen()
        print("🧠 CORTEX v3.2 - Hardcore Mode Added")
        
        selected_file = choose_subject()
        data = load_data(selected_file)

        print(f"\n📂 Soubor: {selected_file} ({len(data)} otázek)")
        show_statistics(data)

        print("\n[1] Spustit zkoušení (Standardní mix) 🎲")
        print("[2] Importovat otázky (JSON) 💾")
        print("[3] Spustit zkoušení (Jen to co neumím) 💀")
        print("[q] Změnit předmět")

        action = input("\nVolba: ")
        
        if action == '1':
            run_quiz_mode(data, selected_file, mode='weighted')
        elif action == '2':
            add_questions_json(data, selected_file)
        elif action == '3':
            run_quiz_mode(data, selected_file, mode='hardest')
        elif action.lower() == 'q':
            continue

if __name__ == "__main__":
    main()