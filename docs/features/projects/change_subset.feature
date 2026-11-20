# language: nl
Feature: Subset wijzigen (F-PROJ-09)

  Background:
    Gegeven er is een geopend project "Project_Test" met subset "subset_a.db"
    En de gebruiker is in stap 1 (template)

  Scenario: Geldige subset kiezen: klassenlijst en relaties worden vernieuwd (S-025)
    Gegeven de gebruiker klikt op "Subset wijzigen"
    En kiest een geldige subset "subset_b.db"
    Als de gebruiker bevestigt
    Dan wordt de subset gewijzigd
    En de modelbuilder wordt vernieuwd
    En de klassenlijst in stap 1 wordt opnieuw geladen uit de nieuwe subset
    En de relaties in stap 3 worden opnieuw geïnitialiseerd
    En de UI wordt gereset
    En de laatst bewerkt-datum wordt bijgewerkt

  Scenario: Ongeldige subset kiezen: foutmelding, oude subset blijft (S-026)
    Gegeven de gebruiker klikt op "Subset wijzigen"
    En kiest een ongeldig bestand
    Als de gebruiker bevestigt
    Dan verschijnt een foutmelding
    En de oude subset "subset_a.db" blijft actief
    En de klassenlijst en relaties wijzigen niet

  Scenario: Annuleren: geen wijziging (S-026 variant)
    Gegeven de gebruiker klikt op "Subset wijzigen"
    En kiest een geldige subset
    Als de gebruiker op "Annuleren" klikt
    Dan blijft de oude subset actief
    En er gebeurt geen wijziging

  Scenario: Subsetkeuze start in de map van de huidige subset of laatst gebruikte subsetmap (BR-PROJ-29)
    Gegeven de gebruiker opent "Subset wijzigen"
    Als de subsetkiezer opent
    Dan start deze in de map van de huidige subset
    Of in de laatst gebruikte subsetmap