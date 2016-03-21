# -- coding: utf-8 --
import os,string,re,sys,math,getopt

training_folder = ''
test_folder = ''

def usage():
    print('usage: python my_authorship_recognition_system.py --training-set /path/to/training/set --test-set /path/to/test/set')

try:
    opts, args = getopt.getopt(sys.argv[1:], "t:s:h", ['training-set=', 'test-set=', 'help'])
    if len(opts) == 0:
	usage()
	sys.exit(2)
except getopt.GetoptError as e:
    print(e)
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt in ('--help'):
        usage()
        sys.exit(2)
    elif opt in ('--training-set'):
        training_folder = arg
    elif opt in ('--test-set'):
	test_folder = arg
    else:
        usage()
        sys.exit(2)

def remove_punctuation(s):
    table = string.maketrans("","")
    return s.translate(table, string.punctuation)

def homogenize(s):
    edited = s
    #replace all turkish characters to their english represantation
    edited = edited.replace('ç','c')
    edited = edited.replace('Ç','c')
    edited = edited.replace('ğ','g')
    edited = edited.replace('Ğ','g')
    edited = edited.replace('ı','i')
    edited = edited.replace('İ','i')
    edited = edited.replace('ö','o')
    edited = edited.replace('Ö','o')
    edited = edited.replace('ş','s')
    edited = edited.replace('Ş','s')
    edited = edited.replace('ü','u')
    edited = edited.replace('Ü','u')

    edited = edited.lower()

    edited = [re.sub(r'([^\w]|_)+', '', word) for word in edited.split() if not re.sub(r'([^\w]|_)+', '', word).isdigit()]

    #return homogenized word
    return edited

def count_words(words):
    wc = {}
    for word in words:
        wc[word] = wc.get(word, 0.0) + 1.0
    return wc

#training
print('training')
priors = {}
vocab = {}
word_counts = {}
authorsList = os.listdir(training_folder)
for author in authorsList:
    authorPath = os.path.join(training_folder,author)
    fileNames = [path for path in os.listdir(authorPath) if not path.startswith('.')] # just to prevent .DS_Store file
    for fileName in fileNames:
        filePath = os.path.join(authorPath,fileName)
        text = ''
        with open(filePath,'r') as f:
            text = f.read().decode('iso-8859-9').encode('utf8')
        if text != '':
            words = homogenize(text)
            wc = count_words(words)
            priors[author] = priors.get(author,0.0) + 1.0
            for word,count in wc.items():
                vocab[word] = vocab.get(word,0.0) + float(count)
                if word_counts.has_key(author):
                    word_counts[author][word] = word_counts[author].get(word,0.0) + float(count)
                else:
                    word_counts[author] = {word:float(count)}

#set prior probabilities
sumPriors = sum(priors.values())
for key in priors.keys():
    priors[key] = priors[key]/sumPriors

p_word = {}
sumVocab = sum(vocab.values())
for key in vocab.keys():
    p_word[key] = vocab[key]/sumVocab
print('testing')
#test
predictions = {}
predictions2 = {}
authorsList = os.listdir(test_folder)
results  = {}
middleResult = {}
results2  = {}
middleResult2 = {}
for author in authorsList[:3]:
    results[author] = [0,0]
    middleResult[author] = 0
    results2[author] = [0,0]
    middleResult2[author] = 0
    authorPath = os.path.join(test_folder,author)
    fileNames = [path for path in os.listdir(authorPath) if not path.startswith('.')] # just to prevent .DS_Store file
    for fileName in fileNames:
        filePath = os.path.join(authorPath,fileName)
        text = ''
        with open(filePath,'r') as f:
            text = f.read().decode('iso-8859-9').encode('utf8')
        if text != '':
            words = homogenize(text)
            wc = count_words(words)
            log_prob_key = 0.0
            probs = {}
            probs2 = {}
            for key in priors.keys():
                prior_key = (priors[key] / sum(priors.values()))
                log_prob_key = 0.0
                totalCount = 0
                for w, cnt in list(wc.items()):
                    if w not in vocab or len(w) <= 3:
                        continue
                    #p_word = vocab[w] / sum(vocab.values())
                    p_w_given = word_counts[key].get(w, 0.0) / sum(word_counts[key].values())
                    if p_w_given > 0:
                        log_prob_key += cnt * math.log(p_w_given / p_word[w])
                        totalCount += cnt
                probs[key] = log_prob_key + math.log(prior_key)# + math.log(totalCount)
                probs2[key] = log_prob_key + math.log(prior_key) + math.log(totalCount)
            tmp = max(probs, key=probs.get)
            tmp2 = max(probs2, key=probs2.get)
            predictions[filePath] = [tmp,probs[tmp],author]
            predictions2[filePath] = [tmp,probs2[tmp2],author]
print('writing')
with open('predictionsBoW.txt', 'w') as f:
    for key in predictions.keys():
        tmp = predictions[key]
        prev = results[tmp[2]]
        if tmp[0] == tmp[2]:
            prev[0] += 1
        prev[1] += 1
        results[tmp[2]] = prev
        middleResult[tmp[0]] += 1
        f.writelines('FilePath: %s Prediction: %s Actual: %s\n' % (key,tmp[0],tmp[2]))

with open('predictionsBoW+WC.txt', 'w') as f:
    for key in predictions2.keys():
        tmp = predictions2[key]
        prev = results2[tmp[2]]
        if tmp[0] == tmp[2]:
            prev[0] += 1
        prev[1] += 1
        results2[tmp[2]] = prev
        middleResult2[tmp[0]] += 1
        f.writelines('FilePath: %s Prediction: %s Actual: %s\n' % (key,tmp[0],tmp[2]))

print('BoW')
#calculate Recall
recall = 0.0
tp = 0
tpfp = 0
tpfn = 0
for key in results.keys():
    tmp = results[key]
    tp += tmp[0]
    tpfp += tmp[1]
recall = float(tp)/tpfp
print('Recall: ',recall)
#calculate Precision
precision = 0.0
for key in middleResult.keys():
    tpfn += middleResult[key]
precision = float(tp)/tpfn
print('Precision: ',precision)
#calculate f score
f_score = (2 * recall * precision) / (recall+precision)
print('Fscore: ',f_score)

print('BoW+WC')
#calculate Recall
recall = 0.0
tp = 0
tpfp = 0
tpfn = 0
for key in results2.keys():
    tmp = results2[key]
    tp += tmp[0]
    tpfp += tmp[1]
recall = float(tp)/tpfp
print('Recall: ',recall)
#calculate Precision
precision = 0.0
for key in middleResult2.keys():
    tpfn += middleResult2[key]
precision = float(tp)/tpfn
print('Precision: ',precision)
#calculate f score
f_score = (2 * recall * precision) / (recall+precision)
print('Fscore: ',f_score)