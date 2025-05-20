#Agent (sender/server)
import random
from fastapi import FastAPI, Request
from RSA_module import RSA
from Crypto.Random import get_random_bytes

app = FastAPI()

#Initialize globals, but safely
app.state.rsa = None
app.state.total_information_items = 10 #n
app.state.information_items = [random.randint(0, 9999) for _ in range(app.state.total_information_items)] #Randomly generated information for sake of simulation
app.state.RN = [int.from_bytes(get_random_bytes(4), byteorder="big") for _ in range(app.state.total_information_items)] #Generate Agent's random numbers (RN[])
app.state.step2_value = None

#Agent initialization - send/receive initial data
@app.post("/step0")
async def step0(request: Request):
    step0_data = await request.json()

    key_size = step0_data.get("key_size") #Allow user to select key size, rather than default of 256
    message_index = step0_data.get("message_index") #Receive k from inquirer!
    message = step0_data.get("message") #Allow user to input message in addition to randomly generated

    app.state.rsa = RSA(key_size) #Generate key pair
    app.state.information_items[message_index] = message #Insert/replace user inputted secret message into randomly generated information 

    return {
        "public_key": app.state.rsa.public_key, #Send public key to Inquirer
        "modulus": app.state.rsa.modulus, #Send modulus to Inquirer
        "n": len(app.state.information_items), #Send number of information items (=total_information_items) to Inquirer
        "information_items": app.state.information_items
    }

#Step 1: Agent sends random numbers RN[1],...,RN[n] to Inquirer
@app.get("/step1")
async def step1():
    return {
        "RN": app.state.RN 
    }

#Step 2: Agent receives K+(IRN)+RN[k] from Inquirer
@app.post("/step2")
async def step2(request: Request):
    step2_data = await request.json()
    app.state.step2_value = step2_data.get("step2_value")

#Step 3: Agent sends Inquirer n items: K-(K+(IRN)+RN[k]-RN[i])+I[i] for i=1,...,n
@app.get("/step3")
async def step3():
    step2_value = int(app.state.step2_value)
    step3_response = []

    for i in range(app.state.total_information_items):
        #Agent derives n terms K+(IRN)+RN[k]-RN[i] for i=1,...,n
        step3_calculation = step2_value-app.state.RN[i]
        #Agent decrypts (using function K-) each of the n terms K+(IRN)+RN[k]-RN[i]
        step3_calculation = app.state.rsa.decrypt(step3_calculation)
        #Agent adds I[i] to each corresponding i-th outcome of the decryption function: K-(K+(IRN)+RN[k]-RN[i])+I[i]
        step3_calculation = step3_calculation+int(app.state.information_items[i])
        step3_response.append(step3_calculation)

    return {
        "responses": step3_response
    }
#Note: without IRN (Inquirer's random number), Agent could not know the specific k-th item that Inquirer requested