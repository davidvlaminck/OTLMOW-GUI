# language: nl
Feature: Validatiefeedback en foutrapportage (F-DATA-03)

  Background:
    Gegeven er is een geopend project met projectbestanden
    En de gebruiker is in stap 2

  Scenario: Succes toont aantallen per type en totaal (S-051)
    Gegeven de validatie is succesvol
    Als de feedbacklijst wordt getoond
    Dan wordt per OTL-type het aantal ingeladen objecten getoond
    En het totaal aantal conforme objecten wordt getoond
    En de kleur is groen

  Scenario: Fout toont documentnaam en foutboodschap (S-052)
    Gegeven de validatie heeft fouten
    Als de feedbacklijst wordt getoond
    Dan wordt per fout de documentnaam en foutboodschap getoond
    En de kleur is rood

  Scenario: Meerdere fouten in één bestand worden allemaal getoond (S-053)
    Gegeven één bestand bevat meerdere validatiefouten
    Als de feedbacklijst wordt getoond
    Dan worden alle fouten van dat bestand getoond

  Scenario: Statusiconen komen overeen met de bestandsstatus (BR-DATA-17)
    Gegeven bestanden met statussen OK, WARNING, ERROR
    Als de lijst wordt getoond
    Dan toont OK een groen vinkje
    En WARNING een oranje waarschuwing
    En ERROR een rood kruis

  Scenario: Foutboodschappen worden vertaald (BR-DATA-15)
    Gegeven de taal is Engels
    En er zijn validatiefouten
    Als de feedbacklijst wordt getoond
    Dan zijn de foutboodschappen in het Engels

  Scenario: Feedback is read-only; corrigeren via bronbestand (BR-DATA-16, A-10 beslissing)
    Gegeven er zijn validatiefouten
    Als de gebruiker de feedback bekijkt
    Dan is de feedback read-only
    En correcties moeten gebeuren in het bronbestand
    En daarna opnieuw valideren

  Scenario: Bij fouten worden ook reeds ingelezen objecten getoond (S-054)
    Gegeven een bestand heeft fouten maar ook geldige rijen
    Als de feedback wordt getoond
    Dan worden de fouten getoond
    En de reeds ingelezen objecten per type worden getoond (voor zover beschikbaar)