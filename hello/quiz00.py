import random

from hello.domains import my100, Member, myRandom, memberlist, myMember


class Quiz00:

    def quiz00calculator(self) -> float:
        a = my100()
        b = my100()
        o = ['+', '-', '*', '/', '%']
        ran_o = o[myRandom(0, 4)]
        if ran_o == '+': res = a + b
        elif ran_o == '-': res = a - b
        elif ran_o == '*': res = a * b
        elif ran_o == '/': res = a / b
        elif ran_o == '%': res = a % b

        print(f'{a} {ran_o} {b} = {res}')

        return None

    def quiz01bmi(self):
        this = Member()
        this.weight = 78.8
        this.height = 178.8
        getBmi = this.weight * 10000 / this.height / this.height
        if getBmi >= 35:
            res = '고도 비반'
        elif getBmi >= 30:
            res = '중도 비만 (2단계 비만)'
        elif getBmi >= 25:
            res = '경도 비만 (1단계 비만)'
        elif getBmi >= 23:
            res = '과체중'
        elif getBmi >= 18.5:
            res = '정상'
        else:
            res = '저체중'
        print(f'{myMember()}님의 BMI는 {getBmi:.2f}, {res}입니다.')
        return None

    def quiz02dice(self):
        print(myRandom(1, 6))
        return None

    def quiz03rps(self):
        p = myRandom(0, 2)
        c = myRandom(0, 2)
        rps = ['가위', '바위', '보']
        res = 'Lose' if (p + 1) % 3 == c else 'Draw' if p == c else 'Win'
        print(f'플레이어: {rps[p]}, 컴퓨터: {rps[c]}, 결과: {res}')
        return None

    def quiz04leap(self):
        y = myRandom(2000, 2022)
        # java
        # String s = () ? : ;
        # String s = (y % 4 == 0 && y % 100 != 0) ? "윤년" : y % 400 == 0 ? "윤년" : "평년";
        res = '윤년' if y % 4 == 0 and y % 100 != 0 or y % 400 == 0 else '평년'
        print(f'{y}년은 {res}입니다.')
        return None

    def quiz05grade(self):
        kor = myRandom(0, 100)
        eng = myRandom(0, 100)
        math = myRandom(0, 100)
        sum = kor + eng + math
        avg = sum / 3
        res = '합격' if avg >= 60 else '불합격'
        print(f'국어: {kor}, 영어: {eng}, 수학: {math}, 평균: {avg:.2f}, 결과: {res}')

    @staticmethod
    def quiz06memberChoice():

        return myMember()

    def quiz07lotto(self):
        print(sorted(random.sample(range(1, 46), 6)))
        return None

    def quiz08bank(self):
        Account.main()

    def quiz09gugudan(self):  # 책받침구구단
        res = ""
        for i in [2, 6]:
            for j in range(1, 10):
                for k in range(0, 4):
                    res += f'{i + k} * {j} = {(i + k) * j}\t'
                res += '\n'
            res += '\n'
        print(res)
        return None

'''
은행 이름은 비트은행
입금자 이름(name), 계좌번호(account_number), 금액(money) 속성값으로 계좌를 생성한다.
계좌번호는 3자리-2자리-6자리 형태로 랜덤하게 생성된다.
ex ) 123-12-123456
금액은 100만원 ~ 999만원 사이로 랜덤하게 입금된다.
'''

class Account(object):
    def __init__(self, name, account_number, money):
        self.BANK_NAME = '비트은행'
        self.name = myMember() if name == None else name
        # number = f'{myRandom(0, 99999999999):0>11}'
        # self.account_number = f'{number[:3]}-{number[3:5]}-{number[5:]}'
        self.account_number = Account.creat_account_number(self) if account_number == None else account_number
        self.money = myRandom(100, 999) if money == None else money

    def to_string(self):
        an = self.account_number
        return f'은행: {self.BANK_NAME}, ' \
               f'입금자: {self.name}, ' \
               f'계좌번호: {self.account_number}, ' \
               f'금액: {self.money}'

    def creat_account_number(self):
        # ls = [str(myRandom(1, 9)) for i in range(3)]
        # ls += '-'
        # ls += [str(myRandom(1, 9)) for i in range(2)]
        # ls += '-'
        # ls += [str(myRandom(1, 9)) for i in range(6)]
        # return "".join(ls)
        return "".join([str(myRandom(1, 9)) if i != 3 and i != 6 else '-' for i in range(13)])

    @staticmethod
    def del_account(ls, account_number):
        for i, j in enumerate(ls):
            if j.account_number == account_number:
                del ls[i]

    @staticmethod
    def find_account(ls, account_number):
        # return ''.join([j.to_string() if j.account_number == account_number else '찾는 계좌 아님' for i, j in enumerate(ls)])
        for i, j in enumerate(ls):
            if j.account_number == account_number:
                return ls[i]

    @staticmethod
    def deposit(ls, account_number, add):
        for i, j in enumerate(ls):
            if j.account_number == account_number:
                ls[i].money = ls[i].money + add

    @staticmethod
    def withdrawal(ls, account_number, sub):
        for i, j in enumerate(ls):
            if j.account_number == account_number:
                ls[i].money = ls[i].money - sub

    @staticmethod
    def main():
        ls = []
        while 1 :
            menu = input('0.종료 1.계좌개설 2.계좌목록 3.입금 4.출급 5.계좌해지 6.계좌금액조회')
            if menu == '0':
                break
            elif menu == '1':
                acc = Account(None, None, None)
                print(f'{acc.to_string()}... 개설되었습니다.')
                ls.append(acc)
            elif menu == '2':
                print('\n'.join(i.to_string() for i in ls))
            elif menu == '3':
                Account.deposit(ls, input('입금 할 계좌번호'), int(input('입금액')))
            elif menu == '4':
                Account.withdrawal(ls, input('출금 할 계좌번호'), int(input('출금액')))
            elif menu == '5':
                Account.del_account(ls, input('탈퇴할 계좌번호'))
            elif menu == '6':
                a = Account.find_account(ls, input('조회 할 계좌번호'))
                print(a.to_string())
            else:
                print('WRONG NUMBER... Try Again')

