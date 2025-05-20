#Inquirer (receiver/client)
import streamlit as st
import pandas as pd
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

from Crypto.Random import get_random_bytes
from Crypto.Util.number import getRandomNBitInteger
from RSA_module import RSA

st.set_page_config("🔐 Inquirer - RSA based 1-out-of-n Oblivious Transfer Simulator", layout="wide")
st.title("🔐 RSA based 1-out-of-n Oblivious Transfer Simulator")
st.header("Inquirer")

total_information_items = 10 #n

#Parameters to initialize Agent in sidebar
st.sidebar.header("Step 0:")
key_size = st.sidebar.selectbox("Key Size (bits)", [256, 512, 1024])
message = st.sidebar.text_input("Secret Message")
message_index = st.sidebar.selectbox("Index (k)", options=list(range(total_information_items)))
step_0 = st.sidebar.button("🔄 Initialize **Agent**")

#Session state management
if "step" not in st.session_state:              st.session_state.step = 0
if "public_key" not in st.session_state:        st.session_state.public_key = None
if "modulus" not in st.session_state:           st.session_state.modulus = None
if "n" not in st.session_state:                 st.session_state.n = None
if "information_items" not in st.session_state: st.session_state.information_items = [] #For displaying in demonstration; should not really know all these
if "RN" not in st.session_state:                st.session_state.RN = []
if "message_index" not in st.session_state:     st.session_state.message_index = None
if "IRN" not in st.session_state:               st.session_state.IRN = getRandomNBitInteger(32) #Generate Inquirer's random number (IRN); random 32-bit integer
if "step3_data" not in st.session_state:        st.session_state.step3_data = []

#Step 0 (initialization):
if st.session_state.step == 0 and step_0:
    st.session_state.message_index = message_index
    try:
        request = {
            "key_size": key_size,
            "message": message,
            "message_index": st.session_state.message_index
        }
        response = requests.post(f"{API_BASE_URL}/step0", json=request)

        if response.status_code == 200:
            st.success(f"**Sent** key size (`{key_size}`-bit), message (`{message}`), and message index (`{message_index}`) to **Agent**")
            st.success("✅ **Agent** initialized!")

            step0_data = response.json()
            st.session_state.public_key = step0_data["public_key"]
            st.session_state.modulus = step0_data["modulus"]
            st.session_state.n = step0_data["n"]
            st.session_state.information_items = step0_data["information_items"] #Sake of demonstration in final step

            st.info(f"**Received** public key, modulus, and number of information items (`{st.session_state.n}`) from **Agent**")

            st.session_state.step = 1
    except Exception as e:
        st.error("❌ Failed to initialize **Agent**")
        st.exception(e)

#Step 1:
if st.session_state.step == 1:
    if st.button("▶️ Step 1"):
        try:
            response = requests.get(f"{API_BASE_URL}/step1")

            if response.status_code == 200:
                step1_data = response.json()
                st.session_state.RN = step1_data["RN"]
                st.info("**Received** random numbers (`RN[0],...,RN[n-1]`) from **Agent**")
                st.subheader("**Agent**'s random numbers (`RN[]`):")
                st.dataframe(pd.DataFrame(st.session_state.RN, columns=['Agent random number (RN[i])']))

                st.session_state.step = 2
        except Exception as e:
            st.error("❌ Failed to contact **Agent**")
            st.exception({e})


#Step 2: Inquirer sends K+(IRN)+RN[k] to Agent
if st.session_state.step == 2:
    if st.button("▶️ Step 2"):
        #Step 2_1: Encrypt Inquirer's random number (IRN)
        rsa = RSA(bit_length=key_size, public_key=st.session_state.public_key, modulus=st.session_state.modulus)
        encrypted_IRN = rsa.encrypt(st.session_state.IRN)
        #Step 2_2: Add Inquirer's random numbers (IRN) to Agent's random numbers
        step2_value = encrypted_IRN+st.session_state.RN[st.session_state.message_index] 

        try:
            response = requests.post(f"{API_BASE_URL}/step2", json={"step2_value": str(step2_value)}) #Convert to string
            if response.status_code == 200:
                st.subheader(f"Inquirer's random number (`IRN`) = `{st.session_state.IRN}`", divider=True)
                st.subheader(f"Encrypted `IRN` = `{encrypted_IRN}`", divider=True)
                st.success(f"**Sent** `{step2_value}` (`K+(IRN)+RN[k]`) to **Agent**")

                st.session_state.step = 3
        except Exception as e:
            st.error("❌ Failed to contact **Agent**")
            st.exception({e})

#Step 3:
if st.session_state.step == 3:
        if st.button("▶️ Step 3"):
            try:
                response = requests.get(f"{API_BASE_URL}/step3")
                if response.status_code == 200:
                    st.session_state.step3_data = response.json()["responses"]
                    st.info("**Received** `K-(K+(IRN)+RN[k]-RN[i])+I[i]` for `i=1,...,n` from **Agent**");
            
                    st.session_state.step = 4
            except Exception as e:
                st.error("❌ Failed to contact **Agent**")
                st.exception({e})

#Step 4: Inquirer offsets the k-th terms sent by Agent in previous step with IRN: K-(K+(IRN)+RN[k]-RN[i])+I[i]
if st.session_state.step == 4:
        if st.button("▶️ Step 4"):
            st.session_state.final_values = [int(value)-st.session_state.IRN for value in st.session_state.step3_data]

            #Convert all to str to avoid problems with big int's
            df = pd.DataFrame({
                "Index": list(range(st.session_state.n)),
                "RN[i]": [str(x) for x in st.session_state.RN],
                "Information Item (I[i])": [str(x) for x in st.session_state.information_items],
                "Response": [str(x) for x in st.session_state.step3_data],
                "Final Value (R - IRN)": [str(x) for x in st.session_state.final_values]
            })

            def highlight_row(row):
                return ['background-color: lightgreen' if row.Index == st.session_state.message_index else '' for _ in row]

            st.dataframe(df.style.apply(highlight_row, axis=1))
            st.success(f"✔️ **Inquirer received** `I[{st.session_state.message_index}] = {st.session_state.final_values[st.session_state.message_index]}` from **Agent**")
