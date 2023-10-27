from pymongo import MongoClient
import pymongo
import pandas
from pymongo.collection import ObjectId, OperationFailure
from sentence_transformers import SentenceTransformer
import requests
import time
import numpy

#define global variables
mongodbAtlasUri = "mongodb+srv://akilsk:Sofia06061991.@cluster0.vdddl.mongodb.net/?retryWrites=true&w=majority"
mongodbAtlasDatabase = "hybrid_search_xmarket"
mongodbAtlasCollection = "hybrid_search_dataset"
userQuery = "ice cream spoon"
numOfResults = 10

#define html result file initialization - https://towardsdatascience.com/text-search-vs-vector-search-better-together-3bd48eb6132a
def init_result_file_html(paramQuery):
    textFile = open("./hybridSearchResult.html","w")
    textFile.write("<html>\n<head>\n<title> \nMongoDB Hybrid Search Results \</title>\n</head><body><h><center>User Search Query: "+paramQuery+"</center></h><hr></body>\n")
    textFile.close()

#enrich html report file
def insert_data_result_file(paramHtmlFileResult,paramSectionTitle):
    textFile = open("./hybridSearchResult.html","a")
    textFile.write("\n<body><h1><center>"+paramSectionTitle+"</center></h1>\n</body>")
    textFile.write("\n<body><i1><center>"+paramHtmlFileResult+"</center></i1>\n</body>")
    textFile.write("\n<body><j1></j1>\n<hr></body>\n")
    textFile.close()

#define model to be used for encoding product title field
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
#define db connection initialization
def startup_db_connection(paramMongodbAtlasConnectionString):
    try:
        mongodbClient = MongoClient(paramMongodbAtlasConnectionString)
        mongodbClient.list_database_names()
        return mongodbClient
    except pymongo.errors.OperationFailure as err:
        print (f"Datacase Connection failed. Error: {err}")

#define db client initialization
def startup_db_client(paramStartupDbConnection,paramMongodbDatabaseName):
    if (paramStartupDbConnection):
        mongodbDatabase = paramStartupDbConnection[paramMongodbDatabaseName]
        return mongodbDatabase

#Atlas Search query
def mongodb_atlas_search_query(paramStartupDbClient,paramMongodbCollectionName,paramUserQuery,paramNumOfResults):
    mongodbCollection = paramStartupDbClient[paramMongodbCollectionName]
    try:
        searchResult = mongodbCollection.aggregate([
        {
            '$search': {
                'index': 'searchIndex',
                'autocomplete': {
                    'path': 'title', 
                    'query': paramUserQuery,
                    'tokenOrder': 'any',
                    'fuzzy': {
                        'maxEdits': 2,
                        'prefixLength': 1,
                        'maxExpansions': 2
                        
                    }
                },
                'highlight': {
                    'path': 'title'
                }
            }
        }, 
        {
            '$limit': int(paramNumOfResults)
        },
        {
            '$project': {
                '_id': 1, 
                'title': 1,
                 
                'score': {
                    '$meta': 'searchScore'
                }
            }
        }, 
        {
            '$sort': {
                'score': -1
            },
        }
        ])
        return searchResult
    except OperationFailure as err:
        print (f"Error related to mongodb_atlas_search_query function: {err}")

#product image retrieval
def mongodb_atlas_product_img_retrieval(paramStartupDbClient,paramMongodbCollectionName,paramProductId):
    mongodbCollection = paramStartupDbClient[paramMongodbCollectionName]
    try:
        productImgRetrieval = mongodbCollection.aggregate([
        {
            '$match': {
                '_id': ObjectId(paramProductId)
            }
        }, {
            '$project': {
                '_id': 1, 
                'imgUrl': {
                    '$split': [
                        '$imgUrl', ',\"'
                    ]
                }
            }
        }
        ])    
        return productImgRetrieval
    except OperationFailure as err:
        print(f"Error related to mongodb_atlas_product_img_retrieval function: {err}")

