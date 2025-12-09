import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import requests
import os

# =========================================================
#             AI-Assisted Text Editor (Final Update)
# =========================================================

class AITextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Assisted Text Editor")
        self.root.geometry("900x650")

        self.current_file = None

        self.create_menu()
        self.create_text_area()
        self.create_context_menu()

    # -----------------------------------------------------
    # Menu Section
    # -----------------------------------------------------
    def create_menu(self):
        menubar = tk.Menu(self.root)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit Menu (복구됨)
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=lambda: self.text_area.event_generate("<<Undo>>"))
        edit_menu.add_command(label="Redo", command=lambda: self.text_area.event_generate("<<Redo>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menubar)

    # -----------------------------------------------------
    # Text Area + Scrollbar
    # -----------------------------------------------------
    def create_text_area(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(frame, wrap="word", undo=True)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area.config(yscrollcommand=scrollbar.set)

        # Right-click event binding
        self.text_area.bind("<Button-3>", self.show_context_menu)

    # -----------------------------------------------------
    # Right-click / Context Menu
    # -----------------------------------------------------
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="AI에게 질문하기", command=self.open_ai_popup)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # -----------------------------------------------------
    # AI LLM Function (Ollama)
    # -----------------------------------------------------
    def ask_llm(self, selected_text, question):
        prompt = f"""
[Selected Text]
{selected_text}

[User Question]
{question}

Provide the best possible answer based strictly on the content above.
"""

        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3:8b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )

            data = response.json()
            return data.get("response", "(no response)")

        except Exception as e:
            return f"Error contacting LLM:\n{e}"

    # -----------------------------------------------------
    # AI Popup
    # -----------------------------------------------------
    def open_ai_popup(self):
        # 선택된 텍스트 없으면 안내
        try:
            selected_text = self.text_area.get("sel.first", "sel.last")
        except:
            messagebox.showinfo("Notice", "먼저 텍스트를 드래그하세요.")
            return

        popup = tk.Toplevel(self.root)
        popup.title("AI에게 질문하기")
        popup.geometry("600x500")

        tk.Label(popup, text="선택한 텍스트:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10)
        selected_box = tk.Text(popup, height=6)
        selected_box.pack(fill=tk.X, padx=10)
        selected_box.insert(tk.END, selected_text)

        tk.Label(popup, text="AI에게 물어볼 질문:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        question_box = tk.Text(popup, height=3)
        question_box.pack(fill=tk.X, padx=10)

        tk.Label(popup, text="AI 응답:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        answer_box = tk.Text(popup, height=15)
        answer_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def ask_ai():
            question = question_box.get("1.0", tk.END).strip()
            if not question:
                messagebox.showinfo("Notice", "질문을 입력하세요.")
                return

            answer_box.delete("1.0", tk.END)
            answer_box.insert(tk.END, "AI 응답 생성 중...\n")

            result = self.ask_llm(selected_text, question)

            answer_box.delete("1.0", tk.END)
            answer_box.insert(tk.END, result)

        tk.Button(popup, text="AI에게 질문하기", command=ask_ai).pack(pady=10)

    # -----------------------------------------------------
    # File Functions
    # -----------------------------------------------------
    def new_file(self):
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.root.title("AI-Assisted Text Editor - New File")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")
            return

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, content)
        self.current_file = file_path
        self.root.title(f"AI-Assisted Text Editor - {os.path.basename(file_path)}")

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    content = self.text_area.get("1.0", tk.END)
                    f.write(content)
                messagebox.showinfo("Saved", "File saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                content = self.text_area.get("1.0", tk.END)
                f.write(content)
            self.current_file = file_path
            self.root.title(f"AI-Assisted Text Editor - {os.path.basename(file_path)}")
            messagebox.showinfo("Saved", "File saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AITextEditor(root)
    root.mainloop()
