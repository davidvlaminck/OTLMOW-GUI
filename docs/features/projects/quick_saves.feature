# language: nl
Feature: Quick saves (F-PROJ-08)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden

  Scenario: Succesvolle validatie maakt een quick save (S-022)
    Gegeven de gebruiker valideert de projectbestanden
    En de validatie slaagt (alle bestanden status OK)
    Als de validatie voltooid is
    Dan wordt een quick save-bestand aangemaakt in "<project>/quick_saves/quick_save-<yymmdd>_<HHMMSS>.json"
    En de quick save bevat de gevalideerde assets en relaties
    En project_details.json onthoudt de laatste quick save

  Scenario: Relatie toevoegen/verwijderen maakt een quick save (S-022 variant)
    Gegeven de gebruiker is in stap 3
    En voegt een relatie toe of verwijdert een relatie
    Als de actie voltooid is
    Dan wordt een nieuwe quick save aangemaakt
    En de vorige quick save blijft behouden (tot 7 dagen)

  Scenario: Heropenen van het project herstelt de laatste quick save (S-023)
    Gegeven er is een project met een quick save
    En de gebruiker sluit het project
    Als de gebruiker het project later opnieuw opent
    Dan worden de assets en relaties uit de laatste quick save geladen
    En de visualisatiestatus wordt hersteld

  Scenario: Quick saves ouder dan 7 dagen worden verwijderd (S-024, A-06 beslissing)
    Gegeven er zijn quick saves van 8 dagen geleden en van vandaag
    En de gebruiker maakt een nieuwe quick save (bijv. door te valideren)
    Als de opruiming wordt uitgevoerd
    Dan wordt de quick save van 8 dagen geleden verwijderd
    En de quick save van vandaag blijft behouden
    En er verschijnt geen melding aan de gebruiker

  Scenario: Afwijkend bestandsnaamformaat blijft bewaard (BR-PROJ-24, A-06 beslissing)
    Gegeven er is een quick save-bestand met een niet-standaard naam (bijv. "backup.json")
    En de gebruiker maakt nieuwe quick saves aan
    Als de 7-daagse opruiming wordt uitgevoerd
    Dan blijft het bestand "backup.json" bewaard
    En wordt nooit automatisch verwijderd

  Scenario: Hervalidatie met bestaande quick save vraagt bevestiging (BR-PROJ-26)
    Gegeven er is een bestaande quick save
    En de gebruiker start een nieuwe validatie
    Als de bevestigingsvenster verschijnt
    En de gebruiker bevestigt
    Dan wordt de nieuwe validatie uitgevoerd
    En de oude quick save wordt overschreven/vervangen
    Als de gebruiker annuleert
    Dan wordt de validatie niet uitgevoerd
    En de bestaande quick save blijft behouden

  Scenario: Header toont save-indicator tijdens bewaren (BR-PROJ-25)
    Gegeven een quick save wordt aangemaakt
    Als het bewaren in gang is
    Dan toont de header een save-animatie of laatste-save-indicator