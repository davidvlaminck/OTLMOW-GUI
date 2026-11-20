# language: nl
Feature: Template-opties en formaatbeperkingen (F-TPL-02)

  Background:
    Gegeven er is een geopend project met een geldige subset
    En de gebruiker is in stap 1, tab "aanlevertemplate"

  Scenario: Wisselen naar CSV past de opties aan (S-030)
    Gegeven het huidige formaat is Excel
    Als de gebruiker het formaat wijzigt naar CSV
    Dan wordt "Keuzelijsten toevoegen" uitgeschakeld (altijd uit voor CSV)
    En "Geometrie-attributen toevoegen" blijft aan/uit zetbaar (standaard aan)
    En "Voorbeeldassets toevoegen" blijft aan/uit zetbaar (standaard aan)
    En "Uitgebreide info" blijft aan/uit zetbaar (standaard uit)

  Scenario: Wisselen naar SDF schakelt keuzelijsten/geometrie uit maar houdt ze aan (S-031)
    Gegeven het huidige formaat is Excel
    En het platform is Windows
    Als de gebruiker het formaat wijzigt naar SDF
    Dan wordt "Keuzelijsten toevoegen" uitgeschakeld en aangevinkt (altijd aan)
    En "Geometrie-attributen toevoegen" uitgeschakeld en aangevinkt (altijd aan)
    En "Voorbeeldassets toevoegen" uitgeschakeld en uitgevinkt (altijd uit)
    En "Uitgebreide info" uitgeschakeld (niet van toepassing op SDF)

  Scenario: DAVIE-conform levert geen attribuutinfo/deprecated-markering (S-032, BR-TPL-09)
    Gegeven de gebruiker kiest "DAVIE conform" als templateformaat
    Als de template wordt gegenereerd
    Dan bevat de template geen attribuutbeschrijvingen
    En geen deprecated-markering

  Scenario: Expanded info levert attribuutinfo en deprecated-markering (S-032 variant, BR-TPL-09)
    Gegeven de gebruiker kiest "Expanded info" als templateformaat
    Als de template wordt gegenereerd
    Dan bevat de template attribuutbeschrijvingen
    En deprecated-markering (highlight_deprecated_attributes = True)

  Scenario: Aantal voorbeelden 0 wanneer de checkbox uit staat (BR-TPL-10)
    Gegeven "Voorbeeldassets toevoegen" is uitgevinkt
    Als de template wordt gegenereerd
    Dan is het aantal voorbeeldassets 0
    Ongeacht de waarde in het aantalveld

  Scenario: Aantal voorbeelden buiten 1-100 kan niet worden ingesteld (BR-TPL-10)
    Gegeven "Voorbeeldassets toevoegen" is aangevinkt
    Als de gebruiker probeert 0 of 101 in te voeren
    Dan wordt de waarde beperkt tot 1-100

  Scenario: Toon deprecated attributen checkbox is niet zichtbaar (A-01 beslissing)
    Gegeven de gebruiker is in stap 1
    Als de template-opties worden getoond
    Dan is er geen checkbox "Toon deprecated attributen" zichtbaar
    En de deprecated-markering wordt uitsluitend bepaald door de keuze DAVIE conform / Expanded info

  @windows
  Scenario: SDF-formaat is beschikbaar op Windows (BR-TPL-21)
    Gegeven het platform is Windows
    En de gebruiker is in stap 1
    Als de formaatkiezer wordt getoond
    Dan is SDF beschikbaar als formaatoptie

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