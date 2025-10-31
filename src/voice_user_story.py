import speech_recognition as sr
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import getpass
load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
    
# Initialize OpenAI LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=os.environ["OPENAI_API_KEY"])

# Initialize recognizer from sr
recognizer = sr.Recognizer()

# Capture voice from mic
with sr.Microphone() as source:
    print("Start Speaking...")
    audio = recognizer.listen(source, phrase_time_limit=15)

# Transcribe to text using Google API
try:
    text = recognizer.recognize_google(audio)
    print("You said:", text)
except sr.UnknownValueError:
    print("Sorry, I couldn't understand.")
    exit()
except sr.RequestError as e:
    print("Could not request results; {0}".format(e))
    exit()

title_schema = ResponseSchema(name="title",
                             description="extract the title if specfically mentioned as 'title'\
                             or make a breif, clear name.")
description_schema = ResponseSchema(name="description",
                             description="define the description if mentioned specifically as 'description'\
                             or make a clear consise explanation of requirment.")
acceptance_criteria_schema = ResponseSchema(name="acceptance_criteria",
                             description="define the acceptance criteria if mentioned specifically as 'acceptance criteria or AC '\
or make a checklist of conditions that must be met for the user story requirment.\
and output them as a comma separated Python list.")
severity_schema = ResponseSchema(name="severity",
                                      description="define the severity if spefically mentioned\
                                      or make it like based on the purpose such as from feature, bug fix, improvment or technical task.")
type_schema = ResponseSchema(name="type",
                                    description="define the type if spefically mentioned\
                                    or make it like based on the purpose such as from feature, bug fix, improvment or technical task.")

response_schemas = [title_schema, 
                    description_schema,
                    acceptance_criteria_schema,
                    severity_schema,
                    type_schema]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

system_template = """\
For the following text, extract the following information to create the user story:

title: extract the title if specfically mentioned as "title" or make a breif, clear name.

description: define the description if mentioned specifically as "description" or make a clear consise explanation of requirment.

acceptance_criteria: define the acceptance criteria if mentioned specifically as 'acceptance criteria or AC '\
or make a checklist of conditions that must be met for the user story requirment.\
and output them as a comma separated Python list.

severity : define the severity if spefically mentioned,\
or make it as from how critical the user story is like Low, Medium, High, Critical.

type : define the type if spefically mentioned,\
or make it like based on the purpose such as from feature, bug fix, improvment or technical task.

Format the output as JSON with the following keys:
title
description
acceptance_criteria
severity
type

text: {text}
"""

prompt = ChatPromptTemplate.from_template(system_template)

chain = prompt | llm

response = chain.invoke({"text": text})

output_dict = output_parser.parse(response.content)
print(output_dict)

