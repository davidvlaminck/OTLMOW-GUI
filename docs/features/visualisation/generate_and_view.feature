# language: nl
Feature: Datavisualisatie genereren en bekijken (F-VIS-01)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3, tab "data visuals"

  Scenario: Visualisatie openen voor een project met bestaande HTML (S-073)
    Gegeven het project heeft een bestaande visualisatie-HTML in de map "visuals"
    Als de gebruiker de tab "data visuals" opent
    Dan wordt de HTML in de webview geladen
    En de graaf is direct zichtbaar

  Scenario: Visualisatie openen voor een project zonder HTML: lege view en regeneratie nodig (S-074)
    Gegeven het project heeft nog geen visualisatie-HTML
    Als de gebruiker de tab "data visuals" opent
    Dan is de webview leeg
    En de gebruiker moet regenereren om de graaf te bouwen

  Scenario: Graaf bevat enkel actieve relaties (BR-VIS-01)
    Gegeven er zijn actieve en inactieve relaties in het project
    Als de visualisatie wordt gegenereerd
    Dan worden alleen actieve relaties in de graaf opgenomen
    En inactieve relaties (behalve inactieve DAVIE-relaties) zijn niet zichtbaar

  Scenario: Limietmelding bij te veel objecten (BR-VIS-04)
    Gegeven het project heeft meer dan 100.000 objecten
    Als de visualisatie wordt geopend
    Dan wordt geen graaf getoond
    En een limietmelding verschijnt

  Scenario: Visualisatie wordt bewaard per project en hergebruikt (BR-VIS-02)
    Gegeven de gebruiker heeft een visualisatie gegenereerd
    En sluit het project
    Als het project later opnieuw wordt geopend
    Dan wordt de bestaande HTML geladen
    En de visualisatie is direct zichtbaar zonder regeneratie

  Scenario: Bij projectwissel wordt de bestaande HTML geladen of de view geleegd (BR-VIS-05)
    Gegeven de gebruiker wisselt van project
    Als het nieuwe project een visualisatie-HTML heeft
    Dan wordt deze geladen
    Als het nieuwe project geen HTML heeft
    Dan wordt de view geleegd