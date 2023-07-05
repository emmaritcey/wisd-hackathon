import boto3
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()



def download_s3_bucket(bucket_name, keys):
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    for key in keys:
        objs = list(bucket.objects.filter(Prefix=key))
        for obj in objs:
            #print(obj.key)
            if os.path.exists('data/'+obj.key)==False: #only download if file hasn't already been downloaded
                # remove the file name from the object key
                obj_path = os.path.dirname(obj.key)
                local_path = 'data/' + obj_path

                # create nested directory structure in data folder
                Path(local_path).mkdir(parents=True, exist_ok=True)

                # save file with full path locally in data folder
                bucket.download_file(obj.key, 'data/'+obj.key)
            else:
                print(obj.key + ' already exists')


