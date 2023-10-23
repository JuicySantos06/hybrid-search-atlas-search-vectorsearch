from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import numpy

#define global variables
MONGODB_ATLAS_URI = "<EDIT_WITH_YOUR_PARAMETER>"
DB_NAME = "sample_xmarket"
COLLECTION_NAME = "homeAndKitchen"
MONGODB_CLIENT = MongoClient(MONGODB_ATLAS_URI)

#define model to be used for encoding product title field
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

#define vector normalization - frobenius norm (numpy.linalg.norm(vectorData) is a generalization of the Euclidean norm for multi-dimensional arrays
def normalize_data(vectorData):
    return (vectorData/numpy.linalg.norm(vectorData))

#define connection initialization
def startup_db_connection():
    try:
        MONGODB_CLIENT.list_database_names()
        print('Database connection established........')
        return True
    except OperationFailure as err:
        print (f"Datacase Connection failed. Error: {err}")
        return False

#define client db initialization
def startup_db_client(resultingStartupDbConnection):
    if (resultingStartupDbConnection == True):
        mongodbDatabase = MONGODB_CLIENT[DB_NAME]
        mongodbCollection = mongodbDatabase[COLLECTION_NAME]
        return mongodbCollection

#define groceryAndGourmetFood data embedding
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
    
    
