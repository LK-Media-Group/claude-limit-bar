---
name: claude-limit-bar
description: Sestavte a nastavte jednoduchý ukazatel limitů Claude Code v horní liště macOS z lokálního exportu statusLine. Použijte při instalaci, vysvětlení či diagnostice tohoto balíčku. Nečte historii konverzací ani přihlašovací klíče a neměří cenu předplatného.
---

# Claude Limit Bar

Tento balíček obsahuje malou macOS aplikaci a sběrač údajů `rate_limits` z oficiálního vstupu Claude Code statusLine. Použijte postup v README; zdrojový kód aplikace je v `Sources/`.

1. Ověřte macOS 13+, Python 3.10+ a dostupnost Swift compileru. Nejprve nabídněte lokální sestavení a demo s fiktivními daty.
2. Pro reálné údaje je potřeba aktuální Claude Code a účet, který ve statusLine skutečně poskytuje pětihodinové či týdenní limity. Nepovažujte absenci pole za nulové využití. Aplikace není samostatný monitor webové aplikace Claude.
3. Pokud uživatel žádá instalaci, spusťte `scripts/configure.py install` a `scripts/build.sh` podle README. Konfigurátor zachovává ostatní nastavení i předchozí příkaz stavového řádku. Při konfliktu nastavení nic nepřepisujte naslepo.
4. Ověřte aplikaci z demo režimu a poté po běžné odpovědi v Claude Code. Sbírají se pouze procenta, časy resetu a čas přijetí. Neotevírejte keychain, OAuth tokeny, transkripty ani jiné projekty.
5. Při pomlčce zkontrolujte nejdřív stáří snímku a přítomnost podporovaných oken. `~` znamená starší data. Po uplynutí resetu aplikace čeká na nový údaj; nedomýšlí si 0 %. Čas posledního vstupu není potvrzení, že server právě přepočítal využití.
6. Vysvětlete, že zobrazené procento patří k limitu, nikoli k délce kontextu či zaplacené ceně. Při více přihlášených účtech by se v jednom lokálním souboru míchaly údaje; tato jednoduchá verze je pro jeden účet.

Odinstalaci provádí `scripts/configure.py uninstall`; obnoví původní statusLine, jen pokud nastavení stále odpovídá této instalaci. Aplikaci ukončete z její nabídky. Neukládejte produkční snímky mezi příklady balíčku.
