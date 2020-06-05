#!/bin/bash

/usr/bin/find /data/CEH_NFLICS/archive/. -type f -mmin +20160 -exec /bin/rm -rf {} \; 
