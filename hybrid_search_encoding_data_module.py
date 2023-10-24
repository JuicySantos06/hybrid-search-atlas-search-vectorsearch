from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import numpy

MONGODB_ATLAS_URI = "<EDIT_WITH_YOUR_PARAMETER>"
DB_NAME = "hybrid_search_xmarket"
COLLECTION_NAME = "hybrid_search_dataset"
MONGODB_CLIENT = MongoClient(MONGODB_ATLAS_URI)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def normalize_data(vectorData):
    return (vectorData/numpy.linalg.norm(vectorData))

def startup_db_connection():
    try:
        MONGODB_CLIENT.list_database_names()
        print('Database connection established........')
        return True
    except OperationFailure as err:
        print (f"Datacase Connection failed. Error: {err}")
        return False
        
def startup_db_client(resultingStartupDbConnection):
    if (resultingStartupDbConnection == True):
        mongodbDatabase = MONGODB_CLIENT[DB_NAME]
        mongodbCollection = mongodbDatabase[COLLECTION_NAME]
        return mongodbCollection

def data_product_embedding(resultingStartupDbClient):
    for doc in resultingStartupDbClient.find():
        try:
            print('Dataset embedding in progress - please wait')
            docFilter = {"_id": doc["_id"]}
            if (len(doc["description"]) == 0):
                continue
            else:
                descriptionVectorEmbedding = model.encode(doc["description"])
                descriptionVectorEmbeddingList = descriptionVectorEmbedding.tolist()
                descriptionVectorEmbeddingDimension = len(descriptionVectorEmbedding)
                descriptionVectorEmbeddingNormalized = normalize_data(descriptionVectorEmbedding).tolist()
                newFieldAttributes = {"$set":{"descriptionVectorEmbedding":descriptionVectorEmbeddingList,"descriptionVectorEmbeddingDimension":descriptionVectorEmbeddingDimension,"descriptionVectorEmbeddingNormalized":descriptionVectorEmbeddingNormalized}}
                resultingStartupDbClient.update_one(docFilter,newFieldAttributes)
        except Exception as ex:
            print (f"Exception encountered: {ex}")

def main():
    data_product_embedding(startup_db_client(startup_db_connection()))
    print('Dataset embedding finished - congratulations')
    
if __name__ == "__main__":
    main()
    
    
