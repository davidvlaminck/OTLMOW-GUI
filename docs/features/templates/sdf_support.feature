# language: nl
Feature: SDF-ondersteuning (F-TPL-05)

  Background:
    Gegeven het platform is Windows
    En FDO Toolbox is geïnstalleerd
    En er is een geopend project met een geldige subset

  @windows
  Scenario: SDF-formaat is beschikbaar in template-opties (BR-TPL-21, A-11 beslissing)
    Gegeven de gebruiker is in stap 1
    Als de formaatkiezer wordt getoond
    Dan is SDF beschikbaar als formaatoptie
    En de SDF-specifieke instellingen zijn actief (keuzelijsten en geometrie altijd aan)

  @linux
  Scenario: SDF-formaat is niet beschikbaar op Linux (A-11 beslissing, S-036)
    Gegeven het platform is Linux
    En de gebruiker is in stap 1
    Als de formaatkiezer wordt getoond
    Dan is SDF niet beschikbaar als formaatoptie

  @macos
  Scenario: SDF-formaat is niet beschikbaar op macOS (A-11 beslissing)
    Gegeven het platform is macOS
    En de gebruiker is in stap 1
    Als de formaatkiezer wordt getoond
    Dan is SDF niet beschikbaar als formaatoptie

  @windows
  Scenario: SDF genereren zonder FDO Toolbox vraagt installatie (BR-TPL-22, S-037)
    Gegeven het platform is Windows
    En FDO Toolbox is **niet** geïnstalleerd
    En de gebruiker kiest SDF als formaat en probeert te genereren
    Dan verschijnt een melding om FDO Toolbox te installeren
    En de installerlocatie wordt geopend

  @windows
  Scenario: SDF inladen splitst het bestand per klasse in CSV (BR-TPL-24, S-038)
    Gegeven de gebruiker voegt een SDF-bestand toe in stap 2
    Als het bestand wordt ingelezen
    Dan wordt het SDF-bestand opgesplitst in één CSV-bestand per klasse
    En de CSV-bestanden worden in de projectmap geplaatst

  @windows
  Scenario: SDF-objecten bevatten geen FeatId na inladen (BR-TPL-25, S-039)
    Gegeven een SDF-bestand met FeatId-attributen wordt ingeladen
    Als de conversie naar CSV voltooid is
    Dan bevat het resultaat geen FeatId-attribuut meer