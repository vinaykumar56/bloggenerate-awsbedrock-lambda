import boto3
import botocore.config
import json
import datetime


def generate_blog_bedrock(topic:str)->str:
    #prompt
    prompt = f"""
    <s>[INST]Human: Write a blog in 200 words on the topic {topic}
    Assistant:[/INST]
    """
    #Body
    body = {
        "prompt":prompt,
        "max_gen_len":512,
        "temperature": 0.5,
        "top_p":0.9
    }
    try:
        #bedrockClient
        bedrockClient = boto3.client("bedrock-runtime", region_name="us-east-1", 
                                     config=botocore.config.Config(read_timeout=300,retries={'max_attempt':3}))
        #model ID
        model_id = "meta.llama3-8b-instruct-v1:0" 
        response = bedrockClient.invoke_model(body=json.dumps(body),model_id=model_id)
        response_content = json.loads(response.get('body').read())
        blog = response_content['generation']
        return blog
    except Exception as e:
        print(f"Error in generating blog:{e}")
        return ""


def save_blog_details_s3(bucket,key,blog):
    s3Client=boto3.client('s3')
    try:
        s3Client.put_object(Buket = bucket, Key=key, Body=blog)
        print("blog text saved to s3")
    except Exception as e:
        print("error saving blog file to s3 : {e}")    



def lambda_handler(event, context):
    event = json.loads(event['body'])
    topic = event['blogTopic']
    blog = generate_blog_bedrock(topic=topic)
    if blog:
        currentTime = datetime.now().strftime('%H%M%S')
        s3Key = f"blogOutput/{topic}_{currentTime}.txt"
        s3Bucket = 'aws_bedrock_test'
        save_blog_details_s3(s3Bucket,s3Key,blog)
    else:
        print("No blog was generated")











