


import xml.etree.ElementTree as ET
import tkinter as tk
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

    # Create a new window
    details_window = tk.Toplevel(root)
    details_window.title("Frage-Details")

    # For each selected item, use the iid to get the actual question element
    row = 0
    for item_id in selected:
        question_index = int(item_id)  # Because we used the index as the iid
        frage_element = all_questions[question_index]

        # Extract whatever data you need
        name_obj = frage_element.find('name')
        question_name = name_obj.find('text').text if name_obj is not None else "—"

        question_text_elem = frage_element.find('questiontext')
        question_text = question_text_elem.find('text').text if question_text_elem is not None else "—"

        # Display them in the new window:
        tk.Label(details_window, text=f"Name: {question_name}").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        row += 1

        tk.Label(details_window, text=f"Frage-Text: {question_text}").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        row += 1

        # If you have more fields, handle them similarly
        tk.Label(details_window, text="—" * 40).grid(row=row, column=0, padx=5, pady=5)
        row += 1


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