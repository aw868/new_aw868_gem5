#!/bin/bash

echo -n "total_transmission_count: "
grep -E "transmission_count:" condortest.out | grep -Eo "[0-9]+" | sort -rn | head -n 1