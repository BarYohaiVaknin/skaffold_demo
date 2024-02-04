# Skaffold Demo

# Description:
This project made as an home assigment, and includes mainly the technologies as below: <br  />
>K8s<br  />
>Docker<br  />
>Skaffold<br  />

>The project purpose is to create a tool for developers which helps them to run envrionment convienetly for micro-service development.<br />

# How to run?
1. Clone the repository to your local machine.
2. Use the command 'python3 devEnv.py'.
3. The script will ask you for Five different inputs:
 <br /> 3.1. The app name.
 <br /> 3.2. The code language you would to develop with.
 <br /> 3.3. The base image for the app.
 <br /> 3.4. The required ports for the app to work properly.
 <br /> 3.5. The required metrics you would like to monitor with promethues & grafana.
4. The script will deploy the environment your requested. 


# Few Notes:
1. The script available for Linux/Unix OS and for python development only.
2. The script assume you provide at least one port.
3. The metrics will be available on the first nodePort created.

# Future Plans: (As an answer for 'If you had a week extra..')
1. Data validation for the various inputs. (Ports must be numbers minimum Four-letters long for example).
2. Handling error with try-catch as should be done.
3. Seperate the code to main and logical functions on different libraries and use 'import function from functions'
4. Supporting the script to run on Windows 
5. Supporting JS & Bash as coding languges
6. Additional Abilities:
 <br /> 6.1. Clean-up ability which use 'skaffold delete' & 'docker-compose down -v' (A user choise)
 <br /> 6.2. Running on dev mode - let the user choose if he would like to run on dev mode - which will automatically redeploy the files for every change.
 <br /> 6.3. Roll-back - The script will create a configuration file to make sure the user can restore the exact same environment for future use (Development a new feature after a year for the same micro-service for example)
 <br /> 6.4. Dry run approval - A glance for the user to see what is going to be deploy after his approval.
 <br /> 6.5. Feedback mechanism - Let the developer the option to require for additional features.

# Additional changes or addons for a big scale:
1. I would make a list of 'common-use' setups and images for the user convinient, which eventually let him run the environment more easily.
2. The more user will use it - the more requirement they have, thus I would treat the script as a whole product which includes CI/CD process, to make sure the base files are updated and relevant for their purposes.
3. I'm not sure if that's the case - but for a big scale development on various products I would work in the opposite way - I would create a VM on the cloud for every development request and install locally the user requirement. there are a lot of advantages in this method like security, real-time backup, computing resources in case of micro-service which requires 'heavy computing' etc.
