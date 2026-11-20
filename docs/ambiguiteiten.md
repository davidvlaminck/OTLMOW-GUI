# Openstaande punten en ambiguiteiten

Dit document hoort bij [functioneel-overzicht.md](functioneel-overzicht.md) en bundelt alle punten
die tijdens de code-analyse niet eenduidig uit de implementatie konden worden afgeleid. Ze zijn
bedoeld als besluitlijst vóór of tijdens het schrijven van Gherkin-scenario's.

## 1. Doel en gebruik

- Elk punt beschrijft **waargenomen gedrag**, **bewijs in de code**, **waarom het onduidelijk is**,
  **de te nemen beslissing** en **de impact op Gherkin**.
- De voorgestelde aanname is de default die in het functioneel overzicht is gebruikt. Zodra een
  punt is beslist, wordt de status aangepast en wordt het overzicht bijgewerkt.
- Statuswaarden: `open`, `beslist`, `vervallen`.
- Verwijs in Gherkin-tickets naar het ID (bijvoorbeeld `A-03`) in plaats van de vraag opnieuw uit
  te leggen.

## 2. Samenvatting

| ID | Onderwerp | Type | Impact | Status |
|---|---|---|---|---|
| A-01 | Deprecated-attributenoptie en omgekeerde flag | Dode code/naamgeving | Laag | beslist |
| A-02 | Gedeelde klassenselectie tussen beide template-tabs | Gedrag | Hoog | beslist |
| A-03 | Infotemplate negeert klassenselectie | Gedrag | Hoog | beslist |
| A-04 | Activatie en betekenis van diff-export | Gedrag | Hoog | beslist |
| A-05 | Projectexport bevat enkel de laatste quick save | Scope/data | Middel | beslist |
| A-06 | Bewaartermijn quick saves (7 dagen, stil) | Data/communicatie | Laag | beslist |
| A-07 | Kaart "verouderd" deelt status met datavisualisatie | Gedrag | Middel | beslist |
| A-08 | Logs openen werkt enkel op Windows | Platform | Laag | beslist |
| A-09 | Projectbestanden definitief verwijderen | Semantiek | Hoog | beslist |
| A-10 | Attributen zijn niet bewerkbaar in de GUI | Scope | Hoog | beslist |
| A-11 | SDF enkel op Windows met FDO Toolbox | Platform | Middel | beslist |
| A-12 | Ontbrekende foutmeldingen (TODO's) | Foutafhandeling | Hoog | beslist |
| A-13 | "Geen resultaten" wordt nooit getoond | Gedrag | Laag | beslist |
| A-14 | Exporteren met ontbrekende bestanden | Foutafhandeling | Middel | beslist |
| A-15 | Agent-klasse stil geblokkeerd in template | Gedrag | Laag | beslist |
| A-16 | Dubbele identificatoren in de objectlijst | Foutafhandeling | Middel | beslist |

## 3. Detail per punt

### A-01 Deprecated-attributenoptie en omgekeerde flag

**Status:** beslist — dode code verwijderen, zie [TODO.md](../TODO.md).

**Waargenomen gedrag**
- De checkbox `show_deprecated_attributes` wordt aangemaakt en geconfigureerd, maar **nooit aan een
  layout toegevoegd**. De checkbox is dus niet zichtbaar in de GUI. Hetzelfde geldt voor het label
  `non_otl_conform_settings_title`.
- De checkbox staat bovendien op `disabled` en wordt nergens opnieuw ingeschakeld.
- De domeinvlag `has_a_class_with_deprecated_attributes` krijgt de uitkomst van
  `check_for_no_deprecated_present()`. Die functie geeft `True` wanneer er **geen** verouderde
  attributen zijn, dus de vlag betekent het omgekeerde van zijn naam.
- De daadwerkelijke markering van verouderde attributen in het template wordt bepaald door de
  radiokeuze: alleen bij de niet-DAVIE-optie ("Expanded info") staat `highlight_deprecated_attributes`
  aan.

**Bewijs**
- `otlmow_gui/GUI/screens/TemplateScreen.py:276` (aanmaken checkbox)
- `otlmow_gui/GUI/screens/TemplateScreen.py:347-352` (configureren, maar geen `addWidget`)
- `otlmow_gui/GUI/screens/TemplateScreen.py:364-377` (layout zonder de checkbox)
- `otlmow_gui/Domain/step_domain/TemplateDomain.py:35-36` (`check_for_no_deprecated_present`)
- `otlmow_gui/Domain/step_domain/TemplateDomain.py:140` (omgekeerde toewijzing)
- `otlmow_gui/GUI/screens/TemplateScreen.py:754-772` (radio bepaalt markering)

**Waarom onduidelijk**
De checkbox en het label zijn dode UI-code: ze bestaan in het objectmodel maar worden nooit
gerenderd. De vlag heeft een misleidende naam en beïnvloedt alleen een onzichtbare checkbox.

**Beslissing**
De checkbox, het label, de domeinvlag en `check_for_no_deprecated_present()` zijn dood en worden
verwijderd. De radiokeuze "Expanded info" blijft de enige bepaler van de deprecated-markering.

**Gherkin-impact**
Geen scenario voor `show_deprecated_attributes`; wel een scenario voor de markering via de
template-optie.

---

### A-02 Gedeelde klassenselectie tussen beide template-tabs

**Waargenomen gedrag**
- Beide schermen (`TemplateScreen` en `InfoTemplateScreen`) tonen een klassenlijst.
- De selectie staat in één class-attribuut `TemplateDomain.selected_classes_indexes`.
- `TemplateDomain.get_screen()` geeft het **actieve** tabblad terug; `update_frontend()` werkt
  daardoor alleen het zichtbare scherm bij.

**Bewijs**
- `otlmow_gui/Domain/step_domain/TemplateDomain.py:29`
- `otlmow_gui/Domain/step_domain/TemplateDomain.py:181-193`
- `otlmow_gui/GUI/screens/TemplateScreen.py:908`
- `otlmow_gui/GUI/screens/InfoTemplateScreen.py:266`

**Waarom onduidelijk**
Een wijziging in de ene tab beïnvloedt de andere tab, maar het niet-actieve scherm wordt niet
meteen visueel bijgewerkt. Het is niet duidelijk of gedeelde selectie functioneel gewenst is of
een neveneffect van de gedeelde domeinklasse.

**Beslissing nodig**
Moeten aanlevertemplate en infotemplate een eigen, onafhankelijke klassenselectie hebben?

**Voorgestelde aanname**
De selectie is bewust gedeeld: de gebruiker kiest één keer de klassen voor beide templates.
Gherkin beschrijft expliciet dat wijzigen in de ene tab de andere tab beïnvloedt.

**Gherkin-impact**
Eén scenario "klassenselectie is gedeeld tussen aanlever- en infotemplate", plus een scenario
dat het niet-actieve tabblad bij terugkeer de actuele selectie toont.

---

### A-03 Infotemplate negeert klassenselectie

**Waargenomen gedrag**
- Het infotemplate-scherm toont de klassenlijst, de teller en een exportknop die pas actief wordt
  bij minstens één geselecteerde klasse.
- De export roept `InfotemplateGenerator.generate_infotemplate_from_subset_async()` aan met
  **alleen** `subset_path` en `template_file_path`. De selectie wordt niet meegegeven.
- De generator komt uit de externe package `otlmow_template` en bepaalt de inhoud op basis van de
  volledige subset.

**Bewijs**
- `otlmow_gui/GUI/screens/InfoTemplateScreen.py:198-202` (knop actief bij selectie)
- `otlmow_gui/GUI/screens/InfoTemplateScreen.py:228-241` (export zonder selectie)
- `otlmow_gui/Domain/step_domain/TemplateDomain.py:213-219` (selectie wordt alleen bij het
  aanlevertemplate gebruikt)

**Waarom onduidelijk**
De UI wekt de indruk dat de selectie de infotemplate bepaalt, maar de code doet dat niet. Of dit
een fout is of een bewuste beperking van de externe generator is niet vast te stellen.

**Beslissing nodig**
1. Moet de infotemplate de geselecteerde klassen respecteren?
2. Zo nee: de selectie-UI op het infotemplate-scherm verwijderen of als "alleen informatief"
   labelen.
3. Zo ja: generator uitbreiden en de verwachte inhoudspecificeren.

**Voorgestelde aanname**
De infotemplate bevat altijd alle klassen van de subset. De selectie-UI op dat scherm is
informatief en de exportknop wordt niet als selectie-afhankelijk getest.

**Gherkin-impact**
Geen scenario dat een gefilterde infotemplate verwacht. Wel een expliciet scenario dat de
infotemplate de volledige subset bevat.

---

### A-04 Activatie en betekenis van diff-export

**Waargenomen gedrag**
- De knop "Export without unedited data" wordt actief zodra minstens één origineel bestand is
  toegevoegd; een expliciete stap "Toon verschillen" is niet vereist.
- "Toon verschillen" vult alleen een preview-tabel.
- Bij export wordt de diff opnieuw berekend tegen de originelen en weggeschreven.

**Bewijs**
- `otlmow_gui/GUI/screens/ExportData_elements/ExportFilteredDataSubScreen.py:236-242`
- `otlmow_gui/GUI/screens/ExportData_elements/ExportFilteredDataSubScreen.py:250-256`
- `otlmow_gui/Domain/step_domain/ExportFilteredDataSubDomain.py:93-105`
- `otlmow_gui/Domain/step_domain/ExportFilteredDataSubDomain.py:118-...`

**Waarom onduidelijk**
De preview is optioneel en de export hangt niet af van de getoonde diff. Daardoor kan de
gebruiker exporteren zonder de verschillen te hebben gecontroleerd. Ook is niet vastgelegd wat
er gebeurt als een origineel bestand intussen is gewijzigd.

**Beslissing** (beslist 2026-11-19)
1. Preview is optioneel; export is niet geblokkeerd zonder preview.
2. Export herberekent de diff op het moment van exporteren (niet de getoonde preview).
3. Bij gewijzigd of verwijderd origineel bestand: export blokkeert met een melding ("Fout in
   originele bestanden"); gebruiker moet corrigeren.

**Gherkin-impact**
Aparte scenario's voor "verschillen tonen" en "gewijzigde data exporteren"; geen scenario dat
export blokkeert zonder preview; plus een scenario voor de foutmelding bij gewijzigd origineel.

---

### A-05 Projectexport bevat enkel de laatste quick save

**Waargenomen gedrag**
- `.otlw`-export schrijft projectdetails, documentenoverzicht, subset, projectbestanden, de
  **laatste** quick save en de actuele visualisatiebestanden.
- Oudere quick saves worden niet meegenomen.

**Bewijs**
- `otlmow_gui/Domain/project/Project.py:499-564`, specifiek `549-552`

**Waarom onduidelijk**
Bij delen of back-uppen gaat de bewerkgeschiedenis van oudere quick saves verloren. Het is niet
duidelijk of dit bewust is om de export klein te houden.

**Beslissing** (beslist 2026-11-19)
Alleen de laatste quick save gaat mee in het `.otlw`-bestand. Oudere quick saves blijven lokaal.

**Gherkin-impact**
Scenariostap: "het geëxporteerde project bevat de laatst bewaarde quick save en geen oudere
quick saves".

---

### A-06 Bewaartermijn quick saves (7 dagen, stil)

**Waargenomen gedrag**
- Bij elke quick save worden bestanden ouder dan 7 dagen verwijderd.
- Verwijdering gebeurt stil, zonder melding of gebruikersinstelling.
- Bestanden die niet het standaard naamformaat volgen, worden nooit verwijderd.

**Bewijs**
- `otlmow_gui/Domain/project/Project.py:56-57` (`max_days_quicksave_stored = 7`)
- `otlmow_gui/Domain/project/Project.py:408-419`
- `otlmow_gui/Domain/project/Project.py:460-496`

**Waarom onduidelijk**
De termijn is een hardcoded constante. Het is niet duidelijk of dit een functionele eis is of een
technische opruimregel.

**Beslissing** (beslist 2026-11-19)
7 dagen blijft de geldende bewaartermijn; geen gebruikersinstelling en geen melding. Bestanden die
niet het standaard naamformaat volgen, worden nooit verwijderd.

**Gherkin-impact**
Eén scenario over automatische opruiming van quick saves ouder dan 7 dagen.

---

### A-07 Kaart "verouderd" deelt status met datavisualisatie

**Waargenomen gedrag**
- De kaart toont een label "De visualisatie is verouderd" op basis van
  `RelationChangeDomain.is_visualisation_uptodate()`.
- Die methode leest dezelfde `visualisation_uptodate`-state als de datavisualisatie.
- De kaart heeft geen eigen actualiteitsstatus.

**Bewijs**
- `otlmow_gui/GUI/screens/MapScreen.py:173`
- `otlmow_gui/GUI/screens/MapScreen.py:261`
- `otlmow_gui/Domain/step_domain/RelationChangeDomain.py:1560-1561`

**Waarom onduidelijk**
De indicator kan afwijken van de werkelijke kaartactualiteit: een wijziging kan de visualisatie
verouderen zonder dat de kaart inhoudelijk is bijgewerkt, of omgekeerd.

**Beslissing** (beslist 2026-11-19)
Indicator deelt bewust dezelfde status; "visualisatie" in brede zin (datavisualisatie en kaart samen).
Gherkin spreekt over "visualisatie" als geheel.

**Gherkin-impact**
Scenariostap: "de kaart toont de verouderd-indicator wanneer de visualisatiestatus verouderd is".

---

### A-08 Logs openen werkt enkel op Windows

**Waargenomen gedrag**
- "Open logs" start `explorer /select,...` zonder platformcontrole.
- Op Linux en macOS bestaat `explorer` niet, waardoor de actie faalt of niets doet.

**Bewijs**
- `otlmow_gui/GUI/header/HeaderBar.py:167-179`

**Waarom onduidelijk**
Het menu-item is op alle platformen zichtbaar, maar de implementatie is Windows-specifiek.

**Beslissing** (beslist 2026-11-19)
Cross-platform, best-effort: Windows/macOS selecteren het bestand; Linux opent de map (en waar
mogelijk het bestand). Geen platformvoorwaarde meer; werkt op alle platformen met degraded
gedrag op Linux.

**Gherkin-impact**
Scenario "logs openen" zonder platformvoorwaarde; optioneel `@windows`-achtige tags niet nodig.

---

### A-09 Projectbestanden definitief verwijderen

**Waargenomen gedrag**
- `remove_all_project_files()` en `remove_project_file()` verwijderen bestanden definitief van
  schijf.
- Er is geen prullenbak, undo of bevestiging in de domeinlaag; de bevestiging zit in het
  dialoogvenster.

**Bewijs**
- `otlmow_gui/Domain/project/Project.py:1030-1051`
- `otlmow_gui/Domain/project/Project.py:1054-1084`
- `otlmow_gui/GUI/dialog_windows/RemoveProjectFilesWindow.py:39`

**Waarom onduidelijk**
"Verwijderen uit project" kan voor de gebruiker betekenen "uit de lijst halen" of "van schijf
verwijderen". De code kiest het tweede, zonder herstel.

**Beslissing** (beslist 2026-11-19)
Definitief verwijderen van de kopie in de projectmap is gewenst; het bevestigingsvenster is de
enige waarschuwing. Het origineel elders op schijf blijft onaangetast.

**Gherkin-impact**
Scenario expliciteert dat het bestand na bevestiging niet meer in de projectmap bestaat.

---

### A-10 Attributen zijn niet bewerkbaar in de GUI

**Status:** beslist — attribuutwaarden zijn read-only in de GUI.

**Waargenomen gedrag**
- De GUI toont attributen van objecten en relaties, maar biedt geen algemene bewerkactie voor
  attribuutwaarden.
- Bewerkbaar zijn: relaties toevoegen/verwijderen, externe assets toevoegen en bestandsbeheer.
- Correcties verlopen via de bronbestanden en hervalidatie.

**Bewijs**
- `otlmow_gui/GUI/screens/RelationChangeScreen.py:302-317` (enkel vullen/tonen)
- `otlmow_gui/Domain/step_domain/RelationChangeDomain.py:612` (attributen doorgeven aan scherm)

**Waarom onduidelijk**
Dit is een bewuste scope-keuze, maar ze is nergens als eis vastgelegd. Zonder expliciete
vermelding gaan lezers ervan uit dat een attributenpaneel ook editbaar is.

**Beslissing**
Attribuutwaarden zijn read-only; correctie gebeurt via bronbestanden en hervalidatie.

**Gherkin-impact**
Geen scenario voor attribuutbewerking; wel een negatief/scope-scenario dat het paneel read-only is.

---

### A-11 SDF enkel op Windows met FDO Toolbox

**Status:** beslist — SDF is een aparte, Windows-only optionele feature met FDO Toolbox-vereiste.

**Waargenomen gedrag**
- SDF staat alleen in de ondersteunde formaten wanneer `sys.platform` Windows is.
- De SDF-verwerking vereist FDO Toolbox.

**Bewijs**
- `otlmow_gui/Domain/global_vars.py:13-17`
- `otlmow_gui/Domain/util/SDFHandler.py`

**Waarom onduidelijk**
SDF is een optionele feature met een externe dependency. Het is niet vastgelegd of dit een
platformvoorwaarde of een aparte optionele feature moet zijn in Gherkin.

**Beslissing**
SDF is een aparte feature met Windows- en FDO-Toolbox-voorwaarde.

**Gherkin-impact**
`@windows`-tag en een `Given`-voorwaarde "FDO Toolbox is beschikbaar" op SDF-scenario's.

---

### A-12 Ontbrekende foutmeldingen (TODO's)

**Status:** beslist — AS-IS gedrag documenteren: fouten worden gesilenced (TODO's in code), geen gebruikersmelding.

**Waargenomen gedrag**
Op verschillende plaatsen wordt een fout doorgegeven of genegeerd zonder gebruikersgerichte
melding. De code markeert dit zelf met `TODO`.

**Bewijs**
- `otlmow_gui/GUI/header/HeaderBar.py:271` (project importeren)
- `otlmow_gui/GUI/screens/Home_elements/OverviewTable.py:193` (project exporteren)
- `otlmow_gui/GUI/screens/TemplateScreen.py:745` (template exporteren)
- `otlmow_gui/GUI/screens/InsertDataScreen.py:567` (bestand toevoegen)
- `otlmow_gui/GUI/screens/ExportData_elements/AbstractExportDataSubScreen.py:154`
- `otlmow_gui/GUI/screens/ExportData_elements/ExportFilteredDataSubScreen.py:185`
- `otlmow_gui/Domain/project/Project.py:584, 1047, 1077, 1111`
- `otlmow_gui/Domain/step_domain/TemplateDomain.py:146` (subsetbestand niet gevonden)

**Waarom onduidelijk**
Het gewenste gedrag (blokkeren, melding, gedeeltelijke doorgang) is niet gespecificeerd.

**Beslissing**
Gherkin beschrijft het huidige gedrag: fouten worden niet getoond aan de gebruiker (gesilenced).
De TODO's in de code zijn de specificatie. Later kunnen code en Gherkin samen worden bijgewerkt
wanneer foutafhandeling wordt verbeterd.

**Gherkin-impact**
Scenario's per foutpad die het afwezig zijn van een gebruikersmelding bevestigen (negatieve
scenario's: "geen foutmelding wordt getoond").

---

### A-13 "Geen resultaten" wordt nooit getoond

**Status:** beslist — melding tonen bij lege projectenlijst én bij lege zoekresultaten.

**Waargenomen gedrag**
- De projectentabel maakt een `error_widget` aan en zet de tekst op "no results" (in `reset_ui`).
- De widget wordt nergens aan de tabel of layout toegevoegd, dus de melding is niet zichtbaar.
- De `filter()` methode verwijdert rijen die niet matchen, maar toont geen melding wanneer alle rijen
  gefilterd zijn.

**Bewijs**
- `otlmow_gui/GUI/screens/Home_elements/OverviewTable.py:50` (aanmaken `error_widget`)
- `otlmow_gui/GUI/screens/Home_elements/OverviewTable.py:118` (filter wordt aangeroepen na vullen)
- `otlmow_gui/GUI/screens/Home_elements/OverviewTable.py:228-274` (filter verwijdert niet-matchende rijen)
- `otlmow_gui/GUI/screens/Home_elements/OverviewTable.py:315` (tekst instellen, maar widget niet tonen)
- Geen andere referenties naar `error_widget` in de projectentabel.

**Waarom onduidelijk**
De bedoeling is duidelijk (melding bij 0 resultaten), maar de implementatie ontbreekt. Onduidelijk
was: geldt dit voor een initieel lege lijst, voor lege zoekresultaten, of voor beide?

**Beslissing**
De melding "geen resultaten" verschijnt in twee situaties:
1. **Initieel lege projectenlijst** — wanneer de gebruiker nog geen projecten heeft aangemaakt.
2. **Lege zoekresultaten** — wanneer een zoekopdracht (via zoekveld) 0 matchende projecten oplevert.

De `error_widget` (of een equivalente placeholder-rij) wordt in de tabelzone getoond zodra
`rowCount() == 0` na vullen of na filteren.

**Gherkin-impact**
Twee scenario's:
- "lege projectenlijst toont geen resultaten-melding"
- "zoekopdracht zonder matches toont geen resultaten-melding"

---

### A-14 Exporteren met ontbrekende bestanden

**Status:** beslist — gebruiker krijgt expliciete waarschuwing en kan doorgaan; export bevat enkel bestaande bestanden.

**Waargenomen gedrag**
- Bij projectexport wordt gecontroleerd of alle projectbestanden bestaan.
- Ontbrekende bestanden worden in een ja/nee-venster opgesomd; "Nee" annuleert de export.
- De vergelijking met `65536` is een hardcoded Qt-knopwaarde (`No`).

**Bewijs**
- `otlmow_gui/Domain/project/Project.py:529-542`

**Waarom onduidelijk**
Het gedrag is functioneel duidelijk, maar de hardcoded waarde is fragiel. Ook is niet vastgelegd
of de export zonder de ontbrekende bestanden mag doorgaan (momenteel: ja, na bevestiging).

**Beslissing**
De gebruiker krijgt een expliciete waarschuwing en kan doorgaan; het exportbestand bevat dan enkel
de bestaande bestanden.

**Gherkin-impact**
Scenario: "exporteren met ontbrekende bestanden vraagt om bevestiging en gaat daarna door".

---

### A-15 Agent-klasse stil geblokkeerd in template

**Status:** beslist — Agent is in geen enkel template selecteerbaar; expliciete business rule.

**Waargenomen gedrag**
- De klasse `Agent` wordt in de klassenlijst grijs en niet-selecteerbaar gemaakt.
- De tooltip licht toe dat Agent niet is toegestaan in een template.
- Bij "alles selecteren" wordt Agent overgeslagen.

**Bewijs**
- `otlmow_gui/GUI/screens/TemplateScreen.py:946-953`
- `otlmow_gui/Domain/step_domain/TemplateDomain.py:141, 156, 251`

**Waarom onduidelijk**
Het is een bewuste beperking, maar ze staat niet in een functionele eis. Bovendien wordt Agent in
de infotemplate niet op dezelfde manier behandeld.

**Beslissing**
Agent is in geen enkel template selecteerbaar; dit is een expliciete business rule.

**Gherkin-impact**
Scenario: "Agent kan niet geselecteerd worden voor een template".

---

### A-16 Dubbele identificatoren in de objectlijst

**Status:** beslist — huidige gedrag behouden: dubbele identificatoren over verschillende bestanden worden geaccepteerd, enkel gelogd; geen blokkering tenzij tegenstrijdige informatie.

**Waargenomen gedrag**
- Bij het opzoeken van een object met een identificator wordt een dubbele match enkel gelogd.
- De code gaat verder met `pass`; er wordt geen fout aan de gebruiker gemeld.

**Bewijs**
- `otlmow_gui/Domain/step_domain/RelationChangeDomain.py:490-497`

**Waarom onduidelijk**
Dubbele identificatoren wijzen op een dataprobleem. Het is niet duidelijk of dit moet blokkeren,
waarschuwen of stil moet doorgaan.

**Beslissing**
Twee bestanden mogen objecten met gelijke identificatoren bevatten; dat is geen probleem op zich.
Alleen wanneer ze tegenstrijdige informatie bevatten (bv. attribuutwaarden) is er sprake van een
conflict. Huidig gedrag (loggen en doorgaan) is correct; het relatiescherm hoeft dit niet apart af
te handelen.

**Gherkin-impact**
Geen scenario voor blokkering bij dubbele identificatoren. Wel scenario dat herkent dat gelijke
identificatoren over bestanden heen toegestaan zijn.

---

## 4. Aannames die nu in het overzicht zijn gebruikt

Deze defaults gelden zolang het bijbehorende punt open is:

| ID | Default in het overzicht |
|---|---|
| A-01 | Beslist: dode checkbox/label/vlag verwijderen; radiokeuze bepaalt markering. |
| A-02 | Beslist: klassenselectie gedeeld + live sync. |
| A-03 | Beslist: infotemplate respecteert selectie (filter, fallback volledige subset). |
| A-04 | Beslist: huidig gedrag (preview optioneel, diff herberekend, blokkeren + melding). |
| A-05 | Beslist: enkel de laatste quick save gaat mee in `.otlw`. |
| A-06 | Beslist: 7 dagen stil opgeruimd, geen instelling/melding. |
| A-07 | Beslist: kaart en datavisualisatie delen de verouderd-status. |
| A-08 | Beslist: cross-platform best-effort. |
| A-09 | Beslist: definitief verwijderen van kopie in projectmap. |
| A-10 | Attribuutwaarden zijn read-only in de GUI. |
| A-11 | SDF is een aparte, Windows-only optionele feature. |
| A-12 | Huidig gedrag: fouten worden gesilenced (TODO's), geen gebruikersmelding. |
| A-13 | Melding "geen resultaten" bij initieel lege lijst én lege zoekresultaten. |
| A-14 | Export met ontbrekende bestanden mag na bevestiging doorgaan. |
| A-15 | Agent is in geen enkel template selecteerbaar. |
| A-16 | Dubbele identificatoren over bestanden zijn toegestaan; enkel gelogd, geen blokkering. |

## 5. Besluitregistratie

Voeg per beslissing een regel toe aan onderstaande tabel, zodat het overzicht en de Gherkin in
sync blijven.

| ID | Datum | Beslissing | Door | Gevolg voor overzicht/Gherkin |
|---|---|---|---|---|
| A-01 | 2026-11-19 | Dode deprecated-UI en omgekeerde vlag verwijderen | Opdrachtgever | Geen scenario voor de checkbox; verwijdering staat in `TODO.md` |
| A-02 | 2026-11-19 | Klassenselectie gedeeld + live sync tussen beide tabs | Opdrachtgever | `TODO.md` (A-02); scenario's: gedeeld + live sync |
| A-03 | 2026-11-19 | Infotemplate respecteert selectie via `class_uris_filter` (fallback volledige subset) | Opdrachtgever | `TODO.md` (A-03); generator uitbreiden; scenario's: gefilterd + fallback |
| A-04 | 2026-11-19 | Huidig gedrag behouden: preview optioneel, diff herberekend bij export, blokkeren + melding bij gewijzigd origineel | Opdrachtgever | Geen code-wijziging; Gherkin beschrijft preview en export onafhankelijk |
| A-05 | 2026-11-19 | Alleen de laatste quick save gaat mee in `.otlw` | Opdrachtgever | Geen code-wijziging; Gherkin beschrijft enkel laatste quick save |
| A-06 | 2026-11-19 | Huidig gedrag behouden: 7 dagen stil opgeruimd | Opdrachtgever | Geen code-wijziging |
| A-07 | 2026-11-19 | Gedeelde verouderd-indicator behouden | Opdrachtgever | Geen code-wijziging |
| A-08 | 2026-11-19 | Cross-platform best-effort bestandsselectie | Opdrachtgever | `TODO.md` (A-08); `HeaderBar.py` aanpassen |
| A-09 | 2026-11-19 | Definitief verwijderen van kopie in projectmap behouden | Opdrachtgever | Geen code-wijziging |
| A-10 | 2026-11-20 | Attribuutwaarden zijn read-only in de GUI; correctie via bronbestanden | Opdrachtgever | Geen code-wijziging; Gherkin bevat read-only scope-scenario |
| A-11 | 2026-11-20 | SDF is een aparte, Windows-only optionele feature met FDO Toolbox-vereiste | Opdrachtgever | `@windows`-tag + `Given "FDO Toolbox is beschikbaar"` op SDF-scenario's |
| A-12 | 2026-11-20 | AS-IS gedrag documenteren: fouten gesilenced (TODO's), geen melding | Opdrachtgever | Negatieve scenario's: "geen foutmelding wordt getoond"; later code+Gherkin samen bijwerken |
| A-13 | 2026-11-20 | Melding "geen resultaten" bij initieel lege lijst én lege zoekresultaten | Opdrachtgever | Twee scenario's: lege projectenlijst + lege zoekresultaten; `error_widget` tonen bij `rowCount()==0` |
| A-14 | 2026-11-20 | Export met ontbrekende bestanden mag na bevestiging doorgaan; enkel bestaande bestanden in export | Opdrachtgever | Scenario: bevestiging bij ontbrekende bestanden; export bevat enkel bestaande bestanden |
| A-15 | 2026-11-20 | Agent is in geen enkel template selecteerbaar; expliciete business rule | Opdrachtgever | Scenario: "Agent kan niet geselecteerd worden voor een template" |
| A-16 | 2026-11-20 | Dubbele identificatoren over bestanden toegestaan; enkel gelogd, geen blokkering tenzij tegenstrijdige attributen | Opdrachtgever | Geen blokkerings-scenario; scenario: gelijke identificatoren over bestanden toegestaan |
