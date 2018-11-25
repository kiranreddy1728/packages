import psycopg2
import time
import urllib2
import sys
from datetime import datetime
from readCfg import ConfigRead
from itertools import islice
import timeit
import os
import boto
import boto.s3
from boto.s3.key import Key
import boto3
from botocore.client import Config
from utility import UtilityClass
import shutil



flow_id=sys.argv[1]
step_id=sys.argv[2]

start_time=timeit.default_timer()

print("Flow id is="+str(flow_id)+" step_id="+str(step_id))
if(flow_id.strip()==""):
	print("Flow id is empty")
print("----------SETTING VARIABLES FROM PROPERTIES FILE------------")	
ConfigRead.set_flow_id(flow_id,str(step_id))
print("----------Local To Redshift------------")

User = ConfigRead.S3_REDSHIFT_USERNAME_REDSHIFT
print(User)
Pwd = ConfigRead.S3_REDSHIFT_PASSWORD_REDSHIFT
print(Pwd)
Host = ConfigRead.S3_REDSHIFT_HOST_NAME_REDSHIFT
print(Host)
Port = ConfigRead.S3_REDSHIFT_PORT_NUMBER_REDSHIFT
print(Port)
table_name_list = ConfigRead.S3_REDSHIFT_TABLE_NAME_LIST
print(table_name_list)
DatabaseName = ConfigRead.S3_REDSHIFT_SCHEMA_NAME
print(DatabaseName)
#print(ConfigRead.Redshift_COLUMN_LIST)
#elapsed=timeit.default_timer() - start_time
#print("Total time Taken was: "+str(elapsed)+" Seconds!")


DATABASE_NAME=ConfigRead.S3_REDSHIFT_SCHEMA_NAME
HOST=ConfigRead.S3_REDSHIFT_HOST_NAME_REDSHIFT
USER=ConfigRead.S3_REDSHIFT_USERNAME_REDSHIFT
PASSWORD=ConfigRead.S3_REDSHIFT_PASSWORD_REDSHIFT
PORT = ConfigRead.S3_REDSHIFT_PORT_NUMBER_REDSHIFT
cnx= psycopg2.connect(dbname=DATABASE_NAME,host=HOST,port=PORT,user=USER,password=PASSWORD)

uploadFileNames = []
extension = '.csv'
QueryMode=""
'''
if(ConfigRead.S3_REDSHIFT_SRC_COMPRESSION.lower()=="zip"):
	extension='.zip'
	QueryMode="ZIP"
'''
if(ConfigRead.S3_REDSHIFT_SRC_COMPRESSION.lower()=="gz" or ConfigRead.S3_REDSHIFT_SRC_COMPRESSION.lower()=="gzip" or ConfigRead.S3_REDSHIFT_SRC_COMPRESSION.lower()=="gzip2"):
	extension='.gz'
	QueryMode="GZIP"

print("Extention is: "+extension)
print("QueryMode is: "+QueryMode)
# listCol=[]
# listCol=ConfigRead.REDSHIFT_COLUMN_LIST.split(",")
# createState=''
# comma1=''
# for i in listCol:
	# createState=createState+comma1 +' '+'`'+i+'`'+' '+'varchar(100)'
	# comma1=','
ziped_file_path_list=[]
try:
	print("AccessKeyId:"+ConfigRead.S3_ACCESS_KEY_ID_REDSHIFT)
	print("SecretAccessKeyId:"+ConfigRead.S3_SECRET_KEY_REDSHIFT)
	conn = boto.connect_s3(ConfigRead.S3_ACCESS_KEY_ID_REDSHIFT,ConfigRead.S3_SECRET_KEY_REDSHIFT)
	print("Redshhiftbucket:"+ConfigRead.S3_BUCKET_NAME_REDSHIFT)
	print("ConfigRead.S3_REDSHIFT_SRC_PREFIX="+ConfigRead.S3_REDSHIFT_SRC_PREFIX+" extention:"+extension)
	bucket = conn.get_bucket(ConfigRead.S3_BUCKET_NAME_REDSHIFT)
	bucket_list = bucket.list()

	
	
	for l in bucket_list:
			#print("key:"+l.key)
			keyString = str(l.key)
			#print("Keystr:"+keyString)
			if(keyString.startswith(ConfigRead.S3_REDSHIFT_SRC_PREFIX) and keyString.endswith(extension)):
				#print("KeyString Obtained: "+keyString)
				#list=keyString.strip('/')
				#print list
				#print("Strip:"+str(keyString.split(os.sep)))
				'''
				if(extension==".zip"):
					print("Zip UnCompression Selected= "+ConfigRead.S3_REDSHIFT_SRC_COMPRESSION)
					print("Copying file "+keyString+" to local temp Location: "+full_file_path_local_temp)
					if not os.path.exists(full_file_path_local_temp+flow_id+'/'):
						os.makedirs(full_file_path_local_temp+flow_id+"/")
						print("Directory Created!")
					print("Path Exists:"+str(os.path.exists(full_file_path_local_temp+flow_id+'/')))
					#if(os.path.exists(full_file_path_local)):
					print("Downloading file...")
					
					s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))
					temp_zip_file_location=""+full_file_path_local_temp+flow_id+"/"+keyString.split("/")[-1]
					s3_client.download_file(ConfigRead.S3_REDSHIFT_BUCKET_NAME, keyString, temp_zip_file_location)
					print("Downloading finished...")
					
					print("Unziping : "+temp_zip_file_location)
					path_to_zip_file=""+temp_zip_file_location
					directory_to_extract_to=full_file_path_local_temp+flow_id+"/uncompress/"
					print("ZIP path:"+path_to_zip_file)
					print("Directory to extract to:"+directory_to_extract_to)
					#+tail.split(".")[0]+".csv"
					filepath="'"+full_file_path_local_temp+flow_id+"/uncompress/"+(keyString.split("/")[-1]).split(".")[0]+".csv'"
					print("ZIP to CSV")
					UtilityClass.convert_zip_to_csv(path_to_zip_file,directory_to_extract_to)
					ziped_file_path_list.append(full_file_path_local_temp+flow_id+"/uncompress/"+(keyString.split("/")[-1]).split(".")[0]+".csv")
				'''
				fileName=''+keyString.split(os.sep)[-1]
				print("FileNames identified is: "+str(fileName))
				uploadFileNames.append(fileName)
	print("Files to be loaded: "+str(uploadFileNames))
