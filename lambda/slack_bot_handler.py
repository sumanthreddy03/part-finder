import json
import os
import hmac
import hashlib
import time
import base64
import boto3
import urllib.request
import urllib.parse

# Slack app and API configuration
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
YOUR_WEBSITE_API_URL = os.environ.get("YOUR_WEBSITE_API_URL")

# Lamba invokes itself asynchronously to avoid slack timeout limits
LAMBDA_FUNCTION_NAME = os.environ.get("LAMBDA_FUNCTION_NAME", "slack_bot_handler")

lambda_client = boto3.client("lambda")


def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    # Handle async lambda invocations triggered by Slack requests
    if event.get("async_task") == "partfinder":
        return run_partfinder_async(event)

    if event.get("async_task") == "partfinder_channel":
        return run_partfinder_channel_async(event)

    path = event.get("rawPath") or event.get("path", "")
    headers = event.get("headers", {}) or {}
    body = event.get("body", "") or ""

    if path == "/health":
        return response(200, "OK")

    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")

    print("PATH:", path)
    print("DECODED BODY:", body)

    # Slack Events API endpoint for app mentions and URL verification
    if "/events" in path or "/slack/events" in path:
        return handle_events(body)

    # Slash commands must be verified before processing
    if not verify_slack_signature(headers, body):
        return response(403, "Invalid signature")

    if "/commands" in path:
        return handle_slash_command(body)

    return response(404, "Not found")


def handle_slash_command(body):
    # Parse Slack slash command payload
    params = dict(urllib.parse.parse_qsl(body))

    command = params.get("command", "")
    text = params.get("text", "")
    response_url = params.get("response_url", "")

    if command != "/find":
        return slack_response(f"Unknown command: {command}")

    inputs = text.strip().split()

    if len(inputs) != 2:
        return slack_response(
            "Usage: `/partfinder <part_number> <home_site>`\nExample: `/partfinder PART1001 SITE_A`"
        )

    part_number = inputs[0].strip()
    home_site = inputs[1].strip().upper()

    payload = {
        "async_task": "partfinder",
        "part_number": part_number,
        "home_site": home_site,
        "response_url": response_url
    }

    # Invoke Lambda asynchronously to avoid Slack timeout limits
    lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8")
    )

    return slack_response(
        f"Searching for part `{part_number}` from home site `{home_site}`. I’ll post results here when ready."
    )


def handle_events(body):
    # Handle Slack Events API requests
    data = json.loads(body)

    if data.get("type") == "url_verification":
        return response(
            200,
            json.dumps({"challenge": data["challenge"]}),
            content_type="application/json"
        )

    event = data.get("event", {})

    if event.get("type") == "app_mention":
        text = event.get("text", "")
        channel = event.get("channel", "")

        parts = text.strip().split()

        # Expected format: @PART_FINDER <part_number> <home_site>
        if len(parts) < 3:
            post_message_to_channel(
                channel,
                "Usage: `@PART_FINDER <part_number> <home_site>`\nExample: `@PART_FINDER 1001 SITE_A`"
            )
            return response(200, "")

        part_number = parts[1].strip()
        home_site = parts[2].strip().upper()

        payload = {
            "async_task": "partfinder_channel",
            "part_number": part_number,
            "home_site": home_site,
            "channel": channel
        }

        # Process app mention search asynchronously
        lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType="Event",
            Payload=json.dumps(payload).encode("utf-8")
        )

        post_message_to_channel(
            channel,
            f"Searching for part `{part_number}` from home site `{home_site}`. I’ll post results here when ready."
        )

    return response(200, "")


def run_partfinder_async(event):
    # Execute slash command search and respond using Slack response_url
    part_number = event["part_number"]
    home_site = event["home_site"]
    response_url = event["response_url"]

    result = fetch_data_from_website(part_number, home_site)
    formatted = format_response(result)

    post_to_response_url(response_url, {
        "response_type": "in_channel",
        "text": formatted
    })

    return {
        "statusCode": 200,
        "body": "Async completed"
    }


def fetch_data_from_website(part_number, home_site):
    # Call Flask/API endpoint that performs part search
    payload = json.dumps({
        "apn": part_number,
        "input_site_code": home_site
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            YOUR_WEBSITE_API_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)

    except Exception as e:
        print("WEBSITE API ERROR:", str(e))
        return {"error": str(e)}


def post_to_response_url(response_url, payload):
    # Post delayed slash-command response back to Slack
    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        response_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        print("SLACK POST RESPONSE:", resp.read().decode("utf-8"))


def run_partfinder_channel_async(event):
    # Execute @mention search and post results into the Slack channel
    part_number = event["part_number"]
    home_site = event["home_site"]
    channel = event["channel"]

    result = fetch_data_from_website(part_number, home_site)
    formatted = format_response(result)

    post_message_to_channel(channel, formatted)

    return {
        "statusCode": 200,
        "body": "Channel async completed"
    }


def post_message_to_channel(channel, text):
    # Send message to Slack channel using chat.postMessage
    url = "https://slack.com/api/chat.postMessage"

    payload = {
        "channel": channel,
        "text": text
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        print("SLACK CHANNEL POST:", resp.read().decode("utf-8"))


def verify_slack_signature(headers, body):
    # Verify Slack request authenticity using signing secret
    timestamp = headers.get("x-slack-request-timestamp", "")
    signature = headers.get("x-slack-signature", "")

    if not timestamp or not signature:
        return False

    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    sig_basestring = f"v0:{timestamp}:{body}"

    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode("utf-8"),
        sig_basestring.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, signature)


def format_response(data):
    # Format API response into a Slack-readable fixed-width table
    if isinstance(data, dict) and "error" in data:
        return f":x: Error: {data['error']}"

    rows = data.get("results", []) if isinstance(data, dict) else data

    if not rows:
        return "No matching parts found."

    columns = [
        ("site", "SITE", 8),
        ("apn", "APN", 8),
        ("inventory_units", "UNITS", 6),
        ("min_level", "MIN", 5),
        ("max_level", "MAX", 5),
        ("inventory_status", "STATUS", 12),
        ("total_inventory_units_above_max", "ABV_MAX", 8),
        ("planner_aliases", "PLANNER_ALIASES", 24),
        ("distance_miles", "DIST", 8),
    ]

    lines = ["*Part Finder Results*", "```"]

    header = " ".join([f"{label:<{width}}" for _, label, width in columns])
    lines.append(header)
    lines.append("-" * len(header))

    for row in rows:
        values = []

        for key, label, width in columns:
            value = row.get(key, "")

            if value is None:
                value = 0

            if key == "distance_miles":
                try:
                    value = round(float(value), 1)
                except Exception:
                    value = 0

            value = str(value).replace("\n", " ").replace("\r", " ")

            if len(value) > width:
                value = value[:width - 1] + "…"

            values.append(f"{value:<{width}}")

        lines.append(" ".join(values))

    lines.append("```")
    lines.append(f"Showing all {len(rows)} results.")

    return "\n".join(lines)


def slack_response(text):
    # Standar ephemeral response for slash command acknowledgements
    return response(
        200,
        json.dumps({
            "response_type": "ephemeral",
            "text": text
        }),
        content_type="application/json"
    )


def response(status_code, body, content_type="text/plain"):
    # Standard API Gateway response format
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": content_type},
        "body": body
    }