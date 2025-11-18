from flask import Flask, request, jsonify, render_template
from src.services.analysis import analyze, rewrite
import time

# --- Observability Metrics ---
metrics = {
    "start_time": time.time(),
    "analyze_requests": 0,
    "rewrite_requests": 0
}

app = Flask(__name__, template_folder="src/web")

@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def get_metrics():
    uptime = time.time() - metrics["start_time"]
    return {
        "uptime_seconds": round(uptime, 2),
        "analyze_requests": metrics["analyze_requests"],
        "rewrite_requests": metrics["rewrite_requests"],
    }

@app.post("/analyze")
def route_analyze():
    metrics["analyze_requests"] += 1
    app.logger.info("Analyze requested")
    
    data = request.get_json(silent=True) or request.form
    text = (data.get("text") or "").strip()
    res = analyze(text)
    return jsonify({
        "lines": res.lines,
        "rhyme_scheme": res.rhyme_scheme,
        "tone": res.tone,
    })


@app.post("/rewrite")
def route_rewrite():
    metrics["rewrite_requests"] += 1
    app.logger.info("Rewrite requested")
    
    data = request.get_json(silent=True) or request.form
    text = (data.get("text") or "").strip()
    payload = rewrite(text)
    if request.content_type and "application/json" in (request.content_type or ""):
        return jsonify(payload)
    else:
        lines_html = "<br>".join(payload["rewrite"])
        html = (
            "<h3>Analysis</h3>"
            f"<pre>{payload['analysis']}</pre>"
            f"<h3>Rewrite ({payload['chosen_scheme']})</h3>"
            f"<p style='font-family: serif; line-height: 1.6'>{lines_html}</p>"
            "<a href='/'>Back</a>"
        )
        return html


if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=8000, debug=False)
