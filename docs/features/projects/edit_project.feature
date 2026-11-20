# language: nl
Feature: Project bewerken (F-PROJ-03)

  Background:
    Gegeven de gebruiker is op het Home-scherm
    En er bestaat een project "Project_Test" met bestek "12345" en subset "subset_a.db"

  Scenario: Bestek wijzigen (S-014)
    Gegeven de gebruiker klikt op het potloodicoon van "Project_Test"
    En wijzigt het bestek naar "67890"
    Als de gebruiker op "Submit" klikt
    Dan wordt de metadata bijgewerkt
    En de laatst bewerkt-datum wordt geactualiseerd
    En de lijst toont het nieuwe bestek

  Scenario: Subset wijzigen naar geldige database (S-015)
    Gegeven de gebruiker klikt op het potloodicoon van "Project_Test"
    En kiest een andere geldige subset "subset_b.db"
    Als de gebruiker op "Submit" klikt
    Dan wordt de subset gewijzigd
    En de modelbuilder wordt vernieuwd
    En de klassenlijst en relaties worden opnieuw geladen
    En de laatst bewerkt-datum wordt geactualiseerd

  Scenario: Subset wijzigen naar ongeldige database: fout en ongewijzigd (S-016)
    Gegeven de gebruiker klikt op het potloodicoon van "Project_Test"
    En kiest een ongeldig bestand als subset
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een foutmelding
    En de oude subset blijft actief
    En de metadata wordt niet gewijzigd

  Scenario: Eigen referentie wijzigen: map wordt hernoemd (S-016 variant)
    Gegeven de gebruiker klikt op het potloodicoon van "Project_Test"
    En wijzigt de eigen referentie naar "Project_Nieuw"
    Als de gebruiker op "Submit" klikt
    Dan wordt de projectmap hernoemd van "Project_Test" naar "Project_Nieuw"
    En de metadata wordt bijgewerkt

  Scenario: Eigen referentie wijzigen naar bestaande naam: fout (S-016 variant)
    Gegeven er bestaat al een project "Project_Bestaat"
    En de gebruiker klikt op het potloodicoon van "Project_Test"
    En wijzigt de eigen referentie naar "Project_Bestaat"
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een foutmelding dat de naam al bestaat
    En de projectmap wordt niet hernoemd
    En de metadata blijft ongewijzigd

  Scenario: Subsetwijziging werkt subsetpad bij wanneer subset in oude projectmap stond (BR-PROJ-12)
    Gegeven de subset van "Project_Test" staat in de projectmap
    En de gebruiker hernoemt het project naar "Project_Nieuw"
    Als de wijziging wordt bevestigd
    Dan wordt het subsetpad in de metadata bijgewerkt naar de nieuwe projectmap