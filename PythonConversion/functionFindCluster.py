def findCluster(spPath, k, clusters, clusterPaths):
    if len(clusters) == 0:
        clusters.append([k]);
        clusterPaths.append(spPath);
    else:
        flag = False;
        for l in range(len(clusters)):
            if len(spPath) == len(clusterPaths[l]):
                flag = True;
                for m in range(len(spPath)):
                    if spPath[m] != clusterPaths[l][m]:
                        flag = False;
                        break;
                if flag:
                    clusters[l].append(k);
                    break;
        if not flag:
            clusters.append([k]);
            clusterPaths.append(spPath);
    return clusters, clusterPaths