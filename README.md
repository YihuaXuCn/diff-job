# diff-job
extract fn.s from sol file and dele blank and tab symbols, then compare diff lines to get diff scores

datasets are at google driver.

## step 1
to download your zip file

to download this repo.

to extract files from the zip file into a folder

## step 2.
In order to speed up our experiment, I took a way of splitting dataset into smaller slices, and separately run them. you can use the following cmd to get diff scores

Assume you dataset at './dataset/', and your mechine can run 4 independent shell.

shell_1:

python3 preprocess.py -d ./dataset/ -i 0 -s 4 && python3 diffJob.py -d ./dataset/ -ot overtime -ds diffScore_0.json -s 4 -i 0

shell_2:

python3 preprocess.py -d ./dataset/ -i 1 -s 4 && python3 diffJob.py -d ./dataset/ -ot overtime -ds diffScore_1.json -s 4 -i 1

shell_3:

python3 preprocess.py -d ./dataset/ -i 2 -s 4 && python3 diffJob.py -d ./dataset/ -ot overtime -ds diffScore_2.json -s 4 -i 2

shell_4:

python3 preprocess.py -d ./dataset/ -i 3 -s 4 && python3 diffJob.py -d ./dataset/ -ot overtime -ds diffScore_3.json -s 4 -i 3

you can adjust the argument of '-s' depending on your machine

### notice
if it is crashed after 'preprocess done', you won't need to run preprocess again but just to run diffJob.
