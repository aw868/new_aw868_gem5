#!/bin/bash

grep -nir "router_dynamic_power" | sort >> router_dynamic_power.txt

grep -nir "router_leakage_power" | sort >> router_leakage_power.txt

grep -nir "link_dynamic_power" | sort >> link_dynamic_power.txt

grep -nir "link_leakage_power" | sort >> link_leakage_power.txt