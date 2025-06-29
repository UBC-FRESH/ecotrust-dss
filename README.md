# Overview

This repository includes a web-based app Decision Support System (DSS) that enables a user with a limitted skill set to improve forest management activities considering GHG emissions and Biodiversity concerns.

# Repository Structure

The main companents of the DSS is backend and frontend. The `util` script includes modules of the backend, and you can run the backend as an standalone tool by running the `scenario_running.ipynb`.
The webAppFrontEnd has the script of the web app.
The web application there are 3 major software components that constitute the entire web application. These 3 components are:
1. The actual Python web application, whech has been developed and tested on Ubuntu 24.04 operating system using Python 3.10.
2. Nginx web server as our choice of open-source web server
3. Gunicorn, which acts as the Python Web Server Gateway Interface (WSGI), a glue between the actual Python application and Nginx webserver.
To install and run the web application, follow these instructions:
1. Install Nginx
2. Clone this repository
3. create and activate a virtual environment and install Python 3.10
4. Install all required packages using the following command
       pip install -r requirements.txt
   This would install all required python packages into the virtual environment, including the WSGI sever Gunicorn.
5. Start the webv application using Gunicorn
   Inside the root of the repository, type the following command:
   /path/to/virtual/environment/gunicorn -t 0 -w 1 -b yyy.y.y.y:xxxx webAppFrontEnd:server
   where yyy.y.y.y is the user's local IP while xxxx is the port that the user wants the webapp to run on. For example, if the python virtual environment is in /home/myusername/environment and the user wants to run the web server on port 8002, the command would:
   /home/myusername/environment/bin/gunicorn -w 1 -b yyy.y.y.y:8002 webAppFrontEnd:server

# Input Dataset Download and Installation

The input dataset is set up as a DataLad-managed git submodule, so there are a few extra steps required to correctly download and install the dataset if you are deploying this repository to a new working directory.

Install the DataLad command (if not already available in your environment):
```bash
pip install datalad[full]
```

Initialize the git submodule:
```bash
git submodule update --init --recurive
```

Download the data:
```bash
datalad get data -r
```

The dataset contains one large (12 Gb) GIS polygon data layer (`ecotrust-dss-bc-data/merged_stands.gpkg`), which needed to be split into a 2-part ZIP archive to get around a 5 Gb upload file size limit in the S3 protocol interface we are using to push data files up to the Arbutus cloud object storage that is backing this. You will need to reconstitute this data layer back into a single file before running the parent web app. 

To reconstitute the data file into a useable format, run the following shell commands from the project root directory:
```bash
cd data/ecotrust-dss-bc-data
zip -FF merged_stands_split.zip --out merged_stands_fixed.zip
unzip merged_stands_fixed.zip
```
