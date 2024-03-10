from xmlrpc.server import SimpleXMLRPCServer # create an XML-RPC server 
from xmlrpc.server import SimpleXMLRPCRequestHandler  
import xml.etree.ElementTree as ET # handle XML data
import datetime
import requests

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server which is set up on port 8000 of the localhost.
server = SimpleXMLRPCServer(('localhost', 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

# Load or initialize XML database for data storage and management.
try:
    tree = ET.parse('db.xml')
    root = tree.getroot()
except Exception as e:
    root = ET.Element("data")
    tree = ET.ElementTree(root)

# Function to add or update a note
def add_or_update_topic(topic_name, note_name, text, timestamp):
    # Check if topic exists
    topic = root.find(f".//topic[@name='{topic_name}']")
    if topic is None:
        topic = ET.SubElement(root, 'topic', name=topic_name)
    
    # Add new note
    note = ET.SubElement(topic, 'note', name=note_name)
    ET.SubElement(note, 'text').text = text
    ET.SubElement(note, 'timestamp').text = timestamp
    
    # Save changes
    tree.write('db.xml')
    return True

# Function to retrieve topic notes
def get_topic_notes(topic_name):
    notes_info = []
    topic = root.find(f".//topic[@name='{topic_name}']")
    if topic is not None:
        for note in topic.findall('note'):
            note_info = {
                'name': note.get('name'),
                'text': note.find('text').text,
                'timestamp': note.find('timestamp').text
            }
            notes_info.append(note_info)
    return notes_info

def search_wikipedia(topic_name):
    base_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": topic_name,
        "format": "json"
    }

    response = requests.get(base_url, params=params).json()
    search_results = response.get("query", {}).get("search", [])
    if not search_results:
        return "No result found."

    # Assuming I am interested in the first result
    page_id = search_results[0]['pageid']
    return f"https://en.wikipedia.org/?curid={page_id}"

def add_wikipedia_info(topic_name):
    wikipedia_url = search_wikipedia(topic_name)
    note_name = "Wikipedia Link"
    text = f"More info: {wikipedia_url}"
    timestamp = datetime.datetime.now().strftime("%m/%d/%y - %H:%M:%S")
    
    # Reuse existing functionality to add this as a note
    add_or_update_topic(topic_name, note_name, text, timestamp)
    return wikipedia_url

# Register the functions
server.register_function(add_wikipedia_info, 'add_wikipedia_info')
server.register_function(add_or_update_topic, 'add_or_update_topic')
server.register_function(get_topic_notes, 'get_topic_notes')

print("Server is running.")
server.serve_forever()