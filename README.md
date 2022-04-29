#### TextractAWS: 
Amazon Textract uses the Optical Character Recognition (OCR) that automatically extracts the text and structured data.  

In this demo, we have extracted the entities from pdf, png, jpg, and jpeg formats(other formats are not allowed in Amazon Textract).

#### Steps to Follow:
Create an AWS account, set the IAM user, and connect to EC2 cloud of amazon.

We created a bucket, and we wrote a python code that automatically stores the files in S3 bucket. We changed the name of the files with random id’s in order to avoid the conflit of two or more people having the same name.

You can check the output in the postman. 

#### Key point:

- The .doc and .docx formats are not valid in textract.
- You can send file in .pdf, .jpeg, .jpg and .png formats.
- To get more details on Amazon Textract formats you can refer https://aws.amazon.com/textract/faqs/
