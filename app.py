import streamlit as st 
import requests
import io
from PIL import Image
from openai import OpenAI
import re
import random
api_key = 'Add your API KEY'
client = OpenAI(api_key=api_key)
API_URL1 = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
API_URL2 = "https://api-inference.huggingface.co/models/cloudqi/cqi_text_to_image_pt_v0"
headers = {"Authorization": "Bearer **YOUR BEARER"}

st.set_page_config(
    page_title = 'Create your BLOG-POST',
    page_icon = '🆗',
    layout = 'wide'
)
headers_lst = ['introduction']

def get_keywords_gpt(article,audience='casual', content_type='tutorial', brand_voice='neutral', subject_matter='general', consistency='consistent'):
    # Constructing a system message to guide the GPT-3 model    
    system_message = f"You are a {audience} writer creating {content_type} content with a {brand_voice} voice. Your blog focuses on {subject_matter}. Aim for {consistency} tone throughout your posts."
    # Using the OpenAI API to generate keywords for the given article
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": system_message},
    {"role": "user", "content": f'generate strong keywords for "{article}" bolgpost and make every keyword in seperated line'}
    ]
    )
    # Extracting keywords from the response and cleaning them
    keywords = [keyword for keyword in completion.choices[0].message.content.split('\n') ]
    cleaned_keywords = [re.sub(r'^[^a-zA-Z]+', '', word) for word in keywords]
    return cleaned_keywords
    

def get_message_gpt(article, keywords, kind='paragraph',headers_lst=headers_lst, lst=True, audience='casual', content_type='tutorial', brand_voice='neutral', subject_matter='general', consistency='consistent'):
    # Constructing a system message to guide the GPT-3 model
    system_message = f"You are a {audience} writer creating {content_type} content with a {brand_voice} voice. Your blog focuses on {subject_matter}. Aim for {consistency} tone throughout your posts."
    # Constructing content based on the specified kind and options
    if kind == 'paragraph':
        if lst:
            # Content for generating a paragraph with a numbered list
            content = f"generate a paragraph for '{article}' blog post. Ensure it contains just one header and the header must not be one of {headers_lst}, and includes some of these keywords: {keywords}.The header must start the token '<H>' and end with token </H>. Place a numbered list at the end of the paragraph make sure the list at the end of the paragraph, and the header of the list must start the token '<HL>' and end with token </HL>. Each list element should start the token '<LI>' and end with token </LI>. give me only the paragraph and the list don't return any other text rather that paragraph and the list."
        else:
            # Content for generating a plain paragraph
            content = f"generate a paragraph for '{article}' blog post. Ensure it contains just one header and the header must not be one of {headers_lst}, and includes some of these keywords: {keywords}. The header must start the token '<H>' and end with token </H>. give me only the paragraph don't return any other text rather that paragraph."
    else:
        content = f"generate {kind} for '{article}' blog post. Ensure it contains some of these keywords: {keywords}.give me only the {kind} and the list don't return any other text rather that {kind}."
    # Making the API call to generate content
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": content}
        ]
    )
    # Extracting the generated content from the response
    generated_content = completion.choices[0].message.content

    # Ensure consistent formatting of header and list tokens
    generated_content = generated_content.replace("<hl>", "<HL>").replace("</hl>", "</HL>")
    generated_content = generated_content.replace("<li>", "<LI>").replace("</li>", "</LI>")
    
    return generated_content

def split_header(paragraph):
    # Define a regex pattern to capture the header and the rest of the text
    pattern = re.compile(r'<H>(.*?)</H>(.*)', re.DOTALL)

    # Use the regex pattern to extract the header and the rest of the text
    match = pattern.match(paragraph)
    if match:
        header = match.group(1).strip()
        rest_of_text = match.group(2).strip()
    else:
        header = 'empty'
        rest_of_text=paragraph
    return header,rest_of_text

