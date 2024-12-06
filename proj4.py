import csv
import random
import tkinter as tk
from tkinter import messagebox

"""
한자 퀴즈 프로그램
---------------
급수별 한자 데이터가 DataManager에 저장되어 있다.(4~9급)
QuizManager로 문제를 출제하며 QuizGui로 GUI를 표현한다.
결과는 ResultManager에서 관리한다.
"""

# 한자 데이터 DB
class DataManager:
    all_DB = []

    @classmethod
    def load_all_levels(cls):
        """모든 급수의 데이터 로드"""
        for level in range(4, 10):
            db = cls()
            db.load(f'level{level}.csv')

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
        self.is_wrong_answer_mode = False
        self.quiz_list = []

    def load_data_from_db(self, level: str):
        self.hanja_list = []  # 리스트 초기화
        for db in DataManager.all_DB:
            if db.level == level:
                # extend 대신 리스트를 복사해서 추가
                self.hanja_list.extend(db.hanja_list.copy())
        if len(self.hanja_list) == 0:
            raise ValueError("해당 급수의 데이터는 존재하지 않습니다.")
        # 리스트를 섞어서 저장
        random.shuffle(self.hanja_list)

    def load_data_from_list(self, hanja_list: list):
        self.hanja_list = hanja_list

    def start_quiz(self, num_quiz: int):
        if num_quiz > len(self.hanja_list):
            raise ValueError("개수를 초과하였습니다")
        self.current_question = 0
        self.total_questions = num_quiz

        if self.is_wrong_answer_mode:
            self.quiz_list = self.hanja_list[:num_quiz]
        else:
            self.result_manager = ResultManager()
            shuffled_list = self.hanja_list.copy()
            random.shuffle(shuffled_list)
            self.quiz_list = shuffled_list[:num_quiz]

        self.result_manager.set_total_questions(num_quiz)

    def get_next_question(self) -> 'Question':
        if self.current_question >= self.total_questions:
            raise ValueError("모든 문제를 다 풀었습니다")

        question = self.quiz_list[self.current_question]
        self.current_question += 1
        return Question(question['한자'], question['뜻'], question['음'])

    def create_wrong_answer_quiz(self) -> 'QuizManager':
        """오답 노트용 새 QuizManager 생성"""
        # 중복 제거된 틀린 문제 리스트 생성
        unique_wrong_answers = []
        seen_hanja = set()

        for wrong in self.result_manager.wrong_answers:
            if wrong['한자'] not in seen_hanja:
                unique_wrong_answers.append(wrong)
                seen_hanja.add(wrong['한자'])

        wrong_answer_notes = QuizManager()
        wrong_answer_notes.is_wrong_answer_mode = True
        wrong_answer_notes.load_data_from_list(unique_wrong_answers)  # 중복 제거된 리스트 사용
        wrong_answer_notes.start_quiz(len(unique_wrong_answers))
        return wrong_answer_notes


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

    def get_results(self) -> dict:
        return {"correct": self.correct_count, "total": self.total_questions}


# 문제 관련
class Question:
    def __init__(self, character: str, meaning: str, pronunciation: str):
        self.character = character
        self.meaning = meaning
        self.pronunciation = pronunciation

    # 뜻과 음이 모두 맞을 경우에만 true 반환
    def check_answer(self, answer: str) -> bool:
        try:
            meaning, pronunciation = answer.split()  # 공백으로 분리
            return meaning == self.meaning and pronunciation == self.pronunciation
        except ValueError:  # 공백이 없거나 공백이 여러 개인 경우
            return False


