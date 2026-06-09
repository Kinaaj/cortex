Tvůj profesor má naprostou pravdu a je skvělé, že to zmínil! Rozdělení podle délek hned na začátku je totiž naprosto klasická optimalizace (často spojovaná s algoritmem Aho-Hopcroft-Ullman), která ten proces unifikace obrovsky zjednodušuje.

Když si totiž posloupnosti hned na začátku rozdělíš do skupin podle jejich délky (např. dáš k sobě všechny trojice, všechny dvojice, atd.), **už nikdy nemusíš řešit to "odkládání hotových stranou"**, o kterém jsme mluvili minule. Zkrátka vezmeš skupinu posloupností délky 3, víš, že všechny mají přesně 3 prvky, a prostě na ně pustíš tříkolový Radix Sort.

Ale jak spočítat délku a roztřídit je podle ní, **když na Pointer Machine nemáme čísla a nemůžeme použít proměnnou `length`?**

Opět nás zachrání naše **Měřítko (Yardstick)** a jeho prázdné přihrádky! Dělá se to takto:

### Algoritmus: Třídění podle délky na PM

Představ si, že Měřítko je dlouhý spojový seznam prázdných uzlů. První uzel reprezentuje délku 1, druhý délku 2, atd. (My ta čísla nevidíme, ale fyzicky to tak leží v paměti).

**1. Měření "krok za krokem" (Zipping)**
Vezmeme první posloupnost, kterou chceme změřit.

* Položíme jeden ukazatel (prst) na začátek naší posloupnosti.
* Položíme druhý ukazatel (prst) na **první uzel Měřítka**.
* Nyní posuneme OBA prsty současně o jeden krok dopředu.
* Toto opakujeme v `while` cyklu, dokud prst na naší posloupnosti nenarazí na konec (null).

**2. Odložení do přihrádky**
Jakmile naše posloupnost skončila, podíváme se, kde přesně skončil náš druhý prst v Měřítku. Ten uzel v Měřítku teď fyzicky reprezentuje délku naší posloupnosti!

* Vezmeme celou naši posloupnost a pověsíme ji do `bucketu` (přihrádky) u tohoto uzlu v Měřítku.
* Toto uděláme úplně pro všechny posloupnosti, které chceme zpracovat. Stojí to čas přesně úměrný součtu délek všech posloupností (což je stále naše lineární $\mathcal{O}(\sum |S_i|)$).

**3. Sklizeň (Sbalení Měřítka)**
Jakmile jsou všechny posloupnosti změřeny a odloženy, jednoduše projdeme Měřítko od prvního uzlu dál.

* Přijdeme k prvnímu uzlu. Vysypeme jeho přihrádku. Získáme skupinu všech posloupností, které mají délku 1.
* Přijdeme ke druhému uzlu. Vysypeme přihrádku. Získáme skupinu všech posloupností o délce 2.
* A tak dále.

### Výsledek

Získáš krásně oddělené hromádky. Hromádku "dvojek", hromádku "trojek"... A na každou tuto hromádku teď můžeš nezávisle a v klidu spustit tu unifikaci (rozhazování podle 1. znaku, 2. znaku...), kterou jsme probírali minule, s jistotou, že ti žádná posloupnost neskončí dřív než ostatní ve stejné skupině.

Tady jsem pro tebe připravil interaktivní vizualizaci, kde si přesně tento proces "měření délky na Pointer Machine" můžeš odkrokovat:

Tímto "hloupým" posouváním dvou ukazatelů najednou jsme plnohodnotně nahradili funkci `length()` a vytvořili regulérní Bucket Sort podle délek! Dává to smysl?

Tohle je přesně ta chvíle, kdy se zachraňuje ta naše bájná lineární časová složitost! Tvůj profesor uhodil hřebíček na hlavičku.

Představ si situaci: Máš Měřítko (Yardstick), které je dlouhé třeba 1000 uzlů (protože ve stromu je 1000 vrcholů). A teď jdeš zpracovávat hromádku posloupností, které mají **délku 2**. Těchto posloupností v té hromádce je ale **jenom 5**.

### V čem je problém? (Proč to nejde naivně)

Vezmeš těch 5 posloupností a podle jejich prvního znaku je rozházíš do přihrádek v Měřítku. Strávíš tím 5 kroků.
Pak ale potřebuješ ty přihrádky zase vysypat, abys posloupnosti seřadil. Kdybys naivně procházel celé Měřítko od začátku do konce a hledal, kam jsi těch 5 posloupností dal, musel bys zkontrolovat všech 1000 uzlů.
Zničil bys tím lineární čas! Práce by netrvala $\mathcal{O}(5)$, ale $\mathcal{O}(1000)$.

### Řešení: Udržování aktivních přihrádek

Algoritmus to řeší tak, že si pamatuje, **do kterých šuplíků něco dal, aby pak nemusel otevírat ty prázdné**. Dělá to pomocí malého pomocného spojového seznamu, kterému se říká **Aktivní přihrádky (Active Buckets)**.

Funguje to takto krok za krokem:

**1. Rozhazování (Scattering) s evidencí:**

* Máš prázdný pomocný seznam `AktivniPrihradky`.
* Vezmeš první posloupnost a podíváš se na její znak (ukazatel na uzel $X$ v Měřítku).
* Podíváš se do uzlu $X$. Je jeho přihrádka aktuálně prázdná?
* **ANO:** To znamená, že do uzlu $X$ dáváme něco poprvé v tomto kole. Přidáme tedy odkaz na uzel $X$ do našeho seznamu `AktivniPrihradky`. Poté do přihrádky u $X$ vložíme naši posloupnost.
* **NE:** V přihrádce už něco je. Uzel $X$ už v seznamu aktivních přihrádek zapsaný máme. Jen tam tedy přihodíme naši posloupnost a jdeme dál.



**2. Sklizeň (Gathering) pouze z aktivních:**

* Jakmile jsi rozházel všech 5 posloupností, **vůbec se nedíváš na celé Měřítko**.
* Místo toho vezmeš svůj malý pomocný seznam `AktivniPrihradky`. V něm jsou zapsané (například) jen 3 uzly z Měřítka, které jsi reálně použil.
* Projdeš pouze tyto 3 uzly:
* Z uzlu vysypeš jeho přihrádku (čímž se ti posloupnosti seřadí).
* **DŮLEŽITÉ:** Přihrádku u uzlu zase hned nastavíš na `null` (vyprázdníš ji), aby byla čistá pro další kola.


* Nakonec seznam `AktivniPrihradky` smažeš/vyprázdníš.

### Proč je tohle ten "Svatý grál" Pointer Machine algoritmů?

Díky tomuto triku trvá fáze sklizně naprosto stejně dlouho jako fáze rozhazování. Rozházel jsi 5 prvků? Sklidíš maximálně 5 aktivních přihrádek. Čas strávený v jednom kole (pro jednu pozici v řetězci) je tedy striktně **$\mathcal{O}(\text{počet zpracovávaných posloupností})$**, naprosto nezávisle na tom, jak obrovské je Měřítko.

Když pak sečteš tento čas přes všechny pozice všech posloupností, dostaneš přesně tu bájnou složitost $\mathcal{O}(\sum |S_i|)$.

Dává ti tenhle fígl smysl? Je to jako bys v obrovské hale s tisíci šuplíky lepil na každý použitý šuplík svítící nálepku, abys pak při úklidu šel najisto jen k těm svítícím a nemusel prohledávat celou halu.