# Hybrid Search with Atlas Search & Vector Search

![Screenshot 2023-10-18 at 10 47 48](https://github.com/JuicySantos06/hybrid-search-atlas-search-vectorsearch/assets/84564830/9c4cbd11-d3bd-4a95-b03b-15f20f422231)

## General Information
> The following demo aims to demonstrate the ability to enhance the search experience through the joint use of both keyword-based and vector-based search technology.
> We will be using using the following native MongoDB technologies:
* MongoDB Atlas Search
* MongoDB Atlas Vector Search

### Step 1 : Import the Cross-Market Recommendations dataset into your Atlas Database
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

### Step 3: Run the hybrid_search_encoding_data_module.py file
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

### Step 4: Edit the hybrid_search_text_search_and_vector_search.py file
> Update the mongodbAtlasUri parameter with your Atlas connection string.
> Update the userQuery parameter with your query.
> You can also change the number of results by updating the numOfResults parameter.

### Step 5: Create the following Atlas Search index for version 1 of our hybrid search engine
> Create the following Atlas Search index.
> Note that the index has to be linked to the right collection that is hybrid_search_dataset.
> Here is the index definition.
> Index name = default.
```
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "title": {
        "type": "string"
      }
    }
  }
}
```

### Step 6: Create the following Atlas Vector Search index for version 1 of our hybrid search engine
> Create the following Atlas Vector Search index.
```
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "descriptionVectorEmbeddingNormalized": {
        "dimensions": 384,
        "similarity": "dotProduct",
        "type": "knnVector"
      }
    }
  }
}
```

### Step 7: Install the following Python packages
> Ensure that you have installed the relevant Python package beforehand.
```
pip install sentence-transformers
pip install pymongo
pip install pandas
pip install requests
```

### Step 8: Run the hybrid_search_text_search_and_vector_search.py file
> That version 1 uses a basic Atlas Search indexing feature (no typo tolerance, autocomplete, whatsover).
> Here are a sample of items we queried using that hybrid search engine:
```
* I want an ice cream spoon
* silver ice cream spoon
* scoop for ice cream
```

### Step 9: Create the following Atlas Search index for version 2 of our hybrid search engine
> Create the following Atlas Search index.
> Note that the index has to be linked to the right collection that is hybrid_search_dataset.
> Here is the index definition.
> Index name = searchIndex.
```
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "title": [
        {
          "type": "string"
        },
        {
          "foldDiacritics": true,
          "maxGrams": 15,
          "minGrams": 2,
          "tokenization": "edgeGram",
          "type": "autocomplete"
        }
      ]
    }
  }
}
```

### Step 10: Edit the hybrid_search_text_search_typo_tolerance_and_vector_search.py file
> Update the mongodbAtlasUri parameter with your Atlas connection string.
> Update the userQuery parameter with your query.
> You can also change the number of results by updating the numOfResults parameter.
