# language: nl
Feature: Projectbestanden beheren (F-DATA-01)

  Background:
    Gegeven er is een geopend project
    En de gebruiker is in stap 2 (data inladen/valideren)

  Scenario: Meerdere bestanden toevoegen (S-037)
    Gegeven de gebruiker klikt op "Kies bestand"
    En selecteert meerdere bestanden (Excel, CSV, JSON, GeoJSON)
    Als de bestanden worden toegevoegd
    Dan worden alle bestanden naar de map "project_files" gekopieerd
    En verschijnen ze in de lijst met status WARNING
    En de validatieknop wordt ingeschakeld

  Scenario: Dubbel bestandsnaam toevoegen: melding en geen extra bestand (S-038)
    Gegeven er is al een bestand "bestand.xlsx" in het project
    En de gebruiker probeert een ander bestand met dezelfde naam toe te voegen
    Als de toevoeging wordt geprobeerd
    Dan verschijnt een melding dat de bestandsnaam al bestaat
    En er wordt geen extra bestand toegevoegd

  Scenario: Excel toevoegen: dropdown-werkbladen worden verwijderd (S-039)
    Gegeven de gebruiker voegt een Excel-bestand toe met werkbladen "Keuzelijsten" en "dropdownvalues"
    Als het bestand wordt verwerkt
    Dan worden deze werkbladen uit de kopie in de projectmap verwijderd
    En het originele bestand blijft ongewijzigd

  Scenario: Bestand verwijderen met de kruisknop (S-040)
    Gegeven er is een bestand in de projectlijst
    Als de gebruiker op het kruisicoon van dat bestand klikt
    Dan wordt het bestand uit de lijst verwijderd
    En het bestand wordt van schijf verwijderd uit de projectmap

  Scenario: Alle bestanden verwijderen met bevestiging (S-041)
    Gegeven er zijn meerdere bestanden in het project
    Als de gebruiker op "Reset" klikt
    En bevestigt in het bevestigingsvenster
    Dan worden alle bestanden uit de lijst verwijderd
    En alle bestanden van schijf verwijderd
    En saved_documents.json wordt bijgewerkt

  Scenario: Alle bestanden verwijderen annuleren (S-041 variant)
    Gegeven er zijn meerdere bestanden in het project
    Als de gebruiker op "Reset" klikt
    En annuleert in het bevestigingsvenster
    Dan blijven alle bestanden in de lijst en op schijf

  Scenario: Bestand verwijderen dat openstaat in Excel: foutmelding (S-042)
    Gegeven een projectbestand staat open in Excel en kan niet worden verwijderd
    Als de gebruiker probeert het bestand te verwijderen
    Dan verschijnt een foutmelding dat het bestand niet verwijderd kan worden
    En het bestand blijft in de lijst en op schijf

  Scenario: Toegevoegd bestand heeft initieel status WARNING (BR-DATA-02)
    Gegeven een bestand wordt toegevoegd
    Als het in de lijst verschijnt
    Dan is de status WARNING (nog niet gevalideerd)