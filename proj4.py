import csv
import random
import tkinter as tk
from tkinter import messagebox

"""
한자 퀴즈 프로그램
---------------
급수별 한자 데이터가 DataManager에 저장되어 있다.(4~8급)
QuizManager로 문제를 출제하며 UIManager로 GUI를 표현한다.
결과는 ResultManager에서 관리한다.

"""


# 문제 관련 - 맨 위로 이동
class Question:
    def __init__(self, character: str, pronunciation: str, meaning: str):
        self.character = character
        self.pronunciation = pronunciation
        self.meaning = meaning

    def check_answer(self, answer: str) -> bool:
        return (answer == self.meaning
                or answer == self.pronunciation
                or answer == self.pronunciation + '/' + self.meaning)

    def generate_options(self, all_list: list, num_options=4):
        if num_options > len(all_list):
            return ValueError("가능한 보기 개수를 초과하였습니다")

        filtered_list = [data for data in all_list if data.get("한자") != self.character]
        return random.sample(filtered_list, num_options - 1)  # 정답 요소는 제외


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
        self.current_question = 0
        self.total_questions = 0
        self.quiz_list = []

    def load_data_from_db(self, level: str):
        for db in DataManager.all_DB:
            if db.level == level:
                self.hanja_list.extend(db.hanja_list)
        print(self.hanja_list)
        if len(self.hanja_list) == 0:
            raise ValueError("해당 급수의 데이터는 존재하지 않습니다.")

    def load_data_from_list(self, hanja_list: list):
        self.hanja_list = hanja_list

    def start_quiz(self, num_quiz: int):
        """퀴즈 시작"""
        if num_quiz > len(self.hanja_list):
            raise ValueError("개수를 초과하였습니다")

        self.current_question = 0
        self.total_questions = num_quiz
        self.result_manager = ResultManager()

        # 문제 리스트 생성
        shuffled_list = self.hanja_list.copy()
        random.shuffle(shuffled_list)
        self.quiz_list = shuffled_list[:num_quiz]

        self.result_manager.set_total_questions(num_quiz)

    def get_next_question(self) -> Question:
        """다음 문제 가져오기"""
        if self.current_question >= self.total_questions:
            raise ValueError("모든 문제를 다 풀었습니다")

        question = self.quiz_list[self.current_question]
        self.current_question += 1
        return Question(question['한자'], question['음'], question['뜻'])

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
        return (self.correct_count / self.total_questions) * 100

    # 정답 개수와 전체 문제 수를 반환
    def get_results(self) -> dict:
        return {"correct": self.correct_count, "total": self.total_questions}


