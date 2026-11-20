# language: nl
Feature: Navigatie, stepper en onopgeslagen wijzigingen (F-APP-03, F-APP-04)

  Background:
    Gegeven de applicatie is gestart
    En een project is geopend met geldige projectbestanden (status OK)

  Scenario: Project openen zonder bestanden: stap 3/4 zijn uitgeschakeld (S-005)
    Gegeven een project zonder projectbestanden is geopend
    Als de gebruiker naar stap 3 of 4 probeert te navigeren
    Dan zijn de stappen 3 en 4 uitgeschakeld in de stepper

  Scenario: Alle bestanden valideren: stap 3/4 worden actief (S-006)
    Gegeven een project met meerdere projectbestanden
    En alle bestanden hebben status OK na validatie
    Dan zijn de stappen 3 en 4 ingeschakeld in de stepper

  Scenario: Eén bestand op ERROR: stap 3/4 worden opnieuw uitgeschakeld (S-005 variant)
    Gegeven een project met meerdere projectbestanden
    En één bestand heeft status ERROR na validatie
    Dan zijn de stappen 3 en 4 uitgeschakeld in de stepper

  Scenario: Tabs wisselen behoudt de geselecteerde klassen/relaties (S-055 variant)
    Gegeven de gebruiker is in stap 1
    En heeft klassen geselecteerd in de aanlevertemplate-tab
    Als de gebruiker wisselt naar de infotemplate-tab
    En terug naar de aanlevertemplate-tab
    Dan zijn de geselecteerde klassen behouden (gedeelde selectie, A-02)

  Scenario: Sluiten zonder onopgeslagen graaf: applicatie sluit (S-007)
    Gegeven er is een project open
    En de visualisatie heeft geen onopgeslagen wijzigingen (graph_saved_status == True)
    Als de gebruiker de applicatie sluit
    Dan sluit de applicatie direct

  Scenario: Sluiten met onopgeslagen graaf en "Back": applicatie blijft open (S-007)
    Gegeven er is een project open
    En de visualisatie heeft onopgeslagen wijzigingen (graph_saved_status == False)
    Als de gebruiker de applicatie sluit
    En in het waarschuwingsvenster "Back" kiest
    Dan blijft de applicatie open
    En het project blijft geopend

  Scenario: Terug naar Home met onopgeslagen graaf en "Continue": project wordt gesloten (S-007 variant)
    Gegeven er is een project open
    En de visualisatie heeft onopgeslagen wijzigingen
    Als de gebruiker op "Terug naar Home" klikt
    En in het waarschuwingsvenster "Continue" kiest
    Dan wordt het project gesloten
    En de gebruiker keert terug naar Home

  Scenario: Terug naar Home zonder project: direct naar Home
    Gegeven er is geen project open
    Als de gebruiker op "Terug naar Home" klikt
    Dan keert de gebruiker direct terug naar Home

  Scenario: Bij sluiten worden lopende asynchrone taken geannuleerd (BR-UI-07)
    Gegeven er loopt een asynchrone taak (bijv. validatie of export)
    Als de gebruiker de applicatie sluit
    Dan wordt de asynchrone taak geannuleerd

  Scenario: Bij terugkeer naar Home worden gecachte exportbestandsnamen gereset (BR-UI-08)
    Gegeven de gebruiker heeft een exportbestandsnaam gekozen in stap 4
    Als de gebruiker terugkeert naar Home
    Dan is de gecachte exportbestandsnaam gereset