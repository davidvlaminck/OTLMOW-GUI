# language: nl
Feature: Incrementele updates en verouderd-indicator (F-VIS-04)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de visualisatie is gegenereerd en up-to-date

  Scenario: Relatie toevoegen toont "verouderd" (S-080)
    Gegeven de visualisatie is up-to-date
    Als de gebruiker in stap 3 een relatie toevoegt of verwijdert
    En vervolgens de tab "data visuals" opent
    Dan wordt de verouderd-indicator getoond
    En de incrementele update wordt uitgevoerd (alleen de gewijzigde relaties worden toegevoegd/verwijderd in de bestaande graaf)

  Scenario: Visualisatietab openen werkt incrementeel bij (BR-VIS-16)
    Gegeven er zijn relatiewijzigingen sinds de laatste visualisatie
    Als de gebruiker de tab "data visuals" opent
    Dan worden alleen de nieuwe/verwijderde relaties verwerkt in de bestaande graaf
    En geen volledige regeneratie wordt uitgevoerd

  Scenario: Na update verdwijnt de verouderd-melding (BR-VIS-18)
    Gegeven de verouderd-indicator is zichtbaar
    En de gebruiker opent de visualisatietab
    Als de incrementele update voltooid is
    Dan verdwijnt de verouderd-indicator
    En de status is up-to-date

  Scenario: Relatie verwijderen en opnieuw toevoegen maakt de wachtrij leeg (BR-VIS-17)
    Gegeven een relatie wordt verwijderd
    En daarna weer opnieuw toegevoegd (dezelfde relatie)
    Als de visualisatietab wordt geopend
    Dan staat die relatie niet in de update-wachtrij
    En de graaf verandert niet voor die relatie

  Scenario: Relatie toevoegen en daarna verwijderen maakt de wachtrij leeg (BR-VIS-17)
    Gegeven een relatie wordt toegevoegd
    En daarna weer verwijderd
    Als de visualisatietab wordt geopend
    Dan staat die relatie niet in de update-wachtrij