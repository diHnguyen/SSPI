# using DataFrames
# using JuMP
# using TimerOutputs
# using Plots

function findRange((l1,u1),(l2,u2)) #Used in Convolution
    r = u1-l1
    R = u2-l2
    bounds = Array{Float64}(undef, (0, 2))
    if R != r
        bounds = [0 r; r R; R R+r]
#         bounds =[ ]
        bounds = bounds.+(l1+l2)
    else
        bounds = [0 r; r r+R]
        bounds = bounds.+(l1+l2)
    end
    return bounds
end
function timeShift(poly, direction, r) #Used in Convolution
    c = coeffs(poly)
    myRoot = 0
    if direction == "left"
        myRoot = -r
    end
    
    if direction == "right"
        myRoot = r
    end
    multiplier_poly = Polynomial([1]) 
    # println(multiplier_poly)
    my_poly = Polynomial([0])

    for i = 1:length(c)
        my_poly = my_poly + multiplier_poly*c[i]
        multiplier_poly = multiplier_poly*(fromroots([myRoot])) 
    end
    return my_poly
end

function Convolve(cL, cU, unc_arcs)
#     cL = [0,0,0].+1
#     cU = [3,1,2].+1
#     println("cL = ", cL)
#     println("cU = ", cU)
#     global Len
        #Temporary Creating ranges here:
        
        df = DataFrame(PolyNum = String[], Poly = Polynomial{Float64}[], l = Float64[], u = Float64[], leftShift = Float64[])
    
#     if length(unc_arcs) == 0
#         push!(df, (1, Polynomial([1]), 0,0,0))
#     else
        df_Uniform = DataFrame(LB = Float64[], UB = Float64[], r = Float64[])
    #     println("Deterministic Arcs = ", det_arcs)
        for i = 2:length(unc_arcs)
            k = unc_arcs[i]
            push!(df_Uniform,(cL[k],cU[k],cU[k]-cL[k]))
        end
    #     println("dfUniform ", df_Uniform)
        numOrder = length(cL)  #maxOrder = numOrder - 1 since we need to account for degree 0
        
        first_arc = unc_arcs[1]
        push!(df,("", 1/(cU[first_arc]-cL[first_arc]), cL[first_arc],cU[first_arc], 0.0))
        numPoly = 1
        ii=0

        while length(df_Uniform[:,:LB]) > 0
    #         println(df)

            l1 = df_Uniform[1,:LB]
            u1 = df_Uniform[1,:UB]
            r1 = df_Uniform[1,:r]

            poly1 = Polynomial([1/r1])

            #Time shift Uniform Var.###
            l1LeftShift = l1
            ####Update (l1,u1)
            u1 = r1
            l1 = 0

            poly_to_Integrate = length(df[:, :PolyNum])
            ii=ii+1

            for k = 1:poly_to_Integrate #numPoly #numOrder-1
                l2 = df[k,:l]
                u2 = df[k,:u]
                r2 = u2 - l2

                poly2 = df[k,:Poly]

                #Shift poly2:
                poly2 = timeShift(poly2, "left", l2)
                totalLeftShift = l1LeftShift + l2 + df[k,:leftShift]
                u2 = r2
                l2 = 0

                bounds = []
                int_L = 0
                int_U = 0

                abs_L = l2
                abs_U = u2

                if r2 > r1
                    bounds = findRange((l1,u1), (l2,u2))
                else
                    bounds = findRange((l2,u2), (l1,u1))
                end

                #This returns the function that we need to integrate wrt different sets of bounds
                p_combine = poly1 * poly2

                #Integrate p_combine: Same for all 2 or 3 ranges below
                p_int = integrate(p_combine)

                #Calculate the lower-bound polynomial with variable 
                #E.g. if the integration goes from t-4 to t then the lower bound is evaluated at t-4
                #E.g. if the integration goes from t-3 to t-1 then the upper bound is evaluated at t-1
                #Note that for the lower bound integral we use fromroots([int_U]) since t-int_U gives us a lower bound
                #Note that for the upper bound integral we use fromroots([int_L]) since t-int_L gives us an upper bound

                #Evaluate p_int at the lower bound t-root_L is
                #similar to perform time shift to the right or when = "post" 

                my_poly_L = timeShift(p_int, "right", r1)

                #Evaluate with 1st resulting range: from L to t
                L = bounds[1,1]
                U = bounds[1,2]
                p_1 = p_int - p_int(l2) #Note that p_combine evaluated at t returns the same polynomial 
                df[k,:] = df[k,:PolyNum]*".1", p_1, L, U, totalLeftShift         

                #Deal with 2nd resulting range: from t-some_range to t
                #If there are only 2 resulting ranges then we don't need to calculate this.
                row = 2
                if length(bounds[:,1]) > 2
                    numPoly = numPoly + 1
                    p_2 = Polynomial([0])
                    if r2 > r1
                        p_2 = p_int - my_poly_L
                    end

                    if r2 < r1
                        interval_2 = p_int(u2) - p_int(l2)
                        p_2 = Polynomial([interval_2])
                    end
                    push!(df,(df[k,:PolyNum]*"."*string(row), p_2, bounds[row,1], bounds[row,2],totalLeftShift))
                    row = row + 1
                end

                p_3 = p_int(u2) - my_poly_L
                numPoly = numPoly + 1
                push!(df,(df[k,:PolyNum]*"."*string(row),p_3,bounds[row,1],bounds[row,2],totalLeftShift))

            end
            delete!(df_Uniform, 1)

        end
#     end
    return df, numPoly
end


function convolveEachCell()
    global df_cell, Len, d, x_now
    df_cellPoly = DataFrame(CELL = Int64[], df = Any[], NUMPOLY = Int64[], DETSHIFT = Float64[])
#     println(df_cell)
    for k = 1:nrow(df_cell)
        cL = df_cell[k,:LB]+d.*x_now
        cU = df_cell[k,:UB]+d.*x_now
        y = df_cell[k,:Y]
#         println("\nCell ", k)
        unc_arcs = findall((y.>0) .& (cL.<cU))
        det_arcs = findall((y.>0) .& (cL.==cU))
#         println("unc_arcs = ", unc_arcs)
#         println("det_arcs = ", det_arcs)
        if isempty(det_arcs) == false
            det_Shift = sum(cL[i] for i in det_arcs)
        else
            det_Shift = 0
        end
#         println("Cell ", k, " : g = ", df_cell[k,:g, ",", path, "; cL = ", L[path],", cU = ", U[path], "; gU = ", sum(U[path]), "; p = ",i.PROB)
        df = DataFrame(PolyNum = String[], Poly = Polynomial{Float64}[], l = Float64[], u = Float64[], leftShift = Float64[])
        if isempty(unc_arcs) == true
            push!(df, ("1", Polynomial([1]), 0, 0, det_Shift) ) #Changes made here
            numPoly = 0 #Changes made here
        else
            df, numPoly = Convolve(cL, cU, unc_arcs)
        end
        if numPoly == 0
            df.w = zeros(1) #Changes made here
        else
            df.w = zeros(numPoly)
        end
#         println(df)
        push!(df_cellPoly, (k,df,numPoly, det_Shift))
    end
    return df_cellPoly
end