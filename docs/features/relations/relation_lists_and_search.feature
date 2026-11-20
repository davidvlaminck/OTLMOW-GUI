# language: nl
Feature: Relatielijsten, attributenpaneel en zoeken (F-REL-01)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden (status OK)
    En de gebruiker is in stap 3 (relaties)

  Scenario: Scherm toont de drie kolommen met objecten (S-047)
    Gegeven de gebruiker opent stap 3
    Dan zijn de drie kolommen zichtbaar: OTL-assets, mogelijke relaties, bestaande relaties
    En elke kolom heeft een zoekbalk, een gegroepeerde lijst en een attributenpaneel

  Scenario: Object selecteren vult de mogelijke relaties en attributen (S-048)
    Gegeven de gebruiker selecteert een object in de eerste kolom
    Dan wordt de tweede kolom gevuld met mogelijke relaties voor dat object
    En het attributenpaneel van de eerste kolom toont de attributen van het geselecteerde object

  Scenario: Attributen zijn read-only (A-10 beslissing, BR-REL-01)
    Gegeven een object is geselecteerd
    En het attributenpaneel is zichtbaar
    Als de gebruiker probeert attribuutwaarden te wijzigen
    Dan is het paneel read-only
    En correcties moeten gebeuren via de bronbestanden en hervalidatie

  Scenario: Zoeken in de objectenlijst op naam (S-049)
    Gegeven er zijn objecten in de eerste kolom
    Als de gebruiker zoekt op een deel van de naam
    Dan worden alleen matchende objecten getoond
    En mappen met treffers worden automatisch uitgeklapt
    En de zoekopdracht is case-insensitive

  Scenario: Zoeken in de mogelijke relaties op TypeURI (S-049 variant)
    Gegeven er zijn mogelijke relaties in de tweede kolom
    Als de gebruiker zoekt op een TypeURI
    Dan worden alleen matchende relaties getoond

  Scenario: Zoeken in de bestaande relaties op bron- of doelnaam (S-049 variant)
    Gegeven er zijn bestaande relaties in de derde kolom
    Als de gebruiker zoekt op een bron- of doelnaam
    Dan worden alleen matchende relaties getoond

  Scenario: Wissen van zoektekst herstelt de volledige lijst (S-050)
    Gegeven een zoekopdracht is actief en de lijst is gefilterd
    Als de gebruiker het zoekveld wist
    Dan worden alle items weer getoond

  Scenario: Aantal geselecteerde items verschijnt in de mapnaam (S-051)
    Gegeven de gebruiker selecteert meerdere items in een gegroepeerde lijst
    Dan verschijnt het aantal geselecteerde items in de mapnaam

  Scenario: Selectie in eerste kolom vult zoekbalk van bestaande relaties (BR-REL-05)
    Gegeven de gebruiker klikt op een object in de eerste kolom
    Dan wordt de zoekbalk van de derde kolom (bestaande relaties) ingevuld met de objectnaam

  Scenario: Geopende kaart markeert geselecteerd object (BR-REL-06)
    Gegeven de kaart is open
    En de gebruiker selecteert een object in de lijst
    Dan wordt dat object op de kaart gemarkeerd