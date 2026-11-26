#!/bin/bash

declare -A expected
expected[platform_driver]=unsat
expected[acpi_wmi_driver]=unsat
expected[ns2_led_driver]=unsat
expected[gti_wdt_driver]=unsat
expected[stm32_iwdg_driver]=unsat
expected[hisi_thermal_driver]=sat
expected[ptp_qoriq_driver]=unsat
expected[ptp_dte_driver]=unsat
expected[xvtc_driver]=unsat
expected[xtpg_driver]=sat
expected[xvip_composite_driver]=sat
expected[i8042_driver]=unsat
expected[unimac_mdio_driver]=unsat
expected[apple_nvme_driver]=sat
expected[edma_driver]=sat
expected[acpi_fan_driver]=sat
expected[ged_driver]=unsat

for driver in "${!expected[@]}"; do
  echo Running DrvHorn on $driver..
  result=$(docker run --rm joehattori/drvhorn timeout 500 /drvhorn/build/run/bin/sea kernel --platform-driver=$driver /drvhorn/simple_kernel.bc 2>/dev/null | grep -E '^(sat|unsat)$')
  exit_code=${PIPESTATUS[0]}

  if [[ $exit_code -eq 124 ]]; then
    result="timeout"
  elif [[ -z "$result" ]]; then
    result="unknown"
  fi

  exp=${expected[$driver]}
  if [[ "$result" == "$exp" ]]; then
    status="✓"
  else
    status="✗"
  fi

  echo "$result (expected: $exp) $status"
  echo ""
done

