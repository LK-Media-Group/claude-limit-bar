# Claude Limit Bar

Malý ukazatel pětihodinového a týdenního limitu Claude Code v horní liště macOS. Zobrazuje vyšší procento z dostupných oken a v nabídce obě hodnoty i čas obnovení. Je to nezávislá komunitní pomůcka, bez spojení s Anthropic.

## Co potřebujete

macOS 13+, Python 3.10+ a Apple Command Line Tools (Swift compiler; pokud chybějí, spusťte `xcode-select --install`). Pro skutečné údaje potřebujete aktuální Claude Code a účet, který předává podporované limity do statusLine. Podle [oficiální dokumentace](https://code.claude.com/docs/en/statusline#available-data) se pětihodinové a týdenní údaje týkají předplatitelů Pro/Max a objevují se po první API odpovědi v relaci; jednotlivá okna mohou chybět.

Aplikace sama nevolá API. Čte lokální export ze stavového řádku. Samostatné používání Claude v prohlížeči bez Claude Code ji neaktualizuje. Podporuje jeden účet v jednom macOS profilu. Nezaměňujte limit s využitím kontextového okna nebo s cenou předplatného.

## Instalace přes skill

Stáhněte **Code → Download ZIP**, rozbalenou složku pojmenujte `claude-limit-bar` a vložte do `.claude/skills/` svého projektu nebo `~/.claude/skills/`. Požádejte asistenta:

> Použijte claude-limit-bar. Nejprve sestavte aplikaci a ukažte demo, potom ji nastavte pro můj Claude Code. Zachovejte můj současný stavový řádek.

## Ruční sestavení a demo

Příkazy spouštějte ve složce repozitáře:

```sh
sh scripts/build.sh
python3 scripts/collect.py --demo --output build/demo.json
open "build/Claude Limit Bar.app" --args --snapshot "$PWD/build/demo.json" --demo-label
```

V horní liště uvidíte **DEMO CL 61 %** (mezery závisejí na zobrazení). Nabídka ukáže 23 % pro 5 hodin a 61 % pro týden. Jsou to smyšlené údaje. Demo ukončete přes jeho nabídku před spuštěním reálné aplikace.

## Připojení k vašemu Claude Code

```sh
python3 scripts/configure.py install
open "build/Claude Limit Bar.app"
```

Instalátor změní pouze `statusLine` v `~/.claude/settings.json`, zachová ostatní položky a předchozí příkaz. Pokud jste statusLine už měli, most mu dál předává původní vstup a zachovává jeho výstup. Most čeká na původní příkaz nejvýše 10 sekund. Zálohu nastavení a vlastní pomocné soubory uloží jen lokálně do `~/Library/Application Support/ClaudeLimitBar/`, s omezenými oprávněními. **Tuto složku se zálohami nesdílejte**: záloha patří vašemu nastavení, ne tomuto repozitáři.

Otevřete Claude Code a po běžné odpovědi zkontrolujte ukazatel. Projektové nastavení statusLine může přebít uživatelské; v takovém případě nejprve prověřte konfiguraci daného projektu. Nevytvářejte další placený požadavek jen kvůli instalaci, pokud jej nepotřebujete.

Pro pohodlné spouštění můžete sestavenou aplikaci zkopírovat do vlastní složky Aplikace. Automatické spouštění po přihlášení si případně zapněte v Nastavení systému. Skript ho sám nezapíná. Balíček obsahuje zdrojový kód; sestavená aplikace je lokálně podepsaná, není notarizovaná ani distribuovaná jako univerzální binární soubor.

## Význam zobrazení

- `CL 61%`: vyšší využití z dostupných a dosud neobnovených oken.
- `CL ~61%`: poslední přijatý vstup je starší než 10 minut, případně má podezřelý čas v budoucnosti.
- `CL —`: nejsou dostupné použitelné údaje. Po resetu se čeká na nový vstup; chybějící hodnota se nevydává za nulu.

Aplikace čte soubor každých 10 sekund. „Poslední vstup“ znamená čas přijetí dat ze statusLine, **nikoli čas nového měření na serveru**. Při práci ve více relacích stejného účtu vyhrává poslední přijatý vstup; nejde o nepřetržité sledování serveru.

## Data a odinstalace

Sběrač ze vstupu uloží pouze `used_percentage`, `resets_at` pro dvě okna, vlastní čas přijetí a verzi formátu. Vstupní JSON obsahuje i jiné údaje, ale ty se nezapisují. Nástroj nečte konverzace, projektové soubory, keychain ani přihlašovací tokeny a nic neodesílá. Původní statusLine, pokud existuje, nadále funguje podle vaší vlastní konfigurace.

```sh
python3 scripts/configure.py uninstall
```

Odinstalátor obnoví původní statusLine a zachová ostatní aktuální nastavení. Pokud někdo mezitím statusLine změnil, odmítne jej přepsat; porovnejte nastavení se zálohou. Pak ukončete aplikaci a smažte její vlastní složku podle potřeby. Lokální zálohy se automaticky nemažou.

## Testy

```sh
python3 -m unittest discover -s tests -v
mkdir -p build
xcrun swiftc Sources/Limits.swift tests/main.swift -o build/limits-tests
build/limits-tests
```

Testy používají fiktivní vstupy a dočasné nastavení. Ověřují vyřazení ostatních polí, neplatné hodnoty, reset, stará data, zachování konfigurace a obnovu. Žádný test nepotřebuje přihlášení do Claude.