#define Atlas Vector Search query
def mongodb_atlas_vector_search_query(paramStartupDbClient,paramMongodbCollectionName,queryEmbedding,paramNumOfResults):
    mongodbCollection = paramStartupDbClient[paramMongodbCollectionName]
    try:
        vectorSearchResult = mongodbCollection.aggregate([
        {
            '$search': {
                'index': 'vectorIndex',
                'knnBeta': {
                    'vector': queryEmbedding, 
                    'path': 'descriptionVectorEmbedding',
                    'k': paramNumOfResults
                }
            }
        }, 
        {
            '$project': {
                '_id': 1, 
                'title': 1,
                'score': {
                    '$meta': 'searchScore'
                } 
            }
        }   
        ])
        return vectorSearchResult
    except OperationFailure as err:
        print (f"Error related to mongodb_atlas_vector_search_query function: {err}")


def mongodb_atlas_cleanse_enrich(paramStartupDbClient,paramMongodbCollectionName):
    mongodbCollection = paramStartupDbClient[paramMongodbCollectionName]
    try:
        #print(f"cleansing and enriching {mongodbCollection}")
        result = mongodbCollection.aggregate([
            {
                    '$lookup': {
                        'from': mongodbAtlasCollection, 
                        'localField': '_id', 
                        'foreignField': '_id', 
                        'as': 'result', 
                        'pipeline': [
                            {
                                '$project': {
                                    '_id': 0, 
                                    'description': 1, 
                                    'related.boughtTogether': 1, 
                                    'related.compared': 1
                                }
                            }
                        ]
                    }
                }, {
                    '$unwind': {
                        'path': '$result'
                    }
                }, {
                    '$set': {
                        'productDescription': '$result.description', 
                        'productsBoughtTogether': {
                            '$concatArrays': [
                                '$result.related.boughtTogether', '$result.related.compared'
                            ]
                        }
                    }
                }, {
                    '$project': {
                        'productName': 1, 
                        'productImg': 1, 
                        'productScore': 1, 
                        'productDescription': 1, 
                        'productsBoughtTogether': 1
                    }
                },
                {
                    '$out': paramMongodbCollectionName
                }
        ])
        return result
    except OperationFailure as err:
        print (f"Error related to mongodb_atlas_cleanse_enrich function: {err}")
    

# convert your links to html tags 
def download_product_image(paramUrl,paramFileName):
    url = paramUrl
    file_name = "./" + paramFileName

    res = requests.get(url, stream = True).content
    with open(file_name,'wb') as f:
        f.write(res)
    print('Image sucessfully Downloaded: ',file_name)
    return file_name

def to_img_tag(path):
    return '<img src="'+ path + '"width=50">'
    
