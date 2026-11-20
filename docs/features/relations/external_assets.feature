# language: nl
Feature: Externe asset toevoegen (F-REL-05)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3

  Scenario: Geldige externe asset toevoegen (S-062)
    Gegeven de gebruiker klikt op "Externe asset toevoegen"
    En vult een identificator/naam in
    En kiest een OTL-type uit de doorzoekbare lijst
    Als de gebruiker op "Submit" klikt
    Dan wordt de asset als extern object toegevoegd
    En de asset verschijnt in de eerste kolom (OTL-assets)
    En de relatiemogelijkheden worden opnieuw berekend (volledig model)
    En een quick save wordt aangemaakt

  Scenario: Lege naam: foutmelding (BR-REL-24)
    Gegeven de gebruiker opent het dialoogvenster
    En laat de identificator/naam leeg
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een foutmelding dat de naam verplicht is
    En de asset wordt niet toegevoegd

  Scenario: Bestaande naam: foutmelding (BR-REL-25)
    Gegeven er bestaat al een object met identificator "Asset_1"
    En de gebruiker probeert een externe asset met dezelfde naam toe te voegen
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een foutmelding dat de naam al bestaat
    En de asset wordt niet toegevoegd

  Scenario: Agent-type toevoegen: wordt als Agent behandeld (S-063)
    Gegeven de gebruiker kiest een type met een agentId
    Als de asset wordt toegevoegd
    Dan wordt deze als Agent-object behandeld
    En verschijnt in de eerste kolom als Agent

  Scenario: Toevoegen maakt quick save (S-064)
    Gegeven een externe asset wordt toegevoegd
    Als de actie voltooid is
    Dan wordt een quick save aangemaakt

  Scenario: Nieuwe externe asset verschijnt in de eerste kolom (S-065)
    Gegeven een externe asset is toegevoegd
    Als de gebruiker kijkt naar de eerste kolom
    Dan is de nieuwe asset zichtbaar en selecteerbaar

  Scenario: Externe assets krijgen toegekendDoor = "OTL_wizard_2" (BR-REL-26)
    Gegeven een externe asset wordt toegevoegd
    Als de asset in de data zit
    Dan heeft assetId.toegekendDoor = "OTL_wizard_2"

  Scenario: Keuzelijst bevat concrete OTL-assettypes, inclusief legacy, gesorteerd (BR-REL-27)
    Gegeven het dialoogvenster voor externe asset is open
    Als de gebruiker de typelijst opent
    Dan zijn alle concrete OTL-assettypes zichtbaar
    En legacy-types zijn opgenomen
    En de lijst is gesorteerd

  Scenario: Na toevoegen worden relatiemogelijkheden opnieuw berekend (BR-REL-28)
    Gegeven een externe asset is toegevoegd
    Als de gebruiker een object selecteert
    Dan worden de mogelijke relaties berekend met het volledige OTL-model