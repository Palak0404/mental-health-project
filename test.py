import google.generativeai as genai
genai.configure(api_key="AIzaSyD4Q785-hi7YmshqlSj5rirR3220xL7QsE")

model = genai.GenerativeModel("gemini-pro")
response = model.generate_content("Hello!")
print(response)
