# RSA based 1-out-of-n Oblivious Transfer Simulator
A simulator of the 1-out-of-n Oblivious Transfer protocol - redone in Python from my earlier Java [project](https://github.com/jsgarcha/one-over-n-oblivious-transfer/). Instead of sockets, this follows a REST API architecture. The front-end is in Streamlit and back-end in FastAPI.
Beware: the program implements non-standard RSA (for academic purposes), so it is not suited for real-world use! Though it hints at proper practice by calling functions from [PyCryptodome](https://www.pycryptodome.org/). Furthermore, only a numeric message is currently supported as input to simplify encryption/decryption operations.

## Usage:
This simulator allows the user to select/input some pieces of data and step through the 1-out-of-n Oblivious Transfer protocol's execution, from start to end. At each step, the actions of `Agent` and `Inquirer` and their results, generally hidden behind the scenes, are displayed; run the simulator again by refreshing the page and selecting/inputting different data. Ultimately, the goal of this visual demonstration is to teach the user how Oblivious Transfer works.

Make sure you have Python version >= `3.12.10`
1) `git clone https://github.com/jsgarcha/oblivious-transfer-simulator`
2) `cd oblivious-transfer-simulator`
3) `pip install -r requirements.txt`
4) `fastapi run agent.py`
5) In another terminal: `streamlit run inquirer.py`

## Overview:
1) `Agent` is initialized with random information. 
2)  User's secret message is sent to `Agent`
3) `Inquirer` is initialized with a random `k` (index of the information item it desires). 
4) `Agent` listens for `Inquirer`. 
5) Once `Inquirer` connects to the `Agent`, 1-out-of-n Oblivious Transfer begins. 
6) The protocol ends with `Inquirer` receiving the `k`th information item from the `Agent`.

For a more thorough overview of the mathematical steps involved in the protocol, please refer to my comments in the code.