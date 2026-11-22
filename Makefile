.PHONY: rca

RCA_PORT ?= 4173

## Uruchamia lokalny podgląd strony RCA Lubecko.
rca:
	@echo "Strona RCA: http://127.0.0.1:$(RCA_PORT)/"
	python3 -m http.server $(RCA_PORT) --bind 127.0.0.1 --directory issue_rca_lubecko/www
