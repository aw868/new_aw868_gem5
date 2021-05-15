#!/bin/bash
echo -n "router_dynamic_power: "

grep -Pzo "system.ruby.network.routers.*Dynamic power:.*\n" energy.out | grep -Pzo "Dynamic power: ', [0-9]+[.][0-9]+e[-][0-9]+[)]" | tr ")" "\n" | tr -d '\0' | grep -Po "[0-9]+[.][0-9]+e[-][0-9]+" | awk '{ sum += $1 } END { print sum }'

echo -n "router_leakage_power: "

grep -Pzo "system.ruby.network.routers.*Leakage power:.*\n" energy.out | grep -Pzo "Leakage power: ', [0-9]+[.][0-9]+[)]" | tr ")" "\n" | tr -d '\0' | grep -Po "[0-9]+[.][0-9]+" | awk '{ sum += $1 } END { print sum }'

echo -n "link_dynamic_power: "

grep -Pzo "system.ruby.network.*links.*Dynamic power:.*\n" energy.out | grep -Pzo "Dynamic power: ', [0-9]+[.][0-9]+e[-][0-9]+[)]" | tr ")" "\n" | tr -d '\0' | grep -Po "[0-9]+[.][0-9]+e[-][0-9]+" | awk '{ sum += $1 } END { print sum }'

echo -n "link_leakage_power: "

grep -Pzo "system.ruby.network.*links.*Leakage power:.*\n" energy.out | grep -Pzo "Leakage power: ', [0-9]+[.][0-9]+e[-][0-9]+[)]" | tr ")" "\n" | tr -d '\0' | grep -Po "[0-9]+[.][0-9]+e[-][0-9]+" | awk '{ sum += $1 } END { print sum }'