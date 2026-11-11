#!/bin/sh
# zaofang CLI splash: types the name, then blinks a block cursor three times and leaves it on.
# Truecolor escapes; terminals without truecolor show the nearest colour.
ink='\033[38;2;240;231;213m'; amber='\033[38;2;240;164;69m'; reset='\033[0m'
printf '\033[?25l'
for ch in z a o f a n g; do printf "${ink}%s${reset}" "$ch"; sleep 0.09; done
printf ' '
for i in 1 2 3; do printf "${amber}\342\226\210${reset}"; sleep 0.53; printf '\b \b'; sleep 0.53; done
printf "${amber}\342\226\210${reset}\n\033[?25h"
