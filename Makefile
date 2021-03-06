.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = censusdata-199ca23a-006d-4a26-ae62-0c41c0d56db5
PROFILE = default
PROJECT_NAME = demographics-by-drivetime
PYTHON_INTERPRETER = python3

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Load data to SQL db
load_all: load_boundaries load_demographics

load_demographics: clean requirements load_CO_demo load_MT_demo

load_CO_demo:
	$(PYTHON_INTERPRETER) src/data/load_sql.py -d -s Colorado -l debug >> logs/loadsql_log.txt

load_MT_demo:
	$(PYTHON_INTERPRETER) src/data/load_sql.py -d -s Montana -l debug >> logs/loadsql_log.txt

load_boundaries: clean requirements load_meta load_county #TODO (find solution to memory issues) -> load_CO load_MT 

load_meta:
	$(PYTHON_INTERPRETER) src/data/load_sql.py -b -m -l debug >> logs/loadsql_log.txt

load_county:
	$(PYTHON_INTERPRETER) src/data/load_sql.py -b -c -l debug >> logs/loadsql_log.txt

load_CO_boundaries:
	$(PYTHON_INTERPRETER) src/data/load_sql.py -b -s "Colorado" -l debug >> logs/loadsql_log.txt

load_MT_boundaries:
	$(PYTHON_INTERPRETER) src/data/load_sql.py -s "Montana" -l debug >> logs/loadsql_log.txt

## Clear Database

# delete_tables:
delete_tables:
	$(PYTHON_INTERPRETER) src/data/delete_tables.py

## Delete all compiled Python files
clean: black
	find . -name "*.py" -exec sed -i '/ipdb/d' {} + 
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".ipynb_checkpoints" | xargs rm -rf

black:
	black src/.

## Upload Data to S3
sync_data_to_s3: clean
ifeq (default,$(PROFILE))
	aws s3 sync data/ s3://$(BUCKET)/
else
	aws s3 sync data/ s3://$(BUCKET)/ --profile $(PROFILE)
endif

## Download Data from S3
sync_data_from_s3: clean
ifeq (default,$(PROFILE))
	aws s3 sync data/ s3://$(BUCKET)/
else
	aws s3 sync data/ s3://$(BUCKET)/ --profile $(PROFILE)
endif

## Set up python interpreter environment
create_environment:
ifeq (True,$(HAS_CONDA))
		@echo ">>> Detected conda, creating conda environment."
ifeq (3,$(findstring 3,$(PYTHON_INTERPRETER)))
	conda create --name $(PROJECT_NAME) python=3
else
	conda create --name $(PROJECT_NAME) python=2.7
endif
		@echo ">>> New conda env created. Activate with:\nsource activate $(PROJECT_NAME)"
else
	$(PYTHON_INTERPRETER) -m pip install -q virtualenv virtualenvwrapper
	@echo ">>> Installing virtualenvwrapper if not already installed.\nMake sure the following lines are in shell startup file\n\
	export WORKON_HOME=$$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\nsource /usr/local/bin/virtualenvwrapper.sh\n"
	@bash -c "source `which virtualenvwrapper.sh`;mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER)"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
endif

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
