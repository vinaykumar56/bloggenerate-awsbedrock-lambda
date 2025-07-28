import boto3
import botocore.config
import json
import datetime

#bedrockClient
bedrockClient = boto3.client("bedrock-runtime", region_name="us-east-1", 
config=botocore.config.Config(read_timeout=300,retries={'max_attempts':3}))

s3Client=boto3.client('s3')

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
        #model ID
        model_id = "meta.llama3-8b-instruct-v1:0" 
        response = bedrockClient.invoke_model(body=json.dumps(body),modelId=model_id)
        response_content = json.loads(response.get('body').read())
        blog = response_content['generation']
        print(f"blog generated for topic {topic}")
        print(blog)
        return blog
    except Exception as e:
        print(f"Error in generating blog:{e}")
        return ""


def save_blog_details_s3(bucket,key,blog):
    
    try:
        s3Client.put_object(Bucket = bucket, Key=key, Body=blog)
        print("blog text saved to s3")
    except Exception as e:
        print("error saving blog file to s3 :",e)    



def lambda_handler(event, context):
    print(event)
    event = json.loads(event['body'])
    print(event)
    topic = event['blogTopic']
    print(topic)
    blog = generate_blog_bedrock(topic=topic)
    if blog:
        currentTime = datetime.datetime.now().strftime('%H%M%S')
        s3Key = f"blogOutput/{topic}_{currentTime}.txt"
        s3Bucket = 'vinay-balyan'
        save_blog_details_s3(s3Bucket,s3Key,blog)
        return {
            'statusCode': 200,
            'body': json.dumps('Blog generated and saved to S3')
        }
    else:
        print("No blog was generated")
        return {
            'statusCode': 500,
            'body': json.dumps('Error generating blog')
        }