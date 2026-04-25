import json
import os
import boto3
import anthropic

# Cache SSM client and API key between Lambda invocations (warm start optimization)
_ssm = boto3.client("ssm")
_api_key_cache = None

SYSTEM_PROMPT = """You are an AI assistant representing Zheenbek Karaev, a Senior DevOps/SRE Engineer based in Chicago, IL.
Answer questions about him professionally and concisely (2-4 sentences max).

PROFILE:
- Experience: 6+ years in DevOps/SRE
- Currently: Senior DevOps Engineer at Wells Fargo (Nov 2023–Present)
- Previous: DevOps Engineer at The Home Depot (2019–2022)
- Side project: Octopus AI — cloud-based TMS platform with OpenAI API integrations

CORE SKILLS:
- Cloud: AWS (EKS, EC2, Lambda, RDS, S3, Route53, CloudWatch, Bedrock, SageMaker)
- IaC: Terraform, Ansible
- Containers: Kubernetes, Docker, Helm, ArgoCD
- CI/CD: Jenkins, GitHub Actions, GitLab CI
- Monitoring: Prometheus, Grafana, ELK Stack
- AI/ML Infra: AWS SageMaker, Bedrock, GitHub Copilot, OpenAI API integrations

CERTIFICATIONS:
- AWS Certified Solutions Architect – Associate
- HashiCorp Certified Terraform Associate

OPEN TO: Senior DevOps / SRE / Cloud Engineer roles in Chicago (hybrid or on-site)

RULES:
- Be helpful, concise, and professional
- Never fabricate specific metrics or numbers
- Salary questions: "Zheenbek prefers to discuss compensation directly in interviews"
- Contact: direct to the Contact section on karaevops.com
- Always respond in the same language the user writes in (English, Russian, etc.)
"""

def get_api_key():
    global _api_key_cache
    if _api_key_cache:
        return _api_key_cache
    param = _ssm.get_parameter(
        Name=os.environ["SSM_PARAM_NAME"],
        WithDecryption=True
    )
    _api_key_cache = param["Parameter"]["Value"]
    return _api_key_cache


def lambda_handler(event, context):
    allowed_origin = os.environ.get("ALLOWED_ORIGIN", "https://karaevops.com")

    headers = {
        "Access-Control-Allow-Origin": allowed_origin,
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Content-Type": "application/json"
    }

    # Preflight
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}

    try:
        body = json.loads(event.get("body") or "{}")
        messages = body.get("messages", [])

        if not messages:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "No messages provided"})
            }

        # Keep last 10 messages to control cost
        messages = messages[-10:]

        # Validate roles
        for msg in messages:
            if msg.get("role") not in ("user", "assistant"):
                raise ValueError("Invalid message role")

        client = anthropic.Anthropic(api_key=get_api_key())

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=messages
        )

        reply = response.content[0].text

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"reply": reply})
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Something went wrong. Please try again."})
        }
