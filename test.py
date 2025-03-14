


import xml.etree.ElementTree as ET
import tkinter as tk
import re
from tkinter import ttk, filedialog

# Global (or class-level) reference to all question elements
all_questions = []

def lese_xml_datei(dateipfad):
    try:
        tree = ET.parse(dateipfad)
        root = tree.getroot()
        return root.iter('question')
    except FileNotFoundError:
        print(f"Fehler: Datei '{dateipfad}' nicht gefunden.")
        return None
    except ET.ParseError:
        print(f"Fehler: Fehler beim Parsen der XML-Datei '{dateipfad}'.")
        return None


def waehle_datei():
    # Parse XML
    dateipfad = filedialog.askopenfilename(
        title="XML-Datei auswählen",
        filetypes=[("XML-Dateien", "*.xml")]
    )
    if dateipfad:
        fragen = lese_xml_datei(dateipfad)
        # "fragen" is now an iterator of all <question> elements
        if fragen:
            # Clear the tree and the global list
            for row in tree_display.get_children():
                tree_display.delete(row)
            all_questions.clear()

            for frage in fragen:
                kategorie = frage.get("type")
                name_object = frage.find('name')
                if name_object:
                    name = name_object.find('text').text
                    # Keep a reference to the entire question element:
                    all_questions.append(frage)
                    # Insert into TreeView using the index as iid
                    current_index = len(all_questions) - 1
                    tree_display.insert(
                        "",
                        "end",
                        iid=current_index,
                        values=(name, kategorie)
                    )
    else:
        print("Keine Datei ausgewählt.")

def get_selected_items():
    selected = tree_display.selection()
    if not selected:
        print("Keine Zeile ausgewählt.")
        return

    details_window = tk.Toplevel(root)
    details_window.title("Frage beantworten")

    row = 0
    user_answers = {}  # Speichert die Nutzerantworten

    for item_id in selected:
        question_index = int(item_id)
        frage_element = all_questions[question_index]

        # Name der Frage
        name_obj = frage_element.find('name')
        question_name = name_obj.find('text').text if name_obj is not None else "—"

        # Frage-Text
        question_text_elem = frage_element.find('questiontext')
        question_text = remove_html_tags(question_text_elem.find('text').text) if question_text_elem is not None else "—"

        # Frage-Typ
        question_type = frage_element.get("type", "Unbekannt")

        # Name anzeigen
        tk.Label(details_window, text=f"Name: {question_name}", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=2)
        row += 1

        # Frage-Text anzeigen
        tk.Label(details_window, text=f"Frage: {question_text}", wraplength=400, justify="left").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        row += 1

        # Matching-Fragen (Zuordnung)
        if question_type == "matching":
            tk.Label(details_window, text="Zuordnungen:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1
            answer_options = set()  # Mögliche Antworten sammeln

            for subquestion in frage_element.findall('subquestion'):
                answer_elem = subquestion.find('answer/text')
                if answer_elem is not None:
                    answer_options.add(answer_elem.text)

            answer_options = list(answer_options)  # Set → Liste für Combobox
            user_answers[item_id] = {}  # Speicher für Nutzerantworten

            for subquestion in frage_element.findall('subquestion'):
                subquestion_text_elem = subquestion.find('text')
                subquestion_text = remove_html_tags(subquestion_text_elem.text.strip()) if subquestion_text_elem is not None else "—"

                tk.Label(details_window, text=f"{subquestion_text} →").grid(row=row, column=0, sticky="w", padx=5, pady=2)

                var = tk.StringVar(value="Wählen...")
                combo = ttk.Combobox(details_window, textvariable=var, values=answer_options, state="readonly")
                combo.grid(row=row, column=1, padx=5, pady=2)
                user_answers[item_id][subquestion_text] = (var, subquestion.find('answer/text').text)
                row += 1

        # Multiple-Choice-Fragen
        elif question_type == "multichoice":
            tk.Label(details_window, text="Antwortmöglichkeiten:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1

            user_answers[item_id] = tk.StringVar()  # Nutzer-Antwort speichern
            for answer in frage_element.findall('answer'):
                answer_text_elem = answer.find('text')
                answer_text = remove_html_tags(answer_text_elem.text.strip()) if answer_text_elem is not None else "—"

                is_correct = answer.get("fraction")  # Richtig oder falsch
                correct = float(is_correct) > 0 if is_correct else False

                rb = tk.Radiobutton(details_window, text=answer_text, variable=user_answers[item_id], value=answer_text)
                rb.grid(row=row, column=0, sticky="w", padx=5, pady=2)

                # Richtig-Falsch speichern
                user_answers[item_id + answer_text] = correct  
                row += 1
        
        #truefalse-Fragen
        elif question_type == "truefalse":
            tk.Label(details_window, text="Antwortmöglichkeiten:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=2)
            row += 1

            user_answers[item_id] = tk.StringVar()  # Nutzer-Antwort speichern
            for answer in frage_element.findall('answer'):
                answer_text_elem = answer.find('text')
                answer_text = remove_html_tags(answer_text_elem.text) if answer_text_elem is not None else "—"

                is_correct = answer.get("fraction")  # Richtig oder falsch
                correct = float(is_correct) > 0 if is_correct else False
                rb = tk.Radiobutton(details_window, text=answer_text, variable=user_answers[item_id], value=answer_text)
                rb.grid(row=row, column=0, sticky="w", padx=5, pady=2)
                
                # Richtig-Falsch speichern
                user_answers[item_id + answer_text] = correct
                row += 1

        # Trennlinie
        tk.Label(details_window, text="—" * 50).grid(row=row, column=0, columnspan=2, padx=5, pady=5)
        row += 1

    def auswertung():
        """Überprüft die Nutzerantworten"""
        richtig = 0
        falsch = 0

        for q_id, answers in user_answers.items():
            if isinstance(answers, dict):  # Matching
                for text, (var, correct_answer) in answers.items():
                    if var.get() == correct_answer:
                        richtig += 1
                    else:
                        falsch += 1
            elif isinstance(answers, tk.StringVar):  # Multiple-Choice
                user_choice = answers.get()
                if user_answers[q_id + user_choice]:  # Richtig?
                    richtig += 1
                else:
                    falsch += 1

        ergebnis_label.config(text=f"Ergebnis: {richtig} richtig, {falsch} falsch")

    ergebnis_label = tk.Label(details_window, text="")
    ergebnis_label.grid(row=row, column=0, columnspan=2, pady=10)
    row += 1

    auswerten_button = tk.Button(details_window, text="Antworten prüfen", command=auswertung)
    auswerten_button.grid(row=row, column=0, columnspan=2, pady=10)

def remove_html_tags(text):
    text = text.replace("<br>", "\n")  # HTML-Zeilenumbruch → echtes \n
    clean_text = re.sub(r'<.*?>', '', text)  # Entfernt restliche Tags
    return clean_text.strip()


root = tk.Tk()
root.title("Quiz Fragen")

waehl_button = ttk.Button(root, text="XML-Datei auswählen", command=waehle_datei)
waehl_button.pack(pady=10, side="top")

columns = ("Name", "Kategorie")
tree_display = ttk.Treeview(root, columns=columns, show="headings")
tree_display.heading("Name", text="Name")
tree_display.heading("Kategorie", text="Kategorie")
tree_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

select_button = ttk.Button(root, text="Auswahl anzeigen", command=get_selected_items)
select_button.pack(pady=10)

root.mainloop()



