import boto
import boto.s3
import sys
from boto.s3.key import Key

AWS_ACCESS_KEY_ID = 'XXXXXXXXXXX'
AWS_SECRET_ACCESS_KEY = 'XXXXXXXXXXX'

bucket_name = AWS_ACCESS_KEY_ID.lower() + '-dump'
conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY)


bucket = conn.create_bucket(bucket_name,
    location=boto.s3.connection.Location.DEFAULT)

testfile = "C:\Users\KiranReddy\Downloads\project3.csv"
print 'Uploading %s to Amazon S3 bucket %s' % \
   (testfile, bucket_name)
   
def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()
k = Key(bucket)
k.key = testfile
k.set_contents_from_filename(testfile,cb=percent_cb, num_cb=10)
k.set_acl('public-read-write')
k.generate_url(expires_in=0, query_auth=False)
print 'uploading was completed'
