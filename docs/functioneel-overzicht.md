# Functioneel overzicht OTL Wizard 2

Dit document inventariseert de functionaliteiten van de OTLMOW-GUI (OTL Wizard 2) op basis van de
codebase, met als doel ze daarna om te zetten in Gherkin-scenario's. Per functionaliteit staan de
actoren, precondities, hoofdflow, Business Rules (BR), alternatieve flows en kandidaten voor
scenario's. De terminologie sluit aan bij de GUI en de code.

- Onderzochte versie: `1.3.0rc1` (`pyproject.toml`)
- Hoofdcode: `otlmow_gui/` (`Domain/`, `GUI/`, `Exceptions/`)
- Buiten scope van dit overzicht: build/installer, packaging, vertaalmechanisme (Babel), interne
  werking van de externe OTLMOW-bibliotheken, testfixtures en de map `LatestReleaseMulti/`.
- Gherkin-taal: scenario's kunnen in het Nederlands of Engels worden geschreven; gebruik de
  termen uit [Begrippen](#2-begrippen) consequent.

---

## 1. Actoren en systeemcontext

| Actor | Rol |
|---|---|
| Gebruiker / opdrachtnemer | Beheert projecten, maakt templates, valideert aanleverbestanden, beheert relaties, bekijkt visualisaties en exporteert data. |
| Beheerder / support | Gebruikt logbestanden, about- en foutmeldingsvensters. |
| DAVIE | Externe bron van bestaande relaties met AIM-ID's. Relaties worden niet live opgehaald; ze zitten in de aangeleverde bestanden. |
| GitHub (OTLMOW-GUI / OTLMOW-Model) | Bron voor updatecontrole en het verversen van de `otlmow_model`-bibliotheek. |
| FDO Toolbox | Externe Windows-tool voor SDF-conversie (SDF naar CSV en subset/XSD naar SDF). |

Systeemcontext:

```text
Home (projecten) -> Stap 1 template -> Stap 2 data inladen/valideren
                  -> Stap 3 relaties | data-visualisatie (tabs)
                  -> Stap 4 exporteren
```

Stap 3 en 4 zijn pas bruikbaar als alle projectbestanden bestaan en de status `OK` hebben.

---

## 2. Begrippen

| Term | Betekenis in de applicatie |
|---|---|
| Project | Werkmap onder `~/OTLWizardProjects/Projects/<eigen referentie>` met metadata, subset, projectbestanden, quick saves en visualisaties. |
| Eigen referentie | Door gebruiker gekozen unieke projectnaam; tevens mapnaam. |
| Bestek / service order | Vrij tekstveld met de opdrachtreferentie. |
| Subset | SQLite-databank (`.db`) die het toegestane OTL-model/classebereik bepaalt. |
| OTL-asset | Concreet OTL-object (AIM-object) met `assetId.identificator`. |
| Agent | OTL-object met `agentId` in plaats van `assetId`; geen gewone AIM-asset. |
| Relatie | `RelatieObject` met bron- en doelasset, richting en `isActief`. |
| AIM-ID | Identificator van een bestaande DAVIE-relatie; herkenbaar aan de opbouw uuid + base64-typeURI. |
| Aanlevertemplate | Door de gebruiker in te vullen template met OTL-klassen. |
| Infotemplate | Template met attribuutinformatie (voor informdoeleinden). |
| Quick save | Automatische JSON-snapshot van de gevalideerde assets en relaties. |
| `.otlw` | ZIP-bestand met een volledig project (delen/importeren). |
| DAVIE-conform template | Template zonder extra attribuutinfo/deprecated-markering, klaar voor DAVIE. |
| Uitgebreide info | Templatevariant met attribuutbeschrijving en deprecated-markering. |
| Geldig projectbestand | Bestand met `FileState.OK` na validatie. |
| Visualisatie | Interactieve HTML-graaf van assets en actieve relaties. |

---

## 3. Hoofdflow (happy path)

1. Gebruiker start de applicatie; de projectenlijst verschijnt op Home.
2. Gebruiker maakt een project aan (eigen referentie, bestek, subset) of opent/importeert een project.
3. In stap 1 selecteert hij klassen en genereert hij een aanlevertemplate.
4. Hij vult het template extern in en voegt het in stap 2 toe.
5. Hij valideert de bestanden; bij succes worden stap 3 en 4 ontgrendeld.
6. In stap 3 controleert hij relaties, voegt hij relaties/externe assets toe of verwijdert hij ze.
7. Optioneel bekijkt/regenerate hij de datavisualisatie en bewaart hij ze.
8. In stap 4 exporteert hij alle data of enkel de gewijzigde data.
9. Hij gaat terug naar Home; het project blijft lokaal bewaard met quick saves.

---

## 4. Feature-catalogus

### F-APP-01 Applicatiestart en updatecontrole

**Doel:** applicatie opstarten met geldige instellingen, logging en actuele OTLMOW-modelbibliotheek.

**Precondities:** applicatiebestanden aanwezig; optioneel internet.

**Hoofdflow**
1. `Settings.get_or_create_settings_file()` leest of maakt `settings.json` in `~/OTLWizardProjects`.
2. `OTLLogger` wordt geïnitialiseerd.
3. Bij opstart wordt gecontroleerd of een nieuwe OTL Wizard-versie beschikbaar is (GitHub `pyproject.toml`).
4. De `otlmow_model`-bibliotheek wordt gecontroleerd en indien verouderd vervangen door de GitHub-versie.
5. De hoofdvenster start op Home; bij een beschikbare update verschijnt een update-suggestie.

**Business Rules**
- BR-APP-01: Een netwerkfout bij updatecontrole mag het opstarten niet blokkeren; de fout wordt gelogd.
- BR-APP-02: Een verouderd `otlmow_model` leidt tot een waarschuwing/suggestie, niet tot een crash.
- BR-APP-03: De applicatie opent standaard Nederlandstalig als er geen geldige taalinstelling is.

**Scenario-kandidaten**
- Opstarten zonder beschikbare updates.
- Opstarten met een nieuwe Wizard-versie: suggestie verschijnt.
- Opstarten met verouderd OTL-model: modelsuggestie verschijnt.
- Opstarten zonder internet: applicatie start en logt de fout.

**Bron:** `wizard_main.py:132`, `Domain/Settings.py:62`, `Domain/network/Updater.py:36`, `GUI/screens/HomeScreen.py:67`.

---

### F-APP-02 Taal, instellingen en help

**Doel:** taal wijzigen en hulp-/informatiefuncties gebruiken.

**Hoofdflow**
1. Gebruiker klikt op het tandwiel in de header.
2. Kiest Nederlands of Engels.
3. De taal wordt in `settings.json` opgeslagen.
4. Een melding vraagt de applicatie opnieuw te starten.
5. Via het helpmenu kan de gebruiker de wiki openen, "About" bekijken, een fout melden of de logmap openen.

**Business Rules**
- BR-SET-01: Een taalwijziging wordt pas actief na herstart.
- BR-SET-02: Ontbrekende vertaalbestanden vallen terug op de originele tekst (identity translation).
- BR-SET-03: "About" toont de applicatieversie en contactgegevens; "Report error" toont het contactadres van Team BIM.
- BR-SET-04: "Logs" opent de nieuwste logfile in de systeemverkenner (Windows-specifiek).

**Scenario-kandidaten**
- Wijzigen naar Engels leidt tot herstartmelding en opgeslagen taal.
- Ontbrekende vertaling valt terug op de brontaal.
- About toont de juiste versie.
- Logs openen op een niet-Windows-systeem faalt gracefully/wordt gelogd. *(Open punt)*

**Bron:** `GUI/header/HeaderBar.py:135`, `GUI/dialog_windows/LanguageWindow.py:15`, `Domain/Settings.py:108`, `GUI/dialog_windows/MenuActionsWindow.py:11`.

---

### F-APP-03 Navigatie, stepper en schermopbouw

**Doel:** tussen de processtappen navigeren en de juiste schermen tonen.

**Hoofdflow**
1. Home toont de projectenlijst.
2. Een project opent een scherm met header, stepper (stap 1-4) en tabs.
3. Stap 1 heeft tabs "aanlevertemplate" en "infotemplate".
4. Stap 3 heeft tabs "relation_change" en "data visuals".
5. Stap 4 heeft één tab "export_data".
6. Bij wisselen van stap wordt de domeinstate naar de frontend gesynchroniseerd.

**Business Rules**
- BR-UI-01: Zonder geopend project zijn stap 1-4 niet zinvol bereikbaar; Home blijft de start.
- BR-UI-02: Stap 3 en 4 zijn uitgeschakeld als er geen geldige projectbestanden zijn of als minstens één bestand niet `OK` is.
- BR-UI-03: Bij het openen van stap 3 of 4 worden de lijsten/het exportscherm verversd vanuit de domeinlaag.
- BR-UI-04: Er is altijd een terugkeeractie naar Home.

**Scenario-kandidaten**
- Project openen zonder bestanden: stap 3/4 zijn uitgeschakeld.
- Alle bestanden valideren: stap 3/4 worden actief.
- Eén bestand op ERROR: stap 3/4 worden opnieuw uitgeschakeld.
- Tabs wisselen behoudt de geselecteerde klassen/relaties.

**Bron:** `GUI/MainWindow.py:31`, `GUI/header/StepperWidget.py:57`, `GUI/header/TabWidget.py:16`.

---

### F-APP-04 Terug naar Home en applicatie sluiten

**Doel:** project verlaten of applicatie sluiten zonder onopgeslagen graafwijzigingen te verliezen.

**Hoofdflow**
1. Gebruiker klikt "terug naar home" of sluit het venster.
2. Als de visualisatie onopgeslagen wijzigingen heeft, verschijnt een waarschuwing met "Continue"/"Back".
3. Bij "Continue" wordt het project verlaten/afgesloten; bij "Back" blijft de gebruiker in de applicatie.
4. Bij terugkeer naar Home wordt het huidige project losgekoppeld en de modelbuilder uit geheugen verwijderd.

**Business Rules**
- BR-UI-05: De waarschuwing verschijnt alleen als een project open is en `graph_saved_status == False`.
- BR-UI-06: Annuleren/Back mag het sluiten of navigeren tegenhouden.
- BR-UI-07: Bij sluiten worden lopende asynchrone taken geannuleerd.
- BR-UI-08: Bij terugkeer naar Home worden gecachte exportbestandsnamen gereset.

**Scenario-kandidaten**
- Sluiten zonder onopgeslagen graaf: applicatie sluit.
- Sluiten met onopgeslagen graaf en "Back": applicatie blijft open.
- Terug naar Home met onopgeslagen graaf en "Continue": project wordt gesloten.
- Terug naar Home zonder project: direct naar Home.

**Bron:** `GUI/MainWindow.py:101`, `GUI/header/TabWidget.py:61`.

---

### F-PROJ-01 Projectenoverzicht, zoeken en sorteren (Home)

**Doel:** bestaande projecten vinden en openen.

**Hoofdflow**
1. Home toont per project: eigen referentie, bestek, subsetnaam, laatst bewerkt en acties (bewerken, verwijderen, delen).
2. De tabel sorteert standaard dalend op "laatst bewerkt".
3. Zoektekst filtert op eigen referentie, bestek, subset en datum; overeenkomende cellen worden gemarkeerd en niet-overeenkomende rijen verdwijnen.
4. Dubbelklikken op een rij opent het project.
5. Wissen van de zoektekst toont opnieuw alle projecten.

**Business Rules**
- BR-PROJ-01: Zoeken is case-insensitive en werkt als substring op de vier zichtbare gegevenskolommen.
- BR-PROJ-02: Een nieuw aangemaakt of geïmporteerd project wordt visueel gemarkeerd.
- BR-PROJ-03: De actieknoppen staan per rij en beïnvloeden alleen dat project.

**Scenario-kandidaten**
- Projecten worden dalend op laatste wijziging getoond.
- Zoeken op bestek verbergt niet-matchende projecten.
- Zoeken op subset toont het juiste project.
- Wissen van de zoektekst herstelt de volledige lijst.
- Dubbelklikken opent het project.

**Bron:** `GUI/screens/Home_elements/OverviewTable.py:91`, `GUI/screens/HomeScreen.py:130`.

---

### F-PROJ-02 Project aanmaken

**Doel:** een nieuw project met subset aanmaken.

**Precondities:** gebruiker op Home.

**Hoofdflow**
1. Gebruiker klikt "Nieuw project".
2. Vult eigen referentie en bestek in en kiest een subsetbestand via de bestandskiezer.
3. Bij "Submit" worden de velden gevalideerd.
4. Bij geldige invoer wordt de projectmap aangemaakt, de subset ernaar gekopieerd en `project_details.json` geschreven.
5. Het project verschijnt in de lijst en is gemarkeerd als laatst toegevoegd.

**Business Rules**
- BR-PROJ-04: Eigen referentie, bestek en subsetpad mogen niet leeg zijn.
- BR-PROJ-05: De subset moet een geldige SQLite-subsetdatabank zijn; anders verschijnt een foutmelding.
- BR-PROJ-06: Een bestaande projectmap met dezelfde eigen referentie geeft een "Project bestaat al"-melding en blokkeert aanmaken.
- BR-PROJ-07: De subset wordt in de projectmap gekopieerd, zodat het project zelfstandig is.
- BR-PROJ-08: De laatst gekozen subsetmap wordt onthouden voor de volgende keuze.

**Scenario-kandidaten**
- Geldig project aanmaken.
- Lege eigen referentie: foutmelding, geen project.
- Leeg bestek: foutmelding.
- Geen subset gekozen: foutmelding.
- Ongeldige database: foutmelding.
- Bestaande projectnaam: melding en geen overschrijving.
- Subset wordt lokaal gekopieerd.

**Bron:** `GUI/dialog_windows/UpsertProjectWindow.py:21`, `Domain/step_domain/HomeDomain.py:85`, `Domain/project/Project.py:165`.

---

### F-PROJ-03 Project bewerken

**Doel:** eigen referentie, bestek of subset van een bestaand project wijzigen.

**Hoofdflow**
1. Gebruiker klikt het potlood bij een project.
2. Het dialoogvenster opent met de huidige waarden.
3. Bij een nieuwe eigen referentie wordt de projectmap hernoemd.
4. Bestek en/of subset worden bijgewerkt; de laatste wijzigingsdatum wordt geactualiseerd.
5. Bij een subsetswijziging worden template- en relatiedata opnieuw opgebouwd.

**Business Rules**
- BR-PROJ-09: Een nieuwe eigen referentie die al bestaat, geeft een fout en er wordt niets hernoemd.
- BR-PROJ-10: Een ongeldige subset wordt geweigerd; de bestaande subset blijft behouden.
- BR-PROJ-11: Na een subsetswijziging worden de klassenlijst en relatiemogelijkheden opnieuw geladen.
- BR-PROJ-12: Het wijzigen van de eigen referentie werkt ook het subsetpad bij wanneer de subset in de oude projectmap stond.

**Scenario-kandidaten**
- Bestek wijzigen.
- Subset wijzigen naar geldige database.
- Subset wijzigen naar ongeldige database: fout en ongewijzigd.
- Eigen referentie wijzigen: map wordt hernoemd.
- Eigen referentie wijzigen naar bestaande naam: fout.

**Bron:** `Domain/step_domain/HomeDomain.py:219`, `Domain/project/Project.py:1135`, `Domain/project/Project.py:1161`.

---

### F-PROJ-04 Project verwijderen

**Doel:** een project definitief verwijderen.

**Hoofdflow**
1. Gebruiker klikt het vuilnisbakicoon.
2. Een bevestigingsvenster met "Ja/Nee" verschijnt.
3. Bij "Ja" wordt de volledige projectmap verwijderd en de lijst ververst.
4. Bij "Nee" gebeurt er niets.

**Business Rules**
- BR-PROJ-13: Verwijderen is definitief en verwijdert de projectmap met alle bestanden en quick saves.
- BR-PROJ-14: Zonder expliciete bevestiging wordt niets verwijderd.

**Scenario-kandidaten**
- Verwijderen bevestigen: project verdwijnt uit de lijst en van schijf.
- Verwijderen annuleren: project blijft bestaan.

**Bron:** `GUI/dialog_windows/RemoveProjectWindow.py:9`, `Domain/step_domain/HomeDomain.py:66`.

---

### F-PROJ-05 Project importeren

**Doel:** een gedeeld `.otlw`-project importeren.

**Hoofdflow**
1. Gebruiker klikt "Import" in de header.
2. Kiest een `.otlw`-bestand.
3. Het archief wordt uitgepakt in `~/OTLWizardProjects/Projects/<eigen referentie>`.
4. Het project wordt geladen, aan de lijst toegevoegd en gemarkeerd.

**Business Rules**
- BR-PROJ-15: Als de projectmap al bestaat, wordt de import geweigerd met een melding.
- BR-PROJ-16: Na import worden de projecten opnieuw van schijf geladen.

**Scenario-kandidaten**
- Geldig `.otlw` importeren.
- Importeren van een project met bestaande naam: melding, niets uitgepakt.
- Ongeldig bestand: fout wordt getoond/afgehandeld. *(Foutafhandeling is nog TODO in code)*

**Bron:** `GUI/header/HeaderBar.py:250`, `Domain/project/Project.py:566`.

---

### F-PROJ-06 Project exporteren/delen

**Doel:** een project als `.otlw` bestand delen.

**Hoofdflow**
1. Gebruiker klikt het deelicoon bij een project.
2. Kiest een opslaglocatie; extensie `.otlw` wordt afgedwongen.
3. Het ZIP-bestand wordt aangemaakt en de verkenner opent op het bestand.

**Inhoud van het `.otlw`-bestand**
- `project_details.json`
- `saved_documents.json` (indien aanwezig)
- de subset-databank
- alle bestaande projectbestanden
- de laatste quick save (indien aanwezig)
- de visualisatie-HTML en de bijhorende support-JSON (indien aanwezig)

**Business Rules**
- BR-PROJ-17: Ontbrekende projectbestanden geven een waarschuwing met de vraag of de gebruiker toch wil exporteren.
- BR-PROJ-18: Alleen de laatste quick save wordt meegenomen, niet de volledige quick-savehistoriek.
- BR-PROJ-19: Niet-bestaande bestanden worden niet in het archief opgenomen.

**Scenario-kandidaten**
- Exporteren zonder ontbrekende bestanden.
- Exporteren met ontbrekende bestanden en "Ja".
- Exporteren met ontbrekende bestanden en "Nee": geen export.
- Extensie wordt automatisch `.otlw`.
- Archief bevat subset, projectbestanden en laatste quick save.

**Bron:** `GUI/screens/Home_elements/OverviewTable.py:186`, `Domain/project/Project.py:499`.

---

### F-PROJ-07 Project openen en projectstate

**Doel:** een project laden en alle domeinen initialiseren.

**Hoofdflow**
1. Gebruiker dubbelklikt op een project.
2. Het project wordt als `current_project` gezet.
3. De lijst met opgeslagen projectbestanden wordt geladen.
4. Template-, insert- en relatiedomeinen worden geïnitialiseerd.
5. De gefilterde exportstate wordt gewist.
6. De visualisatie wordt geïnformeerd dat er een projectwissel was.
7. De stepper wordt geëvalueerd op basis van de bestandsstatussen.

**Business Rules**
- BR-PROJ-20: Een project opent alleen als de projectmetadata en subset beschikbaar zijn.
- BR-PROJ-21: Bestanden die als `OK` opgeslagen zijn maar waarvoor geen quick save bestaat, worden op `WARNING` gezet.
- BR-PROJ-22: Bij het openen worden alle projectbestanden gecontroleerd op bestaan; ontbrekende bestanden worden als fout gemarkeerd.

**Scenario-kandidaten**
- Project met geldige bestanden openen: stap 3/4 beschikbaar.
- Project met ontbrekend bestand openen: bestand wordt fout gemarkeerd.
- Project met status OK maar zonder quick save: status wordt WARNING.
- Project openen initialiseert de visualisatie opnieuw.

**Bron:** `Domain/step_domain/HomeDomain.py:185`, `Domain/project/Project.py:716`, `Domain/project/Project.py:788`.

---

### F-PROJ-08 Quick saves (automatisch bewaren en herstellen)

**Doel:** werk van de gebruiker automatisch en herstartbaar bewaren.

**Hoofdflow**
1. Na een geslaagde validatie of een relatiewijziging wordt automatisch een quick save gemaakt.
2. De quick save is een JSON-bestand in `<project>/quick_saves/quick_save-<yymmdd>_<HHMMSS>.json`.
3. `project_details.json` onthoudt de laatste quick save.
4. Bij openen van het project worden de laatste gevalideerde assets uit de quick save geladen.
5. Quick saves ouder dan 7 dagen worden verwijderd.

**Business Rules**
- BR-PROJ-23: Quick saves bevatten de getoonde objecten (inclusief externe assets/agents) en de persistente relaties.
- BR-PROJ-24: Bestanden die niet het standaardnaamformaat hebben, worden nooit automatisch verwijderd.
- BR-PROJ-25: De header toont een save-animatie/laatste-save-indicator tijdens het bewaren.
- BR-PROJ-26: Een bestaande quick save veroorzaakt bij hervalidatie een waarschuwing dat eerdere wijzigingen overschreven kunnen worden.

**Scenario-kandidaten**
- Succesvolle validatie maakt een quick save.
- Relatie toevoegen/verwijderen maakt een quick save.
- Heropenen van het project herstelt de laatste quick save.
- Quick saves ouder dan 7 dagen worden verwijderd.
- Afwijkend bestandsnaamformaat blijft bewaard.
- Hervalidatie met bestaande quick save vraagt bevestiging.

**Bron:** `Domain/project/Project.py:388`, `Domain/project/Project.py:460`, `Domain/step_domain/RelationChangeDomain.py:35`, `GUI/dialog_windows/RevalidateDocumentsWindow.py:7`.

---

### F-PROJ-09 Subset wijzigen

**Doel:** een project aan een andere subset koppelen.

**Toegang:** stap 1 (aanlevertemplate en infotemplate) via "Subset wijzigen".

**Hoofdflow**
1. Gebruiker opent het subsetvenster; huidige subset staat vooringevuld.
2. Kiest een nieuwe `.db`.
3. Bij "Submit" wordt de database gevalideerd.
4. Bij geldigheid wordt de subset gewijzigd, de modelbuilder vernieuwd en het model
   (`TemplateDomain`) en de relaties (`RelationChangeDomain`) opnieuw geïnitialiseerd.
5. De UI wordt gereset.

**Business Rules**
- BR-PROJ-27: Een ongeldige of niet-bestaande database wordt geweigerd; de oude subset blijft actief.
- BR-PROJ-28: De wijziging wordt in de projectmetadata bewaard en de laatste wijzigingsdatum wordt bijgewerkt.
- BR-PROJ-29: De subsetkeuze start in de map van de huidige subset of de laatst gebruikte subsetmap.

**Scenario-kandidaten**
- Geldige subset kiezen: klassenlijst en relaties worden vernieuwd.
- Ongeldige subset kiezen: foutmelding, oude subset blijft.
- Annuleren: geen wijziging.

**Bron:** `GUI/dialog_windows/ChangeSubsetWindow.py:14`, `Domain/step_domain/HomeDomain.py:126`, `Domain/project/Project.py:1115`.

---

### F-TPL-01 Klassenlijst en klassenselectie

**Doel:** bepalen voor welke OTL-klassen een template wordt gemaakt.

**Hoofdflow**
1. Bij openen van stap 1 worden de klassen uit de subset geladen.
2. Relatieklassen en abstracte klassen worden eruit gefilterd.
3. De klassen worden alfabetisch getoond, gegroepeerd per klassenaam.
4. Standaard zijn alle klassen geselecteerd.
5. De gebruiker kan "Alles selecteren" aan/uit zetten, individueel selecteren of dubbelklikken.
6. De teller toont het aantal geselecteerde klassen; bij 0 is exporteren uitgeschakeld.

**Business Rules**
- BR-TPL-01: De klasse "Agent" wordt getoond maar is niet selecteerbaar; ze wordt niet in een template opgenomen.
- BR-TPL-02: De klassenlijst wordt uit de geselecteerde subset gehaald, niet uit het volledige OTL-model.
- BR-TPL-03: Selectie is gedeeld tussen de tabbladen "aanlevertemplate" en "infotemplate".
- BR-TPL-04: Bij een subsetswijziging wordt de lijst volledig opnieuw geladen.
- BR-TPL-05: Als de subset geen klassen oplevert, toont de lijst een "geen klassen gevonden"-melding.
- BR-TPL-06: Een minimale selectie van één klasse is nodig om te exporteren.

**Scenario-kandidaten**
- Openen van stap 1 vult de klassenlijst uit de subset.
- Standaard zijn alle klassen geselecteerd.
- Agent is zichtbaar maar niet selecteerbaar.
- Alles deselecteren schakelt de exportknop uit.
- Eén klasse selecteren schakelt de exportknop in.
- Subset zonder klassen toont de juiste melding.
- Selectie in de ene tab wordt weerspiegeld in de andere tab.

**Bron:** `Domain/step_domain/TemplateDomain.py:115`, `GUI/screens/TemplateScreen.py:908`, `GUI/screens/InfoTemplateScreen.py:266`.

---

### F-TPL-02 Template-opties en formaatbeperkingen

**Doel:** het juiste templateformaat en de juiste inhoud kiezen.

**Opties**
- Bestandstype: `Excel`, `CSV`, en op Windows ook `SDF`. (`JSON` en `GeoJSON` worden niet aangeboden voor templatecreatie.)
- Templateformaat: `DAVIE conform` (standaard) of `Expanded info`.
- `Keuzelijsten toevoegen`.
- `Geometrie-attributen toevoegen`.
- `Voorbeeldassets toevoegen` met aantal 1-100.

De checkbox `Toon deprecated attributen` bestaat in de code maar wordt nooit aan een layout
toegevoegd en is dus niet zichtbaar in de GUI (zie A-01).

**Per formaat (volgens `TemplateScreen.file_type_settings`)**

| Formaat | Keuzelijsten | Geometrie | Voorbeelden | Uitgebreide info |
|---|---|---|---|---|
| Excel | aan/uit, standaard aan | aan/uit, standaard aan | aan/uit, standaard uit | aan/uit, standaard uit |
| CSV | uitgeschakeld | aan/uit, standaard aan | aan/uit, standaard aan | aan/uit, standaard uit |
| SDF | uitgeschakeld, altijd aan | uitgeschakeld, altijd aan | uitgeschakeld, altijd uit | uitgeschakeld |

**Business Rules**
- BR-TPL-07: Bij formaatwissel worden de opties ingesteld volgens de tabel en voorzien van een tooltip.
- BR-TPL-08: Een optie die voor een formaat niet ondersteund wordt, is uitgeschakeld.
- BR-TPL-09: "DAVIE conform" zet attribuutbeschrijving en deprecated-markering uit; "Expanded info" zet beide aan.
- BR-TPL-10: De hoeveelheid voorbeelden telt alleen als "Voorbeeldassets toevoegen" aangevinkt is; anders is het aantal 0.
- BR-TPL-11: Voor SDF worden keuzelijsten en geometrie altijd toegevoegd.

**Scenario-kandidaten**
- Wisselen naar CSV past de opties aan.
- Wisselen naar SDF schakelt keuzelijsten/geometrie uit maar houdt ze aan.
- DAVIE-conform levert geen attribuutinfo/deprecated-markering.
- Expanded info levert beide wel.
- Aantal voorbeelden 0 wanneer de checkbox uit staat.
- Aantal voorbeelden buiten 1-100 kan niet worden ingesteld.

**Bron:** `GUI/screens/TemplateScreen.py:98`, `GUI/screens/TemplateScreen.py:776`, `GUI/screens/TemplateScreen.py:748`.

---

### F-TPL-03 Aanlevertemplate genereren

**Doel:** een templatebestand genereren op basis van de subset en de selectie.

**Hoofdflow**
1. Gebruiker klikt "Exporteer".
2. Kiest formaat en opslaglocatie.
3. De applicatie genereert asynchroon een template met de geselecteerde klassen en opties.
4. Na succes wordt het bestand geopend (Excel) of de map met het bestand getoond.

**Business Rules**
- BR-TPL-12: De template wordt gegenereerd uit de subset van het huidige project.
- BR-TPL-13: De Agent-klasse wordt altijd uit de selectie gefilterd.
- BR-TPL-14: Als er geen klassen geselecteerd zijn, start de export niet (knop uit).
- BR-TPL-15: Een bestand dat in Excel openstaat en niet beschrijfbaar is, geeft een toelichtende melding.
- BR-TPL-16: Generatiefouten worden gelogd en als fout aan de gebruiker getoond.
- BR-TPL-17: Excel-bestanden worden na creatie automatisch geopend; andere formaten openen de map.

**Scenario-kandidaten**
- Excel-template genereren met alle klassen.
- Template genereren met een subset van klassen.
- Template genereren met keuzelijsten/geometrie/voorbeelden.
- Export naar een bestand dat openstaat in Excel: melding.
- Genereren zonder geselecteerde klassen: niet mogelijk.
- Agent wordt niet in het template opgenomen.
- Na export opent het bestand of de map.

**Bron:** `Domain/step_domain/TemplateDomain.py:44`, `Domain/step_domain/TemplateDomain.py:196`, `GUI/screens/TemplateScreen.py:722`.

---

### F-TPL-04 Infotemplate genereren

**Doel:** een informatief template met attribuutinformatie genereren.

**Hoofdflow**
1. Gebruiker opent de tab "infotemplate".
2. Selecteert klassen (gedeelde selectie met aanlevertemplate).
3. Kiest opslaglocatie.
4. De applicatie genereert een infotemplate via `InfotemplateGenerator`.
5. De map met het bestand wordt geopend.

**Business Rules**
- BR-TPL-18: De infotemplate gebruikt dezelfde subset en klassenselectie als het aanlevertemplate.
- BR-TPL-19: Er zijn geen formaat-/voorbeeldopties; de generator bepaalt de uitgebreide inhoud.
- BR-TPL-20: Zonder selectie is exporteren uitgeschakeld.

**Scenario-kandidaten**
- Infotemplate genereren met geselecteerde klassen.
- Selectie wijzigen in de infotab beïnvloedt de aanlevertemplate-selectie.
- Infotemplate exporteren zonder selectie is niet mogelijk.

**Bron:** `GUI/screens/InfoTemplateScreen.py:218`, `Domain/step_domain/TemplateDomain.py:189`.

---

### F-TPL-05 SDF-ondersteuning

**Doel:** SDF-bestanden lezen en genereren (enkel Windows).

**Business Rules**
- BR-TPL-21: SDF is alleen beschikbaar als het platform Windows is.
- BR-TPL-22: Voor SDF is FDO Toolbox nodig; als die niet geïnstalleerd is, vraagt de applicatie om installatie en opent ze de installerlocatie.
- BR-TPL-23: SDF-generatie gebeurt door eerst een gefilterde XSD uit de subset te maken en die met FDO om te zetten naar SDF.
- BR-TPL-24: Bij het inlezen wordt een SDF opgesplitst in één CSV per klasse.
- BR-TPL-25: Het `FeatId`-attribuut wordt na SDF-conversie verwijderd.

**Scenario-kandidaten**
- SDF-formaat is niet beschikbaar op Linux/macOS.
- SDF genereren zonder FDO Toolbox vraagt installatie.
- SDF inladen splitst het bestand per klasse in CSV.
- SDF-objecten bevatten geen `FeatId` na inladen.

**Bron:** `Domain/global_vars.py:13`, `Domain/util/SDFHandler.py:114`, `Domain/util/SDFHandler.py:222`, `Domain/step_domain/InsertDataDomain.py:105`.

---

### F-DATA-01 Projectbestanden toevoegen en beheren

**Doel:** aanleverbestanden aan een project toevoegen en verwijderen.

**Hoofdflow**
1. Gebruiker klikt "Kies bestand" in stap 2 en selecteert één of meerdere bestanden.
2. Ondersteunde formaten: Excel (`.xls`, `.xlsx`), CSV, JSON, GeoJSON en (Windows) SDF.
3. Excel-bestanden worden ontdaan van de werkbladen `Keuzelijsten` en `dropdownvalues`.
4. Het bestand wordt naar de map `project_files` gekopieerd en in de lijst gezet met status `WARNING`.
5. Per bestand is er een verwijderknop.
6. "Reset" opent een bevestiging om alle projectbestanden te verwijderen.

**Business Rules**
- BR-DATA-01: Een bestand met een bestandsnaam die al in het project voorkomt, wordt geweigerd met een melding.
- BR-DATA-02: Een toegevoegd bestand heeft initieel status `WARNING` (nog niet gevalideerd).
- BR-DATA-03: De validatieknop is uitgeschakeld zolang er geen bestanden zijn.
- BR-DATA-04: Verwijderen van een bestand verwijdert het uit de projectlijst en van schijf.
- BR-DATA-05: Alle bestanden verwijderen vereist bevestiging en werkt `saved_documents.json` bij.
- BR-DATA-06: Een bestand dat niet verwijderd kan worden (bv. open in Excel) geeft een melding.

**Scenario-kandidaten**
- Meerdere bestanden toevoegen.
- Dubbel bestandsnaam toevoegen: melding en geen extra bestand.
- Excel toevoegen: dropdown-werkbladen worden verwijderd.
- Bestand verwijderen met de kruisknop.
- Alle bestanden verwijderen met bevestiging.
- Alle bestanden verwijderen annuleren.
- Bestand verwijderen dat openstaat in Excel: foutmelding.

**Bron:** `GUI/screens/InsertDataScreen.py:545`, `Domain/step_domain/InsertDataDomain.py:185`, `Domain/project/Project.py:951`, `Domain/project/Project.py:1030`.

---

### F-DATA-02 Bestanden valideren

**Doel:** controleren of alle bestanden OTL-conform zijn en klaar zijn voor relatiebeheer.

**Hoofdflow**
1. Gebruiker klikt "Valideer".
2. Als er een quick save bestaat, vraagt de applicatie om bevestiging (eerdere wijzigingen worden overschreven).
3. Ontbrekende projectbestanden worden gedetecteerd en gemeld; validatie stopt.
4. Elk bestand wordt ingelezen en omgezet naar OTL-objecten.
5. Objecten worden opgesplitst in assets en relaties.
6. Relaties worden gecontroleerd op bron/doel-typeURI's en geldigheid.
7. Meerdere voorkomens van hetzelfde asset-ID worden samengevoegd.
8. De bestandsstatus wordt `OK` of `ERROR` en opgeslagen.
9. Bij succes worden de objecten aan het relatiedomein doorgegeven en wordt een quick save gemaakt.
10. De UI toont een groene succesboodschap of een rode foutboodschap met details.

**Business Rules**
- BR-DATA-07: Validatie vereist minstens één projectbestand.
- BR-DATA-08: Een bestand met conversie- of OTL-fouten krijgt status `ERROR` en de fout wordt per document getoond.
- BR-DATA-09: Een lege `assetId.identificator` (of `agentId.identificator` voor Agent) is een fout.
- BR-DATA-10: Een relatie waarvan bron- of doel-TypeURI niet bestaat of niet geldig is voor het relatietype, is een fout.
- BR-DATA-11: Als het samenvoegen van dubbele assets mislukt door conflicterende waarden of types, wordt dit als fout gemeld en worden de betrokken bestanden ongeldig.
- BR-DATA-12: Zolang niet alle bestanden `OK` zijn, blijven stap 3 en 4 uitgeschakeld.
- BR-DATA-13: Een geslaagde validatie vervangt de inhoud van het relatiedomein en reset de visualisatiestatus.
- BR-DATA-14: Validatiefouten blokkeren het doorgeven van objecten aan stap 3.

**Scenario-kandidaten**
- Alle bestanden geldig: groene feedback, stap 3/4 actief, quick save gemaakt.
- Eén bestand met een OTL-fout: rode feedback, bestand ERROR, stap 3/4 blijven uit.
- Lege identificator: fout in de feedbacklijst.
- Relatie met onbestaande bron-TypeURI: fout.
- Relatie met onbestaande doel-TypeURI: fout.
- Relatie met ongeldige combinatie bron/doel/relatietype: fout.
- Twee rijen met hetzelfde asset-ID en aanvullende attributen: samengevoegd.
- Twee rijen met hetzelfde asset-ID en conflicterende waarden: fout.
- Validatie zonder bestanden: knop is uitgeschakeld.
- Hervalidatie met bestaande quick save: bevestiging vereist.
- Ontbrekend bestand vóór validatie: melding en geen validatie.

**Bron:** `Domain/step_domain/InsertDataDomain.py:320`, `Domain/step_domain/InsertDataDomain.py:450`, `Domain/util/CombineAssetHelper.py:17`, `GUI/screens/InsertDataScreen.py:179`.

---

### F-DATA-03 Feedback en foutrapportage na validatie

**Doel:** de gebruiker inzicht geven in resultaten en fouten.

**Hoofdflow**
1. Na validatie wordt de feedbacklijst leeggemaakt.
2. Bij fouten wordt per fout een regel met documentnaam en foutboodschap toegevoegd (rood).
3. Bij succes wordt per OTL-type het aantal ingeladen objecten getoond, plus het totaal aantal conforme objecten.
4. Bij fouten worden ook de reeds ingelezen objecten per type getoond, voor zover beschikbaar.

**Business Rules**
- BR-DATA-15: Foutboodschappen worden vertaald via `ValidationErrorReportTranslations`.
- BR-DATA-16: De feedback is read-only; corrigeren gebeurt in het bronbestand en daarna opnieuw valideren.
- BR-DATA-17: De status van elk bestand wordt met een icoon getoond: groen vinkje (`OK`), oranje waarschuwing (`WARNING`), rood kruis (`ERROR`).

**Scenario-kandidaten**
- Succes toont aantallen per type en totaal.
- Fout toont documentnaam en foutboodschap.
- Meerdere fouten in één bestand worden allemaal getoond.
- Statusiconen komen overeen met de bestandsstatus.

**Bron:** `GUI/screens/InsertDataScreen.py:239`, `GUI/screens/InsertDataScreen.py:749`, `GUI/screens/InsertDataScreen.py:780`, `Domain/enums.py:9`.

---

### F-REL-01 Relation-scherm: drie lijsten en attributenpaneel

**Doel:** assets en relaties overzichtelijk beheren.

**Hoofdflow**
1. Stap 3 toont drie kolommen: OTL-assets, mogelijke relaties en bestaande relaties.
2. Elke kolom heeft een zoekbalk, een lijst gegroepeerd per type en een attributenpaneel.
3. Elke groep toont het aantal items en, bij selectie, het aantal geselecteerde items.
4. Selectie in de eerste kolom bepaalt de inhoud van de tweede kolom.
5. Selectie in de tweede of derde kolom vult het bijhorende attributenpaneel.
6. Toegevoegde items worden gemarkeerd.

**Business Rules**
- BR-REL-01: Attributen zijn read-only; wijzigen gebeurt via de bronbestanden en hervalidatie.
- BR-REL-02: De eerste kolom toont alle getoonde objecten: interne assets, externe assets en Agent-objecten.
- BR-REL-03: De lijsten zijn gegroepeerd per (verkorte) TypeURI; de mapstate (open/dicht) blijft behouden bij verversen.
- BR-REL-04: Zoeken is case-insensitive en werkt op de zichtbare kolommen en de typenaam; bij zoeken worden mappen met treffers automatisch geopend.
- BR-REL-05: Een klik op een object vult automatisch de zoekbalk van de bestaande relaties met de objectnaam.
- BR-REL-06: Als een kaartvenster open is, wordt het geselecteerde object op de kaart gemarkeerd.

**Scenario-kandidaten**
- Scherm toont de drie kolommen met objecten.
- Object selecteren vult de mogelijke relaties en attributen.
- Zoeken in de objectenlijst op naam.
- Zoeken in de mogelijke relaties op TypeURI.
- Zoeken in de bestaande relaties op bron- of doelnaam.
- Wissen van zoektekst herstelt de volledige lijst.
- Aantal geselecteerde items verschijnt in de mapnaam.

**Bron:** `GUI/screens/RelationChangeScreen.py:247`, `GUI/screens/RelationChange_elements/AbstractInstanceListWidget.py:202`, `GUI/screens/RelationChange_elements/ObjectListWidget.py:36`.

---

### F-REL-02 Mogelijke relaties bepalen

**Doel:** tonen welke relaties tussen het geselecteerde object en andere objecten mogelijk zijn.

**Hoofdflow**
1. Bij selectie van een object worden de relatietypes bepaald op basis van het model.
2. Standaard gebeurt dit op basis van de subset (`OSLOCollector.find_all_concrete_relations`).
3. Als er externe assets, Agent-objecten of de volledige-OTL-modus actief zijn, wordt het volledige model gebruikt.
4. Per kandidaat-partner wordt een relatieobject aangemaakt, tenzij die relatie al bestaat.
5. Inactieve DAVIE-relaties worden ook als mogelijke relatie getoond.
6. Resultaten worden gesorteerd en per doeltype gegroepeerd.

**Business Rules**
- BR-REL-07: Het geselecteerde object zelf wordt nooit als mogelijke partner getoond.
- BR-REL-08: Reeds bestaande relaties worden niet als mogelijke relatie aangeboden.
- BR-REL-09: Richting (`Source -> Destination`, `Destination -> Source`, `Unspecified`) wordt gerespecteerd en met een pijlicoon getoond.
- BR-REL-10: Voor legacy-assets (`https://lgc...`) wordt een `HoortBij`-relatie naar concrete OTL-klassen aangeboden.
- BR-REL-11: Ontbrekende bron-/doelassets in bestaande relaties worden automatisch als externe asset aangemaakt.
- BR-REL-12: "Toon alle OTL-relaties" schakelt het zoeken in het volledige OTL-model in/uit en ververst de lijst.
- BR-REL-13: Als er geen object geselecteerd is, toont de lijst een plaatshouder.

**Scenario-kandidaten**
- Object selecteren toont mogelijke relaties uit de subset.
- Object zonder mogelijke relaties toont een lege/plaatshoudermelding.
- Externe asset aanwezig: relaties worden uit het volledige model gehaald.
- "Toon alle OTL-relaties" aanzetten verruimt de lijst.
- Bestaande relatie wordt niet opnieuw als mogelijk aangeboden.
- Legacy-asset biedt HoortBij aan.
- Ontbrekende relatiepartner wordt als externe asset toegevoegd.

**Bron:** `Domain/step_domain/RelationChangeDomain.py:550`, `Domain/step_domain/RelationChangeDomain.py:784`, `GUI/screens/RelationChange_elements/PossibleRelationListWidget.py:288`.

---

### F-REL-03 Relatie toevoegen

**Doel:** één of meerdere mogelijke relaties actief maken.

**Hoofdflow**
1. Gebruiker selecteert één of meerdere mogelijke relaties.
2. Klikt "Relatie toevoegen".
3. De relatie(s) verhuizen van de mogelijke naar de bestaande relaties en krijgen `isActief = True`.
4. De relatiemap wordt uitgeklapt en de toegevoegde items worden gemarkeerd.
5. De visualisatie wordt als verouderd gemarkeerd.
6. Er wordt een quick save gemaakt.

**Business Rules**
- BR-REL-14: Meerdere relaties kunnen in één actie worden toegevoegd.
- BR-REL-15: Als de selectie intussen verouderd is (lijst opnieuw opgebouwd), worden die items genegeerd.
- BR-REL-16: Een `HeeftBetrokkene`-relatie vraagt om een rolattribuut via een dialoogvenster.
- BR-REL-17: De knop is uitgeschakeld zonder selectie.
- BR-REL-18: Een toegevoegde relatie krijgt `toegekendDoor = "OTL_wizard_2"`.

**Scenario-kandidaten**
- Eén relatie toevoegen.
- Meerdere relaties tegelijk toevoegen.
- Relatie toevoegen zonder selectie: knop uit.
- HeeftBetrokkene toevoegen: roldialoog verschijnt.
- HeeftBetrokkene annuleren: geen relatie toegevoegd.
- Toevoegen maakt quick save en markeert visualisatie verouderd.
- Verouderde selectie wordt genegeerd.

**Bron:** `Domain/step_domain/RelationChangeDomain.py:1152`, `GUI/screens/RelationChange_elements/PossibleRelationListWidget.py:155`, `GUI/dialog_windows/DefineHeeftBetrokkeneRelationWindow.py:22`.

---

### F-REL-04 Relatie verwijderen

**Doel:** bestaande relaties deactiveren.

**Hoofdflow**
1. Gebruiker selecteert één of meerdere bestaande relaties.
2. Klikt "Relatie verwijderen".
3. De relatie wordt uit de actieve lijst gehaald en `isActief = False`.
4. De relatie komt terug als mogelijke relatie (behalve als ze een DAVIE/AIM-ID-relatie is; die blijft persistent maar inactief).
5. De visualisatie wordt verouderd gemarkeerd en er wordt een quick save gemaakt.

**Business Rules**
- BR-REL-19: Meerdere relaties kunnen in één actie worden verwijderd.
- BR-REL-20: Verwijderen verwijdert de relatie niet fysiek uit de data; ze wordt gedeactiveerd.
- BR-REL-21: Een gedeactiveerde AIM-ID-relatie blijft bewaard en wordt bij export/quicksave meegenomen.
- BR-REL-22: De knop is uitgeschakeld zonder selectie.
- BR-REL-23: Na verwijderen wordt de bijhorende relatiemap in de mogelijke relaties uitgeklapt.

**Scenario-kandidaten**
- Eén relatie verwijderen.
- Meerdere relaties verwijderen.
- Verwijderde gegenereerde relatie verschijnt terug bij mogelijke relaties.
- Verwijderde AIM-ID-relatie blijft inactief bewaard.
- Verwijderen zonder selectie: knop uit.
- Verwijderen maakt quick save en markeert visualisatie verouderd.

**Bron:** `Domain/step_domain/RelationChangeDomain.py:1293`, `GUI/screens/RelationChange_elements/ExistingRelationListWidget.py:129`.

---

### F-REL-05 Externe asset toevoegen

**Doel:** een asset toevoegen dat niet in de aangeleverde bestanden zit.

**Hoofdflow**
1. Gebruiker klikt "Externe asset toevoegen".
2. Vult een identificator/naam in en kiest een OTL-type uit een doorzoekbare lijst.
3. Bij "Submit" wordt de invoer gecontroleerd.
4. De asset wordt als extern object toegevoegd (of als Agent wanneer het type een `agentId` heeft).
5. De lijst en de relatiemogelijkheden worden ververst; er wordt een quick save gemaakt.

**Business Rules**
- BR-REL-24: De identificator/naam mag niet leeg zijn.
- BR-REL-25: Een bestaande identificator/naam mag niet opnieuw worden toegevoegd.
- BR-REL-26: Externe assets krijgen `assetId.toegekendDoor = "OTL_wizard_2"`.
- BR-REL-27: De keuzelijst bevat concrete OTL-assettypes, inclusief legacy-types, gesorteerd.
- BR-REL-28: Na toevoegen worden de relatiemogelijkheden opnieuw berekend (volledig model).

**Scenario-kandidaten**
- Geldige externe asset toevoegen.
- Lege naam: foutmelding.
- Bestaande naam: foutmelding.
- Agent-type toevoegen: wordt als Agent behandeld.
- Toevoegen maakt quick save.
- Nieuwe externe asset verschijnt in de eerste kolom.

**Bron:** `GUI/dialog_windows/AddExternalAssetWindow.py:23`, `Domain/step_domain/RelationChangeDomain.py:1516`, `Domain/util/Helpers.py:38`.

---

### F-REL-06 HeeftBetrokkene-rol definiëren

**Doel:** bij een `HeeftBetrokkene`-relatie de verplichte rol invullen.

**Hoofdflow**
1. Bij toevoegen van een `HeeftBetrokkene`-relatie verschijnt een dialoogvenster.
2. De gebruiker kiest een rol uit `KlBetrokkenheidRol` (enkel opties met status "ingebruik").
3. Bij "Submit" krijgen alle geselecteerde HeeftBetrokkene-relaties die rol en worden ze toegevoegd.
4. Bij annuleren worden de relaties niet toegevoegd en wordt de UI ververst.

**Business Rules**
- BR-REL-29: De rol is verplicht voor HeeftBetrokkene-relaties.
- BR-REL-30: Enkel rollen met status "ingebruik" zijn selecteerbaar.
- BR-REL-31: De dialoog kan één of meerdere relaties tegelijk verwerken.
- BR-REL-32: Het venster toont de betrokken bron- en doelidentificatoren.

**Scenario-kandidaten**
- HeeftBetrokkene toevoegen met gekozen rol.
- Meerdere HeeftBetrokkene-relaties in één keer voorzien van een rol.
- Annuleren voegt niets toe.
- Buiten gebruik zijnde rol is niet selecteerbaar.

**Bron:** `GUI/dialog_windows/DefineHeeftBetrokkeneRelationWindow.py:35`, `Domain/step_domain/RelationChangeDomain.py:1177`.

---

### F-REL-07 DAVIE/AIM-ID-relaties

**Doel:** correct omgaan met relaties die al in DAVIE bestaan.

**Business Rules**
- BR-REL-33: Een relatie waarvan de identificator een AIM-ID is, wordt als DAVIE-relatie beschouwd.
- BR-REL-34: Actieve DAVIE-relaties worden bij de bestaande relaties getoond.
- BR-REL-35: Inactieve DAVIE-relaties worden als mogelijke relatie aangeboden.
- BR-REL-36: Bij export en quick save worden actieve relaties plus inactieve DAVIE-relaties bewaard.
- BR-REL-37: Bij verwijderen van een DAVIE-relatie blijft ze als inactief record bestaan.

**Scenario-kandidaten**
- Actieve AIM-ID-relatie verschijnt bij bestaande relaties.
- Inactieve AIM-ID-relatie verschijnt bij mogelijke relaties.
- AIM-ID-relatie verwijderen: blijft inactief bewaard.
- Export bevat actieve en inactieve DAVIE-relaties.

**Bron:** `Domain/step_domain/RelationChangeDomain.py:340`, `Domain/step_domain/RelationChangeDomain.py:1411`, `Domain/step_domain/RelationChangeDomain.py:1474`.

---

### F-MAP-01 Kaartvisualisatie van assets

**Doel:** de geografische ligging van de getoonde assets bekijken en van daaruit selecteren.

**Hoofdflow**
1. Gebruiker klikt de kaartknop naast de relatielijsten.
2. Een kaartvenster opent met de assets uit de eerste kolom.
3. De kaart wordt gegenereerd met Folium en in een webview getoond.
4. Een klik op een asset op de kaart selecteert die asset in het relatenscherm.
5. Een klik op een asset in de lijst markeert die asset op de kaart.
6. Met "Refresh" wordt de kaart opnieuw opgebouwd.

**Business Rules**
- BR-MAP-01: De kaart gebruikt de huidige, gefilterde inhoud van de eerste kolom.
- BR-MAP-02: Boven 300 objecten wordt geen kaart getoond maar een limietmelding.
- BR-MAP-03: Bij geopende kaart wordt een selectie in de lijst automatisch gemarkeerd.
- BR-MAP-04: Een selectie op de kaart werkt de objectselectie en relatiepanelen bij.
- BR-MAP-05: Sluiten van de kaart reset de referentie in het relatenscherm.

**Scenario-kandidaten**
- Kaart openen met assets.
- Kaart openen met meer dan 300 assets: limietmelding.
- Asset op de kaart aanklikken selecteert het in de lijst.
- Asset in de lijst aanklikken markeert het op de kaart.
- Kaart verversen na relatie-/assetwijziging.
- Kaart sluiten en opnieuw openen.

**Bron:** `GUI/screens/MapScreen.py:72`, `GUI/screens/RelationChangeScreen.py:485`, `GUI/screens/Map_elements/MapHelper.py:20`.

---

### F-VIS-01 Datavisualisatie genereren en bekijken

**Doel:** een interactieve graaf van assets en actieve relaties maken.

**Hoofdflow**
1. Gebruiker opent de tab "data visuals".
2. Bij een nieuw/gewijzigd project wordt de graaf opgebouwd uit de actieve objecten en relaties.
3. De graaf wordt als HTML bewaard in de map `visuals` van het project.
4. De HTML wordt in een webview geladen.
5. De gebruiker kan de graaf verkennen (slepen, selecteren, relatiepijlen verslepen).

**Business Rules**
- BR-VIS-01: Enkel actieve objecten en relaties worden in de visualisatie opgenomen.
- BR-VIS-02: De visualisatie wordt bewaard per project en hergebruikt bij heropenen.
- BR-VIS-03: Zonder bestaande HTML wordt de view leeggemaakt en wordt een volledige regeneratie gevraagd.
- BR-VIS-04: Boven 100 000 objecten wordt geen graaf getoond maar een limietmelding (praktisch zeldzaam).
- BR-VIS-05: Bij projectwissel wordt de bestaande HTML geladen of de view geleegd.

**Scenario-kandidaten**
- Visualisatie openen voor een project met bestaande HTML.
- Visualisatie openen voor een project zonder HTML: lege view en regeneratie nodig.
- Graaf bevat enkel actieve relaties.
- Limietmelding bij te veel objecten.

**Bron:** `GUI/screens/DynamicDataVisualisationScreen.py:381`, `GUI/screens/DynamicDataVisualisationScreen.py:488`, `GUI/screens/DataVisualisation_elements/VisualisationHelper.py:15`.

---

### F-VIS-02 Visualisatie-opties en legende

**Doel:** de weergave van de graaf aanpassen.

**Opties**
- Visualisatiemodus: hiërarchisch, spinnenweb, shell, ForceAtlas2-based.
- Collectiedrempel: slider; relaties naar dezelfde asset worden gebundeld vanaf de drempel.
- Legende per relatietype met aan/uit-checkbox en kleur.
- Help met muisbediening.
- Knop om de HTML-locatie te openen.

**Business Rules**
- BR-VIS-06: Een wijziging van modus of drempel markeert de visualisatie als verouderd; de gebruiker moet regenereren.
- BR-VIS-07: De drempelslider wordt begrensd door het aantal getoonde assets + 1; op het maximum toont het label "uit".
- BR-VIS-08: De legende toont enkel relatietypes die in de huidige data voorkomen.
- BR-VIS-09: Een legendavinkje verbergt/toont alle relaties van dat type in de graaf.
- BR-VIS-10: De legende moet de aangevinkte status behouden bij verversen.

**Scenario-kandidaten**
- Modus wijzigen markeert de graaf als verouderd.
- Drempel wijzigen markeert de graaf als verouderd.
- Drempel op maximum toont "uit".
- Legende toont enkel aanwezige relatietypes.
- Relatietype verbergen via legende.
- Relatietype opnieuw tonen.
- HTML-locatie openen.

**Bron:** `GUI/screens/DynamicDataVisualisationScreen.py:188`, `GUI/screens/DynamicDataVisualisationScreen.py:279`, `GUI/screens/DynamicDataVisualisationScreen.py:467`.

---

### F-VIS-03 Visualisatie bewaren en regenereren

**Doel:** wijzigingen in de graaf bewaren en de graaf opnieuw opbouwen.

**Hoofdflow**
1. "Bewaar wijzigingen" vraagt de JavaScript-graaf om de huidige nodes/edges naar Python te sturen.
2. Python vervangt de node-/edge-data in de HTML en bewaart de supportdata in JSON.
3. De status gaat naar "Changes saved".
4. "Regenerate" vraagt bevestiging en bouwt de HTML volledig opnieuw op.

**Business Rules**
- BR-VIS-11: Regenereren toont een bevestiging dat de huidige graaflayout overschreven wordt.
- BR-VIS-12: Bewaren werkt alleen als de HTML nog bestaat en het project nog open is; anders volgt een melding.
- BR-VIS-13: Na bewaren wordt de supportdata (posities, collecties, joint nodes) in `visuals_python_support_data.json` opgeslagen.
- BR-VIS-14: De status "Changes are not saved" verschijnt zodra de gebruiker de graaf wijzigt.
- BR-VIS-15: Bij verlaten van het project/de app wordt om bevestiging gevraagd bij onbewaarde graafwijzigingen.

**Scenario-kandidaten**
- Wijzigingen bewaren in de HTML.
- Bewaren zonder bestaande HTML: foutmelding.
- Regenereren bevestigen: HTML wordt opnieuw opgebouwd.
- Regenereren annuleren: niets gebeurt.
- Graaf wijzigen toont "niet bewaard".
- Bewaren toont "bewaard".
- Project verlaten met onbewaarde graaf vraagt bevestiging.

**Bron:** `GUI/screens/DynamicDataVisualisationScreen.py:512`, `GUI/screens/DynamicDataVisualisationScreen.py:538`, `GUI/dialog_windows/OverwriteGraphWarningWindow.py:8`.

---

### F-VIS-04 Incrementele update en verouderd-indicator

**Doel:** de graaf actueel houden zonder altijd volledig te regenereren.

**Hoofdflow**
1. Relatiewijzigingen worden bijgehouden in `VisualisationStateTracker` (toe te voegen/te verwijderen relaties).
2. Bij openen van de visualisatietab worden enkel die relaties toegevoegd/verwijderd in de bestaande graaf.
3. Het label "The visualisation is outdated, refresh to see new changes" verschijnt zolang de staat niet up-to-date is.
4. Na een volledige regeneratie of incrementele update verdwijnt het label.

**Business Rules**
- BR-VIS-16: Een relatie die eerst verwijderd en daarna opnieuw toegevoegd wordt, wordt uit de wachtrij gehaald.
- BR-VIS-17: Een relatie die eerst toegevoegd en daarna verwijderd wordt, wordt uit de wachtrij gehaald.
- BR-VIS-18: De indicator wordt verborgen zodra de visualisatiestaat up-to-date is.

**Scenario-kandidaten**
- Relatie toevoegen toont "verouderd".
- Visualisatietab openen werkt incrementeel bij.
- Na update verdwijnt de verouderd-melding.
- Relatie verwijderen en opnieuw toevoegen maakt de wachtrij leeg.

**Bron:** `Domain/util/VisualisationStateTracker.py:16`, `GUI/screens/DynamicDataVisualisationScreen.py:438`.

---

### F-EXP-01 Exportmodus kiezen

**Doel:** kiezen tussen alle data en enkel gewijzigde data.

**Hoofdflow**
1. Stap 4 toont twee radiobuttons: "All data" en "Without unedited data".
2. Zonder keuze is er geen subscherm actief.
3. Bij "All data" verschijnt het exportformulier voor alle data.
4. Bij "Without unedited data" verschijnt het vergelijkingsformulier.

**Business Rules**
- BR-EXP-01: Slechts één modus is tegelijk actief.
- BR-EXP-02: Wisselen van modus verbergt het andere subscherm en toont het gekozen subscherm.
- BR-EXP-03: De export is alleen beschikbaar in stap 4, dus enkel bij geldige projectbestanden.

**Scenario-kandidaten**
- "All data" kiezen toont het bijhorende formulier.
- "Without unedited data" kiezen toont het vergelijkingsformulier.
- Wisselen tussen modi verbergt het vorige formulier.

**Bron:** `GUI/screens/ExportDataScreen.py:164`.

---

### F-EXP-02 Alle data exporteren

**Doel:** de volledige projectdata exporteren naar een bestand.

**Hoofdflow**
1. Gebruiker kiest formaat (Excel, CSV, JSON, GeoJSON; SDF niet ondersteund).
2. Optioneel: "relaties en assets in verschillende bestanden".
3. Bij CSV verschijnt de optie "assets in verschillende bestanden per klasse".
4. Klik "Exporteer", kies opslaglocatie.
5. De applicatie exporteert alle interne objecten en persistente relaties.
6. Na succes opent de map met het exportbestand.

**Business Rules**
- BR-EXP-04: "All data" exporteert de interne objecten plus de persistente relaties (actief + inactieve DAVIE-relaties).
- BR-EXP-05: Relaties en assets splitsen levert `<naam>_relations.<ext>` en `<naam>_assets.<ext>`.
- BR-EXP-06: Splitsen per klasse is enkel zinvol/ beschikbaar voor CSV en produceert meerdere bestanden.
- BR-EXP-07: Bij geen exporteerbare data verschijnt "Er is geen data om te exporteren".
- BR-EXP-08: Bij een schrijffout (bv. bestand open in Excel) verschijnt een toelichting met de bestandsnaam.
- BR-EXP-09: De extensie wordt bepaald door het gekozen formaat en de bestandskiezer.

**Scenario-kandidaten**
- Alle data naar Excel exporteren.
- Alle data naar CSV exporteren.
- Alle data naar JSON/GeoJSON exporteren.
- Relaties en assets in aparte bestanden.
- Splitsen per klasse bij CSV.
- Exporteren zonder data: melding.
- Exporteren naar een openstaand bestand: toestemming geweigerd-melding.
- Na export opent de map.

**Bron:** `Domain/step_domain/ExportDataDomain.py:30`, `GUI/screens/ExportData_elements/AbstractExportDataSubScreen.py:130`, `GUI/screens/ExportData_elements/ExportAllDataSubScreen.py:11`.

---

### F-EXP-03 Enkel gewijzigde data exporteren (diff)

**Doel:** een export maken met enkel de verschillen ten opzichte van de originele aanleverbestanden.

**Hoofdflow**
1. Gebruiker voegt één of meerdere originele bestanden toe.
2. De bestanden verschijnen in een lijst met verwijderknop.
3. "Toon verschillen" leest de originele bestanden, valideert ze en vergelijkt ze attribuut-per-attribuut met de huidige data.
4. Een tabel toont per verschil: volgnummer, identificator, actie, attribuut, oude waarde, nieuwe waarde.
5. Acties: `asset added`, `relation added`, `attribute changed`.
6. Bij fouten in de originele bestanden verschijnt een fouttabel in plaats van de verschillentabel.
7. "Exporteer" schrijft enkel de gewijzigde assets en relaties weg.
8. "Lege velden" wist de originele bestanden en de vergelijking.

**Business Rules**
- BR-EXP-10: De vergelijking gebeurt op attribuutniveau, inclusief complexe attributen (oude/nieuwe waarde per subattribuut).
- BR-EXP-11: Nieuwe assets en relaties worden als toegevoegd gerapporteerd.
- BR-EXP-12: Gewijzigde assets worden per gewijzigd attribuut gerapporteerd.
- BR-EXP-13: Zonder originele bestanden zijn "Toon verschillen" en "Exporteer" uitgeschakeld.
- BR-EXP-14: Bij ongeldige originele bestanden wordt een foutentabel getoond; de export gebeurt niet of faalt met een melding.
- BR-EXP-15: De export bevat alleen de verschillen, niet alle data.
- BR-EXP-16: Meerdere originele bestanden worden samengevoegd tot één vergelijkingsbasis.
- BR-EXP-17: Een bestand verwijderen uit de lijst verbergt de vergelijking en wist de tabel.
- BR-EXP-18: Na export opent de map met het exportbestand.

**Scenario-kandidaten**
- Origineel bestand toevoegen.
- Meerdere originele bestanden toevoegen.
- Bestand verwijderen uit de originelenlijst.
- "Toon verschillen" zonder origineel: knop uit.
- Gewijzigd attribuut wordt getoond met oud/nieuw.
- Nieuw asset wordt getoond als "asset added".
- Nieuwe relatie wordt getoond als "relation added".
- Meerdere complexe subattributen worden als aparte regels getoond.
- Ongeldig origineel bestand toont foutentabel.
- Exporteren van verschillen naar Excel/CSV.
- Exporteren van verschillen zonder verschillen: melding "geen data".
- "Lege velden" wist de lijst en tabel.

**Bron:** `Domain/step_domain/ExportFilteredDataSubDomain.py:57`, `Domain/step_domain/ExportFilteredDataSubDomain.py:116`, `GUI/screens/ExportData_elements/ExportFilteredDataSubScreen.py:149`, `GUI/screens/ExportData_elements/ExportFilteredDataSubScreen.py:250`.

---

### F-EXP-04 Exportformaten en platformgedrag

**Business Rules**
- BR-EXP-19: Exportformaten zijn platformafhankelijk: Excel, CSV, JSON, GeoJSON; SDF enkel op Windows en momenteel niet voor export aangeboden.
- BR-EXP-20: Conversie gebeurt via `OtlmowConverter`; fouten worden als melding of fout getoond.
- BR-EXP-21: Bestandsnamen en extensies worden door de file picker bepaald; de applicatie forceert `.otlw` enkel bij projectexport.
- BR-EXP-22: De exporteerbare objecten zijn interne objecten + persistente relaties, niet de externe/Agent-objecten.

**Scenario-kandidaten**
- Beschikbare formaten verschillen per platform.
- SDF is niet beschikbaar als exportformaat.
- Export bevat geen externe assets.
- Export bevat actieve en inactieve DAVIE-relaties.

**Bron:** `Domain/global_vars.py:13`, `GUI/screens/ExportDataScreen.py:41`, `Domain/step_domain/RelationChangeDomain.py:1426`.

---

## 5. Cross-cutting Business Rules

### 5.1 Bestandsstatussen en stapvergrendeling
- `WARNING`: toegevoegd maar nog niet gevalideerd.
- `OK`: succesvol gevalideerd.
- `ERROR`: validatiefout of ontbrekend bestand.
- Stap 3/4 zijn enkel beschikbaar als er minstens één bestand is en alle bestanden `OK` zijn.

### 5.2 Persistentie
- Projectmetadata: `project_details.json`.
- Projectbestanden: `saved_documents.json` + map `project_files`.
- Quick saves: `quick_saves/quick_save-<datum>_<tijd>.json`, maximaal 7 dagen.
- Visualisatie: `visuals/graph_visualisation.html` + `visuals/visuals_python_support_data.json`.
- Instellingen: `~/OTLWizardProjects/settings.json`.

### 5.3 Asynchrone operaties en loading screens
- Templatecreatie, validatie, conversies, visualisatie en export lopen asynchroon.
- Tijdens langdurige operaties verschijnt een loading screen; dit mag de UI niet blokkeren.
- Fouten in asynchrone taken worden via de exception handler aan de gebruiker getoond.

### 5.4 Foutafhandeling
- Voorspelbare fouten (lege velden, ongeldige database, dubbele namen, rechten) krijgen een gerichte melding.
- Onverwachte fouten worden gelogd en via `ErrorScreen` getoond; de foutmelding wordt naar het klembord gekopieerd.
- Netwerk-/updatefouten blokkeren de kernfunctionaliteit niet.

### 5.5 Platformspecifiek
- SDF en FDO Toolbox: enkel Windows.
- "Logs openen" gebruikt Windows Verkenner.
- Bestanden openen in de standaardapplicatie verschilt per OS.

### 5.6 Visuele feedback
- Statusiconen: groen vinkje, oranje waarschuwing, rood kruis.
- Toegevoegde/gewijzigde items worden gemarkeerd.
- "Laatst toegevoegd project" wordt gemarkeerd.
- Verouderde visualisatie krijgt een rode indicator.

---

## 6. Scenario-seeds (compact)

Onderstaande lijst is bedoeld als directe invoer voor Gherkin-schrijvers. Elke regel kan één scenario
worden; schrijf de `Given` vanuit de precondities en de `Then` vanuit de verwachting.

| ID | Feature | Scenario | Kernverwachting |
|---|---|---|---|
| S-001 | F-APP-01 | Opstarten zonder updates | Home verschijnt, geen updatevenster |
| S-002 | F-APP-01 | Update beschikbaar | Suggestievenster met lokale/nieuwe versie |
| S-003 | F-APP-01 | Geen internet | App start, fout wordt gelogd |
| S-004 | F-APP-02 | Taal naar Engels | `settings.json` aangepast, herstartmelding |
| S-005 | F-APP-03 | Project zonder bestanden | Stap 3/4 uitgeschakeld |
| S-006 | F-APP-03 | Alle bestanden OK | Stap 3/4 ingeschakeld |
| S-007 | F-APP-04 | Sluiten met onbewaarde graaf | Waarschuwing; Back houdt app open |
| S-008 | F-PROJ-01 | Sorteren op laatste wijziging | Nieuwste project bovenaan |
| S-009 | F-PROJ-01 | Zoeken op bestek | Enkel matchende rijen zichtbaar |
| S-010 | F-PROJ-02 | Project aanmaken | Projectmap, subset en metadata bestaan |
| S-011 | F-PROJ-02 | Lege eigen referentie | Foutmelding, geen project |
| S-012 | F-PROJ-02 | Ongeldige subset | Foutmelding, geen project |
| S-013 | F-PROJ-02 | Dubbele projectnaam | Melding, geen overschrijving |
| S-014 | F-PROJ-03 | Bestek wijzigen | Metadata bijgewerkt |
| S-015 | F-PROJ-03 | Referentie wijzigen | Projectmap hernoemd |
| S-016 | F-PROJ-04 | Project verwijderen | Map en lijst vermelding weg |
| S-017 | F-PROJ-05 | `.otlw` importeren | Project verschijnt in lijst |
| S-018 | F-PROJ-05 | Import met bestaande naam | Melding, niets uitgepakt |
| S-019 | F-PROJ-06 | Project exporteren | `.otlw` bevat subset, bestanden, laatste quick save |
| S-020 | F-PROJ-06 | Export met ontbrekend bestand | Waarschuwing; Nee stopt export |
| S-021 | F-PROJ-07 | Project openen | Bestanden geladen, stappen geëvalueerd |
| S-022 | F-PROJ-08 | Validatie maakt quick save | JSON-bestand in `quick_saves` |
| S-023 | F-PROJ-08 | Heropenen herstelt quick save | Assets/relaties terug |
| S-024 | F-PROJ-08 | Quick save ouder dan 7 dagen | Bestand verwijderd |
| S-025 | F-PROJ-09 | Geldige subset wijzigen | Klassen/relaties vernieuwd |
| S-026 | F-PROJ-09 | Ongeldige subset wijzigen | Fout, oude subset actief |
| S-027 | F-TPL-01 | Stap 1 openen | Klassen uit subset, alles geselecteerd |
| S-028 | F-TPL-01 | Agent in lijst | Niet selecteerbaar |
| S-029 | F-TPL-01 | Alles deselecteren | Exportknop uit |
| S-030 | F-TPL-02 | Formaat CSV kiezen | Keuzelijsten uitgeschakeld |
| S-031 | F-TPL-02 | Expanded info kiezen | Attribuutinfo en deprecated aan |
| S-032 | F-TPL-03 | Excel-template genereren | Bestand bestaat en opent |
| S-033 | F-TPL-03 | Template met 0 klassen | Export niet gestart |
| S-034 | F-TPL-03 | Bestand open in Excel | Toelichtende foutmelding |
| S-035 | F-TPL-04 | Infotemplate genereren | Bestand wordt aangemaakt |
| S-036 | F-TPL-05 | SDF op Linux | Formaat niet beschikbaar |
| S-037 | F-DATA-01 | Bestand toevoegen | Status WARNING, kopie in project |
| S-038 | F-DATA-01 | Dubbel bestandsnaam | Melding, geen extra bestand |
| S-039 | F-DATA-01 | Bestand verwijderen | Bestand en lijstitem weg |
| S-040 | F-DATA-02 | Geldige validatie | Status OK, groene feedback |
| S-041 | F-DATA-02 | OTL-fout | Status ERROR, rode feedback |
| S-042 | F-DATA-02 | Lege identificator | Fout in feedbacklijst |
| S-043 | F-DATA-02 | Ongeldige relatie | Fout in feedbacklijst |
| S-044 | F-DATA-02 | Dubbele asset samenvoegen | Eén gecombineerd asset |
| S-045 | F-DATA-02 | Conflict bij samenvoegen | Fout, bestand ERROR |
| S-046 | F-DATA-02 | Hervalidatie met quick save | Bevestigingsvenster |
| S-047 | F-REL-01 | Object selecteren | Attributen en mogelijke relaties gevuld |
| S-048 | F-REL-01 | Zoeken in objectenlijst | Gefilterde lijst, mappen open |
| S-049 | F-REL-02 | Bestaande relatie | Niet opnieuw als mogelijk |
| S-050 | F-REL-02 | Full OTL aanzetten | Ruimere relatielijst |
| S-051 | F-REL-03 | Relatie toevoegen | Bestaande lijst +1, quick save |
| S-052 | F-REL-03 | Meerdere relaties toevoegen | Alle geselecteerde toegevoegd |
| S-053 | F-REL-04 | Relatie verwijderen | Bestaande -1, mogelijk +1, quick save |
| S-054 | F-REL-04 | AIM-ID-relatie verwijderen | Blijft inactief bewaard |
| S-055 | F-REL-05 | Externe asset toevoegen | Object in eerste kolom |
| S-056 | F-REL-05 | Lege externe assetnaam | Foutmelding |
| S-057 | F-REL-06 | HeeftBetrokkene rol kiezen | Relatie krijgt rol |
| S-058 | F-REL-06 | HeeftBetrokkene annuleren | Geen relatie toegevoegd |
| S-059 | F-MAP-01 | Kaart openen | Webview met assets |
| S-060 | F-MAP-01 | Kaart boven 300 assets | Limietmelding |
| S-061 | F-MAP-01 | Asset op kaart klikken | Selectie in relatenscherm |
| S-062 | F-VIS-01 | Visualisatie openen | HTML geladen |
| S-063 | F-VIS-02 | Modus wijzigen | Verouderd-indicator |
| S-064 | F-VIS-02 | Drempel op maximum | Label "uit" |
| S-065 | F-VIS-02 | Relatietype verbergen | Relaties verdwijnen uit graaf |
| S-066 | F-VIS-03 | Wijzigingen bewaren | HTML + support-JSON bijgewerkt |
| S-067 | F-VIS-03 | Regenereren | Bevestiging en nieuwe graaf |
| S-068 | F-VIS-03 | Project verlaten onbewaard | Waarschuwing |
| S-069 | F-VIS-04 | Relatie toevoegen | Verouderd-melding |
| S-070 | F-EXP-01 | Exportmodus wisselen | Juiste subscherm zichtbaar |
| S-071 | F-EXP-02 | Alle data exporteren | Bestand met alle objecten/relaties |
| S-072 | F-EXP-02 | Relaties/assets splitsen | `_relations` en `_assets` bestanden |
| S-073 | F-EXP-02 | Geen data | Melding "geen data" |
| S-074 | F-EXP-02 | Bestand open in Excel | Toestemming geweigerd-melding |
| S-075 | F-EXP-03 | Origineel bestand toevoegen | Bestand in originelenlijst |
| S-076 | F-EXP-03 | Verschillen tonen | Tabel met acties en waarden |
| S-077 | F-EXP-03 | Gewijzigd attribuut | `attribute changed` met oud/nieuw |
| S-078 | F-EXP-03 | Nieuw asset | `asset added` |
| S-079 | F-EXP-03 | Nieuwe relatie | `relation added` |
| S-080 | F-EXP-03 | Ongeldig origineel | Foutentabel |
| S-081 | F-EXP-03 | Enkel verschillen exporteren | Export bevat enkel changes |
| S-082 | F-EXP-03 | Lege velden | Lijst en tabel gewist |

---

## 7. Openstaande punten voor Gherkin/PO

De gevonden ambiguïteiten zijn gebundeld in een apart document:
[ambiguiteiten.md](ambiguiteiten.md). Dat document bevat per punt (A-01 tot en met A-16) het
waargenomen gedrag, de bewijslocatie in de code, de te nemen beslissing, de voorgestelde aanname
en de impact op Gherkin.

---

## 8. Niet-actieve of ondersteunende code (buiten feature-scope)

Deze onderdelen zijn aanwezig maar horen niet bij de actieve gebruikersflow; ze hoeven geen Gherkin
te krijgen tenzij expliciet gevraagd:

- `GUI/screens/ConversionScreen.py`: leeg/niet aangesloten conversiescherm.
- `GUI/dialog_windows/ExportToTemplateWindow.py`: ouderdialoog, niet gebruikt door de actieve flow.
- `GUI/screens/DataVisualisation_elements/` en `Map_elements/`: ondersteunende logica (wel gebruikt).
- `SQLITE_to_XSD.py`, `csv_to_sqlite.py`: losse hulpscripts.
- `pyinstaller_script.py`, `scripts/`, `LatestReleaseMulti/`: build en distributie.
- `UnitTests/`: tests en fixtures, geen gebruikersfunctionaliteit.

---

## 9. Voorgestelde Gherkin-structuur

```text
features/
  app/
    startup_and_updates.feature
    language_and_help.feature
    navigation_and_unsaved_changes.feature
  projects/
    project_overview.feature
    create_project.feature
    edit_project.feature
    delete_project.feature
    import_export_project.feature
    quick_saves.feature
    change_subset.feature
  templates/
    class_selection.feature
    template_options.feature
    generate_delivery_template.feature
    generate_info_template.feature
    sdf_support.feature
  data/
    manage_project_files.feature
    validate_documents.feature
    validation_feedback.feature
  relations/
    relation_lists_and_search.feature
    possible_relations.feature
    add_relations.feature
    remove_relations.feature
    external_assets.feature
    heeft_betrokkene_role.feature
    davie_aim_id_relations.feature
    map_view.feature
  visualisation/
    generate_and_view.feature
    options_and_legend.feature
    save_and_regenerate.feature
    stale_and_incremental_updates.feature
  export/
    choose_export_mode.feature
    export_all_data.feature
    export_changes.feature
    export_formats_and_errors.feature
```

Aanbevolen scenario-opbouw:

- **Background**: geopend project, subset, geopende stap.
- **Given**: bestandsstatus, quick-save aanwezigheid, geselecteerde objecten, bestaande relaties.
- **When**: één concrete gebruikersactie of systeemtrigger.
- **Then**: waarneembare UI-uitkomst + persistente toestand (bestand, status, metadata).
- **And**: bijkomende asserties, maar vermijd meerdere acties in één `When`.

---

## 10. Bronverwijzingen (samenvatting)

| Domein | Belangrijkste bestanden |
|---|---|
| App/start/navigatie | `wizard_main.py`, `GUI/MainWindow.py`, `GUI/header/*` |
| Projecten | `Domain/project/Project.py`, `Domain/step_domain/HomeDomain.py`, `GUI/screens/Home_elements/OverviewTable.py` |
| Templates | `Domain/step_domain/TemplateDomain.py`, `GUI/screens/TemplateScreen.py`, `GUI/screens/InfoTemplateScreen.py` |
| Data/validatie | `Domain/step_domain/InsertDataDomain.py`, `Domain/util/CombineAssetHelper.py`, `GUI/screens/InsertDataScreen.py` |
| Relaties | `Domain/step_domain/RelationChangeDomain.py`, `GUI/screens/RelationChangeScreen.py`, `GUI/screens/RelationChange_elements/*` |
| Visualisatie | `GUI/screens/DynamicDataVisualisationScreen.py`, `Domain/util/VisualisationStateTracker.py`, `GUI/screens/DataVisualisation_elements/VisualisationHelper.py` |
| Kaart | `GUI/screens/MapScreen.py`, `GUI/screens/Map_elements/MapHelper.py` |
| Export | `Domain/step_domain/ExportDataDomain.py`, `Domain/step_domain/ExportFilteredDataSubDomain.py`, `GUI/screens/ExportDataScreen.py`, `GUI/screens/ExportData_elements/*` |
| Instellingen/updates | `Domain/Settings.py`, `Domain/network/Updater.py`, `GUI/dialog_windows/LanguageWindow.py` |
| SDF | `Domain/util/SDFHandler.py`, `Domain/util/XSDCreator.py` |
