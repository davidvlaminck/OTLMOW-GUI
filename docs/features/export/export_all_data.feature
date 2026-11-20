# language: nl
Feature: Alle data exporteren (F-EXP-02)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 4
    En de exportmodus "All data" is geselecteerd

  Scenario: Alle data naar Excel exporteren (S-083)
    Gegeven de gebruiker kiest formaat Excel
    En kiest een opslaglocatie
    Als de gebruiker op "Exporteer" klikt
    Dan wordt de export uitgevoerd
    En na succes opent de map met het exportbestand
    En het bestand bevat alle interne objecten en persistente relaties

  Scenario: Alle data naar CSV exporteren (S-084)
    Gegeven de gebruiker kiest formaat CSV
    En kiest een opslaglocatie
    Als de gebruiker op "Exporteer" klikt
    Dan wordt de export uitgevoerd
    En na succes opent de map met het exportbestand

  Scenario: Alle data naar JSON/GeoJSON exporteren (S-085)
    Gegeven de gebruiker kiest formaat JSON of GeoJSON
    En kiest een opslaglocatie
    Als de gebruiker op "Exporteer" klikt
    Dan wordt de export uitgevoerd
    En na succes opent de map met het exportbestand

  Scenario: Relaties en assets in aparte bestanden (BR-EXP-05)
    Gegeven de gebruiker vinkt "Relaties en assets in verschillende bestanden" aan
    En kiest formaat Excel of CSV
    Als de export wordt uitgevoerd
    Dan worden twee bestanden aangemaakt: <naam>_relations.<ext> en <naam>_assets.<ext>

  Scenario: Splitsen per klasse bij CSV (BR-EXP-06)
    Gegeven de gebruiker kiest formaat CSV
    En vinkt "Assets in verschillende bestanden per klasse" aan
    Als de export wordt uitgevoerd
    Dan worden meerdere CSV-bestanden aangemaakt, één per klasse

  Scenario: Exporteren zonder data: melding (BR-EXP-07)
    Gegeven het project heeft geen exporteerbare data (geen interne objecten)
    Als de gebruiker op "Exporteer" klikt
    Dan verschijnt de melding "Er is geen data om te exporteren"
    En er wordt geen bestand aangemaakt

  Scenario: Exporteren naar een openstaand bestand: toestemming geweigerd-melding (BR-EXP-08)
    Gegeven het doelbestand staat open in Excel en is niet beschrijfbaar
    Als de gebruiker probeert te exporteren
    Dan verschijnt een toelichting met de bestandsnaam
    En de export wordt niet overschreven

  Scenario: Export bevat actieve en inactieve DAVIE-relaties (BR-EXP-04, BR-REL-36)
    Gegeven het project heeft actieve relaties en inactieve AIM-ID-relaties
    Als de gebruiker "Alle data" exporteert
    Dan bevat de export alle actieve relaties plus alle inactieve AIM-ID-relaties

  Scenario: Export bevat geen externe assets/Agent-objecten (BR-EXP-22)
    Gegeven het project heeft externe assets en Agent-objecten
    Als de gebruiker exporteert
    Dan zitten deze NIET in de export
    Enkel interne objecten en persistente relaties worden geëxporteerd

  Scenario: Na export opent de map (BR-EXP-18)
    Gegeven de export is succesvol voltooid
    Als het proces afgerond is
    Dan opent de bestandsverkenner op de map met het exportbestand