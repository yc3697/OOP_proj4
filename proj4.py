import csv
import random

"""
한자 퀴즈 프로그램
---------------
급수별 한자 데이터가 DataManager에 저장되어 있다.(4~8급)
QuizManager로 문제를 출제하며 UIManager로 GUI를 표현한다.
결과는 ResultManager에서 관리한다.

"""


# 한자 데이터 DB
class DataManager:
    all_DB = []

    def __init__(self):
        self.level: str = ""
        self.hanja_list = []
        DataManager.all_DB.append(self)

    def load(self, filename: str):
        self.level = filename[0:-4]

        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.hanja_list.append(row)


# 퀴즈 관리
class QuizManager:
    def __init__(self):
        self.hanja_list = []
        self.result_manager = ResultManager()

    def load_data_from_db(self, level: str):
        for db in DataManager.all_DB:
            if db.level == level:
                self.hanja_list.extend(db.hanja_list)
        print(self.hanja_list)
        if len(self.hanja_list) == 0:
            raise ValueError("해당 급수의 데이터는 존재하지 않습니다.")

    def load_data_from_list(self, hanja_list: list):
        self.hanja_list = hanja_list

    def start_quiz(self, num_quiz: int, type_question: str = "주관식"):

        if num_quiz > len(self.hanja_list):
            raise ValueError("개수를 초과하였습니다")
        else:
            self.result_manager.set_total_questions(num_quiz)

        if type_question == "주관식":
            # 랜덤 인덱스로 참고해서 데이터 얻어와서 Question 객체 생성 .. num_quiz 만큼 반복하면서 ask랑 check
            for i in range(0, num_quiz):
                # 문제 생성
                random_index = random.randint(0, len(self.hanja_list) - 1)
                print(random_index)
                random_question = self.hanja_list[random_index]
                print(random_question)
                question = Question(random_question['한자'], random_question['음'], random_question['뜻'])

                # 질문
                self.ask_questions(question)

                # 정답 확인 및 결과 처리
                user_answer = input("음/뜻을 입력하시오 (e.g. 하늘/천)")
                if question.check_answer(user_answer):
                    print("정답입니다")
                    self.result_manager.record_correct_num()
                else:
                    print("오답입니다")
                    self.result_manager.record_wrong_answer(random_question)

        # 추후 구현
        # elif type_question == "객관식":
        # # 방식 위랑 동일하고 generate_options()도 같이

        else:
            raise ValueError("잘못된 문제 입력입니다")

    def ask_questions(self, question: 'Question'):
        print(question.character)
    def retry_wrong_answers(self):
        wrong_answer_notes = QuizManager()
        wrong_answer_notes.load_data_from_list(self.result_manager.wrong_answers)
        print("오답 노트", wrong_answer_notes.hanja_list)
        wrong_answer_notes.start_quiz(len(self.result_manager.wrong_answers))


# 결과 저장
class ResultManager:
    def __init__(self):
        self.total_questions = 0
        self.correct_count = 0
        self.wrong_answers = []

    def set_total_questions(self, num_total: int):
        self.total_questions = num_total

    def record_correct_num(self):
        self.correct_count += 1

    def record_wrong_answer(self, wrong: dict):
        self.wrong_answers.append(wrong)

    def get_correct_rate(self) -> float:
        return (self.correct_count/self.total_questions)*100

    # 정답 개수와 전체 문제 수를 반환
    def get_results(self) -> dict:
        return {"correct": self.correct_count, "total": self.total_questions}


# 문제 관련
class Question:
    def __init__(self, character: str, pronunciation: str, meaning: str):
        self.character = character
        self.pronunciation = pronunciation
        self.meaning = meaning

    # 뜻이나 음, 혹은 두 가지 모두 맞을 경우 true 반환
    def check_answer(self, answer: str) -> bool:
        return (answer == self.meaning
                or answer == self.pronunciation
                or answer == self.pronunciation+'/'+self.meaning)

    # 해당 한자를 제외한 나머지 리스트에서 원하는 수만큼 랜덤 보기를 생성하여 반환
    def generate_options(self, all_list: list, num_options=4):
        if num_options > len(all_list):
            return ValueError("가능한 보기 개수를 초과하였습니다")

        filtered_list = [data for data in all_list if data.get("한자") != self.character]
        return random.sample(filtered_list, num_options-1)  # 정답 요소는 제외


# GUI 띄우기
class UIManager:
    def create_main_menu(self):
        pass

    def display_question(self, question: Question):
        pass

    def display_result(self, correct: bool, question: Question):
        pass

    def show_final_results(self, correct_count: int, total_questions: int):
        pass

    def select_menu(self):
        """
        다른 급수 풀어보기 : 급수 선택 창 띄워서 load_data_from_db(급수)로 세팅 후 start_quiz()
        틀린 문제 다시 풀어보기 : retry_wrong_answers()
        종료 : 종료
        """
        pass


# 내부 로직 흐름 파악용(실행 흐름 참고)
def process():
    test: QuizManager = QuizManager()
    while True:
        try:
            level = input("급수 입력(e.g. 4급 = level4, 준4급 = level4_semi): ")
            test.load_data_from_db(level)
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        try:
            num_prob = int(input("문제 개수 입력(e.g. 100): "))
            test.start_quiz(num_prob)
            break
        except ValueError as e:
            print(f"Error: {e}")

    print(test.result_manager.get_results())

    while True:
        print("옵션 입력")
        print("1. 처음부터 도전(!!!기존 내용은 초기화 됩니다!!!)")
        print("2. 틀린 문제 다시 풀어보기")
        print("3. 종료")

        options = int(input("옵션 번호 입력: "))

        if options == 1:
            process()
            break
        elif options == 2:
            test.retry_wrong_answers()
        elif options == 3:
            break
        else:
            print("잘못된 입력")
            continue

    return


def main():
    ## 내부 로직 테스트

    # DB 형성
    level8 = DataManager()
    level8.load('level8.csv')

    level7 = DataManager()
    level7.load('level7.csv')

    level6 = DataManager()
    level6.load('level6.csv')

    level5 = DataManager()
    level5.load('level5.csv')

    level5_semi = DataManager()
    level5_semi.load('level5_semi.csv')

    level4 = DataManager()
    level4.load('level4.csv')

    level4_semi = DataManager()
    level4_semi.load('level4_semi.csv')

    # 실행
    process()


if __name__ == "__main__":
    main()