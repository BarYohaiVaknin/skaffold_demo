import subprocess, yaml, shutil, sys

def inputValidation():
    inputDetails = {
        'appName': {
            'initialMessage': "What is the name of the app? (a-z letters only, no spaces)",
            'inputLegality': lambda x: x.islower() and x.isalpha(),
            'errorMessage': "Invalid input.\nPlease enter lowercase letters (a-z) only, no spaces."
        },
        'codeLangChoice': {
            'initialMessage': "Which code language you are going to use?\n1. Python\n2. Bash\n3. JS",
            'inputLegality': lambda x: x.isdigit() and 1 <= int(x) <= 3,
            'errorMessage': "Invalid input.\nPlease enter a number between 1 and 3."
        },
        'requiredPorts': {
            'initialMessage': "Which ports are required for the app to work properly? (For Example - 8080 80 5000 etc)",
            'inputLegality': lambda x: len(x.split()) >= 1 and all(2 <= len(port) <= 5 and port.isdigit() for port in x.split()),
            'errorMessage': "Invalid input.\nPlease enter one or more space-separated port numbers while each port is 2-5 digits long."
        },
        'baseImageURL': {
            'initialMessage': "What is the URL for the base image for the app?",
            'inputLegality': lambda x: ' ' not in x,
            'errorMessage': "Invalid URL.\nImage URL can't include spaces."
        },
        'requiredMetrics': {
            'initialMessage': "Any specific metrics you would like Prometheus to monitor? (For Example - data clock output etc..)",
            'inputLegality': lambda x: True,
            'errorMessage': None  
        }
    }

    validatedInputs = {}
    for requiredInput, legality in inputDetails.items():
        initialMessage = legality['initialMessage']
        inputLegality = legality['inputLegality']
        errorMessage = legality['errorMessage']
        
        userInput = input(initialMessage + "\n")
        
        if inputLegality:
            while not inputLegality(userInput):
                print(errorMessage)
                userInput = input(initialMessage + "\n")
        
        validatedInputs[requiredInput] = userInput
    return validatedInputs


