# language: nl
Feature: Klassenlijst en klassenselectie (F-TPL-01)

  Background:
    Gegeven er is een geopend project met een geldige subset
    En de gebruiker is in stap 1 (template)

  Scenario: Openen van stap 1 vult de klassenlijst uit de subset (S-027)
    Gegeven de gebruiker opent stap 1
    Dan worden de klassen uit de subset geladen
    En relatieklassen en abstracte klassen worden uitgefilterd
    En de klassen worden alfabetisch getoond, gegroepeerd per klassenaam
    En standaard zijn alle klassen geselecteerd

  Scenario: Agent in lijst is niet selecteerbaar (S-028, A-15 beslissing)
    Gegeven de subset bevat de klasse "Agent"
    Als de klassenlijst wordt getoond
    Dan is "Agent" zichtbaar in de lijst
    Maar is grijs en niet-selecteerbaar
    En de tooltip geeft aan dat Agent niet in een template mag
    En bij "Alles selecteren" wordt Agent overgeslagen
    En dit geldt voor zowel aanlevertemplate als infotemplate

  Scenario: Alles deselecteren schakelt de exportknop uit (S-029)
    Gegeven alle klassen zijn geselecteerd
    Als de gebruiker op "Alles deselecteren" klikt
    Dan zijn geen klassen geselecteerd
    En de exportknop is uitgeschakeld

  Scenario: Eén klasse selecteren schakelt de exportknop in (S-029 variant)
    Gegeven geen klassen zijn geselecteerd
    Als de gebruiker één klasse selecteert
    Dan wordt de exportknop ingeschakeld

  Scenario: Selectie is gedeeld tussen aanlevertemplate- en infotemplate-tab (A-02 beslissing)
    Gegeven de gebruiker heeft klassen geselecteerd in de aanlevertemplate-tab
    Als de gebruiker wisselt naar de infotemplate-tab
    Dan zijn dezelfde klassen geselecteerd
    En de teller toont hetzelfde aantal
    En een wijziging in de ene tab wordt direct zichtbaar in de andere tab (live sync)

  Scenario: Subset zonder klassen toont de juiste melding (BR-TPL-05)
    Gegeven de subset levert geen concrete klassen op
    Als de gebruiker stap 1 opent
    Dan toont de klassenlijst een "geen klassen gevonden"-melding
    En de exportknop is uitgeschakeld

  Scenario: Subsetswijziging laadt de lijst volledig opnieuw (BR-TPL-04)
    Gegeven de gebruiker wijzigt de subset in stap 1
    Als de nieuwe subset wordt geladen
    Dan wordt de klassenlijst volledig opnieuw opgebouwd
    En de selectie wordt gereset (alles geselecteerd in de nieuwe lijst)