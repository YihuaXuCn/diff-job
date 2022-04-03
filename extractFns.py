import os, re
import argparse
from subprocess import run, TimeoutExpired, CompletedProcess
from concurrent.futures import ProcessPoolExecutor

def extractFns(file):
    cntFnLeft = 0
    cntFnRigt = 0
    cntContL = 0
    cntContR = 0
    funLines = []
    saveFn = False
    foundFn = False
    contractStart = False
    contractEnd = True
    fnSaveFolder = 'datasetFns/'+os.path.dirname(file).split('/')[-1]
    if not os.path.exists(fnSaveFolder):
        run(['mkdir', '-p', fnSaveFolder])


    with open(file, 'r') as f:
        lines = f.readlines()

    for i, l in enumerate(lines, start=1):
        if contractEnd and re.match("^\\s*([Cc]ontract|[Ll]ibrary)(\\s*\\S*)*", l):
            contractStart = True
            contractEnd = False
        if not foundFn and not re.match("^\\s*[Ff]unction(\\s*\\S)*", l):
            cntContL += l.count('{')
            cntContR += l.count('}')
            # if i < 100:
            #     print("i: {}\t cl = {} \t cr = {}".format(i, cntContL, cntContR))
        if contractStart and cntContL == cntContR and cntContR != 0 and cntContL !=0:
            contractEnd = True
            contractStart = False
            cntContR = cntContL = 0

        if contractStart and re.match("^\\s*[Ff]unction(\\s*\\S)*", l):
            foundFn = True
            # fnName = re.split('[\\s\\W]', l.strip())[1]
            lineNmb = '{0:04}'.format(i)
        if contractStart and foundFn:
            funLines.append(l)
            cntFnLeft += l.count('{')
            cntFnRigt += l.count('}')
            if cntFnRigt == cntFnLeft: # and cntFnLeft !=0 and cntFnLeft != 0:
                saveFn = True
                saveFile = os.path.basename(file)[:-4]+"."+lineNmb+".fn"
                saveFile = os.path.join(fnSaveFolder, saveFile)
        if saveFn:
            with open(saveFile, 'w') as sf:
                sf.writelines(funLines)
            foundFn = False
            saveFn = False
            cntFnLeft = 0
            cntFnRigt = 0
            funLines = []

parser = argparse.ArgumentParser()
parser.add_argument('-d', "--directory", type=str, help="path of a folder", required=True)
args = parser.parse_args()

folder = args.directory
cmdStr = "find " + folder + " -type f -name *.sol"
cmd = cmdStr.split(' ')
process = run(cmd, capture_output=True)
files = process.stdout.decode('utf-8').split('\n')[:-1]

with ProcessPoolExecutor(max_workers=8) as executor:
    pool = executor.map(extractFns, files)
