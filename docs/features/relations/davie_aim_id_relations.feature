# language: nl
Feature: DAVIE/AIM-ID-relaties (F-REL-07)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3
    En de aangeleverde data bevat relaties met AIM-ID's

  Scenario: Actieve AIM-ID-relatie verschijnt bij bestaande relaties (BR-REL-33, S-067)
    Gegeven een relatie heeft een identificator die een AIM-ID is
    En de relatie is actief
    Als de bestaande relaties worden getoond
    Dan verschijnt de relatie in de derde kolom (bestaande relaties)

  Scenario: Inactieve AIM-ID-relatie verschijnt bij mogelijke relaties (BR-REL-35)
    Gegeven een relatie heeft een AIM-ID
    En de relatie is inactief
    Als de mogelijke relaties worden getoond
    Dan verschijnt de relatie in de tweede kolom (mogelijke relaties)

  Scenario: AIM-ID-relatie verwijderen: blijft inactief bewaard (BR-REL-37, S-068)
    Gegeven een actieve AIM-ID-relatie in de bestaande relaties
    Als de gebruiker de relatie selecteert en op "Verwijderen" klikt
    Dan wordt de relatie inactief (isActief = False)
    En de relatie blijft bewaard in de data
    En de relatie verschijnt NIET terug bij de mogelijke relaties

  Scenario: Export bevat actieve en inactieve DAVIE-relaties (BR-REL-36)
    Gegeven er zijn actieve en inactieve AIM-ID-relaties
    Als de gebruiker exporteert (alle data of diff)
    Dan worden zowel actieve als inactieve AIM-ID-relaties in de export opgenomen

  Scenario: Persistente relaties = actief + inactieve DAVIE (BR-EXP-04)
    Gegeven het project heeft actieve relaties en inactieve AIM-ID-relaties
    Als de gebruiker "Alle data" exporteert
    Dan bevat de export alle actieve relaties plus alle inactieve AIM-ID-relaties