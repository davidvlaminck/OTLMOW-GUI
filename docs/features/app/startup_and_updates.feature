# language: nl
Feature: Applicatiestart en updatecontrole (F-APP-01)

  Background:
    Gegeven de applicatiebestanden zijn aanwezig
    En de instellingenmap "~/OTLWizardProjects" bestaat

  Scenario: Opstarten zonder beschikbare updates (S-001)
    Gegeven er is geen internetverbinding
    Als de applicatie start
    Dan verschijnt het Home-scherm met de projectenlijst
    En er verschijnt geen update-suggestievenster
    En de fout wordt gelogd

  Scenario: Opstarten met een nieuwe Wizard-versie beschikbaar (S-002)
    Gegeven er is internetverbinding
    En de GitHub-release heeft een hogere versie dan de geïnstalleerde
    Als de applicatie start
    Dan verschijnt het Home-scherm
    En een update-suggestievenster toont de lokale en nieuwe versie

  Scenario: Opstarten met verouderd OTL-model (S-003)
    Gegeven er is internetverbinding
    En de lokale otlmow_model-bibliotheek is ouder dan de GitHub-versie
    Als de applicatie start
    Dan verschijnt een waarschuwing/suggestie om het model te verversen
    En de applicatie crasht niet

  Scenario: Opstarten zonder internet (S-004)
    Gegeven er is geen internetverbinding
    Als de applicatie start
    Dan start de applicatie normaal
    En de netwerkfout bij updatecontrole wordt gelogd
    En de applicatie wordt niet geblokkeerd

  Scenario: Standaardtaal is Nederlands bij ontbrekende instelling (BR-APP-03)
    Gegeven er is geen geldige taalinstelling in settings.json
    Als de applicatie start
    Dan is de UI in het Nederlands