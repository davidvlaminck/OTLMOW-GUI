# language: nl
Feature: Kaartvisualisatie (F-MAP-01)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3
    Er zijn assets met geometrie in de eerste kolom

  Scenario: Kaart openen met assets (S-069)
    Gegeven de gebruiker klikt op de kaartknop naast de relatielijsten
    Als het kaartvenster opent
    Dan worden de assets uit de eerste kolom op de kaart getoond
    En de kaart is gegenereerd met Folium in een webview

  Scenario: Kaart openen met meer dan 300 assets: limietmelding (BR-MAP-02, S-070)
    Gegeven er zijn meer dan 300 assets in de eerste kolom
    Als de gebruiker probeert de kaart te openen
    Dan wordt geen kaart getoond
    En een limietmelding verschijnt

  Scenario: Asset op de kaart aanklikken selecteert het in de lijst (BR-MAP-04, S-071)
    Gegeven de kaart is open
    En de gebruiker klikt op een asset op de kaart
    Dan wordt dat object geselecteerd in de eerste kolom
    En de mogelijke relaties en attributen worden bijgewerkt

  Scenario: Asset in de lijst aanklikken markeert het op de kaart (BR-MAP-03)
    Gegeven de kaart is open
    En de gebruiker selecteert een asset in de eerste kolom
    Dan wordt die asset op de kaart gemarkeerd

  Scenario: Kaart verversen na relatie-/assetwijziging (S-072)
    Gegeven de kaart is open
    En de gebruiker voegt een relatie toe of verwijdert een asset
    Als de gebruiker op "Refresh" klikt
    Dan wordt de kaart opnieuw opgebouwd met de actuele data

  Scenario: Kaart sluiten en opnieuw openen (S-072 variant)
    Gegeven de kaart is open
    Als de gebruiker de kaart sluit
    En later opnieuw opent
    Dan wordt de kaart opnieuw gegenereerd op basis van de huidige data

  Scenario: Kaart gebruikt de huidige, gefilterde inhoud van de eerste kolom (BR-MAP-01)
    Gegeven de gebruiker heeft een zoekfilter actief in de eerste kolom
    Als de kaart wordt geopend
    Dan worden alleen de zichtbare (gefilterde) assets op de kaart getoond