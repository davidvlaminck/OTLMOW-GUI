# TODO

## Dode deprecated-attributen UI verwijderen (A-01)

De checkbox `show_deprecated_attributes` en het label `non_otl_conform_settings_title` worden
aangemaakt maar nooit aan een layout toegevoegd. Ze zijn dus onzichtbaar. De bijbehorende
domeinvlag `has_a_class_with_deprecated_attributes` is omgekeerd benoemd en beïnvloedt alleen deze
onzichtbare checkbox. Alles wordt verwijderd.

Zie `docs/ambiguiteiten.md` A-01.

### Taken

- [ ] `otlmow_gui/GUI/screens/TemplateScreen.py`
  - [ ] Docstring: regels voor `show_deprecated_attributes` en `non_otl_conform_settings_title`
        verwijderen (rond regel 50-52).
  - [ ] Widgets niet meer aanmaken (rond regel 276-278).
  - [ ] Configuratieblok verwijderen (rond regel 347-352).
  - [ ] Uitgecommentarieerde regel `non_otl_conform_settings_title` verwijderen (rond regel 873).
  - [ ] `set_classes`: parameter `has_a_class_with_deprecated_attributes`, bijbehorende docstring
        en de `if`-tak die de checkbox uitschakelt verwijderen (rond regel 908-959).
- [ ] `otlmow_gui/GUI/screens/InfoTemplateScreen.py`
  - [ ] `set_classes`: ongebruikte parameter `has_a_class_with_deprecated_attributes` verwijderen
        (rond regel 269).
- [ ] `otlmow_gui/GUI/screens/screen_interface/TemplateScreenInterface.py`
  - [ ] Abstracte `set_classes`-signatuur bijwerken (rond regel 85-86).
- [ ] `otlmow_gui/Domain/step_domain/TemplateDomain.py`
  - [ ] Veld `has_a_class_with_deprecated_attributes` verwijderen (regel 31).
  - [ ] `check_for_no_deprecated_present()` verwijderen (regel 34-36).
  - [ ] Reset in `fill_list()` verwijderen (regel 118).
  - [ ] Toewijzing in `fill_list()` verwijderen (regel 140).
  - [ ] Argument in `update_frontend()` verwijderen (regel 186).
- [ ] `UnitTests/domain_test/TemplateDomain_test.py`
  - [ ] Fixtures `mock_non_deprecated_classes` en `mock_deprecated_classes` verwijderen.
  - [ ] Tests `test_check_for_no_deprecated_present_detects_deprecated` en
        `test_check_for_no_deprecated_present_detects_no_deprecated` verwijderen.
  - [ ] Ongebruikte import `OSLOClass` verwijderen.
- [ ] Verificatie
  - [ ] `rg "show_deprecated_attributes|non_otl_conform_settings_title|has_a_class_with_deprecated_attributes|check_for_no_deprecated_present"` geeft geen treffers meer in `otlmow_gui/` en `UnitTests/`.
  - [ ] `python -m compileall otlmow_gui` slaagt.
  - [ ] Relevante tests draaien (minstens `UnitTests/domain_test/TemplateDomain_test.py`).
- [ ] Documentatie
  - [ ] `docs/functioneel-overzicht.md` F-TPL-02: opmerking over dode checkbox vervangen door
        "verwijderd" zodra de code weg is.

## Gedeelde klassenselectie + live sync tussen template-tabs (A-02)

De selectie is bewust gedeeld (`TemplateDomain.selected_classes_indexes`). Beide tabbladen moeten
live gesynchroniseerd worden: een wijziging in de actieve tab werkt het niet-actieve tabblad meteen
bij, zodat beide altijd dezelfde selectie tonen. Huidig gedrag werkt alleen het actieve scherm bij
via `get_screen()`.

Zie `docs/ambiguiteiten.md` A-02.

### Taken

- [ ] `otlmow_gui/Domain/step_domain/TemplateDomain.py`
  - [ ] `update_frontend()`: beide schermen bijwerken (niet alleen `get_screen()`).
  - [ ] `toggle_class_index()`, `select_all_classes()`, `deselect_all_classes()`,
        `set_selected_indexes()`: niet-actieve tab ook verversen.
  - [ ] Helper toevoegen om beide schermen te bereiken (tab1 en tab2), i.p.v. enkel actieve.
