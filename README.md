Julebrus-prosjektet
===================

Dette repoet inneholder en liten Flask-applikasjon for å samle og vise rangeringer av julebrus. Data lagres som tab-separerte filer (TSV) i `data/`. Under ligger en oversikt over hvordan du kommer i gang og hva slags funksjonalitet som finnes.

Kom i gang
------------

- Installer avhengighetene med `uv sync` i prosjektroten  (alternativt `pip install -e .` )
- Bruk `uv run -m julebrus.generate_julebrus_table <brus1> <brus2> osv` for å generere en ny `julebrus.tsv` med kodenavn (standardfil er `data/table_data/julebrus.tsv`).
- Start applikasjonen med `uv run -m julebrus` (alternativt `python -m julebrus`).
- Åpne nettleseren på `http://localhost:5000` for å rangere eller se resultater.

