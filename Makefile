APP_DIR = chocolate_in
PYTHON_FILE = main.py
RUNNER_SCRIPT = chocolate
VENV_DIR = .venv
SAFE_DIR = /opt/chocolate
INSTALL_DIR = /usr/local/bin

all: sandbox helper create-venv install-deps copy-app create-runner move-runner

create-venv:
	@python3 -m venv $(VENV_DIR)

install-deps:
	@$(VENV_DIR)/bin/pip install --upgrade pip
	@$(VENV_DIR)/bin/pip install rich pytest paramiko

copy-app:
	@sudo rm -rf $(SAFE_DIR)
	@sudo mkdir -p $(SAFE_DIR)
	@sudo cp -r $(APP_DIR) $(SAFE_DIR)
	@sudo cp -r $(VENV_DIR) $(SAFE_DIR)
	@sudo cp choco-sandbox $(INSTALL_DIR)
	@sudo cp choco-help $(INSTALL_DIR)
	@sudo mkdir -p /usr/share/doc/chocolate
	@sudo cp -r man/* /usr/share/doc/chocolate


create-runner:
	@echo "#!/bin/bash" > $(RUNNER_SCRIPT)
	@echo "$(SAFE_DIR)/$(VENV_DIR)/bin/python3 $(SAFE_DIR)/$(APP_DIR)/$(PYTHON_FILE) \"\$$@\"" >> $(RUNNER_SCRIPT)
	@chmod +x $(RUNNER_SCRIPT)

move-runner:
	@sudo mv $(RUNNER_SCRIPT) $(INSTALL_DIR)/$(RUNNER_SCRIPT)

sandbox:
	g++ -o choco-sandbox chocolate_in/sandbox.cpp -lseccomp -D_GNU_SOURCE

helper:
	g++ -o choco-help chocolate_in/help.cpp 


clean:
	@rm -f $(RUNNER_SCRIPT)
	@rm -rf $(VENV_DIR)
	@sudo rm -rf $(SAFE_DIR)
