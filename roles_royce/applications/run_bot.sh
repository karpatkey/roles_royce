#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

echo "Running $BOT_NAME"

if [[ "$BOT_NAME" == "bridge_keeper" ]]; then
  python3 -u "$SCRIPT_DIR/bridge_keeper/bridge_keeper.py"
elif [[ "$BOT_NAME" == "EURe_rebalancing" ]]; then
  python3 -u "$SCRIPT_DIR/EURe_rebalancing_bot/EURe_bot.py"
elif [[ "$BOT_NAME" == "spark_anti_liquidation" ]]; then
  python3 -u "$SCRIPT_DIR/spark_anti_liquidation_bot/spark_anti_liquidation.py"
elif [[ "$BOT_NAME" == "uniswap_v3_keeper" ]]; then
  python3 -u "$SCRIPT_DIR/uniswap_v3_keeper/uniswap_v3_keeper.py"
else
  echo Bad bot name: "$BOT_NAME"
  exit 1
fi
