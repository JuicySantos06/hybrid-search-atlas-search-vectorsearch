from pymongo import MongoClient
import pymongo
import pandas
from pymongo.collection import ObjectId, OperationFailure
import requests

mongodbAtlasDatabase = "hybrid_search_xmarket"
mongodbAtlasCollection = "hybrid_search_dataset"
numOfResults = 10

def init_result_file_html(paramQuery):
    textFile = open("./hybridSearchResult.html","w")
    textFile.write("<html>\n<head>\n<title> \nMongoDB Hybrid Search Results \</title>\n</head><body><h><center>User Search Query: "+paramQuery+"</center></h><hr></body>\n")
    textFile.close()

def insert_data_result_file(paramHtmlFileResult,paramSectionTitle):
    textFile = open("./hybridSearchResult.html","a")
    textFile.write("\n<body><h1><center>"+paramSectionTitle+"</center></h1>\n</body>")
    textFile.write("\n<body><i1><center>"+paramHtmlFileResult+"</center></i1>\n</body>")
    textFile.write("\n<body><j1></j1>\n<hr></body>\n")
    textFile.close()
  
def startup_db_connection(paramMongodbAtlasConnectionString):
    try:
        mongodbClient = MongoClient(paramMongodbAtlasConnectionString)
        mongodbClient.list_database_names()
        return mongodbClient
    except pymongo.errors.OperationFailure as err:
        print (f"Datacase Connection failed. Error: {err}")

def startup_db_client(paramStartupDbConnection,paramMongodbDatabaseName):
    if (paramStartupDbConnection):
        mongodbDatabase = paramStartupDbConnection[paramMongodbDatabaseName]
        return mongodbDatabase

def mongodb_text_search_query(paramStartupDbClient,paramMongodbCollectionName,paramUserQuery,paramNumOfResults):
    mongodbCollection = paramStartupDbClient[paramMongodbCollectionName]
    try:
        searchResult = mongodbCollection.aggregate([
        {
            "$match":
            {
                "$text": {
                    "$search": paramUserQuery,
                }
            }
        },
        {
            "$limit": paramNumOfResults
        },
        {
            "$project":
            {
                "_id": 1,
                "title": 1,
            }
        }
        ])
        return searchResult
    except OperationFailure as err:
        print (f"Error related to mongodb_atlas_search_query function: {err}")

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
    mongodbAtlasUri = input("Enter MongoDB Atlas connection string: ")
    userQuery = input("Enter search item: ")
    init_result_file_html(userQuery)
    listOfHtmlFileResults = dict()
    currMongoClient = startup_db_connection(mongodbAtlasUri)
    pandas.set_option('mode.chained_assignment',None)

    #TEXT SEARCH
    searchResultList = mongodb_text_search_query(startup_db_client(currMongoClient,mongodbAtlasDatabase),mongodbAtlasCollection,userQuery,numOfResults)
    searchResultDataFrame = pandas.DataFrame(list(searchResultList))
    searchResultNumpyArray = searchResultDataFrame.to_numpy() 
    displaySearchResult = pandas.DataFrame(searchResultNumpyArray,columns=['ID','NAME'])
    displaySearchResult['IMAGE'] = None
    dictOfProductImg = []
    for i in range(len(displaySearchResult)):
        productId = displaySearchResult['ID'].iloc[i]
        for doc in mongodb_atlas_product_img_retrieval(startup_db_client(currMongoClient,mongodbAtlasDatabase),mongodbAtlasCollection,productId):
            dictOfProductImg.append(doc['imgUrl'][0].split('"')[1])  
    displaySearchResult['IMAGE'] = dictOfProductImg
    listOfHtmlFileResults["MongoDB Text Search Results"] = displaySearchResult.to_html(escape=False,formatters=dict(IMAGE=to_img_tag))
    dbCursor = startup_db_client(startup_db_connection(mongodbAtlasUri),mongodbAtlasDatabase)
    collCursor = dbCursor["textSearchQueryResult"]
    collCursor.drop()
    for i in range(len(displaySearchResult)):
        try:
            collCursor.insert_one({
                "_id": ObjectId(displaySearchResult['ID'].iloc[i]),
                "productName": displaySearchResult['NAME'].iloc[i],
                "productImg": displaySearchResult['IMAGE'].iloc[i],
            })
        except OperationFailure as err:
            print(f"Error related to mongodb_atlas_product_img_retrieval function: {err}")

    for key,value in listOfHtmlFileResults.items():
        insert_data_result_file(value,key)

if __name__ == "__main__":
    main()
