# language: nl
Feature: Projectenoverzicht, zoeken en sorteren (F-PROJ-01)

  Background:
    Gegeven de applicatie is gestart
    En het Home-scherm is zichtbaar

  Scenario: Projecten worden dalend op laatste wijziging getoond (S-008)
    Gegeven er zijn meerdere projecten met verschillende "laatst bewerkt" datums
    Als het Home-scherm wordt getoond
    Dan worden de projecten gesorteerd met het nieuwste project bovenaan

  Scenario: Zoeken op bestek verbergt niet-matchende projecten (S-009)
    Gegeven er zijn projecten met besteknummers "12345", "67890", "12399"
    Als de gebruiker "123" in het zoekveld typt
    Dan zijn alleen de projecten met bestek "12345" en "12399" zichtbaar
    En de overeenkomende cellen worden gemarkeerd

  Scenario: Zoeken op subset toont het juiste project (S-009 variant)
    Gegeven er zijn projecten met subsetnamen "subset_a.db", "subset_b.db"
    Als de gebruiker "subset_a" in het zoekveld typt
    Dan is alleen het project met subset "subset_a.db" zichtbaar

  Scenario: Zoeken op eigen referentie
    Gegeven er zijn projecten met eigen referenties "Project_Alpha", "Project_Beta"
    Als de gebruiker "Alpha" in het zoekveld typt
    Dan is alleen "Project_Alpha" zichtbaar

  Scenario: Zoeken is case-insensitive (BR-PROJ-01)
    Gegeven er is een project met bestek "ABC123"
    Als de gebruiker "abc" in het zoekveld typt
    Dan is het project zichtbaar

  Scenario: Wissen van de zoektekst herstelt de volledige lijst (S-009 variant)
    Gegeven de gebruiker heeft gezocht op "123"
    En de lijst is gefilterd
    Als de gebruiker het zoekveld wist
    Dan zijn alle projecten weer zichtbaar

  Scenario: Dubbelklikken opent het project (S-009 variant)
    Gegeven er is een project in de lijst
    Als de gebruiker dubbelklikt op de rij
    Dan opent het project in stap 1

  Scenario: Lege projectenlijst toont geen resultaten-melding (A-13 beslissing)
    Gegeven de gebruiker heeft nog geen projecten aangemaakt
    Als het Home-scherm wordt getoond
    Dan wordt de melding "geen resultaten" getoond in de tabelzone

  Scenario: Zoekopdracht zonder matches toont geen resultaten-melding (A-13 beslissing)
    Gegeven er zijn projecten in de lijst
    Als de gebruiker zoekt op een term die geen project matcht
    Dan wordt de melding "geen resultaten" getoond in de tabelzone
    En geen projectrijen zijn zichtbaar

  Scenario: Nieuw aangemaakt project wordt visueel gemarkeerd (BR-PROJ-02)
    Gegeven de gebruiker maakt een nieuw project aan
    Als het project in de lijst verschijnt
    Dan is de rij visueel gemarkeerd als laatst toegevoegd

  Scenario: Actieknoppen staan per rij en beïnvloeden alleen dat project (BR-PROJ-03)
    Gegeven er zijn meerdere projecten in de lijst
    Als de gebruiker op de bewerkknop van het tweede project klikt
    Dan opent het bewerkdialoogvenster voor dat specifieke project