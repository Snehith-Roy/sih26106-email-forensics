#!/bin/bash
set -e

# Train ML model if not already present (volume mount may override build artifacts)
if [ ! -f /app/models_store/xgb_classifier.pkl ]; then
    echo "Training ML model..."
    cd /app && PYTHONPATH=. python -m app.nlp.train_baseline
    echo "ML model trained successfully."
else
    echo "ML model already present, skipping training."
fi

# Execute the main command (uvicorn)
exec "$@"
