# Julebrus-rangering

Dette repoet inneholder en liten Flask-applikasjon for å samle og vise rangeringer av julebrus.  

## Installer avhengigheter
- Installer avhengighetene med `uv sync`

## Lag data for rangering
1. Lag en datamappe i `data`, f.eks `data/2026`. Heretter referert til som `datamappe`.
2. Lag filen `datamappe/brusnavn.json`, som inneholder kortnavn som nøkkel og fullt navn som verdi, f.eks. `{"oskar_sylte": "Rudolf & Nissens julebrus"}`. Fullnavnet vises i resultat-oversikten, og kortnavnet brukes for å lage datatabeller med rangering
3. Lag mappa `datamappe/bilder`, og legg inn bilder av brusene. Bildene må ha kortnavn som navn, og filendelse jpg, f.eks `oskar_sylte.jpg`.
4. Kjør appen med `uv run julebrus datamappe`, feks `uv run julebrus data/2026`


## Vis resultater 
Brukerdata som rangeres lagres i `datamappe/user_data`. Når appen kjøres, kan du finne resultatene på `/results`
