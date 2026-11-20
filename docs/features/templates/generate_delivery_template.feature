# language: nl
Feature: Aanlevertemplate genereren (F-TPL-03)

  Background:
    Gegeven er is een geopend project met een geldige subset
    En de gebruiker is in stap 1, tab "aanlevertemplate"
    En er is minstens één klasse geselecteerd

  Scenario: Excel-template genereren met alle klassen (S-032)
    Gegeven alle klassen zijn geselecteerd
    En het formaat is Excel
    En de gebruiker kiest een opslaglocatie
    Als de gebruiker op "Exporteer" klikt
    Dan wordt de template asynchroon gegenereerd
    En na succes opent het Excel-bestand automatisch
    En de template bevat alle geselecteerde klassen met de gekozen opties

  Scenario: Template genereren met een subset van klassen (S-032 variant)
    Gegeven een subset van klassen is geselecteerd
    Als de gebruiker de template genereert
    Dan bevat de template enkel de geselecteerde klassen

  Scenario: Template genereren met keuzelijsten/geometrie/voorbeelden (S-032 variant)
    Gegeven de opties "Keuzelijsten", "Geometrie" en "Voorbeeldassets" zijn aangevinkt
    En het aantal voorbeelden is ingesteld op 5
    Als de template wordt gegenereerd
    Dan bevat de template keuzelijsten, geometrie-attributen en 5 voorbeeldassets per klasse

  Scenario: Export naar een bestand dat openstaat in Excel: melding (S-034)
    Gegeven het doelbestand staat al open in Excel en is niet beschrijfbaar
    Als de gebruiker probeert te exporteren naar dat bestand
    Dan verschijnt een toelichtende foutmelding
    En de export wordt niet overschreven

  Scenario: Genereren zonder geselecteerde klassen: niet mogelijk (BR-TPL-14)
    Gegeven geen klassen zijn geselecteerd
    Als de gebruiker kijkt naar de exportknop
    Dan is de exportknop uitgeschakeld
    En de export kan niet gestart worden

  Scenario: Agent wordt niet in het template opgenomen (BR-TPL-13, A-15 beslissing)
    Gegeven de klasse Agent staat in de subset
    En de gebruiker selecteert alle klassen
    Als de template wordt gegenereerd
    Dan is Agent niet in het gegenereerde template aanwezig

  Scenario: Generatiefouten worden gelogd en als fout getoond (BR-TPL-16)
    Gegeven er treedt een onverwachte fout op tijdens generatie
    Als de generatie faalt
    Dan wordt de fout gelogd
    En een foutmelding wordt aan de gebruiker getoond

  Scenario: Na export opent het bestand of de map (BR-TPL-17)
    Gegeven de template is succesvol gegenereerd
    Als het formaat Excel is
    Dan opent het bestand automatisch
    Als het formaat CSV is
    Dan opent de map met het bestand