def split_content_list(input_paragraph):
    # Define a regex pattern to capture the header, paragraph without lists, list header, and list elements
    pattern = re.compile(r'<H>(.*?)</H>(.*?)<HL>(.*?)</HL>(.*?)<LI>(.*?)</LI>', re.DOTALL)
    # Use the regex pattern to extract the content
    match = pattern.match(input_paragraph)
    if match:
        header = match.group(1).strip()
        rest_of_text_without_lists = match.group(2).strip()
        list_header = match.group(3).strip()
        list_elements_str = match.group(4).strip()
        # Handle list elements separately using a different regex
        list_elements = re.findall(r'<LI>(.*?)</LI>', input_paragraph)
        list_elements = [item.strip() for item in list_elements]

    else:
        
        header = 'empty'
        rest_of_text_without_lists = input_paragraph
        list_header = 'empty'
        list_elements = []

    return header, rest_of_text_without_lists, list_header, list_elements

def image_query(payload):
    response = requests.post(API_URL1, headers=headers, json=payload)
    return response.content

def create_image(random_keyword):
    image_bytes = image_query({
    "inputs": f"create image about {random_keyword} image shouldn't include any words or numbers or characters",
    })
    image = Image.open(io.BytesIO(image_bytes))
    return image

def random_size(size):
    # Generate random numbers for paragraphs and images
    num_paragraphs = random.randint(2, size)  # Random number of paragraphs between 2 and max_size
    num_images = random.randint(1, min(num_paragraphs - 1, size))  # Random number of images, ensuring it's less than num_paragraphs and less than max_size

    # Generate random positions for images
    image_positions = random.sample(range(1, num_paragraphs), num_images)

    # Sort the image positions to ensure they are in ascending order
    image_positions.sort()
    return num_paragraphs ,num_images, image_positions






article = st.text_area("Enter your blog-post topic", "Web development")
st.warning("Make sure that you write the words correctly and that the letters are arranged well.")
# Sample options for dropdown lists
default_audiences = ['Professional', 'Casual', 'Technical','Other']
default_content_types = ['Tutorial', 'News', 'Review','Other']
default_brand_voices = ['Neutral', 'Friendly', 'Formal','Other']
default_subject_matters = ['Technology', 'Lifestyle', 'Science','Other']
default_consistencies = ['Consistent', 'Varied','Other']

st.markdown("### Audience:")
st.write("Consider your target audience. Are they professionals, casual readers, or a specific demographic? Tailor your tone to resonate with your audience.")
# User selects values from dropdown lists
selected_audience = st.selectbox("Select Audience:", default_audiences)
if selected_audience == 'Other':
    selected_audience = st.text_input("Please specify the other audience:")




st.markdown("### Content Type:")
st.write("The type of content you're creating will influence the tone. Is it a tutorial, a news article, a review, or a personal blog? Each type may require a different approach.")
selected_content_type = st.selectbox("Select Content Type:", default_content_types)

if selected_content_type == 'Other':
    selected_content_type = st.text_input("Please specify the other content type:")


st.markdown("### Brand Voice:")
st.write("If your blog is associated with a brand, ensure that the tone aligns with the brand's voice and values.")
selected_brand_voice = st.selectbox("Select Brand Voice:", default_brand_voices)
if selected_brand_voice == 'Other':
    selected_brand_voice = st.text_input("Please specify the other brand voice:")

st.markdown("### Subject Matter:")
st.write("The topic of your blog post can influence the tone. For example, a serious topic may require a more somber tone, while a light-hearted topic may allow for a more playful tone.")
selected_subject_matter = st.selectbox("Select Subject Matter:", default_subject_matters)
if selected_subject_matter == 'Other':
    selected_subject_matter = st.text_input("Please specify the other subject matter:")



st.markdown("### Consistency:")
st.write("Consistency in tone across your blog can help build a recognizable and cohesive brand identity.")
selected_consistency = st.selectbox("Select Consistency:", default_consistencies)
if selected_consistency == 'Other':
    selected_consistency = st.text_input("Please specify the other consistency:")


st.markdown("### Keyword Selection")