except Exception as e:
	print("Error in Bucket Connection!!")
	print(str(e))
print("Ziped files path List:"+str(ziped_file_path_list))
try:
	delimiter=ConfigRead.S3_REDSHIFT_SRC_FILE_DELIMITER
	delimiter_mode=""
	if(delimiter<>None):
		delimiter=','
		delimiter_mode="delimiter '"+delimiter+"'"
	else:
		delimiter_mode="delimiter '"+delimiter+"'"
	#delimiter=","
	strCols=""
	comma=""
	cursor = cnx.cursor()
	for colname in ConfigRead.S3_REDSHIFT_COLUMN_LIST.split(','):
		type="varchar(100)"
		strCols=strCols+""+comma+"\""+colname+"\" "+type
		comma=","
	query="CREATE TABLE IF NOT EXISTS "+ConfigRead.S3_REDSHIFT_TABLE_NAME_LIST+" ("+strCols+");"
	print("CreateQuery: "+query)
	cursor.execute(query)
	print("automatically creating table if NOT EXISTS.")
	
	iam_role_mode=" iam_role '"+ConfigRead.S3_REDSHIFT_SRC_IAM_ROLE+"' "
	print("iam role mode: "+iam_role_mode)
	i=0
	for filename in uploadFileNames:
		print("Copying or inserting File: "+filename)
		#format: 's3://<bucket-name>/<file-path>' NOTE: will get prefix ending with /
		'''
		if(ConfigRead.S3_REDSHIFT_SRC_COMPRESSION.lower()=="zip"):
		
			#csv_file = open(str(ziped_file_path_list[i]), 'r')
			query100="COPY "+ConfigRead.S3_REDSHIFT_TABLE_NAME_LIST+" from '"+ziped_file_path_list[i]+"' delimiter '"+delimiter+"' removequotes;"
			#print("ZIPQuery:"+query100)
			#cursor.copy_expert(query100,file = csv_file)
			#cursor.copy_from(csv_file, ConfigRead.S3_REDSHIFT_TABLE_NAME_LIST, sep=''+delimiter)
			#csv_file.close()
		else:
		'''
		print("table name : " + ConfigRead.S3_REDSHIFT_TABLE_NAME_LIST)
		#print("Bucket Name : " + ConfigRead.S3_REDSHIFT_BUCKET_NAME)
		print("prefix :"+ConfigRead.S3_REDSHIFT_SRC_PREFIX)
		print("filename : " + filename)
		print("delimiter : " + delimiter_mode)
		print("IAM ROLE : " + iam_role_mode)
		query100="COPY "+ConfigRead.S3_REDSHIFT_TABLE_NAME_LIST+" from 's3://"+ConfigRead.S3_BUCKET_NAME_REDSHIFT+"/"+ConfigRead.S3_REDSHIFT_SRC_PREFIX+filename+"' "+iam_role_mode+" "+QueryMode+" "+delimiter_mode+";"#removequotes
		#query100="COPY "+ConfigRead.S3_REDSHIFT_TABLE_NAME_LIST+" from 's3://"+ConfigRead.S3_BUCKET_NAME_REDSHIFT+"/"+ConfigRead.S3_REDSHIFT_SRC_PREFIX+filename+"' CREDENTIALS 'aws_access_key_id="+ConfigRead.S3_ACCESS_KEY_ID_REDSHIFT+";aws_secret_access_key="+ConfigRead.S3_SECRET_KEY_REDSHIFT+"' "+QueryMode+" delimiter '"+delimiter+"';"#removequotes
		print("Query:"+query100)
		cursor.execute(query100)
		i+=1
	cnx.commit()
	print("All Files Commited to SQL")
except Exception as e:
	print("Error")
	print(str(e))
	cnx.rollback()
	
	
finally:
	print("Connection Closed!!")
	cnx.close()


'''
query100="COPY "+ConfigRead.REDSHIFT_TGT_TABLE_NAME_LIST+" from 's3://"+ConfigRead.REDSHIFT_BUCKET_NAME+"/"+ConfigRead.S3_REDSHIFT_SRC_PREFIX+"' CREDENTIALS 'aws_access_key_id="+ConfigRead.REDSHIFT_ACCESS_KEY_ID+";aws_secret_access_key="+ConfigRead.REDSHIFT_SECRET_KEY+"' delimiter '"+ConfigRead.REDSHIFT_FILE_DELIMITER+"' removequotes;"
print("Query:"+query100)
try:
	cursor = cnx.cursor()
	cursor.execute(query100)
	cnx.commit()
	print("Commited to SQL")
except Exception as e:
	print("Error")
	print(str(e))
	cnx.rollback()
	print(er)
	print("Rolling Back coz of Error:"+str(er))
finally:
	print("Connection Closed!!")
	cnx.close()
'''

elapsed=timeit.default_timer() - start_time
print("Total time Taken was: "+str(elapsed)+" Seconds!")
