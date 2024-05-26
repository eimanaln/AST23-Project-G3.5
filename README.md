## Automated Cross-Platform Compatibility Testing for Infrastructure as Code 

We present an automated testing framework designed to verify the cross-platform compatibility of Ansible automation scripts across different operating systems. Utilizing black-box functional testing and custom test oracles, our framework validates the functional requirements of IaC deployments across various platforms. Its modular architecture facilitates the incorporation of additional operating systems, deployment scripts, and test oracles, ensuring adaptability and scalability.

### Requirements
- [Python 3.12](https://www.python.org/downloads/release/python-3123/) or higher
- [Docker](https://docs.docker.com/get-docker/)
- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
- [Pipenv](https://pypi.org/project/pipenv/) (Recommended)

### Installation
1. Clone the repository:  
   `git clone https://github.com/eimanaln/AST24-Project-G3_5.git`  
   `cd AST24-Project-G3_5`
2. Install the required Python packages using pipenv  
    `pipenv install`

### Usage
1. Run the test  
    `pipenv run python ansible_os_distribution_test.py`

### Files and Folders
- `test_resources`: This folder contains the ansible playbooks that are used to deploy the Apache and Nginx servers, `deploy_apache.yml` and `deploy_nginx.yml`. 
- `test_runner/test_oracle`: This folder contains the three test oracle classes that are used to test the deployed infrastructures, `aliveness_oracle.py`,`recap_oracle.py` and `vulnerability_oracle.py`. 
- `host_manager`: This folder contains the class that manages the creation, network setup and deleting Docker containers. 
- `ansible_os_distribution_test.py`: This is the file that is responsible for starting the test framework. 


### Contributors 
This is a project for Automated Software Testing 2024 at ETH Zurich by Eiman Alnuaimi and Matteo Nussbaumer. 
