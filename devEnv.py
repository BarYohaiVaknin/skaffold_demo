###########################################################################
import subprocess, platform, os, shutil, sys
from devEnvFunctions import codeLangVerifier, textReplacement, yamlHandler, toolsVerifier, inputValidation
###########################################################################
# Inputs:  
###########################################################################
print("Hey user, I need to get number of parameters from you, so we can setup the required environment.\n")
validatedInput = inputValidation()
appName = validatedInput['appName']
codeLang = {
    "1": "Python3",
    "2": "Bash",
    "3": "JS"
}
codeLangChoice = codeLang.get(validatedInput[codeLang])
requiredPorts = validatedInput['requiredPorts'].split() 
requiredPorts4Docker = requiredPorts.copy()
for port in requiredPorts4Docker:
    requiredPorts4Docker[requiredPorts4Docker.index(port)] = "EXPOSE " + port 
baseImageURL = validatedInput['baseImageURL'] 
operatingSystem = platform.system()
requiredPorts4Docker = '\n'.join(requiredPorts4Docker)
dockerfileValues = f'''FROM {baseImageURL}

{requiredPorts4Docker} 

ENTRYPOINT sleep 3000'''
requiredMetrics = validatedInput['requiredMetrics'].split() 
requiredTools = ["curl","kubectl","minikube","skaffold"]
print("Great!\nThank you for the information,let me check if the required tools are installed...\n")

#requiredTools Verifier
toolsVerifier(requiredTools,operatingSystem)
print("All the required tools found, we are all set!\nIt's time to configure the requested devEnv.\n")

#codeLang Dependencies
print(f"Verifying if {codeLangChoice} and it's dependencies are all set...\n")
codeLangVerifier(codeLangChoice.lower(),operatingSystem)

#Repo creation
os.mkdir(os.getcwd()+"/"+appName+"Repo")
folderPath = os.getcwd()+'/'+appName+"Repo"+'/'
print(f"A repository which called {appName}Repo created and all of the necessary files will be there.")

##Dockerfile creation
with open(folderPath+'Dockerfile', 'w') as dockerfile:
    dockerfile.write(dockerfileValues)
print(f"A dockerfile created on the folder {appName}Repo with the required params,\nplease notice that for the sake of convenient there's a sleep entrypoint to make sure the pod is staying alive.")

#Skaffold yaml
print(f"Creating an skaffold & deployment yamls...")
try:
    shutil.copyfile("skaffold.yaml", folderPath+"skaffold.yaml")
    subprocess.run(['skaffold', 'init', '--generate-manifests',"--force"],cwd=folderPath)
except Exception as Error:
    print(f'Error while creating skaffold.yaml:\n{Error}\nAborting.')
    sys.exit()
    
#Deployment values
replacementData = {
    "dockerfile-image": appName,
    "clusterIP: None": "type: NodePort"
}
try:
    textReplacement(folderPath+'deployment.yaml',replacementData)
except Exception as error:
    print(f"Something went wrong\nError:\n{error}")
requiredData = [appName, requiredPorts]
yamlHandler(folderPath,'deployment.yaml',requiredData)

#Skaffold values
replacementData = {
    "dockerfile-image": appName
}
try:
    textReplacement(folderPath+'skaffold.yaml',replacementData)
except Exception as error:
    print(f"Something went wrong\nError:\n{error}")
yamlHandler(folderPath,'skaffold.yaml',requiredData)

#Run Part #1
print(f"All the required files created at {appName}Repo, running the pods...")
subprocess.run(['skaffold','run'],cwd=folderPath)
try:
    shutil.copyfile("docker-compose.yaml", folderPath+"docker-compose.yaml")
except Exception as Error:
    print(f'Error while creating docker-compose.yaml:\n{Error}\nAborting.')
    sys.exit()

#Metrics Values
nodeIP = subprocess.run(['minikube','ip'],stdout=subprocess.PIPE, text=True).stdout.strip()
nodePortsOutput = subprocess.run(
    ["kubectl", "get", "svc", f"{appName}", "--no-headers", "-o", "custom-columns=PORTS:.spec.ports[*].nodePort"],
    capture_output=True,
    text=True
).stdout.strip()
nodePortsArray = [port.rstrip() for port in nodePortsOutput.split(',')]
requiredData.append(nodeIP)
requiredData.append(nodePortsArray)
requiredData.append(requiredMetrics)
try:
    shutil.copyfile("promethuesConfig.yaml", folderPath+"promethuesConfig.yaml")
except Exception as Error:
    print(f'Failed to create prometheus config file.\nError:\n{Error}\nAborting')
    sys.exit()
yamlHandler(folderPath,'promethuesConfig.yaml',requiredData)

#Run Part#2
print("Running montior components (Promethues + Grafana)...")
subprocess.run(['docker compose up -d'],cwd=folderPath,shell=True)
print("All set!\nHappy development.")