# Radio button for choosing between automatic generation and manual addition
keyword_selection = st.radio("Keywords:", ['Automatic Generation', 'Manual Addition'])
generate_keywords = True
if keyword_selection == 'Automatic Generation':
    # Call the function for automatic keyword generation
    generate_keywords=True
    #keywords = get_keywords_gpt(article,selected_audience,selected_content_type,selected_brand_voice,selected_subject_matter,selected_consistency)
    #st.write("Automatic Keywords:", keywords)
else:
    # Text input box for manual addition of keywords
    manual_keywords = st.text_input("Add your specific keywords separated by commas:")
    
    # Process the manual_keywords string into a list of keywords (assuming comma-separated)
    manual_keywords_seperated = [keyword.strip() for keyword in manual_keywords.split(',')]
    generate_keywords=False
    #st.write("Manually Added Keywords:", keywords)
if generate_keywords==False:
    st.write(f"manual_keywords_seperated: {manual_keywords_seperated}")

max_size = st.number_input("Enter maximum number of paragaraphs:", value=5, step=1)
st.markdown("##### Omar Khaled Sayed")
st.markdown("##### omarkhaledcvexpert@gmail.com")
st.markdown("##### +201150499570")



def start(article,selected_audience,selected_content_type,selected_brand_voice,selected_subject_matter,selected_consistency,headers_lst,size=4,generate_keywords=True):
    st.title(f"{article}")
    

    #st.markdown(f"# {article}")

    num_paragraphs ,num_images, image_positions = random_size(size)
    st.write(f'Your blog post will have {num_paragraphs} paragaraphs, {num_images} images and image positions are {image_positions}')
    if generate_keywords:
        keywords = get_keywords_gpt(article,selected_audience,selected_content_type,selected_brand_voice,selected_subject_matter,selected_consistency)
    else:
        keywords = manual_keywords_seperated


    introduction = get_message_gpt(article,keywords,kind='introduction',headers_lst = headers_lst,lst=False,
                                    audience=selected_audience,content_type=selected_content_type,
                                    brand_voice=selected_brand_voice,subject_matter=selected_subject_matter,
                                    consistency=selected_consistency)
    st.markdown("## Introduction")
    st.write(introduction)

    for i in range(1,num_paragraphs+1):
        probability_distribution = [True] * 65 + [False] * 35
        random_bool = random.choice(probability_distribution)
        paragraph_with_header = get_message_gpt(article,keywords,kind='paragraph',headers_lst = headers_lst,lst=random_bool,
                                    audience=selected_audience,content_type=selected_content_type,
                                    brand_voice=selected_brand_voice,subject_matter=selected_subject_matter,
                                    consistency=selected_consistency)
        if random_bool ==False:
            header , paragraph = split_header(paragraph_with_header)
            if header != 'empty':
                st.markdown(f"## {header}")
                headers_lst.append(header)
            st.write(paragraph)
        else:
            header, rest_of_text_without_lists, list_header, list_elements = split_content_list(paragraph_with_header)
            if header != 'empty':
                st.markdown(f"## {header}")
                headers_lst.append(header)
            st.write(rest_of_text_without_lists)
            st.markdown(f"##### {list_header}")
            st.write(list_elements)
    
        if (i in image_positions) and (num_images !=0):
            #st.write("Image must appear here")
            if header !='empty':
                img = create_image(header)
                st.image(img, caption=f'{header}')
            else:
                random_keyword = random.choice(keywords)
                img = create_image(random_keyword) # replace data with our value
                st.image(img, caption=f'{random_keyword}')#, use_column_width=True)
            num_images -=1
    conclusion = get_message_gpt(article,keywords,kind='conclusion',headers_lst = headers_lst,lst=False,
                                    audience=selected_audience,content_type=selected_content_type,
                                    brand_voice=selected_brand_voice,subject_matter=selected_subject_matter,
                                    consistency=selected_consistency)
    st.markdown("## conclusion")
    st.write(conclusion)
    #st.write(headers_lst)


# Button to start the main function
if st.button("Start"):
    start(article,
        selected_audience,
        selected_content_type,
        selected_brand_voice,
        selected_subject_matter,
        selected_consistency,
        headers_lst,
        size=max_size,
        generate_keywords=generate_keywords)

