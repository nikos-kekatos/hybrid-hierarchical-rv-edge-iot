#!/bin/bash
#
# Run Evaluation Experiment
# Orchestrates docker compose, metrics collection, and analysis
#

# Change to script directory to ensure correct paths
cd "$(dirname "$0")/.."

DURATION=${1:-120}  # Default: 2 minutes
LOG_DIR="./shared_data"
RESULTS_DIR="./results"

# Trap EXIT to ensure graceful shutdown and analysis even if interrupted
cleanup() {
    echo ""
    echo "[5/6] Stopping docker compose..."
    docker compose down

    # Collect metrics
    echo "[6/6] Analyzing results..."
    if [ -f "evaluation/collect_metrics.py" ]; then
        python3 evaluation/collect_metrics.py \
            --log-dir "${LOG_DIR}" \
            --output "${RESULTS_DIR}/metrics.json"

        python3 evaluation/analyze_results.py \
            --metrics "${RESULTS_DIR}/metrics.json" \
            --output "${RESULTS_DIR}/analysis.json"
    else
        echo "Error: Python analysis scripts not found in evaluation/ directory."
    fi

    echo ""
    echo "=========================================="
    echo "Experiment Complete!"
    echo "=========================================="
    echo "Results saved to: ${RESULTS_DIR}/"
    echo "  - metrics.json   (raw metrics)"
    echo "  - analysis.json  (detection rates)"
    echo ""
    echo "View logs:"
    echo "  - ${LOG_DIR}/events.log    (raw events)"
    echo "  - ${LOG_DIR}/alerts.log    (Layer 2 alerts)"
    echo "  - ${LOG_DIR}/incidents.log (Layer 3 incidents)"
    echo ""
}

trap cleanup EXIT INT TERM

echo "=========================================="
echo "Hierarchical RV Evaluation Experiment"
echo "=========================================="
echo "Duration: ${DURATION}s"
echo ""

# Clean previous logs
echo "[1/6] Cleaning previous logs..."
rm -rf "${LOG_DIR:?}"/* 2>/dev/null || true
mkdir -p "${LOG_DIR}"
mkdir -p "${RESULTS_DIR}"

# Initialize empty log files so they always exist
touch "${LOG_DIR}/events.log"
touch "${LOG_DIR}/alerts.log"
touch "${LOG_DIR}/incidents.log"

# Start system
echo "[2/6] Starting docker compose..."
docker compose up --build -d

# Wait for system to initialize
echo "[3/6] Waiting for system initialization (10s)..."
sleep 10

# Run experiment
echo "[4/6] Running experiment for ${DURATION}s..."
echo "  System is collecting data..."
echo "  Press Ctrl+C to stop early and trigger analysis"

# Sleep in the background and wait so it handles Ctrl+C gracefully
sleep "${DURATION}" &
wait $!