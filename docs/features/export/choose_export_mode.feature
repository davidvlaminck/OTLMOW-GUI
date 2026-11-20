# language: nl
Feature: Exportmodus kiezen (F-EXP-01)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden (status OK)
    En de gebruiker is in stap 4 (exporteren)

  Scenario: "All data" kiezen toont het bijhorende formulier (S-081)
    Gegeven de gebruiker is in stap 4
    Als de gebruiker de radiobutton "All data" selecteert
    Dan wordt het exportformulier voor alle data getoond
    En het vergelijkingsformulier is verborgen

  Scenario: "Without unedited data" kiezen toont het vergelijkingsformulier (S-082)
    Gegeven de gebruiker is in stap 4
    Als de gebruiker de radiobutton "Without unedited data" selecteert
    Dan wordt het vergelijkingsformulier getoond
    En het exportformulier voor alle data is verborgen

  Scenario: Wisselen tussen modi verbergt het vorige formulier (BR-EXP-02)
    Gegeven de gebruiker heeft "All data" geselecteerd
    En het bijhorende formulier is zichtbaar
    Als de gebruiker "Without unedited data" selecteert
    Dan is het "All data" formulier verborgen
    En het vergelijkingsformulier is zichtbaar

  Scenario: Export is alleen beschikbaar in stap 4 bij geldige projectbestanden (BR-EXP-03)
    Gegeven er is een project zonder geldige bestanden
    Als de gebruiker naar stap 4 probeert te navigeren
    Dan is stap 4 uitgeschakeld
    En de export is niet bereikbaar