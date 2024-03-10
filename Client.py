import xmlrpc.client # implement communication between the client and the XML-RPC server
import datetime

try:
    s = xmlrpc.client.ServerProxy('http://localhost:8000')
except Exception as e:
    print(f"Failed to connect to server: {e}")
    exit(1)

# Function to add note
def add_note():
    topic_name = input("Enter topic name: ")
    note_name = input("Enter note name: ")
    text = input("Enter note text: ")
    timestamp = datetime.datetime.now().strftime("%m/%d/%y - %H:%M:%S")
    retry_count = 3
    for attempt in range(retry_count):
        try:
            s.add_or_update_topic(topic_name, note_name, text, timestamp)
            print("Note added successfully.")
            break  
        except Exception as e:
            if attempt < retry_count - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
            else:
                print("Failed to add note after several attempts. Please try again later.")

# Function to view notes by topic
def view_notes():
    topic_name = input("Enter topic name to view notes: ")
    notes = s.get_topic_notes(topic_name)
    if not notes:
        print("No notes found for this topic.")
    else:
        for note in notes:
            print(f"Name: {note['name']}, Text: {note['text']}, Timestamp: {note['timestamp']}")

# Add a option for the user to search Wikipedia and add info
def search_wikipedia_and_add():
    topic_name = input("Enter topic name to search on Wikipedia and add info: ")
    wikipedia_url = s.add_wikipedia_info(topic_name)
    print(f"Wikipedia info added. See more at: {wikipedia_url}")

# Update the main loop to include the new option
while True:
    print("(1) Add Info\n(2) View Info\n(3) Search Wikipedia and Add Info\n(4) Exit")
    choice = input("Choose an action: ")
    if choice == '1':
        add_note()
    elif choice == '2':
        view_notes()
    elif choice == '3':
        search_wikipedia_and_add()
    elif choice == '4':
        break
    else:
        print("Invalid choice.")
