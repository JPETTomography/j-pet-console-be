# Deployment on jpet servers

## Agent

First setup the vpn to be able to access project,
Need to connect to server (currently jpet3 aka. x.x.x.220).
Ther should already be a tmux session running.
Inside the tmux session there should be an opened folder `~/repos/agent`.
It already has `config.yaml` and `docker-compose.depl.yml` which set correct paths.
The `~/rootfiles` should contain the actual data taken by the machine, the agent is setup so that it will monitor that folder, and upon encountering the change it will process the new file and send it to worker.

## Backend

Go to github -> actions -> backend, click "run workflow", select the branch you want to deploy.

## Frontend

Go to github -> actions -> frontend, click "run workflow", select the branch you want to deploy.


# Developement Setup

## Agent
go to `common/data_helpers` and get the data first


```
./download_data.sh
```

It will download all the needed examplary data to the examplary_data folder.

Then **inside the ``agent/`` folder**, create a config file:

```
cp examplary_config.yaml config.yaml
```

Edit config.yaml as necessesary, then do:

```
docker compose -f docker-compose.yaml -f docker-compose.local.yaml up --build
```

This should start agent.

## Backend and worker

For developement purposes, with volumes mounted up simply run

```
docker compose -f docker-compose.yaml -f docker-compose.local.yaml up --build
```

The `docker-compose.local.yaml` adds local files as volumes to sync without rebuilding.

For deployment purposes run:

```
docker compose -f docker-compose.yaml up --build
```

then see `localhost:8000/docs`
to run full process of running agent, reading data from root, sending it to worker by json and then worker sending it to database use `/send_agent/` method

## Frontend

Inside the `frontend/` folder:

```
docker compose -f docker-compose.yaml -f docker-compose.local.yaml up --build
```

# Demo step by step

1. Download the repo
2. Download the git submodule using
3. Download data. Use `common/data_helpers/download_data.sh` to download exemplary files to `examplary_data_hold` folder and copy `histo_description.json` to `examplary_data`

```
git submodule init
git submodule update --remote --recursive

```

4. Run backend


```
docker compose -f docker-compose.yaml -f docker-compose.local.yaml up --build
```

5. Run frontend

```
cd j-pet-console-fe
docker compose -f docker-compose.yml up --build
```

6. Run Agent

```
cd agent
cp examplary_config.yaml config.yaml
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build

```

6. Open http://localhost:8000/docs and trigger `seed`
7. Wait untill all of the services are up
8. Copy any .root file from `examplary_data_hold` to `examplary_data` - this will trigger root conversion and upload
