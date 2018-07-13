'''
Created on 2018/07/12 14:45:43

@author: Yingkang Cao
'''

import re
import argparse

def first_quotePair(s, start_idx=0):
    '''
    find the first pair of quotes in <s> and return the two indices of individual quote
    note: do not consider escaped quote '\"'
    return scenarios:
        idx_l == -1 : fail to find any quote
        idx_l >= 0 and idx_r == -1 : find only one quote
        idx_l >= 0 and idx_r >= 0 : succeed 
    '''
    idx_l = -1
    idx_r = -1
    for idx in range(start_idx, len(s)):
        
        if s[idx] == '"':
            #TODO: check if this quote is escaped
            substr = s[idx-1::-1]
            if re.match(r"(\\\\)*\\", substr):
                continue
            #TODO: reset <idx_l> and <idx_r>
            if idx_l == -1:
                idx_l = idx
            else:
                idx_r = idx
                break
    return idx_l, idx_r


def first_balanced_symbolPair(s, lsymbol, rsymbol, start_idx=0, ignore_inQuotesSym=True):
    '''
    find the first <lsymbol>(search from index <start_idx>) and find its balanced <rsymbol>
    return the two indices of each symbol of the balanced pair
    return scenarios:
        idx_l == -1 : fail to find any <lsymbol>
        idx_l >= 0 and idx_r == -1 : fail to balance symbol pairs
        idx_l >= 0 and idx_r >= 0 : succeed 
    '''
    assert lsymbol != rsymbol, 'arguments <lsymbol> and <rsymbol> cannot be the same'
    count = 0
    idx_l = -1
    idx_r = -1
    idx = start_idx
    while idx < len(s):
        chrc = s[idx]
        if ignore_inQuotesSym == True and chrc == '"':
            idx = first_quotePair(s, idx)[1] + 1
            continue
        if chrc == lsymbol:
            if idx_l == -1:
                idx_l = idx
            count += 1
        if chrc == rsymbol and idx_l >= 0:
            count -= 1    
        if count == 0 and idx_l >= 0:
            idx_r = idx
            break
        idx += 1
    return idx_l, idx_r


def isMonochromaticList(l):
    '''
    judge if the list <l>'s entries are monochromatic
    '''
    assert type(l) == type([]), 'argument l in function isMonochromaticList is not a list' 
    for i in range(1,len(l)):
        if l[0] != l[i]:
            return False
    return True
    



if __name__ == "__main__":
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument('InputPaths', help='Paths for input files, format: "path_1,path_2,...,path_n" (use "," as the separate symbol)')
    argparser.add_argument('OutputPath', help='Path for output file')
    args = argparser.parse_args()
    
    path_strs = args.InputPaths.split(',')
    output_path = args.OutputPath
    
    cells_list = [] #List<String>
    metadata_list = [] #List<String>
    nbformat_list = [] #List<Integer>
    nbformat_minor_list = [] #List<Integer>

    cel_pObj = re.compile('"cells":')
    met_pObj = re.compile('"metadata":')
    nbf_pObj = re.compile('"nbformat":')
    nbf_m_pObj = re.compile('"nbformat_minor":')
    int_pObj = re.compile('\d+')
    
    for path_str in path_strs:
        with open(path_str,'r',encoding='utf-8') as f:
            s = f.read()
            #TODO: extract "cells" info
            match = re.search(cel_pObj, s)
            assert match, 'fail to find "cells" info in file: ' + path_str
            s = s[match.end():]
            idx_l, idx_r = first_balanced_symbolPair(s, lsymbol='[', rsymbol=']')        
            assert idx_l >= 0 and idx_r >= 0, 'idx_l={},idx_r={}'.format(idx_l, idx_r)+'fail to balance symbol pairs containing "cells" info in file: ' + path_str
            cells_info = s[idx_l+1:idx_r].strip() #strips '[', ']' and white symbols
            cells_list.append(cells_info)
            s = s[idx_r+1:]
            #TODO: extract "metadata" info
            match = re.search(met_pObj, s)
            assert match, 'fail to find "metadata" info in file: ' + path_str
            s = s[match.end():]
            idx_l, idx_r = first_balanced_symbolPair(s, lsymbol='{', rsymbol='}')        
            assert idx_l >= 0 and idx_r >= 0, 'fail to balance symbol pairs containing "metadata" info in file: ' + path_str
            metadata_info = s[idx_l+1:idx_r].strip() #strips '{', '}' and white symbols
            metadata_list.append(metadata_info)
            s = s[idx_r+1:]
            #TODO: extract "nbformat" info
            match = re.search(nbf_pObj, s)
            assert match, 'fail to find "nbformat" info in file: ' + path_str
            s = s[match.end():]
            match = re.search(int_pObj, s)
            assert match, 'fail to find any integer after "nbformat" in file: ' + path_str
            nbformat_info = int(match.group())
            nbformat_list.append(nbformat_info)
            s = s[match.end():]
            #TODO: extract "nbformat_minor" info
            match = re.search(nbf_m_pObj, s)
            assert match, 'fail to find "nbformat_minor" info in file: ' + path_str
            s = s[match.end():]
            match = re.search(int_pObj, s)
            assert match, 'fail to find any integer after "nbformat_minor" in file: ' + path_str
            nbformat_minor_info = int(match.group())
            nbformat_minor_list.append(nbformat_minor_info)
            s = s[match.end():]
            
            s = s.strip().strip('}')
            assert len(s) == 0, 'syntax error in file: ' + path_str
    
    assert isMonochromaticList(metadata_list), 'the "metadata" info is not the same between these files'
    assert isMonochromaticList(nbformat_list), 'the "nbformat" info is not the same between these files'
    assert isMonochromaticList(nbformat_minor_list), 'the "nbformat_minor" info is not the same between these files' 
    
    with open(path_strs[0], 'r',encoding='utf-8') as f:
        s = f.read()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        #TODO: synthesize all_cells_info
        idx_first_l, idx_first_r = first_balanced_symbolPair(cells_list[0], lsymbol='{', rsymbol='}')
        idx_second_l, idx_second_r = first_balanced_symbolPair(cells_list[0], lsymbol='{', rsymbol='}', start_idx=idx_first_r)
        join_str = cells_list[0][idx_first_r+1:idx_second_l]
        all_cells_info = join_str.join(cells_list)
        #TODO: write output_path
        '''
        match = re.search(cells_list[0], s)
        s[match.start():match.end()] = all_cells_info
        '''
        repl_start = s.find(cells_list[0])
        assert repl_start >= 0
        repl_end = repl_start + len(cells_list[0])
        output_s = s[:repl_start] + all_cells_info + s[repl_end:]
        f.write(output_s)




