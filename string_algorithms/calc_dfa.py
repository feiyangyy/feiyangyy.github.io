def calc_dfa(pattern:str):
    dfa =  [[0] * len(pattern) for _ in range(256)]
    j :int = 0
    
    # the first character
    # the dfa[pat[0]][0] = 1, others zero
    dfa[ord(pattern[0])][j] = 1
    
    X = 0
    # j is current state, means how many chs we've matched.
    # X is the restart state of current state j, and it's unique.
    # dfa['A'][j] means that given current state j, if we've matched A, the next state will be dfa['A'][j]
    # if matched, dfa[ch][j] = j + 1(next match), while ch = pattern[j]
    for j in range(1, len(pattern)):
        # here ch comes frome the original text, and is mismatched with the pattern[j]
        # so the next matched step should be it's RESTART STATE
        # dfa[c][X] means the TEXT[i]=c and the cases will be listed:
        # 1. pattern[X] != c; 
        # 2. pattern[X] == c;
        # means, the handle of mismatched chs will reuse the restart state.
        # it's the inheritance of the DFA
        # see how the restart state goes, if c == p[X], then dfa[c][j] = X+1 （reuse common prefix)
        # if c != p[X], then it depends, maximum X, it depends on X's previous value.
        # dfa[c][X-1], and if c == p[X-1], then it's value is X, and so on.
        # is it possible, that X will directly become 0? yes, if c is not in pattern [0:X-1], then it becomes zero.
        # we have to start from the begining. 
        # for example. we have the pattern ABABC,  and while j = 4,  the X = 2
        # c somehow can be dfa['O'][4] = dfa['O'][X=2] = dfa['O'][j=2] = 0
        for c in range(256):
            dfa[c][j] = dfa[c][X] # what does dfa[c][x] mean? the ch here is mismatched character
        # aussume that for ABABC, we've matched ABA, then the dfa ['A'][3] = 4;
        # but for the first A, we have the dfa['A'][1] = 2
        dfa [ord(pattern[j])][j] = j+1
        # X becomes the restart state of j + 1, and is the handle for pat[j] of the current restart state.
        # why can we do that? 
        # KMP aussmues that, we've stood on the current restart state, and we try to read a ch of pat[j], the result will be 
        # next state's restart state. but why?
        # ASSUME: X is commen length of  the prefix [0, X-1] vs suffix [j - |X|+1:j] 
        # but we can't see the comparison between prefix and suffix.
        # this is because the implicit DYNAMIC-PROGRAMMING.
        # according to the ASSUME, with given commen length X, if pattern [j] eqauls to pattern[X]
        # the dfa[p[j]][X] will not be zero. and remember the DFA means: at state X, read ch c equals to p[j], it stores the next state.
        # and if p[j] = p[X] (dfa[][X] represent [0: X-1], and if p[j] == p[X], means the commen-string grows up.), it will goes to some how X+1? 
        # is it possilbe that X will grow incontiniously? = NO! because the maximum value of dfa[][X] will be X+1.
        # but it could decrese incontiniously, that's depends on dfa[p[j]][X]
        # and here, is to checkout, whether start pos could handle pattern[J] or not.
        # which also means checkout if pattern[X] == pattern[j]
        # NOTE: this calculates the restart states of J+1!!!!!
        X = dfa[ord(pattern[j])][X]
        print(f"round {j} X:{X}")
    return dfa

def calc_dfa_human(pattern:str):
    l = len(pattern)
    # change first dim to state, second dim to ch
    dfa = [[0] * 256 for _ in range(l)]
    j = 0
    dfa[j][ord(pattern[0])] = 1
    X = 0
    for j in range(1, l):
        # default ch process
        for ch in range(256):
            dfa[j][ch] = dfa[X][ch]
        # if state j encounter pat[j], then matched
        dfa[j][ord(pattern[j])] = j+1
        # check if State X could handle pat[j]
        X = dfa[X][ord(pattern[j])]
    return dfa
"""
means 
a [1, 1, 3, 1, 3] => dfa['a'][0] = 1 dfa['a'][1] = 1 ...
b [0, 2, 0, 4, 0] 
c [0, 0, 0, 0, 5]
"""

calc_dfa("AAAABCDEFABCDE")

dfa = calc_dfa_human('ababc')

for i, e in enumerate(dfa):
    print(f"state {i} {e[ord('a')]}, {e[ord('b')]}, {e[ord('c')]}")

# print(lines[ord('a')])
# print(lines[ord('b')])
# print(lines[ord('c')])

"""
KMP的难点在于很多关键性的动态规划结构和计算过程是暗含的，由数据结构隐式的给出，不利于人去跟踪其变化
暗含的递推包括：
0. 前缀后缀重叠，不是回文串，如 ABCDABCD， 重叠区间为(0,3) (4:), 而ABCDDCBA没有重叠区间 (前缀后缀理解错误了)
    - 
1. 重启状态的递推，并且是逐步递推的（可重复的前缀、后缀，一定是连续增长的），但是下降可能是不连续的
2. 重启状态的隐式含义：在 j 状态下（已匹配j个字符）， 前缀(0, X-1) 与后缀(j-X+1, j)是重复的，X即为其长度， 重启状态为X，则重复前缀、后缀的长度为X，索引为(0, X-1)
   如 ABABA, 若X=2， 则AB前缀和后缀AB重复， 前后缀不能重叠即对于(ABABA) 而言， (0:2) (2:)  不是最大重叠子串


"""
def search_string( pattern:str, inputs:str):
    lines = calc_dfa_human(pattern)
    j = 0
    for _, i in enumerate(inputs):
        org_j = j
        j = lines[j][ord(i)]
        print(f"next state {j} for ch {i} with dfa[{org_j}][{i}]")
        if j == len(pattern):
            return True
    return False

search_string('ABABC', "ABABC")
print("-----")
"""
Here ,we got next state 4 for ch B ABAB is matched.
the next round, we encounter A, and dfa['C'][4] = 3, (which is consturcted in calc_dfa)
how do we understand that? dfa['C'][4] = 5, dfa['A'][4] = 3. 
and we can see, for state 4, the restart state is 2. and by dfa, this automatically handles the next start pointer,
as we've caluclated the correct next pos of current state.
"""
search_string('ABABC', "ABABA")