## Pyrenote, The E4E Manual Audio Labeling System

This project, Pyrenote, creates moment to moment or strong labels for audio data. Pyrenote and much of this README are based on heavily on [Audino](https://github.com/midas-research/audino) as well as [Wavesurfer.js](https://github.com/katspaugh/wavesurfer.js). The name is a combination of Py, Lyrebird, and note (such as making a note on a label).

If you want to use Pyrenote, use the following to get started!

**NOTE**: Before making any changes to the code, make sure to create a branch to safely make changes. Never commit directly to main or production branch.
**Read github_procedures.md for more detailed information before contributing to the repo.** 

## Usage

*Note: Before getting the project set up, message project leads for env file. This file should be put in `/audino`. **Make sure the file is never pushed to the github***

Please install the following dependencies to run `Pyrenote` on your system:

1. [git](https://git-scm.com/) *[tested on v2.23.0]*
2. [docker](https://www.docker.com/) *[tested on v19.03.8, build afacb8b]*
3. [docker-compose](https://docs.docker.com/compose/) *[tested on v1.25.5, build 8a1c60f6]*

### Clone the repository

```sh
$ git clone https://github.com/UCSD-E4E/Pyrenote.git
$ cd audino
```

**Note for Windows users**: Please configure git to handle line endings correctly as services might throw an error and not come up. You can do this by cloning the project this way:

```sh
$ git clone https://github.com/UCSD-E4E/Pyrenote.git --config core.autocrlf=input
```

### For Development (Note this is the one we will test on and use)

Similar to `production` setup, you need to use development [configuration](./docker-compose.dev.yml) for working on the project, fixing bugs and making contributions.
**Note**: Before proceeding further, you might need to give docker `sudo` access or run the commands listed below as `sudo`.

**To build the services (do this when you first start it), run:**  
**Note**: Remember to cd into audino before starting
```sh
$ docker-compose -f docker-compose.dev.yml build
```

**To bring up the services, run:**
```sh
$ docker-compose -f docker-compose.dev.yml up
```
Then, in browser, go to [http://localhost:3000/](http://localhost:3000/) to view the application.

**To bring down the services, run:**

```sh
$ docker-compose -f docker-compose.dev.yml down
```
## Troubleshooting for starting docker

1) Docker containers do not even get a chance to start
  - Make sure docker is set up properly
  - Make sure docker itself has started. On Windows, check the system tray and hover over the icon to see the current status. Restart it if necessary
2) Backend crashes
  - For this error, check the top of the log. It should be complaining about /r characters in the run-dev.sh files
  - The backend will crash if the endline characters are set to CRLF rather than LF
  - On VSCode, you can swap this locally via going into the file and changing the CRLF icon in the bottom right to LF
  - Do this for `frontend/scripts/run-dev.sh` and `backend/scripts/run-dev.sh`
3) Database migration issues
  - If the backend complains about compiler issues while the database migration is occurring go into `backend/scripts/run-dev.sh`
  - On line 25, check and make sure that the stamp command is pointing to the right migration for the database
      - Ask for help on this one

## Getting Started

At this point, the docker should have gotten everything set up. After going to [http://localhost:3000/](http://localhost:3000/) you should be able to log into the docker

To access the site, sign in with the username of **admin** and password of **password**. On logging in, navigate to the admin-portal to create your first project. Make sure to make a label group and some labels for the project!

After creating a project, get the API key by returning to the admin portal. You can use the API key to add data to a project. Create a new terminal (while docker is running the severs) and cd into `audino/backend/scripts`. Here use the following command:

```
python upload_mass.py --username admin.test --is_marked_for_review True --audio_file C:\REPLACE\THIS\WITH\FOLDER\PATH\TO\AUDIO\DATA --host localhost --port 5000 --api_key REPLACE_THIS_WITH_API_KEY
```
Make sure to have a folder with the audio data ready to be added. For testing purposes, get a folder with about 20 clips. 

Once that runs, you are ready to start testing!


### For Production (Don't use on windows)

You can either run the project on [default configuration](./docker-compose.prod.yml) or modify them to your need.  
**Note**: Before proceeding further, you might need to give docker `sudo` access or run the commands listed below as `sudo`.  
**Note**: Remember to cd into audino before starting  

**To build the services, run:**

```sh
$ docker-compose -f docker-compose.prod.yml build
```

**To bring up the services, run:**

```sh
$ docker-compose -f docker-compose.prod.yml up
```

Then, in browser, go to [http://0.0.0.0/](http://0.0.0.0/) to view the application.

**To bring down the services, run:**

```sh
$ docker-compose -f docker-compose.prod.yml down
```

### For Dev Team:
Features should be turned on and off by admins for individual projects. When adding a new feature to either a project's data page or
annotation page, make sure to do the following:
1) Go to `.\audino\frontend\src\containers\forms\featureForm.js`
2) Add a new item in the featuresEnabled directory. This will be the name of the `feature_toggle` variable. 
3) Return to the page you are working on. 
  - For example, if you are working on the annotation page, navigate to the `componentDidMount()` method
  - about 20 lines down in the `setState` callback, add to the list `SOME_VAR: response.data.features_list['VARIABLE_NAMED_IN_STEP_2']`.

  