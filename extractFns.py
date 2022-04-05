import os, re
import argparse
from subprocess import run, TimeoutExpired, CompletedProcess
from concurrent.futures import ProcessPoolExecutor

def extractFns(file):
    cntContL = 0
    cntContR = 0
    funLines = []
    foundNewFn = False
    foundFn = False
    contractStart = False
    contractEnd = True
    multiLnCommtsStart = False
    fnSaveFolder = 'datasetFns/'+os.path.dirname(file).split('/')[-1]
    if not os.path.exists(fnSaveFolder):
        run(['mkdir', '-p', fnSaveFolder])

    with open(file, 'r') as f:
        lines = f.readlines()

    # remove // comments
    solLns = [ ((re.split('//', l, maxsplit=1)[0] + '\n') if ('//' in l) else l)  for l in lines]

    # remove /* and */ comments
    for i, l in enumerate(solLns, start=1):
        if multiLnCommtsStart:
            if '*/' in l:
                solLns[i-1] = re.split('\\*/', l, maxsplit=1)[1]
                multiLnCommtsStart = False
            else:
                solLns[i-1] = '\n'
                continue
        else:
            if '/*' in l :
                multiLnCommtsStart = True
                # perheps */ exits in the same line
                if '*/' in l:
                    multiLnCommtsStart = False
                    solLns[i-1] = re.split('/\\*', l, maxsplit=1)[0] + re.split('\\*/', l, maxsplit=1)[1]
                else:
                    solLns[i-1] = re.split('/\\*', l, maxsplit=1)[0] + '\n'

    for i, l in enumerate(solLns, start=1):
        if contractEnd and re.match("^\\s*([Cc]ontract|[Ll]ibrary)(\\s*\\S*)*", l):
            contractStart = True
            contractEnd = False

        cntContL += l.count('{')
        cntContR += l.count('}')
            # if i < 100:
            #     print("i: {}\t cl = {} \t cr = {}".format(i, cntContL, cntContR))
        if contractStart and cntContL == cntContR and cntContR != 0 and cntContL !=0:
            contractEnd = True
            contractStart = False
            cntContR = cntContL = 0

        if contractStart:
            if re.match("^\\s*[Ff]unction(\\s*\\S)*", l):
                if foundFn:
                    foundNewFn = True
                    temp = '{0:04}'.format(i)
                else:
                    foundFn = True
                    lineNmb = '{0:04}'.format(i)

            if foundFn and not foundNewFn:
                funLines.append(l)

            if foundNewFn and foundFn:
                saveFileName = os.path.basename(file)[:-len('.sol')]+"."+lineNmb+".fn"
                saveFile = os.path.join(fnSaveFolder, saveFileName)
                with open(saveFile, 'w') as sf:
                    sf.writelines(funLines)
                foundNewFn = False
                funLines = []
                lineNmb = temp
                funLines.append(l)
        else:
            if foundFn:
                saveFileName = os.path.basename(file)[:-len('.sol')]+"."+lineNmb+".fn"
                saveFile = os.path.join(fnSaveFolder, saveFileName)
                with open(saveFile, 'w') as sf:
                    sf.writelines(funLines)
                foundNewFn = False
                foundFn = False
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
