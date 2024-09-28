import streamlit as st
import google.generativeai as genai

st.title("🥗 Nutrition & Fitness Bot ")
st.subheader("Your personalized meal plan and fitness assistant")

# Capture Gemini API Key
gemini_api_key = st.text_input("Gemini API Key: ", placeholder="Type your API Key here...", type="password")
# Initialize the Gemini Model
model = None
if gemini_api_key:
    try:
        # Configure Gemini with the provided API Key
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-pro")
        st.success("Gemini API Key successfully configured.")
    except Exception as e:
        st.error(f"An error occurred while setting up the Gemini model: {e}")

# Initialize session state for storing chat history, user details, and plan type
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Initialize with an empty list
if "user_data" not in st.session_state:
    st.session_state.user_data = {
        "age": None,
        "weight": None,
        "height": None,
        "bmi": None,
        "expected_weight": None
    }
if "plan_generated" not in st.session_state:
    st.session_state.plan_generated = False  # Track if the plan (meal or fitness) is generated

# Sidebar for selecting Nutrition Expert or Gym Coach using a drop-down list
with st.sidebar:
    expert_type = st.selectbox(
        "Select your assistant:",
        ("Nutrition Expert", "Gym Coach")
    )

# Capture user details for nutrition or fitness
def get_user_details():
    with st.form("User Details"):
        st.session_state.user_data["age"] = st.number_input("Enter your age", min_value=10, max_value=100, step=1)
        st.session_state.user_data["weight"] = st.number_input("Enter your current weight (kg)", min_value=30.0, max_value=200.0, step=0.1)
        st.session_state.user_data["height"] = st.number_input("Enter your height (cm)", min_value=100, max_value=250, step=1)
        st.session_state.user_data["expected_weight"] = st.number_input("Enter your expected weight (kg)", min_value=30.0, max_value=200.0, step=0.1)
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            # Calculate BMI
            height_m = st.session_state.user_data["height"] / 100
            st.session_state.user_data["bmi"] = st.session_state.user_data["weight"] / (height_m ** 2)
            st.success(f"Your BMI is: {st.session_state.user_data['bmi']:.2f}")

            # Generate the weekly plan once user data is submitted
            generate_plan()

# Function to generate meal or fitness plan
def generate_plan():
    if model and not st.session_state.plan_generated:
        try:
            age = st.session_state.user_data["age"]
            weight = st.session_state.user_data["weight"]
            bmi = st.session_state.user_data["bmi"]
            expected_weight = st.session_state.user_data["expected_weight"]
            
            if expert_type == "Nutrition Expert":
                # Generate a weekly meal plan
                prompt = (
                    f"Generate a weekly meal plan for a {age}-year-old person weighing {weight} kg, "
                    f"with a BMI of {bmi:.2f}, aiming to reach {expected_weight} kg. The person wants a "
                    "balanced, nutritious diet with diverse meals."
                )
            else:
                # Generate a weekly fitness plan from a gym coach
                prompt = (
                    f"Generate a weekly exercise plan for a {age}-year-old person weighing {weight} kg, "
                    f"with a BMI of {bmi:.2f}, aiming to reach {expected_weight} kg. The person wants a "
                    "balanced fitness routine, including strength, cardio, and flexibility exercises."
                )
            
            # Generate content using the prompt
            response = model.generate_content(prompt)
            bot_response = response.text
            
            # Store and display the bot response
            st.session_state.chat_history.append(("assistant", bot_response))
            st.session_state.plan_generated = True
            st.chat_message("assistant").markdown(bot_response)
        except Exception as e:
            st.error(f"An error occurred while generating the plan: {e}")

get_user_details()

# Display previous chat history using st.chat_message (if available)
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# After the plan is generated, allow user to ask further questions about their nutrition or fitness
if st.session_state.plan_generated:
    st.subheader(f"Ask me anything about your {expert_type.lower()}!")
    if user_input := st.chat_input("Type your question here..."):
        # Store and display user message
        st.session_state.chat_history.append(("user", user_input))
        st.chat_message("user").markdown(user_input)

        # Generate a response based on the selected expert
        if model:
            try:
                # Generate response from the selected expert type
                prompt = f"You are a {expert_type.lower()}. Answer this user's question: '{user_input}'"
                response = model.generate_content(prompt)
                bot_response = response.text

                # Store and display the bot response
                st.session_state.chat_history.append(("assistant", bot_response))
                st.chat_message("assistant").markdown(bot_response)
            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")


