##########################################################################
# devEnv - Made by Bar Yohai Vaknin.
# Purpose - Setting a dev environment for microservices development using skaffold, minikube and docker.
# Version - 1.0
###########################################################################
# Imports:  
###########################################################################
import subprocess, platform, yaml, os, shutil, sys

###########################################################################
# Inputs:  
###########################################################################
requiredTools = ["curl","minikube","skaffold"]
print("Hey user, I need to get number of parameters from you, so we can setup the required environment.\n")
appName = input("What is the name of the app?\n").lower()
codeLang = {
    "1": "Python3",
    "2": "Bash",
    "3": "JS"
}
codeLangChoice = codeLang.get(input("Which code language you are going to use?\n1.Python\n2.Bash\n3.JS\n"))
requiredPorts = input("Which ports are required for the app to work properly? (For Example - 8080 80 5000 etc)\n").split()
requiredPorts4Docker = requiredPorts.copy()
for port in requiredPorts4Docker:
    requiredPorts4Docker[requiredPorts4Docker.index(port)] = "EXPOSE " + port 
baseImageURL = input("What is the url for the base image for the app?\n")
requiredPorts4Docker = '\n'.join(requiredPorts4Docker)
dockerfileValues = f'''FROM {baseImageURL}

{requiredPorts4Docker} 

ENTRYPOINT sleep 3000'''
requiredMetrics = input("Any specific metrics you would like prometheus will monitor? (For Example - data clock output etc..)\n").lower().split()

print("Great!\nThank you for the information,let me check which operating system you're currently using...\n")
if "Windows" not in platform.system(): 
    print(f"It seems like you're using {platform.system()}, let's make sure you have the required tools...\n")
    for tool in requiredTools:
        if shutil.which(tool) is None:
            userAnswer = input(f"It's seems like the {tool} is missing, would like to install it? (Y/N)\n")
            if userAnswer == "Y":
                print(f"Installing {tool}...")
            else:
                print(f"The script can't keep going without the tool {tool}, aborting.")
                sys.exit() 
    print("All the required tools found, we are all set!\nIt's time to configure the requested devEnv.\n")

    #codeLang Dependencies
    print(f"Verifying if {codeLangChoice} and it's dependencies are all set...\n")
    if shutil.which(codeLangChoice) is None:
        print(f"Installing {codeLangChoice}...\n")

    #Repo creation
    os.mkdir(os.getcwd()+"/"+appName+"Repo")
    folderPath = os.getcwd()+'/'+appName+"Repo"+'/'
    print(f"A repository which called {appName}Repo created and all of the necessary files will be there.")

    ##Dockerfile creation
    subprocess.run(f'echo "{dockerfileValues}" > "{folderPath}Dockerfile"', shell=True)
    print(f"A dockerfile created on the folder {appName}Repo with the required params,\nplease notice that for the sake of convenient there's a sleep entrypoint to make sure the pod is staying alive.")

    #Skaffold yaml
    shutil.copyfile("skaffold.yaml", folderPath+"skaffold.yaml")
    subprocess.run(['skaffold', 'init', '--generate-manifests',"--force"],cwd=folderPath)

    #Deployment values
    subprocess.run(f"sed -i '' 's/dockerfile-image/{appName}/' {folderPath}deployment.yaml",shell=True)
    subprocess.run(f"sed -i '' 's/clusterIP: None/type: NodePort/' {folderPath}deployment.yaml",shell=True)
    
    with open(folderPath+"deployment.yaml", 'r') as yamlSource:
        yamlSourceData = list(yaml.load_all(yamlSource, Loader=yaml.FullLoader))
        for doc in yamlSourceData:
            svcYamlSource = yamlSourceData[0]
            deploymentYamlSource = yamlSourceData[1]
            break
    svcYamlDest = dict(svcYamlSource)
    svcYamlDest['spec']['ports'] = [{'name': f"{appName}port{requiredPorts.index(port)}",'port': int(port), 'protocol': 'TCP'} for port in requiredPorts]
    combinedData = f"{yaml.dump(svcYamlDest, default_flow_style=False)}---\n{yaml.dump(deploymentYamlSource, default_flow_style=False)}"
    with open(folderPath+"deployment.yaml", 'w') as editedYaml:
        editedYaml.write(combinedData)

    #Skaffold values
    subprocess.run(f"sed -i '' 's/dockerfile-image/{appName}/' {folderPath}skaffold.yaml",shell=True)
    with open(folderPath+"skaffold.yaml", 'r') as yamlSource:
        yamlSourceData = yaml.load(yamlSource, Loader=yaml.FullLoader)
    skaffoldWUpdatedPorts = yamlSourceData
    skaffoldWUpdatedPorts['portForward'] = [{'resourceType': 'service', 'resourceName': appName,'port' : int(port)} for port in requiredPorts]
    editedYaml = open(folderPath+"skaffold.yaml", 'w')
    yaml.safe_dump(skaffoldWUpdatedPorts,editedYaml,sort_keys=False,default_flow_style=False)
    editedYaml.close()

    #Run Part #1
    print(f"All the required files created at {appName}Repo, running the pods...")
    subprocess.run(['skaffold','run'],cwd=folderPath)
    shutil.copyfile("docker-compose.yaml", folderPath+"docker-compose.yaml")

    #Metrics Values
    nodeIP = subprocess.run(['minikube','ip'],stdout=subprocess.PIPE, text=True).stdout.strip()
    nodePortsOutput = subprocess.run(
        ["kubectl", "get", "svc", f"{appName}", "--no-headers", "-o", "custom-columns=PORTS:.spec.ports[*].nodePort"],
        capture_output=True,
        text=True
    ).stdout.strip()
    nodePortsArray = [port.rstrip() for port in nodePortsOutput.split(',')]
    shutil.copyfile("promethuesConfig.yaml", folderPath+"promethuesConfig.yaml")
    with open(folderPath+"promethuesConfig.yaml", 'r') as yamlSource:
        yamlSourceData = yaml.load(yamlSource, Loader=yaml.FullLoader)
    yamlSourceData['scrape_configs'] = [{
        'job_name': f"'{appName}_metric_{metric}'",
        'static_configs': [{'targets': [f"{nodeIP}:{nodePortsArray[0]}"]}]
    } for metric in requiredMetrics]
    editedYaml = open(folderPath+"promethuesConfig.yaml", 'w')
    yaml.safe_dump(yamlSourceData,editedYaml,sort_keys=False,default_flow_style=False)
    editedYaml.close()
    
    #Run Part#2
    print("Running montior components (Promethues + Grafana)...")
    subprocess.run(['docker compose up -d'],cwd=folderPath,shell=True)
    print("All set!\nHappy development.")
else:
    print("Windows users aren't supported yet.")
