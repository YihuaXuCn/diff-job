from concurrent.futures import ProcessPoolExecutor
from subprocess import run, TimeoutExpired, CompletedProcess
from multiprocessing import Value
from time import sleep
import os, re
import argparse

 
parser = argparse.ArgumentParser()
parser.add_argument('-d', "--directory", type=str, help="path of a folder", required=True)
parser.add_argument('-t', "--fileType", type=str, help="type of a file", required=True)
# parser.add_argument('-o', "--output", type=str, help="output file name", required=True)
# parser.add_argument('-l', "--logDir", type=str, help="log folder name", required=True)
# parser.add_argument('-f1', "--fileName1", type=str, help="path of a file", required=True)
# parser.add_argument('-f2', "--fileName2", type=str, help="path of a file", required=True)
args = parser.parse_args()

def testFind(folder):
    # folder = args.directory
    cmdStr = 'find ' + folder + ' -type f -name *.txt'
    # cmdStr = 'ls ' + folder
    print(cmdStr)
    cmd = cmdStr.split(' ')
    try:
        process = run(cmd\
                    , timeout = 10 \
                    , capture_output=True\
                    )
    except Exception as e:
        print("timeout")
    else:
        result = process.stdout.decode("utf-8")
        result = result.split('\n')[:-1]
        print(type(result))
        print(result)
    finally:
        print("test find end")

def testSed(file):
    #     pass
    # file = args.fileName
    cmdStr = "sed -i s/[[:blank:]]//g;/^$/d " + file
    # cmdStr = 'ls ' + folder
    print(cmdStr)
    cmd = cmdStr.split(' ')
    print(cmd)
    try:
        process = run(cmd\
                    , timeout = 10 \
                    , capture_output=True\
                    )
    except Exception as e:
        print("timeout")
    else:
        print(process.returncode)
    finally:
        print("test sed end")

def testOutput(file, output):
    # file = args.fileName
    cmdStr = "cat"
    cmd = cmdStr.split(' ')+[file]
    print(cmd)
    try:
        with open(output, 'w') as outfile:
            process = run(cmd\
                        # , timeout = 30 \
                        # , capture_output=True\
                        , stdout = outfile
                        )
    except Exception as e:
        print("Exception")
        raise
    else:
        print(process.returncode)
    finally:
        print("test output end")

def testExtractFns(file):
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

def testDiff(file1, file2):
    cmdStr = "diff -i"
    cmd = cmdStr.split(' ')
    cmd = cmd + [file1, file2]
    output = file1[:-3]+"_vs_"+os.path.basename(file2)[:-3] + ".dif"
    print(output)
    try:
        with open(output, 'w') as outfile:
            process = run(cmd, timeout = 60, stdout = outfile)
    except TimeoutExpired:
        print("timeout")
        return file
    else:
        print("test diff end")

def testWc(file):
    cmd = ['wc',file, '-l']
    try:
        process = run(cmd, timeout=60, capture_output=True)
        result = process.stdout.decode("utf-8")
        return result
    except Exception as e:
        raise e

def runCmdFind(folder, fileType):
    cmdStr = "find "+folder+" -type f -name *."+fileType
    cmd = cmdStr.split(' ')
    process = run(cmd, capture_output=True)
    files = process.stdout.decode('utf-8').split('\n')[:-1]
    return files

if __name__ == '__main__':
    # file1 = args.fileName1
    # file2 = args.fileName2
    folder = args.directory
    fileType = args.fileType

    print(len(runCmdFind(folder, fileType)))