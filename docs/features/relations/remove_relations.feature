# language: nl
Feature: Relatie verwijderen (F-REL-04)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3
    En er zijn bestaande relaties in de derde kolom

  Scenario: Eén relatie verwijderen (S-060)
    Gegeven de gebruiker selecteert één bestaande relatie
    Als de gebruiker op "Relatie verwijderen" klikt
    Dan wordt de relatie uit de actieve lijst gehaald
    En isActief wordt False
    En de relatie komt terug als mogelijke relatie (tweede kolom)
    En de bijhorende map in de mogelijke relaties wordt uitgeklapt
    En een quick save wordt aangemaakt
    En de visualisatie wordt als verouderd gemarkeerd

  Scenario: Meerdere relaties verwijderen (BR-REL-19)
    Gegeven de gebruiker selecteert meerdere bestaande relaties
    Als de gebruiker op "Relatie verwijderen" klikt
    Dan worden alle geselecteerde relaties gedeactiveerd
    En alle komen terug als mogelijke relaties

  Scenario: Verwijderde gegenereerde relatie verschijnt terug bij mogelijke relaties (BR-REL-20)
    Gegeven een gegenereerde relatie (geen AIM-ID) wordt verwijderd
    Als de actie voltooid is
    Dan verschijnt de relatie weer in de lijst met mogelijke relaties

  Scenario: Verwijderde AIM-ID-relatie blijft inactief bewaard (BR-REL-21, S-061)
    Gegeven een AIM-ID-relatie (DAVIE-relatie) wordt verwijderd
    Als de actie voltooid is
    Dan blijft de relatie als inactief record bewaard
    En de relatie verschijnt NIET terug bij de mogelijke relaties
    En bij export en quick save wordt de inactieve AIM-ID-relatie meegenomen

  Scenario: Verwijderen zonder selectie: knop uit (BR-REL-22)
    Gegeven geen bestaande relaties zijn geselecteerd
    Als de gebruiker kijkt naar de knop "Relatie verwijderen"
    Dan is de knop uitgeschakeld

  Scenario: Verwijderen maakt quick save en markeert visualisatie verouderd (S-061 variant)
    Gegeven een relatie wordt verwijderd
    Als de actie voltooid is
    Dan wordt een quick save aangemaakt
    En de visualisatiestatus wordt verouderd