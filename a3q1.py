import copy

# Print factor in specific format
def print_format(factor):
    s = [[str(e) for e in row] for row in factor]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))
    return
    
# This function restricts the given variable in the given factor to the given
# value
def restrict(factor,variable,value):
    print("Restricted to "+variable+" = "+str(value)+":")
    print_format(factor)
    print("")
    # Represent how many rows and columns in the factor
    row = len(factor)
    column = len(factor[0])
    result = copy.deepcopy(factor)
    # Find the column of restrict variable
    index = -1
    for i in range(column):
        if factor[0][i] == variable:
            index = i
            break
    # Find the restricted row and if it is not the value then remove it
    # If it is the value remove the item
    for item in result[1:]:
        if item[index] != value:
            result.remove(item)
        else:
            item.pop(index)
    # Remove the restricted variable from the first line
    result[0].pop(index)
    print("Result:")
    print_format(result)
    print("--------------")
    return result

def add_rows(common,tf,var,factor):
    result = copy.deepcopy(factor[1:])
    # Collect the index of common variables in var
    index = []
    for i in range(len(common)):
        for j in range(len(var)):
            if common[i] == var[j]:
                index.append(j)
    # Check each row if it is the one we need
    for row in factor[1:]:
        for i in range(len(index)):
            if row[index[i]] != tf[i]:
                result.remove(row)
                break
    index.sort(reverse=True)
    for row in result:
        for i in range(len(index)):
            row.pop(index[i])  
    return result

# This funtion performs pointwise multiplication of the given two factors
def multiply(factor1,factor2):
    print("Multipying:")
    print_format(factor1)
    print("")
    print_format(factor2)
    print("")
    var1 = factor1[0][:-1]
    var2 = factor2[0][:-1]
    common = []
    union = var1
    # Find common variables
    result = [union]
    for item in var2:
        if item in var1:
            common.append(item)
        else:
            union.append(item)
    result[0].append("Prob")
    for row in factor1[1:]:
        tf = []
        for i in range(len(var1)):
            if var1[i] in common:
                tf.append(row[i])
        new_data = add_rows(common,tf,var2,factor2)
        for item in new_data:
            temp1 = copy.deepcopy(row[:-1])
            temp2 = copy.deepcopy(item[:-1])
            temp3 = [row[-1]*item[-1]]
            temp = temp1+temp2+temp3
            result.append(copy.deepcopy(temp))
    print("Result:")
    print_format(result)
    print("--------------")
    return result

# This funtion sums out a variable in a given factor
def sumout(factor,variable):
    print("Sumout "+variable+" from:")
    print_format(factor)
    print("")    
    result = factor
    row = len(factor)
    column = len(factor[0])
    # Find the column of sumout variable
    index = -1
    for i in range(column-1):
        if factor[0][i] == variable:
            index = i
            break  
    for row in result:
        row.pop(index)
    for i in range(1,len(result)):
        for j in range(i+1,len(result)):
            if result[i][:-1] == result[j][:-1]:
                result[i][-1] += result[j][-1]
                result.pop(j)
                break
    print("Result:")
    print_format(result)
    print("--------------")
    return result

# This function normalizes a factor by dividing each entry by the sum of all the
# entries.
def normalize(factor):
    print("Normalize:")
    print_format(factor)
    print("")    
    total = 0
    for item in factor[1:]:
        total += item[-1]
    for item in factor[1:]:
        item[-1] = item[-1]/total
    print("Result:")
    print_format(factor)
    print("--------------")
    return factor