def main():
    init_result_file_html(userQuery)
    listOfHtmlFileResults = dict()

    currMongoClient = startup_db_connection(mongodbAtlasUri)

    pandas.set_option('mode.chained_assignment',None)

    #ATLAS SEARCH
    searchResultList = mongodb_atlas_search_query(startup_db_client(currMongoClient,mongodbAtlasDatabase),mongodbAtlasCollection,userQuery,numOfResults)
    searchResultDataFrame = pandas.DataFrame(list(searchResultList))
    #print(searchResultDataFrame)

    searchResultMaxScore = searchResultDataFrame['score'].loc[searchResultDataFrame.index[0]]
    searchResultNumpyArray = searchResultDataFrame.to_numpy()
    
    for searchResultDataFrameRow in searchResultDataFrame.itertuples():
        currScore = searchResultDataFrame.at[searchResultDataFrameRow.Index,'score']
        normalizedScore = (currScore/searchResultMaxScore)
        searchResultNumpyArray[searchResultDataFrameRow.Index,2] = normalizedScore
    
    displaySearchResult = pandas.DataFrame(searchResultNumpyArray,columns=['ID','NAME','SCORE'])
    displaySearchResult['IMAGE'] = None
    dictOfProductImg = []
    for i in range(len(displaySearchResult)):
        productId = displaySearchResult['ID'].iloc[i]
        for doc in mongodb_atlas_product_img_retrieval(startup_db_client(currMongoClient,mongodbAtlasDatabase),mongodbAtlasCollection,productId):
            dictOfProductImg.append(doc['imgUrl'][0].split('"')[1])  
    displaySearchResult['IMAGE'] = dictOfProductImg

    listOfHtmlFileResults["MongoDB Atlas Search Results"] = displaySearchResult.to_html(escape=False,formatters=dict(IMAGE=to_img_tag))

    #WRITE ATLAS SEARCH RESULT INTO MONGODB COLLECTION
    dbCursor = startup_db_client(startup_db_connection(mongodbAtlasUri),mongodbAtlasDatabase)
    collCursor = dbCursor["atlasSearchQueryResult"]
    collCursor.drop()
        
    for i in range(len(displaySearchResult)):
        try:
            collCursor.insert_one({
                "_id": ObjectId(displaySearchResult['ID'].iloc[i]),
                "productName": displaySearchResult['NAME'].iloc[i],
                "productImg": displaySearchResult['IMAGE'].iloc[i],
                "productScore": displaySearchResult['SCORE'].iloc[i]
            })
        except OperationFailure as err:
            print(f"Error related to mongodb_atlas_product_img_retrieval function: {err}")
      
    #ATLAS VECTOR SEARCH
    userQueryVectorEmbedding = model.encode(userQuery)
    vectorSearchResultList = mongodb_atlas_vector_search_query(startup_db_client(currMongoClient,mongodbAtlasDatabase),mongodbAtlasCollection,userQueryVectorEmbedding.tolist(),numOfResults)
    
    #print(vectorSearchResultList)

    vectorSearchResultDataFrame = pandas.DataFrame(list(vectorSearchResultList))
    vectorSearchResultMaxScore = vectorSearchResultDataFrame['score'].loc[searchResultDataFrame.index[0]]
    vectorSearchResultNumpyArray = vectorSearchResultDataFrame.to_numpy()
    
    for vectorSearchResultDataFrameRow in vectorSearchResultDataFrame.itertuples():
        currScore = vectorSearchResultDataFrame.at[vectorSearchResultDataFrameRow.Index,'score']
        normalizedScore = (currScore/vectorSearchResultMaxScore)
        vectorSearchResultNumpyArray[vectorSearchResultDataFrameRow.Index,2] = normalizedScore

    displayVectorSearchResult = pandas.DataFrame(vectorSearchResultNumpyArray,columns=['ID','NAME','SCORE'])
    displayVectorSearchResult['IMAGE'] = None
    dictOfProductImg = []
    for i in range(len(displayVectorSearchResult)):
        productId = displayVectorSearchResult['ID'].iloc[i]
        for doc in mongodb_atlas_product_img_retrieval(startup_db_client(currMongoClient,mongodbAtlasDatabase),mongodbAtlasCollection,productId):
            dictOfProductImg.append(doc['imgUrl'][0].split('"')[1])  
    displayVectorSearchResult['IMAGE'] = dictOfProductImg

    listOfHtmlFileResults["MongoDB Atlas Vector Search Results"] = displayVectorSearchResult.to_html(escape=False,formatters=dict(IMAGE=to_img_tag))

    #WRITE ATLAS VECTOR SEARCH RESULT INTO MONGODB COLLECTION
    dbCursor = startup_db_client(startup_db_connection(mongodbAtlasUri),mongodbAtlasDatabase)
    collCursor = dbCursor["atlasVectorSearchQueryResult"]
    collCursor.drop()

    for i in range(len(displaySearchResult)):
        try:
            collCursor.insert_one({
                "_id": ObjectId(displayVectorSearchResult['ID'].iloc[i]),
                "productName": displayVectorSearchResult['NAME'].iloc[i],
                "productImg": displayVectorSearchResult['IMAGE'].iloc[i],
                "productScore": displayVectorSearchResult['SCORE'].iloc[i]
            })
        except OperationFailure as err:
            print(f"Error related to mongodb_atlas_product_img_retrieval function: {err}")


    #CLEANSE AND ENRICH PREVIOUS RESULTS
    time.sleep(2)
    mongodb_atlas_cleanse_enrich(startup_db_client(currMongoClient,mongodbAtlasDatabase),"atlasSearchQueryResult")
    #CLEANSE AND ENRICH PREVIOUS RESULTS
    time.sleep(2)
    mongodb_atlas_cleanse_enrich(startup_db_client(currMongoClient,mongodbAtlasDatabase),"atlasVectorSearchQueryResult")

    for key,value in listOfHtmlFileResults.items():
        insert_data_result_file(value,key)

if __name__ == "__main__":
    main()
