# language: nl
Feature: Mogelijke relaties bepalen (F-REL-02)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3
    En een object is geselecteerd in de eerste kolom

  Scenario: Object selecteren toont mogelijke relaties uit de subset (S-052)
    Gegeven er is een object geselecteerd
    En er zijn geen externe assets of Agent-objecten
    En "Toon alle OTL-relaties" is uit
    Als de mogelijke relaties worden geladen
    Dan worden de relatietypes bepaald op basis van de subset
    En per kandidaat-partner wordt een relatieobject aangemaakt (tenzij al bestaand)

  Scenario: Object zonder mogelijke relaties toont een lege/plaatshoudermelding (S-053)
    Gegeven het geselecteerde object heeft geen mogelijke relaties in de subset
    Als de lijst wordt getoond
    Dan is de lijst leeg of toont een plaatshouder

  Scenario: Externe asset aanwezig: relaties uit volledig model (BR-REL-11, S-054)
    Gegeven er is een externe asset in de eerste kolom
    Of een Agent-object
    Als de mogelijke relaties worden geladen
    Dan wordt het volledige OTL-model gebruikt in plaats van de subset

  Scenario: "Toon alle OTL-relaties" aanzetten verruimt de lijst (BR-REL-12, S-055)
    Gegeven "Toon alle OTL-relaties" is uit
    En de gebruiker schakelt het aan
    Als de lijst wordt ververst
    Dan worden relaties uit het volledige OTL-model getoond
    En de lijst is ruimer

  Scenario: Bestaande relatie wordt niet opnieuw als mogelijk aangeboden (BR-REL-08, S-056)
    Gegeven er bestaat al een actieve relatie tussen object A en object B
    Als de mogelijke relaties voor object A worden getoond
    Dan wordt de relatie naar object B niet als mogelijke reliteit getoond

  Scenario: Richting wordt gerespecteerd en met pijlicoon getoond (BR-REL-09)
    Gegeven een relatie heeft richting "Source -> Destination"
    Als de relatie in de lijst verschijnt
    Dan wordt de richting getoond met het bijhorende pijlicoon

  Scenario: Legacy-asset biedt HoortBij aan (BR-REL-10)
    Gegeven er is een legacy-asset (https://lgc...) geselecteerd
    Als de mogelijke relaties worden geladen
    Dan wordt een HoortBij-relatie naar concrete OTL-klassen aangeboden

  Scenario: Ontbrekende relatiepartner wordt als externe asset toegevoegd (BR-REL-11)
    Gegeven een bestaande relatie heeft een ontbrekende bron- of doelasset
    Als de lijsten worden opgebouwd
    Dan wordt de ontbrekende asset automatisch als externe asset aangemaakt

  Scenario: Geselecteerd object zelf wordt nooit als partner getoond (BR-REL-07)
    Gegeven er is een object geselecteerd
    Als de mogelijke relaties worden getoond
    Dan staat het geselecteerde object zelf niet in de lijst met mogelijke partners