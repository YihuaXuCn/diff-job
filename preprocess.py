from subprocess import run
import concurrent.futures
import os
import argparse
from subprocess import run, TimeoutExpired
from concurrent.futures import ProcessPoolExecutor

parser = argparse.ArgumentParser()
parser.add_argument('-d', "--directory", type=str, help="path of a folder", required=True)
parser.add_argument('-o', "--output", type=str, help="output file name", required=True)
# parser.add_argument('-l', "--logDir", type=str, help="log folder name", required=True)
args = parser.parse_args()

def preprocessOneFile(file):
    cmdStr = "sed -i s/[[:blank:]]//g;/^$/d"
    cmd = cmdStr.split(' ') + [file]
    try:
        process = run(cmd, capture_output=True, timeout = 60)
    except TimeoutExpired:
        state=1
        return state, file
    else:
        # print("sed cmd returncode :{}".format(process.returncode))
        if process.returncode != 0:
            state=2
            return process.stderr.decode('utf-8'), file
        else:
            # logfd.close()
            state=3
            return state, None


folder = args.directory
cmdStr = "find " + folder + " -type f -name *.fn"
cmd = cmdStr.split(' ')
process = run(cmd, capture_output=True)
# print("find cmd returncode :{}".format(process.returncode))
files = process.stdout.decode('utf-8').split('\n')[:-1]

with ProcessPoolExecutor(max_workers=8) as executor:
    failed = []
    # folder = args.directory
    # files = os.listdir(folder)
    # logdir = os.path.join(folder, args.logDir)
    # if not os.path.exists(logdir):
    #       run(['mkdir', '-p', logdir])
    # files = [os.path.join(folder,f) for f in files]
    # end = round(len(files)/10)
    # files = files[:end]
    # print(files[0])
    # preprocessOneFile(files[0])
    pool = executor.map(preprocessOneFile, files)
    for res in pool:
        if res[1] == None:
            continue
        failed.append('{}\t{}\n'.format(res[0],res[1]))
    # failed = [f for f in failed]

    fd = open(args.output,'w+')
    # fd.write(str(end))
    # for f in failed:
    #     fd.writelines(failed)
    fd.writelines(failed)
    fd.close()