# GUI 띄우기
class QuizGui:
    def __init__(self, root):
        self.root = root
        self.root.title("한자 급수 QUIZ")
        self.root.geometry("800x600")
        self.root.configure(bg="#B1D095")

        self.main_frame = tk.Frame(self.root, bg="#B1D095")
        self.main_frame.pack(fill="both", expand=True)

        self.quiz_manager = QuizManager()
        self.create_main_menu()

    def clear_frame(self):
        """프레임 내의 모든 위젯 제거"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        """메인 메뉴 화면 표시"""
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
            fg="black",
            relief="flat",
            highlightthickness=0,
            bd=0,
        )
        start_button.pack(pady=(20, 0))

        def on_enter(e):
            start_button.configure(bg="#2F9D27")

        def on_leave(e):
            start_button.configure(bg="#58623F")

        start_button.bind("<Enter>", on_enter)
        start_button.bind("<Leave>", on_leave)

    def select_level(self):
        """급수 선택 화면"""
        self.clear_frame()

        # 새로운 QuizManager 생성하여 모든 결과 초기화
        self.quiz_manager = QuizManager()

        title_label = tk.Label(
            self.main_frame,
            text="급수를 선택하세요",
            font=("Arial", 36, "bold"),
            bg="#B1D095",
            fg="black"
        )
        title_label.pack(pady=(100, 50))

        button_frame = tk.Frame(self.main_frame, bg="#B1D095")
        button_frame.pack(pady=20)

        for level in ['4급', '5급', '6급', '7급', '8급', '9급']:
            level_button = tk.Button(
                button_frame,
                text=level,
                font=("Arial", 16, "bold"),
                width=8,
                height=2,
                bg="#548235",
                fg="black",
                command=lambda l=level: self.choose_problem_count(l)
            )
            level_button.pack(side=tk.LEFT, padx=10)

    def choose_problem_count(self, level):
        """문제 개수 선택 화면"""
        self.clear_frame()
        selected_level = f'level{level.replace("급", "")}'

        try:
            self.quiz_manager.load_data_from_db(selected_level)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.select_level()
            return

        title_label = tk.Label(
            self.main_frame,
            text="도전할 문제의 개수를 선택하시오",
            font=("Arial", 36, "bold"),
            bg="#B1D095",
            fg="black"
        )
        title_label.pack(pady=(200, 0))

        subtitle_label = tk.Label(
            self.main_frame,
            text="(숫자만 입력하시오.  9급 : 50개, 8급 : 100개, 7급 : 150개,\n6급 : 150개, 5급 : 150개, 4급 : 200개)",
            font=("Arial", 20),
            bg="#B1D095",
            fg="black"
        )
        subtitle_label.pack(pady=(20, 50))

        entry_frame = tk.Frame(
            self.main_frame,
            bg="#B1D095"
        )
        entry_frame.pack(pady=20)

        self.problem_count_entry = tk.Entry(
            entry_frame,
            font=("Arial", 16),
            width=30,
            justify='center'
        )
        self.problem_count_entry.pack()

        underline = tk.Frame(
            entry_frame,
            height=2,
            bg="black"
        )
        underline.pack(fill='x', pady=(0, 20))

        level_num = int(level.replace('급', ''))

        def press_enter(event):
            count = self.problem_count_entry.get()
            if count.isdigit():
                count = int(count)
                max_problems = {
                    9: 50,
                    8: 100,
                    7: 150,
                    6: 150,
                    5: 150,
                    4: 200
                }
                if 1 <= count <= max_problems[level_num]:
                    self.start_quiz(count)
                else:
                    messagebox.showerror("오류", f"{level_num}급의 최대 문제 개수는 {max_problems[level_num]}개입니다.")
            else:
                messagebox.showerror("오류", "숫자만 입력해주세요.")

        self.problem_count_entry.bind('<Return>', press_enter)
        self.problem_count_entry.focus()

    def start_quiz(self, num_questions):
        """퀴즈 시작"""
        try:
            self.quiz_manager.start_quiz(num_questions)
            self.show_question()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.select_level()

    def show_question(self):
        """문제 화면 표시"""
        self.clear_frame()

        try:
            question = self.quiz_manager.get_next_question()

            question_label = tk.Label(
                self.main_frame,
                text="다음 한자의 뜻/음을 입력하세요:",
                font=("Arial", 24, "bold"),
                bg="#B1D095",
                fg="black"
            )
            question_label.pack(pady=(50, 20))

            format_label = tk.Label(
                self.main_frame,
                text="(뜻 음 형식으로 입력하세요. 예: 한 일)",
                font=("Arial", 16),
                bg="#B1D095",
                fg="black"
            )
            format_label.pack(pady=(0, 20))

            hanja_label = tk.Label(
                self.main_frame,
                text=question.character,
                font=("Arial", 70),
                bg="#B1D095",
                fg="black"
            )
            hanja_label.pack(pady=20)

            # 결과 표시 레이블 추가
            self.result_label = tk.Label(
                self.main_frame,
                text="",
                font=("Arial", 20),
                bg="#B1D095",
                fg="black"
            )
            self.result_label.pack(pady=10)

            self.answer_entry = tk.Entry(
                self.main_frame,
                font=("Arial", 14),
                width=30,
                justify='center'
            )
            self.answer_entry.pack(pady=10)
            self.answer_entry.focus()

            self.answer_entry.bind('<Return>', lambda e: self.check_answer(question))

        except ValueError:
            self.show_result()

    def check_answer(self, question):
        """답안 체크"""
        user_answer = self.answer_entry.get()
        self.answer_entry.delete(0, tk.END)

        if question.check_answer(user_answer):
            self.quiz_manager.result_manager.record_correct_num()
            self.result_label.config(text="정답입니다!", fg="#2F9D27")
        else:
            self.quiz_manager.result_manager.record_wrong_answer({
                '한자': question.character,
                '뜻': question.meaning,
                '음': question.pronunciation
            })
            self.result_label.config(
                text=f"오답입니다.\n정답은 {question.meaning} {question.pronunciation} 입니다.",
                fg="#FF0000"  # 빨간색으로 표시
            )

        self.root.after(1000, self.show_question)  # 1초 후 다음 문제로

    def show_result(self):
        """결과 화면 표시"""
        self.clear_frame()

        results = self.quiz_manager.result_manager.get_results()
        correct_rate = self.quiz_manager.result_manager.get_correct_rate()

        result_text = f"결과: {results['correct']}/{results['total']}\n정답률: {correct_rate:.1f}%"

        result_label = tk.Label(
            self.main_frame,
            text=result_text,
            font=("Arial", 36, "bold"),
            bg="#B1D095",
            fg="black"
        )
        result_label.pack(pady=(100, 50))

        button_frame = tk.Frame(self.main_frame, bg="#B1D095")
        button_frame.pack(pady=20)

        retry_button = tk.Button(
            button_frame,
            text="다시 도전",
            font=("Arial", 16, "bold"),
            width=12,
            height=2,
            bg="#548235",
            fg="black",
            command=self.select_level
        )
        retry_button.pack(side=tk.LEFT, padx=10)

        if len(self.quiz_manager.result_manager.wrong_answers) > 0:
            wrong_button = tk.Button(
                button_frame,
                text="오답 다시 풀기",
                font=("Arial", 16, "bold"),
                width=12,
                height=2,
                bg="#548235",
                fg="black",
                command=self.retry_wrong_answers
            )
            wrong_button.pack(side=tk.LEFT, padx=10)

        # 종료 버튼 추가
        exit_button = tk.Button(
            button_frame,
            text="종료",
            font=("Arial", 16, "bold"),
            width=12,
            height=2,
            bg="#548235",
            fg="black",
            command=self.root.destroy  # 프로그램 종료
        )
        exit_button.pack(side=tk.LEFT, padx=10)

    def retry_wrong_answers(self):
        """오답 다시 풀기"""
        try:
            self.quiz_manager = self.quiz_manager.create_wrong_answer_quiz()
            self.show_question()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.select_level()


def main():
    # DB 형성
    DataManager.load_all_levels()

    # GUI 실행
    root = tk.Tk()
    app = QuizGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()