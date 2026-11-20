# language: nl
Feature: Documenten valideren (F-DATA-02)

  Background:
    Gegeven er is een geopend project met minstens één projectbestand
    En de gebruiker is in stap 2

  Scenario: Alle bestanden geldig: groene feedback, stap 3/4 actief, quick save gemaakt (S-043)
    Gegeven alle projectbestanden zijn OTL-conform
    Als de gebruiker op "Valideer" klikt
    Dan worden alle bestanden ingelezen en omgezet naar OTL-objecten
    En de status van alle bestanden wordt OK
    En er verschijnt groene feedback met aantallen per type en totaal
    En de objecten worden aan het relatiedomein doorgegeven
    En een quick save wordt aangemaakt
    En stap 3 en 4 worden ingeschakeld

  Scenario: Eén bestand met een OTL-fout: rode feedback, bestand ERROR, stap 3/4 uit (S-044)
    Gegeven één projectbestand bevat een OTL-fout
    Als de gebruiker op "Valideer" klikt
    Dan krijgt dat bestand status ERROR
    En er verschijnt rode feedback met documentnaam en foutboodschap
    En stap 3 en 4 blijven uitgeschakeld

  Scenario: Lege identificator: fout in de feedbacklijst (S-045)
    Gegeven een projectbestand bevat een rij met lege assetId.identificator
    Als de validatie wordt uitgevoerd
    Dan verschijnt in de feedbacklijst een fout over de lege identificator
    En het bestand krijgt status ERROR

  Scenario: Ongeldige relatie: fout in de feedbacklijst (S-046)
    Gegeven een projectbestand bevat een relatie met onbestaande bron-TypeURI
    Of een relatie met onbestaande doel-TypeURI
    Of een ongeldige combinatie bron/doel/relatietype
    Als de validatie wordt uitgevoerd
    Dan verschijnt een fout in de feedbacklijst
    En het bestand krijgt status ERROR

  Scenario: Twee rijen met hetzelfde asset-ID en aanvullende attributen: samengevoegd (S-047)
    Gegeven een projectbestand bevat twee rijen met hetzelfde asset-ID
    En de rijen hebben aanvullende, niet-conflicterende attributen
    Als de validatie wordt uitgevoerd
    Dan worden de rijen samengevoegd tot één asset
    En het bestand krijgt status OK

  Scenario: Twee rijen met hetzelfde asset-ID en conflicterende waarden: fout (S-048)
    Gegeven een projectbestand bevat twee rijen met hetzelfde asset-ID
    En de rijen hebben conflicterende attribuutwaarden of types
    Als de validatie wordt uitgevoerd
    Dan verschijnt een fout over het samenvoegconflict
    En de betrokken bestanden krijgen status ERROR

  Scenario: Validatie zonder bestanden: knop is uitgeschakeld (BR-DATA-07)
    Gegeven er zijn geen projectbestanden
    Als de gebruiker kijkt naar de validatieknop
    Dan is de knop uitgeschakeld

  Scenario: Hervalidatie met bestaande quick save: bevestiging vereist (BR-PROJ-26)
    Gegeven er is een bestaande quick save
    En de gebruiker start een nieuwe validatie
    Als het bevestigingsvenster verschijnt
    En de gebruiker bevestigt
    Dan wordt de validatie uitgevoerd
    En de oude quick save wordt vervangen
    Als de gebruiker annuleert
    Dan wordt de validiteit niet uitgevoerd

  Scenario: Ontbrekend bestand vóór validatie: melding en geen validatie (S-050)
    Gegeven een projectbestand dat in de lijst staat, ontbreekt op schijf
    Als de gebruiker op "Valideer" klikt
    Dan verschijnt een melding over het ontbrekende bestand
    En de validatie start niet

  Scenario: Fouten in asynchrone taken worden via exception handler getoond (BR-5.3)
    Gegeven er treedt een onverwachte fout op tijdens validatie
    Als de validatie faalt
    Dan wordt de fout gelogd
    En via ErrorScreen aan de gebruiker getoond
    En de foutmelding wordt naar het klembord gekopieerd