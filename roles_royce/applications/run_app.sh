#!/bin/sh

SCRIPT_DIR=$(dirname "$0")

echo "Running $APP"

if [[ "$APP" == "bridge_keeper" ]]; then
  python3 -u "$SCRIPT_DIR/bridge_keeper/bridge_keeper.py"
elif [[ "$APP" == "EURe_rebalancing" ]]; then
  python3 -u "$SCRIPT_DIR/EURe_rebalancing_bot/EURe_bot.py"
elif [[ "$APP" == "GBPe_rebalancing" ]]; then
  python3 -u "$SCRIPT_DIR/GBPe_rebalancing_bot/GBPe_bot.py"
elif [[ "$APP" == "Execution_http_server" ]]; then
  python3 -u "$SCRIPT_DIR/execution_app/http_server.py"
elif [[ "$APP" == "spark_anti_liquidation" ]]; then
  python3 -u "$SCRIPT_DIR/spark_anti_liquidation_bot/spark_anti_liquidation.py"
else
  echo Bad bot name: "$APP"
  exit 1
fi
