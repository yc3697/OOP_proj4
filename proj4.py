import csv

"""
한자 퀴즈 프로그램
---------------
급수별 한자 데이터가 DataManager에 저장되어 있다.(4~8급)
QuizManager로 문제를 출제하며 UIManager로 GUI를 표현한다.
결과는 ResultManager에서 관리한다.

"""


# 한자 데이터 DB
class DataManager:
    def __init__(self):
        self.level: str = ""
        self.hanja_list = []

    def load(self, filename: str):
        pass


# 퀴즈 관리
class QuizManager:
    def __init__(self):
        self.hanja_list = []
        self.result_manager = ResultManager()

    def load_questions(self, questions: list):
        pass

    def start_quiz(self, hanja_list, type_question):
        pass

    def ask_questions(self, question: dict):
        pass

    def check_answer(self, input_answer):
        pass

    def retry_wrong_answers(self):
        pass

    def get_results(self) -> dict:
        pass


# 결과 저장
class ResultManager:
    def __init__(self):
        self.total_questions = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.wrong_answers = []

    def record_correct_answer(self, correct: dict):
        pass

    def record_wrong_answer(self, wrong: dict):
        pass

    def set_results(self, correct: int, total: int):
        pass

    def get_correct_rate(self) -> float:
        pass

    def get_results(self) -> dict:
        pass


# 문제 관련
class Question:
    def __init__(self, character: str, meaning: str, pronunciation: str):
        self.character = character
        self.meaning = meaning
        self.pronunciation = pronunciation

    def check_answer(self, answer: str) -> bool:
        pass

    def generate_options(self, all_list, num_options=4):
        pass


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

    def select_menu(self) -> int:
        pass


def main():
    pass


if __name__ == "__main__":
    main()