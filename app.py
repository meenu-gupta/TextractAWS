from flask import Flask, jsonify, request
from trp import Document
import random
import boto3
import time
import os
app = Flask(__name__)

s3BucketName = "give bucket name"
aws_access_key_id="give access id"
aws_secret_access_key= "give secret key"
region_name = "give region name"

textract = boto3.client('textract', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key, region_name=region_name)


def startJob(s3BucketName, documentName):
	response = None
	client = boto3.client('textract', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key, region_name=region_name)
	response = client.start_document_text_detection(
	DocumentLocation={
		'S3Object': {
			'Bucket': s3BucketName,
			'Name': documentName
		}
	})
	return response["JobId"]

def isJobComplete(jobId):
	time.sleep(5)
	client= boto3.client('textract', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key, region_name=region_name)
	response = client.get_document_text_detection(JobId=jobId)
	status = response["JobStatus"]
	
	print("Job status: {}".format(status))
	while(status == "IN_PROGRESS"):
		time.sleep(5)
		response = client.get_document_text_detection(JobId=jobId)
		status = response["JobStatus"]
		
		print("Job status: {}".format(status))
	
	return status

def getJobResults(jobId):

	pages = []
	time.sleep(5)
	client= boto3.client('textract', aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key, region_name=region_name)
	response = client.get_document_text_detection(JobId=jobId)
	
	pages.append(response)
	print("Resultset page recieved: {}".format(len(pages)))
	nextToken = None
	if('NextToken' in response):
		nextToken = response['NextToken']

	while(nextToken):
		time.sleep(5)
		response = client.get_document_text_detection(JobId=jobId, NextToken=nextToken)
		pages.append(response)
		print("Resultset page recieved: {}".format(len(pages)))
		nextToken = None
		if('NextToken' in response):
			nextToken = response['NextToken']
	return pages

def saveImage(image):
	image_name = "{}_{}".format(random.randint(100000, 999999),image.name)
	print('--------------------------->> File name')
	print(image_name)
	s3 = boto3.client("s3", aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
	acl="public-read"
	url = s3.upload_fileobj(
			image,
			s3BucketName,
			image_name,
			ExtraArgs={
				"ACL": acl,
				"ContentType": image.content_type
			}
		)

	s3_location = "https://{}.s3.ap-south-1.amazonaws.com/".format("extext")
	return "{}{}".format(s3_location, image_name), image_name

@app.route('/extract', methods=['POST'])
def index():
	s3BucketName= s3BucketName
	if request.method == 'POST':
		if 'file' not in request.files:
			return jsonify({"message": 'No file provided/Check the key, spelling or any space after or in the key.'})
		file = request.files['file']
		if file.filename == '':
			return jsonify({"message": 'No file selected.'})

	filename, file_extension =  os.path.splitext(file.filename)
	# print(f'{filename}, {file_extension}')

	for im in dict((request.files).lists())['file']: 
		image_url, image_name = saveImage(im)
	# print(image_url, image_name)
	
	jobId = startJob(s3BucketName, image_name)
	print(jobId)
	5007
	print("Started job with id: {}".format(jobId))
	if(isJobComplete(jobId)):
		response = getJobResults(jobId)

	if (file_extension) == ".pdf":    
		text = ''
		for resultPage in response:
			for item in resultPage["Blocks"]:
				if item["BlockType"] == "LINE":
					
					print ('\033[94m' +  item["Text"] + '\033[0m')
					text = text + " " + item["Text"]

					
		
		
		comprehend= boto3.client("comprehend", aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key, region_name=region_name)

		# Detect sentiment
		sentiment =  comprehend.detect_sentiment(LanguageCode="en", Text=text)
		print ("\nSentiment\n========\n{}".format(sentiment.get('Sentiment')))

		# Detect entities
		en= []
		entities =  comprehend.detect_entities(LanguageCode="en", Text=text)
		print("\nEntities\n========")
		
		for entity in entities["Entities"]:
			v= "{} : {}".format(entity["Type"], entity["Text"])
			# print(v)
			en.append(v)
		# print(en)
		return jsonify({"message": en})

	elif ((file_extension) == ".png") or ((file_extension) == ".jpeg") or ((file_extension) == ".jpg"):
	
		doc = Document(response)
		for page in doc.pages:
		# Print fields
			all_fields = []
			print("Fields:")
			for field in page.form.fields:
				x = "Key: {}, Value: {}".format(field.key, field.value)
				print(x)
				all_fields.append(x)
				# print("Key: {}, Value: {}".format(field.key, field.value))

			# Get field by key
			get_field_by_key=[]
			print("\nGet Field by Key:")
			key = "Phone Number:"
			field = page.form.getFieldByKey(key)
			if(field):
				y = "Key: {}, Value: {}".format(field.key, field.value)
				print(y)
				get_field_by_key.append(y)
				# print("Key: {}, Value: {}".format(field.key, field.value))

			search_field_by_key=[]
			# Search fields by key
			print("\nSearch Fields:")
			key = "address"
			fields = page.form.searchFieldsByKey(key)
			for field in fields:
				z = "Key: {}, Value: {}".format(field.key, field.value)
				print(z)
				search_field_by_key.append(z)
			# print(z)
				# print("Key: {}, Value: {}".format(field.key, field.value))
		return jsonify({"Fields":all_fields, "Get_Field_by_Key":get_field_by_key, "Search_Field_by_Key":search_field_by_key})

if __name__ == '__main__':
	app.run(host= '0.0.0.0', port=5007, debug=True)
