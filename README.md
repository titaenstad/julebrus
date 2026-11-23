Julebrus-prosjektet
===================

Dette repoet inneholder en liten Flask-applikasjon for å samle og vise rangeringer av julebrus. Data lagres som tab-separerte filer (TSV) i `data/`. Under ligger en oversikt over hvordan du kommer i gang og hva slags funksjonalitet som finnes.

Kom i gang
------------

- Installer avhengighetene med `uv sync` i prosjektroten  (alternativt `pip install -e .` )
- Bruk `uv run -m julebrus.generate_julebrus_table <brus1> <brus2> osv` for å generere en ny `julebrus.tsv` med kodenavn (standardfil er `data/table_data/julebrus.tsv`).
- Start applikasjonen med `uv run -m julebrus`, eller bare `uv run julebrus` (alternativt `python -m julebrus`). Send med datamappe for å se tidligere år `uv run julebrus data/2025` 
- Resultatene ser du på /results.

