import requests
import json
import random
import time
import os

# GETTING JSONs THROUGH API 
 
# SET REQUIRED IDs DIAPASONE
START_CID = 1        
END_CID = 2500000     
COUNT = 200000  # total number of photos to download       

SAVE_FOLDER = "pastvu_photos" 
os.makedirs(SAVE_FOLDER, exist_ok=True)

API_URL = "https://api.pastvu.com/api2"

def get_photo_info(cid):
    params = {
        "method": "photo.giveForPage",
        "params": {"cid": cid}
    }

    try:
        response = requests.get(API_URL, params={"method": "photo.giveForPage",
                                                 "params": json.dumps({"cid": cid})})
        data = response.json()

        return data

    except Exception as e:
        print(f"Error for CID={cid}: {e}")
        return None


def save_json(cid, data):
    filename = f"{SAVE_FOLDER}/photo_{cid}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {filename}")


def main():
    random_cids = random.sample(range(START_CID, END_CID + 1), COUNT)

    for cid in random_cids:
        data = get_photo_info(cid)

        if data:
            save_json(cid, data)

        time.sleep(0.4) # choose optimal time 


if __name__ == "__main__":
    main()
