# language: nl
Feature: Visualisatie-opties en legende (F-VIS-02)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3, tab "data visuals"
    En de visualisatie is geladen

  Scenario: Modus wijzigen markeert de graaf als verouderd (BR-VIS-06, S-075)
    Gegeven de visualisatie is up-to-date
    Als de gebruiker de visualisatiemodus wijzigt (bijv. van hiërarchisch naar spinnenweb)
    Dan wordt de verouderd-indicator getoond ("The visualisation is outdated, refresh to see new changes")
    En de graaf moet geregenereerd worden

  Scenario: Drempel wijzigen markeert de graaf als verouderd (BR-VIS-06)
    Gegeven de visualisatie is up-to-date
    Als de gebruiker de collectiedrempel wijzigt
    Dan wordt de verouderd-indicator getoond

  Scenario: Drempel op maximum toont "uit" (BR-VIS-07)
    Gegeven de gebruiker verplaatst de drempelslider naar het maximum
    Als het label wordt getoond
    Dan toont het label "uit"
    En relaties naar dezelfde asset worden niet meer gebundeld

  Scenario: Legende toont enkel aanwezige relatietypes (BR-VIS-08)
    Gegeven de visualisatie is geladen
    Als de legende wordt getoond
    Dan zijn alleen relatietypes zichtbaar die in de huidige data voorkomen

  Scenario: Relatietype verbergen via legende (BR-VIS-09, S-076)
    Gegeven de legende toont een relatietype met een aangevinkte checkbox
    Als de gebruiker de checkbox uitschakelt
    Dan verdwijnen alle relaties van dat type uit de graaf
    En de checkbox blijft uitgevinkt bij verversen (BR-VIS-10)

  Scenario: Relatietype opnieuw tonen (BR-VIS-09 variant)
    Gegeven een relatietype is verborgen via de legende
    Als de gebruiker de checkbox weer inschakelt
    Dan verschijnen de relaties van dat type weer in de graaf

  Scenario: HTML-locatie openen (BR-VIS-10)
    Gegeven de visualisatie is geladen
    Als de gebruiker op de knop "HTML-locatie openen" klikt
    Dan opent de bestandsverkenner op de map met de visualisatie-HTML

  Scenario: Help met muisbediening
    Gegeven de visualisatie is geladen
    Als de gebruiker op "Help" klikt
    Dan wordt de muisbediening uitgelegd