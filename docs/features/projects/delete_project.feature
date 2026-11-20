# language: nl
Feature: Project verwijderen (F-PROJ-04)

  Background:
    Gegeven de gebruiker is op het Home-scherm
    En er bestaat een project "Project_Te_Verwijderen"

  Scenario: Verwijderen bevestigen: project verdwijnt uit de lijst en van schijf (S-017)
    Gegeven de gebruiker klikt op het vuilnisbakicoon van "Project_Te_Verwijderen"
    En bevestigt met "Ja" in het bevestigingsvenster
    Dan verdwijnt het project uit de lijst
    En de volledige projectmap wordt van schijf verwijderd
    En alle quick saves worden verwijderd

  Scenario: Verwijderen annuleren: project blijft bestaan (S-018)
    Gegeven de gebruiker klikt op het vuilnisbakicoon van "Project_Te_Verwijderen"
    En kiest "Nee" in het bevestigingsvenster
    Dan blijft het project in de lijst
    En de projectmap blijft op schijf bestaan

  Scenario: Verwijderen is definitief zonder prullenbak (A-09 beslissing)
    Gegeven de gebruiker verwijdert een project met bevestiging
    Als de gebruiker daarna naar de projectmap kijkt
    Dan bestaat de map niet meer
    En er is geen mogelijkheid tot herstel via de applicatie
    En het originele bestand elders op schijf (indien apart bewaard) blijft onaangetast