def toolsVerifier(requiredTools, operatingSystem):
    print(f"It seems like you're using {operatingSystem}, let's make sure you have the required tools...\n")
    packageManager = {
        'packageManagerName': {
            'Windows': 'Chocolatey',
            'Darwin': 'Homebrew'
        },
        'verifyCommand': {
            'Windows': 'choco',
            'Darwin': 'brew'
        },
        'installationCommand': {
            'Windows': 'powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString(\'https://chocolatey.org/install.ps1\'))"',
            'Darwin': '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        }
    }
    toolsInstallationCommand = {
        'curl': {
            'Windows': "choco install curl",
            'Linux': "apt install curl -y",
            'Darwin': "brew install curl"
        },
        'kubectl': {
            'Windows': "choco install kubernetes-cli",
            'Linux': """ curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && chmod +x kubectl && mkdir -p ~/.local/bin && mv ./kubectl ~/.local/bin/kubectl """,
            'Darwin': "brew install kubectl -y"
        },
        'minikube': {
            'Windows': "choco install minikube -y",
            'Linux': 'curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && install minikube-linux-amd64 /usr/local/bin/minikube',
            'Darwin': 'brew install minikube'
        },
        'skaffold': {
            'Windows': "choco install -y skaffold",
            'Linux': "curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && install skaffold /usr/local/bin/",
            'Darwin': "brew install skaffold"
        }
    }
    for tool in requiredTools:
        if shutil.which(tool) is None:
            userAnswer = input(f"It's seems like the {tool} is missing, would like to install it? (Y/N)\n")
            if userAnswer == "Y":
                if 'Windows' or 'Linux' in operatingSystem:
                    if shutil.which(packageManager['verifyCommand'][operatingSystem]) is None:
                        userAnswer = input(f"The installtions on {operatingSystem} made with the package manager {packageManager['packageManagerName'][operatingSystem]}, would you like to install it? (Y/N)\n")
                        if userAnswer == "Y":
                            try:
                                subprocess.run(packageManager['installationCommand'][operatingSystem],capture_output=True, text=True)
                            except Exception as Error:
                                print(f"Could not complete the installation\n.Error:\n{Error}\nAborting.")
                                sys.exit()
                        else:
                            print(f"The script can't keep going without the package manager {packageManager['packageManagerName'][operatingSystem]}, aborting.")
                            sys.exit()
                print(f"Installing {tool}...\n")
                try:
                    subprocess.run(toolsInstallationCommand[tool][operatingSystem],check=True, shell=True)
                except Exception as error:
                    print(f"Can't proceed with installation.\nError:\n{error}\nAborting.")
                    sys.exit()
            else:
                print(f"The script can't keep going without the tool {tool}, aborting.")
                sys.exit()
        else:
            print(f"Great news - {tool} is already installed.\n")
    return 0

def codeLangVerifier(codeLang, operatingSystem):
    codeLangInstallationCmd = {
        'python3': {
            'Windows': 'curl -o python-installer.exe https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe && python-installer.exe /quiet InstallAllUsers=1 PrependPath=1',
            'Linux': 'apt install python3 -y',
            'Darwin': 'brew install python3'
        },
        'bash': {
            'Windows': None,
            'Linux': 'apt install bash',
            'Darwin': 'brew install bash'
        },
        'js': {
            'Windows': 'curl -o node-installer.exe https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi && node-installer.exe /quiet',
            'Linux': 'apt install nodejs -y',
            'Darwin': 'brew install node'
        }
    }
    if 'Windows' in operatingSystem and codeLang == 'bash':
        print('Invalid combination\nAborting.')
        sys.exit()
    else:
        if shutil.which(codeLang.lower()) is None:
            userAnswer = input(f"It's seems like the {codeLang} is missing, would like to install it? (Y/N)\n")
            if userAnswer == "Y":
                print(f"Installing {codeLang}...\n")
                try:
                    subprocess.run(codeLangInstallationCmd[codeLang][operatingSystem],check=True, shell=True)
                except Exception as error:
                    print(f"Can't proceed with the installation of {codeLang}.\nError:\n{error}\nAborting.")
                    sys.exit()
            else:
                print(f"The script can't keep going without {codeLang}.\nAborting.")
                sys.exit()
        else:
            print(f"{codeLang} is already installed.\n")
    return 0

def textReplacement(filePath, replacementDict):
    with open(filePath, 'r') as fileData:
        oldData = fileData.read()
    newData = oldData
    for oldText, newText in replacementDict.items():
        newData = newData.replace(str(oldText), str(newText))
    with open(filePath, 'w') as fileData:
        fileData.write(newData)     
    return 0

def yamlHandler(folderPath, fileName, requiredData):
    with open(folderPath+fileName, 'r') as yamlSource:
        yamlSourceData = list(yaml.load_all(yamlSource, Loader=yaml.FullLoader))
        if len(yamlSourceData) > 1:
            if 'Service' in yamlSourceData[0]['kind']:
                valuesForDeployment = dict(yamlSourceData[0])
                restOfYamlDest = dict(yamlSourceData[1])
            else:
                restOfYamlDest = dict(yamlSourceData[0])
                valuesForDeployment = dict(yamlSourceData[1])
        else:
            valuesForDeployment = dict(yamlSourceData[0])

    if fileName == 'deployment.yaml':
        valuesForDeployment['spec']['ports'] = [{
            'name': f"{requiredData[0]}port{requiredData[1].index(port)}",
            'port': int(port),
            'protocol' : 'TCP'
        } for port in requiredData[1]]
        combinedData = f"{yaml.dump(valuesForDeployment, default_flow_style=False)}---\n{yaml.dump(restOfYamlDest, default_flow_style=False)}"
        with open(folderPath+fileName, 'w') as editedYaml:
            editedYaml.write(combinedData)
        return 0

    if fileName == 'skaffold.yaml':
        valuesForDeployment['portForward'] = [{
            'resourceType': 'service',
            'resourceName': requiredData[0],
            'port' : int(port)
        } for port in requiredData[1]]

    if fileName == 'promethuesConfig.yaml':
        valuesForDeployment['scrape_configs'] = [{
            'job_name': f"'{requiredData[0]}_metric_{metric}'",
            'static_configs': [{'targets': [f"{requiredData[2]}:{requiredData[3][0]}"]}]
        } for metric in requiredData[4]]

    editedYaml = open(folderPath+fileName, 'w')
    yaml.safe_dump(valuesForDeployment,editedYaml,sort_keys=False,default_flow_style=False)
    editedYaml.close()
    return 0
