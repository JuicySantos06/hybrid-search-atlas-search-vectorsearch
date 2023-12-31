# Hybrid Search with Atlas Search & Atlas Vector Search

![Screenshot 2023-10-18 at 10 47 48](https://github.com/JuicySantos06/hybrid-search-atlas-search-vectorsearch/assets/84564830/9c4cbd11-d3bd-4a95-b03b-15f20f422231)

## General Information
> The following demo aims to demonstrate the ability to enhance the search experience through the joint use of both keyword-based and vector-based search technology.
> We will be using using the following native MongoDB technologies:
* MongoDB Atlas Search
* MongoDB Atlas Vector Search
> Beforehand, we will be looking at the first generation of text search in order to appreciate the fantastic technology evolution we have delivered throughout MongoDB.

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

## Search technology gen0

### Step 2: Create a text index on the field title
> Choose whichever methods you see fit to create the aforementionned a text index on the aforementionned field.
> hybrid_search_xmarket.hybrid_search_dataset.createIndex( { "title": “text” } )

### Step 3: Install the following Python packages
> Ensure that you have installed the relevant Python package beforehand.
```
pip install pymongo
pip install pandas
pip install requests
```

### Step 4: Run the text_search.py file
> That version 1 uses a basic Atlas Search indexing feature (no typo tolerance, autocomplete, whatsover).
> Here are a sample of items we queried:
```
* I want an ice cream spoon
* silver ice cream spoon
* scoop for ice cream
```

## Search technology gen1

### Step 5: Edit the hybrid_search_encoding_data_module.py file
> Update the MONGODB_ATLAS_URI parameter with your Atlas connection string.

### Step 6: Run the hybrid_search_encoding_data_module.py file
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

### Step 7 (Optional): Edit the hybrid_search_text_search_and_vector_search.py file
> You can change the number of results by updating the numOfResults parameter.

### Step 8: Create the following Atlas Search index for version 1 of our hybrid search engine
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

### Step 9: Create the following Atlas Vector Search index for version 1 of our hybrid search engine
> Create the following Atlas Vector Search index.
> Index name = vectorIndex.
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

### Step 10: Install the following Python packages
> Ensure that you have installed the relevant Python package beforehand.
```
pip install sentence-transformers
pip install pymongo
pip install pandas
pip install requests
```

### Step 11: Run the hybrid_search_text_search_and_vector_search.py file
> That version 1 uses a basic Atlas Search indexing feature (no typo tolerance, autocomplete, whatsover).
> Here are a sample of items we queried:
```
* I want an ice cream spoon
* silver ice cream spoon
* scoop for ice cream
```

## Search technology gen2

### Step 12: Create the following Atlas Search index for version 2 of our hybrid search engine
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
        }
      ]
    }
  }
}
```

### Step 13 (Optional): Edit the hybrid_search_text_search_typo_tolerance_and_vector_search.py file
> You can change the number of results by updating the numOfResults parameter.

### Step 14: Run the hybrid_search_text_search_typo_tolerance_and_vector_search.py file
> That version 2 uses an enhanced Atlas Search indexing feature (typo tolerance) which is then being injected into Atlas Vector Search query.
> Here are a sample of items we queried:
```
* eye want an ice cram spoo
* silvar ice crem spon
* scop for ice crem
```

## Conclusion
> This demonstration shows the evolution of search technologies and the complementarity of keyword-based and semantic-based search technology in order to provide the most accurate search capability for your customers.
