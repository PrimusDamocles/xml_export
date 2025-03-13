


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

# def get_selected_items():
#     selected = tree_display.selection()
#     if not selected:
#         print("Keine Zeile ausgewählt.")
#         return

#     # Create a new window
#     details_window = tk.Toplevel(root)
#     details_window.title("Frage-Details")

#     # For each selected item, use the iid to get the actual question element
#     row = 0
#     for item_id in selected:
#         question_index = int(item_id)  # Because we used the index as the iid
#         frage_element = all_questions[question_index]

#         # Extract whatever data you need
#         name_obj = frage_element.find('name')
#         question_name = name_obj.find('text').text if name_obj is not None else "—"

#         question_text_elem = frage_element.find('questiontext')
#         question_text = question_text_elem.find('text').text if question_text_elem is not None else "—"

#         # Display them in the new window:
#         tk.Label(details_window, text=f"Name: {question_name}").grid(row=row, column=0, padx=5, pady=5, sticky='w')
#         row += 1

#         tk.Label(details_window, text=f"Frage-Text: {question_text}").grid(row=row, column=0, padx=5, pady=5, sticky='w')
#         row += 1

#         # If you have more fields, handle them similarly
#         tk.Label(details_window, text="—" * 40).grid(row=row, column=0, padx=5, pady=5)
#         row += 1


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



# def lese_xml_datei(dateipfad):
#     try:
#         tree = ET.parse(dateipfad)
#         root = tree.getroot()
#         return root.iter('question')
#     except FileNotFoundError:
#         print(f"Fehler: Datei '{dateipfad}' nicht gefunden.")
#         return None
#     except ET.ParseError:
#         print(f"Fehler: Fehler beim Parsen der XML-Datei '{dateipfad}'.")
#         return None


# def waehle_datei():
#     dateipfad = filedialog.askopenfilename(title="XML-Datei auswählen", filetypes=[("XML-Dateien", "*.xml")])
#     if dateipfad:
#         fragen = lese_xml_datei(dateipfad)
#         print(fragen)

#         if fragen:
#             for row in tree_display.get_children():
#                 tree_display.delete(row)
#             for frage in fragen:
#                 kategorie = frage.get("type")
#                 name_object = frage.find('name')
#                 if name_object:
#                     name = name_object.find('text').text
#                     tree_display.insert("", "end", values=(name, kategorie))
#     else:
#         print("Keine Datei ausgewählt.")


# def get_selected_items():
#     selected_items = [tree_display.item(item, "values") for item in tree_display.selection()]
#     print("Ausgewählte Elemente:", selected_items)

# root = tk.Tk()
# root.title("Quiz Fragen")



# waehl_button = ttk.Button(root, text="XML-Datei auswählen", command=waehle_datei)
# waehl_button.pack(pady=10,side="top")

# columns = ("Name", "Kategorie")
# tree_display = ttk.Treeview(root, columns=columns, show="headings")
# tree_display.heading("Name", text="Name")
# tree_display.heading("Kategorie", text="Kategorie")
# tree_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# select_button = ttk.Button(root, text="Auswahl anzeigen", command=get_selected_items)
# select_button.pack(pady=10)

# root.mainloop()






















































# def zeige_frage_details(frage):
#     detail_fenster = tk.Toplevel(root)  # Neues Fenster für Details
#     detail_fenster.title(frage.find('name/text').text if frage.find('name/text') is not None else "Frage Details")

#     for element in frage.iter():
#         if element.tag not in ['subquestion', 'answer', 'tags', 'tag']: #Ausblenden von subquestion, answer, tags und tag in der Detailansicht
#             text = element.text.strip() if element.text else ""
#             if text:
#                 label = ttk.Label(detail_fenster, text=f"{element.tag}: {text}", wraplength=400) #wraplength für automatischen Zeilenumbruch
#                 label.pack(pady=2)
#             elif element.attrib:
#                 label = ttk.Label(detail_fenster, text=f"{element.tag}: {element.attrib}", wraplength=400)
#                 label.pack(pady=2)
#         elif element.tag == 'subquestion':
#             subquestion_frame = ttk.LabelFrame(detail_fenster, text="Subquestion")
#             subquestion_frame.pack(pady=5)
#             subquestion_text = element.find('text').text.strip() if element.find('text') is not None else ""
#             subquestion_label = ttk.Label(subquestion_frame, text=subquestion_text, wraplength=380)
#             subquestion_label.pack()
#             answer_text = element.find('answer/text').text.strip() if element.find('answer/text') is not None else ""
#             answer_label = ttk.Label(subquestion_frame, text=f"Answer: {answer_text}", wraplength=380)
#             answer_label.pack()
#         elif element.tag == 'tag':
#             tag_frame = ttk.LabelFrame(detail_fenster, text="Tags")
#             tag_frame.pack(pady=5)
#             tag_text = element.find('text').text.strip() if element.find('text') is not None else ""
#             tag_label = ttk.Label(tag_frame, text=tag_text, wraplength=380)
#             tag_label.pack()


# def zeige_frage_uebersicht(fragen):
#     for i, frage in enumerate(fragen):
#         frage_name = frage.find('name/text').text if frage.find('name/text') is not None else f"Frage {i+1}"
#         button = ttk.Button(root, text=frage_name, command=lambda f=frage: zeige_frage_details(f))
#         button.pack(pady=2)