using CSV
N25 = [108,115,121,125,131,164,57,6,86,96]
N50 = [110,118,142,16,35,41,43,56,79,84]
N100 = [12,122,15,22,38,65,68,73,78,8]


testSet = "N100"

for i in N100
    fileName = "./"*testSet*"/"*testSet*"_"*string(i)*".jl"
    include(fileName)

    println(edge)
    # timesFiles
    f = open(testSet*"_"*string(i)*".csv", "w")
    # write(f,"#################################\n")
    # write(f,"# Content of file\n")
    # write(f,"#################################\n")
    # write(f,"#\n")
    # write(f,"# Number of arcs\n")
    # write(f,"# Origin node\n")
    # write(f,"# Destination node\n")
    # write(f,"#\n")
    # write(f,"# List of arc information (delimiter = \\t): i  j  cL_{ij}  cU_{ij}  d_{ij} as (Tail)  (Head)  (Cost Lower Bound)  (Cost Upper Bound)  (Interdiction Cost)\n")
    # write(f,"#\n")
    # write(f,"#################################\n")
    # write(f,"\n")
    write(f, string(Len),"\n")
    # println(cL_orig[1])
    write(f,string(origin),"\n")
    write(f,string(destination),"\n")
    write(f,"\n")
    for e =1:Len
        write(f, string(edge[e, 1]), "\t", string(edge[e, 2]),"\t", string(cL_orig[e]),"\t", string(cU_orig[e]),"\t", string(d[e]),"\n")
    end

    close(f)
end
# println(timesFile, dataSet, "; Ins ", Ins, "; Time ", total_time, "; MP_obj ", MP_obj, "; x_now ", findall(x_now.==1),"; Cells ", nrow(df_cell), "; Iter ", iter)#, "; W ", LB_w, "; Cuts ", numConv)
# close(timesFile)