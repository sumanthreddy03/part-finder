"""
Flask entry point for the Part Finder app.

Provides:
Browser-based search UI
JSON API endpoint for part search
"""

import pandas as pd
from flask import Flask, request, jsonify

from services.part_search_service import search_part_data

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return """
    <h2>Part Finder Search</h2>

    <form action="/search-ui" method="post">
        <label>APN / Part Number:</label><br>
        <input type="text" name="apn"><br><br>

        <label>Input Site Code:</label><br>
        <input type="text" name="input_site_code"><br><br>

        <button type="submit">Search</button>
    </form>

    <br>
    """


@app.route("/search-ui", methods=["POST"])
def search_ui():
    # Read search inputs from the browser form
    apn = request.form.get("apn")
    input_site_code = request.form.get("input_site_code")

    # Call backend search service
    result, status = search_part_data(apn, input_site_code)

    if status != 200:
        return jsonify(result), status

    # Convert returned records into a readable HTML table
    rows = result.get("results", [])

    if not rows:
        return "<h3>No matching parts found.</h3><br><a href='/'>Back</a>"

    df = pd.DataFrame(rows)

    # Hide coordinate fields from the user-facing result table
    df = df.drop(
            columns=["latitude", "longitude"],
            errors="ignore"
    )
    
    df = df.fillna(0)

    table_html = df.to_html(index=False)

    return f"""
    <h2>Search Results</h2>
    <p><b>APN:</b> {apn} | <b>Input Site:</b> {input_site_code}</p>
    <a href="/">Back to Search</a>
    <br><br>
    {table_html}
    """


@app.route("/search-part", methods=["POST"])
def search_part():
    # JSON endpoint used by API clients or other services
    data = request.get_json() or {}

    apn = data.get("apn")
    input_site_code = data.get("input_site_code")

    if not apn or not input_site_code:
        return jsonify({
            "error": "apn and input_site_code are required"
        }), 400

    result, status = search_part_data(apn, input_site_code)

    return jsonify(result), status


if __name__ == "__main__":
    # Run Flask app for local/container execution
    app.run(host="0.0.0.0", port=80)