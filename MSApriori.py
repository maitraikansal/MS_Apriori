# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 22:06:09 2018

"""


import itertools
from collections import OrderedDict


def loadDataSet(file):
    t = open(file,"r").read().split("\n")
    return t


def must_have_check(freq_item_set, must_have):

    if len(must_have) > 0:
        for i in range(len(freq_item_set)):
            item_set_index = 0
            for item_set in range(len(freq_item_set[i])):
                if i > 0 and freq_item_set[i]:
                    f_k = [x[:-2] for x in freq_item_set[i]]
                else:
                    f_k = freq_item_set[i]
                if bool(set(must_have) & set(f_k[item_set_index])) == False:
                    freq_item_set[i].remove(freq_item_set[i][item_set_index])
                    item_set_index = item_set_index - 1
                item_set_index += 1
    return freq_item_set



def init_pass1(transactions, itemMinSupport):
    candidate = []
    l_item = []
    MIS = next (iter (itemMinSupport.values()))
    for row in itemMinSupport.items():
        count = 0
        support = 0
        
        for t in transactions:
            count += t.count(row[0])
        support = (count/len(transactions))
        if support >= float(MIS):
            l_item = [row[0], float(row[1]), support]
            candidate.append(l_item)
    return candidate


def cannot_be_together_check(freq_item_set,cannot_have):

    if len(cannot_have) > 0:
        for item_set in cannot_have:
            for i in range(len(freq_item_set)):
                item_index = 0
                if i > 0 and freq_item_set[i]:
                    f_k = [x[:-2] for x in freq_item_set[i]]
                    for j in f_k:
                        if set(item_set) <= set(f_k[item_index]):
                            freq_item_set[i].remove(freq_item_set[i][item_index])
                            f_k.remove(f_k[item_index])
                            item_index = item_index -1
                        item_index = item_index + 1
            
    return freq_item_set


def findSubsets(itemSet,subsetLength):
    return list(set(itertools.combinations(itemSet, subsetLength)))


def level_2_candidate_generation(l,sdc):
    candidate_list = []
    l_index = 0
    for l_items in l:
        l_index += 1
        if l_items[2] >= l_items[1] :
            for h_items in l[l_index:]:
                if h_items[2] >= l_items[1] and abs(h_items[2] - l_items[2]) <= sdc:
                    candidate_list.append(l_items[0]+","+h_items[0])
        
    return candidate_list

def MScandidate_gen(frequent_items_set,sdc,l,itemMinSupport): 
    candidate = []
    index_f = 0
    frequent_item_pair = False
    for f1 in frequent_items_set:
        k_items = len(f1)
        for f2 in frequent_items_set[index_f+1:]:
            c = []
            for i in range(k_items-1):
                if f1[i] == f2[i]:
                    frequent_item_pair = True
                else:
                    frequent_item_pair = False
                    break
            if frequent_item_pair == True:
                
                sup_f1 = [x[2] for x in l if f1[k_items-1] == x[0]]
                sup_f2 = [x[2] for x in l if f2[k_items-1] == x[0]]
                if (itemMinSupport.get(f1[k_items-1]) < itemMinSupport.get(f2[k_items-1])) and (abs(float(sup_f2[0])- float(sup_f1[0])) <= sdc):
                    
                    c = list(set(f1 + f2))
                    candidate.append(c)
                if len(c) > 1: 
                    subsets = findSubsets(c, len(c)-1)
                    for s in subsets:
                        
                        if (c[0] in list(s)) or (itemMinSupport.get(c[1]) == itemMinSupport.get(c[0])):
                            if list(s) not in frequent_items_set:
                                candidate.remove(c)
                                break
    return candidate
                


def MSApriori():

    
    file = ['data/input-data.txt','para/parameter-file.txt']
    candidates_set = []
    frequent_items_set = []
    transactions = loadDataSet(file[0])
    transactions = [t.strip("{}") for t in transactions]
    transactions = [x.split((',')) for x in transactions]
    transactions = [[x.strip(" ") for x in t] for t in transactions]
    
    
    itemMinSupport = {}
    with open(file[1],"r") as f:
        for row in f:
            row_val = row.replace("=",":").split(":")
            
            if not row.isspace():
                if row_val[0] != 'SDC ':
                    if row_val[0][4].isdigit():
                        row_val[0] = row_val[0][4:].replace(") ","")    
                    row_val[1] = row_val[1].strip(" ")
                itemMinSupport[row_val[0]] = row_val[1].strip("\n")
    must_have = itemMinSupport.get("must-have")
    if must_have:
        del itemMinSupport["must-have"]
        must_have = list(must_have.split(" or "))
    else:
        must_have = []
    cannot_have = itemMinSupport.get("cannot_be_together")
    if cannot_have:
        del itemMinSupport["cannot_be_together"]
        cannot_have = list(cannot_have.split("},"))
        cannot_have = list([y.split(",") for y in [x.strip(" {}") for x in cannot_have]])
        cannot_have = [[x.strip(" ") for x in t] for t in cannot_have]
    else:
        cannot_have = []
    sdc = float(itemMinSupport.pop("SDC "))
    
    itemMinSupport = OrderedDict(sorted(itemMinSupport.items(), key=lambda t: t[1]))
    
    l = init_pass1(transactions, itemMinSupport)
    
    frequent_items_set.append(list([x[0].split(',') for x in l if x[2] >= x[1]]))
    
    
    index_k = 1
    while len(frequent_items_set[index_k -1]) > 0: 
        if index_k == 1:
            candidates_set = list(level_2_candidate_generation(l,sdc))
            
        else:
            candidates_set = MScandidate_gen(f_k,sdc,l,itemMinSupport)
        for t in transactions:
            index_c = 0    
            
            for c in candidates_set:
                try:
                    c = list(c.split(','))
                except:
                    print("c as list: ",c)
                if len(c)<index_k+2:
                    c.append(0)
                    c.append(0)
                
                if set(c[:2])<set(t):
                    c[-2] = int(c[-2]) + 1
                candidates_set[index_c] = ','.join(str(x) for x in c)
                if set(c[1:-2]) < set(t):
                    c[-1] = int(c[-1]) + 1
                candidates_set[index_c] = ','.join(str(x) for x in c)
                index_c += 1   
        f_k = []
        for c in candidates_set:
            c= list(c.split(','))
            if float(c[-2])/len(transactions) >= float(itemMinSupport.get(c[0])): 
                f_k.append(c)
        
        frequent_items_set.append(f_k) 
        f_k = [f[:-2] for f in f_k]       
        index_k += 1
    frequent_items_set = cannot_be_together_check(frequent_items_set,cannot_have)
    frequent_items_set = must_have_check(frequent_items_set, must_have)
    print("Pruned Frequent_item_set: ", frequent_items_set)
    return frequent_items_set, transactions


def output(frequent_items_set, transactions):
    output_file = open("result/result.txt","w") 
    for i in range(len(frequent_items_set)):
        
        if len(frequent_items_set[i]) >0:
            output_file.write("Frequent %s-itemset " %(i+1)+"\n")
            print("Frequent %s-itemset " %(i+1))              
        if(i == 0) and (len(frequent_items_set[i]) == 0):
            print("Total number of itemsets = 0")
            output_file.write("Total number of itemsets = 0")
        
        if i == 0:
            for k in (frequent_items_set[i]):
                count = 0
                for t in transactions:
                    count += t.count(k[0])
                output_file.write("\t%s : %s "%(count,set(k))+"\n") 
                print("\t%s : %s "%(count,set(k)))
        for j in range(len(frequent_items_set[i])):
            if (i > 0) and (len(frequent_items_set[i]) >0):
                output_file.write("\t%s : %s "%(frequent_items_set[i][j][-2],set(frequent_items_set[i][j][:-2]))+"\n") 
                output_file.write("Tail Count = %s" %(frequent_items_set[i][j][-1])+"\n") 
                print("\t%s : %s "%(frequent_items_set[i][j][-2],set(frequent_items_set[i][j][:-2]))+"\n")
                print ("Tail Count = ", frequent_items_set[i][j][-1]+"\n")
    output_file.close()    



def main():
    
    frequent_items_set, transactions = MSApriori()
    output(frequent_items_set, transactions)


if __name__ == "__main__": main()







