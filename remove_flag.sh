#!/bin/bash
rm ./flaglink
echo '1' > flaglink
git add .
git commit -m 'remove flaglink'
git push
