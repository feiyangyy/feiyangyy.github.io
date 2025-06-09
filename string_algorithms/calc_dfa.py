"""
1. 基本概念 非平凡 前缀-后缀最大重叠子串
如字符串ABABA， prefix:A AB ABA ABAB sufix:A BA ABA BABA (这里看后缀时总是情不自禁倒数)，此时j=5, 如果j+1 发生失配比如：
文本 ABABAB... <= i =5, j = 6 失配, 此时看失配前一状态j-1=5的模式串(ABABA) 和文本串是匹配的 
模式 ABABAC                       
调整:
ABABA|D...  => ABABA|D... 
ABABA|C     =>   ABA|BAC --> 已知3个匹配，处理第四个
                 ---
                 此处为复用部分
下一步，当前j=3,匹配子串为ABA，前缀 A AB , 后缀A BA， 那么最大... 是 A，因此重启状态是1（当然，生成阶段不是这么推的）
调整2：
ABABA|D   => ABABA|D...
  ABA|BA  =>     A|BABAC  => 这里j=1, 处理第2个匹配，即pat[1] vs i

这里ABABA 是已知的匹配字符数，即dfa=5的状态， 此时前缀-后缀最大重叠为3，即j=5的重启状态为3(这里容易受到j起始值的干扰)

这些步骤在生成dfa时已唯一被确定

calc_dfa(ABABAC)
round 1 X:0
round 2 X:1
round 3 X:2
round 4 X:3 ==> 这里的重启状态对于j=5 起作用（已有5个匹配，并且正在处理第6个匹配），可以这么断言pat[STATE]在STATE时尚未匹配
round 5 X:0 ==> 这里没有下一轮

这里记住一个法则：456， 即第4轮迭代，设置第5个状态，处理第6个字符
round 4 X:3 代表pat[5] 失配时，从重启状态X=3开始，对text[i]输入进行匹配
"""

"""
2. 再来看生成dfa的过程
for ch in range(256):
    dfa[j][ch] = dfa[X][ch] ==> 使用重启状态处理不匹配字符（已知X匹配，尝试匹配X+1）
正常处理
    这个要理解匹配迭代过程最长公共...的变化流程，
这里的j表示 已知j个匹配，从而，匹配的索引是**(0,j-1)**

对于ABABA 这个匹配串
j=0, X=0, m='' 初始状态,dfa[0]['A'] = 1(只要匹配就前进)，其他为0
j=1, X=0, m='A'，不存在...
j=2, X=0, m ='AB'， 无公共.., dfa[0]['B'] = 0
j=3, X=1, m='ABA' => 明显此时有最大... 'A'，长度为1 X=1 ， 再计算下一个迭代：X(j+1)=dfa[1][pat[j]] = 2 => 当前重叠位置是(0)(2), 而j=3,意味着处理第4个字符(count from 1)
                  => 即检查：当前最大...(0, X-1)的下一个字符 pat[X] 是否与 当前处理的字符 pat[j] 相等。
j=4, X=2, m='ABAB' => .... 'AB' => X=2， X(j+1)=dfa[1][B] = 2 （乱的又来了, 当前状态的X，是在上一个状态中计算的)
...
X = dfa[X][ord(pattern[j])]

站在'ABAB'这种情况来看， X=2，即前缀'AB', 后缀'AB', dfa[X]实际上是'AB'的下一个字符,dfa[0] 可以理解为取得''的下一个字符（也就是模式串的第一个字符）
我们这么看
X(j+1) = dfa[X][ord(pattern[j])]
=> j 是已知匹配字符数量，匹配区间是（0，j-1)
=> pat[j] 是匹配区间的下一个字符
=> dfa[X] 是当前最大重叠区间的[0, X-1]的下一个字符 => 这里总是不知道X是相对于谁的
=> X 是相对于状态j的，描述的是字符串(0,j-1)情况，而非（0，j)的情况 （X意味着历史匹配）
=> 状态j负责匹配转移第j个字符（意味着尚未匹配）
"""

def calc_dfa(pattern:str):
    dfa =  [[0] * len(pattern) for _ in range(256)]
    j :int = 0
    
    # the first character
    # the dfa[pat[0]][0] = 1, others zero
    dfa[ord(pattern[0])][j] = 1
    x_arr=list()
    X = 0
    x_arr.append(X)
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
        x_arr.append(X)
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
        # here x is for j+1
        X = dfa[X][ord(pattern[j])]
    return dfa
"""
means 
a [1, 1, 3, 1, 3] => dfa['a'][0] = 1 dfa['a'][1] = 1 ...
b [0, 2, 0, 4, 0] 
c [0, 0, 0, 0, 5]
"""

calc_dfa("ABABAC")

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


def calc_dfa_foo(pattern:str):
    l = len(pattern)
    dfa = [[0] * 256 for _ in range(l)]
    dfa[0][ord(pattern[0])] = 1
    X=0
    for j in range(1, l):
        # 在[0,j-1] 已匹配的串中，根据重叠串的情况
        # 这里的含义其实就是回退模式串指针，或者是右移模式串，把[0,X-1] 对齐到[i-X, i-1]的位置
        # 这里的i是文本串，也就是所谓的重启状态处理
        for ch in range(256):
            # note if there is a duplicate
            # check if dfa[X=0][ch=pat[X]] = X+1
            # for exp: AB dfa[1][A] =dfa[0][A] = 1
            
            dfa[j][ch] = dfa[X][ch]
        # 转移下一个状态，J状态处理pattern[j] 匹配时发生的时
        dfa[j][ord(pattern[j])] = j + 1
        # 尝试匹配pat[X], pattern[j], 一旦成功，则重叠更新为[0,X], [j-X+1, j]
        # X(j+1) = X+1 for [0,j]
        X = dfa[X][ord(pattern[j])]
    return dfa
        
def kmp_search(p:str, text:str):
    dfa = calc_dfa_foo(p)
    l = len(p)
    matched = 0
    for ch in text:
        # 对ch 处理由这个dfa 状态转移自动处理，可以说，dfa 唯一确认了在状态s下，输入ch的下一个状态（重点）
        matched = dfa[matched][ch]
        if matched == l:
            return True
    return False
