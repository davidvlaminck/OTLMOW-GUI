# language: nl
Feature: HeeftBetrokkene-rol definiëren (F-REL-06)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3
    En een object is geselecteerd
    En er is een HeeftBetrokkene-relatie mogelijk

  Scenario: HeeftBetrokkene toevoegen met gekozen rol (S-066)
    Gegeven de gebruiker selecteert een HeeftBetrokkene-relatie
    En klikt op "Relatie toevoegen"
    Als de roldialoog verschijnt
    En de gebruiker kiest een rol uit KlBetrokkenheidRol
    En bevestigt
    Dan krijgt de relatie de gekozen rol
    En de relatie wordt toegevoegd aan de bestaande relaties

  Scenario: Meerdere HeeftBetrokkene-relaties in één keer voorzien van een rol (BR-REL-31)
    Gegeven de gebruiker selecteert meerdere HeeftBetrokkene-relaties
    En klikt op "Relatie toevoegen"
    Als de roldialoog verschijnt
    En de gebruiker kiest een rol
    En bevestigt
    Dan krijgen alle geselecteerde relaties dezelfde rol
    En worden alle toegevoegd

  Scenario: Annuleren voegt niets toe (BR-REL-31 variant)
    Gegeven de roldialoog is open
    Als de gebruiker annuleert
    Dan worden geen van de geselecteerde HeeftBetrokkene-relaties toegevoegd
    En de UI wordt ververst

  Scenario: Buiten gebruik zijnde rol is niet selecteerbaar (BR-REL-30)
    Gegeven de roldialoog is open
    Als de gebruiker kijkt naar de beschikbare rollen
    Dan zijn enkel rollen met status "ingebruik" selecteerbaar
    En rollen met een andere status zijn niet zichtbaar of uitgeschakeld

  Scenario: Venster toont betrokken bron- en doelidentificatoren (BR-REL-32)
    Gegeven de roldialoog is open
    Als de gebruiker kijkt naar het venster
    Dan zijn de identificatoren van het bron- en doelobject zichtbaar