- [ ] `otlmow_gui/GUI/screens/TemplateScreen.py` en `InfoTemplateScreen.py`
  - [ ] `opened()` blijft werken als fallback, maar is niet meer de enige sync.
- [ ] Verificatie
  - [ ] Schakelen tussen tabs toont dezelfde selectie zonder handmatige refresh.
  - [ ] Relevante tests draaien.

## Infotemplate respecteert klassenselectie (A-03)

De infotemplate-export moet de geselecteerde klassen respecteren i.p.v. altijd de volledige subset.
De externe generator `otlmow_template.InfotemplateGenerator` krijgt een optionele parameter
`class_uris_filter` (analoog aan `SubsetTemplateCreator.generate_template_from_subset_async`).
Als de filter leeg is, fallback op alle concrete klassen (huidig gedrag).

Zie `docs/ambiguiteiten.md` A-03.

### Taken

- [ ] `otlmow_gui/Domain/step_domain/TemplateDomain.py` (of caller)
  - [ ] Geselecteerde klassen als URI-lijst afleiden (`classes[i].objectUri` voor
        `i in selected_classes_indexes`).
- [ ] `otlmow_gui/GUI/screens/InfoTemplateScreen.py`
  - [ ] `save_template()`: geselecteerde klassen doorgeven aan
        `generate_infotemplate_from_subset_async` als `class_uris_filter`.
- [ ] `otlmow_template/InfotemplateGenerator.py` (extern package, apart repo)
  - [ ] `generate_infotemplate_from_subset` en `_async`-variant: parameter `class_uris_filter`
        toevoegen (default `None`).
  - [ ] Bij filter: `concrete_classes` filteren op objectUri in de filterlijst.
  - [ ] Bij lege/None filter: huidig gedrag (alle concrete klassen).
- [ ] Verificatie
  - [ ] Infotemplate bevat enkel geselecteerde klassen na export.
  - [ ] Lege selectie → volledige subset (fallback).
  - [ ] Relevante tests draaien.

## "Geen resultaten" melding implementeren (A-13)

De `error_widget` (`OverviewTableItem` met tekst "no results") wordt aangemaakt en de tekst wordt
ingesteld in `reset_ui()`, maar de widget wordt **nooit aan de tabel of layout toegevoegd**.
Daardoor is de melding onzichtbaar, zowel bij een initieel lege projectenlijst als bij lege
zoekresultaten.

Zie `docs/ambiguiteiten.md` A-13.

### Taken

- [ ] `otlmow_gui/GUI/screens/Home_elements/OverviewTable.py`
  - [ ] `error_widget` tonen wanneer `rowCount() == 0` na `fill_table()` en na `filter()`.
    - Optie A: een lege rij met de `error_widget` als span over alle kolommen invoegen.
    - Optie B: `setRowCount(1)` en `setSpan(0, 0, 1, columnCount())` met `error_widget` in cel (0,0).
  - [ ] `error_widget` verbergen wanneer `rowCount() > 0`.
  - [ ] Zorg dat `filter()` na verwijderen van alle rijen de melding toont.
- [ ] Verificatie
  - [ ] Initieel lege projectenlijst toont "geen resultaten" in de tabelzone.
  - [ ] Zoekopdracht zonder matches toont "geen resultaten".
  - [ ] Normale lijst met projecten toont geen melding.
  - [ ] Relevante tests draaien.

## Logs openen cross-platform (A-08)

"Open logs" gebruikt nu `explorer /select,...` (Windows-only). Wordt cross-platform gemaakt:
Windows/macOS selecteren het bestand; Linux opent de map (best-effort selectie).

Zie `docs/ambiguiteiten.md` A-08.

### Taken

- [ ] `otlmow_gui/GUI/header/HeaderBar.py`
  - [ ] Platformdetectie (`sys.platform` / `platform.system()`).
  - [ ] Windows: `explorer /select,<pad>` (huidig).
  - [ ] macOS: `open -R <pad>`.
  - [ ] Linux: `xdg-open <map>` (best-effort; waar mogelijk `--select`).
- [ ] Verificatie
  - [ ] Op Windows/macOS/Linux (of minimaal Windows + Linux) werkt "Open logs".
  - [ ] Relevante tests draaien.
