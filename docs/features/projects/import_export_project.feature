# language: nl
Feature: Project importeren en exporteren (F-PROJ-05, F-PROJ-06)

  Background:
    Gegeven de applicatie is gestart
    En de gebruiker is op het Home-scherm

  Scenario: Geldig .otlw importeren (S-018)
    Gegeven de gebruiker klikt op "Import" in de header
    En kiest een geldig .otlw-bestand
    En de projectmap bestaat nog niet lokaal
    Als de import wordt uitgevoerd
    Dan wordt het archief uitgepakt in "~/OTLWizardProjects/Projects/<eigen referentie>"
    En het project wordt geladen en aan de lijst toegevoegd
    En het project wordt gemarkeerd als laatst toegevoegd

  Scenario: Importeren van een project met bestaande naam: melding, niets uitgepakt (S-019)
    Gegeven er bestaat al een project met eigen referentie "Project_Import"
    En de gebruiker probeert een .otlw te importeren met dezelfde eigen referentie
    Als de import wordt geprobeerd
    Dan verschijnt een melding dat de projectmap al bestaat
    En er wordt niets uitgepakt
    En het bestaande project blijft ongewijzigd

  Scenario: Ongeldig .otlw-bestand: fout wordt gesilenced (A-12 beslissing)
    Gegeven de gebruiker klikt op "Import"
    En kiest een bestand dat geen geldig .otlw-archief is
    Als de import wordt geprobeerd
    Dan verschijnt geen gebruikersmelding (fout is gesilenced per TODO in code)
    En de applicatie crasht niet

  Scenario: Project exporteren zonder ontbrekende bestanden (S-020)
    Gegeven er is een project met alle projectbestanden aanwezig
    En de gebruiker klikt op het deelicoon
    En kiest een opslaglocatie
    Als de export wordt uitgevoerd
    Dan wordt een .otlw-bestand aangemaakt
    En de verkenner opent op het bestand
    En het archief bevat: project_details.json, saved_documents.json, subset, alle projectbestanden, laatste quick save, visualisatiebestanden

  Scenario: Exporteren met ontbrekende bestanden en "Ja" (S-021, A-14 beslissing)
    Gegeven er is een project waar een projectbestand ontbreekt op schijf
    En de gebruiker klikt op het deelicoon
    En kiest een opslaglocatie
    Als de waarschuwing verschijnt met de lijst van ontbrekende bestanden
    En de gebruiker kiest "Ja"
    Dan gaat de export door
    En het .otlw-bestand bevat enkel de bestaande bestanden
    En de ontbrekende bestanden zitten niet in het archief

  Scenario: Exporteren met ontbrekende bestanden en "Nee": geen export (A-14 beslissing)
    Gegeven er is een project waar een projectbestand ontbreekt op schijf
    En de gebruiker klikt op het deelicoon
    Als de waarschuwing verschijnt
    En de gebruiker kiest "Nee"
    Dan wordt de export geannuleerd
    En er wordt geen .otlw-bestand aangemaakt

  Scenario: Extensie wordt automatisch .otlw (S-020 variant)
    Gegeven de gebruiker kiest een opslaglocatie zonder extensie
    Als de export wordt uitgevoerd
    Dan krijgt het bestand de extensie .otlw

  Scenario: Archief bevat subset, projectbestanden en laatste quick save (BR-PROJ-18, A-05 beslissing)
    Gegeven een project met meerdere quick saves
    Als het project wordt geëxporteerd
    Dan bevat het .otlw-bestand alleen de laatste quick save
    En oudere quick saves zitten niet in het archief