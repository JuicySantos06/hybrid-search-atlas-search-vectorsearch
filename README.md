# Hybrid Search with Atlas Search & Vector Search

![Screenshot 2023-10-18 at 10 47 48](https://github.com/JuicySantos06/hybrid-search-atlas-search-vectorsearch/assets/84564830/9c4cbd11-d3bd-4a95-b03b-15f20f422231)

## General Information
> The following demo aims to demonstrate the ability to enhance the search experience through the joint use of both keyword-based and vector-based search technology.
> We will be using using the following native MongoDB technologies:
* MongoDB Atlas Search
* MongoDB Atlas Vector Search

### Step 1 : Import Cross-Market Recommendations dataset into your Atlas Database
> Download the US Home and Kitchen/metadata category dataset.
```
link: https://xmrec.github.io/data/us/
```
> Create the following database and collection in Atlas
```
DB_NAME = hybrid_search_xmarket
COLLECTION_NAME = hybrid_search_dataset
```
> Extract and import the data into the aforementioned collection using Compass or any other tools you see fit.

### Step 2: Edit the hybrid_search_encoding_data_module.py file
> Update the MONGODB_ATLAS_URI parameter with your Atlas connection string.

### Step 3: Run the the hybrid_search_encoding_data_module.py file
> Ensure that you have installed the relevant Python package beforehand.
```
pip install sentence-transformers
pip install pymongo
pip install numpy
```
> Run the script and then wait until completion.
```
python hybrid_search_encoding_data_module.py
```
