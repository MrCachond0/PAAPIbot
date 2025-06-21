import os
import datetime
import hashlib
import hmac
import requests
import json
from dotenv import load_dotenv

load_dotenv()

AMAZON_ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY')
AMAZON_SECRET_KEY = os.getenv('AMAZON_SECRET_KEY')
AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG')
AMAZON_REGION = "us-east-1"
AMAZON_SERVICE = "ProductAdvertisingAPI"
AMAZON_HOST = "webservices.amazon.com"
AMAZON_ENDPOINT = f"https://{AMAZON_HOST}/paapi5/searchitems"

# Función para firmar la solicitud (AWS Signature V4)
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'aws4_request')
    return kSigning

def search_amazon_items(keyword, item_count=1):
    method = 'POST'
    service = AMAZON_SERVICE
    host = AMAZON_HOST
    region = AMAZON_REGION
    endpoint = AMAZON_ENDPOINT
    content_type = 'application/json; charset=utf-8'
    amz_target = 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems'
    request_parameters = {
        "Keywords": keyword,
        "SearchIndex": "All",
        "ItemCount": item_count,
        "PartnerTag": AMAZON_ASSOCIATE_TAG,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.com",
        "Resources": [
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Images.Primary.Large",
            "ItemInfo.Features",
            "ItemInfo.ByLineInfo",
            "BrowseNodeInfo.BrowseNodes"
        ]
    }
    request_payload = json.dumps(request_parameters)
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    canonical_uri = '/paapi5/searchitems'
    canonical_querystring = ''
    canonical_headers = f'content-encoding:utf-8\ncontent-type:{content_type}\nhost:{host}\nx-amz-date:{amz_date}\nx-amz-target:{amz_target}\n'
    signed_headers = 'content-encoding;content-type;host;x-amz-date;x-amz-target'
    payload_hash = hashlib.sha256(request_payload.encode('utf-8')).hexdigest()
    canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{date_stamp}/{region}/{service}/aws4_request'
    string_to_sign = f'{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'
    signing_key = getSignatureKey(AMAZON_SECRET_KEY, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = (
        f'{algorithm} Credential={AMAZON_ACCESS_KEY}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, Signature={signature}'
    )
    headers = {
        'Content-Encoding': 'utf-8',
        'Content-Type': content_type,
        'Host': host,
        'X-Amz-Date': amz_date,
        'X-Amz-Target': amz_target,
        'Authorization': authorization_header
    }
    response = requests.post(endpoint, data=request_payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error Amazon PAAPI: {response.status_code} - {response.text}")
        return None

# Ejemplo de uso directo
if __name__ == "__main__":
    keyword = "fitness"
    result = search_amazon_items(keyword)
    print(json.dumps(result, indent=2))
