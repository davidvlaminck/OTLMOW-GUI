# language: nl
Feature: Exportformaten en foutafhandeling (F-EXP-04, A-12)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 4

  Scenario: Beschikbare formaten verschillen per platform (BR-EXP-19)
    Gegeven het platform is Windows
    Als de gebruiker in stap 4 kijkt naar de exportformaten
    Dan zijn Excel, CSV, JSON, GeoJSON beschikbaar
    En SDF is niet beschikbaar voor export (alleen voor template)
    Gegeven het platform is Linux of macOS
    Als de gebruiker in stap 4 kijkt naar de exportformaten
    Dan zijn Excel, CSV, JSON, GeoJSON beschikbaar
    En SDF is niet beschikbaar

  Scenario: SDF is niet beschikbaar als exportformaat (BR-EXP-19)
    Gegeven de gebruiker is in stap 4
    Als de gebruiker kijkt naar de exportformaten
    Dan is SDF nooit beschikbaar als exportformaat

  Scenario: Export bevat geen externe assets (BR-EXP-22)
    Gegeven het project heeft externe assets
    Als de gebruiker exporteert (alle data of diff)
    Dan zitten de externe assets NIET in de export

  Scenario: Export bevat actieve en inactieve DAVIE-relaties (BR-EXP-04)
    Gegeven het project heeft actieve relaties en inactieve AIM-ID-relaties
    Als de gebruiker exporteert
    Dan zijn beide typen relaties in de export opgenomen

  Scenario: Conversiefouten worden als melding of fout getoond (BR-EXP-20)
    Gegeven er treedt een fout op tijdens conversie (bijv. OtlmowConverter)
    Als de export wordt uitgevoerd
    Dan wordt de fout als melding of fout aan de gebruiker getoond

  Scenario: Bestandsnamen en extensies worden door de file picker bepaald (BR-EXP-21)
    Gegeven de gebruiker kiest een opslaglocatie
    Als de export wordt uitgevoerd
    Dan wordt de extensie bepaald door het gekozen formaat
    En de applicatie forceert .otlw enkel bij projectexport

  Scenario: Fout bij project importeren wordt gesilenced (A-12 beslissing)
    Gegeven de gebruiker importeert een .otlw-bestand
    En er treedt een fout op tijdens uitpakken of laden
    Als de fout optreedt
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO in HeaderBar.py:271)
    En de applicatie crasht niet

  Scenario: Fout bij project exporteren wordt gesilenced (A-12 beslissing)
    Gegeven de gebruiker exporteert een project
    En er treedt een fout op tijdens het aanmaken van de .otlw
    Als de fout optreedt
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO in OverviewTable.py:193)
    En de applicatie crasht niet

  Scenario: Fout bij template exporteren wordt gesilenced (A-12 beslissing)
    Gegeven de gebruiker exporteert een template
    En er treedt een fout op tijdens generatie
    Als de fout optreedt
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO in TemplateScreen.py:745)
    En de applicatie crasht niet

  Scenario: Fout bij bestand toevoegen wordt gesilenced (A-12 beslissing)
    Gegeven de gebruiker voegt een bestand toe in stap 2
    En er treedt een fout op tijdens kopiëren of verwerken
    Als de fout optreedt
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO in InsertDataScreen.py:567)
    En de applicatie crasht niet

  Scenario: Fout bij export (alle data) wordt gesilenced (A-12 beslissing)
    Gegeven de gebruiker exporteert alle data
    En er treedt een fout op tijdens export
    Als de fout optreedt
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO in AbstractExportDataSubScreen.py:154)
    En de applicatie crasht niet

  Scenario: Fout bij export (diff) wordt gesilenced (A-12 beslissing)
    Gegeven de gebruiker exporteert gewijzigde data
    En er treedt een fout op tijdens export
    Als de fout optreedt
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO in ExportFilteredDataSubScreen.py:185)
    En de applicatie crasht niet

  Scenario: Fout in Project.py wordt gesilenced (A-12 beslissing)
    Gegeven er treedt een fout op in Project.py (regels 584, 1047, 1077, 1111)
    Als de fout optreedt
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO)
    En de applicatie crasht niet

  Scenario: Subsetbestand niet gevonden fout wordt gesilenced (A-12 beslissing)
    Gegeven de subset van een project is niet te vinden
    Als de fout optreedt
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO in TemplateDomain.py:146)
    En de applicatie crasht niet