# language: nl
Feature: Project aanmaken (F-PROJ-02)

  Background:
    Gegeven de gebruiker is op het Home-scherm

  Scenario: Geldig project aanmaken (S-010)
    Gegeven de gebruiker klikt op "Nieuw project"
    En vult een unieke eigen referentie in
    En vult een bestek in
    En kiest een geldige subsetbestand (.db)
    Als de gebruiker op "Submit" klikt
    Dan wordt de projectmap aangemaakt onder "~/OTLWizardProjects/Projects/<eigen referentie>"
    En de subset wordt naar de projectmap gekopieerd
    En project_details.json wordt geschreven
    En het project verschijnt in de lijst gemarkeerd als laatst toegevoegd

  Scenario: Lege eigen referentie: foutmelding, geen project (S-011)
    Gegeven de gebruiker klikt op "Nieuw project"
    En laat de eigen referentie leeg
    En vult een bestek in
    En kiest een geldige subset
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een foutmelding dat de eigen referentie verplicht is
    En er wordt geen project aangemaakt

  Scenario: Leeg bestek: foutmelding (S-011 variant)
    Gegeven de gebruiker klikt op "Nieuw project"
    En vult een eigen referentie in
    En laat het bestek leeg
    En kiest een geldige subset
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een foutmelding dat het bestek verplicht is
    En er wordt geen project aangemaakt

  Scenario: Geen subset gekozen: foutmelding (S-011 variant)
    Gegeven de gebruiker klikt op "Nieuw project"
    En vult een eigen referentie in
    En vult een bestek in
    En kiest geen subsetbestand
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een foutmelding dat een subset verplicht is
    En er wordt geen project aangemaakt

  Scenario: Ongeldige database: foutmelding (S-012)
    Gegeven de gebruiker klikt op "Nieuw project"
    En vult een eigen referentie in
    En vult een bestek in
    En kiest een bestand dat geen geldige SQLite-subsetdatabase is
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een foutmelding dat de subset ongeldig is
    En er wordt geen project aangemaakt

  Scenario: Bestaande projectnaam: melding en geen overschrijving (S-013)
    Gegeven er bestaat al een project met eigen referentie "Project_X"
    En de gebruiker klikt op "Nieuw project"
    En vult "Project_X" in als eigen referentie
    Als de gebruiker op "Submit" klikt
    Dan verschijnt een melding "Project bestaat al"
    En het bestaande project wordt niet overschreven

  Scenario: Subset wordt lokaal gekopieerd (BR-PROJ-07)
    Gegeven de gebruiker maakt een project aan met een subsetbestand uit een externe map
    Als het project wordt aangemaakt
    Dan bestaat een kopie van de subset in de projectmap
    En het project is zelfstandig van de originele subsetlocatie

  Scenario: Laatst gekozen subsetmap wordt onthouden (BR-PROJ-08)
    Gegeven de gebruiker heeft een subset gekozen uit map "/data/subsets/"
    Als de gebruiker later een nieuw project aanmaakt
    Dan opent de subsetkiezer standaard in "/data/subsets/"