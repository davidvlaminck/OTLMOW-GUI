# language: nl
Feature: Relatie toevoegen (F-REL-03)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3
    En een object is geselecteerd in de eerste kolom
    En er zijn mogelijke relaties zichtbaar in de tweede kolom

  Scenario: Eén relatie toevoegen (S-057)
    Gegeven de gebruiker selecteert één mogelijke relatie
    Als de gebruiker op "Relatie toevoegen" klikt
    Dan verhuist de relatie naar de bestaande relaties (derde kolom)
    En de relatie krijgt isActief = True
    En de relatiemap wordt uitgeklapt
    En de toegevoegde relatie wordt gemarkeerd
    En een quick save wordt aangemaakt
    En de visualisatie wordt als verouderd gemarkeerd

  Scenario: Meerdere relaties tegelijk toevoegen (S-058)
    Gegeven de gebruiker selecteert meerdere mogelijke relaties
    Als de gebruiker op "Relatie toevoegen" klikt
    Dan worden alle geselecteerde relaties toegevoegd
    En de quick save bevat alle nieuwe relaties

  Scenario: Relatie toevoegen zonder selectie: knop uit (BR-REL-17)
    Gegeven geen mogelijke relaties zijn geselecteerd
    Als de gebruiker kijkt naar de knop "Relatie toevoegen"
    Dan is de knop uitgeschakeld

  Scenario: HeeftBetrokkene toevoegen: roldialoog verschijnt (BR-REL-16, S-059)
    Gegeven de gebruiker selecteert een HeeftBetrokkene-relatie
    Als de gebruiker op "Relatie toevoegen" klikt
    Dan verschijnt een dialoogvenster om een rol te kiezen uit KlBetrokkenheidRol
    En enkel rollen met status "ingebruik" zijn selecteerbaar
    Als de gebruiker een rol kiest en bevestigt
    Dan krijgt de relatie die rol en wordt toegevoegd
    Als de gebruiker annuleert
    Dan wordt de relatie niet toegevoegd

  Scenario: Toegevoegde relatie krijgt toegekendDoor = "OTL_wizard_2" (BR-REL-18)
    Gegeven een relatie wordt toegevoegd via de wizard
    Als de relatie in de bestaande relaties staat
    Dan heeft de relatie toegekendDoor = "OTL_wizard_2"

  Scenario: Verouderde selectie wordt genegeerd (BR-REL-15)
    Gegeven de gebruiker heeft een relatie geselecteerd
    En de lijst met mogelijke relaties wordt tussen selectie en klik op "Toevoegen" opnieuw opgebouwd
    Als de gebruiker op "Relatie toevoegen" klikt
    Dan wordt de verouderde selectie genegeerd
    En er verschijnt geen fout