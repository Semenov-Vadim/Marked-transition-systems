# -*- coding: utf-8 -*-
##для написания комментариев на русском/украинском


##print('''Розробити клас, що представляє марковану систему переходів.
##Цей клас повинен мати метод accept(s : str) : bool,
##який повертає True якщо s сприймається МСП і False упротилежному випадку\n''')

print('''Від регулярного виразу до МСП.
Написати функцію ReX2LTS, що будує МСП, яка сприймає
точно множину слів специфіковану заданим регулярним
виразом\n''')

##Маркированная система переходов
class MarkedSys:
    def __init__(self, sigma: list, s: list, sFst: str,sLst: str, t:list):
        ##конечное ножество символов
        self.sigma = sigma
        ##символ спонтанного перехода
        self.eps = "e"
        ##Множество состояний
        self.s = s
        ##Начально состояние
        self.sFst = sFst
        ##Конечное состояние
        self.sLst = sLst
        ##Множество переходов
        self.t = t
    
    ##формирование замыкания
    def closure(self, x: list) -> list:
        ##x- пара: состояние и необработанный хвост слова
        w1 = [x]
        w2 = []
        while w1 != w2:
            w2 = w1
            ##расширяем w1 состояниями, достижимыми при спонтанном переходе из w2
            for trans in self.t:
                for temp in w2:
                    if trans[0] == temp[0] and trans[1] == self.eps:
                        w1.append([trans[2],x[1]])
        return w1
        
    ##проверка траектории на корректность
    def accept(self,s : str) -> bool:
        ##s- траектория (цепочка переходов)
        ##w- писок пар (состояние и количество обработанных символов из слова s)
        ##изначально находимся в начальном состоянии s1 и все слово еще не обработано
        w = self.closure(["s1",0])
        
        while len(w) != 0:
            x = w[0]
            ##отбрасываем элемент х из списка w
            w = w[1:]
            ##если дошли до конца слова
            if x[1] == len(s):
                ##если текущее состояние соответствует конечному состоянию
                if x[0] == self.sLst:
                    return True
            
            ##добавляем состояния, в которые можем перейти следующим шагом по траектории
            for trans in self.t:
                ##также не будем добавлять новые переходы, если уже достигнута длина слова (иначе будет IndexError: string index out of range)
                if trans[0] == x[0] and x[1] < len(s) and s[x[1]] == trans[1]:
                    ##сделаем замыкание
                    for temp in self.closure([trans[2],x[1] + 1]):
                        w.append(temp)
        return False

'''Class representing regular expression tree'''
class ReX:
    def __init__(self,**kwargs):
        ##дерево регулярного выражения
        self.tree = {}
        
        ##тривиальный случай
        ##Е обозначает пустое слово
        if len(kwargs) == 0:
            self.tree[0] = 'E'
        ##случай с одним токеном 
        elif 'token' in kwargs:
            self.tree[0] = kwargs['token']
        ##рассмотрим все возможные операции
        elif 'operation' in kwargs and 'expressions' in kwargs:
            if kwargs['operation'] == '*':
                if len(kwargs['expressions']) != 1:
                    raise Exception("Incorrect number of expressions")
                else:
                    self.tree['*'] = kwargs['expressions'][0].tree
            ##проверяем конкатенацию и альтернацию
            elif kwargs['operation'] in ('|',','):
                if len(kwargs['expressions']) != 2:
                    raise Exception('Incorrect number of expressions for ', kwargs['operation'])
                ##обавляем левое и правое поддерево
                else:
                    self.tree[kwargs['operation']] = {'left': kwargs['expressions'][0].tree,'right':kwargs['expressions'][1].tree}
        else:
            raise Exception('Incorrect input data')
        ##print(self.tree)

    def __str__(self):
        ##строковое представление дерева
        self.summary = ''
        return self.strTree(self.tree)
            
    def strTree(self, tree):
        if  0 in tree:
            ##пустое слово
            if tree[0] == 'E':
                self.summary = self.summary + ''
            ##токен
            else:
                self.summary = self.summary + tree[0]
        ##конкатенация между левым и правым поддеревом
        elif ',' in tree:
            self.summary = self.summary + '(' 
            self.strTree(tree[',']['left'])
            self.summary = self.summary + ','
            self.strTree(tree[',']['right'])
            self.summary = self.summary + ')'
        ##альтернация между левым и правым поддеревом    
        elif '|' in tree:
            self.summary = self.summary + '(' 
            self.strTree(tree['|']['left'])
            self.summary = self.summary +'|'
            self.strTree(tree['|']['right'])
            self.summary = self.summary + ')'
        ##звездочка, примененная ко всему выражению
        elif '*' in tree:
            self.strTree(tree['*'])
            self.summary = self.summary + '*'
        return self.summary
    
    def Rex2LTS(self):
        ##маркированная система переходов по дереву
        self.lts = [[],['sStart','sEnd'],'sStart','sEnd',[]]
        ##номер последнего состояния при построении LTS 
        self.num = 0
        return self.LTSMaker(self.tree, 'sStart', 'sEnd' )

    def LTSMaker(self, tree: list, sLft: str, sRgt: str):
        ##0 обозначает либо спонтанный переход, либо токен
        if 0 in tree:
            ##пустое слово
            if tree[0] == 'E':
                if not [sLft,'e',sRgt] in self.lts[4]:
                    ##добавляем спонтанный переход
                    self.lts[4].append([sLft,'e',sRgt])
            ##токен
            else:
                #добавляем переход по этому токену
                if not [sLft, tree[0], sRgt] in self.lts[4]:
                    self.lts[4].append([sLft, tree[0] ,sRgt])
                ##записываем этот токен во множество sigma
                if not tree[0] in self.lts[0]:
                    self.lts[0].append(tree[0])
        ##звездочка, примененная ко всему выражению
        elif '*' in tree:
            ##создаем новые входные и выходные состояния
            self.num += 1
            s1 = 's'+ str(self.num)
            self.num += 1
            s2 = 's'+ str(self.num)
            self.lts[1].append(s1)
            self.lts[1].append(s2)
            ##перепривязываем старые переходы
            ##заменяем выходящие переходы из старого входного состояния
            for i in range(len(self.lts[4])):
                if self.lts[4][i][0] == sLft:
                    self.lts[4][i][0] = s1
            ##заменяем входящие переходы в старое выходное состояние
            for i in range(len(self.lts[4])):
                if self.lts[4][i][2] == sRgt:
                    self.lts[4][i][2] = s2
            self.lts[4].append([sLft,'e',s1])
            self.lts[4].append([s2,'e',sRgt])    
            ##добавляем спонтанные переходы, если их не было
            if not [s1,'e',s2] in self.lts[4]:
                self.lts[4].append([s1,'e',s2])
            if not [s2,'e',s1] in self.lts[4]:
                self.lts[4].append([s2,'e',s1])
            self.LTSMaker(tree['*'], s1, s2)
        
        ##конкатенация между левым и правым поддеревом
        elif ',' in tree:
            ##создаем новое состояние
            self.num += 1
            s1 = 's'+ str(self.num)
            self.lts[1].append(s1)
            
            ##заменяем выходное состояние левого поддерева новым входным состоянием правого поддерева
            self.LTSMaker(tree[',']['left'], sLft, s1)
            self.LTSMaker(tree[',']['right'], s1, sRgt)
            
        ##альтернация между левым и правым поддеревом
        elif '|' in tree:
            ##привязываем входное и выходное состояния левого и правого поддерева к одному входному состоянию и одному выходному
            self.LTSMaker(tree['|']['left'], sLft, sRgt)
            self.LTSMaker(tree['|']['right'], sLft, sRgt)
        
        return self.lts
   
