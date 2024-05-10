import functions_framework
from google.cloud import firestore
import json

db = firestore.Client()
COLLECTION_NAME = "example_collection"

@functions_framework.http
def firebase_connector(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600'
    }
    if request.method == 'OPTIONS':
        return ('Success', 204, headers)
    
    if request.method == 'POST':
        request_json = request.get_json(silent=True)
        if request_json['request_type'] == 'getUserInfo':
            collection = db.collection(COLLECTION_NAME)
            doc = collection.document(str(request_json['user_id'])).get().to_dict()
            return (doc, 200, headers)
        
        if request_json['request_type'] == 'getAllUserInfo':
            collection = db.collection(COLLECTION_NAME)
            doc = collection.document().get().to_dict()
            return (doc, 200, headers)
        
        if request_json['request_type'] == 'createUser':
            collection = db.collection(COLLECTION_NAME)
            doc = collection.document(str(request_json['user_id']))
            if 'update_dict' in request_json:
                if isinstance(request_json['update_dict'], dict):
                    update_dict = request_json['update_dict']
                else:
                    try:
                        update_dict = json.loads(request_json['update_dict'])
                    except TypeError as err:
                        return ({"message": f"Incompatible update_dict: {err}\n{request_json['update_dict']}"}, 400, headers)
                doc.set(update_dict)
                return ({"message": "Success"}, 200, headers)
            else:
                return ({"message": "Invalid request type"}, 400, headers)
        
        if request_json['request_type'] == 'updateUserInfo':
            collection = db.collection(COLLECTION_NAME)
            doc = collection.document(str(request_json['user_id']))
            if isinstance(request_json['update_dict'], dict):
                update_dict = request_json['update_dict']
            else:
                try:
                    update_dict = json.loads(request_json['update_dict'])
                except TypeError as err:
                    return ({"message": f"Incompatible update_dict: {err}\n{request_json['update_dict']}"}, 400, headers)
            doc.update(update_dict)
            return ({"message": "Success"}, 200, headers)
        
        if request_json['request_type'] == 'checkUser':
            collection = db.collection(COLLECTION_NAME)
            doc = collection.document(str(request_json['user_id'])).get().exists
            if doc:
                return ({"message": "True"}, 200, headers)
            else:
                return ({"message": "False"}, 200, headers)

    if request.method == 'GET':
        return 'Hello World!'