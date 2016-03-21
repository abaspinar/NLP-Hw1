#Naive Bayes Author Classifier

##Data set generation
python training_and_test_set_builder.py --data-set /path/to/dataset  --training-set /path/to/training/set --test-set /path/to/test/set

##Running The Code
python my_authorship_recognition_system.py --training-set /path/to/training/set --test-set /path/to/test/set

##Implementation Details
The program is implemented with Python 2.7 and it requires no external libraries.

##Outputs
The program creates predictionsBoW.txt and predictionsBoW+WC.txt files.
It also prints the recall, precision and fscore to the console.
