import json
import copy
import shared_vars as sv
from datetime import datetime
from models.settings import Settings
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from exchange_workers.bybit_http import BybitAPI

# Initialize Firebase SDK
cred = credentials.Certificate('rychara-31314.json')
firebase_admin.initialize_app(cred)

# Create a Firestore client
db = firestore.client()

def write_data_to_array(collection, document, field, data):
    doc_ref = db.collection(collection).document(document)
    doc_ref.update({
        field: firestore.ArrayUnion([data])
    })

def get_last_element(collection, document, field):
    doc_ref = db.collection(collection).document(document)
    doc = doc_ref.get()
    if doc.exists:
        array = doc.to_dict()[field]
        if array:
            last_saldo_dict =  json.loads(array[-1])
            return float(last_saldo_dict['saldo'])
        else:
            return 0.
    else:
        return 0.


# Write data to Firestore
def write_data(collection, document, name, status):
    doc_ref = db.collection(collection).document(document)
    doc_ref.update({name: status})

# Read data from Firestore
def read_data(collection, document):
    doc_ref = db.collection(collection).document(document)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return None
    
def change_rating(coin: str, plus_minus_value: int):
    doc_ref = db.collection('coin_rating').document('coins')
    doc = doc_ref.get()
    if doc.exists:
        rating = doc.get(f'{coin}.rating')
        new_rating = rating + plus_minus_value if rating != 0 else 0
        doc_ref.update({f'{coin}.rating': new_rating})

def write_settings(collections, document, prop, settings):
    doc_ref = db.collection(collections).document(document)
    
    doc_ref.update({prop: vars(settings)})

def delete_prop_from_settings(collections, document, prop):
    doc_ref = db.collection(collections).document(document)
    
    doc_ref.update({prop: firestore.DELETE_FIELD})

def write_exchange_limits(exchanges_positions_limit):
    doc_ref = db.collection('settings').document('individual_ex_settings')
    for key, value in exchanges_positions_limit.items():
        doc_ref.update({key: value})

def read_exchange_limits():
    doc_ref = db.collection('settings').document('individual_ex_settings')
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        print('No such document!')