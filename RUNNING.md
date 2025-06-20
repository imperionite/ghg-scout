# ghg-scout

**GHG Scout PH** is an open-source, API-driven, community-based greenhouse gas (GHG) emission web application of the [GHG Data Explorer PH](https://ghgph-55623.firebaseapp.com/) designed to **empower schools and LGUs in the Philippines** to monitor, estimate, and visualize their local GHG emissions. It bridges the gap between national-level reporting systems like the [Philippine Greenhouse Gas Inventory Management and Reporting System (PGHGIMRS)](https://niccdies.climate.gov.ph/ghg-inventory) and community-level participation.

This tool is designed to be lightweight, educational, and locally relevant — supporting GHG emissions awareness and its climate change impact and reporting at the grassroots level.

This section provides a list of the common CLI commands used during the entire development process.

---

## CLI Commands

**Run MongoDB container**

```sh
docker run -d \
  --name mongodb \
  -p 37017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
  -e MONGO_INITDB_ROOT_PASSWORD=secret \
  -e MONGO_INITDB_DATABASE=ghg_scout \
  mongo
```

**Mongodb connection string**

```sh
mongodb://mongoadmin:secret@localhost:37017/ghg_scout?authSource=admin
```

**Mongo shell from host machine**
```sh
mongosh "mongodb://mongoadmin:secret@localhost:27017/ghg_scout?authSource=admin"
# Once connected, you’re in myappdb. Confirm by running
db
```

**From inside the MongoDB container**

```sh
# Get mongodb container names or id, if needed
docker ps
docker exec -it mongodb mongosh -u mongoadmin -p secret --authenticationDatabase admin
# show all db
show databasesdb.stats()
# Then, once inside mongosh, switch to app database
use ghg_scout

```

**Common commands**

```sh
# Get stats
db.stats()
# Drop current DB
db.dropDatabase()
# List collections on current DB
show collections
# Drop collection
db.collection_name.drop()
# Find all document
db.collection_name.find()
# Exit shell
# Count documents
db.collection_name.countDocuments()
exit

```

**To run the app**

```sh
# initial run only when DB is not yet seeded
./build.sh
# main: the name of your Python file (without .py)
# app: the name of your FastAPI instance
# --reload: enables auto-reload on code changes (useful for development)
uvicorn main:app --reload # main.py
# Docs: http://127.0.0.1:8000/docs
# Root: http://127.0.0.1:8000

# create new virtual env and upgrade pip and install dependencies from requirements file
pip cache purge && rm -rf venv && python -m venv venv && source vevn/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
```

