# language: nl
Feature: Enkel gewijzigde data exporteren (diff) (F-EXP-03)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 4
    En de exportmodus "Without unedited data" is geselecteerd

  Scenario: Origineel bestand toevoegen (S-086)
    Gegeven de gebruiker klikt op "Voeg origineel bestand toe"
    En kiest een origineel aanleverbestand
    Als het bestand wordt toegevoegd
    Dan verschijnt het in de originelenlijst met een verwijderknop
    En de knoppen "Toon verschillen" en "Exporteer" worden ingeschakeld

  Scenario: Meerdere originele bestanden toevoegen (S-087)
    Gegeven de gebruiker voegt meerdere originele bestanden toe
    Als de bestanden worden toegevoegd
    Dan worden ze allemaal in de lijst getoond
    En bij vergelijking worden ze samengevoegd tot één vergelijkingsbasis (BR-EXP-16)

  Scenario: Bestand verwijderen uit de originelenlijst (S-088)
    Gegeven er staan originele bestanden in de lijst
    Als de gebruiker op het verwijdericoon van een bestand klikt
    Dan wordt het bestand uit de lijst verwijderd
    En de vergelijking en tabel worden gewist

  Scenario: "Toon verschillen" zonder origineel: knop uit (BR-EXP-13)
    Gegeven er zijn geen originele bestanden in de lijst
    Als de gebruiker kijkt naar de knop "Toon verschillen"
    Dan is de knop uitgeschakeld

  Scenario: Gewijzigd attribuut wordt getoond met oud/nieuw (BR-EXP-10, S-089)
    Gegeven er is een origineel bestand toegevoegd
    Als de gebruiker op "Toon verschillen" klikt
    Dan worden de originele bestanden ingelezen en gevalideerd
    En een tabel toont per verschil: volgnummer, identificator, actie, attribuut, oude waarde, nieuwe waarde
    En gewijzigde attributen worden als "attribute changed" getoond met oude en nieuwe waarde per subattribuut

  Scenario: Nieuw asset wordt getoond als "asset added" (BR-EXP-11, S-090)
    Gegeven er is een asset in de huidige data die niet in de originele bestanden zit
    Als de verschillen worden getoond
    Dan wordt deze asset als "asset added" gerapporteerd

  Scenario: Nieuwe relatie wordt getoond als "relation added" (BR-EXP-11, S-091)
    Gegeven er is een relatie in de huidige data die niet in de originele bestanden zit
    Als de verschillen worden getoond
    Dan wordt deze relatie als "relation added" gerapporteerd

  Scenario: Meerdere complexe subattributen worden als aparte regels getoond (BR-EXP-10)
    Gegeven een complex attribuut (bijv. geometrie) heeft meerdere subattributen gewijzigd
    Als de verschillen worden getoond
    Dan wordt elke gewijzigde subattribuut als aparte regel getoond

  Scenario: Ongeldig origineel bestand toont foutentabel (BR-EXP-14)
    Gegeven een origineel bestand bevat validatiefouten
    Als de gebruiker op "Toon verschillen" klikt
    Dan wordt een foutentabel getoond in plaats van de verschillentabel
    En de export kan niet uitgevoerd worden

  Scenario: Exporteren van verschillen naar Excel/CSV (S-092)
    Gegeven de verschillen zijn getoond
    En de gebruiker kiest formaat en opslaglocatie
    Als de gebruiker op "Exporteer" klikt
    Dan wordt een bestand aangemaakt met enkel de gewijzigde assets en relaties
    En na succes opent de map met het exportbestand

  Scenario: Exporteren van verschillen zonder verschillen: melding "geen data" (BR-EXP-07)
    Gegeven de huidige data is identiek aan de originele bestanden
    Als de gebruiker op "Exporteer" klikt
    Dan verschijnt de melding "Er is geen data om te exporteren"

  Scenario: "Lege velden" wist de lijst en tabel (S-093)
    Gegeven er staan originele bestanden in de lijst
    En de vergelijking is getoond
    Als de gebruiker op "Lege velden" klikt
    Dan wordt de originelenlijst gewist
    En de vergelijkingstabel gewist
    En de knoppen "Toon verschillen" en "Exporteer" worden uitgeschakeld

  Scenario: Preview is optioneel; export herberekent diff op moment van exporteren (A-04 beslissing)
    Gegeven de gebruiker heeft originele bestanden toegevoegd
    En heeft NIET op "Toon verschillen" geklikt
    Als de gebruiker direct op "Exporteer" klikt
    Dan wordt de diff herberekend tegen de originele bestanden
    En de export bevat de juiste verschillen
    En de preview is niet vereist

  Scenario: Gewijzigd origineel bestand blokkeert export met melding (A-04 beslissing)
    Gegeven de gebruiker heeft een origineel bestand toegevoegd
    En het origineel bestand wordt na toevoegen gewijzigd op schijf
    Als de gebruiker op "Exporteer" klikt
    Dan blokkeert de export met de melding "Fout in originele bestanden"
    En de gebruiker moet het origineel bestand corrigeren of opnieuw toevoegen