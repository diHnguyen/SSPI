using CSV
include("./N4_1.jl")

println(edge)
# timesFiles
f = open("test.csv", "w")
write(f,"#################################\n")
write(f,"# Content of file\n")
write(f,"#################################\n")
write(f,"#\n")
write(f,"# Number of arcs\n")
write(f,"# Origin node\n")
write(f,"# Destination node\n")
write(f,"#\n")
write(f,"# List of arc information (delimiter = \\t): i  j  cL_{ij}  cU_{ij}  d_{ij} as (Tail)  (Head)  (Cost Lower Bound)  (Cost Upper Bound)  (Interdiction Cost)\n")
write(f,"#\n")
write(f,"#################################\n")
write(f,"\n")
write(f, string(Len),"\n")
# println(cL_orig[1])
write(f,string(origin),"\n")
write(f,string(destination),"\n")
write(f,"\n")
for e =1:Len
    write(f, string(edge[e, 1]), "\t", string(edge[e, 2]),"\t", string(cL_orig[e]),"\t", string(cU_orig[e]),"\t", string(d[e]),"\n")
end

close(f)
# println(timesFile, dataSet, "; Ins ", Ins, "; Time ", total_time, "; MP_obj ", MP_obj, "; x_now ", findall(x_now.==1),"; Cells ", nrow(df_cell), "; Iter ", iter)#, "; W ", LB_w, "; Cuts ", numConv)
# close(timesFile)