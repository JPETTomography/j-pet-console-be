# How to run this stuff

go to `common/data_helpers` and get the data first


```
./download_data.sh
```

will download all the needed examplary data to the examplary_data folder.

For developement purposes, with volumes mounted up simply run

```
docker compose -f docker-compose.yaml -f docker-compose.agent.yaml -f docker-compose.local.yaml up --build
```

For deployment purposes run:

```
docker compose -f docker-compose.yaml up --build
```

then see `localhost:8000/docs`
to run full process of running agent, reading data from root, sending it to worker by json and then worker sending it to database use `/send_agent/` method


if the services did not stand up try calling them in this order

```
docker compose up web -d
docker compose up agent -d
docker compose up worker -d
```

or better yet, open each one in separate terminal

```
docker compose up web
docker compose up agent
docker compose up worker
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
