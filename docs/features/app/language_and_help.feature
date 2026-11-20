# language: nl
Feature: Taal, instellingen en help (F-APP-02)

  Background:
    Gegeven de applicatie is gestart
    En het Home-scherm is zichtbaar

  Scenario: Wijzigen naar Engels leidt tot herstartmelding en opgeslagen taal (S-004)
    Gegeven de huidige taal is Nederlands
    Als de gebruiker op het tandwiel in de header klikt
    En "Engels" kiest
    Dan wordt de taal in settings.json opgeslagen als "en"
    En een melding vraagt de applicatie opnieuw te starten
    Na herstart is de UI in het Engels

  Scenario: Ontbrekende vertaling valt terug op de brontaal (BR-SET-02)
    Gegeven de taal is Engels
    En een vertaalsleutel ontbreekt in het Engels-vertalingsbestand
    Als de bijbehorende UI-tekst wordt getoond
    Dan wordt de originele (Nederlandse) tekst getoond

  Scenario: About toont de juiste versie en contactgegevens (BR-SET-03)
    Gegeven de gebruiker opent het helpmenu
    En kiest "About"
    Dan verschijnt een venster met de applicatieversie
    En de contactgegevens van Team BIM

  Scenario: Report error toont contactadres (BR-SET-03)
    Gegeven de gebruiker opent het helpmenu
    En kiest "Fout melden"
    Dan verschijnt een venster met het contactadres van Team BIM

  @windows
  Scenario: Logs openen op Windows (BR-SET-04)
    Gegeven de gebruiker opent het helpmenu
    En kiest "Logs"
    Dan opent de systeemverkenner met de nieuwste logfile geselecteerd

  @linux
  Scenario: Logs openen op Linux (A-08 beslissing)
    Gegeven de gebruiker opent het helpmenu
    En kiest "Logs"
    Dan opent de bestandsbeheerder in de logmap (best-effort)

  @macos
  Scenario: Logs openen op macOS (A-08 beslissing)
    Gegeven de gebruiker opent het helpmenu
    En kiest "Logs"
    Dan opent Finder met de logfile geselecteerd