##для удобной расшифровки элементов МСП
def Expalain(lts: list):
    print('Конечное ножество символов: ', lts[0])
    print('Множество состояний: ', lts[1])
    print('Начальное состояние: ', lts[2])
    print('Конечное состояние: ', lts[3])
    print('Множество переходов: ', lts[4])
##-----------------------------------------------------
'''Примеры:'''

regExpr = ReX()
##print('Empty expression: ', regExpr)
##print('LTS Empty expression: ', regExpr.Rex2LTS('s1','s2'))
ltsExpr1 = regExpr.Rex2LTS()
##print('LTS Empty expression: ', ltsExpr1)

regExpr2 = ReX(token = 'a')
##print('Expression with one token: ', regExpr2)
ltsExpr2 = regExpr2.Rex2LTS()
##print('LTS Expression with one token: ', ltsExpr2)

regExpr3 = ReX(operation = '*', expressions = [regExpr2])
##print('Expression with *: ', regExpr3)
##ltsExpr3 = regExpr3.Rex2LTS('s1','s2', lts= ltsExpr2)
ltsExpr3 = regExpr3.Rex2LTS()
##print('LTS Expression with one token and *: ', ltsExpr3)


regExpr4 = ReX(operation = '|', expressions=[ReX(token='a'),ReX(token='b')])
##print('Expression with alternation: ', regExpr4)
##ltsExpr40 = ReX(token = 'b').Rex2LTS('s3','s4', lts= ltsExpr2)
ltsExpr4 = regExpr4.Rex2LTS()
##print('LTS Expression with alternation: ', ltsExpr4)
##Expalain(ltsExpr4)

regExpr5 = ReX(operation = ',', expressions=[regExpr4, ReX(token='c')])
##print('Expression with alternation and concatenation: ', regExpr5)
ltsExpr5 = regExpr5.Rex2LTS()
##print('LTS Expression with alternation and concatenation: ', ltsExpr5)


regExpr6 = ReX(operation = '*', expressions=[regExpr5])
print("Expression with alternation, concatenation and '*': ", regExpr6)
ltsExpr6 = regExpr6.Rex2LTS()
print('LTS Expression with alternation and concatenation: ', ltsExpr6)
print()
Expalain(ltsExpr6)

##incorrect cases:
##ReX(operation='*')
##ReX(operation=',', expressions= [ReX(token='a')])
##ReX(operation='*', expressions= [ReX(token='a'),ReX(token='b')])




##МСП, воспринимающая слова с четным числом вхождений a (пример из лекции):
m1 = MarkedSys(["a","b"],["s1","s2","sEven","sOdd"],"s1","s2", [["s1","e","sEven"],["sEven","e","s2"],["sEven","a","sOdd"],["sEven","b","sEven"],["sOdd","a","sEven"],["sOdd","b","sOdd"]])

##True, так как количество вхождения "а" парное
##print(m1.accept("aaabab"))

##True, так как перешли по спонтанному переходу
##print(m1.accept(""))

##False, так как непарное количество "a"
##print(m1.accept("bbbbbbbbba"))



m2 = MarkedSys(["a","b","f"],["s1","s2"],"s1","s2",[["s1","e","s2"],["s1","a","s2"],["s1","b","s2"],["s2","f","s1"]])

##False, т.к. перейдя в состояние s2 из него можно выйти только с помощью "f"
##print(m2.accept("aa"))

##True: перешли в s2 по "а", вернулись в s1 по "f", перешли в s2 по спонтанному переходу
##print(m2.accept("af"))

##False, т.к. перейдя по "а", нет возможности вернуться обратно
##print(MarkedSys(["a"],["s1","s2"],"s1","s2",[["s1","a","s2"]]).accept("aa"))





