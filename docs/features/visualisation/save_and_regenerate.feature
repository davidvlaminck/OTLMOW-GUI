# language: nl
Feature: Visualisatie bewaren en regenereren (F-VIS-03)

  Background:
    Gegeven er is een geopend project met geldige projectbestanden
    En de gebruiker is in stap 3, tab "data visuals"
    En de visualisatie is geladen

  Scenario: Wijzigingen bewaren in de HTML (S-077)
    Gegeven de gebruiker heeft de graaf gewijzigd (nodes versleept, collecties aangepast)
    En de status is "Changes are not saved"
    Als de gebruiker op "Bewaar wijzigingen" klikt
    Dan wordt de JavaScript-graaf gevraagd om nodes/edges naar Python te sturen
    En Python vervangt de node-/edge-data in de HTML
    En de supportdata wordt opgeslagen in visuals_python_support_data.json
    En de status gaat naar "Changes saved"

  Scenario: Bewaren zonder bestaande HTML: foutmelding (BR-VIS-12)
    Gegeven er is geen visualisatie-HTML
    En de gebruiker heeft wijzigingen aangebracht (theoretisch)
    Als de gebruiker probeert te bewaren
    Dan verschijnt een foutmelding dat er geen HTML is om te bewaren

  Scenario: Regenereren bevestigen: HTML wordt opnieuw opgebouwd (S-078)
    Gegeven de visualisatie is geladen
    Als de gebruiker op "Regenerate" klikt
    Dan verschijnt een bevestigingsvenster dat de huidige layout overschreven wordt
    Als de gebruiker bevestigt
    Dan wordt de HTML volledig opnieuw opgebouwd
    En de status gaat naar "Changes saved"
    Als de gebruiker annuleert
    Dan gebeurt er niets

  Scenario: Na bewaren wordt supportdata opgeslagen (BR-VIS-13)
    Gegeven de gebruiker bewaart wijzigingen
    Als het bewaren voltooid is
    Dan wordt visuals_python_support_data.json bijgewerkt met posities, collecties en joint nodes

  Scenario: Graaf wijzigen toont "niet bewaard" (BR-VIS-14)
    Gegeven de visualisatie is up-to-date
    Als de gebruiker een node versleept of een collectie wijzigt
    Dan verandert de status direct naar "Changes are not saved"

  Scenario: Project verlaten met onbewaarde graaf vraagt bevestiging (BR-VIS-15, S-079)
    Gegeven de visualisatie heeft onbewaarde wijzigingen
    En de gebruiker probeert het project te sluiten of naar Home te gaan
    Als het waarschuwingsvenster verschijnt
    En de gebruiker kiest "Back"
    Dan blijft het project open
    En de gebruiker kiest "Continue"
    Dan wordt het project gesloten zonder de graafwijzigingen te bewaren