# GUI 띄우기
class UIManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("한자 급수 QUIZ")
        self.root.geometry("800x600")
        self.root.configure(bg="#B1D095")

        self.quiz_manager = QuizManager()
        self.main_frame = tk.Frame(self.root, bg="#B1D095")
        self.main_frame.pack(fill="both", expand=True)

    def clear_frame(self):
        """프레임 내의 모든 위젯 제거"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        """메인 메뉴 화면"""
        self.clear_frame()

        title = tk.Label(
            self.main_frame,
            text="한자 급수\nQUIZ",
            font=("Arial", 64, "bold"),
            bg="#B1D095",
            fg="black"
        )
        title.pack(pady=(180, 0))

        start_button = tk.Button(
            self.main_frame,
            text="시작",
            font=("Arial", 16, "bold"),
            command=self.select_level,
            width=20,
            height=2,
            bg="#548235",
            fg="black"
        )
        start_button.pack(pady=(20, 0))

    def select_level(self):
        """급수 선택 화면"""
        self.clear_frame()

        title_label = tk.Label(
            self.main_frame,
            text="급수를 선택하세요",
            font=("Arial", 36, "bold"),
            bg="#B1D095",
            fg="black"
        )
        title_label.pack(pady=(100, 50))

        # 버튼을 담을 프레임들 생성
        button_frame1 = tk.Frame(self.main_frame, bg="#B1D095")
        button_frame1.pack(pady=10)

        button_frame2 = tk.Frame(self.main_frame, bg="#B1D095")
        button_frame2.pack(pady=10)

        # 상단 줄에 9, 8, 7급 버튼
        levels_top = ['level9', 'level8', 'level7']
        for level in levels_top:
            display_text = f"{level[-1]}급"
            level_button = tk.Button(
                button_frame1,
                text=display_text,
                font=("Arial", 16, "bold"),
                command=lambda l=level: self.select_question_count(l),
                width=8,
                height=2,
                bg="#548235",
                fg="black"
            )
            level_button.pack(side=tk.LEFT, padx=10)

        # 하단 줄에 6, 5, 4급 버튼
        levels_bottom = ['level6', 'level5', 'level4']
        for level in levels_bottom:
            display_text = f"{level[-1]}급"
            level_button = tk.Button(
                button_frame2,
                text=display_text,
                font=("Arial", 16, "bold"),
                command=lambda l=level: self.select_question_count(l),
                width=8,
                height=2,
                bg="#548235",
                fg="black"
            )
            level_button.pack(side=tk.LEFT, padx=10)

    def select_question_count(self, level):
        """문제 개수 선택 화면"""
        self.clear_frame()

        try:
            self.quiz_manager.load_data_from_db(level)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.select_level()
            return

        title_label = tk.Label(
            self.main_frame,
            text="문제 개수를 입력하세요",
            font=("Arial", 36, "bold"),
            bg="#B1D095",
            fg="black"
        )
        title_label.pack(pady=(100, 20))

        # 급수별 최대 문제 개수 안내
        info_text = "(각 급수별 최대 문제 개수)\n" + \
                    "9급: 50개\n" + \
                    "8급: 100개\n" + \
                    "7급: 150개\n" + \
                    "6급: 150개\n" + \
                    "5급: 150개\n" + \
                    "4급: 200개"

        info_label = tk.Label(
            self.main_frame,
            text=info_text,
            font=("Arial", 14),
            bg="#B1D095",
            fg="black"
        )
        info_label.pack(pady=(0, 30))

        self.count_entry = tk.Entry(
            self.main_frame,
            font=("Arial", 20, "bold"),
            width=10
        )
        self.count_entry.pack(pady=20)

        start_button = tk.Button(
            self.main_frame,
            text="시작하기",
            font=("Arial", 16, "bold"),
            command=lambda: self.start_quiz(int(self.count_entry.get())),
            bg="#548235",
            fg="black"
        )
        start_button.pack(pady=20)

    def start_quiz(self, question_count):
        """퀴즈 시작"""
        try:
            self.quiz_manager.start_quiz(question_count)
            # 첫 문제를 가져와서 display_question에 전달
            first_question = self.quiz_manager.get_next_question()
            self.display_question(first_question)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.select_level()

    def display_question(self, question: Question):
        """문제 표시"""
        self.clear_frame()

        question_label = tk.Label(
            self.main_frame,
            text=f"다음 한자의 음과 뜻을 입력하세요:\n{question.character}",
            font=("Arial", 36, "bold"),
            bg="#B1D095",
            fg="black"
        )
        question_label.pack(pady=(100, 20))

        # 입력 형식 안내
        format_label = tk.Label(
            self.main_frame,
            text="(음/뜻 형식으로 입력하세요)",
            font=("Arial", 14),
            bg="#B1D095",
            fg="black"
        )
        format_label.pack(pady=(0, 30))

        # 결과 표시 레이블 추가
        self.result_label = tk.Label(
            self.main_frame,
            text="",
            font=("Arial", 20, "bold"),
            bg="#B1D095",
            fg="black"
        )
        self.result_label.pack(pady=10)

        self.answer_entry = tk.Entry(
            self.main_frame,
            font=("Arial", 20, "bold"),
            width=20
        )
        self.answer_entry.pack(pady=20)
        self.answer_entry.focus()  # 자동으로 입력 포커스

        # Enter 키 바인딩 추가
        self.answer_entry.bind('<Return>', lambda e: self.check_answer(question))

        submit_button = tk.Button(
            self.main_frame,
            text="제출",
            font=("Arial", 16, "bold"),
            command=lambda: self.check_answer(question),
            bg="#548235",
            fg="black"
        )
        submit_button.pack(pady=20)

    def check_answer(self, question: Question):
        """답안 확인"""
        answer = self.answer_entry.get()
        self.answer_entry.delete(0, tk.END)  # 입력 필드 초기화

        if question.check_answer(answer):
            self.quiz_manager.result_manager.record_correct_num()
            self.result_label.config(
                text="정답입니다!",
                fg="#2F9D27"  # 초록색
            )
        else:
            self.quiz_manager.result_manager.record_wrong_answer({
                "한자": question.character,
                "음": question.pronunciation,
                "뜻": question.meaning
            })
            self.result_label.config(
                text=f"오답입니다.\n정답: {question.pronunciation}/{question.meaning}",
                fg="#FF0000"  # 빨간색
            )

        # 1초 후 다음 문제로 이동
        self.root.after(1000, self.display_next_question)

    def display_next_question(self):
        """다음 문제 표시 또는 결과 화면으로 이동"""
        if self.quiz_manager.current_question < self.quiz_manager.total_questions:
            self.display_question(self.quiz_manager.get_next_question())
        else:
            self.show_final_results()

    def show_final_results(self):
        """최종 결과 화면"""
        self.clear_frame()

        results = self.quiz_manager.result_manager.get_results()
        correct_rate = self.quiz_manager.result_manager.get_correct_rate()

        result_label = tk.Label(
            self.main_frame,
            text=f"결과: {results['correct']}/{results['total']}\n정답률: {correct_rate:.1f}%",
            font=("Arial", 36, "bold"),
            bg="#B1D095",
            fg="black"
        )
        result_label.pack(pady=(100, 50))

        retry_button = tk.Button(
            self.main_frame,
            text="다시 도전",
            font=("Arial", 16),
            command=self.select_level,
            bg="#548235",
            fg="black"
        )
        retry_button.pack(pady=20)

        if len(self.quiz_manager.result_manager.wrong_answers) > 0:
            wrong_button = tk.Button(
                self.main_frame,
                text="오답 다시 풀기",
                font=("Arial", 16),
                command=self.retry_wrong_answers,
                bg="#548235",
                fg="black"
            )
            wrong_button.pack(pady=20)

    def retry_wrong_answers(self):
        """오답 다시 풀기"""
        try:
            # 새로운 QuizManager 생성
            wrong_quiz_manager = QuizManager()
            wrong_quiz_manager.load_data_from_list(self.quiz_manager.result_manager.wrong_answers)

            # 기존 QuizManager를 새로운 것으로 교체
            self.quiz_manager = wrong_quiz_manager

            # 오답 문제들로 새로운 퀴즈 시작
            self.quiz_manager.start_quiz(len(self.quiz_manager.hanja_list))

            # 첫 문제 표시
            first_question = self.quiz_manager.get_next_question()
            self.display_question(first_question)

        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.select_level()

    def run(self):
        """GUI 실행"""
        self.create_main_menu()
        self.root.mainloop()


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
    # DB 형성 - 4-9급만 로드
    level9 = DataManager()
    level9.load('level9.csv')

    level8 = DataManager()
    level8.load('level8.csv')

    level7 = DataManager()
    level7.load('level7.csv')

    level6 = DataManager()
    level6.load('level6.csv')

    level5 = DataManager()
    level5.load('level5.csv')

    level4 = DataManager()
    level4.load('level4.csv')

    # GUI 실행
    ui = UIManager()
    ui.run()


if __name__ == "__main__":
    main()