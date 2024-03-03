import csv 
import numpy as np



# print(edge)
# arc = np.array([[1,2]])
# edge = np.concatenate((edge, arc), axis=0)
# print(edge)
# edge = np.empty([[]])
def processInputFile(testSet, i):
    print("Processing network instance", testSet+"_"+str(i))
    # fileName = "/Users/dinguyen/Desktop/Local Documents/GitHub/Paper5/TestInstances/CSV_TestInstances/"+testSet+"/"+testSet+"_"+str(i)+".csv"
    fileName = "/Users/dinguyen/Desktop/Local Documents/GitHub/Paper5/NewCSVFeb24/"+testSet+"_"+str(i)+".csv"
    # Desktop/Local Documents/GitHub/Paper5/TestInstances/CSV_TestInstances/N25/N25_108.csv
    # N25/N25_108.csv
    with open(fileName, newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        count = 0
        edge = np.empty((0,2), int)
        d = np.empty(shape=(0,))
        cL_orig = np.empty(shape=(0,))
        cU_orig = np.empty(shape=(0,))
        # print("d ", d)
        for row in spamreader:
            # print(', '.join(row))
            count +=1 
            # print(count," ", len(row), " ", row)
            if count == 1:
                Len = int(row[0])
            if count == 2:
                origin = int(row[0])
            if count == 3:
                destination = int(row[0])
            if count >= 5: 
                arc = np.array([[int(row[0]), int(row[1])]])
                # print("Shape arc: ", np.shape(arc))
                # print("arc ", arc)
                edge = np.concatenate((edge, arc), axis=0)
                # print(row[2])
                d = np.append(d, float(row[4]))
                cL_orig = np.append(cL_orig, float(row[2]))
                cU_orig = np.append(cU_orig, float(row[3]))
                # print(d)
    return Len, origin, destination, edge,d, cL_orig, cU_orig
    
