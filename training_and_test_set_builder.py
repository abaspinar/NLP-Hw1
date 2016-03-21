import sys, os, shutil, random, getopt

def usage():
    print('usage: python training_and_test_set_builder.py --data-set /path/to/dataset  --training-set /path/to/training/set --test-set /path/to/test/set')

try:
    opts, args = getopt.getopt(sys.argv[1:], "d:t:s:h", ['data-set=', 'training-set=', 'test-set=', 'help'])
    if len(opts) == 0:
	usage()
	sys.exit(2)
except getopt.GetoptError as e:
    print(e)
    usage()
    sys.exit(2)

data_folder = ''
training_folder = ''
test_folder = ''
for opt, arg in opts:
    if opt in ('--help'):
        usage()
        sys.exit(2)
    elif opt in ('--data-set'):
        data_folder = arg
    elif opt in ('--training-set'):
        training_folder = arg
    elif opt in ('--test-set'):
	test_folder = arg
    else:
        usage()
        sys.exit(2)

def createTrainandTestFolder():
    #clean
    if os.path.exists(training_folder):
        shutil.rmtree(training_folder)
    if os.path.exists(test_folder):
        shutil.rmtree(test_folder)
    #create folders
    os.makedirs(training_folder)
    os.makedirs(test_folder)
    return training_folder,test_folder

def randomSample(fileNames,randPercent):
    count = len(fileNames)
    trainCount = int((count * randPercent)/100)
    sample = random.sample(range(count),trainCount)
    trainingFiles = []
    testFiles = []
    sampleList = [False]*count
    for i in sample:
        sampleList[i] = True
    for k in range(len(sampleList)):
        if sampleList[k]:
            trainingFiles.append(fileNames[k])
        else:
            testFiles.append(fileNames[k])
    return trainingFiles,testFiles

def analyzeFolder(dataFolder,randPercent):
    rawTexts = '%s' % (dataFolder)
    authorsList = os.listdir(rawTexts)
    training = {}
    test = {}
    if len(authorsList) != 0:
        trainingPath,testPath = createTrainandTestFolder()
        for author in authorsList:
            location = '%s/%s' % (rawTexts,author)
            if os.path.isdir(location):
                fileNames = [name for name in os.listdir(location) if not name.startswith('.')]
                trainingFiles,testFiles = randomSample(fileNames,randPercent)
                for trainingFile in trainingFiles:
                    src = '%s/%s' % (location,trainingFile)
                    dst = '%s/%s' % (trainingPath,author)
                    if not os.path.exists(dst):
                        os.mkdir(dst)
                    dst = '%s/%s' % (dst,trainingFile)
                    training[author] = training.get(author,0) + 1
                    shutil.copyfile(src,dst)
                for testFile in testFiles:
                    src = '%s/%s' % (location,testFile)
                    dst = '%s/%s' % (testPath,author)
                    if not os.path.exists(dst):
                        os.mkdir(dst)
                    dst = '%s/%s' % (dst,testFile)
                    shutil.copyfile(src,dst)
                    test[author] = test.get(author,0) + 1
    with open('set_info.txt','w') as f:
        for key in training:
            if training.has_key(key) and test.has_key(key):
                f.writelines('Author: %s Training_Documents_length: %d Test_Documents_length: %d\n' % (key,training[key],test[key]))
randPercent = 60
analyzeFolder(data_folder,randPercent)