# This function computes Pr(query_variable|evidence_vars) by the variable 
# elimination algorithm
def inference(factor_list,query_variable,ordered_hidden_var_list,evidence_vars):
    print("Step 1: Restrict the factors.\n")
    restricted_factors = []
    for factor in factor_list:
        new_factor = factor
        for evidence in evidence_vars:
            if evidence[0] not in factor[0]:
                continue
            new_factor = restrict(new_factor,evidence[0],evidence[1])
        restricted_factors.append(new_factor)        
    print("Step 2: Eliminate each hidden variable according to an order.\n")
    filtered_factors = []
    remained_factors = []
    for factor in restricted_factors:
        for var in ordered_hidden_var_list:
            if var in factor[0]:
                filtered_factors.append(factor)
                break
    for item in restricted_factors:
        if item not in filtered_factors:
            remained_factors.append(item)
    # Multiply factors
    product = filtered_factors[0]
    for item in filtered_factors[1:]:
        product = multiply(product,item)
    # Sum out hidden variables
    sumed = product
    for var in ordered_hidden_var_list:
        sumed = sumout(sumed,var)
    print("Step 3: Multiple the remaining factors.\n")
    result = sumed
    for item in remained_factors:
        result = multiply(result,item)
    print("Step 4: Normalize the resulting factor.\n")
    result = normalize(result)
    print("================================================================")
    return

def main():
    '''
    Variables:
    • AB: There is food left in Aria’s food bowl. 
    • AH: Aria howls.
    • AS: Aria is sick.
    • M: There is a full moon.
    • NA: Your neighbour is away.
    • NH: Your neighbour’s dog howls.
    '''
    f1 = [["AS","Prob"],[1,0.05],[0,0.95]]
    f2 = [["AB","AS","Prob"],[1,1,0.6],[1,0,0.1],[0,1,0.4],[0,0,0.9]]
    f3 = [["M","Prob"],[1,1/28],[0,1-1/28]]
    f4 = [["NA","Prob"],[1,0.3],[0,0.7]]
    f5 = [["NH","M","NA","Prob"],[1,1,1,0.8],[1,1,0,0.4],[1,0,1,0.5],[1,0,0,0],
          [0,1,1,0.2],[0,1,0,0.6],[0,0,1,0.5],[0,0,0,1]]
    f6 = [["AH","AS","M","NH","Prob"],[1,1,1,1,0.99],[1,1,1,0,0.9],
          [1,1,0,1,0.75],[1,1,0,0,0.5],[1,0,1,1,0.65],[1,0,1,0,0.4],
          [1,0,0,1,0.2],[1,0,0,0,0],[0,1,1,1,0.01],[0,1,1,0,0.1],[0,1,0,1,0.25],
          [0,1,0,0,0.5],[0,0,1,1,0.35],[0,0,1,0,0.6],[0,0,0,1,0.8],[0,0,0,0,1]]
    factor_list = [f1,f2,f3,f4,f5,f6]
    
    # (a) Compute Aria howls
    print("(a)\n**Compute Aria howls** \n P(AH)")
    query_variable = "AH"
    ordered_hidden_var_list = ["AB","AS","M","NA","NH"]
    evidence_vars = []
    inference(factor_list,query_variable,ordered_hidden_var_list,evidence_vars)
    # (b) Compute Aria is sick. Knowing Aria is howling and full moon
    print("(b)\n**Compute Aria is sick. Knowing Aria is howling and full moon** \n P(AS|AH,M)")
    query_variable = "AS"
    ordered_hidden_var_list = ["AB","NA","NH"]
    evidence_vars = [["AH",1],["M",1]]
    inference(factor_list,query_variable,ordered_hidden_var_list,evidence_vars) 
    # (c) Compute Aria is sick. Knowing Aria is howling, full moon and left food
    print("(c)\n**Compute Aria is sick. Knowing Aria is howling, full moon and left food** \n P(AS|AH,M,AB)")
    query_variable = "AS"
    ordered_hidden_var_list = ["NA","NH"]
    evidence_vars = [["AH",1],["M",1],["AB",1]]
    inference(factor_list,query_variable,ordered_hidden_var_list,evidence_vars) 
    # (d) Compute Aria is sick. Knowing Aria is howling, full moon, left food and neighbour not home
    print("(c)\n**Compute Aria is sick. Knowing Aria is howling, full moon, left food and neighbour not home** \n P(AS|AH,M,AB,NA)")
    query_variable = "AS"
    ordered_hidden_var_list = ["NH"]
    evidence_vars = [["AH",1],["M",1],["AB",1],["NA",1]]
    inference(factor_list,query_variable,ordered_hidden_var_list,evidence_vars)
    
if __name__ == "__main__":
    main()
