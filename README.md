# Skaffold Demo

## Description

This project is a home assignment that primarily involves the following technologies:

- Kubernetes (K8s)
- Docker
- Skaffold

The project's purpose is to create a developer tool that facilitates the convenient setup of the development environment for microservice development.

## How to Run?

1. Clone the repository to your local machine.
2. Use the command `python3 devEnv.py`.
3. The script will prompt you for five different inputs:
   - The app name.
   - The code language you want to develop with.
   - The base image for the app.
   - The required ports for the app to work properly.
   - The required metrics you want to monitor with Prometheus & Grafana.
4. The script will deploy the environment as per your request.

## Notes

1. The script is available for Linux/Unix OS and for Python development only.
2. The script assumes you provide at least one port.
3. The metrics will be available on the first NodePort created.

## Future Plans

(In response to 'If you had an extra week...')

1. Implement data validation for various inputs (e.g., ports must be numbers, minimum four letters long).
2. Add error handling using try-catch.
3. Organize the code into main and logical functions in different libraries using `import function from functions`.
4. Add support for the script to run on Windows.
5. Extend support to include JS & Bash as coding languages.
6. Additional Abilities:
   - Clean-up functionality - using 'skaffold delete' & 'docker-compose down -v' (according to user's choice).
   - Dev mode - allowing the user to use skaffold's ability to automatically redeploy files for every change.
   - Rollback feature - creating a configuration file to make sure the user can restore the exact same environment for future use (Development a new feature after a year for the same micro-service for example)
   - Dry run approval - provide a preview of the deployment before approval.
   - Feedback mechanism - allow developers to request additional features and submit a feedback.

## Additional Changes or Add-ons for Large Scale

1. Create a list of 'common-use' setups and images for user convenience, making it easier and quicker for the developer to set up the environment.
2. Implement a CI/CD process to keep base files updated and relevant for a growing user base.
3. For large-scale development on various products, consider creating a VM on the cloud (or BMC) for every development request and installing the user's requirements locally. This approach offers advantages in terms of security, real-time backup, computing resources (incase of microservices which requiring 'heavy computing').
