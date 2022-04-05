import argparse, os, json
from subprocess import run, TimeoutExpired
from concurrent.futures import ProcessPoolExecutor

parser = argparse.ArgumentParser()
parser.add_argument('-d', "--directory", type=str, help="path of a folder", required=True)
parser.add_argument('-o', "--output", type=str, help="output overtime file name", required=True)
args = parser.parse_args()

def runCmdFind(folder, fileType):
    cmdStr = "find "+folder+" -type f -name *."+fileType
    cmd = cmdStr.split(' ')
    process = run(cmd, capture_output=True)
    files = process.stdout.decode('utf-8').split('\n')[:-1]
    return files

def diffOneFile(filePair):
    fnfile1, fnfile2 = filePair
    cmdStr = "diff -i"
    cmd = cmdStr.split(' ')
    cmd = cmd + [fnfile1, fnfile2]

    difFolder = 'diffs'
    file1Name = os.path.basename(fnfile1)[:-len('.fn')]
    file1NameFolder = os.path.join(difFolder, file1Name)
    if not os.path.exists(file1NameFolder):
        run(['mkdir','-p',file1NameFolder])
    difFileName = os.path.basename(fnfile1)[:-len('.fn')]+"_vs_" \
                +os.path.basename(fnfile2)[:-len('.fn')] + ".dif"
    difFile = os.path.join(file1NameFolder, difFileName)
    if os.path.exists(difFile):
        return None
    if len(difFileName) > 255:
        with open('nameErr.txt', 'a') as f:
            f.write(difFileName[:255])
            f.write('-->')
            f.write(difFileName)
            f.write('\n')
        difFileName = difFileName[:255]
    # print(difFileName)
    try:
        with open(difFile, 'w') as outfile:
            process = run(cmd, timeout = 60, stdout = outfile)
    except TimeoutExpired:
        # print("timeout")
        return file
    else:
        return None
        # print("test diff end")

def getFileLns(file):
    process = run(['wc',file,'-l'], timeout=60, capture_output=True)
    result = process.stdout.decode("utf-8").split(' ')[0]
    return file, result


evaluatedFns = runCmdFind('34DappsFns', 'fn')
folder = args.directory
datasetFns = runCmdFind(folder, 'fn')

filePairList = []
if os.path.exists('nameErr.txt'):
    run(['rm', 'nameErr.txt'])
for file1 in evaluatedFns:
    for file2 in datasetFns:
        filePairList.append((file1,file2))

with ProcessPoolExecutor(max_workers=8) as executor:
    failed = []
    pool = executor.map(diffOneFile, filePairList)

    for res in pool:
        if res == None:
            continue
        failed.append('{}\t{}\n'.format('timeover',res))
    # failed = [f for f in failed]

    fd = open(args.output,'w+')
    fd.writelines(failed)
    fd.close()

# calculate diff scores
evalFnLnCntDict = {}
for fn in evaluatedFns:
    _, lnCnt = getFileLns(fn)
    key = os.path.basename(fn)[:-len('.fn')]
    evalFnLnCntDict[key] = lnCnt

diffScoresDict = {}
allDifFiles = runCmdFind('diffs', 'dif')
print("diff files :{}".format(len(allDifFiles)))

if os.path.exists('diffScores.json'):
    run(['rm', '-f', 'diffScores.json'])

with ProcessPoolExecutor(max_workers=8) as executor:
    pool = executor.map(getFileLns, allDifFiles)
    for result in pool:
        difFileName, lnCnt = result
        evalFn = os.path.basename(difFileName)[:-len('.dif')].split('_vs_')[0]
        evalFnLnCnt = evalFnLnCntDict[evalFn]
        diffScoresDict[difFileName] = int(lnCnt)/int(evalFnLnCnt)
    sortedDiffScores = sorted(diffScoresDict.items(), key=lambda x: x[1])
    sortedDiffScoresDict = { e[0]: e[1] for e in sortedDiffScores}
    with open('diffScores.json', 'w+') as outfile:
        json.dump(sortedDiffScoresDict, outfile, indent=4)