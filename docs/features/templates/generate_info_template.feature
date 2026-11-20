# language: nl
Feature: Infotemplate genereren (F-TPL-04)

  Background:
    Gegeven er is een geopend project met een geldige subset
    En de gebruiker is in stap 1, tab "infotemplate"

  Scenario: Infotemplate genereren met geselecteerde klassen (S-035, A-03 beslissing)
    Gegeven de gebruiker heeft klassen geselecteerd (gedeelde selectie met aanlevertemplate)
    En de gebruiker kiest een opslaglocatie
    Als de gebruiker op "Exporteer" klikt
    Dan wordt de infotemplate gegenereerd via InfotemplateGenerator
    En de infotemplate bevat **enkel de geselecteerde klassen** (class_uris_filter wordt doorgegeven)
    En de map met het bestand wordt geopend

  Scenario: Infotemplate fallback naar volledige subset bij lege selectie (A-03 beslissing)
    Gegeven de gebruiker heeft geen klassen geselecteerd
    En de exportknop is uitgeschakeld (BR-TPL-20)
    Als de gebruiker toch zou exporteren (via edge case)
    Dan bevat de infotemplate alle concrete klassen uit de subset (fallback gedrag)

  Scenario: Selectie wijzigen in de infotab beïnvloedt de aanlevertemplate-selectie (A-02 beslissing)
    Gegeven de gebruiker is in de infotemplate-tab
    En wijzigt de klassenselectie
    Als de gebruiker wisselt naar de aanlevertemplate-tab
    Dan is de selectie gesynchroniseerd (gedeelde selectie, live sync)

  Scenario: Infotemplate exporteren zonder selectie is niet mogelijk (BR-TPL-20)
    Gegeven geen klassen zijn geselecteerd
    Als de gebruiker kijkt naar de exportknop
    Dan is de exportknop uitgeschakeld

  Scenario: Infotemplate gebruikt dezelfde subset als aanlevertemplate (BR-TPL-18)
    Gegeven de gebruiker heeft de subset gewijzigd
    Als de infotemplate wordt gegenereerd
    Dan gebruikt deze de huidige subset van het project